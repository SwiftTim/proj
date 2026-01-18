"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { BarChart3, ArrowLeft, UserIcon, Bell, Shield, CreditCard, Download, Trash2 } from "lucide-react"
import { useSuccessNotification, useErrorNotification } from "@/components/toast-notifications"
import Link from "next/link"

interface NotificationSettings {
  emailNotifications: boolean
  documentProcessed: boolean
  weeklyReports: boolean
  securityAlerts: boolean
}

export default function SettingsPage() {
  const [user, setUser] = useState<any | null>(null)
  const [notifications, setNotifications] = useState<NotificationSettings>({
    emailNotifications: true,
    documentProcessed: true,
    weeklyReports: false,
    securityAlerts: true,
  })
  const [isLoading, setIsLoading] = useState(false)

  const showSuccess = useSuccessNotification()
  const showError = useErrorNotification()

  useEffect(() => {
    const savedUser = localStorage.getItem("auth_user")
    if (savedUser) {
      setUser(JSON.parse(savedUser))
    }
  }, [])

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user) return

    setIsLoading(true)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      localStorage.setItem("auth_user", JSON.stringify(user))
      showSuccess("Profile updated", "Your profile information has been saved successfully.")
    } catch (error) {
      showError("Update failed", "Failed to update profile. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleNotificationUpdate = async (setting: keyof NotificationSettings, value: boolean) => {
    setNotifications((prev) => ({ ...prev, [setting]: value }))

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 300))
      showSuccess("Settings updated", "Notification preferences saved.")
    } catch (error) {
      showError("Update failed", "Failed to update notification settings.")
    }
  }

  const handleExportData = async () => {
    try {
      // Simulate data export
      await new Promise((resolve) => setTimeout(resolve, 2000))
      showSuccess("Export complete", "Your data has been exported and will be emailed to you.")
    } catch (error) {
      showError("Export failed", "Failed to export data. Please try again.")
    }
  }

  const handleDeleteAccount = async () => {
    if (!confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
      return
    }

    try {
      // Simulate account deletion
      await new Promise((resolve) => setTimeout(resolve, 1000))
      localStorage.removeItem("auth_user")
      showSuccess("Account deleted", "Your account has been successfully deleted.")
      window.location.href = "/"
    } catch (error) {
      showError("Deletion failed", "Failed to delete account. Please contact support.")
    }
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>Authentication Required</CardTitle>
            <CardDescription>Please sign in to access settings</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/dashboard">Go to Dashboard</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/dashboard">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Dashboard
                </Link>
              </Button>
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-8 w-8 text-accent" />
                <span className="text-xl font-bold">Settings</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Account Settings</h1>
          <p className="text-muted-foreground">Manage your account preferences and settings</p>
        </div>

        <Tabs defaultValue="profile" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="profile" className="flex items-center space-x-2">
              <UserIcon className="h-4 w-4" />
              <span>Profile</span>
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center space-x-2">
              <Bell className="h-4 w-4" />
              <span>Notifications</span>
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center space-x-2">
              <Shield className="h-4 w-4" />
              <span>Security</span>
            </TabsTrigger>
            <TabsTrigger value="billing" className="flex items-center space-x-2">
              <CreditCard className="h-4 w-4" />
              <span>Billing</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="profile" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>Update your personal information and preferences</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleProfileUpdate} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name</Label>
                      <Input
                        id="name"
                        value={user.name}
                        onChange={(e) => setUser((prev) => (prev ? { ...prev, name: e.target.value } : null))}
                        disabled={isLoading}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        value={user.email}
                        onChange={(e) => setUser((prev) => (prev ? { ...prev, email: e.target.value } : null))}
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="organization">Organization</Label>
                      <Input
                        id="organization"
                        value={user.organization || ""}
                        onChange={(e) => setUser((prev) => (prev ? { ...prev, organization: e.target.value } : null))}
                        placeholder="University, NGO, Government Agency"
                        disabled={isLoading}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="country">Country</Label>
                      <Select
                        value={user.country || ""}
                        onValueChange={(value) => setUser((prev) => (prev ? { ...prev, country: value } : null))}
                        disabled={isLoading}
                      >
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
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="role">Role</Label>
                    <Select
                      value={user.role}
                      onValueChange={(value) => setUser((prev) => (prev ? { ...prev, role: value } : null))}
                      disabled={isLoading}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="researcher">Academic Researcher</SelectItem>
                        <SelectItem value="journalist">Journalist</SelectItem>
                        <SelectItem value="citizen">Concerned Citizen</SelectItem>
                        <SelectItem value="government">Government Official</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Button type="submit" disabled={isLoading}>
                    {isLoading ? "Updating..." : "Update Profile"}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="notifications" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
                <CardDescription>Choose how you want to be notified about important updates</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">Receive notifications via email</p>
                  </div>
                  <Switch
                    checked={notifications.emailNotifications}
                    onCheckedChange={(checked) => handleNotificationUpdate("emailNotifications", checked)}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Document Processed</Label>
                    <p className="text-sm text-muted-foreground">Get notified when document analysis is complete</p>
                  </div>
                  <Switch
                    checked={notifications.documentProcessed}
                    onCheckedChange={(checked) => handleNotificationUpdate("documentProcessed", checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Weekly Reports</Label>
                    <p className="text-sm text-muted-foreground">Receive weekly summary reports</p>
                  </div>
                  <Switch
                    checked={notifications.weeklyReports}
                    onCheckedChange={(checked) => handleNotificationUpdate("weeklyReports", checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Security Alerts</Label>
                    <p className="text-sm text-muted-foreground">Important security and account notifications</p>
                  </div>
                  <Switch
                    checked={notifications.securityAlerts}
                    onCheckedChange={(checked) => handleNotificationUpdate("securityAlerts", checked)}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="security" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Security Settings</CardTitle>
                <CardDescription>Manage your account security and data</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h4 className="font-medium mb-2">Password</h4>
                  <p className="text-sm text-muted-foreground mb-4">Change your password to keep your account secure</p>
                  <Button variant="outline">Change Password</Button>
                </div>

                <Separator />

                <div>
                  <h4 className="font-medium mb-2">Data Export</h4>
                  <p className="text-sm text-muted-foreground mb-4">
                    Download a copy of all your data including uploaded documents and analysis results
                  </p>
                  <Button variant="outline" onClick={handleExportData}>
                    <Download className="h-4 w-4 mr-2" />
                    Export My Data
                  </Button>
                </div>

                <Separator />

                <div>
                  <h4 className="font-medium mb-2 text-destructive">Danger Zone</h4>
                  <p className="text-sm text-muted-foreground mb-4">
                    Permanently delete your account and all associated data. This action cannot be undone.
                  </p>
                  <Button variant="destructive" onClick={handleDeleteAccount}>
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete Account
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="billing" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Subscription & Billing</CardTitle>
                <CardDescription>Manage your subscription and payment information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h4 className="font-medium">Current Plan</h4>
                    <p className="text-sm text-muted-foreground">Professional Plan</p>
                  </div>
                  <div className="text-right">
                    <Badge className="bg-accent/10 text-accent border-accent/20">Active</Badge>
                    <p className="text-sm text-muted-foreground mt-1">$299/month</p>
                  </div>
                </div>

                <div className="flex space-x-4">
                  <Button variant="outline" asChild>
                    <Link href="/pricing">Change Plan</Link>
                  </Button>
                  <Button variant="outline">Update Payment Method</Button>
                </div>

                <Separator />

                <div>
                  <h4 className="font-medium mb-4">Billing History</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-3 border rounded">
                      <div>
                        <p className="font-medium">Professional Plan</p>
                        <p className="text-sm text-muted-foreground">January 2025</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">$299.00</p>
                        <Badge variant="secondary">Paid</Badge>
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-3 border rounded">
                      <div>
                        <p className="font-medium">Professional Plan</p>
                        <p className="text-sm text-muted-foreground">December 2024</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">$299.00</p>
                        <Badge variant="secondary">Paid</Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
