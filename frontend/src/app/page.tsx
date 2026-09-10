"use client";

import { useMemo, useState } from "react";

import { Bookmark, Clock, Eye } from "lucide-react";

import {
  articles,
  getCategoryById,
  mostViewedArticles,
} from "@/data/mockData";

export default function Home() {
  /**
   * Tất cả bài viết được sắp xếp mới nhất -> cũ nhất.
   *
   * Đây là danh sách dùng cho:
   * - BẢN TIN 01
   * - BẢN TIN 02
   * - BẢN TIN 03
   * - ...
   */
  const newsArticles = useMemo(() => {
    return [...articles].sort(
      (a, b) =>
        new Date(b.publishedAt).getTime() -
        new Date(a.publishedAt).getTime(),
    );
  }, []);

  /**
   * Mặc định mở bài mới nhất.
   */
  const [selectedArticleId, setSelectedArticleId] = useState(
    newsArticles[0]?.id ?? "",
  );

  /**
   * Tìm bài đang được chọn.
   */
  const selectedArticle = newsArticles.find(
    (article) => article.id === selectedArticleId,
  );

  /**
   * Xác định số thứ tự của bài đang đọc.
   *
   * index = 0 -> BẢN TIN 01
   * index = 1 -> BẢN TIN 02
   * ...
   */
  const selectedIndex = newsArticles.findIndex(
    (article) => article.id === selectedArticleId,
  );

  const selectedNumber = selectedIndex + 1;

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* =====================================================
            KHỐI ĐỌC BÀI + DANH SÁCH BẢN TIN
        ====================================================== */}
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-[minmax(0,1fr)_360px]">
          {/* ===================================================
              CỘT TRÁI - BÀI ĐANG ĐỌC
          ==================================================== */}
          <section>
            {/* Tiêu đề */}
            <div className="mb-5 border-b border-gray-200 pb-4">
              <h1 className="text-xl font-bold tracking-tight text-gray-900">
                BẢN TIN {String(selectedNumber).padStart(2, "0")}
              </h1>
            </div>

            {selectedArticle ? (
              <article className="overflow-hidden border border-gray-200 bg-white">
                {/* Ảnh */}
                <div className="relative">
                  <img
                    src={selectedArticle.coverImage}
                    alt={selectedArticle.title}
                    className="h-64 w-full object-cover sm:h-80 lg:h-[360px]"
                  />

                  {/* Số bản tin */}
                  <div className="absolute left-4 top-4 flex h-10 w-10 items-center justify-center bg-red-600 text-sm font-bold text-white">
                    {String(selectedNumber).padStart(2, "0")}
                  </div>
                </div>

                {/* Thông tin bài */}
                <div className="p-6 sm:p-8">
                  <div className="mb-3 flex flex-wrap items-center gap-3 text-xs">
                    <span className="font-semibold uppercase tracking-wide text-red-600">
                      {getCategoryById(selectedArticle.categoryId)?.name ??
                        "Công nghệ"}
                    </span>

                    <span className="text-gray-300">•</span>

                    <span className="flex items-center text-gray-400">
                      <Clock className="mr-1 h-3.5 w-3.5" />
                      {selectedArticle.publishedAt}
                    </span>
                  </div>

                  <h2 className="text-2xl font-bold leading-tight text-gray-900 sm:text-3xl">
                    {selectedArticle.title}
                  </h2>

                  <p className="mt-4 text-base leading-7 text-gray-600">
                    {selectedArticle.excerpt}
                  </p>

                  <div className="mt-5 flex items-center justify-between border-t border-gray-100 pt-4">
                    <span className="text-xs text-gray-400">
                      {selectedArticle.author}
                    </span>

                    <button
                      type="button"
                      aria-label="Lưu bài viết"
                      className="rounded p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-red-600"
                    >
                      <Bookmark className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                {/* Nội dung bài */}
                <div className="border-t border-gray-100 px-6 py-6 sm:px-8 sm:py-8">
                  <div className="max-w-none">
                    {selectedArticle.content
                      .split("\n")
                      .filter((paragraph) => paragraph.trim() !== "")
                      .map((paragraph, index) => (
                        <p
                          key={`${selectedArticle.id}-${index}`}
                          className="mb-5 text-[15px] leading-8 text-gray-700 last:mb-0"
                        >
                          {paragraph}
                        </p>
                      ))}
                  </div>
                </div>
              </article>
            ) : (
              <div className="border border-gray-200 bg-white p-8 text-center text-gray-500">
                Chưa có bài viết.
              </div>
            )}
          </section>

          {/* ===================================================
              CỘT PHẢI - TẤT CẢ BẢN TIN
          ==================================================== */}
          <aside className="lg:sticky lg:top-6 lg:self-start">
            <div className="border-b border-gray-200 pb-4">
              <h2 className="text-xl font-bold tracking-tight text-gray-900">
                TẤT CẢ BẢN TIN
              </h2>
            </div>

            <div className="mt-2 max-h-[calc(100vh-120px)] overflow-y-auto pr-1">
              {newsArticles.map((article, index) => {
                const articleNumber = index + 1;
                const isSelected = article.id === selectedArticleId;

                return (
                  <button
                    key={article.id}
                    type="button"
                    onClick={() => setSelectedArticleId(article.id)}
                    className={`group flex w-full gap-4 border-b border-gray-200 py-4 text-left transition-colors ${
                      isSelected
                        ? "bg-red-50 px-3"
                        : "px-0 hover:bg-gray-50"
                    }`}
                  >
                    {/* Số thứ tự */}
                    <div
                      className={`flex h-9 w-9 shrink-0 items-center justify-center text-sm font-bold ${
                        isSelected
                          ? "bg-red-600 text-white"
                          : "bg-gray-100 text-gray-500 group-hover:bg-gray-200"
                      }`}
                    >
                      {String(articleNumber).padStart(2, "0")}
                    </div>

                    {/* Thumbnail */}
                    <img
                      src={article.coverImage}
                      alt={article.title}
                      className="h-16 w-24 shrink-0 object-cover"
                    />

                    {/* Thông tin */}
                    <div className="min-w-0 flex-1">
                      <div className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-red-600">
                        {getCategoryById(article.categoryId)?.name ??
                          "Công nghệ"}
                      </div>

                      <h3
                        className={`line-clamp-2 text-sm font-semibold leading-5 ${
                          isSelected
                            ? "text-red-700"
                            : "text-gray-900 group-hover:text-red-600"
                        }`}
                      >
                        {article.title}
                      </h3>

                      <div className="mt-2 flex items-center gap-2 text-[11px] text-gray-400">
                        <span>{article.publishedAt}</span>

                        <span>•</span>

                        <span className="flex items-center">
                          <Eye className="mr-1 h-3 w-3" />
                          {article.views.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </aside>
        </div>

        {/* =====================================================
            ĐƯỢC QUAN TÂM
            Nằm bên dưới toàn bộ khối trên.
            Heading thẳng hàng với BẢN TIN 01.
        ====================================================== */}
        <section className="mt-14 border-t border-gray-200 pt-8">
          <div className="mb-5">
            <h2 className="text-xl font-bold tracking-tight text-gray-900">
              ĐƯỢC QUAN TÂM
            </h2>
          </div>

          <div className="grid grid-cols-1 gap-x-8 md:grid-cols-2 lg:grid-cols-5">
            {mostViewedArticles.map((article, index) => (
              <div
                key={article.id}
                className="border-b border-gray-200 py-4 lg:border-b-0 lg:border-r lg:px-4 lg:first:pl-0 lg:last:border-r-0"
              >
                {/* Ảnh */}
                <div className="relative mb-3 overflow-hidden">
                  <img
                    src={article.coverImage}
                    alt={article.title}
                    className="h-36 w-full object-cover"
                  />

                  <span className="absolute left-2 top-2 bg-white px-2 py-1 text-sm font-bold text-gray-700">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                </div>

                {/* Lượt xem */}
                <div className="mb-2 flex items-center">
                  <span className="flex items-center text-[11px] text-gray-400">
                    <Eye className="mr-1 h-3 w-3" />
                    {article.views.toLocaleString()}
                  </span>
                </div>

                {/* Tiêu đề */}
                <h3 className="line-clamp-3 text-sm font-semibold leading-5 text-gray-900 hover:text-red-600">
                  {article.title}
                </h3>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}