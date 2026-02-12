import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchEventById } from "@/lib/api";

export default async function EventDetailPage({ params }: { params: { id: string } }) {
  const event = await fetchEventById(params.id);
  if (!event) notFound();

  return (
    <article className="card detail">
      <p className="meta">
        <span>{event.category}</span>
        <span>{event.location}</span>
        <span>{new Date(event.publishedAt).toLocaleString()}</span>
      </p>
      <h1>{event.title}</h1>
      <p>{event.content}</p>
      <p>
        <Link href="/">← Back to all events</Link>
      </p>
    </article>
  );
}
