import { NextResponse } from "next/server";
import { Pool } from "pg";
import path from "path";
import fs from "fs/promises";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL, // stored in .env.local
});

export async function POST(req: Request) {
  try {
    const formData = await req.formData();
    const county = formData.get("county") as string;
    const year = formData.get("year") as string;
    const files = formData.getAll("files") as File[];

    if (!county || !year || files.length === 0) {
      return NextResponse.json({ success: false, error: "Missing county, year, or files" }, { status: 400 });
    }

    // Ensure upload directory exists
    const uploadDir = path.join(process.cwd(), "public/uploads");
    await fs.mkdir(uploadDir, { recursive: true });

    // Save files physically
    const savedFileNames: string[] = [];

    for (const file of files) {
      const bytes = await file.arrayBuffer();
      const buffer = Buffer.from(bytes);
      const filePath = path.join(uploadDir, file.name);
      await fs.writeFile(filePath, buffer);
      savedFileNames.push(file.name);
    }

    // Save metadata to database
    const client = await pool.connect();
    await client.query(
      `INSERT INTO uploads (county, year, filenames, created_at) VALUES ($1, $2, $3, NOW())`,
      [county, year, JSON.stringify(savedFileNames)]
    );
    client.release();

    return NextResponse.json({ success: true, uploaded: savedFileNames });
  } catch (err: any) {
    console.error("Upload error:", err);
    return NextResponse.json({ success: false, error: err.message }, { status: 500 });
  }
}
