"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import {
  getArticlesByCategory,
  getCategories,
  type Article,
  type Category,
} from "@/api/api";

import { toDisplayArticles } from "@/api/articles";
import NewsGridLayout from "@/components/news/NewsGridLayout";

// =========================================================
// CATEGORY PAGE CONTENT
// =========================================================

function CategoryPageContent() {
  const params = useParams<{ slug: string }>();

  // =======================================================
  // CATEGORY SLUG
  // =======================================================

  const categorySlug = Array.isArray(params.slug)
    ? params.slug[0]
    : params.slug;

  // =======================================================
  // CATEGORIES
  // =======================================================

  const [categories, setCategories] = useState<Category[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState(true);
  const [categoriesError, setCategoriesError] = useState(false);

  // =======================================================
  // ARTICLES
  // =======================================================

  const [articles, setArticles] = useState<Article[]>([]);
  const [articlesLoading, setArticlesLoading] = useState(true);
  const [articlesError, setArticlesError] = useState(false);

  // =======================================================
  // LOAD CATEGORY + ARTICLES
  // =======================================================

  useEffect(() => {
    const slug = categorySlug;

    if (!slug) {
      return;
    }

    let cancelled = false;

    async function loadData() {
      setCategoriesLoading(true);
      setArticlesLoading(true);

      setCategoriesError(false);
      setArticlesError(false);

      const [categoryResult, articleResult] =
        await Promise.allSettled([
          getCategories(),
          getArticlesByCategory(slug),
        ]);

      if (cancelled) {
        return;
      }

      // ---------------------------------------------------
      // CATEGORY RESULT
      // ---------------------------------------------------

      if (categoryResult.status === "fulfilled") {
        setCategories(categoryResult.value);
        setCategoriesLoading(false);
      } else {
        console.error(
          "Không thể lấy danh mục:",
          categoryResult.reason
        );

        setCategoriesError(true);
        setCategoriesLoading(false);
      }

      // ---------------------------------------------------
      // ARTICLE RESULT
      // ---------------------------------------------------

      if (articleResult.status === "fulfilled") {
        setArticles(articleResult.value);
        setArticlesLoading(false);
      } else {
        console.error(
          "Không thể lấy bài viết theo chuyên mục:",
          articleResult.reason
        );

        setArticlesError(true);
        setArticlesLoading(false);
      }
    }

    loadData();

    return () => {
      cancelled = true;
    };
  }, [categorySlug]);

  // =======================================================
  // CURRENT CATEGORY
  // =======================================================

  const category = useMemo(() => {
    return categories.find(
      (item) => item.slug === categorySlug
    );
  }, [categories, categorySlug]);

  // =======================================================
  // CONVERT ARTICLES
  // =======================================================

  const newsArticles = useMemo(
    () => toDisplayArticles(articles),
    [articles]
  );

  // =======================================================
  // LOADING
  // =======================================================

  if (categoriesLoading || articlesLoading) {
    return (
      <div className="min-h-screen bg-gray-50 font-sans dark:bg-[#0B0F19]">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="border border-gray-200 bg-white p-8 text-center text-gray-500 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400">
            Đang tải bản tin...
          </div>
        </div>
      </div>
    );
  }

  // =======================================================
  // ERROR
  // =======================================================

  if (categoriesError || articlesError) {
    return (
      <div className="min-h-screen bg-gray-50 font-sans dark:bg-[#0B0F19]">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="border border-gray-200 bg-white p-8 dark:border-gray-800 dark:bg-gray-900">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Không thể tải dữ liệu
            </h1>

            <p className="mt-2 text-gray-500 dark:text-gray-400">
              Không thể kết nối tới hệ thống dữ liệu
              của Tech Việt.
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
  // CATEGORY NOT FOUND
  // =======================================================

  if (!category) {
    return (
      <div className="min-h-screen bg-gray-50 font-sans dark:bg-[#0B0F19]">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="border border-gray-200 bg-white p-8 dark:border-gray-800 dark:bg-gray-900">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Không tìm thấy chuyên mục
            </h1>

            <p className="mt-2 text-gray-500 dark:text-gray-400">
              Chuyên mục bạn đang truy cập không tồn tại.
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
  // UI
  // =======================================================

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900 dark:bg-[#0B0F19] dark:text-gray-100">
      <NewsGridLayout
        articles={newsArticles}
        getArticleHref={(article) =>
          `/bai-viet/${encodeURIComponent(article.slug)}?id=${article.id}`
        }
      />
    </div>
  );
}

// =========================================================
// PAGE
// =========================================================

export default function CategoryPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 font-sans dark:bg-[#0B0F19]">
          <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            <div className="border border-gray-200 bg-white p-8 text-center text-gray-500 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400">
              Đang tải bản tin...
            </div>
          </div>
        </div>
      }
    >
      <CategoryPageContent />
    </Suspense>
  );
}