"use client"

import { NATIONAL_BUDGET_2025 } from "@/lib/dashboard-constants"
import { Badge } from "@/components/ui/badge"

export function NationalBudgetHeader() {
    return (
        <div className="flex flex-col items-end gap-1">
            <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">National Budget</span>
                <Badge variant="outline" className="text-lg py-1 px-4 border-accent/30 bg-accent/5 text-accent font-bold ring-1 ring-accent/20">
                    Ksh {(NATIONAL_BUDGET_2025.total_budget / 1e12).toFixed(2)} Trillion
                </Badge>
            </div>
            <p className="text-[10px] text-muted-foreground italic mr-1">FY {NATIONAL_BUDGET_2025.fiscal_year} Projections</p>
        </div>
    )
}
