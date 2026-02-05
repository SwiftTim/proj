"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts"
import { NATIONAL_BUDGET_2025 } from "@/lib/dashboard-constants"

export function SectoralAllocationChart() {
    const data = NATIONAL_BUDGET_2025.sectoral_allocation;

    return (
        <Card className="h-full border-border/50 bg-card/50 backdrop-blur-sm">
            <CardHeader>
                <CardTitle className="text-lg">Budget Share</CardTitle>
                <CardDescription>National Sectoral Allocation {NATIONAL_BUDGET_2025.fiscal_year}</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="amount"
                                nameKey="sector"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip
                                formatter={(value: number) => `Ksh ${(value / 1e9).toFixed(1)}B`}
                                contentStyle={{
                                    backgroundColor: "rgba(10, 10, 10, 0.8)",
                                    border: "1px solid hsl(var(--border))",
                                    borderRadius: "12px",
                                }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
                <div className="mt-4 grid grid-cols-1 gap-2">
                    {data.slice(0, 5).map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between text-xs">
                            <div className="flex items-center gap-2">
                                <div className="h-2 w-2 rounded-full" style={{ backgroundColor: item.color }} />
                                <span className="text-muted-foreground">{item.sector}</span>
                            </div>
                            <span className="font-semibold">{item.percentage}%</span>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    )
}
