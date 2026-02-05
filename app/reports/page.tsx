"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ArrowLeft, Download, FileText, Calendar, Search, Loader2, FileCheck } from "lucide-react"
import { BudgetChart } from "@/components/budget-chart"
import Link from "next/link"
import { generateIntegrityReport } from "@/lib/pdf-generator"

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")

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
    r.county.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.year.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header */}
      <header className="border-b border-border bg-card sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/dashboard">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Dashboard
                </Link>
              </Button>
              <div className="flex items-center space-x-2">
                <div className="bg-emerald-600 p-1.5 rounded-lg">
                  <FileCheck className="h-5 w-5 text-white" />
                </div>
                <span className="text-xl font-bold">Audit Reports</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Audit Registry</h1>
          <p className="text-muted-foreground">Download finalized AI-audited budget integrity reports.</p>
        </div>

        <Tabs defaultValue="reports" className="space-y-6">
          <TabsList className="bg-muted/50 p-1">
            <TabsTrigger value="reports">Verified Reports</TabsTrigger>
            <TabsTrigger value="analytics">Global Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="reports" className="space-y-6">
            {/* Filters */}
            <Card className="border-border/50 shadow-sm">
              <CardHeader className="pb-4">
                <CardTitle className="text-sm font-medium">Quick Search</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by county or financial year..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 h-11"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Reports List */}
            {loading ? (
              <div className="flex justify-center p-20">
                <Loader2 className="h-10 w-10 animate-spin text-emerald-600" />
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredReports.map((report) => (
                  <Card key={report.id} className="relative group hover:shadow-lg transition-all border-emerald-500/10 hover:border-emerald-500/30 overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500/0 group-hover:bg-emerald-500 transition-all" />
                    <CardHeader>
                      <div className="flex justify-between items-start mb-2">
                        <Badge variant="outline" className="text-[10px] uppercase font-bold border-emerald-500/30 text-emerald-600 bg-emerald-500/5">
                          {report.year}
                        </Badge>
                        <span className="text-[10px] text-muted-foreground flex items-center">
                          <Calendar className="h-3 w-3 mr-1" />
                          {new Date(report.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <CardTitle className="text-xl group-hover:text-emerald-400 transition-colors uppercase tracking-tight">{report.county}</CardTitle>
                      <CardDescription className="line-clamp-3 text-xs leading-relaxed mt-2 h-12">
                        {report.summary_text || "Automated integrity assessment completed."}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="flex items-center justify-end border-t border-border/50 pt-4 mt-2">
                        <Button
                          onClick={() => generateIntegrityReport(report)}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/10 w-full"
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Download Audit Report (PDF)
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}

                {filteredReports.length === 0 && (
                  <Card className="col-span-full border-dashed border-2">
                    <CardContent className="p-20 text-center">
                      <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-20" />
                      <h3 className="font-semibold text-xl mb-2">No Reports Found</h3>
                      <p className="text-muted-foreground">
                        Try searching for a different county or upload new documents for analysis.
                      </p>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-3">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Reports Generated</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-black text-emerald-600">{reports.length}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Counties Covered</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-black text-emerald-600">{new Set(reports.map((r) => r.county)).size}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Coverage Percent</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-black text-emerald-600">
                    {Math.round((new Set(reports.map((r) => r.county)).size / 47) * 100)}%
                  </div>
                </CardContent>
              </Card>
            </div>
            <BudgetChart />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
