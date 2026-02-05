"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { Loader2, ArrowRightLeft, TrendingUp, CircleCheck, CircleX, Upload, AlertCircle, CheckCircle2, ShieldAlert, FileText } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

const MERITS = [
    { id: "absorption", label: "Absorption Gap", description: "Target dev budget vs actual spending" },
    { id: "revenue", label: "Revenue Variance", description: "Projected OSR vs actual collections" },
    { id: "wage_bill", label: "Wage Bill Compliance", description: "Check if PE exceeds 35% ceiling" },
    { id: "debt", label: "Debt Stock", description: "Pushed bills vs official national stock" }
]

export function ComparisonModule() {
    const [documents, setDocuments] = useState<any[]>([])
    const [loading, setLoading] = useState(false)
    const [activeMode, setActiveMode] = useState("push_compare")

    // Mode 1: County vs County
    const [selectionA, setSelectionA] = useState({ county: "", year: "" })
    const [selectionB, setSelectionB] = useState({ county: "", year: "" })
    const [comparisonResult, setComparisonResult] = useState<any | null>(null)

    // Mode 2: PDF Push & Compare
    const [pushCounty, setPushCounty] = useState("")
    const [selectedMerits, setSelectedMerits] = useState<string[]>(["absorption", "revenue"])
    const [integrityResult, setIntegrityResult] = useState<any | null>(null)

    useEffect(() => {
        const fetchDocuments = async () => {
            try {
                const res = await fetch("/api/documents")
                const data = await res.json()
                if (data.success) setDocuments(data.documents)
            } catch (err) {
                console.error("Failed to fetch documents:", err)
            }
        }
        fetchDocuments()
    }, [])

    const counties = [...new Set(documents.map((d) => d.county))].sort()
    const years = [...new Set(documents.map((d) => d.year))].sort().reverse()

    const toggleMerit = (id: string) => {
        if (selectedMerits.includes(id)) {
            setSelectedMerits(selectedMerits.filter(m => m !== id))
        } else {
            setSelectedMerits([...selectedMerits, id])
        }
    }

    const runPushCompare = async () => {
        if (!pushCounty) return alert("Please select a county")
        const currentDoc = documents.find(d => d.county === pushCounty)
        if (!currentDoc) return alert("No uploaded documents found for this county to 'push'")

        setLoading(true)
        setIntegrityResult(null)

        try {
            const res = await fetch("http://127.0.0.1:8000/compare/gemini", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    pushed_pdf_id: currentDoc.filenames[0],
                    county: pushCounty,
                    merits: selectedMerits.map(m => MERITS.find(mi => mi.id === m)?.label)
                })
            })

            const data = await res.json()
            if (data.success) {
                setIntegrityResult(data.data)
            } else {
                alert("Error: " + data.error)
            }
        } catch (err: any) {
            console.error(err)
            alert("External Analysis Error: Ensure Colab/Gemini backend is active.")
        } finally {
            setLoading(false)
        }
    }

    const analyzeAndCompare = async () => {
        if (!selectionA.county || !selectionB.county) return alert("Select both counties")
        setLoading(true)
        setComparisonResult(null)
        try {
            const fetchAnalysis = async (sel: { county: string, year: string }) => {
                const doc = documents.find(d => d.county === sel.county && d.year === sel.year)
                if (!doc) throw new Error(`Document not found for ${sel.county}`)
                const fileName = doc.filenames[0]
                const fileRes = await fetch(`/uploads/${fileName}`)
                const blob = await fileRes.blob()
                const formData = new FormData()
                formData.append("county", sel.county)
                formData.append("year", sel.year)
                formData.append("file", blob, fileName)
                const res = await fetch("http://127.0.0.1:8000/analyze_pdf", { method: "POST", body: formData })
                const data = await res.json()
                return data.data || data
            }
            const [resultA, resultB] = await Promise.all([fetchAnalysis(selectionA), fetchAnalysis(selectionB)])
            const compareRes = await fetch("http://127.0.0.1:8000/compare_counties", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ county_a: resultA, county_b: resultB })
            })
            const compareData = await compareRes.json()
            if (compareData.success) { setComparisonResult(compareData.comparison) }
            else { alert("Comparison failed: " + compareData.error) }
        } catch (err: any) { alert("Error: " + err.message) } finally { setLoading(false) }
    }

    return (
        <Card className="max-w-6xl mx-auto border-slate-800 bg-slate-950/50 backdrop-blur-xl shadow-2xl">
            <CardHeader className="border-b border-slate-800/50 bg-slate-900/20">
                <div className="flex justify-between items-center">
                    <div>
                        <CardTitle className="text-white text-2xl font-black tracking-tight">Financial Comparison Suite</CardTitle>
                        <CardDescription className="text-slate-400">Cross-reference budget data and verify integrity.</CardDescription>
                    </div>
                    <Tabs value={activeMode} onValueChange={setActiveMode} className="bg-slate-900/50 p-1 rounded-full border border-slate-800">
                        <TabsList className="bg-transparent">
                            <TabsTrigger value="push_compare" className="rounded-full px-6 data-[state=active]:bg-blue-600 data-[state=active]:text-white">PDF Push & Compare</TabsTrigger>
                            <TabsTrigger value="county_vs_county" className="rounded-full px-6 data-[state=active]:bg-blue-600 data-[state=active]:text-white">Benchmarking</TabsTrigger>
                        </TabsList>
                    </Tabs>
                </div>
            </CardHeader>
            <CardContent className="p-8">

                {activeMode === "push_compare" ? (
                    <div className="space-y-10">
                        {/* --- Ingestion Layer --- */}
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            {/* County Selection Fields */}
                            <div className="lg:col-span-2 space-y-6">
                                <label className="text-[10px] font-black uppercase tracking-widest text-slate-500">1. Select Counties to Compare</label>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {/* County A */}
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-slate-400">County A</label>
                                        <Select value={selectionA.county} onValueChange={(v) => setSelectionA({ ...selectionA, county: v })}>
                                            <SelectTrigger className="bg-slate-900 border-slate-700 text-white h-12 hover:border-slate-600 focus:ring-0">
                                                <SelectValue placeholder="Select First County" />
                                            </SelectTrigger>
                                            <SelectContent className="bg-slate-900 border-slate-700 text-white backdrop-blur-xl">
                                                {counties.map(c => <SelectItem key={c} value={c} className="hover:bg-slate-800 focus:bg-slate-800">{c}</SelectItem>)}
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    {/* County B */}
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-slate-400">County B</label>
                                        <Select value={selectionB.county} onValueChange={(v) => setSelectionB({ ...selectionB, county: v })}>
                                            <SelectTrigger className="bg-slate-900 border-slate-700 text-white h-12 hover:border-slate-600 focus:ring-0">
                                                <SelectValue placeholder="Select Second County" />
                                            </SelectTrigger>
                                            <SelectContent className="bg-slate-900 border-slate-700 text-white backdrop-blur-xl">
                                                {counties.map(c => <SelectItem key={c} value={c} className="hover:bg-slate-800 focus:bg-slate-800">{c}</SelectItem>)}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                </div>

                                {/* Document Selection */}
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-slate-400">Select Document to Push for Comparison</label>
                                    <Select value={pushCounty} onValueChange={setPushCounty}>
                                        <SelectTrigger className="bg-slate-900 border-slate-700 text-white h-12 hover:border-slate-600 focus:ring-0">
                                            <SelectValue placeholder="Choose a document from uploaded files" />
                                        </SelectTrigger>
                                        <SelectContent className="bg-slate-900 border-slate-700 text-white backdrop-blur-xl max-h-[300px]">
                                            {documents.map((doc, idx) => (
                                                <SelectItem 
                                                    key={idx} 
                                                    value={doc.county}
                                                    className="hover:bg-slate-800 focus:bg-slate-800"
                                                >
                                                    <div className="flex items-center justify-between w-full">
                                                        <span className="font-medium">{doc.county}</span>
                                                        <span className="text-xs text-slate-500 ml-4">{doc.year || 'N/A'}</span>
                                                    </div>
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <p className="text-[10px] text-slate-500 mt-1">
                                        This document (pushed) will be compared against the official CBIRR report for {pushCounty || 'selected county'}.
                                    </p>
                                </div>
                            </div>

                            {/* Upload Status Card */}
                            <div className="lg:col-span-1 space-y-4">
                                <label className="text-[10px] font-black uppercase tracking-widest text-slate-500">Document Status</label>
                                <div className="p-6 border-2 border-dashed border-slate-800 rounded-3xl bg-slate-900/20 text-center space-y-4">
                                    <div className="bg-blue-500/10 p-3 rounded-2xl w-fit mx-auto">
                                        <Upload className="h-6 w-6 text-blue-500" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-bold text-white">Ready for Comparison</p>
                                        <p className="text-[10px] text-slate-500 uppercase mt-1">
                                            {documents.length} Document{documents.length !== 1 ? 's' : ''} Available
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* --- Merit Selection --- */}
                        <div className="space-y-6">
                            <label className="text-[10px] font-black uppercase tracking-widest text-slate-500">2. Comparison Merits (Suggested)</label>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {MERITS.map((merit) => (
                                    <button
                                        key={merit.id}
                                        onClick={() => toggleMerit(merit.id)}
                                        className={`p-4 rounded-2xl text-left border transition-all ${selectedMerits.includes(merit.id)
                                                ? "bg-blue-600/10 border-blue-500/50 shadow-[0_0_20px_rgba(37,99,235,0.1)]"
                                                : "bg-slate-900/50 border-slate-800 hover:border-slate-700"
                                            }`}
                                    >
                                        <div className="flex justify-between items-start">
                                            <span className={`text-sm font-bold ${selectedMerits.includes(merit.id) ? "text-blue-400" : "text-slate-300"}`}>
                                                {merit.label}
                                            </span>
                                            {selectedMerits.includes(merit.id) && <CircleCheck className="h-4 w-4 text-blue-500" />}
                                        </div>
                                        <p className="text-[10px] text-slate-500 mt-1">{merit.description}</p>
                                    </button>
                                ))}
                            </div>

                            <Button
                                onClick={runPushCompare}
                                disabled={loading || !pushCounty}
                                className="w-full h-14 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-black uppercase tracking-widest text-xs rounded-2xl shadow-xl transition-all active:scale-[0.98]"
                            >
                                {loading ? <Loader2 className="h-5 w-5 animate-spin mr-2" /> : <ShieldAlert className="h-5 w-5 mr-2" />}
                                Trigger Integrity Cross-Reference
                            </Button>
                        </div>

                        {/* --- Reporting Layer (Integrity Scorecard) --- */}
                        {integrityResult && (
                            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                                <div className="flex flex-col md:flex-row gap-6 items-center bg-slate-900/50 p-8 rounded-3xl border border-slate-800">
                                    <div className="flex flex-col items-center justify-center p-6 bg-slate-950 rounded-full border-4 border-slate-900 w-40 h-40 shadow-2xl">
                                        <span className="text-[10px] font-black uppercase text-slate-500 mb-1">Integrity</span>
                                        <span className={`text-5xl font-black ${integrityResult.integrity_score > 70 ? 'text-emerald-500' : integrityResult.integrity_score > 40 ? 'text-yellow-500' : 'text-red-500'}`}>
                                            {integrityResult.integrity_score}
                                        </span>
                                        <span className="text-[10px] font-bold text-slate-600">SCOREcard</span>
                                    </div>
                                    <div className="flex-1 space-y-2 text-center md:text-left">
                                        <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 uppercase text-[10px]">Senior Auditor Verdict</Badge>
                                        <p className="text-2xl font-bold text-white tracking-tight">{integrityResult.verdict}</p>
                                        <div className="flex flex-wrap gap-2 mt-4 justify-center md:justify-start">
                                            {integrityResult.integrity_alerts?.map((alert: string, idx: number) => (
                                                <Badge key={idx} variant="destructive" className="bg-red-500/10 text-red-500 border-red-500/20 text-[9px] uppercase font-black">
                                                    <AlertCircle className="h-3 w-3 mr-1" /> {alert}
                                                </Badge>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                {/* Data Quality Notes */}
                                {integrityResult.data_quality_notes && (
                                    <div className="bg-blue-950/20 border border-blue-900/50 rounded-2xl p-6">
                                        <div className="flex items-start gap-3">
                                            <div className="bg-blue-500/10 p-2 rounded-lg">
                                                <FileText className="h-5 w-5 text-blue-400" />
                                            </div>
                                            <div className="flex-1">
                                                <h4 className="text-sm font-black uppercase tracking-widest text-blue-400 mb-2">Data Quality Assessment</h4>
                                                <p className="text-sm text-slate-300 leading-relaxed">{integrityResult.data_quality_notes}</p>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Merit Comparisons */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {integrityResult.merit_comparison?.map((comparison: any, idx: number) => (
                                        <Card key={idx} className="bg-slate-900/30 border-slate-800 overflow-hidden group hover:border-slate-700 transition-all">
                                            <CardContent className="p-6 space-y-4">
                                                <div className="flex justify-between items-center">
                                                    <h4 className="text-sm font-black uppercase tracking-widest text-slate-400">{comparison.merit}</h4>
                                                    {comparison.status === "verified" ? (
                                                        <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                                                    ) : comparison.status === "data_missing" ? (
                                                        <AlertCircle className="h-5 w-5 text-yellow-500" />
                                                    ) : (
                                                        <ShieldAlert className="h-5 w-5 text-red-500" />
                                                    )}
                                                </div>

                                                {/* Variance Badge */}
                                                {comparison.variance_percent !== undefined && (
                                                    <div className="flex justify-center">
                                                        <Badge
                                                            className={`text-xs font-bold ${Math.abs(comparison.variance_percent) < 5
                                                                    ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                                                                    : Math.abs(comparison.variance_percent) < 10
                                                                        ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
                                                                        : 'bg-red-500/10 text-red-500 border-red-500/20'
                                                                }`}
                                                        >
                                                            {comparison.variance_percent > 0 ? '+' : ''}{comparison.variance_percent.toFixed(1)}% Variance
                                                        </Badge>
                                                    </div>
                                                )}

                                                <div className="grid grid-cols-2 gap-4 bg-slate-950/50 p-4 rounded-2xl border border-slate-800/50">
                                                    <div>
                                                        <p className="text-[9px] font-black text-slate-500 uppercase">Official CBIRR</p>
                                                        <p className="text-lg font-bold text-white">{comparison.official_value}</p>
                                                        {comparison.official_source && (
                                                            <p className="text-[8px] text-slate-600 mt-1 italic">Source: {comparison.official_source}</p>
                                                        )}
                                                    </div>
                                                    <div className="border-l border-slate-800 pl-4">
                                                        <p className="text-[9px] font-black text-blue-500 uppercase">Pushed Doc</p>
                                                        <p className="text-lg font-bold text-blue-400">{comparison.pushed_value}</p>
                                                        {comparison.pushed_source && (
                                                            <p className="text-[8px] text-blue-600 mt-1 italic">Source: {comparison.pushed_source}</p>
                                                        )}
                                                    </div>
                                                </div>
                                                <p className="text-xs text-slate-400 italic">"{comparison.discrepancy}"</p>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="space-y-8">
                        {/* Legacy County vs County Benchmarking UI */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                            <div className="space-y-4 p-8 border border-slate-800 rounded-3xl bg-slate-900/20">
                                <h3 className="font-black text-xs uppercase tracking-widest text-slate-500">Benchmark Jurisdiction A</h3>
                                <div className="space-y-3">
                                    <Select value={selectionA.county} onValueChange={(v) => setSelectionA({ ...selectionA, county: v })}>
                                        <SelectTrigger className="bg-slate-900 border-slate-700 text-white hover:border-slate-600 focus:ring-0"><SelectValue placeholder="Select County" /></SelectTrigger>
                                        <SelectContent className="bg-slate-900 border-slate-700 text-white backdrop-blur-xl">{counties.map(c => <SelectItem key={c} value={c} className="hover:bg-slate-800 focus:bg-slate-800">{c}</SelectItem>)}</SelectContent>
                                    </Select>
                                    <Select value={selectionA.year} onValueChange={(v) => setSelectionA({ ...selectionA, year: v })}>
                                        <SelectTrigger className="bg-slate-900 border-slate-700 text-white hover:border-slate-600 focus:ring-0"><SelectValue placeholder="Select Year" /></SelectTrigger>
                                        <SelectContent className="bg-slate-900 border-slate-700 text-white backdrop-blur-xl">{years.map(y => <SelectItem key={y} value={y} className="hover:bg-slate-800 focus:bg-slate-800">{y}</SelectItem>)}</SelectContent>
                                    </Select>
                                </div>
                            </div>

                            <div className="space-y-4 p-8 border border-slate-800 rounded-3xl bg-slate-900/20">
                                <h3 className="font-black text-xs uppercase tracking-widest text-slate-500">Benchmark Jurisdiction B</h3>
                                <div className="space-y-3">
                                    <Select value={selectionB.county} onValueChange={(v) => setSelectionB({ ...selectionB, county: v })}>
                                        <SelectTrigger className="bg-slate-900 border-slate-700 text-white hover:border-slate-600 focus:ring-0"><SelectValue placeholder="Select County" /></SelectTrigger>
                                        <SelectContent className="bg-slate-900 border-slate-700 text-white backdrop-blur-xl">{counties.map(c => <SelectItem key={c} value={c} className="hover:bg-slate-800 focus:bg-slate-800">{c}</SelectItem>)}</SelectContent>
                                    </Select>
                                    <Select value={selectionB.year} onValueChange={(v) => setSelectionB({ ...selectionB, year: v })}>
                                        <SelectTrigger className="bg-slate-900 border-slate-700 text-white hover:border-slate-600 focus:ring-0"><SelectValue placeholder="Select Year" /></SelectTrigger>
                                        <SelectContent className="bg-slate-900 border-slate-700 text-white backdrop-blur-xl">{years.map(y => <SelectItem key={y} value={y} className="hover:bg-slate-800 focus:bg-slate-800">{y}</SelectItem>)}</SelectContent>
                                    </Select>
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-center">
                            <Button onClick={analyzeAndCompare} disabled={loading || !selectionA.county || !selectionB.county} size="lg" className="bg-slate-100 text-black hover:bg-white px-10 rounded-full font-black uppercase tracking-widest text-xs h-14 shadow-2xl transition-transform active:scale-95">
                                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <ArrowRightLeft className="h-4 w-4 mr-2" />}
                                Compute Benchmark
                            </Button>
                        </div>

                        {comparisonResult && (
                            <div className="mt-8 space-y-6">
                                <div className="grid grid-cols-1 gap-4">
                                    {Object.entries(comparisonResult.metrics).map(([key, metric]: [string, any]) => (
                                        <Card key={key} className="overflow-hidden bg-slate-900/50 border-slate-800">
                                            <CardContent className="p-0">
                                                <div className="grid grid-cols-3 divide-x divide-slate-800">
                                                    <div className={`p-6 flex flex-col items-center justify-center ${metric.winner === 'a' ? 'bg-blue-600/10' : ''}`}>
                                                        <span className="text-xs font-black text-slate-500 uppercase tracking-tighter mb-2">{comparisonResult.county_a}</span>
                                                        <span className="text-xl font-black text-white">
                                                            {metric.format === 'currency' ? `Ksh ${metric.a.toLocaleString()}` :
                                                                metric.format === 'percent' ? `${metric.a.toFixed(1)}%` : metric.a}
                                                        </span>
                                                        {metric.winner === 'a' && <Badge variant="outline" className="mt-3 bg-blue-500/20 text-blue-400 border-blue-500/30">Leader</Badge>}
                                                    </div>
                                                    <div className="p-6 flex flex-col items-center justify-center bg-slate-950/50">
                                                        <span className="font-black text-[11px] uppercase tracking-widest text-slate-400 text-center">{metric.label}</span>
                                                        <Badge className="mt-2 bg-slate-800 text-slate-400">VAR: {metric.diff > 0 ? '+' : ''}{metric.format === 'currency' ? metric.diff.toLocaleString() : metric.diff.toFixed(1)}</Badge>
                                                    </div>
                                                    <div className={`p-6 flex flex-col items-center justify-center ${metric.winner === 'b' ? 'bg-blue-600/10' : ''}`}>
                                                        <span className="text-xs font-black text-slate-500 uppercase tracking-tighter mb-2">{comparisonResult.county_b}</span>
                                                        <span className="text-xl font-black text-white">
                                                            {metric.format === 'currency' ? `Ksh ${metric.b.toLocaleString()}` :
                                                                metric.format === 'percent' ? `${metric.b.toFixed(1)}%` : metric.b}
                                                        </span>
                                                        {metric.winner === 'b' && <Badge variant="outline" className="mt-3 bg-blue-500/20 text-blue-400 border-blue-500/30">Leader</Badge>}
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
