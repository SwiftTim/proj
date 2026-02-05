"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { BarChart3, ArrowRight, Globe, Shield, Zap } from "lucide-react"
import Link from "next/link"
import { KenyaMap } from "@/components/landing-page/kenya-map"
import { LiveTicker } from "@/components/landing-page/live-ticker"
import { InsightCarousel } from "@/components/landing-page/insight-carousel"
import { CountySpotlight } from "@/components/landing-page/county-cards"
import { WhyItMatters } from "@/components/landing-page/why-it-matters"

export default function LandingPage() {
  const [isVisible, setIsVisible] = useState(false)
  const scrollSpeed = useRef(0)
  const animationFrameId = useRef<number | null>(null)

  useEffect(() => {
    setIsVisible(true)

    const handleMouseMove = (e: MouseEvent) => {
      const h = window.innerHeight
      const y = e.clientY
      const zone = h * 0.15 // 15% trigger zone

      if (y < zone) {
        // Top zone: speed proportional to closeness to top
        scrollSpeed.current = -1 * (1 - y / zone) * 15
      } else if (y > h - zone) {
        // Bottom zone: speed proportional to closeness to bottom
        scrollSpeed.current = (1 - (h - y) / zone) * 15
      } else {
        scrollSpeed.current = 0
      }
    }

    const scrollLoop = () => {
      if (Math.abs(scrollSpeed.current) > 0.1) {
        window.scrollBy({ top: scrollSpeed.current, behavior: "auto" as any }) // using auto for instant updates in loop
      }
      animationFrameId.current = requestAnimationFrame(scrollLoop)
    }

    window.addEventListener("mousemove", handleMouseMove)
    animationFrameId.current = requestAnimationFrame(scrollLoop)

    return () => {
      window.removeEventListener("mousemove", handleMouseMove)
      if (animationFrameId.current) cancelAnimationFrame(animationFrameId.current)
    }
  }, [])

  return (
    <div className="min-h-screen bg-[#020617] text-slate-50 font-sans selection:bg-blue-500/30">
      {/* Navigation */}
      <nav className="border-b border-slate-800/50 bg-slate-950/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold tracking-tight">BudgetAI <span className="text-blue-500">2.0</span></span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <Link href="#impact" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">
                Impact
              </Link>
              <Link href="#data" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">
                Data
              </Link>
              <Link href="#why" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">
                Why BudgetAI
              </Link>
              <div className="h-4 w-[1px] bg-slate-800" />
              <Button variant="ghost" size="sm" className="text-slate-300" asChild>
                <Link href="/dashboard">Sign In</Link>
              </Button>
              <Button size="sm" className="bg-blue-600 hover:bg-blue-500 text-white border-none shadow-lg shadow-blue-900/20" asChild>
                <Link href="/dashboard">Get Started</Link>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-20 pb-0 overflow-hidden">
        {/* Background Decorative Elements */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[800px] bg-gradient-to-b from-blue-600/10 via-transparent to-transparent pointer-events-none -z-10" />
        <div className="absolute top-40 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-[120px] pointer-events-none -z-10" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-[120px] pointer-events-none -z-10" />

        <div className="container mx-auto px-6">
          <div className="text-center max-w-5xl mx-auto mb-20">
            <div
              className={`transition-all duration-1000 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
            >
              <Badge variant="outline" className="mb-8 px-5 py-2 border-blue-500/30 text-blue-400 bg-blue-500/5 backdrop-blur-sm text-sm font-semibold">
                <Globe className="h-4 w-4 mr-2" />
                Empowering 47 Counties for Fiscal Accountability
              </Badge>
              <h1 className="text-6xl md:text-8xl font-extrabold mb-10 tracking-tighter leading-[1.05]">
                The Pulse of the <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-emerald-400 animate-gradient">Nation</span>
              </h1>
              <p className="text-2xl md:text-3xl text-slate-300 mb-12 max-w-3xl mx-auto font-light leading-relaxed">
                Using AI to transform chaotic PDF reports into a <span className="text-white font-semibold">real-time map</span> of Kenya's public spending.
              </p>
              <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-24">
                <Button size="xl" className="h-16 px-12 text-xl bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white group shadow-2xl shadow-blue-900/40 hover:shadow-blue-900/60 transition-all duration-300 border-0" asChild>
                  <Link href="/subscribe">
                    Explore the Platform
                    <ArrowRight className="ml-3 h-6 w-6 transition-transform group-hover:translate-x-2" />
                  </Link>
                </Button>
                <Button variant="outline" size="xl" className="h-16 px-12 text-xl border-slate-600 bg-slate-900/70 hover:bg-slate-800/90 text-white backdrop-blur-md hover:border-slate-500 transition-all duration-300">
                  Watch the Impact
                </Button>
              </div>
            </div>
          </div>

          {/* Interactive Map Section */}
          <div className={`transition-all duration-1000 delay-300 ${isVisible ? "opacity-100 scale-100" : "opacity-0 scale-95"}`}>
            <KenyaMap />
          </div>
        </div>

        {/* Live Ticker */}
        <div className="mt-20">
          <LiveTicker />
        </div>
      </section>

      {/* Insight Carousel Section */}
      <section id="impact" className="py-32 relative">
        <div className="absolute top-1/2 left-0 w-full h-[500px] bg-blue-600/5 -skew-y-3 -z-10" />
        <InsightCarousel />
      </section>

      {/* County Spotlight Section */}
      <section id="data" className="py-24 bg-slate-950/20">
        <CountySpotlight />
      </section>

      {/* Why It Matters / Trade-off Section */}
      <section id="why" className="py-24 border-t border-slate-900">
        <WhyItMatters />
      </section>

      {/* CTA Section */}
      <section className="py-32 relative overflow-hidden">
        <div className="absolute inset-0 bg-blue-600 -z-20" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-500 to-blue-700 -z-10" />
        <div className="absolute top-0 left-0 w-full h-full bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-10 -z-5" />

        <div className="container mx-auto px-6 text-center">
          <h2 className="text-4xl md:text-6xl font-black mb-8 text-white tracking-tight">
            Ready to track the <br className="hidden md:block" /> transparency revolution?
          </h2>
          <p className="text-xl text-blue-100 mb-12 max-w-2xl mx-auto font-light leading-relaxed">
            Join the movement towards data-driven governance. Get instant access to county budget insights today.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Button size="xl" className="h-16 px-12 text-xl bg-white text-blue-700 hover:bg-blue-50 white-glow" asChild>
              <Link href="/subscribe">Start Free Trial</Link>
            </Button>
            <Button variant="outline" size="xl" className="h-16 px-12 text-xl border-white/30 text-white hover:bg-white/10 backdrop-blur-md">
              Contact Sales
            </Button>
          </div>
        </div>

        <style jsx>{`
          .white-glow {
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
          }
          .white-glow:hover {
            box-shadow: 0 0 40px rgba(255, 255, 255, 0.5);
          }
        `}</style>
      </section>

      {/* Footer */}
      <footer className="bg-slate-950 border-t border-slate-900 py-20 px-6">
        <div className="container mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-16">
            <div className="space-y-6">
              <div className="flex items-center space-x-3">
                <div className="bg-blue-600 p-1.5 rounded-md">
                  <BarChart3 className="h-5 w-5 text-white" />
                </div>
                <span className="text-lg font-bold">BudgetAI</span>
              </div>
              <p className="text-slate-400 text-sm leading-relaxed">
                Kenya's most advanced fiscal transparency engine. Turning government data into public power since 2024.
              </p>
            </div>

            <div>
              <h4 className="font-bold text-white mb-6 uppercase tracking-widest text-xs">Platform</h4>
              <ul className="space-y-4 text-sm font-medium text-slate-500">
                <li><Link href="#" className="hover:text-blue-400 transition-colors">Real-time Map</Link></li>
                <li><Link href="#" className="hover:text-blue-400 transition-colors">County Reports</Link></li>
                <li><Link href="#" className="hover:text-blue-400 transition-colors">AI Analysis</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-white mb-6 uppercase tracking-widest text-xs">Resources</h4>
              <ul className="space-y-4 text-sm font-medium text-slate-500">
                <li><Link href="#" className="hover:text-blue-400 transition-colors">Documentation</Link></li>
                <li><Link href="#" className="hover:text-blue-400 transition-colors">Open Data Portal</Link></li>
                <li><Link href="#" className="hover:text-blue-400 transition-colors">API Status</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-white mb-6 uppercase tracking-widest text-xs">Connect</h4>
              <ul className="space-y-4 text-sm font-medium text-slate-500">
                <li><Link href="#" className="hover:text-blue-400 transition-colors">Twitter / X</Link></li>
                <li><Link href="#" className="hover:text-blue-400 transition-colors">LinkedIn</Link></li>
                <li><Link href="#" className="hover:text-blue-400 transition-colors">Contact Support</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-900 mt-20 pt-10 flex flex-col md:flex-row justify-between items-center text-xs text-slate-600 font-medium uppercase tracking-widest gap-6">
            <p>© 2025 BudgetAI 2.0. Built for the citizens of Kenya.</p>
            <div className="flex gap-8">
              <Link href="#" className="hover:text-white transition-colors">Privacy Policy</Link>
              <Link href="#" className="hover:text-white transition-colors">Terms of Service</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
