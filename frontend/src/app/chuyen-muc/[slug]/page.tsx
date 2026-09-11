"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { Bookmark, Clock, Eye } from "lucide-react";
import { useParams, useSearchParams } from "next/navigation";
import Link from "next/link";

import {
  articles,
  categories,
  getCategoryById,
  mostViewedArticles,
} from "@/data/mockData";

function CategoryPageContent() {
  const params = useParams<{ slug: string }>();
  const searchParams = useSearchParams();

  // =========================
  // CATEGORY
  // =========================

  const category = useMemo(() => {
    return categories.find((item) => item.slug === params.slug);
  }, [params.slug]);

  // =========================
  // ARTICLES IN CATEGORY
  // =========================

  const newsArticles = useMemo(() => {
    if (!category) return [];

    return [...articles]
      .filter((article) => article.categoryId === category.id)
      .sort(
        (a, b) =>
          new Date(b.publishedAt).getTime() -
          new Date(a.publishedAt).getTime()
      );
  }, [category]);

  // =========================
  // ARTICLE FROM URL
  // =========================

  const articleParam = searchParams.get("article");

  const articleFromUrl = useMemo(() => {
    if (!articleParam) return undefined;

    return newsArticles.find((article) => article.id === articleParam);
  }, [articleParam, newsArticles]);

  // =========================
  // SELECTED ARTICLE
  // =========================

  const [selectedArticleId, setSelectedArticleId] = useState("");

  useEffect(() => {
    if (articleFromUrl) {
      setSelectedArticleId(articleFromUrl.id);
      return;
    }

    setSelectedArticleId(newsArticles[0]?.id ?? "");
  }, [articleFromUrl, newsArticles]);

  const selectedArticle =
    newsArticles.find((article) => article.id === selectedArticleId) ??
    newsArticles[0];

  const selectedIndex = selectedArticle
    ? newsArticles.findIndex((article) => article.id === selectedArticle.id)
    : -1;

  const selectedNumber = selectedIndex + 1;

  // =========================
  // CATEGORY NOT FOUND
  // =========================

  if (!category) {
    return (
      <div className="min-h-screen bg-gray-50 font-sans">
        <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="border border-gray-200 bg-white p-8">
            <h1 className="text-2xl font-bold text-gray-900">
              Không tìm thấy chuyên mục
            </h1>

            <p className="mt-2 text-gray-500">
              Chuyên mục bạn đang truy cập không tồn tại.
            </p>

            <Link
              href="/"
              className="mt-6 inline-block text-sm font-semibold text-red-600 hover:text-red-700"
            >
              ← Về trang chủ
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* ========================================================= */}
        {/* MAIN CONTENT                                             */}
        {/* ========================================================= */}

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-[minmax(0,1fr)_360px]">
          {/* ===================================================== */}
          {/* LEFT - ARTICLE                                        */}
          {/* ===================================================== */}

          <section>
            <div className="mb-5 border-b border-gray-200 pb-4">
              <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-red-600">
                {category.name}
              </div>

              <h1 className="text-xl font-bold tracking-tight text-gray-900">
                BẢN TIN{" "}
                {selectedArticle
                  ? String(selectedNumber).padStart(2, "0")
                  : "01"}
              </h1>
            </div>

            {selectedArticle ? (
              <article className="overflow-hidden border border-gray-200 bg-white">
                {/* COVER IMAGE */}

                <div className="relative">
                  <img
                    src={selectedArticle.coverImage}
                    alt={selectedArticle.title}
                    className="h-[320px] w-full object-cover sm:h-[400px]"
                  />

                  <div className="absolute left-4 top-4 bg-red-600 px-3 py-1.5 text-sm font-bold text-white">
                    {String(selectedNumber).padStart(2, "0")}
                  </div>
                </div>

                {/* ARTICLE HEADER */}

                <div className="p-6 sm:p-8">
                  <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                    <span className="font-semibold text-red-600">
                      {category.name}
                    </span>

                    <span className="h-1 w-1 rounded-full bg-gray-300" />

                    <span className="flex items-center gap-1">
                      <Clock className="h-3.5 w-3.5" />

                      {new Date(
                        selectedArticle.publishedAt
                      ).toLocaleString("vi-VN", {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>

                  <h2 className="mt-4 text-2xl font-bold leading-tight tracking-tight text-gray-900 sm:text-3xl">
                    {selectedArticle.title}
                  </h2>

                  <p className="mt-4 text-base leading-7 text-gray-600">
                    {selectedArticle.excerpt}
                  </p>

                  <div className="mt-6 flex items-center justify-between border-t border-gray-100 pt-5">
                    <div>
                      <div className="text-xs text-gray-400">
                        Tác giả
                      </div>

                      <div className="mt-1 text-sm font-semibold text-gray-900">
                        {selectedArticle.author}
                      </div>
                    </div>

                    <button
                      type="button"
                      className="flex h-9 w-9 items-center justify-center border border-gray-200 text-gray-500 transition hover:border-red-200 hover:text-red-600"
                      aria-label="Lưu bài viết"
                    >
                      <Bookmark className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* ARTICLE CONTENT */}

                <div className="border-t border-gray-100 px-6 py-6 sm:px-8 sm:py-8">
                  <div className="max-w-none">
                    {selectedArticle.content
                      .split("\n")
                      .filter((paragraph) => paragraph.trim().length > 0)
                      .map((paragraph, index) => (
                        <p
                          key={`${selectedArticle.id}-${index}`}
                          className="mb-5 text-base leading-8 text-gray-700 last:mb-0"
                        >
                          {paragraph}
                        </p>
                      ))}
                  </div>
                </div>
              </article>
            ) : (
              <div className="border border-gray-200 bg-white p-8">
                <p className="text-gray-500">
                  Chưa có bài viết trong chuyên mục này.
                </p>
              </div>
            )}
          </section>

          {/* ===================================================== */}
          {/* RIGHT - ALL NEWS                                      */}
          {/* ===================================================== */}

          <aside className="lg:sticky lg:top-8 lg:self-start">
            <div className="mb-5 border-b border-gray-200 pb-4">
              <h2 className="text-xl font-bold tracking-tight text-gray-900">
                TẤT CẢ BẢN TIN
              </h2>
            </div>

            <div className="border border-gray-200 bg-white">
              {newsArticles.length > 0 ? (
                newsArticles.map((article, index) => {
                  const isSelected =
                    article.id === selectedArticle?.id;

                  return (
                    <button
                      key={article.id}
                      type="button"
                      onClick={() => setSelectedArticleId(article.id)}
                      className={`flex w-full gap-3 border-b border-gray-100 p-4 text-left transition last:border-b-0 ${
                        isSelected
                          ? "bg-gray-100"
                          : "bg-white hover:bg-gray-50"
                      }`}
                    >
                      {/* NUMBER */}

                      <div
                        className={`flex h-7 w-7 shrink-0 items-center justify-center text-xs font-bold ${
                          isSelected
                            ? "bg-red-600 text-white"
                            : "bg-gray-100 text-gray-500"
                        }`}
                      >
                        {String(index + 1).padStart(2, "0")}
                      </div>

                      {/* IMAGE */}

                      <div className="h-20 w-24 shrink-0 overflow-hidden">
                        <img
                          src={article.coverImage}
                          alt={article.title}
                          className="h-full w-full object-cover"
                        />
                      </div>

                      {/* INFO */}

                      <div className="min-w-0 flex-1">
                        <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-red-600">
                          {getCategoryById(article.categoryId)?.name ??
                            "Công nghệ"}
                        </div>

                        <h3 className="line-clamp-3 text-sm font-semibold leading-5 text-gray-900">
                          {article.title}
                        </h3>

                        <div className="mt-2 text-xs text-gray-400">
                          {new Date(
                            article.publishedAt
                          ).toLocaleDateString("vi-VN")}
                        </div>
                      </div>
                    </button>
                  );
                })
              ) : (
                <div className="p-6 text-sm text-gray-500">
                  Chưa có bản tin trong chuyên mục này.
                </div>
              )}
            </div>
          </aside>
        </div>

        {/* ========================================================= */}
        {/* ĐƯỢC QUAN TÂM                                           */}
        {/* ========================================================= */}

        <section className="mt-14 border-t border-gray-200 pt-8">
          <div className="mb-5">
            <h2 className="text-xl font-bold tracking-tight text-gray-900">
              ĐƯỢC QUAN TÂM
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5">
            {mostViewedArticles.map((article, index) => {
              const articleCategory = getCategoryById(
                article.categoryId
              );

              if (!articleCategory) return null;

              return (
                <Link
                  key={article.id}
                  href={`/chuyen-muc/${
                    articleCategory.slug
                  }?article=${encodeURIComponent(article.id)}`}
                  className="group border-b border-gray-200 py-5 first:pt-0 sm:px-4 sm:first:pl-0 lg:border-b-0 lg:border-r lg:py-0 lg:first:pl-0 lg:last:border-r-0"
                >
                  {/* IMAGE */}

                  <div className="relative mb-3 overflow-hidden">
                    <img
                      src={article.coverImage}
                      alt={article.title}
                      className="h-40 w-full object-cover transition-transform duration-300 group-hover:scale-105"
                    />

                    <span className="absolute left-3 top-3 bg-red-600 px-2 py-1 text-xs font-bold text-white">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                  </div>

                  {/* VIEWS */}

                  <div className="mb-2 flex items-center gap-1 text-xs text-gray-500">
                    <Eye className="h-3.5 w-3.5" />

                    {article.views.toLocaleString()}
                  </div>

                  {/* TITLE */}

                  <h3 className="line-clamp-3 text-sm font-semibold leading-5 text-gray-900 transition-colors group-hover:text-red-600">
                    {article.title}
                  </h3>
                </Link>
              );
            })}
          </div>
        </section>
      </main>
    </div>
  );
}

export default function CategoryPage() {
  return (
    <Suspense fallback={null}>
      <CategoryPageContent />
    </Suspense>
  );
}