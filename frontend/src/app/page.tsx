"use client";

import { useEffect, useMemo, useState } from "react";

import Link from "next/link";

import { Clock, Eye } from "lucide-react";

import { getArticles } from "@/lib/api";

// =========================================================
// KIỂU DỮ LIỆU ARTICLE TỪ API
// =========================================================
//
// Đây là dữ liệu FastAPI lấy từ PostgreSQL.
//
// thumbnail_url hiện tại trong API của bạn có thể là:
// JSON string chứa object:
// {
//   "URL_ẢNH": "MÔ_TẢ_ẢNH"
// }
//
// =========================================================

type ApiArticle = {
  id: number;
  title: string;
  slug: string;
  content: string | null;

  thumbnail_url:
    | string
    | {
        url?: string;
        src?: string;
        original?: string;
        thumbnail?: string;
      }
    | Array<
        | string
        | {
            url?: string;
            src?: string;
            original?: string;
            thumbnail?: string;
          }
      >
    | null;

  summary: string | null;
  key_points: string | null;
  why_it_matters: string | null;
  importance_score: number | null;

  status: string | null;
  published_at: string | null;
  created_at: string | null;

  category_id: number | null;
  category_name: string | null;
  category_slug: string | null;
};

// =========================================================
// DỮ LIỆU ARTICLE DÙNG CHO GIAO DIỆN
// =========================================================

type DisplayArticle = {
  id: string;
  title: string;
  slug: string;
  content: string;
  coverImage: string;
  publishedAt: string;
  categoryName: string;
  categorySlug: string;
};

// =========================================================
// LẤY URL ẢNH
// =========================================================
//
// thumbnail_url từ API hiện tại có dạng:
//
// "{\"https://...jpg\": \"Mô tả ảnh\"}"
//
// Vì vậy:
// 1. Nếu là string → thử JSON.parse()
// 2. Nếu parse thành object → lấy key đầu tiên
// 3. Key chính là URL ảnh
//
// =========================================================

function getThumbnailUrl(thumbnail: unknown): string {
  if (!thumbnail) {
    return "";
  }

  // PostgreSQL/FastAPI trả JSON object dưới dạng string
  if (typeof thumbnail === "string") {
    try {
      const parsed = JSON.parse(thumbnail);

      if (
        parsed &&
        typeof parsed === "object" &&
        !Array.isArray(parsed)
      ) {
        const entries = Object.entries(parsed);

        if (entries.length > 0) {
          return entries[0][0];
        }
      }
    } catch {
      // Nếu không phải JSON thì coi nó là URL bình thường
      return thumbnail;
    }

    return "";
  }

  // Trường hợp API trả object trực tiếp
  if (typeof thumbnail === "object") {
    if (Array.isArray(thumbnail)) {
      const firstItem = thumbnail[0];

      if (typeof firstItem === "string") {
        return firstItem;
      }

      if (
        firstItem &&
        typeof firstItem === "object" &&
        "url" in firstItem
      ) {
        return String(firstItem.url ?? "");
      }
    }

    const entries = Object.entries(thumbnail);

    if (entries.length > 0) {
      return entries[0][0];
    }
  }

  return "";
}

// =========================================================
// FORMAT NGÀY
// =========================================================

