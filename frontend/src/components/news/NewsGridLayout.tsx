"use client";

import { useState } from "react";
import Link from "next/link";

import type { DisplayArticle } from "@/lib/articles";

type NewsGridLayoutProps = {
  articles: DisplayArticle[];
  getArticleHref: (article: DisplayArticle) => string;
};

const ARTICLES_PER_PAGE = 18;

export default function NewsGridLayout({
  articles,
  getArticleHref,
}: NewsGridLayoutProps) {
  const [visibleCount, setVisibleCount] = useState(ARTICLES_PER_PAGE);

  const visibleArticles = articles.slice(0, visibleCount);

  const hasMoreArticles = visibleCount < articles.length;

  const handleLoadMore = () => {
    setVisibleCount((current) => current + ARTICLES_PER_PAGE);
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900 transition-colors dark:bg-[#0B0F19] dark:text-gray-100">
      <div className="mx-auto max-w-[1800px] px-4 py-6 sm:px-6 lg:px-8">

        {articles.length > 0 ? (
          <section>

            {/* ================================
                SECTION HEADER
            ================================= */}

            <div className="mb-6 flex items-center gap-3 border-b border-gray-200 pb-3 dark:border-gray-800">
              <div className="h-5 w-1 bg-red-600" />

              <h1 className="text-sm font-bold uppercase tracking-wider text-gray-900 dark:text-gray-100">
                Bản tin mới nhất
              </h1>
            </div>

            {/* ================================
                NEWS GRID
                6 BÀI / HÀNG
            ================================= */}

            <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 lg:grid-cols-6 lg:gap-x-5 lg:gap-y-10">

              {visibleArticles.map((article) => (
                <Link
                  key={article.id}
                  href={getArticleHref(article)}
                  className="group block min-w-0"
                >
                  <article>

                    {/* ==========================
                        COVER IMAGE
                    =========================== */}

                    <div className="relative aspect-video overflow-hidden rounded-lg bg-gray-200 dark:bg-[#272727]">

                      {article.coverImage ? (
                        <img
                          src={article.coverImage}
                          alt={article.title}
                          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.04]"
                        />
                      ) : (
                        <div className="flex h-full w-full items-center justify-center text-xs text-gray-500 dark:text-gray-400">
                          Không có ảnh
                        </div>
                      )}

                    </div>

                    {/* ==========================
                        ARTICLE INFO
                    =========================== */}

                    <div className="mt-3">

                      {/* CATEGORY */}

                      <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-red-600">
                        {article.categoryName}
                      </div>

                      {/* TITLE */}

                      <h2 className="line-clamp-2 text-sm font-semibold leading-5 text-gray-900 transition-colors group-hover:text-red-600 dark:text-gray-100 dark:group-hover:text-red-500">
                        {article.title}
                      </h2>

                      {/* DATE */}

                      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                        {article.publishedAt}
                      </div>

                    </div>

                  </article>
                </Link>
              ))}

            </div>

            {/* ================================
                LOAD MORE
            ================================= */}

            {hasMoreArticles && (
              <div className="mt-12 flex justify-center">

                <button
                  type="button"
                  onClick={handleLoadMore}
                  className="rounded-lg border border-gray-300 bg-white px-8 py-3 text-sm font-semibold text-gray-900 transition-colors hover:bg-gray-100 dark:border-gray-700 dark:bg-[#151A24] dark:text-gray-100 dark:hover:bg-[#202632]"
                >
                  Xem thêm
                </button>

              </div>
            )}

          </section>
        ) : (

          /* ================================
             EMPTY STATE
          ================================= */

          <div className="flex min-h-[300px] items-center justify-center rounded-xl bg-gray-100 dark:bg-[#181818]">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Chưa có bài viết.
            </p>
          </div>

        )}

      </div>
    </div>
  );
}