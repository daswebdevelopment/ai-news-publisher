import { NewsEvent } from "@/types/event";

export const events: NewsEvent[] = [
  {
    id: "event-1",
    title: "AI chip supply chain pressure increases across cloud providers",
    summary:
      "Major cloud platforms sign multi-year contracts to secure next-generation AI accelerator capacity.",
    content:
      "Cloud providers are rapidly expanding procurement agreements for high-performance AI chips. The shift may affect startup access, hardware pricing, and deployment timelines across global regions.",
    category: "product",
    location: "global",
    publishedAt: "2026-01-05T10:30:00Z"
  },
  {
    id: "event-2",
    title: "European regulators publish draft guidance for foundation model audits",
    summary:
      "Draft policy clarifies risk reporting and transparency expectations for model providers.",
    content:
      "The new draft guidance outlines disclosure requirements and operational controls for high-impact AI systems, with phased compliance windows for organizations shipping to EU markets.",
    category: "policy",
    location: "berlin",
    publishedAt: "2026-01-05T08:00:00Z"
  },
  {
    id: "event-3",
    title: "Research team demonstrates lower-cost multimodal training recipe",
    summary:
      "A new training approach reduces compute requirements while retaining benchmark performance.",
    content:
      "Researchers shared a reproducible method for multimodal model training that lowers total compute usage and improves run stability, potentially benefiting small teams with tighter budgets.",
    category: "research",
    location: "san-francisco",
    publishedAt: "2026-01-04T18:15:00Z"
  }
];
