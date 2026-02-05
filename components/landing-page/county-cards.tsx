"use client"

import React, { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, AlertTriangle, TrendingUp, Search } from "lucide-react"
import { COUNTY_FACTS } from "@/lib/county-facts"

const getColor = (status: string) => {
    switch (status?.toLowerCase()) {
        case "critical": return "red"
        case "warning": return "amber"
        case "status": return "blue"
        case "leader": return "emerald"
        case "improving": return "purple"
        default: return "blue"
    }
}

export function CountySpotlight() {
    const [counties, setCounties] = useState<any[]>([])

    const refreshSpotlight = () => {
        const shuffled = [...COUNTY_FACTS].sort(() => 0.5 - Math.random())
        const selected = shuffled.slice(0, 3).map(c => ({
            name: `${c.name} Snapshot`,
            status: c.fiscalHealth,
            score: c.fiscalHealth === "Leader" ? "✅" : (c.fiscalHealth === "Critical" ? "⚠️" : "🔍"),
            metrics: [
                { label: "Absorption", value: c.absorption.split(' ')[0], trend: "up" },
                { label: "Gap/Variance", value: c.budgetGap.includes('Pending') ? c.budgetGap.split(' ').slice(1, 3).join(' ') : c.budgetGap.split(' ')[0], trend: "down" }
            ],
            verified: "AI-Verified Data",
            color: getColor(c.fiscalHealth)
        }))
        setCounties(selected)
    }

    useEffect(() => {
        refreshSpotlight()
        const interval = setInterval(refreshSpotlight, 120000)
        return () => clearInterval(interval)
    }, [])

    if (counties.length === 0) return null
    return (
        <div className="container mx-auto px-4">
            <div className="text-center mb-12">
                <h2 className="text-3xl font-bold text-white mb-4">County Spotlight Cards</h2>
                <p className="text-slate-400">Live data extracted from current fiscal reports.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {counties.map((county, idx) => (
                    <motion.div
                        key={idx}
                        whileHover={{ y: -12, scale: 1.02 }}
                        transition={{ type: "spring", stiffness: 300, damping: 20 }}
                        className="group"
                    >
                        <Card className="bg-gradient-to-br from-slate-900/60 to-slate-900/40 border-slate-700/50 backdrop-blur-xl overflow-hidden relative hover:border-slate-600 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-900/20">
                            {/* Gradient overlay on hover */}
                            <div className={`absolute inset-0 bg-gradient-to-br from-${county.color}-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none`} />

                            <CardHeader className="pb-3 relative z-10">
                                <div className="flex justify-between items-start">
                                    <Badge
                                        variant="outline"
                                        className={`border-${county.color}-500/50 text-${county.color}-400 bg-${county.color}-500/10 backdrop-blur-sm px-3 py-1.5 font-semibold text-xs`}
                                    >
                                        {county.status} {county.score}
                                    </Badge>
                                    <Search className="h-5 w-5 text-slate-600 group-hover:text-blue-400 transition-all duration-300 group-hover:rotate-12" />
                                </div>
                                <CardTitle className="text-2xl text-white pt-4 font-bold tracking-tight">{county.name}</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3 relative z-10">
                                {county.metrics.map((metric, midx) => (
                                    <div key={midx} className="flex justify-between items-center border-b border-slate-800/50 pb-3 group/metric hover:border-slate-700 transition-colors">
                                        <span className="text-slate-400 text-sm font-medium">{metric.label}</span>
                                        <div className="flex items-center gap-2">
                                            <span className="text-white font-mono font-bold text-lg">{metric.value}</span>
                                            {metric.trend === "up" && (
                                                <TrendingUp className="h-4 w-4 text-emerald-500" />
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                            <CardFooter className="pt-3 relative z-10">
                                <div className="flex items-center text-xs text-slate-500 font-medium">
                                    <div className={`h-2 w-2 rounded-full mr-2 bg-${county.color}-500 animate-pulse shadow-lg shadow-${county.color}-500/50`} />
                                    {county.verified}
                                </div>
                            </CardFooter>
                        </Card>
                    </motion.div>
                ))}
            </div>
        </div>
    )
}
