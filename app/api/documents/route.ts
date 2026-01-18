// app/api/documents/route.ts
import { NextResponse } from "next/server"
import { Pool } from "pg"

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
})

export async function GET() {
  try {
    const client = await pool.connect()
    const result = await client.query("SELECT * FROM uploads ORDER BY created_at DESC")
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
