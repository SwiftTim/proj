
import asyncio
import sys
import os

# Ensure we can import from current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ["GROQ_API_KEY"] = "dummy"
os.environ["HF_API_KEY"] = "dummy"

from hybrid_processor import HybridBudgetProcessor
from ai_models.ocrflux_client import OCRFluxClient
from ai_models.groq_client import GroqAnalyzer

# Mock classes
class MockOCRFluxClient(OCRFluxClient):
    async def extract(self, pdf_path, county_name, target_tables):
        print("Mock OCRFlux Extract called")
        from ai_models.ocrflux_client import ExtractionResult
        return ExtractionResult(
            markdown=f"### {county_name}\n| County | Target | Actual | % |\n| {county_name} | 1,000 | 500 | 50% |",
            raw_text="...",
            confidence=0.9,
            pages_processed=1
        )

class MockGroqAnalyzer(GroqAnalyzer):
    async def analyze(self, structured_data, county_name, context_snippets):
        print("Mock Groq Analyze called")
        return {
            "risk_assessment": {"level": "High", "score": 80},
            "executive_summary": "Test Summary",
            "integrity_scores": {"overall": 50}
        }

async def test_pipeline():
    print("Testing Hybrid Pipeline Construction...")
    
    # Initialize processor
    processor = HybridBudgetProcessor()
    
    # Patch with mocks
    processor.ocrflux = MockOCRFluxClient(processor.ocrflux.config)
    processor.groq = MockGroqAnalyzer(processor.groq.config)
    
    # Run
    pdf_path = "dummy.pdf" 
    county = "Mombasa"
    
    try:
        result = await processor.process(pdf_path, county)
        print("Pipeline Result Keys:", result.keys())
        print("Extraction Revenue:", result['extraction']['revenue'])
        print("Validation Passed:", result['metadata']['validation_passed'])
        print("✅ Test Passed!")
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pipeline())
