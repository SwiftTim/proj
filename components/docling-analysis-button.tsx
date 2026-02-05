"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"
import { FileSearch, CheckCircle2, Loader2, AlertTriangle, FileText } from "lucide-react"

interface DoclingAnalysisButtonProps {
    pdfId: string // This acts as filename
    county: string
    year: string
    onAnalysisComplete: (data: any) => void
}

export function DoclingAnalysisButton({ pdfId, county, year, onAnalysisComplete }: DoclingAnalysisButtonProps) {
    const [open, setOpen] = useState(false)
    const [progress, setProgress] = useState(0)
    const [status, setStatus] = useState<"idle" | "processing" | "complete" | "error">("idle")
    const [stage, setStage] = useState("")
    const [error, setError] = useState("")

    const stages = [
        { text: "Slicing PDF locally...", prog: 10 },
        { text: "Uploading to Colab GPU Instance...", prog: 30 },
        { text: "Docling: Converting Structural PDF to Markdown...", prog: 60 },
        { text: "Groq: Synthesizing Detailed Auditor Report...", prog: 85 },
        { text: "Finalizing Integrity Summary...", prog: 100 }
    ]

    const handleDoclingAnalysis = async () => {
        setOpen(true)
        setStatus("processing")
        setError("")
        setProgress(0)

        // Simulate progress while waiting for response
        let currentStep = 0
        const progressInterval = setInterval(() => {
            if (currentStep < stages.length - 1) {
                setStage(stages[currentStep].text)
                setProgress(stages[currentStep].prog)
                currentStep++
            }
        }, 3000)

        try {
            setStage("Initializing Docling Pipeline...")

            const response = await fetch('/api/analyze/docling', {
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
                let errorMsg = "Docling analysis failed"
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
            console.log("🚀 Docling Analysis Result:", result)

            // Wait a moment for user to see completion
            setTimeout(() => {
                setOpen(false)
                onAnalysisComplete(result.data)
            }, 1000)

        } catch (err: any) {
            clearInterval(progressInterval)
            console.error("Docling Analysis Error:", err)
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
                onClick={handleDoclingAnalysis}
                className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/20 font-bold"
            >
                <FileSearch className="mr-2 h-4 w-4" />
                GPU Docling Analysis
                <Badge variant="secondary" className="ml-2 bg-white/10 text-white border-0 backdrop-blur-sm">High Fidelity</Badge>
            </Button>

            <Dialog open={open} onOpenChange={(val) => { if (status !== "processing") setOpen(val) }}>
                <DialogContent className="sm:max-w-md border-slate-800 bg-slate-950 text-white">
                    <DialogHeader>
                        <DialogTitle className="text-white">GPU Docling Structural Analysis</DialogTitle>
                        <DialogDescription className="text-slate-400">
                            Converting PDF to Markdown preserving complex table grids via Docling.
                        </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-6 py-4">
                        {status === "error" ? (
                            <div className="flex items-center space-x-2 text-red-400 bg-red-950/20 p-4 rounded-xl border border-red-900/30">
                                <AlertTriangle className="h-5 w-5" />
                                <span className="text-sm font-medium">{error || "Analysis failed. Docling is a heavy library and may time out on first run."}</span>
                            </div>
                        ) : (
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm font-medium text-slate-300">
                                    <span>{stage}</span>
                                    <span className="text-indigo-400">{progress}%</span>
                                </div>
                                <Progress value={progress} className="h-2 bg-slate-800" />
                            </div>
                        )}

                        <div className="rounded-2xl bg-slate-900/50 border border-slate-800 p-5 space-y-4">
                            <div className="flex items-center text-sm font-bold text-slate-300">
                                {progress > 40 ? <CheckCircle2 className="mr-2 h-4 w-4 text-emerald-500" /> : <Loader2 className="mr-2 h-4 w-4 animate-spin text-indigo-500" />}
                                PDF to Markdown (Docling)
                            </div>
                            <div className="flex items-center text-sm font-bold text-slate-300">
                                {progress > 85 ? <CheckCircle2 className="mr-2 h-4 w-4 text-emerald-500" /> : <Loader2 className={`mr-2 h-4 w-4 ${progress > 40 ? "animate-spin" : "text-slate-700"}`} />}
                                Structural Parsing (Groq)
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
