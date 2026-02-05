import { NextResponse } from "next/server"
import { Pool } from "pg"

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
})

export async function GET() {
    try {
        const client = await pool.connect()

        // Fetch all successful analysis results
        const result = await client.query(`
            SELECT 
                ar.id,
                ar.county,
                ar.year,
                ar.summary_text,
                ar.revenue as key_metrics,
                ar.intelligence,
                ar.created_at,
                u.filenames
            FROM analysis_results ar
            JOIN uploads u ON ar.upload_id = u.id
            ORDER BY ar.created_at DESC
        `)

        client.release()

        return NextResponse.json({ success: true, reports: result.rows })
    } catch (err) {
        console.error("Error fetching reports:", err)
        return NextResponse.json({ success: false, error: "Failed to fetch reports" }, { status: 500 })
    }
}
