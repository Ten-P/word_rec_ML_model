import { NextRequest, NextResponse } from "next/server";
import { writeFile } from "fs/promises";
import path from "path";

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const file = formData.get("audio") as File; 
  const name = formData.get("name") as string;

  const safeName = path.basename(name).replace(/[^a-zA-Z0-9_\-\.]/g, "_");

  const buffer = Buffer.from(await file.arrayBuffer()); // File → Buffer

  const savePath = path.join(process.cwd(), "src/app/api/transcri", safeName + ".webm");
  await writeFile(savePath, buffer);

  return NextResponse.json({ saved: savePath });
}