"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { BarChart3, ArrowLeft, CreditCard, Shield, CheckCircle } from "lucide-react"
import Link from "next/link"

export default function SubscribePage() {
  const [selectedPlan, setSelectedPlan] = useState("professional")
  const [billingCycle, setBillingCycle] = useState("annual")
  const [formData, setFormData] = useState({
    email: "",
    organizationName: "",
    firstName: "",
    lastName: "",
    country: "",
    agreeToTerms: false,
  })

  const plans = {
    starter: { name: "Starter", monthly: 99, annual: 990 },
    professional: { name: "Professional", monthly: 299, annual: 2990 },
  }

  const currentPlan = plans[selectedPlan as keyof typeof plans]
  const price = billingCycle === "annual" ? currentPlan.annual : currentPlan.monthly
  const monthlyPrice = billingCycle === "annual" ? Math.floor(currentPlan.annual / 12) : currentPlan.monthly

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle subscription logic here
    console.log("Subscription data:", { ...formData, plan: selectedPlan, billingCycle, price })
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/pricing">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Pricing
                </Link>
              </Button>
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-8 w-8 text-accent" />
                <span className="text-xl font-bold">BudgetAI</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2">Complete Your Subscription</h1>
            <p className="text-muted-foreground">Start your 14-day free trial today</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Subscription Form */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Plan Selection</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Choose Plan</Label>
                    <Select value={selectedPlan} onValueChange={setSelectedPlan}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="starter">Starter - $99/month</SelectItem>
                        <SelectItem value="professional">Professional - $299/month</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Billing Cycle</Label>
                    <Select value={billingCycle} onValueChange={setBillingCycle}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="monthly">Monthly</SelectItem>
                        <SelectItem value="annual">Annual (Save 17%)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Organization Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleInputChange("email", e.target.value)}
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="organizationName">Organization Name</Label>
                      <Input
                        id="organizationName"
                        value={formData.organizationName}
                        onChange={(e) => handleInputChange("organizationName", e.target.value)}
                        required
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="firstName">First Name</Label>
                        <Input
                          id="firstName"
                          value={formData.firstName}
                          onChange={(e) => handleInputChange("firstName", e.target.value)}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="lastName">Last Name</Label>
                        <Input
                          id="lastName"
                          value={formData.lastName}
                          onChange={(e) => handleInputChange("lastName", e.target.value)}
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="country">Country</Label>
                      <Select value={formData.country} onValueChange={(value) => handleInputChange("country", value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select country" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="kenya">Kenya</SelectItem>
                          <SelectItem value="uganda">Uganda</SelectItem>
                          <SelectItem value="tanzania">Tanzania</SelectItem>
                          <SelectItem value="rwanda">Rwanda</SelectItem>
                          <SelectItem value="other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="terms"
                        checked={formData.agreeToTerms}
                        onCheckedChange={(checked) => handleInputChange("agreeToTerms", checked as boolean)}
                      />
                      <Label htmlFor="terms" className="text-sm">
                        I agree to the{" "}
                        <Link href="/terms" className="text-accent hover:underline">
                          Terms of Service
                        </Link>{" "}
                        and{" "}
                        <Link href="/privacy" className="text-accent hover:underline">
                          Privacy Policy
                        </Link>
                      </Label>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Order Summary */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Order Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">{currentPlan.name} Plan</div>
                      <div className="text-sm text-muted-foreground">
                        {billingCycle === "annual" ? "Billed annually" : "Billed monthly"}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">${monthlyPrice}/month</div>
                      {billingCycle === "annual" && <div className="text-sm text-muted-foreground">${price}/year</div>}
                    </div>
                  </div>

                  {billingCycle === "annual" && (
                    <div className="flex justify-between items-center text-accent">
                      <div className="text-sm">Annual discount (17%)</div>
                      <div className="text-sm">-${currentPlan.monthly * 12 - currentPlan.annual}</div>
                    </div>
                  )}

                  <div className="border-t pt-4">
                    <div className="flex justify-between items-center font-medium">
                      <div>Total</div>
                      <div>
                        ${billingCycle === "annual" ? price : monthlyPrice}/
                        {billingCycle === "annual" ? "year" : "month"}
                      </div>
                    </div>
                  </div>

                  <Badge
                    variant="secondary"
                    className="w-full justify-center bg-accent/10 text-accent border-accent/20"
                  >
                    14-day free trial included
                  </Badge>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <CreditCard className="h-5 w-5 mr-2" />
                    Payment Method
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="p-4 border border-dashed border-muted-foreground/30 rounded-lg text-center text-muted-foreground">
                      <Shield className="h-8 w-8 mx-auto mb-2" />
                      <div className="text-sm">Secure payment processing</div>
                      <div className="text-xs">No payment required during trial</div>
                    </div>

                    <Button
                      className="w-full"
                      size="lg"
                      onClick={handleSubmit}
                      disabled={!formData.agreeToTerms || !formData.email || !formData.organizationName}
                    >
                      Start Free Trial
                    </Button>

                    <div className="text-xs text-muted-foreground text-center">
                      You won't be charged until your trial ends. Cancel anytime.
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>What's Included</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center">
                      <CheckCircle className="h-4 w-4 text-accent mr-2" />
                      14-day free trial
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-4 w-4 text-accent mr-2" />
                      Full feature access
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-4 w-4 text-accent mr-2" />
                      Email support
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-4 w-4 text-accent mr-2" />
                      Cancel anytime
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
