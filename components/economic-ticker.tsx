"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"

export function EconomicTicker({ headlines = [] }: { headlines?: string[] }) {
    const [currentIndex, setCurrentIndex] = useState(0)
    const [currentTime, setCurrentTime] = useState("")

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date().toLocaleString('en-KE', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                timeZoneName: 'short'
            }))
        }, 1000)

        const headlineTimer = setInterval(() => {
            if (headlines.length > 0) {
                setCurrentIndex((prev) => (prev + 1) % headlines.length)
            }
        }, 5000)

        return () => {
            clearInterval(timer)
            clearInterval(headlineTimer)
        }
    }, [headlines])

    const defaultHeadlines = [
        "Analyzing latest CBIRR reports...",
        "BudgetAI 2.0 Live - Transforming chaotic data into insights",
        "Real-time monitoring of 47 county budgets active"
    ]

    const displayHeadlines = headlines.length > 0 ? headlines : defaultHeadlines;

    return (
        <div className="fixed bottom-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-t border-border/50 h-12 flex items-center px-6 overflow-hidden">
            <div className="flex items-center gap-4 w-full justify-between">
                <div className="flex items-center gap-4 flex-1">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-accent bg-accent/10 px-2 py-1 rounded">
                        Todays:
                    </span>
                    <div className="relative h-6 flex-1 overflow-hidden">
                        <AnimatePresence mode="wait">
                            <motion.p
                                key={currentIndex}
                                initial={{ y: 20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                exit={{ y: -20, opacity: 0 }}
                                className="text-sm font-medium text-foreground absolute inset-0 flex items-center"
                            >
                                {displayHeadlines[currentIndex]}
                            </motion.p>
                        </AnimatePresence>
                    </div>
                </div>
                <div className="text-[10px] font-mono text-muted-foreground whitespace-nowrap hidden md:block">
                    {currentTime}
                </div>
            </div>
        </div>
    )
}
