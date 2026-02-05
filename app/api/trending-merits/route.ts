import { NextResponse } from "next/server"

export async function GET(req: Request) {
    const { searchParams } = new URL(req.url)
    const days = searchParams.get("days") || "7"

    try {
        const response = await fetch(`http://127.0.0.1:8000/api/trending-merits?days=${days}`)
        const data = await response.json()
        return NextResponse.json(data)
    } catch (err: any) {
        console.error("Trending merits API error:", err)
        return NextResponse.json({ success: false, error: err.message }, { status: 500 })
    }
}
