import { NextRequest, NextResponse } from "next/server";
import { events } from "@/lib/events-data";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const category = searchParams.get("category");
  const location = searchParams.get("location");

  const filtered = events.filter((event) => {
    const categoryOk = !category || event.category === category;
    const locationOk = !location || event.location === location;
    return categoryOk && locationOk;
  });

  const sorted = [...filtered].sort((a, b) => (a.publishedAt < b.publishedAt ? 1 : -1));
  return NextResponse.json(sorted);
}
