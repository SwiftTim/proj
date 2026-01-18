import { NextResponse } from "next/server"

export async function POST(req: Request) {
  try {
    const formData = await req.formData()
    const county = formData.get("county")
    const year = formData.get("year")
    const file = formData.get("file") as File

    const pyForm = new FormData()
    pyForm.append("county", county!)
    pyForm.append("year", year!)
    pyForm.append("file", file)

    const res = await fetch("http://localhost:8000/analyze_pdf", {
      method: "POST",
      body: pyForm,
    })

    const data = await res.json()
    return NextResponse.json(data)
  } catch (err: any) {
    return NextResponse.json({ success: false, error: err.message }, { status: 500 })
  }
}
