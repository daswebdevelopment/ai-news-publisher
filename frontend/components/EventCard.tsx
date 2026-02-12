import Link from "next/link";
import { NewsEvent } from "@/types/event";

export function EventCard({ event }: { event: NewsEvent }) {
  return (
    <article className="card">
      <p className="meta">
        <span>{event.category}</span>
        <span>{event.location}</span>
        <span>{new Date(event.publishedAt).toLocaleString()}</span>
      </p>
      <h2>
        <Link href={`/events/${event.id}`}>{event.title}</Link>
      </h2>
      <p>{event.summary}</p>
    </article>
  );
}
