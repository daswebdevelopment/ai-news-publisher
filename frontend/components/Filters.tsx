import Link from "next/link";

export function Filters({
  category,
  location
}: {
  category?: string;
  location?: string;
}) {
  return (
    <form className="filters" action="/" method="get">
      <label>
        Category
        <select name="category" defaultValue={category ?? ""}>
          <option value="">All</option>
          <option value="product">Product</option>
          <option value="research">Research</option>
          <option value="policy">Policy</option>
        </select>
      </label>

      <label>
        Location
        <select name="location" defaultValue={location ?? ""}>
          <option value="">All</option>
          <option value="global">Global</option>
          <option value="berlin">Berlin</option>
          <option value="san-francisco">San Francisco</option>
        </select>
      </label>

      <div className="filter-actions">
        <button type="submit">Apply filters</button>
        <Link className="ghost-btn" href="/">
          Reset
        </Link>
      </div>
    </form>
  );
}
