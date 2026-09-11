export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string;
}

export interface Article {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  coverImage: string;
  categoryId: string;
  author: string;
  publishedAt: string;
  views: number;
  isHero: boolean;
  isSpotlight: boolean;
  tags: string[];
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
