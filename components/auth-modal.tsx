"use client"

import type React from "react"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { User, Mail, Lock, UserPlus, LogIn } from "lucide-react"
import { LoadingSpinner } from "@/components/loading-spinner"
import { useSuccessNotification, useErrorNotification } from "@/components/toast-notifications"

interface AuthModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onAuthSuccess: (user: { name: string; email: string; role: string }) => void
}

export function AuthModal({ open, onOpenChange, onAuthSuccess }: AuthModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [loginForm, setLoginForm] = useState({ email: "", password: "" })
  const [signupForm, setSignupForm] = useState({ name: "", email: "", password: "", role: "researcher" })

  const showSuccess = useSuccessNotification()
  const showError = useErrorNotification()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!loginForm.email || !loginForm.password) {
      showError("Missing fields", "Please fill in all required fields.")
      return
    }

    setIsLoading(true)

    try {
      // Simulate authentication
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Mock successful login
      const user = {
        name: loginForm.email.split("@")[0],
        email: loginForm.email,
        role: "researcher",
      }

      localStorage.setItem("auth_user", JSON.stringify(user))
      onAuthSuccess(user)
      onOpenChange(false)

      showSuccess("Welcome back!", "You have successfully signed in.")
    } catch (error) {
      showError("Sign in failed", "Please check your credentials and try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!signupForm.name || !signupForm.email || !signupForm.password) {
      showError("Missing fields", "Please fill in all required fields.")
      return
    }

    setIsLoading(true)

    try {
      // Simulate registration
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Mock successful registration
      const user = {
        name: signupForm.name,
        email: signupForm.email,
        role: signupForm.role,
      }

      localStorage.setItem("auth_user", JSON.stringify(user))
      onAuthSuccess(user)
      onOpenChange(false)

      showSuccess("Account created!", "Welcome to AI Budget Transparency platform.")
    } catch (error) {
      showError("Registration failed", "Please try again or contact support.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Access AI Budget Transparency</DialogTitle>
          <DialogDescription>Sign in to upload documents and access advanced analytics</DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="login" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login" disabled={isLoading}>
              Sign In
            </TabsTrigger>
            <TabsTrigger value="signup" disabled={isLoading}>
              Sign Up
            </TabsTrigger>
          </TabsList>

          <TabsContent value="login" className="space-y-4">
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="login-email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="login-email"
                    type="email"
                    placeholder="researcher@university.edu"
                    value={loginForm.email}
                    onChange={(e) => setLoginForm((prev) => ({ ...prev, email: e.target.value }))}
                    className="pl-10"
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="login-password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="login-password"
                    type="password"
                    placeholder="Enter your password"
                    value={loginForm.password}
                    onChange={(e) => setLoginForm((prev) => ({ ...prev, password: e.target.value }))}
                    className="pl-10"
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    Signing In...
                  </>
                ) : (
                  <>
                    <LogIn className="h-4 w-4 mr-2" />
                    Sign In
                  </>
                )}
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="signup" className="space-y-4">
            <form onSubmit={handleSignup} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="signup-name">Full Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="signup-name"
                    type="text"
                    placeholder="Dr. Jane Smith"
                    value={signupForm.name}
                    onChange={(e) => setSignupForm((prev) => ({ ...prev, name: e.target.value }))}
                    className="pl-10"
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="signup-email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="signup-email"
                    type="email"
                    placeholder="researcher@university.edu"
                    value={signupForm.email}
                    onChange={(e) => setSignupForm((prev) => ({ ...prev, email: e.target.value }))}
                    className="pl-10"
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="signup-password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="signup-password"
                    type="password"
                    placeholder="Create a password"
                    value={signupForm.password}
                    onChange={(e) => setSignupForm((prev) => ({ ...prev, password: e.target.value }))}
                    className="pl-10"
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <select
                  id="role"
                  value={signupForm.role}
                  onChange={(e) => setSignupForm((prev) => ({ ...prev, role: e.target.value }))}
                  className="w-full px-3 py-2 border border-input bg-background rounded-md text-sm"
                  disabled={isLoading}
                >
                  <option value="researcher">Academic Researcher</option>
                  <option value="journalist">Journalist</option>
                  <option value="citizen">Concerned Citizen</option>
                  <option value="government">Government Official</option>
                </select>
              </div>
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    Creating Account...
                  </>
                ) : (
                  <>
                    <UserPlus className="h-4 w-4 mr-2" />
                    Create Account
                  </>
                )}
              </Button>
            </form>
          </TabsContent>
        </Tabs>

        <div className="mt-4 p-4 bg-muted/50 rounded-lg">
          <h4 className="font-medium text-sm mb-2">Demo Credentials</h4>
          <div className="text-xs text-muted-foreground space-y-1">
            <p>Email: demo@researcher.edu</p>
            <p>Password: any password</p>
            <Badge variant="secondary" className="text-xs">
              Academic Project
            </Badge>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
