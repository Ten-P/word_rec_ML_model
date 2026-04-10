import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const file = formData.get("audio") as File; 

  // バックエンドに転送
  const backendForm = new FormData();
  backendForm.append("file", file, "recording.webm");

  const response = await fetch("http://localhost:8000/upload-audio", {
    method: "POST",
    body: backendForm,
  })

  const result = await response.json();
  return NextResponse.json(result);
}