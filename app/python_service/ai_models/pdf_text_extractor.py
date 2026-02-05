"""
Fallback PDF Text Extractor
Used when OCRFlux is not available
Extracts text directly from PDF using pypdf
"""

import pypdf
import re
from typing import List


class ContextAwareSlicer:
    """
    Slices raw county text into labeled buckets based on CGBIRR standard headers.
    This prevents the AI from mixing up 'Arrears' with 'Actual Revenue'.
    """
    
    @staticmethod
    def get_section_content(text: str, section_header: str) -> str:
        """
        Fences the text so the AI only looks at the specific sub-chapter.
        Example: section_header = "3.11.2 Own-Source Revenue"
        Matches up to the next 3.X.X numbered header.
        """
        # Find start of section and end before the next numbered header (3.d.d or 3.d County)
        # We use [0-9]+\.[0-9]+\.[0-9]+ to match headers like 3.11.3
        # We also stop at the next main county header like 3.12. County Government
        pattern = rf"{re.escape(section_header)}.*?(?=\d+\.\d+\.\d+|\d+\.\d+\.\s+County Government|$)"
        match = re.search(pattern, text, re.S | re.IGNORECASE)
        return match.group(0).strip() if match else ""

    @staticmethod
    def slice_text(raw_text: str) -> dict:
        # Standard CGBIRR Header Patterns for Chapter 3 (County Detail)
        # Section 3.X.2 is OSR, 3.X.5 is Exchequers (Total Revenue), 3.X.7 is Pending Bills
        patterns = {
            "revenue_actual": r"3\.\d+\.2\s+(?:Own[-\s]Source Revenue|OSR)",
            "revenue_arrears": r"3\.\d+\.3\s+Revenue Arrears",
            "exchequer": r"3\.\d+\.5\s+(?:Exchequer(?:s)? Approved|Total Funds Released|Exchequer Releases)",
            "expenditure": r"3\.\d+\.6\s+County Expenditure Review",
            "pending_bills": r"3\.\d+\.7\s+Settlement of Pending Bills",
            "narrative": r"3\.\d+\.10\s+Observations and Recommendations|3\.\d+\.\d+\s+Executive Summary",
            "recommendations": r"3\.\d+\.16\s+Observations and Recommendations"
        }
        
        sections = {key: "Section not found in text" for key in patterns}
        
        # Sort headers by their appearance in the text
        found_markers = []
        for key, pattern in patterns.items():
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                # Capture the actual header found and its position
                found_markers.append((key, match.start(), match.group(0)))
        
        found_markers.sort(key=lambda x: x[1])
        
        # Slice the text between markers using the 'fencing' logic
        for i in range(len(found_markers)):
            key, start_pos, header_text = found_markers[i]
            # Content lasts until the next numbered header or end of text
            content = ContextAwareSlicer.get_section_content(raw_text[start_pos:], header_text)
            sections[key] = content
            
        return sections


class PDFTextExtractor:
    """
    Fallback extractor when OCRFlux/vision models are not available
    Uses pypdf to extract text directly from PDF
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.reader = pypdf.PdfReader(pdf_path)
    
    def extract_pages(self, page_numbers: List[int]) -> str:
        """
        Extract text from specific pages
        
        Args:
            page_numbers: List of page numbers (1-indexed)
        
        Returns:
            Concatenated text from all pages in markdown-like format
        """
        all_text = []
        
        for page_num in page_numbers:
            try:
                # Convert to 0-indexed
                page_idx = page_num - 1
                
                if page_idx < 0 or page_idx >= len(self.reader.pages):
                    continue
                
                page = self.reader.pages[page_idx]
                text = page.extract_text() or ""
                
                if text.strip():
                    all_text.append(f"--- Page {page_num} ---\n{text}\n")
                    print(f"    ✅ Extracted text from page {page_num} ({len(text)} chars)")
                else:
                    print(f"    ⚠️  Page {page_num} has no extractable text")
                    
            except Exception as e:
                print(f"    ❌ Error extracting page {page_num}: {e}")
                continue
        
        return "\n\n".join(all_text)

    def extract_tagged_sections(self, sections: dict) -> str:
        """
        Extract pages and wrap them in XML-like tags for context separation.
        Args:
            sections: Dict like {"NATIONAL_SUMMARY": [47,48], "COUNTY_DETAIL": [100,101]}
        Returns:
            String with tagged content
        """
        final_output = []
        for tag, pages in sections.items():
            content = self.extract_pages(pages)
            final_output.append(f"<{tag}>\n{content}\n</{tag}>")
        
        return "\n\n".join(final_output)
    
    def extract_page_range(self, start_page: int, end_page: int) -> str:
        """
        Extract text from a range of pages
        
        Args:
            start_page: Start page (1-indexed, inclusive)
            end_page: End page (1-indexed, inclusive)
        
        Returns:
            Concatenated text from all pages
        """
        page_numbers = list(range(start_page, end_page + 1))
        return self.extract_pages(page_numbers)
