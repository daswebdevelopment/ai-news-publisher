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

  const activeFilters = [category, location].filter(Boolean).length;

  return (
    <section className="page">
      <header className="hero">
        <div className="hero-content">
          <p className="eyebrow">AI News Publisher</p>
          <h1>Discover the latest AI stories that matter</h1>
          <p className="intro">
            From model launches to policy shifts, track high-impact updates across global AI hubs in one curated stream.
          </p>
        </div>

        <div className="hero-stats" aria-label="Overview metrics">
          <div className="stat-card">
            <span className="stat-value">{events.length}</span>
            <span className="stat-label">Stories today</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{activeFilters}</span>
            <span className="stat-label">Active filters</span>
          </div>
        </div>
      </header>

      <Filters category={category} location={location} />

      <div className="results-bar">
        <p>
          Showing <strong>{events.length}</strong> event{events.length === 1 ? "" : "s"}
          {activeFilters > 0 ? " for your selected filters" : " across all categories"}.
        </p>
      </div>

      <div className="grid">
        {events.length === 0 ? (
          <p className="empty">No events match this combination yet. Try resetting filters to explore everything.</p>
        ) : (
          events.map((event) => <EventCard key={event.id} event={event} />)
        )}
      </div>
    </section>
  );
}
