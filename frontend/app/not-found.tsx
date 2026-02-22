import Link from "next/link";

export default function NotFound() {
  return (
    <section>
      <h1>Event not found</h1>
      <p>We could not find the event you requested.</p>
      <Link href="/">Return to homepage</Link>
    </section>
  );
}
