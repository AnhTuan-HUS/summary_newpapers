"use client";

import { useEffect, useMemo, useState } from "react";

import { useRouter } from "next/navigation";

import {
  getArticles,
  getCategories,
  type Article,
  type Category,
} from "@/lib/api";

import { toDisplayArticles } from "@/lib/articles";

import NewsGridLayout from "@/components/news/NewsGridLayout";

// =========================================================
// HOME PAGE
// =========================================================

export default function Home() {
  const router = useRouter();

  // =======================================================
  // ARTICLES
  // =======================================================

  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // =======================================================
  // CATEGORIES
  // =======================================================

  const [categories, setCategories] = useState<Category[]>([]);

  // =======================================================
  // LOAD ARTICLES + CATEGORIES
  // =======================================================

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      setLoading(true);
      setError(false);

      try {
        const [articleData, categoryData] = await Promise.all([
          getArticles(),
          getCategories(),
        ]);

        if (cancelled) {
          return;
        }

        setArticles(articleData);
        setCategories(categoryData);
        setLoading(false);
      } catch (error) {
        console.error("Không thể lấy dữ liệu:", error);

        if (!cancelled) {
          setError(true);
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      cancelled = true;
    };
  }, []);

  // =======================================================
  // CONVERT ARTICLE
  // =======================================================

  const newsArticles = useMemo(
    () => toDisplayArticles(articles),
    [articles]
  );

  // =======================================================
  // CHỌN CATEGORY
  // =======================================================

  const handleCategorySelect = (slug: string) => {
    // "Tất cả"
    if (!slug) {
      router.push("/");
      return;
    }

    // Đi tới trang chuyên mục
    router.push(`/chuyen-muc/${slug}`);
  };

  // =======================================================
  // LINK ARTICLE
  // =======================================================

  const getArticleHref = (
    article: (typeof newsArticles)[number]
  ) => {
    return `/bai-viet/${encodeURIComponent(article.slug)}?id=${article.id}`;
  };

  // =======================================================
  // LOADING
  // =======================================================

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 font-sans transition-colors dark:bg-[#0B0F19]">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="border border-gray-200 bg-white p-8 text-center text-gray-500 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400">
            Đang tải bản tin...
          </div>
        </div>
      </div>
    );
  }

  // =======================================================
  // API ERROR
  // =======================================================

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 font-sans transition-colors dark:bg-[#0B0F19]">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="border border-gray-200 bg-white p-8 dark:border-gray-800 dark:bg-gray-900">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Không thể tải dữ liệu
            </h1>

            <p className="mt-2 text-gray-500 dark:text-gray-400">
              Không thể kết nối tới hệ thống dữ liệu
              của Tech Việt.
            </p>

            <button
              type="button"
              onClick={() => window.location.reload()}
              className="mt-6 text-sm font-semibold text-red-600 hover:text-red-700"
            >
              ← Tải lại trang
            </button>
          </div>
        </div>
      </div>
    );
  }

  // =======================================================
  // UI
  // =======================================================

  return (
    <NewsGridLayout
      articles={newsArticles}
      getArticleHref={getArticleHref}
    />
  );
}