"use client"

import { useState, useEffect, Suspense } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Upload,
  FileText,
  BarChart3,
  Users,
  TrendingUp,
  Search,
  Filter,
  LogOut,
  ArrowLeft,
  Settings,
  FileBarChart,
} from "lucide-react"
import { DashboardStats } from "@/components/dashboard-stats"
import { BudgetChart } from "@/components/budget-chart"
import { DocumentList } from "@/components/document-list"
import { UploadModule } from "@/components/upload-module"
import { AnalysisScorecard } from "/home/tim/Downloads/v0-ai-budget-transparency-main (2)/components/analysis-module"
import { AuthModal } from "@/components/auth-modal"
import { ErrorBoundary } from "@/components/error-boundary"
import { DashboardSkeleton, DocumentListSkeleton } from "@/components/loading-skeleton"
import Link from "next/link"

interface User {
  name: string
  email: string
  role: string
}

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("dashboard")
  const [searchQuery, setSearchQuery] = useState("")
  const [user, setUser] = useState<User | null>(null)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const initializeDashboard = async () => {
      // Simulate loading time
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Check for existing auth
      const savedUser = localStorage.getItem("auth_user")
      if (savedUser) {
        setUser(JSON.parse(savedUser))
      }

      setIsLoading(false)
    }

    initializeDashboard()
  }, [])

  const handleSignOut = () => {
    localStorage.removeItem("auth_user")
    setUser(null)
  }

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case "researcher":
        return "bg-chart-1/10 text-chart-1 border-chart-1/20"
      case "journalist":
        return "bg-chart-2/10 text-chart-2 border-chart-2/20"
      case "government":
        return "bg-chart-3/10 text-chart-3 border-chart-3/20"
      default:
        return "bg-chart-4/10 text-chart-4 border-chart-4/20"
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        {/* Header skeleton */}
        <header className="border-b border-border bg-card">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="h-8 w-8 bg-accent rounded" />
                <div>
                  <div className="h-6 w-48 bg-muted rounded mb-1" />
                  <div className="h-4 w-64 bg-muted rounded" />
                </div>
              </div>
              <div className="h-8 w-24 bg-muted rounded" />
            </div>
          </div>
        </header>

        {/* Content skeleton */}
        <main className="container mx-auto px-4 py-8">
          <DashboardSkeleton />
        </main>
      </div>
    )
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b border-border bg-card">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/">
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to Home
                  </Link>
                </Button>
                <div className="flex items-center space-x-2">
                  <BarChart3 className="h-8 w-8 text-accent" />
                  <div>
                    <h1 className="text-2xl font-bold text-foreground">BudgetAI Dashboard</h1>
                    <p className="text-sm text-muted-foreground">Kenya County Budget Analysis Platform</p>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                {user ? (
                  <div className="flex items-center space-x-3">
                    <div className="text-right">
                      <p className="text-sm font-medium">{user.name}</p>
                      <Badge className={getRoleBadgeColor(user.role)} variant="secondary">
                        {user.role}
                      </Badge>
                    </div>
                    <Button variant="ghost" size="sm" asChild>
                      <Link href="/reports">
                        <FileBarChart className="h-4 w-4 mr-2" />
                        Reports
                      </Link>
                    </Button>
                    <Button variant="ghost" size="sm" asChild>
                      <Link href="/settings">
                        <Settings className="h-4 w-4 mr-2" />
                        Settings
                      </Link>
                    </Button>
                    <Button variant="outline" size="sm" onClick={handleSignOut}>
                      <LogOut className="h-4 w-4 mr-2" />
                      Sign Out
                    </Button>
                  </div>
                ) : (
                  <Button variant="outline" size="sm" onClick={() => setShowAuthModal(true)}>
                    <Users className="h-4 w-4 mr-2" />
                    Sign In
                  </Button>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-4 lg:w-[600px]">
              <TabsTrigger value="dashboard" className="flex items-center space-x-2">
                <BarChart3 className="h-4 w-4" />
                <span>Dashboard</span>
              </TabsTrigger>
              <TabsTrigger value="upload" className="flex items-center space-x-2" disabled={!user}>
                <Upload className="h-4 w-4" />
                <span>Upload</span>
              </TabsTrigger>
              <TabsTrigger value="documents" className="flex items-center space-x-2">
                <FileText className="h-4 w-4" />
                <span>Documents</span>
              </TabsTrigger>
              <TabsTrigger value="analysis" className="flex items-center space-x-2" disabled={!user}>
                <TrendingUp className="h-4 w-4" />
                <span>Analysis</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="dashboard" className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-bold text-foreground">Budget Overview</h2>
                  <p className="text-muted-foreground">AI-powered insights from county budget documents</p>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search counties, years..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10 w-64"
                    />
                  </div>
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                  </Button>
                </div>
              </div>

              <Suspense fallback={<DashboardSkeleton />}>
                <DashboardStats />
                <BudgetChart />
              </Suspense>
            </TabsContent>

            <TabsContent value="upload" className="space-y-6">
              {user ? (
                <>
                  <div>
                    <h2 className="text-3xl font-bold text-foreground">Upload Budget Documents</h2>
                    <p className="text-muted-foreground">
                      Upload PDF budget documents for AI analysis and summarization
                    </p>
                  </div>
                  <ErrorBoundary>
                    <UploadModule />
                  </ErrorBoundary>
                </>
              ) : (
                <Card>
                  <CardHeader>
                    <CardTitle>Authentication Required</CardTitle>
                    <CardDescription>Please sign in to upload documents</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button onClick={() => setShowAuthModal(true)}>
                      <Users className="h-4 w-4 mr-2" />
                      Sign In to Upload
                    </Button>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="documents" className="space-y-6">
              <div>
                <h2 className="text-3xl font-bold text-foreground">Document Library</h2>
                <p className="text-muted-foreground">Browse and analyze uploaded budget documents</p>
              </div>
              <Suspense fallback={<DocumentListSkeleton />}>
                <ErrorBoundary>
                  <DocumentList />
                </ErrorBoundary>
              </Suspense>
            </TabsContent>

            <TabsContent value="analysis" className="space-y-6">
  {user ? (
    <>
      <div>
        <h2 className="text-3xl font-bold text-foreground">AI Analysis</h2>
        <p className="text-muted-foreground">
          Advanced insights and trends from budget data
        </p>
      </div>

      {/* ✅ Replace the old placeholder with your new module */}
      <ErrorBoundary>
        <AnalysisScorecard />
      </ErrorBoundary>
    </>
  ) : (
    <Card>
      <CardHeader>
        <CardTitle>Authentication Required</CardTitle>
        <CardDescription>
          Please sign in to access advanced analysis features
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Button onClick={() => setShowAuthModal(true)}>
          <Users className="h-4 w-4 mr-2" />
          Sign In for Analysis
        </Button>
      </CardContent>
    </Card>
  )}
</TabsContent>

          </Tabs>
        </main>

        <AuthModal open={showAuthModal} onOpenChange={setShowAuthModal} onAuthSuccess={setUser} />
      </div>
    </ErrorBoundary>
  )
}
