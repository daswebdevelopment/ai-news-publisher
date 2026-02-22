# Frontend (Next.js)

Minimal Next.js frontend for published news events.

## Features

- SSR homepage with latest events
- Event detail page
- Filter by category and location
- Mobile-first responsive layout
- API integration via `/api/events` endpoints (or external API via `NEWS_API_BASE_URL`)

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Then open <http://localhost:3000>.

## Deployment

This project is deploy-ready for Vercel/Node hosting using standard Next.js build/start commands:

```bash
npm run build
npm run start
```
