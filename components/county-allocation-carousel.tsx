"use client"

import { COUNTY_EQUITABLE_SHARE } from "@/lib/dashboard-constants"
import { motion } from "framer-motion"

export function CountyAllocationCarousel() {
    // Duplicate the list for seamless looping
    const displayItems = [...COUNTY_EQUITABLE_SHARE, ...COUNTY_EQUITABLE_SHARE];

    return (
        <div className="w-full bg-accent/5 border-y border-border/50 backdrop-blur-sm overflow-hidden py-3">
            <div className="flex items-center px-4">
                <span className="text-[10px] font-bold uppercase tracking-widest text-accent mr-6 whitespace-nowrap">
                    FY 2025/26 County Equitable Share:
                </span>
                <div className="relative flex-1 overflow-hidden">
                    <motion.div
                        className="flex gap-12 whitespace-nowrap"
                        animate={{ x: [0, -2000] }}
                        transition={{
                            duration: 60,
                            repeat: Infinity,
                            ease: "linear"
                        }}
                    >
                        {displayItems.map((item, idx) => (
                            <div key={idx} className="flex items-center gap-2">
                                <span className="text-xs font-bold text-foreground">{item.county}</span>
                                <span className="text-xs text-muted-foreground">
                                    Ksh {(item.allocation / 1e9).toFixed(2)}B
                                </span>
                                <div className="h-1 w-1 rounded-full bg-accent/50 ml-4" />
                            </div>
                        ))}
                    </motion.div>
                </div>
            </div>
        </div>
    )
}
