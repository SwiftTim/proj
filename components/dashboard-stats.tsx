import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { FileText, TrendingUp, AlertTriangle, CheckCircle } from "lucide-react"

export function DashboardStats() {
  const stats = [
    {
      title: "Total Documents",
      value: "47",
      description: "Budget documents analyzed",
      icon: FileText,
      trend: "+12%",
      trendUp: true,
    },
    {
      title: "Counties Covered",
      value: "15",
      description: "Out of 47 counties",
      icon: CheckCircle,
      trend: "32%",
      trendUp: true,
    },
    {
      title: "Budget Analyzed",
      value: "KSh 2.4B",
      description: "Total budget amount",
      icon: TrendingUp,
      trend: "+8.2%",
      trendUp: true,
    },
    {
      title: "Issues Identified",
      value: "23",
      description: "Transparency concerns",
      icon: AlertTriangle,
      trend: "-5%",
      trendUp: false,
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, index) => (
        <Card key={index} className="relative overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
            <stat.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{stat.value}</div>
            <div className="flex items-center justify-between mt-2">
              <p className="text-xs text-muted-foreground">{stat.description}</p>
              <Badge
                variant={stat.trendUp ? "default" : "destructive"}
                className={stat.trendUp ? "bg-chart-2/10 text-chart-2 border-chart-2/20" : ""}
              >
                {stat.trend}
              </Badge>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
