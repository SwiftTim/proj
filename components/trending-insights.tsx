"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell,
    LineChart,
    Line,
} from "recharts"
import { TrendingUp, Activity, AlertTriangle, RefreshCw, ChevronRight, BarChart3 } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

interface TrendingMerit {
    id: number
    date: string
    topic_name: string
    description: string
    keywords: string[]
    priority_score: number
    data_fields?: any[]
}

interface MeritData {
    merit_id: number
    topic_name: string
    chart_type: string
    data: {
        labels: string[]
        datasets: {
            label: string
            data: number[]
            backgroundColor: string
            borderColor: string
        }[]
    }
}

export function TrendingInsights() {
    const [merits, setMerits] = useState<TrendingMerit[]>([])
    const [selectedMerit, setSelectedMerit] = useState<TrendingMerit | null>(null)
    const [meritData, setMeritData] = useState<MeritData | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [isDataLoading, setIsDataLoading] = useState(false)
    const [isRefreshing, setIsRefreshing] = useState(false)

    const fetchMerits = async () => {
        try {
            setIsLoading(true)
            const response = await fetch("/api/trending-merits")
            const data = await response.json()
            if (data.success && data.merits.length > 0) {
                setMerits(data.merits)
                setSelectedMerit(data.merits[0])
            }
        } catch (error) {
            console.error("Error fetching merits:", error)
        } finally {
            setIsLoading(false)
        }
    }

    const fetchMeritData = async (meritId: number) => {
        try {
            setIsDataLoading(true)
            const response = await fetch(`/api/trending-merits/${meritId}/data`)
            const data = await response.json()
            if (data.success) {
                setMeritData(data.data)
            }
        } catch (error) {
            console.error("Error fetching merit data:", error)
        } finally {
            setIsDataLoading(false)
        }
    }

    const refreshHotTakes = async () => {
        try {
            setIsRefreshing(true)
            const response = await fetch("/api/trending-merits/trigger", {
                method: "POST"
            })
            const data = await response.json()
            if (data.success) {
                await fetchMerits()
            }
        } catch (error) {
            console.error("Error refreshing hot takes:", error)
        } finally {
            setIsRefreshing(false)
        }
    }

    useEffect(() => {
        fetchMerits()
    }, [])

    useEffect(() => {
        if (selectedMerit) {
            fetchMeritData(selectedMerit.id)
        }
    }, [selectedMerit])

    const formatDataForRecharts = () => {
        if (!meritData) return []
        return meritData.data.labels.map((label, index) => ({
            name: label,
            value: meritData.data.datasets[0].data[index],
        }))
    }

    const getPriorityColor = (score: number) => {
        if (score >= 8) return "bg-red-500/10 text-red-500 border-red-500/20"
        if (score >= 5) return "bg-amber-500/10 text-amber-500 border-amber-500/20"
        return "bg-green-500/10 text-green-500 border-green-500/20"
    }

    if (isLoading) {
        return (
            <div className="grid gap-6 lg:grid-cols-3">
                <Skeleton className="h-[400px] lg:col-span-1 rounded-xl" />
                <Skeleton className="h-[400px] lg:col-span-2 rounded-xl" />
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-xl font-semibold flex items-center gap-2">
                        <Activity className="h-5 w-5 text-accent" />
                        Daily Fiscal "Hot Takes"
                    </h3>
                    <p className="text-sm text-muted-foreground">
                        AI-driven identification of trending budget implementation issues
                    </p>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={refreshHotTakes}
                    disabled={isRefreshing}
                    className="bg-accent/5 hover:bg-accent/10 transition-all border-accent/20"
                >
                    <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`} />
                    {isRefreshing ? "Analyzing..." : "Deep Search"}
                </Button>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Hot Take List */}
                <div className="space-y-4">
                    <AnimatePresence mode="popLayout">
                        {merits.map((merit) => (
                            <motion.div
                                key={merit.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                                whileHover={{ scale: 1.02 }}
                                onClick={() => setSelectedMerit(merit)}
                                className={`cursor-pointer p-4 rounded-xl border transition-all ${selectedMerit?.id === merit.id
                                    ? "bg-accent/10 border-accent/50 shadow-lg shadow-accent/5 ring-1 ring-accent/20"
                                    : "bg-card hover:bg-accent/5 border-border shadow-sm"
                                    }`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <Badge className={getPriorityColor(merit.priority_score)}>
                                        Priority {merit.priority_score}/10
                                    </Badge>
                                    <span className="text-[10px] text-muted-foreground font-mono">
                                        {new Date(merit.date).toLocaleDateString()}
                                    </span>
                                </div>
                                <h4 className="font-bold text-sm mb-1 line-clamp-1">{merit.topic_name}</h4>
                                <p className="text-xs text-muted-foreground line-clamp-2 mb-3">
                                    {merit.description}
                                </p>
                                <div className="flex flex-wrap gap-1">
                                    {merit.keywords.slice(0, 3).map((kw, i) => (
                                        <Badge key={i} variant="outline" className="text-[10px] py-0 px-1 border-muted-foreground/20">
                                            #{kw}
                                        </Badge>
                                    ))}
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {merits.length === 0 && (
                        <Card className="bg-muted/30 border-dashed border-2">
                            <CardContent className="flex flex-col items-center justify-center py-10 text-center">
                                <AlertTriangle className="h-10 w-10 text-muted-foreground mb-4" />
                                <p className="text-sm font-medium text-muted-foreground">No hot takes found.</p>
                                <Button variant="link" onClick={refreshHotTakes} className="text-accent underline">
                                    Trigger Analysis
                                </Button>
                            </CardContent>
                        </Card>
                    )}
                </div>

                {/* Visualization Area */}
                <Card className="lg:col-span-2 overflow-hidden border-border/50 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm">
                    <CardHeader className="pb-2 border-b border-border/10">
                        <div className="flex justify-between items-start">
                            <div>
                                <CardTitle className="text-lg flex items-center gap-2">
                                    <BarChart3 className="h-5 w-5 text-accent" />
                                    {selectedMerit?.topic_name || "Select a Hot Take"}
                                </CardTitle>
                                <CardDescription className="max-w-xl">
                                    {selectedMerit?.description}
                                </CardDescription>
                            </div>
                            {selectedMerit && (
                                <div className="text-right">
                                    <Badge variant="outline" className="bg-accent/5 text-accent border-accent/20">
                                        <TrendingUp className="h-3 w-3 mr-1" />
                                        Hot Insight
                                    </Badge>
                                </div>
                            )}
                        </div>
                    </CardHeader>
                    <CardContent className="pt-6">
                        {isDataLoading ? (
                            <div className="h-[300px] flex items-center justify-center">
                                <div className="flex flex-col items-center gap-2">
                                    <RefreshCw className="h-8 w-8 text-accent animate-spin" />
                                    <p className="text-sm text-muted-foreground">Mapping budget data...</p>
                                </div>
                            </div>
                        ) : meritData ? (
                            <div className="space-y-6">
                                <div className="h-[300px] w-100%">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={formatDataForRecharts()}>
                                            <defs>
                                                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="0%" stopColor="hsl(var(--accent))" stopOpacity={0.8} />
                                                    <stop offset="100%" stopColor="hsl(var(--accent))" stopOpacity={0.1} />
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-muted/30" />
                                            <XAxis
                                                dataKey="name"
                                                axisLine={false}
                                                tickLine={false}
                                                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                                                dy={10}
                                            />
                                            <YAxis
                                                axisLine={false}
                                                tickLine={false}
                                                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                                            />
                                            <Tooltip
                                                cursor={{ fill: "hsl(var(--accent))", opacity: 0.05 }}
                                                contentStyle={{
                                                    backgroundColor: "rgba(10, 10, 10, 0.8)",
                                                    backdropFilter: "blur(4px)",
                                                    border: "1px solid hsl(var(--border))",
                                                    borderRadius: "12px",
                                                    boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                                                }}
                                                itemStyle={{ color: "hsl(var(--accent))" }}
                                            />
                                            <Bar
                                                dataKey="value"
                                                radius={[6, 6, 0, 0]}
                                                fill="url(#barGradient)"
                                                stroke="hsl(var(--accent))"
                                                strokeWidth={1}
                                                animationBegin={0}
                                                animationDuration={1500}
                                                animationEasing="ease-out"
                                            />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>

                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    {selectedMerit?.data_fields?.map((field: any, idx) => (
                                        <div key={idx} className="bg-accent/5 p-3 rounded-lg border border-accent/10">
                                            <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider mb-1">Mapped Merit</p>
                                            <p className="text-xs font-medium text-foreground">{field.field_name}</p>
                                            <Badge variant="outline" className="mt-2 text-[9px] py-0 h-4 border-accent/30 text-accent">
                                                {Math.round(field.confidence * 100)}% Match
                                            </Badge>
                                        </div>
                                    ))}
                                    <div className="bg-muted/30 p-3 rounded-lg border border-border md:col-span-2">
                                        <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider mb-1">Source Context</p>
                                        <p className="text-xs text-muted-foreground italic">
                                            "Mapped using AI keywords to identify pertinent financial datasets in CBIRR reports."
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="h-[300px] flex items-center justify-center text-center">
                                <div className="max-w-xs">
                                    <BarChart3 className="h-12 w-12 text-muted-foreground/30 mx-auto mb-4" />
                                    <p className="text-muted-foreground">Select a hot take on the left to visualize its impact across counties.</p>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
