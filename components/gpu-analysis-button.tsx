"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"
import { Cpu, CheckCircle2, Loader2, AlertTriangle } from "lucide-react"

interface GPUAnalysisButtonProps {
    pdfId: string // This acts as filename
    county: string
    year: string
    onAnalysisComplete: (data: any) => void
}

export function GPUAnalysisButton({ pdfId, county, year, onAnalysisComplete }: GPUAnalysisButtonProps) {
    const [open, setOpen] = useState(false)
    const [progress, setProgress] = useState(0)
    const [status, setStatus] = useState<"idle" | "processing" | "complete" | "error">("idle")
    const [stage, setStage] = useState("")
    const [error, setError] = useState("")

    const stages = [
        { text: "Initializing OCRFlux-3B Vision Model...", prog: 10 },
        { text: "Extracting tables from PDF (High-Res Vision)...", prog: 30 },
        { text: "Parsing financial data structures...", prog: 50 },
        { text: "Running fiscal analysis (Groq LLaMA-3.1-70B)...", prog: 75 },
        { text: "Generating insights and risk scores...", prog: 90 },
        { text: "Finalizing report...", prog: 100 }
    ]

    const handleGPUAnalysis = async () => {
        setOpen(true)
        setStatus("processing")
        setError("")
        setProgress(0)

        // Simulate progress while waiting for response since backend doesn't stream progress yet
        let currentStep = 0
        const progressInterval = setInterval(() => {
            if (currentStep < stages.length - 1) {
                setStage(stages[currentStep].text)
                setProgress(stages[currentStep].prog)
                currentStep++
            }
        }, 2000)

        try {
            setStage("Submitting to Hybrid Engine...")

            const response = await fetch('/api/analyze/gpu', { // Call Next.js API
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pdfId: pdfId,
                    county: county,
                    year: year,
                    extraction_model: 'ocrflux-3b',
                    analysis_model: 'groq-llama-70b',
                    use_vision: true
                })
            })

            clearInterval(progressInterval)

            if (!response.ok) {
                let errorMsg = "Analysis failed"
                try {
                    const errData = await response.json()
                    errorMsg = errData.detail || errorMsg
                } catch (e) {
                    const txt = await response.text()
                    errorMsg = txt || response.statusText
                }
                throw new Error(errorMsg)
            }

            setProgress(100)
            setStage("Complete!")
            setStatus("complete")

            const result = await response.json()
            console.log("🚀 GPU Analysis Result:", result)

            // Wait a moment for user to see completion
            setTimeout(() => {
                setOpen(false)
                onAnalysisComplete(result.data)
            }, 1000)

        } catch (err: any) {
            clearInterval(progressInterval)
            console.error("GPU Analysis Error:", err)
            setStatus("error")
            if (err.message && err.message.includes("Failed to fetch")) {
                setError("Connection Error: Is the local Python backend running on port 8000?")
            } else {
                setError(err.message)
            }
        }
    }

    return (
        <>
            <Button
                onClick={handleGPUAnalysis}
                className="bg-purple-600 hover:bg-purple-700 text-white shadow-lg shadow-purple-500/20 font-bold"
            >
                <Cpu className="mr-2 h-4 w-4" />
                Local Analysis
                <Badge variant="secondary" className="ml-2 bg-white/10 text-white border-0 backdrop-blur-sm">95% Acc</Badge>
            </Button>

            <Dialog open={open} onOpenChange={(val) => { if (status !== "processing") setOpen(val) }}>
                <DialogContent className="sm:max-w-md border-slate-800 bg-slate-950 text-white">
                    <DialogHeader>
                        <DialogTitle className="text-white">Local Document Analysis</DialogTitle>
                        <DialogDescription className="text-slate-400">
                            Running Deep Learning Pipeline: OCRFlux-3B (Vision) + Groq LLaMA-70B
                        </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-6 py-4">
                        {status === "error" ? (
                            <div className="flex items-center space-x-2 text-red-400 bg-red-950/20 p-4 rounded-xl border border-red-900/30">
                                <AlertTriangle className="h-5 w-5" />
                                <span className="text-sm font-medium">{error || "Analysis failed. Ensure the local backend is running."}</span>
                            </div>
                        ) : (
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm font-medium text-slate-300">
                                    <span>{stage}</span>
                                    <span className="text-purple-400">{progress}%</span>
                                </div>
                                <Progress value={progress} className="h-2 bg-slate-800" />
                            </div>
                        )}

                        <div className="rounded-2xl bg-slate-900/50 border border-slate-800 p-5 space-y-4">
                            <div className="flex items-center text-sm font-bold text-slate-300">
                                {progress > 10 ? <CheckCircle2 className="mr-2 h-4 w-4 text-emerald-500" /> : <Loader2 className="mr-2 h-4 w-4 animate-spin text-purple-500" />}
                                Vision Extraction (OCRFlux)
                            </div>
                            <div className="flex items-center text-sm font-bold text-slate-300">
                                {progress > 70 ? <CheckCircle2 className="mr-2 h-4 w-4 text-emerald-500" /> : <Loader2 className={`mr-2 h-4 w-4 ${progress > 30 ? "animate-spin text-purple-500" : "text-slate-700"}`} />}
                                Reasoning & Validation (Groq)
                            </div>
                        </div>

                        {status === "error" && (
                            <Button onClick={() => setOpen(false)} variant="outline" className="w-full border-slate-800 hover:bg-slate-900 text-white">
                                Close
                            </Button>
                        )}
                    </div>
                </DialogContent>
            </Dialog>
        </>
    )
}
