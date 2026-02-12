import { NextResponse } from "next/server";
import { events } from "@/lib/events-data";

export async function GET(_: Request, { params }: { params: { id: string } }) {
  const event = events.find((item) => item.id === params.id);
  if (!event) {
    return NextResponse.json({ message: "Event not found" }, { status: 404 });
  }

  return NextResponse.json(event);
}
