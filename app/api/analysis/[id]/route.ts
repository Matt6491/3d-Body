import { NextRequest, NextResponse } from "next/server";
import { repo } from "@/lib/storage";

export async function DELETE(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const deleted = repo.deleteAnalysis(id);
  return NextResponse.json({ deleted });
}
