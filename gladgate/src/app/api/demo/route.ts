import { NextResponse } from "next/server";
import { getDemoSnapshot, resetDemo } from "@/lib/store";

export async function GET() {
  return NextResponse.json(getDemoSnapshot());
}

export async function DELETE() {
  return NextResponse.json(resetDemo());
}
