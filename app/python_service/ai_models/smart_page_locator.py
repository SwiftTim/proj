import re
import pdfplumber
import pypdf
from typing import List, Dict, Optional, Tuple

class SmartPageLocator:
    """
    CGBIRR August 2025 Specific Page Locator
    
    Logic:
    1. Parse TOC (Pages 2-20) using strict regex '3.X. County Government of ...'
    2. Map County -> Start Page
    3. End Page = (Next County Start Page) - 1
    4. Validate page headers contain 'County Government of {Name}'
    5. SKIP national summary tables (Pages 40-100)
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.toc_map: Dict[str, int] = {}
        self.county_list: List[Tuple[str, int]] = []  # Ordered list for next-county lookup
        self._parse_attempted = False
        
    def locate_county_pages(self, county_name: str) -> List[int]:
        """
        Returns exact page numbers for the county section only (1-indexed)
        Typically 4 pages per county.
        """
        # Global Offset for CGBIRR August 2025
        # Analysis showed TOC Page 278 (Mandera) corresponds to PDF Page 324
        # Offset = 324 - 278 = 46
        PAGE_OFFSET = 46
        
        # 1. Parse TOC if not done
        if not self._parse_attempted:
            self._parse_toc_cgbirr()
            self._parse_attempted = True
        
        # 2. Find target county
        target_county = self._normalize_name(county_name)
        start_page = None
        start_index = -1
        
        # Exact match / partial match search
        for i, (name, page) in enumerate(self.county_list):
            if target_county in self._normalize_name(name):
                start_page = page
                start_index = i
                print(f"  ✅ Found {name} in TOC at page {page} (PDF Page approx {page + PAGE_OFFSET})")
                break
        
        # Fallback if not found in TOC
        if start_page is None:
            print(f"  ⚠️ {county_name} not found in TOC, trying fallback")
            return self._hardcoded_fallback(county_name)
        
        # 3. Find next county to calculate end_page
        if start_index + 1 < len(self.county_list):
            next_county_name, next_page = self.county_list[start_index + 1]
            end_page = next_page - 1  # Stop before next county starts
            print(f"  📍 Next county ({next_county_name}) starts at {next_page}")
        else:
            # Last county (West Pokot) - assume 4 pages
            end_page = start_page + 3
            print(f"  📍 Last county, extracting 4 pages")
        
        # Apply Offset
        pdf_start = start_page + PAGE_OFFSET
        pdf_end = end_page + PAGE_OFFSET
        
        # 4. Generate page list (1-indexed)
        # Ensure we don't go backwards or exceed reasonable page count
        if pdf_end < pdf_start:
            pdf_end = pdf_start + 3
            
        page_numbers = list(range(pdf_start, pdf_end + 1))
        
        # Limit to max 16 pages to capture full Observations (3.X.1 to 3.X.16)
        if len(page_numbers) > 16:
            print(f"  ⚠️ Range exceptionally large ({len(page_numbers)} pages), limiting to first 16. Check TOC mapping.")
            page_numbers = page_numbers[:16]

        print(f"  🎯 Targeted Pages (with offset {PAGE_OFFSET}): {page_numbers}")

        # 5. Validate headers (safety check)
        validated_pages = self._validate_pages(page_numbers, county_name)
        
        # --- NEW: Dynamic Offset Correction ---
        if not validated_pages or pdf_start not in validated_pages:
             print(f"  🔍 Verification: Page {pdf_start} does not start with {county_name} header. Searching nearby...")
             # Check ±5 pages to find the actual start
             for offset_adj in range(-5, 6):
                 if offset_adj == 0: continue
                 check_page = pdf_start + offset_adj
                 if self._validate_pages([check_page], county_name):
                      print(f"  ✨ Found correct header at page {check_page}! Adjusting offset for this session.")
                      # Adjust all pages in range by this amount
                      page_numbers = [p + offset_adj for p in page_numbers]
                      validated_pages = self._validate_pages(page_numbers, county_name)
                      break

        if not validated_pages:
            print("  ⚠️ Validation failed for all pages, reverting to original range (assuming offset is correct)")
            # If validation fails, we trust the offset more than the validation regex (which might be flaky)
            return page_numbers
            
        print(f"  ✅ Validated page range for {county_name}: {validated_pages}")
        return validated_pages
    
    def get_summary_table_pages(self) -> List[int]:
        """
        Returns pages containing National Summary Tables (Table 2.1, 2.5).
        These are critical for extracting OSR and Exchequer Releases.
        OPTIMIZED: Just get the pages with Table 2.1 data (47-51)
        """
        print("  📊 Adding summary tables (Area A) pages 47-51.")
        # CGBIRR 2025: Summary tables are pages 47-51
        return list(range(47, 52))
    
    def _parse_toc_cgbirr(self):
        """
        Parses TOC pages (2-20) looking for:
        3.1. County Government of Mombasa ................................................. 324
        """
        print("  📖 Parsing Table of Contents (Pages 2-20)...")
        toc_text = ""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # TOC typically pages 2-15
                for i in range(1, min(20, len(pdf.pages))):
                    text = pdf.pages[i].extract_text()
                    if text:
                        toc_text += text + "\n"
        except Exception as e:
            print(f"  ❌ TOC Extraction Error: {e}")
            return
        
        if not toc_text:
            print("  ⚠️ Empty TOC text")
            return
        
        self.toc_map = {}
        self.county_list = []
        self.section_numbers = {} # New: map clean_name -> "3.11"
        
        # Pattern matches: "3.11. County Government of Isiolo ... 107"
        # Group 1: "3.11", Group 2: "Isiolo", Group 3: "107"
        pattern = r'(\d+\.\d+)\.\s+County Government of\s+([A-Za-z\s\'\-]+?)\s+\.+\s*(\d{3,})'
        matches = re.findall(pattern, toc_text)
        
        if not matches:
             print("  ⚠️ Strict dot pattern failed, trying relaxed pattern")
             pattern2 = r'(\d+\.\d+)\.\s+County Government of\s+([A-Za-z\s\'\-]+?)\s+.*?(\d{3})\s*\n'
             matches = re.findall(pattern2, toc_text)
        
        for section, county, page in matches:
            clean_name = county.strip()
            page_num = int(page)
            
            # Sanity check: County pages start around 100+
            if page_num < 40: # Some early tables are low
                continue
                
            self.toc_map[clean_name] = page_num
            self.county_list.append((clean_name, page_num))
            self.section_numbers[clean_name] = section
        
        print(f"  ✅ Parsed {len(self.toc_map)} counties from TOC")
    
    def _normalize_name(self, name: str) -> str:
        """Handle variations like 'Mombasa' vs 'Mombasa County'"""
        return name.lower().replace('county', '').replace('government of', '').strip()
    
    def _validate_pages(self, page_numbers: List[int], county_name: str) -> List[int]:
        """Verify pages contain the county header"""
        valid_pages = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for p in page_numbers:
                    # Convert 1-indexed to 0-indexed for pdfplumber
                    idx = p - 1
                    if idx >= len(pdf.pages):
                        continue
                        
                    text = pdf.pages[idx].extract_text() or ""
                    
                    # Check if this page belongs to our county
                    # Robust check: "County Government of Mombasa" OR "MOMBASA COUNTY"
                    # Robust check: "3.11 COUNTY GOVERNMENT OF ISIOLO"
                    section_num = self.section_numbers.get(county_name, "")
                    
                    if (f"County Government of {county_name}" in text or 
                        (section_num and section_num in text and county_name.upper() in text) or
                        county_name.upper() in text or
                        f"VoteNo:{self._normalize_name(county_name)}" in text.replace(" ", "")):
                        valid_pages.append(p)
                    elif valid_pages:  
                        # We already found the start, and this page doesn't have a NEW county header
                        # So it must be a continuation page
                        # Check if it has a Different county header
                        if "County Government of" in text and county_name not in text:
                            # It's the next county! Stop.
                            break
                        valid_pages.append(p)
                        
        except Exception as e:
            print(f"  ⚠️ Validation warning: {e}")
            return page_numbers # Return original if validation fails technically
            
        return valid_pages if valid_pages else page_numbers
    
    def _hardcoded_fallback(self, county_name: str) -> List[int]:
        """Hardcoded approximate locations for major counties (CGBIRR 2025)"""
        fallback_map = {
            'mombasa': 324,
            'kwale': 328,
            'kilifi': 332,
            'tana river': 336,
            'lamu': 340,
            'taita taveta': 344,
            'garissa': 348,
            'wajir': 352,
            'mandera': 356,
            'marsabit': 360,
            'isiolo': 153,  # Adjusted for August 2025 report
            'meru': 368,
            'tharaka nithi': 372,
            'embu': 376,
            'kitui': 380,
            'machakos': 384,
            'makueni': 388,
            'nyandarua': 392,
            'nyeri': 396,
            'kirinyaga': 400,
            'murang\'a': 404,  # Escape quote
            "murang'a": 404,
            'kiambu': 408,
            'turkana': 412,
            'west pokot': 416,
            'samburu': 420,
            'trans nzoia': 424,
            'uasin gishu': 428,
            'elgeyo marakwet': 432,
            'nandi': 436,
            'baringo': 440,
            'laikipia': 444,
            'nakuru': 448,
            'narok': 452,
            'kajiado': 456,
            'kericho': 460,
            'bomet': 464,
            'kakamega': 468,
            'vihiga': 472,
            'bungoma': 476,
            'busia': 480,
            'siaya': 484,
            'kisumu': 488,
            'homa bay': 492,
            'migori': 496,
            'kisii': 500,
            'nyamira': 504,
            'nairobi': 508
        }
        
        normalized = self._normalize_name(county_name)
        start = fallback_map.get(normalized)
        
        if start:
            print(f"  ⚠️ Using hardcoded map for {county_name}: Page {start}")
            return [start, start+1, start+2, start+3]
            
        print(f"  ❌ Completely failed to locate {county_name}")
        return [324, 325, 326, 327] # Default to Mombasa if all else fails