function formatDate(date: string | null): string {
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

// =========================================================
// CHUYỂN ARTICLE API
// → ARTICLE HIỂN THỊ
// =========================================================

function mapArticle(article: ApiArticle): DisplayArticle {
  return {
    id: String(article.id),

    title: article.title,

    slug: article.slug,

    content: article.content ?? "",

    coverImage: getThumbnailUrl(
      article.thumbnail_url
    ),

    publishedAt: formatDate(
      article.published_at
    ),

    categoryName:
      article.category_name ?? "Công nghệ",

    categorySlug:
      article.category_slug ?? "",
  };
}

// =========================================================
// HOME
// =========================================================

export default function Home() {
  // =======================================================
  // ARTICLES TỪ DATABASE
  // =======================================================

  const [articles, setArticles] = useState<ApiArticle[]>(
    []
  );

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(false);

  // =======================================================
  // LOAD ARTICLES
  // =======================================================
  //
  // Browser
  //    ↓
  // getArticles()
  //    ↓
  // FastAPI
  //    ↓
  // PostgreSQL
  //
  // =======================================================

  useEffect(() => {
    let cancelled = false;

    async function loadArticles() {
      setLoading(true);
      setError(false);

      try {
        const data = await getArticles();

        if (!cancelled) {
          setArticles(data);
          setLoading(false);
        }
      } catch (error) {
        console.error(
          "Không thể lấy bài viết:",
          error
        );

        if (!cancelled) {
          setError(true);
          setLoading(false);
        }
      }
    }

    loadArticles();

    return () => {
      cancelled = true;
    };
  }, []);

  // =========================================================
  // TẤT CẢ BÀI VIẾT
  // Mới nhất → cũ nhất
  // =========================================================

  const newsArticles = useMemo(() => {
    return articles
      .filter(
        (article) =>
          article.status === "published"
      )
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
  }, [articles]);

  // =========================================================
  // BÀI ĐANG ĐƯỢC CHỌN
  // Mặc định mở bài mới nhất
  // =========================================================

  const [selectedArticleId, setSelectedArticleId] =
    useState("");

  const selectedArticle =
    newsArticles.find(
      (article) =>
        article.id === selectedArticleId
    ) ?? newsArticles[0];

  // =========================================================
  // ĐANG TẢI
  // =========================================================

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 font-sans transition-colors dark:bg-[#0B0F19]">
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="border border-gray-200 bg-white p-8 text-center text-gray-500 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400">
            Đang tải bản tin...
          </div>
        </main>
      </div>
    );
  }

  // =========================================================
  // API LỖI
  // =========================================================

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 font-sans transition-colors dark:bg-[#0B0F19]">
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
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
              ← Tải lại trang
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 font-sans transition-colors dark:bg-[#0B0F19]">
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">

        {/* =====================================================
            MAIN CONTENT
        ===================================================== */}

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-[minmax(0,1fr)_360px]">

          {/* ===================================================
              CỘT TRÁI - BÀI ĐANG ĐỌC
          =================================================== */}

          <section>
            {selectedArticle ? (
              <article className="overflow-hidden border border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">

                {/* =================================================
                    THÔNG TIN + TIÊU ĐỀ + ẢNH
                ================================================= */}

                <div className="px-6 pb-8 pt-6 sm:px-8 sm:pb-8 sm:pt-7">

                  {/* Chuyên mục + thời gian */}

                  <div className="mb-4 flex flex-wrap items-center gap-3 text-xs">

                    <span className="font-semibold uppercase tracking-wide text-red-600">
                      {selectedArticle.categoryName}
                    </span>

                    <span className="text-gray-300 dark:text-gray-700">
                      •
                    </span>

                    <span className="flex items-center text-gray-400">
                      <Clock className="mr-1 h-3.5 w-3.5" />

                      {selectedArticle.publishedAt}
                    </span>

                  </div>

                  {/* Tiêu đề */}

                  <h1 className="text-2xl font-bold leading-tight tracking-tight text-gray-900 dark:text-gray-100 sm:text-3xl">
                    {selectedArticle.title}
                  </h1>

                  {/* Tác giả */}

                  <div className="mt-4 flex items-center gap-2 text-xs text-gray-400 dark:text-gray-500">
                    <span className="font-medium text-gray-600 dark:text-gray-300">
                      Tech Việt
                    </span>
                  </div>

                  {/* Ảnh bài viết */}

                  {selectedArticle.coverImage && (
                    <div className="mt-6 overflow-hidden">
                      <img
                        src={selectedArticle.coverImage}
                        alt={selectedArticle.title}
                        className="h-64 w-full object-cover sm:h-80 lg:h-[360px]"
                      />
                    </div>
                  )}

                </div>

                {/* =================================================
                    NỘI DUNG BÀI
                ================================================= */}

                <div className="border-t border-gray-100 px-6 py-6 dark:border-gray-800 sm:px-8 sm:py-8">

                  <div className="max-w-none">

                    {selectedArticle.content ? (
                      selectedArticle.content
                        .split("\n")
                        .filter(
                          (paragraph) =>
                            paragraph.trim() !== ""
                        )
                        .map(
                          (
                            paragraph,
                            index
                          ) => (
                            <p
                              key={`${selectedArticle.id}-${index}`}
                              className="mb-5 text-[15px] leading-8 text-gray-700 last:mb-0 dark:text-gray-300"
                            >
                              {paragraph}
                            </p>
                          )
                        )
                    ) : (
                      <p className="text-[15px] leading-8 text-gray-500 dark:text-gray-400">
                        Bài viết chưa có nội dung.
                      </p>
                    )}

                  </div>

                </div>

              </article>
            ) : (
              <div className="border border-gray-200 bg-white p-8 text-center text-gray-500 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400">
                Chưa có bài viết.
              </div>
            )}
          </section>

          {/* ===================================================
              CỘT PHẢI - DANH SÁCH BẢN TIN
          =================================================== */}

          <aside className="lg:sticky lg:top-6 lg:self-start">

            <div className="mt-0 max-h-[calc(100vh-120px)] overflow-y-auto pr-1">

              {newsArticles.map(
                (article, index) => {

                  const articleNumber =
                    index + 1;

                  const isSelected =
                    article.id ===
                    selectedArticle?.id;

                  return (
                    <button
                      key={article.id}
                      type="button"
                      onClick={() =>
                        setSelectedArticleId(
                          article.id
                        )
                      }
                      className={`group flex w-full gap-4 border-b border-gray-200 py-4 text-left transition-colors dark:border-gray-800 ${
                        isSelected
                          ? "bg-red-50 px-3 dark:bg-red-950/30"
                          : "px-0 hover:bg-gray-50 dark:hover:bg-gray-900"
                      }`}
                    >

                      {/* =================================================
                          SỐ THỨ TỰ
                      ================================================= */}

                      <div
                        className={`flex h-9 w-9 shrink-0 items-center justify-center text-sm font-bold ${
                          isSelected
                            ? "bg-red-600 text-white"
                            : "bg-gray-100 text-gray-500 group-hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:group-hover:bg-gray-700"
                        }`}
                      >
                        {String(
                          articleNumber
                        ).padStart(2, "0")}
                      </div>

                      {/* =================================================
                          THUMBNAIL
                      ================================================= */}

                      {article.coverImage ? (
                        <img
                          src={article.coverImage}
                          alt={article.title}
                          className="h-16 w-24 shrink-0 object-cover"
                        />
                      ) : (
                        <div className="h-16 w-24 shrink-0 bg-gray-100 dark:bg-gray-800" />
                      )}

                      {/* =================================================
                          THÔNG TIN
                      ================================================= */}

                      <div className="min-w-0 flex-1">

                        {/* Category */}

                        <div className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-red-600">
                          {article.categoryName}
                        </div>

                        {/* Title */}

                        <h3
                          className={`line-clamp-2 text-sm font-semibold leading-5 ${
                            isSelected
                              ? "text-red-700 dark:text-red-400"
                              : "text-gray-900 group-hover:text-red-600 dark:text-gray-100"
                          }`}
                        >
                          {article.title}
                        </h3>

                        {/* Date */}

                        <div className="mt-2 flex items-center text-[11px] text-gray-400">
                          <span>
                            {article.publishedAt}
                          </span>
                        </div>

                      </div>

                    </button>
                  );
                }
              )}

            </div>

          </aside>

        </div>

        {/* =========================================================
            ĐƯỢC QUAN TÂM
        ========================================================= */}

        <section className="mt-14 border-t border-gray-200 pt-8 dark:border-gray-800">

          <div className="mb-5">
            <h2 className="text-xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
              ĐƯỢC QUAN TÂM
            </h2>
          </div>

          <div className="grid grid-cols-1 gap-x-8 md:grid-cols-2 lg:grid-cols-5">

            {newsArticles
              .slice(0, 5)
              .map(
                (article, index) => {

                  return (
                    <Link
                      key={article.id}
                      href={`/chuyen-muc/${article.categorySlug}?article=${encodeURIComponent(
                        article.id
                      )}`}
                      className="group border-b border-gray-200 py-4 dark:border-gray-800 lg:border-b-0 lg:border-r lg:px-4 lg:first:pl-0 lg:last:border-r-0"
                    >

                      {/* Ảnh */}

                      <div className="relative mb-3 overflow-hidden">

                        {article.coverImage ? (
                          <img
                            src={article.coverImage}
                            alt={article.title}
                            className="h-36 w-full object-cover transition-transform duration-300 group-hover:scale-[1.02]"
                          />
                        ) : (
                          <div className="h-36 w-full bg-gray-100 dark:bg-gray-800" />
                        )}

                        <span className="absolute left-2 top-2 bg-white px-2 py-1 text-sm font-bold text-gray-700 dark:bg-gray-900 dark:text-gray-200">
                          {String(
                            index + 1
                          ).padStart(2, "0")}
                        </span>

                      </div>

                      {/* Tiêu đề */}

                      <h3 className="line-clamp-3 text-sm font-semibold leading-5 text-gray-900 transition-colors group-hover:text-red-600 dark:text-gray-100">
                        {article.title}
                      </h3>

                    </Link>
                  );
                }
              )}

          </div>

        </section>

      </main>
    </div>
  );
}