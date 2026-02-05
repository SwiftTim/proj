from typing import Dict, List, Optional
from difflib import SequenceMatcher
import json

class MeritMapper:
    """
    Maps trending fiscal "hot takes" to specific CBIRR data fields.
    
    Uses keyword matching and fuzzy logic to link topics like "Teacher Salaries"
    to actual budget data fields like "Personnel Emoluments".
    """
    
    # Comprehensive mapping of keywords to CBIRR data fields
    FIELD_MAPPINGS = {
        "personnel_emoluments": {
            "keywords": ["salary", "salaries", "wage", "wages", "teacher", "doctors", "nurses", 
                        "staff", "personnel", "emoluments", "compensation", "payroll"],
            "display_name": "Personnel Emoluments",
            "data_path": "expenditure.personnel_emoluments"
        },
        "pending_bills": {
            "keywords": ["pending bills", "arrears", "debt", "unpaid", "outstanding", 
                        "liabilities", "creditors"],
            "display_name": "Pending Bills",
            "data_path": "debt.pending_bills"
        },
        "osr_actual": {
            "keywords": ["own source revenue", "osr", "local revenue", "collection", 
                        "revenue performance", "taxes", "fees", "charges"],
            "display_name": "Own Source Revenue (Actual)",
            "data_path": "revenue.own_source_revenue"
        },
        "osr_target": {
            "keywords": ["revenue target", "osr target", "collection target", 
                        "revenue projection"],
            "display_name": "OSR Target",
            "data_path": "revenue.osr_target"
        },
        "health_allocation": {
            "keywords": ["health", "healthcare", "medical", "hospital", "clinic", 
                        "health services", "health funding"],
            "display_name": "Health Sector Allocation",
            "data_path": "sectoral_allocations.health"
        },
        "education_allocation": {
            "keywords": ["education", "schools", "learning", "ecde", "vocational training"],
            "display_name": "Education Sector Allocation",
            "data_path": "sectoral_allocations.education"
        },
        "infrastructure_allocation": {
            "keywords": ["infrastructure", "roads", "construction", "public works", 
                        "transport", "bridges"],
            "display_name": "Infrastructure Allocation",
            "data_path": "sectoral_allocations.infrastructure"
        },
        "development_expenditure": {
            "keywords": ["development", "capital", "projects", "investment", 
                        "infrastructure development"],
            "display_name": "Development Expenditure",
            "data_path": "expenditure.development_expenditure"
        },
        "recurrent_expenditure": {
            "keywords": ["recurrent", "operations", "maintenance", "running costs"],
            "display_name": "Recurrent Expenditure",
            "data_path": "expenditure.recurrent_expenditure"
        },
        "total_revenue": {
            "keywords": ["total revenue", "revenue", "income", "receipts"],
            "display_name": "Total Revenue",
            "data_path": "revenue.total_revenue"
        },
        "total_expenditure": {
            "keywords": ["total expenditure", "spending", "expenses", "disbursement"],
            "display_name": "Total Expenditure",
            "data_path": "expenditure.total_expenditure"
        },
        "absorption_rate": {
            "keywords": ["absorption", "utilization", "spending rate", "budget execution"],
            "display_name": "Budget Absorption Rate",
            "data_path": "expenditure.absorption_rate"
        }
    }
    
    def __init__(self):
        pass
    
    def fuzzy_match(self, text1: str, text2: str) -> float:
        """
        Calculate similarity ratio between two strings.
        
        Args:
            text1: First string
            text2: Second string
        
        Returns:
            float: Similarity ratio (0.0 to 1.0)
        """
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def map_keywords_to_fields(self, keywords: List[str]) -> List[Dict]:
        """
        Maps a list of keywords to CBIRR data fields.
        
        Args:
            keywords: List of keywords from hot take
        
        Returns:
            List of matched fields with confidence scores
        """
        matches = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            for field_id, field_info in self.FIELD_MAPPINGS.items():
                # Check for exact or partial matches
                for mapped_keyword in field_info["keywords"]:
                    similarity = self.fuzzy_match(keyword_lower, mapped_keyword)
                    
                    # If similarity is high enough, consider it a match
                    if similarity > 0.7:
                        matches.append({
                            "field_id": field_id,
                            "field_name": field_info["display_name"],
                            "data_path": field_info["data_path"],
                            "matched_keyword": keyword,
                            "confidence": round(similarity, 2)
                        })
                        break  # Move to next keyword once we find a match
        
        # Remove duplicates and sort by confidence
        unique_matches = {}
        for match in matches:
            field_id = match["field_id"]
            if field_id not in unique_matches or match["confidence"] > unique_matches[field_id]["confidence"]:
                unique_matches[field_id] = match
        
        return sorted(unique_matches.values(), key=lambda x: x["confidence"], reverse=True)
    
    def map_hot_take(self, hot_take: Dict) -> Dict:
        """
        Maps a complete hot take to relevant data fields.
        
        Args:
            hot_take: Hot take object with keywords
        
        Returns:
            Enhanced hot take with mapped fields
        """
        keywords = hot_take.get("keywords", [])
        mapped_fields = self.map_keywords_to_fields(keywords)
        
        # Add mapped fields to hot take
        enhanced_hot_take = {
            **hot_take,
            "mapped_data_fields": mapped_fields,
            "primary_field": mapped_fields[0] if mapped_fields else None,
            "visualization_type": self._determine_viz_type(hot_take, mapped_fields)
        }
        
        return enhanced_hot_take
    
    def _determine_viz_type(self, hot_take: Dict, mapped_fields: List[Dict]) -> str:
        """
        Determines the best visualization type for the hot take.
        
        Args:
            hot_take: Hot take object
            mapped_fields: List of mapped fields
        
        Returns:
            str: Visualization type (bar, line, pie, comparison)
        """
        topic_lower = hot_take.get("topic_name", "").lower()
        
        # Trend analysis
        if any(word in topic_lower for word in ["trend", "growth", "decline", "over time"]):
            return "line"
        
        # Comparison analysis
        if any(word in topic_lower for word in ["vs", "versus", "compared to", "gap", "difference"]):
            return "comparison"
        
        # Distribution analysis
        if any(word in topic_lower for word in ["allocation", "distribution", "breakdown"]):
            return "pie"
        
        # Default to bar chart for most cases
        return "bar"
    
    def get_field_info(self, field_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific field.
        
        Args:
            field_id: Field identifier
        
        Returns:
            Dict with field information or None
        """
        return self.FIELD_MAPPINGS.get(field_id)
    
    def extract_data_from_analysis(self, analysis_data: Dict, data_path: str) -> Optional[float]:
        """
        Extracts a specific value from analysis data using dot notation path.
        
        Args:
            analysis_data: The interpreted_data from budget analysis
            data_path: Dot notation path (e.g., "revenue.osr_actual")
        
        Returns:
            Extracted value or None
        """
        try:
            keys = data_path.split(".")
            value = analysis_data
            
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return None
            
            return value
        except Exception as e:
            print(f"⚠️ Data extraction error for path {data_path}: {e}")
            return None


# Test function
if __name__ == "__main__":
    mapper = MeritMapper()
    
    # Test hot take
    test_hot_take = {
        "topic_name": "Teacher Salary Arrears Crisis",
        "description": "Multiple counties struggling with teacher salary payments",
        "keywords": ["teacher", "salaries", "pending bills", "arrears"],
        "priority_score": 8
    }
    
    result = mapper.map_hot_take(test_hot_take)
    print(json.dumps(result, indent=2))
