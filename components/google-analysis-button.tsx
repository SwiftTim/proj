"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"
import { Box, CheckCircle2, Loader2, AlertTriangle, Sparkles } from "lucide-react"

interface GoogleAnalysisButtonProps {
    pdfId: string
    county: string
    year: string
    onAnalysisComplete: (data: any) => void
}

export function GoogleAnalysisButton({ pdfId, county, year, onAnalysisComplete }: GoogleAnalysisButtonProps) {
    const [open, setOpen] = useState(false)
    const [progress, setProgress] = useState(0)
    const [status, setStatus] = useState<"idle" | "processing" | "complete" | "error">("idle")
    const [stage, setStage] = useState("")
    const [error, setError] = useState("")

    const stages = [
        { text: "Connecting to Google AI Studio...", prog: 15 },
        { text: "Uploading PDF to Gemini 1.5 (2M Context)...", prog: 40 },
        { text: "Gemini is reading the entire document...", prog: 70 },
        { text: "Extracting county-specific fiscal flows...", prog: 85 },
        { text: "Formatting structured JSON report...", prog: 95 },
        { text: "Finalizing...", prog: 100 }
    ]

    const handleGoogleAnalysis = async () => {
        setOpen(true)
        setStatus("processing")
        setError("")
        setProgress(0)

        let currentStep = 0
        const progressInterval = setInterval(() => {
            if (currentStep < stages.length - 1) {
                setStage(stages[currentStep].text)
                setProgress(stages[currentStep].prog)
                currentStep++
            }
        }, 3000) // Gemini might take a bit longer for large PDFs

        try {
            setStage("Initializing Gemini Pipeline...")

            const response = await fetch('/api/analyze/gemini', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pdfId: pdfId,
                    county: county,
                    year: year
                })
            })

            clearInterval(progressInterval)

            if (!response.ok) {
                let errorMsg = "Google Analysis failed"
                try {
                    const errData = await response.json()
                    errorMsg = errData.error || errData.detail || errorMsg
                } catch (e) {
                    const txt = await response.text()
                    errorMsg = txt || response.statusText
                }
                throw new Error(errorMsg)
            }

            setProgress(100)
            setStage("Success!")
            setStatus("complete")

            const result = await response.json()
            console.log("🌟 Google Gemini Result:", result)

            setTimeout(() => {
                setOpen(false)
                onAnalysisComplete(result.data)
            }, 1000)

        } catch (err: any) {
            clearInterval(progressInterval)
            console.error("Google Analysis Error:", err)
            setStatus("error")
            if (err.message && err.message.includes("Failed to fetch")) {
                setError("Connection Error: Is the local Python backend running?")
            } else {
                setError(err.message)
            }
        }
    }

    return (
        <>
            <Button
                onClick={handleGoogleAnalysis}
                className="bg-blue-600 hover:bg-blue-700 text-white border-b-4 border-blue-800 active:border-b-0 transition-all font-bold shadow-lg shadow-blue-500/20"
            >
                <Sparkles className="mr-2 h-4 w-4 text-yellow-300 fill-yellow-300" />
                Google Gemini (Full PDF)
                <Badge variant="secondary" className="ml-2 bg-white/10 text-white border-0 backdrop-blur-sm">2.5 Flash</Badge>
            </Button>

            <Dialog open={open} onOpenChange={(val) => { if (status !== "processing") setOpen(val) }}>
                <DialogContent className="sm:max-w-md border-slate-800 bg-slate-950 text-white">
                    <DialogHeader>
                        <DialogTitle className="flex items-center text-white">
                            <Box className="mr-2 h-5 w-5 text-blue-500" />
                            Google AI Studio Analysis
                        </DialogTitle>
                        <DialogDescription className="text-slate-400">
                            Using Gemini 2.5 Flash with 2-Million Token Context. High-performance extraction powered by Google Cloud.
                        </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-6 py-4">
                        {status === "error" ? (
                            <div className="flex items-center space-x-2 text-red-400 bg-red-950/20 p-4 rounded-xl border border-red-900/30">
                                <AlertTriangle className="h-5 w-5" />
                                <span className="text-sm font-medium">{error || "Analysis failed. Google server might be busy."}</span>
                            </div>
                        ) : (
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm font-medium text-slate-300">
                                    <span className="flex items-center">
                                        {status === "processing" && <Loader2 className="mr-2 h-3 w-3 animate-spin text-blue-500" />}
                                        {stage}
                                    </span>
                                    <span className="text-blue-400">{progress}%</span>
                                </div>
                                <Progress value={progress} className="h-2 bg-slate-800" />
                            </div>
                        )}

                        <div className="rounded-2xl bg-slate-900/50 border border-slate-800 p-5 space-y-4">
                            <div className="flex items-center text-sm font-bold text-slate-300">
                                {progress > 40 ? <CheckCircle2 className="mr-2 h-4 w-4 text-emerald-500" /> : <Loader2 className={`mr-2 h-4 w-4 ${progress > 10 ? "animate-spin text-blue-500" : "text-slate-700"}`} />}
                                Gemini 2.5 Long-Context Read
                            </div>
                            <div className="flex items-center text-sm font-bold text-slate-300">
                                {progress >= 100 ? <CheckCircle2 className="mr-2 h-4 w-4 text-emerald-500" /> : <Loader2 className={`mr-2 h-4 w-4 ${progress > 70 ? "animate-spin text-blue-500" : "text-slate-700"}`} />}
                                Zero-Shot Data Extraction
                            </div>
                        </div>

                        {status === "error" && (
                            <Button onClick={() => setOpen(false)} variant="outline" className="w-full border-slate-800 hover:bg-slate-900 text-white">
                                Close & Retry
                            </Button>
                        )}

                        <div className="text-[10px] text-center text-slate-600 font-bold uppercase tracking-widest">
                            Gemini 2.5 Flash • Serverless Pipeline
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </>
    )
}
