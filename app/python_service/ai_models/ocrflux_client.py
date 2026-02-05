import requests
import json
import base64
import os
from typing import Dict, List, Optional
import pdf2image
import io
import asyncio
import re

class ExtractionResult:
    def __init__(self, markdown: str, raw_text: str, confidence: float, pages_processed: int):
        self.markdown = markdown
        self.raw_text = raw_text
        self.confidence = confidence
        self.pages_processed = pages_processed

class OCRFluxClient:
    """
    Client for OCRFlux-3B Vision Model
    Handles PDF → Markdown table extraction
    """
    
    def __init__(self, config):
        self.config = config
        # Prioritize ENV variable for Colab/Ngrok URL (OpenAIv1 format)
        self.api_url = os.getenv("OCRFLUX_URL") or getattr(config, 'local_url', None)
        
        # Legacy/Fallback (probably unused)
        self.hf_url = "https://api-inference.huggingface.co/models/mradermacher/OCRFlux-3B-GGUF"
        
    async def extract(self, pdf_path: str, county_name: str, target_tables: List[str]) -> ExtractionResult:
        """
        OPTIMIZED: Convert PDF pages to images, send to OCRFlux, get structured markdown.
        Uses SmartPageLocator for TOC-based intelligent page discovery.
        
        Before: Scans 800 pages → timeout/zeros
        After: Processes 5-10 targeted pages → fast, accurate
        """
        from .smart_page_locator import SmartPageLocator
        
        relevant_pages = set()
        
        # 1. SMART Page Discovery using TOC
        print(f"🔍 Smart Discovery: Locating {county_name} using TOC-based algorithm...")
        
        summary_pages = []
        county_pages = []
        
        try:
            locator = SmartPageLocator(pdf_path)
            
            # Area A: Summary Tables (Pages 47-51)
            summary_pages = locator.get_summary_table_pages()
            if summary_pages:
                print(f"  📊 Found {len(summary_pages)} summary table pages: {summary_pages}...")
            
            # Area B: County-Specific Section
            county_pages = locator.locate_county_pages(county_name)
            if county_pages:
                print(f"  📍 Located {county_name} section: pages {county_pages}")
            else:
                print(f"  ⚠️ Could not locate {county_name}, using fallback")
                    
        except Exception as e:
            print(f"⚠️ Smart discovery failed: {e}. Falling back to default range.")
        
        # Merge for visual processing (if we were using vision), but we use fallback now
        relevant_pages = set(summary_pages + county_pages)
        
        # Fallback if no pages found
        if not relevant_pages:
            print("⚠️ Using fallback page range")
            target_list = [45, 50, 55, 60, 300, 305, 310, 315] 
            # Treat all as county pages if fallback
            county_pages = target_list
            summary_pages = []
        else:
            target_list = sorted(list(relevant_pages))
            
        print(f"📄 Processing {len(target_list)} targeted pages: {target_list}")
        
        # Fallback if no pages found
        if not relevant_pages:
            print("⚠️ Using fallback page range")
            target_list = [45, 50, 55, 60, 300, 305, 310, 315] # Common CGBIRR pages
        else:
            target_list = sorted(list(relevant_pages))
            
        print(f"📄 Processing {len(target_list)} targeted pages: {target_list}")
        
        # 2. Convert Targeted PDF pages to images
        all_markdown = []
        confidences = []
        pages_processed = 0

        
        # Check if we should use API or Fallback immediately (if no API keys)
        use_fallback = False
        if not self.api_url:
            print("⚠️ No OCRFlux API URL configured. Using direct PDF extraction fallback.")
            use_fallback = True
            
        if not use_fallback:
            loop = asyncio.get_event_loop()
            for page_num in target_list:
                try:
                    # Capture Image (using pdf2image)
                    print(f"  📸 Capturing Page {page_num}...")
                    images = await loop.run_in_executor(
                        None, 
                        lambda: pdf2image.convert_from_path(pdf_path, first_page=page_num, last_page=page_num, dpi=200)
                    )
                    
                    if not images:
                        print(f"    ⚠️ Could not convert page {page_num}")
                        continue
                        
                    img = images[0]
                    
                    # Convert to bytes
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    img_bytes = img_byte_arr.getvalue()
                    
                    # Call Vision API
                    result = await self._call_vision_api(img_bytes)
                    
                    if result and len(result.get('text', '').strip()) > 50:
                        all_markdown.append(f"--- Page {page_num} ---\n" + result['text'])
                        confidences.append(result.get('confidence', 0.8))
                        pages_processed += 1
                        print(f"    ✅ Extracted {len(result['text'])} chars via API")
                    else:
                        text_len = len(result.get('text', '')) if result else 0
                        print(f"    ❌ API returned empty/short text for Page {page_num} (len={text_len})")
                        # If API fails for one page, it likely fails for all (e.g. 404/Connection)
                        # Switch to fallback for remaining pages + current page
                        print("    ⚠️ Switching to fallback mode for this and remaining pages")
                        use_fallback = True
                        break  # Break loop to start fallback
                        
                except Exception as e:
                    print(f"    ❌ Error processing page {page_num}: {e}")
                    use_fallback = True
                    break
        
        # Merge markdown from successful API calls
        full_markdown = "\n\n".join(all_markdown)

        # Execute Fallback if needed
        if use_fallback:
            print(f"🔄 Executing Fallback Extraction for {len(target_list)} pages with Context Tagging...")
            
            tags = {
                "NATIONAL_SUMMARY_CONTEXT": summary_pages,
                "COUNTY_SPECIFIC_DETAIL": county_pages
            }
            
            # Pass dictionary for tagged extraction
            fallback_text = self._fallback_extract_text(pdf_path, page_numbers=[], sections=tags)
            
            if len(fallback_text) > 100:
                print(f"  ✅ Fallback produced tagged text ({len(fallback_text)} chars). Using fallback.")
                full_markdown = fallback_text
            elif not full_markdown:
                 full_markdown = fallback_text
                
        # 3. Post-Process
        if not full_markdown:
             # Final desperation fallback
             tags = {"NATIONAL_SUMMARY_CONTEXT": summary_pages, "COUNTY_SPECIFIC_DETAIL": county_pages}
             fallback_text = self._fallback_extract_text(pdf_path, [], sections=tags)
             full_markdown = fallback_text
             
        if not full_markdown:
             return ExtractionResult(
                markdown="",
                raw_text="", # Changed from tables=[] and metadata={}
                confidence=0.0,
                pages_processed=0
            )
        
        # Isolate specific county data (post-processing)
        # SKIP isolation if we are using tagged context, as we want the LLM to see both summary and detail
        if "<NATIONAL_SUMMARY_CONTEXT>" in full_markdown:
            county_section = full_markdown
        else:
            county_section = self._isolate_county(full_markdown, county_name) 
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return ExtractionResult(
            markdown=county_section,
            raw_text=full_markdown,
            confidence=avg_confidence,
            pages_processed=pages_processed
        )
    
    async def _call_vision_api(self, image_bytes: bytes) -> Optional[Dict]:
        """
        Call OCRFlux via vLLM (OpenAI-compatible) API via Ngrok
        """
        # DISABLED: OCRFlux is broken, always use fallback
        return None
        
        # 1. URL Check
        target_url = self.api_url

        # 2. Encode Image
        try:
            img_base64 = base64.b64encode(image_bytes).decode('utf-8')
        except Exception as e:
            print(f"    ❌ Base64 encoding failed: {e}")
            return None

        # 3. Prepare Payload
        payload = {
            "model": "/content/models/ocrflux.gguf",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Convert this PDF page to clean Markdown table format. Focus on financial data."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                    ]
                }
            ],
            "max_tokens": 4096,
            "temperature": 0.1
        }

        # 4. Execute Request
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    target_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=120
                )
            )
            
            if response.status_code == 200:
                print(f"    ✅ Page processed successfully")
                try:
                    res_json = response.json()
                    content = res_json['choices'][0]['message']['content']
                    return {
                        'text': content,
                        'confidence': 0.95
                    }
                except Exception as e:
                     print(f"    ⚠️ JSON Parse Error: {e}")
                     return None
            else:
                print(f"    ❌ API Error {response.status_code}: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"    ❌ API Connection Failed: {e}")
            return None


    def _fallback_extract_text(self, pdf_path: str, page_numbers: List[int], sections: Dict = None) -> str:
        """
        Fallback: Extract text directly from PDF using pypdf if Vision API fails
        """
        from .pdf_text_extractor import PDFTextExtractor
        
        try:
            extractor = PDFTextExtractor(pdf_path)
            
            if sections:
                print(f"  ⚠️ Switching to Fallback Text Extraction with Context Tagging...")
                return extractor.extract_tagged_sections(sections)
            else:
                print(f"  ⚠️ Switching to Fallback Text Extraction for {len(page_numbers)} pages...")
                return extractor.extract_pages(page_numbers)
                
        except Exception as e:
            print(f"  ❌ Fallback extraction failed: {e}")
            return ""
    
    def _isolate_county(self, markdown: str, county_name: str) -> str:
        """
        Extract only the relevant county section from full markdown
        Uses regex to find county header and next county header
        """
        # Pattern: Find "### 47. County Government of Mombasa" or similar
        # Improved pattern to be more flexible
        pattern = rf"(###?\s*\d*\.?\s*County Government of {re.escape(county_name)}.*?)(?=###?\s*\d*\.?\s*County Government of|\Z)"
        match = re.search(pattern, markdown, re.IGNORECASE | re.DOTALL)
        
        if match:
            return match.group(1)
        
        # Fallback: If we find the county name anywhere (even without headers), return full text
        # This is CRITICAL for summary tables where the county is just a row
        if county_name.lower() in markdown.lower().replace(" ", ""):
             return markdown
             
        # Second fallback: If there are tables but no clear county, still return it for the LLM to decide
        if "|" in markdown:
             return markdown
             
        return markdown # Return everything as fallback
