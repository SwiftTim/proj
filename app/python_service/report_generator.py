from typing import Dict, Any, List
import datetime

class ReportGenerator:
    """
    Assembles structured reports for export.
    """
    
    def generate_report(self, data: Dict[str, Any], report_type: str = "full") -> Dict[str, Any]:
        """
        Generate a structured report object.
        """
        report = {
            "title": f"{data.get('county', 'County')} Budget Implementation Review Report",
            "generated_at": datetime.datetime.now().isoformat(),
            "fiscal_year": data.get("financial_year", "2024/25"),
            "sections": []
        }
        
        # 1. Executive Summary
        report["sections"].append({
            "title": "Executive Summary",
            "content": data.get("summary_text", "No summary available."),
            "type": "text"
        })
        
        # 2. Key Highlights (Metrics)
        metrics = data.get("key_metrics", {})
        report["sections"].append({
            "title": "Key Financial Highlights",
            "content": metrics,
            "type": "metrics_grid"
        })
        
        # 3. Revenue Analysis
        rev = data.get("revenue", {})
        report["sections"].append({
            "title": "Revenue Performance",
            "content": {
                "Target": rev.get("revenue_target"),
                "Actual": rev.get("revenue_actual"),
                "Performance": f"{data.get('computed', {}).get('revenue_performance_percent', 0):.1f}%"
            },
            "type": "table"
        })
        
        # 4. Expenditure Analysis
        exp = data.get("expenditure", {})
        report["sections"].append({
            "title": "Expenditure Analysis",
            "content": {
                "Total Expenditure": exp.get("total_expenditure"),
                "Recurrent": exp.get("recurrent_expenditure"),
                "Development": exp.get("development_expenditure"),
                "Absorption Rate": f"{data.get('computed', {}).get('overall_absorption_percent', 0):.1f}%"
            },
            "type": "table"
        })
        
        # 5. Risks & Recommendations
        intel = data.get("intelligence", {})
        if intel.get("flags"):
            report["sections"].append({
                "title": "Risks & Compliance Issues",
                "content": intel["flags"],
                "type": "list",
                "style": "warning"
            })
            
        return report

    def generate_markdown(self, report_data: Dict[str, Any]) -> str:
        """
        Convert structured report to Markdown.
        """
        md = f"# {report_data['title']}\n"
        md += f"**Date:** {report_data['generated_at'][:10]}\n\n"
        
        for section in report_data["sections"]:
            md += f"## {section['title']}\n\n"
            
            if section["type"] == "text":
                md += f"{section['content']}\n\n"
                
            elif section["type"] == "metrics_grid":
                for k, v in section["content"].items():
                    md += f"- **{k}:** {v}\n"
                md += "\n"
                
            elif section["type"] == "table":
                md += "| Metric | Value |\n|---|---|\n"
                for k, v in section["content"].items():
                    val = f"{v:,}" if isinstance(v, (int, float)) else v
                    md += f"| {k} | {val} |\n"
                md += "\n"
                
            elif section["type"] == "list":
                for item in section["content"]:
                    md += f"- {item}\n"
                md += "\n"
                
        return md
