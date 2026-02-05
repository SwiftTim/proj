// app/api/documents/route.ts
import { NextResponse } from "next/server"
import { Pool } from "pg"

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
})

export async function GET() {
  try {
    const client = await pool.connect()

    // Join uploads with analysis_results to see which have reports
    const result = await client.query(`
      SELECT 
        u.*, 
        ar.id as analysis_id,
        ar.county as analysis_county,
        ar.summary_text,
        ar.revenue as key_metrics,
        ar.intelligence
      FROM uploads u
      LEFT JOIN analysis_results ar ON u.id = ar.upload_id
      ORDER BY u.created_at DESC
    `)

    client.release()

    return NextResponse.json({ success: true, documents: result.rows })
  } catch (err) {
    console.error("Error fetching documents:", err)
    return NextResponse.json(
      { success: false, error: "Failed to fetch documents" },
      { status: 500 }
    )
  }
}
