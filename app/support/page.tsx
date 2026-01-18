"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Mail, MessageCircle, Book, HelpCircle, Send } from "lucide-react"
import { useSuccessNotification } from "@/components/toast-notifications"
import Link from "next/link"

export default function SupportPage() {
  const [contactForm, setContactForm] = useState({
    name: "",
    email: "",
    subject: "",
    category: "",
    message: "",
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const showSuccess = useSuccessNotification()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    // Simulate form submission
    await new Promise((resolve) => setTimeout(resolve, 1000))

    setIsSubmitting(false)
    setContactForm({ name: "", email: "", subject: "", category: "", message: "" })
    showSuccess("Message sent", "We'll get back to you within 24 hours.")
  }

  const faqs = [
    {
      question: "How does the AI document analysis work?",
      answer:
        "Our AI uses advanced OCR technology to extract text from PDF documents, then applies natural language processing to identify key budget information, calculate transparency scores, and detect potential issues or anomalies.",
    },
    {
      question: "What file formats are supported?",
      answer:
        "Currently, we support PDF files only. We're working on adding support for Word documents and Excel spreadsheets in future updates.",
    },
    {
      question: "How accurate is the transparency scoring?",
      answer:
        "Our transparency scoring algorithm has been trained on thousands of budget documents and achieves 95%+ accuracy. However, we recommend human review for critical decisions.",
    },
    {
      question: "Can I export my analysis results?",
      answer:
        "Yes, you can export analysis results in multiple formats including PDF reports, Excel spreadsheets, and raw data CSV files.",
    },
    {
      question: "Is my data secure?",
      answer:
        "Absolutely. We use enterprise-grade encryption, secure cloud storage, and follow strict data protection protocols. Your documents are never shared with third parties.",
    },
    {
      question: "How much does BudgetAI cost?",
      answer:
        "We offer three plans: Starter ($99/month), Professional ($299/month), and Enterprise (custom pricing). All plans include a 14-day free trial.",
    },
    {
      question: "Can I cancel my subscription anytime?",
      answer:
        "Yes, you can cancel your subscription at any time. There are no cancellation fees, and you'll retain access until the end of your billing period.",
    },
    {
      question: "Do you offer training or onboarding?",
      answer:
        "Professional and Enterprise plans include onboarding support. We also provide comprehensive documentation and video tutorials for all users.",
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
                <HelpCircle className="h-8 w-8 text-accent" />
                <span className="text-xl font-bold">Support Center</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold mb-4">How can we help you?</h1>
          <p className="text-xl text-muted-foreground">
            Find answers to common questions or get in touch with our support team
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Card className="text-center hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="mx-auto w-12 h-12 bg-chart-1/10 rounded-full flex items-center justify-center mb-4">
                <Book className="h-6 w-6 text-chart-1" />
              </div>
              <CardTitle>Documentation</CardTitle>
              <CardDescription>Comprehensive guides and tutorials</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full bg-transparent">
                Browse Docs
              </Button>
            </CardContent>
          </Card>

          <Card className="text-center hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="mx-auto w-12 h-12 bg-chart-2/10 rounded-full flex items-center justify-center mb-4">
                <MessageCircle className="h-6 w-6 text-chart-2" />
              </div>
              <CardTitle>Live Chat</CardTitle>
              <CardDescription>Chat with our support team</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full bg-transparent">
                Start Chat
              </Button>
            </CardContent>
          </Card>

          <Card className="text-center hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="mx-auto w-12 h-12 bg-chart-3/10 rounded-full flex items-center justify-center mb-4">
                <Mail className="h-6 w-6 text-chart-3" />
              </div>
              <CardTitle>Email Support</CardTitle>
              <CardDescription>Get help via email</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full bg-transparent">
                Send Email
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* FAQ Section */}
          <div>
            <h2 className="text-2xl font-bold mb-6">Frequently Asked Questions</h2>
            <Accordion type="single" collapsible className="space-y-2">
              {faqs.map((faq, index) => (
                <AccordionItem key={index} value={`item-${index}`} className="border rounded-lg px-4">
                  <AccordionTrigger className="text-left hover:no-underline">{faq.question}</AccordionTrigger>
                  <AccordionContent className="text-muted-foreground">{faq.answer}</AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>

          {/* Contact Form */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Contact Support</CardTitle>
                <CardDescription>
                  Can't find what you're looking for? Send us a message and we'll get back to you.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Name</Label>
                      <Input
                        id="name"
                        value={contactForm.name}
                        onChange={(e) => setContactForm((prev) => ({ ...prev, name: e.target.value }))}
                        required
                        disabled={isSubmitting}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={contactForm.email}
                        onChange={(e) => setContactForm((prev) => ({ ...prev, email: e.target.value }))}
                        required
                        disabled={isSubmitting}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="category">Category</Label>
                    <Select
                      value={contactForm.category}
                      onValueChange={(value) => setContactForm((prev) => ({ ...prev, category: value }))}
                      disabled={isSubmitting}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="technical">Technical Issue</SelectItem>
                        <SelectItem value="billing">Billing Question</SelectItem>
                        <SelectItem value="feature">Feature Request</SelectItem>
                        <SelectItem value="general">General Inquiry</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="subject">Subject</Label>
                    <Input
                      id="subject"
                      value={contactForm.subject}
                      onChange={(e) => setContactForm((prev) => ({ ...prev, subject: e.target.value }))}
                      required
                      disabled={isSubmitting}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="message">Message</Label>
                    <Textarea
                      id="message"
                      rows={5}
                      value={contactForm.message}
                      onChange={(e) => setContactForm((prev) => ({ ...prev, message: e.target.value }))}
                      required
                      disabled={isSubmitting}
                    />
                  </div>

                  <Button type="submit" className="w-full" disabled={isSubmitting}>
                    {isSubmitting ? (
                      "Sending..."
                    ) : (
                      <>
                        <Send className="h-4 w-4 mr-2" />
                        Send Message
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Contact Info */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Other Ways to Reach Us</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-3">
                  <Mail className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Email</p>
                    <p className="text-sm text-muted-foreground">support@budgetai.com</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <MessageCircle className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Response Time</p>
                    <p className="text-sm text-muted-foreground">Within 24 hours</p>
                  </div>
                </div>

                <div className="pt-4 border-t">
                  <div className="flex items-center space-x-2 mb-2">
                    <Badge className="bg-chart-2/10 text-chart-2 border-chart-2/20">Enterprise Support</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Enterprise customers get priority support with dedicated account managers and phone support.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
