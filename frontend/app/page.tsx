import { EventCard } from "@/components/EventCard";
import { Filters } from "@/components/Filters";
import { fetchEvents } from "@/lib/api";

export default async function HomePage({
  searchParams
}: {
  searchParams: { category?: string; location?: string };
}) {
  const category = searchParams.category;
  const location = searchParams.location;
  const events = await fetchEvents({ category, location });

  return (
    <section className="page">
      <header className="hero">
        <p className="eyebrow">AI News Publisher</p>
        <h1>Latest AI News Events</h1>
        <p className="intro">Stay on top of launches, research updates, and policy changes from key AI hubs.</p>
      </header>

      <Filters category={category} location={location} />

      <div className="results-bar">
        <p>{events.length} event{events.length === 1 ? "" : "s"} found</p>
      </div>

      <div className="grid">
        {events.length === 0 ? (
          <p className="empty">No events found for this filter combination. Try clearing one of the filters.</p>
        ) : (
          events.map((event) => <EventCard key={event.id} event={event} />)
        )}
      </div>
    </section>
  );
}
