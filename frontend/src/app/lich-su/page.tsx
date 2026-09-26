"use client";

import { useEffect, useState } from "react";

import { useRouter } from "next/navigation";

import { getArticleViewHistory } from "@/api/api";

import {
    formatDate,
    getThumbnailUrl,
    type DisplayArticle,
  } from "@/api/articles";

import NewsGridLayout from "@/components/news/NewsGridLayout";

// =========================================================
// HISTORY PAGE
// =========================================================

export default function HistoryPage() {
  const router = useRouter();

  // =======================================================
  // HISTORY ARTICLES
  // =======================================================

  const [historyArticles, setHistoryArticles] = useState<
    DisplayArticle[]
  >([]);

  // =======================================================
  // LOADING / ERROR
  // =======================================================

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // =======================================================
  // LOAD HISTORY
  // =======================================================

  useEffect(() => {
    let cancelled = false;

    async function loadHistory() {
      setLoading(true);
      setError(false);

      const token = localStorage.getItem("access_token");

      // -----------------------------------------------------
      // CHƯA ĐĂNG NHẬP
      // -----------------------------------------------------

      if (!token) {
        router.push("/");
        return;
      }

      try {
        const history = await getArticleViewHistory();

        if (cancelled) {
          return;
        }

        const displayArticles: DisplayArticle[] =
          history.map((article) => ({
            id: String(article.article_id),
            title: article.title,
            slug: article.slug,
            coverImage: getThumbnailUrl(article.thumbnail_url),
            categoryName:
              article.category_name ?? "",
            categorySlug:
              article.category_slug ?? "",
            publishedAt: formatDate(article.published_at),
            summary:
              article.summary ?? "",
            content: "",
          }));

        setHistoryArticles(displayArticles);
        setLoading(false);
      } catch (error) {
        console.error(
          "Không thể tải lịch sử xem:",
          error
        );

        if (!cancelled) {
          setError(true);
          setLoading(false);
        }
      }
    }

    loadHistory();

    return () => {
      cancelled = true;
    };
  }, [router]);

  // =======================================================
  // ARTICLE LINK
  // =======================================================

  const getArticleHref = (
    article: DisplayArticle
  ) => {
    return `/bai-viet/${encodeURIComponent(
      article.slug
    )}?id=${article.id}`;
  };

  // =======================================================
  // LOADING
  // =======================================================

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 font-sans transition-colors dark:bg-[#0B0F19]">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="border border-gray-200 bg-white p-8 text-center text-gray-500 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400">
            Đang tải lịch sử xem...
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
              Không thể tải lịch sử xem
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
      articles={historyArticles}
      getArticleHref={getArticleHref}
      title="Bản Tin Đã Xem"
    />
  );
}