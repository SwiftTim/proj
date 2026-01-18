"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { Loader2, Download, TrendingUp } from "lucide-react"
import jsPDF from "jspdf"

export function AnalysisScorecard() {
  const [county, setCounty] = useState("")
  const [year, setYear] = useState("")
  const [loading, setLoading] = useState(false)
  const [documents, setDocuments] = useState<any[]>([])
  const [selectedDoc, setSelectedDoc] = useState<any | null>(null)
  const [result, setResult] = useState<any | null>(null)

  // --- Fetch uploaded documents from your DB ---
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

  const counties = [...new Set(documents.map((d) => d.county))]
  const years = [...new Set(documents.map((d) => d.year))]

  // --- Analyze selected county PDF via FastAPI ---
  const analyzeDocument = async () => {
    if (!county || !year) return alert("Select a county and year first")

    setLoading(true)
    setResult(null)

    const doc = documents.find((d) => d.county === county && d.year === year)
    if (!doc) {
      alert("No matching document found in database.")
      setLoading(false)
      return
    }

    const fileName = doc.filenames[0]
    const filePath = `/uploads/${fileName}`

    try {
      const fileRes = await fetch(filePath)
      const blob = await fileRes.blob()

      const formData = new FormData()
      formData.append("county", county)
      formData.append("year", year)
      formData.append("file", blob, fileName)

      const res = await fetch("http://127.0.0.1:8000/analyze_pdf", {
        method: "POST",
        body: formData,
      })

      const data = await res.json()
      if (data.error) {
        alert("Error analyzing document: " + data.error)
      } else {
        setResult(data)
        setSelectedDoc(doc)
      }
    } catch (err) {
      console.error(err)
      alert("Failed to connect to analysis service.")
    } finally {
      setLoading(false)
    }
  }

  // --- Download PDF Summary ---
  const downloadSummary = () => {
    if (!result || !selectedDoc) return

    const pdf = new jsPDF()
    pdf.setFont("helvetica", "bold")
    pdf.text(`${result.county} County Budget Summary`, 20, 20)
    pdf.setFont("helvetica", "normal")

    pdf.text(`Year: ${year}`, 20, 35)
    pdf.text(`Generated: ${new Date().toLocaleDateString()}`, 20, 45)

    pdf.setFont("helvetica", "bold")
    pdf.text("Extracted Key Metrics:", 20, 65)
    pdf.setFont("helvetica", "normal")

    if (result.key_metrics) {
      let y = 75
      for (const [key, value] of Object.entries(result.key_metrics as Record<string, any>)) {
        pdf.text(`${key.replaceAll("_", " ")}: ${String(value)}`, 25, y)
        y += 10
      }
    }

    pdf.setFont("helvetica", "bold")
    pdf.text("Summary:", 20, 130)
    pdf.setFont("helvetica", "normal")
    const textLines = pdf.splitTextToSize(result.summary_text, 170)
    pdf.text(textLines, 20, 140)

    pdf.save(`${result.county}_${year}_Summary.pdf`)
  }

  return (
    <Card className="max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle>Budget Performance Analyzer</CardTitle>
        <CardDescription>
          Select a county and year to generate an AI-driven performance summary directly from the official budget PDF.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* --- County & Year Selection --- */}
        <div className="flex flex-col md:flex-row gap-4">
          <Select value={county} onValueChange={setCounty}>
            <SelectTrigger className="w-full md:w-1/2">
              <SelectValue placeholder="Select County" />
            </SelectTrigger>
            <SelectContent>
              {counties.map((c) => (
                <SelectItem key={c} value={c}>
                  {c}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={year} onValueChange={setYear}>
            <SelectTrigger className="w-full md:w-1/2">
              <SelectValue placeholder="Select Year" />
            </SelectTrigger>
            <SelectContent>
              {years.map((y) => (
                <SelectItem key={y} value={y}>
                  {y}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* --- Analyze Button --- */}
        <div className="flex justify-end">
          <Button onClick={analyzeDocument} disabled={loading || !county || !year}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <TrendingUp className="h-4 w-4 mr-2" />
            )}
            Analyze
          </Button>
        </div>

        {/* --- Display Extracted Results --- */}
        {result && !result.error && (
          <div className="mt-6 space-y-4">
            <h3 className="text-xl font-semibold text-center">
              🏛️ {result.county} County – FY {year} Performance Summary
            </h3>

            <div className="bg-muted p-4 rounded-md text-sm whitespace-pre-line">
              {result.summary_text}
            </div>

            {/* --- Key Metrics Section --- */}
            {result.key_metrics && (
              <div className="bg-muted/40 p-3 rounded-md">
                <h4 className="font-semibold mb-2">📊 Key Metrics</h4>
                <ul className="list-disc pl-6">
                  {Object.entries(result.key_metrics).map(([key, value]) => (
                    <li key={key}>
                      <strong>{key.replaceAll("_", " ")}:</strong> {String(value)}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="flex justify-center">
              <Button onClick={downloadSummary}>
                <Download className="h-4 w-4 mr-2" /> Download Summary
              </Button>
            </div>
          </div>
        )}

        {result?.error && <p className="text-red-500 text-center mt-4">{result.error}</p>}
      </CardContent>
    </Card>
  )
}
