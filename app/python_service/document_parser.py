import re
import pdfplumber
from typing import Dict, List, Any, Optional, Tuple

class DocumentParser:
    """
    Advanced document parser for CBIRR reports.
    Handles section detection, TOC extraction, and page range mapping.
    """
    
    def __init__(self):
        self.sections = {}
        self.counties = {}
        self.tables_catalog = []
        self.figures_catalog = []
        
    def parse_document_structure(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Main entry point for parsing document structure.
        """
        print("📄 Starting document structure analysis...")
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            total_pages = len(pdf.pages)
            print(f"📄 Document has {total_pages} pages")
            
            # 1. Extract Table of Contents (if available)
            toc = self._extract_toc(pdf)
            
            # 2. Identify Major Sections (Foreword, Exec Summary, etc.)
            sections = self._identify_major_sections(pdf, toc)
            
            # 3. Identify County Sections
            counties = self._identify_county_sections(pdf, toc)
            
            return {
                "total_pages": total_pages,
                "sections": sections,
                "counties": counties,
                "toc_extracted": bool(toc)
            }

    def _extract_toc(self, pdf) -> List[Dict[str, Any]]:
        """
        Attempt to extract and parse the Table of Contents.
        """
        toc_entries = []
        # Look for TOC in first 20 pages
        for i in range(min(20, len(pdf.pages))):
            page = pdf.pages[i]
            text = page.extract_text() or ""
            
            if "table of contents" in text.lower() or "contents" in text.lower():
                # Simple TOC line parser
                lines = text.split('\n')
                for line in lines:
                    # Match "Section Name ....... 123" pattern
                    match = re.search(r'^(.*?)\.+?\s*(\d+)$', line)
                    if match:
                        title = match.group(1).strip()
                        page_num = int(match.group(2))
                        toc_entries.append({"title": title, "page": page_num})
        
        return toc_entries

    def _identify_major_sections(self, pdf, toc: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        """
        Identify start and end pages for major sections.
        """
        sections = {}
        
        # Standard CBIRR sections
        target_sections = [
            "Foreword", "Executive Summary", "Introduction", 
            "Revenue Analysis", "Expenditure Analysis", 
            "Pending Bills", "Conclusion"
        ]
        
        # Strategy 1: Use TOC if available
        if toc:
            for i, entry in enumerate(toc):
                title = entry["title"].lower()
                for target in target_sections:
                    if target.lower() in title:
                        start_page = entry["page"]
                        # End page is start of next entry - 1
                        end_page = toc[i+1]["page"] - 1 if i+1 < len(toc) else len(pdf.pages)
                        sections[target] = {"start_page": start_page, "end_page": end_page}
                        break
        
        # Strategy 2: Scan headers if TOC failed or incomplete
        if not sections:
            print("⚠️ TOC not found or incomplete, scanning headers...")
            # This is a simplified scan - in production would need more robust header detection
            for i, page in enumerate(pdf.pages):
                text = (page.extract_text() or "").split('\n')[0:5] # Check first 5 lines
                header_text = " ".join(text).lower()
                
                for target in target_sections:
                    if target not in sections and target.lower() in header_text:
                        # Found a section start
                        sections[target] = {"start_page": i + 1, "end_page": i + 1} # End page updated later
                        
                        # Update end page of previous section
                        # (Logic omitted for brevity, would need sorting sections by page)
                        
        return sections

    def _identify_county_sections(self, pdf, toc: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        """
        Identify page ranges for each county.
        """
        counties = {}
        
        # Regex for "County Government of X" or "X County" headers
        county_header_re = re.compile(r'(?:county\s+government\s+of\s+|county\s+)(\w+)', re.IGNORECASE)
        
        # Strategy 1: Use TOC
        if toc:
            for i, entry in enumerate(toc):
                title = entry["title"]
                match = county_header_re.search(title)
                if match:
                    county_name = match.group(1)
                    start_page = entry["page"]
                    end_page = toc[i+1]["page"] - 1 if i+1 < len(toc) else len(pdf.pages)
                    counties[county_name] = {"start_page": start_page, "end_page": end_page}
        
        # Strategy 2: Scan pages (fallback)
        if not counties:
            print("⚠️ Scanning pages for county headers...")
            current_county = None
            current_start = 0
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                # Check first few lines for big headers
                header_lines = text.split('\n')[:3]
                header_text = " ".join(header_lines)
                
                match = county_header_re.search(header_text)
                if match:
                    new_county = match.group(1)
                    # Filter out common false positives
                    if new_county.lower() in ['assembly', 'executive', 'treasury']:
                        continue
                        
                    if new_county != current_county:
                        if current_county:
                            counties[current_county]["end_page"] = i
                        
                        counties[new_county] = {"start_page": i + 1, "end_page": i + 1}
                        current_county = new_county
            
            if current_county:
                counties[current_county]["end_page"] = len(pdf.pages)
                
        return counties

import io
