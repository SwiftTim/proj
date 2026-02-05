"use client"

import React, { useState, useEffect, useRef, useMemo } from "react"
import { geoMercator, geoPath } from "d3-geo"
import gsap from "gsap"
import { COUNTY_FACTS } from "@/lib/county-facts"
import { Loader2, ArrowLeft, TrendingUp, TriangleAlert, CheckCircle, Activity, Users, Wallet } from "lucide-react"

const GEO_URL = "https://raw.githubusercontent.com/mikelmaron/kenya-election-data/master/data/counties.geojson"

// Map Dimensions
const WIDTH = 800
const HEIGHT = 600

export function KenyaMap() {
    const [geoData, setGeoData] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [activeCounty, setActiveCounty] = useState<any | null>(null)
    const [hoveredCounty, setHoveredCounty] = useState<any | null>(null)
    const svgRef = useRef<SVGSVGElement>(null)
    const gRef = useRef<SVGGElement>(null)
    const panelRef = useRef<HTMLDivElement>(null)
    const tooltipRef = useRef<HTMLDivElement>(null)

    // Fetch GeoJSON
    useEffect(() => {
        const fetchGeo = async () => {
            try {
                const res = await fetch(GEO_URL)
                const data = await res.json()
                setGeoData(data)
            } catch (e) {
                console.error("Failed to load map data", e)
            } finally {
                setLoading(false)
            }
        }
        fetchGeo()
    }, [])

    // D3 Projection
    const { paths, projection } = useMemo(() => {
        if (!geoData) return { paths: [], projection: null }

        // Fit map to SVG dimensions
        const proj = geoMercator().fitSize([WIDTH, HEIGHT], geoData)
        const pathGenerator = geoPath().projection(proj)

        const renderedPaths = geoData.features.map((feature: any) => ({
            type: "Feature",
            id: feature.properties.COUNTY_NAM || feature.properties.COUNTY || feature.properties.name || "Unknown",
            d: pathGenerator(feature),
            feature: feature
        }))

        return { paths: renderedPaths, projection: proj }
    }, [geoData])

    // Helper to find county data
    const getCountyData = (id: string) => {
        if (!id) return null
        const fsId = id.toLowerCase().replace(" ", "-")
        return COUNTY_FACTS.find(c =>
            c.name.toLowerCase() === id.toLowerCase() ||
            c.id === fsId ||
            c.name.toLowerCase().includes(id.toLowerCase())
        )
    }

    // Mouse Event Handlers
    const handleMouseMove = (e: React.MouseEvent) => {
        if (tooltipRef.current) {
            const x = e.clientX
            const y = e.clientY
            // Offset tooltip to avoid cursor overlap
            tooltipRef.current.style.transform = `translate(${x + 20}px, ${y + 20}px)`
        }
    }

    const handleMouseEnter = (e: React.MouseEvent, countyId: string) => {
        if (!activeCounty) {
            gsap.to(e.currentTarget, { fill: "#3b82f6", duration: 0.3 })
            const data = getCountyData(countyId)
            if (data) setHoveredCounty(data)
        }
    }

    const handleMouseLeave = (e: React.MouseEvent) => {
        if (!activeCounty) {
            gsap.to(e.currentTarget, { fill: "#1e293b", duration: 0.3 })
            setHoveredCounty(null)
        }
    }

    // Handle County Click (Zoom & Drill Down)
    const handleCountyClick = (countyId: string, pathD: string, feature: any) => {
        if (!svgRef.current || activeCounty?.id === countyId || !countyId) return

        // Find facts
        // Try to fuzzy match or direct match
        const fsId = countyId.toLowerCase().replace(" ", "-")
        const facts = COUNTY_FACTS.find(c =>
            c.name.toLowerCase() === countyId.toLowerCase() ||
            c.id === fsId ||
            c.name.toLowerCase().includes(countyId.toLowerCase())
        ) || {
            id: countyId,
            name: countyId,
            pop2026: "N/A",
            fiscalHealth: "Unknown",
            budgetGap: "N/A",
            absorption: "N/A",
            aiInsight: "No AI insight available for this region."
        }

        setActiveCounty(facts)

        // Calculate Bounding Box of the Path
        // We can use d3 path generator bounds function if we have the feature
        const pathGen = geoPath().projection(projection)
        const [[x0, y0], [x1, y1]] = pathGen.bounds(feature)

        const dx = x1 - x0
        const dy = y1 - y0
        const x = (x0 + x1) / 2
        const y = (y0 + y1) / 2

        // Determine scale and translate
        const scale = Math.min(8, 0.6 / Math.max(dx / WIDTH, dy / HEIGHT))
        const translate = [WIDTH / 2 - scale * x, HEIGHT / 2 - scale * y]

        // GSAP Animation: Zoom Map
        const timeline = gsap.timeline()

        // 1. Move the Group (Zoom Effect)
        timeline.to(gRef.current, {
            attr: { transform: `translate(${translate[0]},${translate[1]}) scale(${scale})` },
            duration: 1.2,
            ease: "power3.inOut"
        })

        // 2. Fade out others
        timeline.to(`.county-path:not(#${CSS.escape(countyId)})`, {
            opacity: 0.1,
            fill: "#1e293b",
            duration: 0.8
        }, "<")

        // 3. Highlight Selected
        timeline.to(`#${CSS.escape(countyId)}`, {
            opacity: 1,
            fill: getHealthColor(facts.fiscalHealth),
            stroke: "#fff",
            strokeWidth: 1 / scale, // Keep stroke thin
            duration: 0.8
        }, "<")

        // 4. Slide in Panel
        gsap.fromTo(panelRef.current,
            { x: 100, opacity: 0 },
            { x: 0, opacity: 1, duration: 0.8, ease: "back.out(1.7)", delay: 0.2 }
        )

        // 5. Stagger Text in Panel
        gsap.fromTo(".fact-item",
            { y: 20, opacity: 0 },
            { y: 0, opacity: 1, stagger: 0.1, duration: 0.5, delay: 0.6 }
        )
    }

    // Reset to National View
    const handleReset = () => {
        if (!activeCounty) return
        setActiveCounty(null)

        const timeline = gsap.timeline()

        // 1. Reset Map Transform
        timeline.to(gRef.current, {
            attr: { transform: "translate(0,0) scale(1)" },
            duration: 1,
            ease: "power3.inOut"
        })

        // 2. Reset All Paths opacity and color
        timeline.to(".county-path", {
            opacity: 1,
            fill: "#1e293b",
            stroke: "#334155",
            strokeWidth: 0.5,
            duration: 0.8
        }, "<")

        // 3. Hide Panel
        timeline.to(panelRef.current, {
            x: 50,
            opacity: 0,
            duration: 0.5
        }, "<")
    }

    const getHealthColor = (status: string) => {
        switch (status?.toLowerCase()) {
            case "critical": return "#ef4444" // red
            case "warning": return "#f59e0b" // amber
            case "stable": return "#3b82f6" // blue
            case "leader": return "#10b981" // green
            case "improving": return "#8b5cf6" // purple
            default: return "#3b82f6"
        }
    }

    if (loading) {
        return (
            <div className="w-full h-[600px] flex items-center justify-center bg-slate-950/50 rounded-xl border border-slate-800">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                <span className="ml-3 text-slate-400">Loading geospatial data...</span>
            </div>
        )
    }

    return (
        <div
            className="relative w-full h-[600px] bg-slate-950 rounded-xl overflow-hidden border border-slate-800 shadow-2xl"
            onMouseMove={handleMouseMove} // Track mouse globally in container
        >
            {/* Floating Tooltip (Portal-like behavior via fixed position or absolute if container relative) */}
            <div
                ref={tooltipRef}
                className={`fixed top-0 left-0 z-50 pointer-events-none transition-opacity duration-200 ${hoveredCounty && !activeCounty ? 'opacity-100' : 'opacity-0'}`}
            >
                {hoveredCounty && (
                    <div className="bg-slate-900/95 backdrop-blur-md border border-slate-700 p-5 rounded-xl shadow-2xl min-w-[320px]">
                        <div className="flex justify-between items-start mb-4">
                            <h4 className="text-xl font-black text-white tracking-tight">{hoveredCounty.name}</h4>
                            <span className="px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider border"
                                style={{
                                    backgroundColor: `${getHealthColor(hoveredCounty.fiscalHealth)}10`,
                                    borderColor: `${getHealthColor(hoveredCounty.fiscalHealth)}40`,
                                    color: getHealthColor(hoveredCounty.fiscalHealth)
                                }}>
                                {hoveredCounty.fiscalHealth}
                            </span>
                        </div>

                        <div className="space-y-3">
                            {/* Key Stats Grid */}
                            <div className="grid grid-cols-2 gap-3 text-sm">
                                <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-800">
                                    <div className="flex items-center gap-1.5 mb-1">
                                        <Users className="h-3 w-3 text-slate-500" />
                                        <p className="text-[10px] text-slate-500 uppercase font-bold">Pop. 2026</p>
                                    </div>
                                    <p className="font-mono font-bold text-slate-200">{hoveredCounty.pop2026}</p>
                                </div>
                                <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-800">
                                    <div className="flex items-center gap-1.5 mb-1">
                                        <TrendingUp className="h-3 w-3 text-emerald-500" />
                                        <p className="text-[10px] text-slate-500 uppercase font-bold">Absorption</p>
                                    </div>
                                    <p className="font-mono font-bold text-emerald-400 text-xs">{hoveredCounty.absorption}</p>
                                </div>
                            </div>

                            {/* Budget Gap */}
                            <div className="bg-slate-950/50 p-3 rounded-lg border border-slate-800 text-sm">
                                <div className="flex items-center gap-1.5 mb-1">
                                    <Wallet className="h-3 w-3 text-amber-500" />
                                    <p className="text-[10px] text-slate-500 uppercase font-bold">Fiscal Gap / Warning</p>
                                </div>
                                <p className="font-medium text-amber-200/90 text-xs">{hoveredCounty.budgetGap}</p>
                            </div>

                            {/* AI Insight */}
                            <div className="relative pl-3 pt-1">
                                <div className="absolute left-0 top-1.5 bottom-1.5 w-0.5 bg-blue-500 rounded-full"></div>
                                <p className="text-xs text-blue-200 italic leading-relaxed">
                                    <span className="font-bold text-blue-400 not-italic mr-1">AI Insight:</span>
                                    {hoveredCounty.aiInsight}
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Reset Button (Only visible when zoomed) */}
            {activeCounty && (
                <button
                    onClick={handleReset}
                    className="absolute top-6 left-6 z-20 flex items-center gap-2 bg-slate-900/80 hover:bg-slate-800 text-white px-4 py-2 rounded-full backdrop-blur-md border border-slate-700 transition-all shadow-lg group"
                >
                    <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
                    Back to National View
                </button>
            )}

            {/* SVG Map */}
            <svg
                ref={svgRef}
                viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
                className="w-full h-full cursor-pointer bg-[#020617]"
                onClick={(e) => {
                    if (e.target === svgRef.current) handleReset()
                }}
            >
                <defs>
                    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="3" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                </defs>

                <g ref={gRef} className="transition-transform will-change-transform">
                    {paths.map((p: any) => (
                        <path
                            key={p.id}
                            id={p.id}
                            d={p.d}
                            className="county-path transition-colors duration-300"
                            fill="#1e293b" // Slate-800
                            stroke="#334155" // Slate-700
                            strokeWidth="0.5"
                            vectorEffect="non-scaling-stroke" // Keep stroke consistent? Actually handled by GSAP zoom better manually or logic
                            onMouseEnter={(e) => handleMouseEnter(e, p.id)}
                            onMouseLeave={handleMouseLeave}
                            onClick={(e) => {
                                e.stopPropagation()
                                handleCountyClick(p.id, p.d, p.feature)
                            }}
                            style={{ outline: "none" }} // Prevent focus outline
                        >
                            <title>{p.id}</title>
                        </path>
                    ))}
                </g>
            </svg>

            {/* Facts Panel Overlay */}
            <div
                ref={panelRef}
                className="absolute top-0 right-0 h-full w-full md:w-[400px] bg-slate-900/95 backdrop-blur-xl border-l border-slate-800 p-8 shadow-2xl transform translate-x-full opacity-0 pointer-events-none md:pointer-events-auto"
                style={{ pointerEvents: activeCounty ? 'auto' : 'none' }}
            >
                {activeCounty && (
                    <div className="h-full flex flex-col">
                        {/* Header */}
                        <div className="fact-item mb-8">
                            <div className="flex items-center justify-between mb-2">
                                <h2 className="text-4xl font-black text-white tracking-tight">{activeCounty.name}</h2>
                                <Activity className={`h-8 w-8`} style={{ color: getHealthColor(activeCounty.fiscalHealth) }} />
                            </div>
                            <div
                                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-bold uppercase tracking-wider bg-opacity-20 border border-opacity-30"
                                style={{
                                    backgroundColor: `${getHealthColor(activeCounty.fiscalHealth)}20`,
                                    borderColor: getHealthColor(activeCounty.fiscalHealth),
                                    color: getHealthColor(activeCounty.fiscalHealth)
                                }}
                            >
                                {activeCounty.fiscalHealth} Fiscal Status
                            </div>
                        </div>

                        {/* Facts Grid */}
                        <div className="space-y-6 flex-1 overflow-y-auto pr-2 custom-scrollbar">
                            {/* Population */}
                            <div className="fact-item bg-slate-950/50 p-4 rounded-xl border border-slate-800/50">
                                <div className="flex items-center gap-3 mb-2 text-slate-400 text-sm font-medium uppercase tracking-wide">
                                    <Users className="h-4 w-4 text-blue-500" /> Projected Population (2026)
                                </div>
                                <div className="text-2xl font-bold text-white">{activeCounty.pop2026}</div>
                            </div>

                            {/* Budget Gap */}
                            <div className="fact-item bg-slate-950/50 p-4 rounded-xl border border-slate-800/50">
                                <div className="flex items-center gap-3 mb-2 text-slate-400 text-sm font-medium uppercase tracking-wide">
                                    <Wallet className="h-4 w-4 text-amber-500" /> Budget Gap / Variance
                                </div>
                                <div className="text-xl font-bold text-amber-200">{activeCounty.budgetGap}</div>
                            </div>

                            {/* Absorption */}
                            <div className="fact-item bg-slate-950/50 p-4 rounded-xl border border-slate-800/50">
                                <div className="flex items-center gap-3 mb-2 text-slate-400 text-sm font-medium uppercase tracking-wide">
                                    <TrendingUp className="h-4 w-4 text-emerald-500" /> Absorption Rate
                                </div>
                                <div className="text-xl font-bold text-emerald-200">{activeCounty.absorption}</div>
                            </div>

                            {/* AI Insight */}
                            <div className="fact-item bg-gradient-to-br from-blue-900/20 to-purple-900/20 p-5 rounded-xl border border-blue-500/30 relative overflow-hidden">
                                <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
                                <div className="flex items-center gap-2 mb-3 text-blue-400 text-xs font-bold uppercase">
                                    <span className="animate-pulse">●</span> BudgetAI Insight
                                </div>
                                <p className="text-lg text-blue-100/90 leading-relaxed italic">
                                    "{activeCounty.aiInsight}"
                                </p>
                            </div>
                        </div>

                        <div className="fact-item mt-6 pt-6 border-t border-slate-800">
                            <button className="w-full py-4 bg-white text-slate-950 font-bold rounded-lg hover:bg-blue-50 transition-colors flex items-center justify-center gap-2 group">
                                View Full Report
                                <ArrowSheetRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* Map Overlay Text (Title) */}
            {!activeCounty && (
                <div className="absolute top-6 left-6 pointer-events-none">
                    <h3 className="text-2xl font-bold text-white/50">Explore Counties</h3>
                    <p className="text-sm text-slate-500">Click on a region to view fiscal health</p>
                </div>
            )}
        </div>
    )
}

function ArrowSheetRight(props: any) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
            <line x1="15" x2="15" y1="3" y2="21" />
            <path d="m15 15 2-2-2-2" />
        </svg>
    )
}
