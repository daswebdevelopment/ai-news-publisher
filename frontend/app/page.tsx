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
    <section>
      <h1>Latest AI News Events</h1>
      <p className="intro">Server-rendered feed with category and location filters.</p>
      <Filters category={category} location={location} />

      <div className="grid">
        {events.length === 0 ? (
          <p>No events found for this filter combination.</p>
        ) : (
          events.map((event) => <EventCard key={event.id} event={event} />)
        )}
      </div>
    </section>
  );
}
