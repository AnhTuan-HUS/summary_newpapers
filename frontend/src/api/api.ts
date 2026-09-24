export type Category = {
  id: number;
  name: string;
  slug: string | null;
  article_count?: number | null;
};

export type ArticleCategory = {
  id: number;
  name: string;
  slug: string | null;
};

export type Article = {
  id: number;
  title: string;
  slug: string | null;
  content: string | null;
  thumbnail_url: unknown;
  summary: string | null;
  key_points: unknown;
  why_it_matters: string | null;
  importance_score: number | null;
  status: string | null;
  published_at: string | null;
  created_at: string | null;
  updated_at?: string | null;
  category: ArticleCategory | null;
};

export type PaginatedArticlesResponse = {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: Article[];
};

function getApiBaseUrl(): string {
  const baseUrl =
    process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:18080";

  return baseUrl.replace(/\/+$/, "");
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      `API ${path} thất bại: ${response.status} ${response.statusText}`
    );
  }

  return response.json() as Promise<T>;
}

/**
 * Lấy danh sách bài viết.
 *
 * Backend:
 * GET /api/v1/articles
 *
 * Query:
 * - page
 * - page_size
 * - category_id
 * - category_slug
 * - status
 */
export async function getArticles(
  limit = 20
): Promise<Article[]> {
  const response = await request<PaginatedArticlesResponse>(
    `/api/v1/articles?page=1&page_size=${limit}`
  );

  return response.items;
}

/**
 * Lấy thông tin chi tiết bài viết.
 *
 * Backend:
 * GET /api/v1/articles/{article_id}
 */
export async function getArticle(
  articleIdentifier: string | number
): Promise<Article> {
  const identifier = String(articleIdentifier);

  // Nếu là ID số -> gọi trực tiếp backend
  if (/^\d+$/.test(identifier)) {
    return request<Article>(
      `/api/v1/articles/${encodeURIComponent(identifier)}`
    );
  }

  // Nếu frontend dùng slug:
  // tìm bài viết trong danh sách
  const response = await request<PaginatedArticlesResponse>(
    `/api/v1/articles?page=1&page_size=50`
  );

  const article = response.items.find(
    (item) => item.slug === identifier
  );

  if (!article) {
    throw new Error(
      `Không tìm thấy bài viết với slug: ${identifier}`
    );
  }

  // Sau khi tìm được ID -> lấy API detail đầy đủ
  return request<Article>(
    `/api/v1/articles/${encodeURIComponent(String(article.id))}`
  );
}

/**
 * Lấy danh sách categories.
 *
 * Backend:
 * GET /api/v1/categories
 */
let categoriesPromise: Promise<Category[]> | null = null;

export async function getCategories(): Promise<Category[]> {
  if (!categoriesPromise) {
    categoriesPromise = request<Category[]>(
      "/api/v1/categories"
    ).catch((error) => {
      categoriesPromise = null;
      throw error;
    });
  }

  return categoriesPromise;
}

/**
 * Lấy bài viết theo category.
 *
 * Backend:
 * GET /api/v1/articles?category_slug=...
 */
export async function getArticlesByCategory(
  categorySlug: string,
  limit = 20
): Promise<Article[]> {
  const response = await request<PaginatedArticlesResponse>(
    `/api/v1/articles?category_slug=${encodeURIComponent(
      categorySlug
    )}&page=1&page_size=${limit}`
  );

  return response.items;
}