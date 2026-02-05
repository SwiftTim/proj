from typing import Dict, List, Any

class AIInsightGenerator:
    """
    Generates AI-driven insights, risk flags, and recommendations.
    """
    
    def generate_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive insights from county data.
        """
        insights = {
            "anomalies": [],
            "risk_flags": [],
            "trends": [],
            "recommendations": []
        }
        
        # 1. Revenue Analysis
        rev = data.get("revenue", {})
        target = rev.get("revenue_target", 0)
        actual = rev.get("revenue_actual", 0)
        
        if target > 0:
            perf = (actual / target) * 100
            if perf < 50:
                insights["risk_flags"].append({
                    "severity": "Critical",
                    "message": f"Critically low revenue performance ({perf:.1f}%)",
                    "category": "Revenue"
                })
            elif perf < 80:
                insights["risk_flags"].append({
                    "severity": "Warning",
                    "message": f"Below target revenue performance ({perf:.1f}%)",
                    "category": "Revenue"
                })
                
        # 2. Expenditure Analysis
        exp = data.get("expenditure", {})
        dev_exp = exp.get("development_expenditure", 0)
        total_exp = exp.get("total_expenditure", 0)
        
        if total_exp > 0:
            dev_ratio = (dev_exp / total_exp) * 100
            if dev_ratio < 30:
                insights["risk_flags"].append({
                    "severity": "Critical",
                    "message": f"Failed 30% Development Rule (Actual: {dev_ratio:.1f}%)",
                    "category": "Compliance"
                })
                insights["recommendations"].append(
                    "Prioritize development spending to meet the 30% PFM Act requirement."
                )
                
        # 3. Pending Bills
        debt = data.get("debt_and_liabilities", {})
        bills = debt.get("pending_bills_amount", 0)
        
        if actual > 0 and bills > 0:
            bill_ratio = (bills / actual) * 100
            if bill_ratio > 50:
                insights["risk_flags"].append({
                    "severity": "Critical",
                    "message": f"Pending bills exceed 50% of annual revenue ({bill_ratio:.1f}%)",
                    "category": "Debt"
                })
                insights["recommendations"].append(
                    "Develop a debt resolution plan to reduce pending bills."
                )
                
        # 4. Generate Narrative Summary
        insights["summary"] = self._generate_narrative(data, insights["risk_flags"])
        
        return insights

    def _generate_narrative(self, data, flags):
        """
        Generate a plain-language summary.
        """
        county = data.get("county", "The county")
        rev = data.get("revenue", {}).get("revenue_actual", 0)
        exp = data.get("expenditure", {}).get("total_expenditure", 0)
        
        narrative = f"{county} collected Ksh {rev:,} in revenue and spent Ksh {exp:,}. "
        
        critical_flags = [f for f in flags if f["severity"] == "Critical"]
        if critical_flags:
            narrative += f"However, there are {len(critical_flags)} critical issues requiring attention, "
            narrative += f"including {critical_flags[0]['message'].lower()}. "
        else:
            narrative += "The county shows generally sound financial management. "
            
        return narrative
