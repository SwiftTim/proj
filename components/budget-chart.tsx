"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from "recharts"
import { TrendingUp, Download } from "lucide-react"

const budgetData = [
  { county: "Nairobi", budget: 37.5, transparency: 85 },
  { county: "Mombasa", budget: 15.2, transparency: 72 },
  { county: "Kisumu", budget: 12.8, transparency: 68 },
  { county: "Nakuru", budget: 18.3, transparency: 79 },
  { county: "Machakos", budget: 14.7, transparency: 74 },
  { county: "Kiambu", budget: 22.1, transparency: 81 },
]

const trendData = [
  { year: "2020", amount: 180 },
  { year: "2021", amount: 195 },
  { year: "2022", amount: 210 },
  { year: "2023", amount: 225 },
  { year: "2024", amount: 240 },
]

const categoryData = [
  { name: "Infrastructure", value: 35, color: "hsl(var(--chart-1))" },
  { name: "Healthcare", value: 25, color: "hsl(var(--chart-2))" },
  { name: "Education", value: 20, color: "hsl(var(--chart-3))" },
  { name: "Agriculture", value: 12, color: "hsl(var(--chart-4))" },
  { name: "Other", value: 8, color: "hsl(var(--chart-5))" },
]

export function BudgetChart() {
  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <Card className="lg:col-span-2">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>County Budget Comparison</CardTitle>
            <CardDescription>Budget allocation vs transparency score</CardDescription>
          </div>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={budgetData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="county" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
              />
              <Bar dataKey="budget" fill="hsl(var(--chart-1))" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Budget Categories</CardTitle>
          <CardDescription>Allocation by sector</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {categoryData.map((item, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-muted-foreground">{item.name}</span>
                </div>
                <span className="font-medium">{item.value}%</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="lg:col-span-3">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Budget Trends</CardTitle>
            <CardDescription>Total county budgets over time (KSh Billions)</CardDescription>
          </div>
          <Badge variant="secondary" className="bg-chart-2/10 text-chart-2 border-chart-2/20">
            <TrendingUp className="h-3 w-3 mr-1" />
            +6.7% YoY
          </Badge>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="year" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
              />
              <Line
                type="monotone"
                dataKey="amount"
                stroke="hsl(var(--chart-2))"
                strokeWidth={3}
                dot={{ fill: "hsl(var(--chart-2))", strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}
