from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
)
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat, DocumentInput
import logging

logger = logging.getLogger(__name__)

def run_docling_extraction(pdf_path, target_pages):
    """
    Extracts structured content from a PDF using Docling.
    
    Args:
        pdf_path (str): Path to the PDF file.
        target_pages (list): List of page numbers to extract.
    
    Returns:
        str: Extracted content in Markdown format.
    """
    try:
        logger.info(f"Starting Docling extraction for {pdf_path}, pages: {target_pages}")
        
        # Enable Table Structure Recognition
        options = PdfPipelineOptions()
        options.do_table_structure = True
        options.do_ocr = True  # Fallback for scanned segments
        
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=options)
            }
        )
        
        # Convert specific pages
        doc = DocumentInput.from_file(pdf_path)
        result = converter.convert(doc, pages=target_pages)
        
        # Export to Markdown - This is the "Meaningful Data" format for Groq
        markdown_output = result.document.export_to_markdown()
        
        logger.info("Docling extraction completed successfully.")
        return markdown_output
        
    except Exception as e:
        logger.error(f"Error during Docling extraction: {str(e)}")
        raise e
