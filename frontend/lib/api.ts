import { NewsEvent } from "@/types/event";

type FetchEventsOptions = {
  category?: string;
  location?: string;
};

function withBase(path: string): string {
  const base = process.env.NEXT_PUBLIC_SITE_URL;
  if (!base) {
    return path;
  }
  return `${base}${path}`;
}

export async function fetchEvents(options: FetchEventsOptions = {}): Promise<NewsEvent[]> {
  const params = new URLSearchParams();
  if (options.category) params.set("category", options.category);
  if (options.location) params.set("location", options.location);

  const suffix = params.toString() ? `?${params.toString()}` : "";
  const response = await fetch(withBase(`/api/events${suffix}`), {
    next: { revalidate: 300 }
  });

  if (!response.ok) {
    return [];
  }

  return (await response.json()) as NewsEvent[];
}

export async function fetchEventById(id: string): Promise<NewsEvent | null> {
  const response = await fetch(withBase(`/api/events/${id}`), {
    next: { revalidate: 300 }
  });

  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    return null;
  }

  return (await response.json()) as NewsEvent;
}
