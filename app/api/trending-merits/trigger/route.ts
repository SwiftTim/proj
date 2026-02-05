import { NextResponse } from "next/server"

export async function POST() {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/trigger-hot-take-analysis`, {
            method: 'POST'
        })
        const data = await response.json()
        return NextResponse.json(data)
    } catch (err: any) {
        console.error("Trigger hot take API error:", err)
        return NextResponse.json({ success: false, error: err.message }, { status: 500 })
    }
}
