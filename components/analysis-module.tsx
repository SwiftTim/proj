"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { Download, TrendingUp, CircleCheck, FileText, Search } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { GPUAnalysisButton } from "./gpu-analysis-button"
import { DoclingAnalysisButton } from "./docling-analysis-button"
import { GoogleAnalysisButton } from "./google-analysis-button"
import { Input } from "@/components/ui/input"
import { generateIntegrityReport } from "@/lib/pdf-generator"

export function AnalysisScorecard() {
  const [county, setCounty] = useState("")
  const [year, setYear] = useState("")
  const [documents, setDocuments] = useState<any[]>([])
  const [result, setResult] = useState<any | null>(null)
  const [countySearch, setCountySearch] = useState("")

  // --- Fetch uploaded documents from your DB ---
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const res = await fetch("/api/documents")
        const data = await res.json()
        if (data.success) {
          setDocuments(data.documents)
        }
      } catch (err) {
        console.error("Failed to fetch documents:", err)
      }
    }
    fetchDocuments()
  }, [])

  // Dynamic Filters: Only show options that have uploaded data
  const availableCounties = Array.from(new Set(documents.map(d => d.county))).sort()
  const filteredCounties = availableCounties.filter(c =>
    c.toLowerCase().includes(countySearch.toLowerCase())
  )

  const availableYears = Array.from(new Set(
    documents.filter(d => d.county === county).map(d => d.year)
  )).sort().reverse() // Newest first

  // Derived state for current doc
  const currentDoc = documents.find((d) => d.county === county && d.year === year)

  // Auto-load existing analysis if available
  useEffect(() => {
    if (currentDoc && currentDoc.analysis_id) {
      setResult({
        county: currentDoc.county,
        year: currentDoc.year,
        summary_text: currentDoc.summary_text,
        key_metrics: currentDoc.key_metrics,
        intelligence: currentDoc.intelligence,
        method: "Stored Audit Report",
        id: currentDoc.analysis_id
      })
    } else {
      setResult(null)
    }
  }, [county, year, documents])

  // --- Helper to format numbers legibly ---
  const formatValue = (key: string, value: any) => {
    if (value === null || value === undefined || value === 0) return "Not Found"
    if (key.includes("pct") || key.includes("rate") || key.includes("performance")) return `${value}%`
    if (typeof value === "number" && value > 1000) return `Ksh ${value.toLocaleString()}`
    return String(value)
  }

  // --- Handle Unified Results ---
  const handleGPUResults = (data: any) => {
    if (!data) return

    // Normalize response formats across pipelines
    const interpreted = data.interpreted_data || data
    const summary = interpreted.summary_text || data.summary_text || interpreted.executive_summary || "No summary generated."

    const keyMetrics = interpreted.key_metrics || {
      ...(data.extraction?.revenue || {}),
      ...(data.extraction?.expenditure || {}),
      ...(data.extraction?.debt || {}),
      ...(data.extraction?.health_fif || {}),
      ...(data.key_metrics || {})
    }

    const intel = interpreted.intelligence || data.intelligence || {
      ...(data.analysis?.risk_assessment || {}),
      transparency_risk_score: data.analysis?.risk_assessment?.score || 0,
      flags: data.analysis?.risk_assessment?.flags || []
    }

    setResult({
      ...interpreted,
      county: interpreted.county || county,
      method: data.method || interpreted.method || "Analysis Engine",
      summary_text: summary,
      key_metrics: keyMetrics,
      intelligence: intel,
      raw_verified_data: data.raw_verified_data || interpreted.raw_verified_data,
      processing_time_sec: data.processing_time_sec || interpreted.processing_time_sec
    })

    // Refresh documents to show the new analysis immediately in local state
    fetch("/api/documents")
      .then(res => res.json())
      .then(data => { if (data.success) setDocuments(data.documents) })
  }

  // --- Download Professional Integrity Report ---
  const downloadSummary = () => {
    if (!result) return
    generateIntegrityReport(result)
  }

  return (
    <Card className="max-w-4xl mx-auto border-slate-800 bg-slate-950/50 backdrop-blur-xl shadow-2xl overflow-hidden">
      <CardHeader className="border-b border-slate-800/50 bg-slate-900/20">
        <CardTitle className="text-white text-2xl font-bold flex items-center">
          <TrendingUp className="mr-3 h-6 w-6 text-blue-500" />
          Budget Performance Analyzer
        </CardTitle>
        <CardDescription className="text-slate-400">
          Run high-precision AI diagnostics on official county budget reports.
        </CardDescription>
      </CardHeader>

      <CardContent className="p-8 space-y-8">
        {/* --- Selection Grid --- */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 ml-1">Jurisdiction</label>
            <Select value={county} onValueChange={(val) => { setCounty(val); setYear("") }}>
              <SelectTrigger className="bg-slate-900/80 border-slate-800 text-white h-12">
                <SelectValue placeholder="Select County" />
              </SelectTrigger>
              <SelectContent className="bg-slate-950 border-slate-800 text-white shadow-[0_20px_50px_rgba(0,0,0,0.5)] min-w-[240px]">
                <div className="p-2 border-b border-slate-800 flex items-center gap-2 sticky top-0 bg-slate-950 z-20">
                  <Search className="h-4 w-4 text-slate-400" />
                  <Input
                    placeholder="Search available counties..."
                    value={countySearch}
                    onChange={(e) => setCountySearch(e.target.value)}
                    className="h-9 text-sm bg-slate-900 border-slate-800 text-white focus-visible:ring-blue-500"
                  />
                </div>
                <div className="max-h-[300px] overflow-y-auto p-1 py-1">
                  {filteredCounties.length > 0 ? (
                    filteredCounties.map((c) => (
                      <SelectItem
                        key={c}
                        value={c}
                        className="hover:bg-blue-600/20 focus:bg-blue-600/20 cursor-pointer rounded-md my-0.5 transition-colors border border-transparent hover:border-blue-500/30"
                      >
                        <span className="font-semibold">{c}</span>
                      </SelectItem>
                    ))
                  ) : (
                    <div className="p-4 text-xs text-slate-500 text-center uppercase font-bold">No uploaded documents found</div>
                  )}
                </div>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 ml-1">Period</label>
            <Select value={year} onValueChange={setYear} disabled={!county}>
              <SelectTrigger className="bg-slate-900/80 border-slate-800 text-white h-12">
                <SelectValue placeholder={county ? "Select Financial Year" : "Select County first"} />
              </SelectTrigger>
              <SelectContent className="bg-slate-900 border-slate-800 text-white shadow-2xl">
                {availableYears.map((y) => (
                  <SelectItem key={y} value={y} className="hover:bg-slate-800 focus:bg-slate-800 cursor-pointer">{y}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* --- Analysis Actions --- */}
        <div className="flex flex-col items-center gap-6 bg-slate-900/30 p-10 rounded-3xl border-2 border-dashed border-slate-800 transition-all hover:bg-slate-900/40">
          {currentDoc ? (
            <div className="flex flex-col items-center gap-6">
              {result?.method === "Stored Audit Report" && (
                <div className="bg-emerald-500/10 border border-emerald-500/20 px-6 py-3 rounded-full flex items-center gap-3 animate-pulse">
                  <div className="h-2 w-2 bg-emerald-500 rounded-full" />
                  <span className="text-xs font-black uppercase tracking-widest text-emerald-400">Analysis Database Hit: Ready for Download</span>
                </div>
              )}

              <div className="flex flex-wrap justify-center gap-4">
                <GPUAnalysisButton
                  pdfId={currentDoc.filenames[0]}
                  county={county}
                  year={year}
                  onAnalysisComplete={handleGPUResults}
                />
                <DoclingAnalysisButton
                  pdfId={currentDoc.filenames[0]}
                  county={county}
                  year={year}
                  onAnalysisComplete={handleGPUResults}
                />
                <GoogleAnalysisButton
                  pdfId={currentDoc.filenames[0]}
                  county={county}
                  year={year}
                  onAnalysisComplete={handleGPUResults}
                />
              </div>

              {!result && (
                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-[0.2em]">Select a pipeline to trigger diagnostic</p>
              )}
            </div>
          ) : (
            <div className="text-center">
              <div className="bg-slate-800/50 p-4 rounded-full w-fit mx-auto mb-4 border border-slate-700">
                <FileText className="h-8 w-8 text-slate-500 opacity-50" />
              </div>
              <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">Awaiting Selection</p>
              <p className="text-xs text-slate-500 mt-1 max-w-[250px] mx-auto">Only counties with uploaded PDF reports are visible above.</p>
            </div>
          )}
        </div>

        {/* --- Results Display --- */}
        {result && (
          <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Header with Risk Score */}
            <div className="flex items-end justify-between border-b border-slate-800 pb-6">
              <div className="space-y-1">
                <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 mb-2 uppercase tracking-tighter text-[10px]">Audit Pass Verified</Badge>
                <h3 className="text-4xl font-extrabold text-white tracking-tight">
                  {result.county || county}
                </h3>
                <p className="text-sm font-medium text-slate-500 uppercase tracking-[0.2em] flex items-center">
                  FY {year} <span className="mx-3 text-slate-800">|</span> {result.method}
                </p>
              </div>

              {result.intelligence?.transparency_risk_score !== undefined && (
                <div className="flex flex-col items-end">
                  <span className="text-[10px] font-black uppercase text-slate-500 mb-2 tracking-widest">Fiscal Risk Verdict</span>
                  <div className="flex items-baseline gap-1">
                    <span className={`text-4xl font-black ${result.intelligence.transparency_risk_score > 60 ? 'text-red-500' : 'text-emerald-500'}`}>
                      {result.intelligence.transparency_risk_score}
                    </span>
                    <span className="text-slate-600 font-bold text-lg">/100</span>
                  </div>
                </div>
              )}
            </div>

            {/* Verification Pillar (OSR) */}
            {result.raw_verified_data && (
              <Card className="border-emerald-500/20 bg-emerald-500/[0.03] overflow-hidden shadow-emerald-500/5 shadow-2xl">
                <div className="bg-emerald-500/10 px-5 py-3 border-b border-emerald-500/10 flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <CircleCheck className="h-4 w-4 text-emerald-500" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-emerald-400">Immutable Table Benchmarks</span>
                  </div>
                  <Badge variant="outline" className="text-[10px] border-emerald-500/30 text-emerald-500 bg-emerald-500/5 px-2 uppercase font-black">{result.raw_verified_data.source}</Badge>
                </div>
                <CardContent className="p-8">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
                    <div className="space-y-2 border-r border-emerald-500/10 pr-4">
                      <p className="text-[11px] text-emerald-500/50 uppercase font-black tracking-widest">OSR Revenue Target</p>
                      <p className="text-2xl font-mono font-black text-emerald-400">{result.raw_verified_data.osr_target || "0"}</p>
                    </div>
                    <div className="space-y-2 border-r border-emerald-500/10 pr-4">
                      <p className="text-[11px] text-emerald-500/50 uppercase font-black tracking-widest">Actual OSR Collected</p>
                      <p className="text-2xl font-mono font-black text-emerald-400">{result.raw_verified_data.osr_actual || "0"}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-[11px] text-emerald-500/50 uppercase font-black tracking-widest">OSR Percentage Score</p>
                      <p className="text-2xl font-mono font-black text-emerald-400">{result.raw_verified_data.osr_performance || "N/A"}%</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* AI Narrative Analysis */}
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-3xl blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
              <div className="relative bg-slate-900/80 backdrop-blur-sm border border-slate-800 text-white p-10 rounded-3xl shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                  <div className="bg-blue-500/20 p-2 rounded-xl border border-blue-500/30">
                    <TrendingUp className="h-5 w-5 text-blue-400" />
                  </div>
                  <h4 className="font-black uppercase tracking-[0.3em] text-[11px] text-blue-400">Senior Audit Narrative</h4>
                </div>
                <div className="text-lg whitespace-pre-line leading-relaxed font-medium text-slate-300 antialiased">
                  {result.summary_text}
                </div>
              </div>
            </div>

            {/* Detailed Metric Cards (Fixed White Boxes) */}
            {result.key_metrics && (
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
                {Object.entries(result.key_metrics).map(([key, value]) => (
                  <Card key={key} className="bg-slate-900 border-slate-800 shadow-xl overflow-hidden group hover:border-slate-700 transition-colors">
                    <CardContent className="p-6 relative text-left">
                      <div className="absolute top-0 left-0 w-1 h-full bg-slate-800 group-hover:bg-blue-500/50 transition-colors" />
                      <p className="text-[10px] text-slate-500 uppercase font-black tracking-wider mb-2">{key.replaceAll("_", " ")}</p>
                      <p className="text-xl font-black text-white tracking-tight">{formatValue(key, value)}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-center pt-8 border-t border-slate-800/50">
              <Button onClick={downloadSummary} variant="outline" className="bg-white text-black hover:bg-slate-100 px-12 h-14 rounded-full font-black uppercase tracking-widest text-xs transition-transform active:scale-95 shadow-2xl">
                <Download className="h-4 w-4 mr-3" /> Download Integrity Report
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
