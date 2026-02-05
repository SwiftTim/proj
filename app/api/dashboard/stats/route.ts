import { NextResponse } from "next/server"
import { Pool } from "pg"

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
})

export async function GET() {
    try {
        const client = await pool.connect()

        // Total Documents
        const docsCount = await client.query("SELECT COUNT(*) FROM uploads")

        // Counties Covered (uniquely analyzed)
        const countiesCount = await client.query("SELECT COUNT(DISTINCT county) FROM analysis_results")

        // Total Budget Analyzed (sum of all revenue_actual found)
        // We use a regex to ensure we only sum numeric-looking strings
        const budgetSum = await client.query(`
          SELECT SUM(
            CASE 
              WHEN (revenue->>'own_source_revenue') ~ '^[0-9.]+$' 
              THEN (revenue->>'own_source_revenue')::NUMERIC 
              ELSE 0 
            END
          ) as total 
          FROM analysis_results
        `)

        // Issues identified (count total flags/risks)
        const issuesCount = await client.query(`
          SELECT SUM(
            CASE 
              WHEN jsonb_typeof(intelligence->'flags') = 'array' 
              THEN jsonb_array_length(intelligence->'flags')
              ELSE 0 
            END
          ) as total 
          FROM analysis_results 
        `)

        client.release()

        const totalBudget = parseInt(budgetSum.rows[0].total || "0")
        const formattedBudget = totalBudget > 1000000000
            ? `KSh ${(totalBudget / 1000000000).toFixed(1)}B`
            : `KSh ${(totalBudget / 1000000).toFixed(0)}M`

        return NextResponse.json({
            success: true,
            stats: [
                {
                    title: "Total Documents",
                    value: docsCount.rows[0].count,
                    description: "Budget documents analyzed",
                    trend: "+5%",
                    trendUp: true,
                },
                {
                    title: "Counties Covered",
                    value: countiesCount.rows[0].count,
                    description: "Out of 47 counties",
                    trend: `${Math.round((countiesCount.rows[0].count / 47) * 100)}%`,
                    trendUp: true,
                },
                {
                    title: "Budget Analyzed",
                    value: formattedBudget,
                    description: "Sum of verified OSR",
                    trend: "+12%",
                    trendUp: true,
                },
                {
                    title: "Issues Identified",
                    value: issuesCount.rows[0].total || "0",
                    description: "Transparency concerns",
                    trend: "-2%",
                    trendUp: false,
                },
            ]
        })
    } catch (err) {
        console.error("Dashboard stats error:", err)
        return NextResponse.json({ success: false, error: "Failed to fetch stats" }, { status: 500 })
    }
}
