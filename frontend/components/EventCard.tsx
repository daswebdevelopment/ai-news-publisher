import Link from "next/link";
import { NewsEvent } from "@/types/event";

export function EventCard({ event }: { event: NewsEvent }) {
  return (
    <article className="card">
      <p className="meta">
        <span className="pill">{event.category}</span>
        <span className="pill">{event.location}</span>
        <span>{new Date(event.publishedAt).toLocaleString()}</span>
      </p>
      <h2 className="card-title">
        <Link href={`/events/${event.id}`}>{event.title}</Link>
      </h2>
      <p className="card-summary">{event.summary}</p>
      <Link className="card-link" href={`/events/${event.id}`}>
        Read full coverage →
      </Link>
    </article>
  );
}
