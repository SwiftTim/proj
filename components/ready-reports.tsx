"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Download, FileCheck, Loader2, Search } from "lucide-react"
import { generateIntegrityReport } from "@/lib/pdf-generator"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"

export function ReadyReports() {
    const [reports, setReports] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState("")

    useEffect(() => {
        const fetchReports = async () => {
            try {
                const res = await fetch("/api/reports")
                const data = await res.json()
                if (data.success) {
                    setReports(data.reports)
                }
            } catch (err) {
                console.error("Failed to fetch reports:", err)
            } finally {
                setLoading(false)
            }
        }
        fetchReports()
    }, [])

    const filteredReports = reports.filter(r =>
        r.county.toLowerCase().includes(search.toLowerCase()) ||
        r.year.toLowerCase().includes(search.toLowerCase())
    )

    if (loading) {
        return (
            <div className="flex justify-center p-12">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                        <FileCheck className="h-6 w-6 text-emerald-500" />
                        Analyzed Integrity Reports
                    </h2>
                    <p className="text-slate-400 text-sm">Download pre-generated high-fidelity audit reports.</p>
                </div>
                <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                    <Input
                        placeholder="Search reports..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="pl-10 bg-slate-900 border-slate-800 text-white"
                    />
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredReports.length > 0 ? (
                    filteredReports.map((report) => (
                        <Card key={report.id} className="bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-all group overflow-hidden">
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-500 to-teal-500 opacity-50 group-hover:opacity-100 transition-opacity" />
                            <CardHeader className="pb-3">
                                <div className="flex justify-between items-start">
                                    <Badge variant="outline" className="text-[10px] uppercase font-bold border-emerald-500/30 text-emerald-400 bg-emerald-500/5 mb-2">
                                        {report.year}
                                    </Badge>
                                    <span className="text-[10px] text-slate-500 font-mono">
                                        {new Date(report.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                                <CardTitle className="text-xl font-bold text-white">{report.county}</CardTitle>
                                <CardDescription className="line-clamp-2 text-slate-400 text-xs mt-2">
                                    {report.summary_text || "Automated integrity assessment completed."}
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="flex items-center justify-between mt-4">
                                    <div className="flex flex-col">
                                        <span className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Risk Score</span>
                                        <span className={`text-lg font-bold ${report.intelligence?.transparency_risk_score > 60 ? 'text-red-500' : 'text-emerald-500'}`}>
                                            {report.intelligence?.transparency_risk_score || 0}/100
                                        </span>
                                    </div>
                                    <Button
                                        size="sm"
                                        onClick={() => generateIntegrityReport(report)}
                                        className="bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-900/20"
                                    >
                                        <Download className="h-4 w-4 mr-2" />
                                        Download PDF
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))
                ) : (
                    <div className="col-span-full py-20 text-center border-2 border-dashed border-slate-800 rounded-3xl">
                        <FileCheck className="h-10 w-10 text-slate-700 mx-auto mb-4" />
                        <p className="text-slate-500 font-bold uppercase tracking-widest">No Analyzed Reports Found</p>
                        <p className="text-slate-600 text-xs mt-2">Go to the Analysis tab to generate your first report.</p>
                    </div>
                )}
            </div>
        </div>
    )
}
