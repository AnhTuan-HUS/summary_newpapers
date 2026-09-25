import type { Article } from "@/lib/api";

export type DisplayArticle = {
  id: string;
  title: string;
  summary: string | null;
  slug: string;
  content: string;
  coverImage: string;
  publishedAt: string;
  categoryName: string;
  categorySlug: string;
};

function isHttpUrl(value: string): boolean {
  return (
    value.startsWith("http://") ||
    value.startsWith("https://")
  );
}

export function getThumbnailUrl(thumbnail: unknown): string {
  if (!thumbnail) {
    return "";
  }

  // thumbnail_url là string
  if (typeof thumbnail === "string") {
    const trimmed = thumbnail.trim();

    if (!trimmed) {
      return "";
    }

    // Có thể backend/database lưu JSON dưới dạng string
    if (
      trimmed.startsWith("{") ||
      trimmed.startsWith("[")
    ) {
      try {
        return getThumbnailUrl(JSON.parse(trimmed));
      } catch {
        return trimmed;
      }
    }

    return trimmed;
  }

  // thumbnail_url là array
  if (Array.isArray(thumbnail)) {
    if (thumbnail.length === 0) {
      return "";
    }

    return getThumbnailUrl(thumbnail[0]);
  }

  // thumbnail_url là object
  if (typeof thumbnail === "object") {
    const record = thumbnail as Record<string, unknown>;

    // Các key thường gặp
    for (const key of [
      "url",
      "src",
      "original",
      "thumbnail",
    ]) {
      const value = record[key];

      if (
        typeof value === "string" &&
        value.trim()
      ) {
        return value.trim();
      }
    }

    const entries = Object.entries(record);

    if (entries.length === 0) {
      return "";
    }

    const [firstKey, firstValue] = entries[0];

    // Ví dụ:
    // {
    //   "https://example.com/image.jpg": {...}
    // }
    if (isHttpUrl(firstKey)) {
      return firstKey;
    }

    // Ví dụ:
    // {
    //   image: "https://example.com/image.jpg"
    // }
    if (
      typeof firstValue === "string" &&
      isHttpUrl(firstValue)
    ) {
      return firstValue;
    }
  }

  return "";
}

export function formatDate(
  date: string | null
): string {
  if (!date) {
    return "Chưa có thời gian";
  }

  const parsedDate = new Date(date);

  if (Number.isNaN(parsedDate.getTime())) {
    return date;
  }

  return new Intl.DateTimeFormat("vi-VN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(parsedDate);
}

export function mapArticle(
  article: Article
): DisplayArticle {
  return {
    id: String(article.id),

    title: article.title,
    summary: article.summary,

    slug: article.slug ?? String(article.id),

    content: article.content ?? "",

    coverImage: getThumbnailUrl(
      article.thumbnail_url
    ),

    publishedAt: formatDate(
      article.published_at
    ),

    categoryName:
      article.category?.name ?? "Công nghệ",

    categorySlug:
      article.category?.slug ?? "",
  };
}

export function toDisplayArticles(
  articles: Article[]
): DisplayArticle[] {
  return articles
    .slice()
    .sort((a, b) => {
      const dateA = a.published_at
        ? new Date(a.published_at).getTime()
        : 0;

      const dateB = b.published_at
        ? new Date(b.published_at).getTime()
        : 0;

      return dateB - dateA;
    })
    .map(mapArticle);
}