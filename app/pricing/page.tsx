"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { CheckCircle, BarChart3, ArrowLeft, Star, Shield } from "lucide-react"
import Link from "next/link"

export default function PricingPage() {
  const [isAnnual, setIsAnnual] = useState(false)

  const plans = [
    {
      name: "Starter",
      description: "Perfect for small organizations and NGOs",
      monthlyPrice: 99,
      annualPrice: 990,
      features: [
        "Up to 50 documents/month",
        "Basic transparency scoring",
        "Standard AI analysis",
        "Email support",
        "Basic dashboard",
        "PDF export",
      ],
      limitations: ["Limited to 2 users", "Basic reporting only"],
      cta: "Start Free Trial",
      popular: false,
    },
    {
      name: "Professional",
      description: "For government agencies and research institutions",
      monthlyPrice: 299,
      annualPrice: 2990,
      features: [
        "Up to 500 documents/month",
        "Advanced AI analysis",
        "Real-time monitoring",
        "Custom transparency metrics",
        "Priority support",
        "Advanced dashboard",
        "API access",
        "White-label reports",
        "Team collaboration (up to 10 users)",
      ],
      limitations: [],
      cta: "Start Free Trial",
      popular: true,
    },
    {
      name: "Enterprise",
      description: "For large organizations with custom needs",
      monthlyPrice: null,
      annualPrice: null,
      features: [
        "Unlimited documents",
        "Custom AI models",
        "Dedicated infrastructure",
        "24/7 phone support",
        "Custom integrations",
        "On-premise deployment",
        "Advanced security features",
        "Unlimited users",
        "Custom training",
        "SLA guarantee",
      ],
      limitations: [],
      cta: "Contact Sales",
      popular: false,
    },
  ]

  return (
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
                <span className="text-xl font-bold">BudgetAI</span>
              </div>
            </div>
            <Button asChild>
              <Link href="/dashboard">Get Started</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Pricing Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold mb-4">Simple, Transparent Pricing</h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Choose the plan that fits your organization's budget transparency needs. All plans include a 14-day free
            trial.
          </p>

          {/* Annual/Monthly Toggle */}
          <div className="flex items-center justify-center space-x-4 mb-8">
            <span className={`text-sm ${!isAnnual ? "text-foreground" : "text-muted-foreground"}`}>Monthly</span>
            <Switch checked={isAnnual} onCheckedChange={setIsAnnual} />
            <span className={`text-sm ${isAnnual ? "text-foreground" : "text-muted-foreground"}`}>Annual</span>
            <Badge variant="secondary" className="bg-accent/10 text-accent border-accent/20">
              Save 17%
            </Badge>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => (
            <Card key={plan.name} className={`relative ${plan.popular ? "border-accent shadow-lg scale-105" : ""}`}>
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-accent text-accent-foreground">
                    <Star className="h-3 w-3 mr-1" />
                    Most Popular
                  </Badge>
                </div>
              )}

              <CardHeader className="text-center">
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                <CardDescription className="text-base">{plan.description}</CardDescription>

                <div className="py-4">
                  {plan.monthlyPrice ? (
                    <div>
                      <div className="text-4xl font-bold">
                        ${isAnnual ? Math.floor(plan.annualPrice / 12) : plan.monthlyPrice}
                        <span className="text-lg font-normal text-muted-foreground">/month</span>
                      </div>
                      {isAnnual && (
                        <div className="text-sm text-muted-foreground">Billed annually (${plan.annualPrice}/year)</div>
                      )}
                    </div>
                  ) : (
                    <div className="text-4xl font-bold">Custom</div>
                  )}
                </div>
              </CardHeader>

              <CardContent>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start">
                      <CheckCircle className="h-4 w-4 text-accent mr-3 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                  {plan.limitations.map((limitation, limitIndex) => (
                    <li key={limitIndex} className="flex items-start text-muted-foreground">
                      <div className="h-4 w-4 mr-3 mt-0.5 flex-shrink-0 border border-muted-foreground/30 rounded-full" />
                      <span className="text-sm">{limitation}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  className={`w-full ${plan.popular ? "" : "variant-outline"}`}
                  variant={plan.popular ? "default" : "outline"}
                  size="lg"
                >
                  {plan.cta}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="mt-24">
          <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div>
              <h3 className="font-semibold mb-2">What's included in the free trial?</h3>
              <p className="text-muted-foreground text-sm">
                All plans include a 14-day free trial with full access to features. No credit card required.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Can I change plans anytime?</h3>
              <p className="text-muted-foreground text-sm">
                Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">What payment methods do you accept?</h3>
              <p className="text-muted-foreground text-sm">
                We accept all major credit cards, bank transfers, and can accommodate purchase orders for Enterprise
                clients.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Is there a setup fee?</h3>
              <p className="text-muted-foreground text-sm">
                No setup fees for Starter and Professional plans. Enterprise plans may include implementation services.
              </p>
            </div>
          </div>
        </div>

        {/* Enterprise CTA */}
        <div className="mt-16 text-center">
          <Card className="max-w-2xl mx-auto bg-accent/5 border-accent/20">
            <CardHeader>
              <div className="flex items-center justify-center mb-4">
                <Shield className="h-8 w-8 text-accent" />
              </div>
              <CardTitle>Need a custom solution?</CardTitle>
              <CardDescription>
                Our Enterprise plan offers unlimited scalability, custom integrations, and dedicated support for large
                organizations.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button size="lg" className="mr-4">
                Contact Sales
              </Button>
              <Button variant="outline" size="lg">
                Schedule Demo
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
