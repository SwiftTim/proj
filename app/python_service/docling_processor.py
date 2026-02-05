import os
import json
import logging
import tempfile
from typing import Dict, List, Optional
from ai_models.smart_page_locator import SmartPageLocator
from ai_models.docling_colab_client import DoclingColabClient
from ai_models.groq_client import GroqAnalyzer
from hybrid_processor import GroqConfig
import asyncio
from pypdf import PdfReader, PdfWriter

logger = logging.getLogger(__name__)

class DoclingProcessor:
    def __init__(self, groq_config=None):
        self.groq = GroqAnalyzer(groq_config or GroqConfig())
        self.colab_client = DoclingColabClient()
        
    async def process(self, pdf_path: str, county_name: str) -> Dict:
        """
        Executes the Docling-Colab based extraction. 
        Note: Currently configured to skip Groq interpretation and return direct Markdown for the county.
        """
        temp_slice_path = None
        try:
            logger.info(f"🚀 Starting Docling-Colab Pipeline for {county_name}")
            
            # Step A & B: Page Slicing
            locator = SmartPageLocator(pdf_path)
            county_pages = locator.locate_county_pages(county_name)
            summary_pages = locator.get_summary_table_pages()
            
            # Combine and sort pages (convert to 0-indexed for pypdf)
            target_pages_1_indexed = sorted(list(set(county_pages + summary_pages)))
            logger.info(f"📍 Targeting pages (1-indexed): {target_pages_1_indexed}")
            
            # --- LOCAL SLICING ---
            with tempfile.NamedTemporaryFile(delete=False, suffix="_sliced.pdf") as tmp:
                temp_slice_path = tmp.name
                
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            for p_num in target_pages_1_indexed:
                if 0 < p_num <= len(reader.pages):
                    writer.add_page(reader.pages[p_num - 1])
            
            with open(temp_slice_path, "wb") as f:
                writer.write(f)
            
            logger.info(f"📄 Local slice created: {temp_slice_path} ({len(target_pages_1_indexed)} pages)")

            # Step C: Docling Conversion via Colab (Passing County name)
            result_colab = await self.colab_client.convert(temp_slice_path, county_name)
            county_markdown = result_colab.get("markdown", "")
            
            if not county_markdown:
                return {"status": "error", "error": "Colab Docling extraction produced empty markdown."}

            logger.info(f"📝 Markdown received from Colab for {county_name}")
            
            # --- SKIP GROQ INTERPRETATION FOR NOW ---
            # We return the markdown directly so the frontend can display the clean table
            
            return {
                "status": "success",
                "method": "docling_colab_direct",
                "county": county_name,
                "data": {
                    "interpreted_data": {
                        "county": county_name,
                        "key_metrics": {
                            "total_budget": "See Table below",
                            "total_revenue": "See Table below",
                            "total_expenditure": "See Table below",
                            "own_source_revenue": "See Table below",
                            "pending_bills": "See Table below",
                            "osr_target": "See Table below"
                        },
                        "summary_text": f"### Direct Docling Extraction for {county_name}\n\n{county_markdown}",
                        "intelligence": {
                            "verdict": "Direct Extract",
                            "citizen_summary": f"This is the direct data for {county_name} extracted from the budget report.",
                            "pillars": {
                                "revenue": "See extracted table above",
                                "expenditure": "See extracted table above",
                                "liability": "See extracted table above"
                            },
                            "auditor_key_figures": {}
                        }
                    },
                    "metadata": {
                        "processing_method": "docling_direct_markdown",
                        "pages_processed": target_pages_1_indexed,
                        "markdown_length": len(county_markdown)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Docling-Colab Pipeline failed: {str(e)}")
            return {"status": "error", "error": str(e)}
        finally:
            if temp_slice_path and os.path.exists(temp_slice_path):
                os.remove(temp_slice_path)
