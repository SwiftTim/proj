from typing import Dict, List, Any
import pandas as pd

class ComparisonEngine:
    """
    Engine for comparing counties and generating rankings.
    """
    
    def compare_counties(self, county_a_data: Dict[str, Any], county_b_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two counties side-by-side.
        """
        metrics = {
            "revenue": {
                "label": "Total Revenue",
                "a": county_a_data.get("revenue", {}).get("revenue_actual", 0),
                "b": county_b_data.get("revenue", {}).get("revenue_actual", 0),
                "format": "currency"
            },
            "expenditure": {
                "label": "Total Expenditure",
                "a": county_a_data.get("expenditure", {}).get("total_expenditure", 0),
                "b": county_b_data.get("expenditure", {}).get("total_expenditure", 0),
                "format": "currency"
            },
            "absorption": {
                "label": "Absorption Rate",
                "a": county_a_data.get("computed", {}).get("overall_absorption_percent", 0),
                "b": county_b_data.get("computed", {}).get("overall_absorption_percent", 0),
                "format": "percent"
            },
            "pending_bills": {
                "label": "Pending Bills",
                "a": county_a_data.get("debt_and_liabilities", {}).get("pending_bills_amount", 0),
                "b": county_b_data.get("debt_and_liabilities", {}).get("pending_bills_amount", 0),
                "format": "currency"
            },
            "development_ratio": {
                "label": "Dev. Expenditure Ratio",
                "a": self._calculate_dev_ratio(county_a_data),
                "b": self._calculate_dev_ratio(county_b_data),
                "format": "percent"
            }
        }
        
        # Calculate differences and winners
        for key, m in metrics.items():
            m["diff"] = m["a"] - m["b"]
            m["diff_percent"] = (m["diff"] / m["b"] * 100) if m["b"] != 0 else 0
            
            # Determine "better" (higher is better for rev/abs, lower for debt)
            if key == "pending_bills":
                m["winner"] = "a" if m["a"] < m["b"] else "b"
            else:
                m["winner"] = "a" if m["a"] > m["b"] else "b"
                
        return {
            "county_a": county_a_data["county"],
            "county_b": county_b_data["county"],
            "metrics": metrics
        }

    def rank_counties(self, all_counties_data: List[Dict[str, Any]], metric: str) -> List[Dict[str, Any]]:
        """
        Rank all counties by a specific metric.
        """
        ranked = []
        for data in all_counties_data:
            val = 0
            if metric == "revenue":
                val = data.get("revenue", {}).get("revenue_actual", 0)
            elif metric == "absorption":
                val = data.get("computed", {}).get("overall_absorption_percent", 0)
            elif metric == "pending_bills":
                val = data.get("debt_and_liabilities", {}).get("pending_bills_amount", 0)
            
            ranked.append({
                "county": data["county"],
                "value": val
            })
            
        # Sort (descending for most, ascending for bills)
        reverse = metric != "pending_bills"
        ranked.sort(key=lambda x: x["value"], reverse=reverse)
        
        # Add rank index
        for i, item in enumerate(ranked):
            item["rank"] = i + 1
            
        return ranked

    def _calculate_dev_ratio(self, data):
        try:
            dev = data.get("expenditure", {}).get("development_expenditure", 0)
            total = data.get("expenditure", {}).get("total_expenditure", 0)
            return (dev / total * 100) if total > 0 else 0
        except:
            return 0
