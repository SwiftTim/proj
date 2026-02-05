from typing import Dict, List, Any
from ai_models.ocrflux_client import ExtractionResult

class ValidationResult:
    def __init__(self, is_valid: bool, errors: List[str], confidence: float):
        self.is_valid = is_valid
        self.errors = errors
        self.confidence = confidence

class DataValidator:
    """
    Sanity checks between OCRFlux extraction and Groq analysis
    Prevents hallucinations and data inconsistencies
    """
    
    def check_extraction(self, extraction: ExtractionResult) -> ValidationResult:
        errors = []
        
        # Check 1: Confidence threshold
        # If confidence is missing or very low
        if extraction.confidence < 0.5: # Lowered threshold slightly for testing
            errors.append(f"Low OCR confidence ({extraction.confidence:.2f})")
        
        # Check 2: Required fields present
        # Check for at least some markdown tabular data
        if "|" not in extraction.markdown:
            errors.append("No financial data table structure (|) detected in markdown")
        
        # Check 3: Reasonable length
        if len(extraction.markdown) < 50:
            errors.append("Extraction too short, likely missed tables")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            confidence=extraction.confidence
        )
    
    def validate_math(self, data: Dict) -> bool:
        """
        Verify calculations: OSR Actual/OSR Target should equal OSR Performance %
        """
        try:
            rev = data.get('revenue', {})
            if rev.get('osr_target', 0) > 0:
                calc_pct = (rev['osr_actual'] / rev['osr_target']) * 100
                reported_pct = rev.get('osr_performance_pct', 0)
                
                # Allow 5% variance due to rounding in reports
                if abs(calc_pct - reported_pct) > 5:
                    return False
            
            # Check expenditure totals if available
            exp = data.get('expenditure', {})
            rec = exp.get('recurrent_expenditure', 0)
            dev = exp.get('development_expenditure', 0)
            total = exp.get('total_expenditure', 0)
            
            if total > 0 and (rec > 0 or dev > 0):
                if abs((rec + dev) - total) > 1000: # Allow small rounding diff
                    return False
            
            return True
        except Exception as e:
            print(f"Validation Math Error: {e}")
            return False
