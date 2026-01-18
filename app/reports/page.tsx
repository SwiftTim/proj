"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BarChart3, ArrowLeft, Download, FileText, TrendingUp, AlertTriangle, Calendar, Search } from "lucide-react"
import { BudgetChart } from "@/components/budget-chart"
import Link from "next/link"

interface Report {
  id: string
  title: string
  county: string
  year: string
  type: "transparency" | "budget" | "comparative"
  status: "completed" | "processing" | "failed"
  createdAt: string
  size: string
}

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([])
  const [filteredReports, setFilteredReports] = useState<Report[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [filterType, setFilterType] = useState("all")
  const [filterStatus, setFilterStatus] = useState("all")

  useEffect(() => {
    // Mock reports data
    const mockReports: Report[] = [
      {
        id: "1",
        title: "Nairobi County Budget Transparency Report 2024",
        county: "Nairobi",
        year: "2024",
        type: "transparency",
        status: "completed",
        createdAt: "2025-01-15",
        size: "2.4 MB",
      },
      {
        id: "2",
        title: "Mombasa County Budget Analysis 2024",
        county: "Mombasa",
        year: "2024",
        type: "budget",
        status: "completed",
        createdAt: "2025-01-14",
        size: "1.8 MB",
      },
      {
        id: "3",
        title: "Comparative Analysis: Top 5 Counties 2024",
        county: "Multiple",
        year: "2024",
        type: "comparative",
        status: "processing",
        createdAt: "2025-01-13",
        size: "3.2 MB",
      },
      {
        id: "4",
        title: "Kisumu County Transparency Score 2023",
        county: "Kisumu",
        year: "2023",
        type: "transparency",
        status: "completed",
        createdAt: "2025-01-12",
        size: "1.5 MB",
      },
    ]

    setReports(mockReports)
    setFilteredReports(mockReports)
  }, [])

  useEffect(() => {
    let filtered = reports

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (report) =>
          report.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          report.county.toLowerCase().includes(searchQuery.toLowerCase()),
      )
    }

    // Apply type filter
    if (filterType !== "all") {
      filtered = filtered.filter((report) => report.type === filterType)
    }

    // Apply status filter
    if (filterStatus !== "all") {
      filtered = filtered.filter((report) => report.status === filterStatus)
    }

    setFilteredReports(filtered)
  }, [reports, searchQuery, filterType, filterStatus])

  const getStatusBadge = (status: Report["status"]) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-chart-2/10 text-chart-2 border-chart-2/20">Completed</Badge>
      case "processing":
        return <Badge className="bg-chart-3/10 text-chart-3 border-chart-3/20">Processing</Badge>
      case "failed":
        return <Badge variant="destructive">Failed</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  const getTypeIcon = (type: Report["type"]) => {
    switch (type) {
      case "transparency":
        return <AlertTriangle className="h-4 w-4" />
      case "budget":
        return <BarChart3 className="h-4 w-4" />
      case "comparative":
        return <TrendingUp className="h-4 w-4" />
      default:
        return <FileText className="h-4 w-4" />
    }
  }

  const generateNewReport = () => {
    // Mock report generation
    const newReport: Report = {
      id: Date.now().toString(),
      title: "New Budget Analysis Report",
      county: "Nakuru",
      year: "2024",
      type: "budget",
      status: "processing",
      createdAt: new Date().toISOString().split("T")[0],
      size: "0 MB",
    }

    setReports((prev) => [newReport, ...prev])
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
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
                <FileText className="h-8 w-8 text-accent" />
                <span className="text-xl font-bold">Reports</span>
              </div>
            </div>
            <Button onClick={generateNewReport}>
              <FileText className="h-4 w-4 mr-2" />
              Generate Report
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Reports & Analytics</h1>
          <p className="text-muted-foreground">Generate and download detailed budget analysis reports</p>
        </div>

        <Tabs defaultValue="reports" className="space-y-6">
          <TabsList>
            <TabsTrigger value="reports">My Reports</TabsTrigger>
            <TabsTrigger value="analytics">Analytics Dashboard</TabsTrigger>
          </TabsList>

          <TabsContent value="reports" className="space-y-6">
            {/* Filters */}
            <Card>
              <CardHeader>
                <CardTitle>Filter Reports</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search reports..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  <Select value={filterType} onValueChange={setFilterType}>
                    <SelectTrigger className="w-full md:w-48">
                      <SelectValue placeholder="Report Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      <SelectItem value="transparency">Transparency</SelectItem>
                      <SelectItem value="budget">Budget Analysis</SelectItem>
                      <SelectItem value="comparative">Comparative</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={filterStatus} onValueChange={setFilterStatus}>
                    <SelectTrigger className="w-full md:w-48">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="processing">Processing</SelectItem>
                      <SelectItem value="failed">Failed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Reports List */}
            <div className="space-y-4">
              {filteredReports.map((report) => (
                <Card key={report.id}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="p-2 bg-accent/10 rounded-lg">{getTypeIcon(report.type)}</div>
                        <div>
                          <h3 className="font-semibold">{report.title}</h3>
                          <div className="flex items-center space-x-4 mt-1 text-sm text-muted-foreground">
                            <span>{report.county}</span>
                            <span>•</span>
                            <span>{report.year}</span>
                            <span>•</span>
                            <span className="flex items-center">
                              <Calendar className="h-3 w-3 mr-1" />
                              {report.createdAt}
                            </span>
                            <span>•</span>
                            <span>{report.size}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        {getStatusBadge(report.status)}
                        {report.status === "completed" && (
                          <Button variant="outline" size="sm">
                            <Download className="h-4 w-4 mr-2" />
                            Download
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {filteredReports.length === 0 && (
                <Card>
                  <CardContent className="p-12 text-center">
                    <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="font-semibold mb-2">No reports found</h3>
                    <p className="text-muted-foreground mb-4">
                      {searchQuery || filterType !== "all" || filterStatus !== "all"
                        ? "Try adjusting your filters"
                        : "Generate your first report to get started"}
                    </p>
                    <Button onClick={generateNewReport}>
                      <FileText className="h-4 w-4 mr-2" />
                      Generate Report
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-3">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Total Reports</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-accent">{reports.length}</div>
                  <p className="text-sm text-muted-foreground">Generated this month</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Counties Analyzed</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-accent">{new Set(reports.map((r) => r.county)).size}</div>
                  <p className="text-sm text-muted-foreground">Unique counties covered</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Avg. Transparency Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-accent">7.2</div>
                  <p className="text-sm text-muted-foreground">Out of 10</p>
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
