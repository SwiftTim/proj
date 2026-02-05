"use client"

import React from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend } from "recharts"

const data = [
    { name: "Baringo", wage: 53, dev: 47 },
    { name: "Nairobi", wage: 48, dev: 52 },
    { name: "Turkana", wage: 32, dev: 68 },
    { name: "Makueni", wage: 30, dev: 70 },
]

export function WhyItMatters() {
    return (
        <div className="container mx-auto px-4 py-24">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
                <div className="space-y-10">
                    <h2 className="text-5xl md:text-6xl font-bold text-white tracking-tight leading-tight">
                        Visualizing the <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">Trade-off</span>
                    </h2>
                    <p className="text-xl md:text-2xl text-slate-300 leading-relaxed font-light">
                        When a county spends over 50% on salaries, the remaining funds for life-saving infrastructure—roads, hospitals, and water—dwindle.
                        <span className="block mt-6 text-white font-medium italic text-2xl">
                            "BudgetAI makes this trade-off visible to every citizen."
                        </span>
                    </p>
                    <div className="flex flex-col gap-5 pt-4">
                        <div className="flex items-center gap-4">
                            <div className="h-5 w-5 rounded-md bg-red-500 shadow-lg shadow-red-500/50" />
                            <span className="text-slate-200 text-lg font-medium">Wage Bill & Personnel Emoluments</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="h-5 w-5 rounded-md bg-emerald-500 shadow-lg shadow-emerald-500/50" />
                            <span className="text-slate-200 text-lg font-medium">Development Expenditure</span>
                        </div>
                    </div>
                </div>

                <div className="bg-gradient-to-br from-slate-900/70 to-slate-900/50 border border-slate-700/50 p-10 rounded-[3rem] shadow-2xl backdrop-blur-xl hover:border-slate-600 transition-all duration-300">
                    <div className="h-[450px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={data} layout="vertical" barSize={40} margin={{ left: 20, right: 20 }}>
                                <XAxis type="number" hide />
                                <YAxis
                                    dataKey="name"
                                    type="category"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: "#cbd5e1", fontSize: 16, fontWeight: 600 }}
                                />
                                <Tooltip
                                    cursor={{ fill: "rgba(59, 130, 246, 0.1)" }}
                                    contentStyle={{
                                        backgroundColor: "#0f172a",
                                        border: "1px solid #334155",
                                        borderRadius: "12px",
                                        padding: "12px 16px",
                                        boxShadow: "0 10px 40px rgba(0,0,0,0.5)"
                                    }}
                                    labelStyle={{ color: "#fff", fontWeight: "bold", fontSize: "14px" }}
                                />
                                <Bar dataKey="wage" stackId="a" fill="#ef4444" radius={[6, 0, 0, 6]} />
                                <Bar dataKey="dev" stackId="a" fill="#10b981" radius={[0, 6, 6, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <p className="mt-8 text-center text-sm text-slate-400 font-mono uppercase tracking-widest font-semibold">
                        Comparative Split: Wage vs Development
                    </p>
                </div>
            </div>
        </div>
    )
}
