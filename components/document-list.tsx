"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  FileText,
  Eye,
  Search,
  Calendar,
  MapPin,
  TrendingUp,
  Loader2,
  XCircle,
  Download,
  CheckCircle,
} from "lucide-react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { KENYA_COUNTIES, FINANCIAL_YEARS } from "@/lib/constants"
import jsPDF from "jspdf"

export function DocumentList() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCounty, setSelectedCounty] = useState("")
  const [selectedYear, setSelectedYear] = useState("")
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  // Analysis states
  const [analyzing, setAnalyzing] = useState(false)
  const [docToAnalyze, setDocToAnalyze] = useState<any | null>(null)
  const [analyzeCounty, setAnalyzeCounty] = useState("")
  const [showDialog, setShowDialog] = useState(false)
  const [countySearch, setCountySearch] = useState("")
  const [result, setResult] = useState<any | null>(null)

  const fetchDocs = async () => {
    try {
      const res = await fetch("/api/documents")
      const data = await res.json()
      if (data.success) setDocuments(data.documents)
    } catch (err) {
      console.error("Failed to fetch documents:", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDocs()
  }, [])

  const allCounties = KENYA_COUNTIES
  const allYears = FINANCIAL_YEARS

  const filteredDocuments = documents.filter((doc) => {
    const displayedCounty = doc.analysis_county || doc.county
    const matchesSearch =
      displayedCounty.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.filenames?.join(", ").toLowerCase().includes(searchQuery.toLowerCase())

    const matchesCounty = !selectedCounty || selectedCounty === "All Counties" ||
      doc.county === selectedCounty ||
      doc.analysis_county === selectedCounty
    const matchesYear = !selectedYear || selectedYear === "All Years" || doc.year === selectedYear

    return matchesSearch && matchesCounty && matchesYear
  })

  // --- Download PDF Summary ---
  const downloadReport = (doc: any) => {
    const pdf = new jsPDF()
    pdf.setFont("helvetica", "bold")
    pdf.text(`${doc.county} County Budget Report`, 20, 20)
    pdf.setFont("helvetica", "normal")

    pdf.text(`Year: ${doc.year}`, 20, 35)
    pdf.text(`Generated: ${new Date().toLocaleDateString()}`, 20, 45)

    pdf.setFont("helvetica", "bold")
    pdf.text("Extracted Key Metrics:", 20, 65)
    pdf.setFont("helvetica", "normal")

    if (doc.key_metrics) {
      let y = 75
      for (const [key, value] of Object.entries(doc.key_metrics as Record<string, any>)) {
        pdf.text(`${key.replaceAll("_", " ")}: ${String(value)}`, 25, y)
        y += 10
      }
    }

    pdf.setFont("helvetica", "bold")
    pdf.text("Summary Insights:", 20, 130)
    pdf.setFont("helvetica", "normal")

    const cleanSummary = (doc.summary_text || "No summary available.").replace(/[#*]/g, "")
    const textLines = pdf.splitTextToSize(cleanSummary, 170)
    pdf.text(textLines, 20, 140)

    pdf.save(`${doc.county}_Report_${doc.year}.pdf`)
  }

  return (
    <div className="space-y-6">
      {/* --- Filters --- */}
      <Card>
        <CardHeader>
          <CardTitle>Inventory & Reports</CardTitle>
          <CardDescription>View all stored budget documents and generated reports</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by county or filename..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            <Select value={selectedCounty ?? "All Counties"} onValueChange={setSelectedCounty}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="Select county" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="All Counties">All Counties</SelectItem>
                {allCounties.map((county) => (
                  <SelectItem key={county} value={county}>
                    {county}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={selectedYear ?? "All Years"} onValueChange={setSelectedYear}>
              <SelectTrigger className="w-full md:w-32">
                <SelectValue placeholder="Year" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="All Years">All Years</SelectItem>
                {allYears.map((year) => (
                  <SelectItem key={year} value={year}>
                    {year}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* --- Document List --- */}
      {loading ? (
        <div className="flex justify-center p-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : filteredDocuments.length > 0 ? (
        <div className="space-y-4">
          {filteredDocuments.map((doc) => (
            <Card key={doc.id} className={`overflow-hidden border-l-4 ${doc.analysis_id ? "border-l-emerald-500" : "border-l-muted"}`}>
              <CardContent className="p-0">
                <div className="flex flex-col md:flex-row items-center justify-between p-6 gap-4">
                  <div className="flex items-center gap-4 flex-1">
                    <div className={`p-3 rounded-full ${doc.analysis_id ? "bg-emerald-100 text-emerald-600" : "bg-muted text-muted-foreground"}`}>
                      {doc.analysis_id ? <CheckCircle className="h-6 w-6" /> : <FileText className="h-6 w-6" />}
                    </div>
                    <div>
                      <h4 className="font-bold text-lg">{doc.analysis_county || doc.county} County</h4>
                      <p className="text-sm text-muted-foreground flex items-center gap-2">
                        <Calendar className="h-3 w-3" /> FY {doc.year} • {doc.filenames[0]}
                      </p>
                      {doc.analysis_id && (
                        <Badge variant="outline" className="mt-2 bg-emerald-50 text-emerald-700 border-emerald-200">
                          Report Generated
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {doc.analysis_id && (
                      <Button
                        onClick={() => downloadReport(doc)}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Download Report
                      </Button>
                    )}

                    {/* Non-report documents have no action buttons per user request, 
                          except maybe the basic raw file preview if you consider that part of reports */}
                  </div>
                </div>

                {doc.analysis_id && (
                  <div className="bg-muted/30 px-6 py-4 border-t text-sm italic text-muted-foreground line-clamp-1">
                    "{doc.summary_text.substring(0, 150)}..."
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <XCircle className="h-12 w-12 text-muted-foreground mb-4 opacity-20" />
            <p className="text-muted-foreground">No documents found matching your filter.</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
