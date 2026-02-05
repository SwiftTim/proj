import { NextResponse } from "next/server"
import { Pool } from "pg"

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
})

export async function POST(req: Request) {
    try {
        const { pdfId, county, year } = await req.json()

        console.log(`🌟 Forwarding Gemini Analysis for ${county} (PDF: ${pdfId}) to Python service...`)

        // 1. Call Python service
        const response = await fetch('http://127.0.0.1:8000/analyze/gemini', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pdf_id: pdfId,
                county: county
            })
        })

        if (!response.ok) {
            let errorMsg = "Python service error"
            try {
                const errorData = await response.json()
                errorMsg = errorData.detail || errorMsg
            } catch (e) { }
            console.error(`❌ Python service returned ${response.status}: ${errorMsg}`)
            return NextResponse.json({ success: false, error: errorMsg }, { status: response.status })
        }

        const result = await response.json()
        const data = result.interpreted_data || {}

        // 2. Save to database
        const client = await pool.connect()
        try {
            // Find upload_id by filename
            const uploadRes = await client.query(
                "SELECT id FROM uploads WHERE filenames @> $1 LIMIT 1",
                [JSON.stringify([pdfId])]
            )
            const upload_id = uploadRes.rows[0]?.id

            // Map the Gemini results to the database schema
            const keyMetrics = data.key_metrics || {}
            const intelligence = data.intelligence || {}
            const summary_text = data.summary_text || "No summary provided."
            const raw_extracted = result.raw_verified_data || {}

            // Check if analysis already exists
            const existingAnalysis = await client.query(
                "SELECT id FROM analysis_results WHERE upload_id = $1 AND county = $2 LIMIT 1",
                [upload_id, county]
            )

            if (existingAnalysis.rows.length > 0) {
                // Update
                await client.query(
                    `UPDATE analysis_results SET 
              revenue = $1, expenditure = $2, intelligence = $3, summary_text = $4, raw_extracted = $5, year = $6, created_at = CURRENT_TIMESTAMP
             WHERE id = $7`,
                    [
                        JSON.stringify(keyMetrics),
                        JSON.stringify({}), // Sectoral expenditure could be added later
                        JSON.stringify(intelligence),
                        summary_text,
                        JSON.stringify(raw_extracted),
                        year,
                        existingAnalysis.rows[0].id
                    ]
                )
                console.log(`✅ Updated Gemini analysis for ${county}`)
            } else {
                // Insert
                await client.query(
                    `INSERT INTO analysis_results (
              upload_id, county, year, revenue, expenditure, 
              intelligence, summary_text, raw_extracted
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
                    [
                        upload_id,
                        county,
                        year,
                        JSON.stringify(keyMetrics),
                        JSON.stringify({}),
                        JSON.stringify(intelligence),
                        summary_text,
                        JSON.stringify(raw_extracted)
                    ]
                )
                console.log(`✅ Saved new Gemini analysis for ${county}`)
            }

            if (upload_id) {
                await client.query(
                    "UPDATE uploads SET upload_status = 'completed' WHERE id = $1",
                    [upload_id]
                )
            }
        } finally {
            client.release()
        }

        return NextResponse.json({ success: true, data: result })
    } catch (err: any) {
        console.error("Gemini Analysis API error:", err)
        return NextResponse.json({ success: false, error: err.message }, { status: 500 })
    }
}
