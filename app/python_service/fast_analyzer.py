"""
Optimized wrapper function for fast PDF analysis.
This function provides a fast interface to the comprehensive CountyBudgetAnalyzer.
"""
import io
import time
from typing import Dict, Any
from analyzer import CountyBudgetAnalyzer, normalize_county_name

def run_county_analysis(pdf_bytes: bytes, county: str) -> Dict[str, Any]:
    """
    FAST wrapper around the comprehensive CountyBudgetAnalyzer.
    
    This combines:
    - Speed optimizations (fast county detection, limited page processing)
    - Thoroughness (comprehensive data models, intelligence, all 47 counties support)
    
    Target: < 1 minute for typical county section.
    
    Args:
        pdf_bytes: PDF file as bytes
        county: County name to analyze
        
    Returns:
        Dictionary with comprehensive analysis results
    """
    start_time = time.time()
    
    try:
        print(f"🚀 Starting FAST analysis for {county}...")
        
        # Normalize county name
        normalized_county = normalize_county_name(county)
        print(f"📍 Analyzing: {normalized_county}")
        
        # Use the comprehensive analyzer
        analyzer = CountyBudgetAnalyzer(pdf_bytes)
        result = analyzer.analyze_county(normalized_county)
        
        if not result.get("success"):
            return {"error": result.get("error", "Analysis failed")}
        
        # Extract the analysis object
        analysis = result.get("analysis")
        if not analysis:
            return {"error": "No analysis data returned"}
        
        # Convert to dictionary format expected by API
        output = {
            "county": analysis.county_name,
            "financial_year": analysis.financial_year,
            "revenue": {
                "revenue_target": analysis.revenue.total_revenue if hasattr(analysis.revenue, 'total_revenue') else 0,
                "revenue_actual": analysis.revenue.total_revenue,
                "own_source_revenue": analysis.revenue.osr_actual,
                "equitable_share": analysis.revenue.equitable_share,
                "conditional_grants": analysis.revenue.conditional_grants,
                "revenue_variance": 0,
                "revenue_performance_percent": analysis.revenue.performance_percent
            },
            "expenditure": {
                "approved_budget": analysis.expenditure.total_budget,
                "recurrent_budget": analysis.expenditure.recurrent_budget,
                "recurrent_expenditure": analysis.expenditure.recurrent_expenditure,
                "development_budget": analysis.expenditure.development_budget,
                "development_expenditure": analysis.expenditure.development_expenditure,
                "total_expenditure": analysis.expenditure.total_expenditure,
                "absorption_rate_percent": analysis.expenditure.overall_absorption_percent
            },
            "debt_and_liabilities": {
                "pending_bills_amount": analysis.debt.pending_bills,
                "outstanding_debt": 0,
                "arrears_brought_forward": analysis.debt.revenue_arrears,
                "staff_costs_percent": 0.0,
                "pending_bills_ageing": analysis.debt.pending_bills_ageing or {}
            },
            "intelligence": analysis.intelligence or {},
            "computed": {
                "revenue_variance": 0,
                "revenue_performance_percent": analysis.revenue.performance_percent,
                "overall_absorption_percent": analysis.expenditure.overall_absorption_percent,
                "development_absorption_percent": analysis.expenditure.dev_absorption_percent,
                "compensation_to_revenue_percent": 0.0
            },
            "summary_text": analysis.summary,
            "key_metrics": analysis.key_metrics or {}
        }
        
        elapsed = time.time() - start_time
        print(f"⏱️ Analysis completed in {elapsed:.2f} seconds")
        
        return output
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        elapsed = time.time() - start_time
        print(f"❌ Analysis failed after {elapsed:.2f} seconds")
        return {"error": str(e)}
