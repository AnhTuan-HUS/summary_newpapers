"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";

import { getArticle, getArticles } from "@/api/api";
import {
  toDisplayArticles,
  type DisplayArticle,
} from "@/api/articles";

import NewsReaderLayout from "@/components/news/NewsReaderLayout";

// =========================================================
// ARTICLE PAGE
// =========================================================

export default function ArticlePage() {
  const params = useParams<{ slug: string }>();
  const searchParams = useSearchParams();

  // =======================================================
  // ARTICLE SLUG
  // =======================================================

  const articleSlug = Array.isArray(params.slug)
    ? params.slug[0]
    : params.slug;

  // =======================================================
  // ARTICLE ID
  // =======================================================

  const articleId = searchParams.get("id");

  // =======================================================
  // ARTICLES
  // =======================================================

  const [newsArticles, setNewsArticles] = useState<
    DisplayArticle[]
  >([]);

  const [selectedArticle, setSelectedArticle] =
    useState<DisplayArticle | null>(null);

  // =======================================================
  // LOADING / ERROR
  // =======================================================

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // =======================================================
  // LOAD ARTICLE
  // =======================================================

  useEffect(() => {
    if (!articleSlug) {
      return;
    }

    let cancelled = false;

    async function loadArticlePage() {
      setLoading(true);
      setError(false);

      try {
        // ===================================================
        // 1. LẤY DANH SÁCH BÀI
        // ===================================================

        const articlesResponse = await getArticles();

        if (cancelled) {
          return;
        }

        const articles =
          toDisplayArticles(articlesResponse);

        setNewsArticles(articles);

        // ===================================================
        // 2. NẾU CÓ ID -> LẤY TRỰC TIẾP TỪ BACKEND
        // ===================================================

        if (articleId) {
          const id = Number(articleId);

          if (Number.isNaN(id)) {
            setError(true);
            setSelectedArticle(null);
            return;
          }

          const articleDetail = await getArticle(id);

          if (cancelled) {
            return;
          }

          // -------------------------------------------------
          // Chuyển article detail thành DisplayArticle
          // -------------------------------------------------

          const displayArticles =
            toDisplayArticles([articleDetail]);

          const displayArticle = displayArticles[0];

          if (!displayArticle) {
            setError(true);
            setSelectedArticle(null);
            return;
          }

          setSelectedArticle(displayArticle);

          return;
        }

        // ===================================================
        // 3. FALLBACK CHO URL CŨ KHÔNG CÓ ?id=
        // ===================================================

        const article = articles.find(
          (item) => item.slug === articleSlug
        );

        if (!article) {
          setError(true);
          setSelectedArticle(null);
          return;
        }

        const articleDetail = await getArticle(article.id);

        if (cancelled) {
          return;
        }

        const displayArticle: DisplayArticle = {
          ...article,
          content: articleDetail.content ?? "",
        };

        setSelectedArticle(displayArticle);
      } catch (error) {
        if (cancelled) {
          return;
        }

        console.error(
          "Không thể tải bài viết:",
          error
        );

        setError(true);
        setSelectedArticle(null);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadArticlePage();

    return () => {
      cancelled = true;
    };
  }, [articleSlug, articleId]);

  // =======================================================
  // LOADING
  // =======================================================

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 font-sans dark:bg-[#0B0F19]">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="border border-gray-200 bg-white p-8 text-center text-gray-500 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400">
            Đang tải bài viết...
          </div>
        </div>
      </div>
    );
  }

  // =======================================================
  // ERROR
  // =======================================================

  if (error || !selectedArticle) {
    return (
      <div className="min-h-screen bg-gray-50 font-sans dark:bg-[#0B0F19]">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="border border-gray-200 bg-white p-8 dark:border-gray-800 dark:bg-gray-900">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Không tìm thấy bài viết
            </h1>

            <p className="mt-2 text-gray-500 dark:text-gray-400">
              Bài viết bạn đang truy cập không tồn tại
              hoặc không thể tải dữ liệu.
            </p>

            <Link
              href="/"
              className="mt-6 inline-block text-sm font-semibold text-red-600 hover:text-red-700"
            >
              ← Về trang chủ
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // =======================================================
  // ARTICLE READER
  // =======================================================

  return (
    <NewsReaderLayout
      newsArticles={newsArticles}
      selectedArticle={selectedArticle}
    />
  );
}