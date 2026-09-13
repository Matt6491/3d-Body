import { NextRequest, NextResponse } from "next/server";
import { repo } from "@/lib/storage";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const found = repo.getBody(id);
  if (!found) {
    return NextResponse.json({ detail: "Body model not found" }, { status: 404 });
  }
  return NextResponse.json(found);
}

export async function DELETE(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const deleted = repo.deleteBody(id);
  return NextResponse.json({ deleted });
}
