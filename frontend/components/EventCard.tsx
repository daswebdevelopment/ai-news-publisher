import Link from "next/link";
import { NewsEvent } from "@/types/event";

export function EventCard({ event }: { event: NewsEvent }) {
  const publishedAt = new Date(event.publishedAt).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short"
  });

  return (
    <article className="card">
      <p className="meta">
        <span className="pill">{event.category}</span>
        <span className="pill pill-muted">{event.location}</span>
        <span className="time">{publishedAt}</span>
      </p>
      <h2 className="card-title">
        <Link href={`/events/${event.id}`}>{event.title}</Link>
      </h2>
      <p className="card-summary">{event.summary}</p>
      <Link className="card-link" href={`/events/${event.id}`}>
        Explore full coverage <span aria-hidden>↗</span>
      </Link>
    </article>
  );
}
