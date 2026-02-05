import { NextResponse } from "next/server"
import { Pool } from "pg"

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
})

export async function POST(req: Request) {
  try {
    const formData = await req.formData()
    const county = formData.get("county") as string
    const year = formData.get("year") as string
    const file = formData.get("file") as File
    const method = formData.get("method") as string

    // 1. Forward to Python service
    const pyForm = new FormData()
    pyForm.append("county", county!)
    pyForm.append("year", year!)
    pyForm.append("file", file)
    pyForm.append("method", method || "hybrid")

    const res = await fetch("http://localhost:8000/analyze_pdf", {
      method: "POST",
      body: pyForm,
    })

    const data = await res.json()

    if (data.status === "success" || !data.error) {
      // 2. Save results to database
      const client = await pool.connect()
      try {
        // Find upload_id
        const uploadRes = await client.query(
          "SELECT id FROM uploads WHERE county = $1 AND year = $2 LIMIT 1",
          [county, year]
        )
        const upload_id = uploadRes.rows[0]?.id

        const interpreted = data.interpreted_data || data
        const raw_verified = data.raw_verified_data || null

        await client.query(
          `INSERT INTO analysis_results (
            upload_id, county, year, revenue, expenditure, 
            intelligence, summary_text, raw_extracted
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
          ON CONFLICT DO NOTHING`,
          [
            upload_id,
            county,
            year,
            JSON.stringify(interpreted.key_metrics || {}),
            JSON.stringify(interpreted.sectoral_allocations || {}),
            JSON.stringify(interpreted.intelligence || {}),
            interpreted.summary_text,
            JSON.stringify(raw_verified)
          ]
        )

        // Update upload status
        if (upload_id) {
          await client.query(
            "UPDATE uploads SET upload_status = 'completed' WHERE id = $1",
            [upload_id]
          )
        }
      } finally {
        client.release()
      }
    }

    return NextResponse.json(data)
  } catch (err: any) {
    console.error("Analysis API error:", err)
    return NextResponse.json({ success: false, error: err.message }, { status: 500 })
  }
}
