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
} from "lucide-react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"

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
  const [result, setResult] = useState<any | null>(null)

  useEffect(() => {
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
    fetchDocs()
  }, [])

  const counties = [...new Set(documents.map((doc) => doc.county))].sort()
  const years = [...new Set(documents.map((doc) => doc.year))].sort()

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch =
      doc.county.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.filenames?.join(", ").toLowerCase().includes(searchQuery.toLowerCase())

    const matchesCounty = !selectedCounty || selectedCounty === "All Counties" || doc.county === selectedCounty
    const matchesYear = !selectedYear || selectedYear === "All Years" || doc.year === selectedYear

    return matchesSearch && matchesCounty && matchesYear
  })

  const getScoreColor = (score: number) => {
    if (score >= 80) return "bg-chart-2/10 text-chart-2 border-chart-2/20"
    if (score >= 60) return "bg-chart-3/10 text-chart-3 border-chart-3/20"
    return "bg-destructive/10 text-destructive border-destructive/20"
  }

  // --- Start analyze flow ---
  const startAnalyze = (doc: any) => {
    setDocToAnalyze(doc)
    setAnalyzeCounty("")
    setShowDialog(true)
    setResult(null)
  }

  // --- Perform actual PDF analysis ---
  const analyzeDocument = async () => {
    if (!analyzeCounty) return alert("Please select a county before analyzing.")

    try {
      setAnalyzing(true)
      const fileName = docToAnalyze.filenames[0]
      const filePath = `/uploads/${fileName}`

      const fileRes = await fetch(filePath)
      const blob = await fileRes.blob()

      const formData = new FormData()
      formData.append("county", analyzeCounty)
      formData.append("file", blob, fileName)

      const res = await fetch("http://127.0.0.1:8000/analyze_pdf", {
        method: "POST",
        body: formData,
      })

      const data = await res.json()
      setResult(data)
      if (data.error) alert("Error analyzing document: " + data.error)
    } catch (err) {
      console.error(err)
      alert("Failed to connect to analysis service.")
    } finally {
      setAnalyzing(false)
      setShowDialog(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* --- Filters --- */}
      <Card>
        <CardHeader>
          <CardTitle>Filter Documents</CardTitle>
          <CardDescription>Search and filter budget documents</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search documents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            <Select value={selectedCounty} onValueChange={setSelectedCounty}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="Select county" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="All Counties">All Counties</SelectItem>
                {counties.map((county) => (
                  <SelectItem key={county} value={county}>
                    {county}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={selectedYear} onValueChange={setSelectedYear}>
              <SelectTrigger className="w-full md:w-32">
                <SelectValue placeholder="Year" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="All Years">All Years</SelectItem>
                {years.map((year) => (
                  <SelectItem key={year} value={year}>
                    {year}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* --- Document Grid --- */}
      {loading ? (
        <p className="text-center text-muted-foreground">Loading documents...</p>
      ) : filteredDocuments.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredDocuments.map((doc) => (
            <Card key={doc.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <CardTitle className="text-lg">{doc.filenames?.join(", ")}</CardTitle>
                      <CardDescription className="flex items-center space-x-4 mt-1">
                        <span className="flex items-center space-x-1">
                          <MapPin className="h-3 w-3" />
                          <span>{doc.county}</span>
                        </span>
                        <span className="flex items-center space-x-1">
                          <Calendar className="h-3 w-3" />
                          <span>{doc.year}</span>
                        </span>
                      </CardDescription>
                    </div>
                  </div>
                  <Badge className={getScoreColor(70)}>70%</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>Uploaded {new Date(doc.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex space-x-2 pt-2">
                  <Button variant="outline" size="sm" onClick={() => window.open(`/uploads/${doc.filenames[0]}`, "_blank")}>
                    <Eye className="h-3 w-3 mr-1" /> View
                  </Button>
                  <Button
                    variant="default"
                    size="sm"
                    onClick={() => startAnalyze(doc)}
                    disabled={analyzing}
                  >
                    {analyzing ? (
                      <Loader2 className="h-3 w-3 animate-spin mr-1" />
                    ) : (
                      <TrendingUp className="h-3 w-3 mr-1" />
                    )}
                    Analyze
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="flex items-center justify-center h-32">
            <div className="text-center text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-2" />
              <p>No documents found matching your criteria</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* --- County Selection Modal --- */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Select County to Analyze</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <Select value={analyzeCounty} onValueChange={setAnalyzeCounty}>
              <SelectTrigger>
                <SelectValue placeholder="Select county..." />
              </SelectTrigger>
              <SelectContent>
                {counties.map((county) => (
                  <SelectItem key={county} value={county}>
                    {county}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button onClick={analyzeDocument} disabled={!analyzeCounty || analyzing}>
              {analyzing ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <TrendingUp className="h-4 w-4 mr-2" />
              )}
              Analyze
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* --- Display Analysis Summary --- */}
      {result && !result.error && (
        <Card className="mt-8 border-green-500/30 shadow-md bg-green-50/30">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">
              🏛️ {result.county} County – Performance Summary
            </CardTitle>
            <CardDescription>Extracted from Analyzer</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="whitespace-pre-line text-sm mb-4">{result.summary_text}</div>

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
          </CardContent>
        </Card>
      )}

      {result?.error && (
        <div className="flex items-center justify-center mt-8 text-red-600">
          <XCircle className="h-5 w-5 mr-2" />
          <p>{result.error}</p>
        </div>
      )}
    </div>
  )
}
