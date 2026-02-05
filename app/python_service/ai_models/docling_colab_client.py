import os
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class DoclingColabClient:
    """
    Client to communicate with Docling running on Google Colab (via ngrok).
    """
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("DOCLING_COLAB_URL", "").strip().rstrip('/')
        
    def is_available(self) -> bool:
        """Checks if the Colab server is reachable."""
        if not self.base_url:
            return False
        try:
            response = requests.get(self.base_url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    async def convert(self, pdf_path: str, county: str) -> Dict:
        """
        Sends the PDF to Colab for conversion and requests data for a specific county.
        """
        if not self.base_url:
            raise ValueError("DOCLING_COLAB_URL is not set in environment variables.")

        url = f"{self.base_url}/convert"
        
        try:
            logger.info(f"📤 Sending PDF to Colab Docling: {pdf_path} (County: {county})")
            
            with open(pdf_path, 'rb') as f:
                files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
                data = {'county': county}
                response = requests.post(url, files=files, data=data, timeout=300) # 5 min timeout
                
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_json = response.json()
                    error_detail = error_json.get("detail", response.text)
                except:
                    error_detail = response.text
                raise Exception(f"Colab extraction failed (HTTP {response.status_code}): {error_detail}")
                
            result = response.json()
            
            if not result.get("success"):
                raise Exception(f"Colab extraction failed: {result.get('detail', 'Unknown error')}")
                
            return {
                "markdown": result.get("markdown", ""),
                "county": result.get("county", ""),
                "filename": result.get("filename", "")
            }
            
        except requests.exceptions.Timeout:
            logger.error("❌ Docling Colab request timed out.")
            raise Exception("Colab Docling request timed out. This usually happens on the first run as models load.")
        except Exception as e:
            logger.error(f"❌ Docling Colab error: {str(e)}")
            raise e
