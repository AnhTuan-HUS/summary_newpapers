export interface Category {
  id: number | string;
  name: string;
  slug?: string | null;
  article_count?: number | null;
  description?: string;
}

export interface ArticleCategory {
  id: number;
  name: string;
  slug?: string | null;
}

export interface ApiArticleItem {
  id: number;
  title: string;
  slug?: string | null;
  summary?: string | null;
  thumbnail_url?: any;
  importance_score?: number | null;
  status?: string | null;
  published_at?: string | null;
  created_at?: string | null;
  category?: ArticleCategory | null;
}

export interface ApiArticleDetail extends ApiArticleItem {
  content?: string | null;
  key_points?: any;
  why_it_matters?: string | null;
  updated_at?: string | null;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: T[];
}

export interface Article {
  id: string;
  numericId?: number;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  coverImage: string;
  categoryId: string;
  categoryName?: string;
  categorySlug?: string;
  author: string;
  publishedAt: string;
  views: number;
  importanceScore?: number;
  isHero: boolean;
  isSpotlight: boolean;
  tags: string[];
  keyPoints?: string[];
  whyItMatters?: string;
}

export interface NewsletterSub {
  id: string;
  email: string;
  name: string;
  subscribedAt: string;
  isActive: boolean;
}

export interface MenuItem {
  id: string;
  label: string;
  href: string;
}
