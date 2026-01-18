// app/api/fetchCountyData/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const county = searchParams.get("county");
    const year = searchParams.get("year");
    const category = searchParams.get("category");

    if (!county || !year || !category) {
      return NextResponse.json({ error: "Missing parameters" }, { status: 400 });
    }

    const apiUrl = `https://opencounty.org/opencounty/api/?county=${county}&catgroup=api_budget&category=${category}&year=${year}`;
    const res = await fetch(apiUrl);

    if (!res.ok) {
      return NextResponse.json({ error: "Failed to fetch from OpenCounty API" }, { status: res.status });
    }

    const data = await res.json();
    return NextResponse.json({ success: true, data });
  } catch (err: any) {
    return NextResponse.json({ error: err.message || "Server error" }, { status: 500 });
  }
}
