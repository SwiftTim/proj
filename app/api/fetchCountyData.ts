// app/api/fetchCountyData/route.ts
import { NextRequest, NextResponse } from "next/server"

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url)
    const county = searchParams.get("county")
    const year = searchParams.get("year")
    const category = searchParams.get("category")

    if (!county || !year || !category) {
      return NextResponse.json({ error: "Missing parameters" }, { status: 400 })
    }

    const url = `https://opencounty.org/opencounty/api/?county=${county}&catgroup=api_budget&category=${category}&year=${year}`
    const response = await fetch(url)

    if (!response.ok) {
      return NextResponse.json({ error: "Failed to fetch from OpenCounty API" }, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json({ data })
  } catch (err: any) {
    console.error(err)
    return NextResponse.json({ error: err.message || "Server error" }, { status: 500 })
  }
}
