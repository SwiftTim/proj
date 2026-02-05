import jsPDF from "jspdf"

export const generateIntegrityReport = (result: any) => {
    if (!result) return
    const doc = new jsPDF()
    const margin = 20
    const pageWidth = doc.internal.pageSize.getWidth()
    let yPos = 30

    const formatValue = (key: string, value: any) => {
        if (value === null || value === undefined || value === 0) return "Not Found"
        if (key.includes("pct") || key.includes("rate") || key.includes("performance")) return `${value}%`
        if (typeof value === "number" && value > 1000) return `Ksh ${value.toLocaleString()}`
        return String(value)
    }

    // Header Design
    doc.setFillColor(15, 23, 42) // Slate 900
    doc.rect(0, 0, pageWidth, 50, "F")

    doc.setTextColor(255, 255, 255)
    doc.setFont("helvetica", "bold")
    doc.setFontSize(22)
    doc.text("BUDGET INTEGRITY REPORT", margin, 25)

    doc.setFontSize(10)
    doc.setFont("helvetica", "normal")
    doc.text(`${(result.county).toUpperCase()} COUNTY | FINANCIAL YEAR ${result.year}`, margin, 35)
    doc.text(`PIPELINE: ${result.method?.toUpperCase() || "AI DIAGNOSTIC"}`, margin, 40)

    yPos = 70
    doc.setTextColor(15, 23, 42)

    // Risk Assessment Section
    if (result.intelligence?.transparency_risk_score !== undefined) {
        doc.setFont("helvetica", "bold")
        doc.setFontSize(12)
        doc.text("FISCAL RISK ASSESSMENT", margin, yPos)
        yPos += 8

        const score = result.intelligence.transparency_risk_score
        doc.setFont("helvetica", "normal")
        doc.setFontSize(10)
        doc.text(`Score: ${score}/100`, margin, yPos)

        doc.setDrawColor(200, 200, 200)
        doc.line(margin, yPos + 4, pageWidth - margin, yPos + 4)
        yPos += 15
    }

    // Key Financial Metrics
    doc.setFont("helvetica", "bold")
    doc.setFontSize(12)
    doc.text("KEY FINANCIAL METRICS", margin, yPos)
    yPos += 10

    doc.setFont("helvetica", "normal")
    doc.setFontSize(9)

    const metrics = result.key_metrics || {}
    const metricEntries = Object.entries(metrics)

    metricEntries.forEach(([key, value], index) => {
        const col = index % 2
        const x = margin + (col * (pageWidth - 2 * margin) / 2)

        const label = key.replaceAll("_", " ").toUpperCase()
        const valStr = formatValue(key, value)

        doc.setFont("helvetica", "bold")
        doc.text(label, x, yPos)
        doc.setFont("helvetica", "normal")
        doc.text(valStr, x, yPos + 5)

        if (col === 1 || index === metricEntries.length - 1) {
            yPos += 15
        }

        if (yPos > 270) {
            doc.addPage()
            yPos = 20
        }
    })

    yPos += 5

    // Auditor Summary
    doc.setFont("helvetica", "bold")
    doc.setFontSize(12)
    doc.text("SENIOR AUDITOR EXECUTIVE SUMMARY", margin, yPos)
    yPos += 8

    doc.setFont("helvetica", "normal")
    doc.setFontSize(10)
    const cleanSummary = (result.summary_text || "").replace(/[#*]/g, "")
    const textLines = doc.splitTextToSize(cleanSummary, pageWidth - (2 * margin))

    textLines.forEach((line: string) => {
        if (yPos > 280) {
            doc.addPage()
            yPos = 20
        }
        doc.text(line, margin, yPos)
        yPos += 6
    })

    // Footer
    const totalPages = doc.internal.pages.length - 1
    for (let i = 1; i <= totalPages; i++) {
        doc.setPage(i)
        doc.setFontSize(8)
        doc.setTextColor(150, 150, 150)
        doc.text(`BudgetAI Integrity Diagnostics | Page ${i} of ${totalPages} | Generated on ${new Date().toLocaleDateString()}`, margin, 290)
    }

    doc.save(`${result.county}_Integrity_Report_${result.year}.pdf`)
}
