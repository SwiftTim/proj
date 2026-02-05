import { NextResponse } from "next/server"

export async function GET(
    req: Request,
    { params }: { params: { id: string } }
) {
    const meritId = params.id
    const { searchParams } = new URL(req.url)
    const counties = searchParams.get("counties")

    try {
        let url = `http://127.0.0.1:8000/api/trending-merits/${meritId}/data`
        if (counties) url += `?counties=${counties}`

        const response = await fetch(url)
        const data = await response.json()
        return NextResponse.json(data)
    } catch (err: any) {
        console.error("Merit data API error:", err)
        return NextResponse.json({ success: false, error: err.message }, { status: 500 })
    }
}
