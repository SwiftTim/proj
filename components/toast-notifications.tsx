"use client"
import { useToast } from "@/hooks/use-toast"
import { CheckCircle, AlertCircle, Info, AlertTriangle } from "lucide-react"

interface ToastNotificationProps {
  type: "success" | "error" | "info" | "warning"
  title: string
  description?: string
  duration?: number
}

export function useNotification() {
  const { toast } = useToast()

  const showNotification = ({ type, title, description, duration = 5000 }: ToastNotificationProps) => {
    const icons = {
      success: CheckCircle,
      error: AlertCircle,
      info: Info,
      warning: AlertTriangle,
    }

    const Icon = icons[type]

    toast({
      title: (
        <div className="flex items-center space-x-2">
          <Icon
            className={`h-4 w-4 ${
              type === "success"
                ? "text-chart-2"
                : type === "error"
                  ? "text-destructive"
                  : type === "warning"
                    ? "text-chart-3"
                    : "text-chart-1"
            }`}
          />
          <span>{title}</span>
        </div>
      ),
      description,
      duration,
      variant: type === "error" ? "destructive" : "default",
    })
  }

  return { showNotification }
}

// Predefined notification helpers
export function useSuccessNotification() {
  const { showNotification } = useNotification()

  return (title: string, description?: string) => showNotification({ type: "success", title, description })
}

export function useErrorNotification() {
  const { showNotification } = useNotification()

  return (title: string, description?: string) => showNotification({ type: "error", title, description })
}

export function useInfoNotification() {
  const { showNotification } = useNotification()

  return (title: string, description?: string) => showNotification({ type: "info", title, description })
}
