import React, { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { ChevronLeft, ChevronRight, AlertCircle, HeartPulse, Building2, TrendingUp, ShieldAlert } from "lucide-react"
import { COUNTY_FACTS } from "@/lib/county-facts"

const getIconAndGradient = (health: string) => {
    switch (health?.toLowerCase()) {
        case "critical": return { icon: <AlertCircle className="h-8 w-8 text-red-500" />, gradient: "from-red-500/10 to-transparent" }
        case "warning": return { icon: <ShieldAlert className="h-8 w-8 text-amber-500" />, gradient: "from-amber-500/10 to-transparent" }
        case "leader": return { icon: <TrendingUp className="h-8 w-8 text-emerald-500" />, gradient: "from-emerald-500/10 to-transparent" }
        default: return { icon: <Building2 className="h-8 w-8 text-blue-500" />, gradient: "from-blue-500/10 to-transparent" }
    }
}

export function InsightCarousel() {
    const [slides, setSlides] = useState<any[]>([])
    const [current, setCurrent] = useState(0)

    // Randomize slides every 2 mins
    useEffect(() => {
        const refreshSlides = () => {
            const shuffled = [...COUNTY_FACTS].sort(() => 0.5 - Math.random())
            const selected = shuffled.slice(0, 5).map(c => {
                const style = getIconAndGradient(c.fiscalHealth)
                return {
                    title: `${c.name}: ${c.fiscalHealth} Status`,
                    description: c.aiInsight,
                    icon: style.icon,
                    gradient: style.gradient
                }
            })
            setSlides(selected)
            setCurrent(0)
        }

        refreshSlides()
        const interval = setInterval(refreshSlides, 120000)
        return () => clearInterval(interval)
    }, [])

    useEffect(() => {
        const timer = setInterval(() => {
            if (slides.length > 0) {
                setCurrent((prev) => (prev + 1) % slides.length)
            }
        }, 8000)
        return () => clearInterval(timer)
    }, [slides.length])

    if (slides.length === 0) return null

    const nextSlide = () => setCurrent((prev) => (prev + 1) % slides.length)
    const prevSlide = () => setCurrent((prev) => (prev - 1 + slides.length) % slides.length)

    return (
        <div className="relative max-w-5xl mx-auto px-4">
            <div className="text-center mb-12">
                <h2 className="text-4xl font-bold tracking-tight sm:text-5xl text-white mb-4">Fiscal Health Indicators</h2>
                <p className="mt-4 text-xl text-slate-400 font-light">Deep dives into the data that shapes the nation.</p>
            </div>

            <div className="relative overflow-hidden rounded-3xl border border-slate-700/50 bg-slate-900/60 backdrop-blur-xl shadow-2xl">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={current}
                        initial={{ opacity: 0, x: 100 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -100 }}
                        transition={{ duration: 0.6, ease: "easeInOut" }}
                        className={`p-10 md:p-16 bg-gradient-to-br ${slides[current].gradient} relative`}
                    >
                        <div className="flex flex-col md:flex-row items-center gap-10">
                            <div className="flex-shrink-0 p-6 bg-slate-950/80 rounded-3xl border border-slate-800 shadow-2xl backdrop-blur-sm relative group">
                                <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity" />
                                {slides[current].icon}
                            </div>
                            <div className="flex-1 space-y-6 text-center md:text-left">
                                <h3 className="text-3xl md:text-4xl font-bold text-white tracking-tight">{slides[current].title}</h3>
                                <p className="text-xl md:text-2xl text-slate-200 leading-relaxed font-light italic">
                                    "{slides[current].description}"
                                </p>
                                <div className="pt-2 flex justify-center md:justify-start">
                                    <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-white/10 text-white border border-white/20 backdrop-blur-sm">
                                        Flash Analysis 2.0
                                    </span>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </AnimatePresence>

                {/* Navigation Arrows */}
                <button
                    onClick={prevSlide}
                    className="absolute left-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-slate-900/80 border border-slate-700 text-white hover:bg-slate-800 hover:border-slate-600 transition-all backdrop-blur-sm group"
                    aria-label="Previous slide"
                >
                    <ChevronLeft className="h-6 w-6 group-hover:-translate-x-1 transition-transform" />
                </button>
                <button
                    onClick={nextSlide}
                    className="absolute right-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-slate-900/80 border border-slate-700 text-white hover:bg-slate-800 hover:border-slate-600 transition-all backdrop-blur-sm group"
                    aria-label="Next slide"
                >
                    <ChevronRight className="h-6 w-6 group-hover:translate-x-1 transition-transform" />
                </button>

                {/* Navigation Dots */}
                <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2.5">
                    {slides.map((_, i) => (
                        <button
                            key={i}
                            onClick={() => setCurrent(i)}
                            className={`h-2 rounded-full transition-all duration-300 ${current === i ? "w-10 bg-blue-500 shadow-lg shadow-blue-500/50" : "w-2 bg-slate-600 hover:bg-slate-500"
                                }`}
                            aria-label={`Go to slide ${i + 1}`}
                        />
                    ))}
                </div>
            </div>
        </div>
    )
}
