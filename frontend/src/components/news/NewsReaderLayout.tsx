import Link from "next/link";

import { Clock } from "lucide-react";

import type { DisplayArticle } from "@/api/articles";

type NewsReaderLayoutProps = {
  newsArticles: DisplayArticle[];
  selectedArticle: DisplayArticle;
};

export default function NewsReaderLayout({
  newsArticles,
  selectedArticle,
}: NewsReaderLayoutProps) {
  // Chỉ hiển thị các bài thuộc cùng chuyên mục với bài đang đọc
  const categoryArticles = newsArticles.filter(
    (article) =>
      article.categoryName === selectedArticle.categoryName
  );

  return (
    <div className="min-h-screen bg-gray-50 font-sans dark:bg-[#0B0F19]">
      <div className="mx-auto max-w-[1500px] px-4 pt-2 pb-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-[minmax(0,1fr)_400px]">
          {/* =====================================================
              ARTICLE
          ====================================================== */}
          <article className="min-w-0">
            <div className="border border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
              {/* =================================================
                  CATEGORY + DATE
              ================================================== */}
              <div className="border-b border-gray-200 px-6 py-4 dark:border-gray-800">
                <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
                  <span className="font-semibold uppercase tracking-wide text-red-600">
                    {selectedArticle.categoryName}
                  </span>

                  <span className="text-gray-300 dark:text-gray-700">
                    |
                  </span>

                  <span className="flex items-center gap-1.5">
                    <Clock className="h-4 w-4" />
                    {selectedArticle.publishedAt}
                  </span>
                </div>
              </div>

              {/* =================================================
                  TITLE + SUMMARY
              ================================================== */}
              <div className="px-6 pt-6 sm:px-8 sm:pt-8">
                <h1 className="text-3xl font-bold leading-tight tracking-tight text-gray-900 dark:text-gray-100 sm:text-4xl">
                  {selectedArticle.title}
                </h1>

                <div className="mt-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                  Tech Việt
                </div>

                {/* SUMMARY */}
                {selectedArticle.summary && (
                  <div className="pt-8">
                    <div className="whitespace-pre-line text-justify text-[17px] leading-8 text-gray-700 dark:text-gray-300">
                      {selectedArticle.summary}
                    </div>
                  </div>
                )}
              </div>

              {/* =================================================
                  COVER IMAGE
              ================================================== */}
              {selectedArticle.coverImage && (
                <div className="mx-6 mt-8 overflow-hidden border border-gray-200 bg-gray-100 sm:mx-8 dark:border-gray-800 dark:bg-gray-900">
                  <img
                    src={selectedArticle.coverImage}
                    alt={selectedArticle.title}
                    className="h-auto w-full object-cover"
                  />
                </div>
              )}

              {/* =================================================
                  CONTENT
              ================================================== */}
              <div className="px-6 pb-8 pt-8 sm:px-8">
                {selectedArticle.content ? (
                  <div className="space-y-5 text-[17px] leading-8 text-gray-800 dark:text-gray-200">
                    {(selectedArticle.content.includes("\n\n")
                      ? selectedArticle.content.split(/\n\s*\n/)
                      : selectedArticle.content.split(/\n+/)
                    ).map((paragraph, index) => {
                      const cleanPara = paragraph.trim();
                      if (!cleanPara) return null;
                      return (
                        <p key={index} className="whitespace-pre-line text-justify">
                          {cleanPara}
                        </p>
                      );
                    })}
                  </div>
                ) : (
                  <div className="py-8 text-sm text-gray-500 dark:text-gray-400">
                    Bài viết chưa có nội dung.
                  </div>
                )}
              </div>
            </div>
          </article>

          {/* =====================================================
              SIDEBAR - ALL ARTICLES IN SAME CATEGORY

              Sidebar hoạt động độc lập giống sidebar ChatGPT:
              - Chiếm chiều cao màn hình
              - Header đứng yên
              - Danh sách bên dưới cuộn riêng
          ====================================================== */}
          {categoryArticles.length > 0 && (
            <aside className="hidden lg:block">
              <div className="sticky top-0 h-[calc(100vh-0.2rem)]">
                <div className="flex h-full flex-col border border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
                  {/* =================================================
                      SIDEBAR HEADER
                      Không cuộn
                  ================================================== */}
                  <div className="shrink-0 border-b border-gray-200 px-5 py-4 dark:border-gray-800">
                    <div className="flex items-center gap-3">
                      <div className="h-5 w-1 bg-red-600" />

                      <div>
                        <h2 className="text-sm font-bold uppercase tracking-wide text-gray-900 dark:text-gray-100">
                          Tất cả bản tin
                        </h2>

                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                          {selectedArticle.categoryName}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* =================================================
                      ARTICLE LIST

                      Chỉ phần này được scroll.
                  ================================================== */}
                  <div className="min-h-0 flex-1 overflow-y-auto">
                    <div className="divide-y divide-gray-200 dark:divide-gray-800">
                      {categoryArticles.map((article, index) => {
                        const isSelected =
                          article.id === selectedArticle.id;

                        return (
                          <Link
                            key={article.id}
                            href={`/bai-viet/${encodeURIComponent(
                              article.slug
                            )}`}
                            className={`group block p-4 transition-colors ${
                              isSelected
                                ? "bg-red-50 dark:bg-red-950/20"
                                : "hover:bg-gray-50 dark:hover:bg-gray-800/60"
                            }`}
                          >
                            <div className="flex gap-3">
                              {/* =================================================
                                  THUMBNAIL
                              ================================================== */}
                              <div className="relative h-[76px] w-[115px] shrink-0 overflow-hidden rounded-md bg-gray-100 dark:bg-gray-800">
                                {article.coverImage ? (
                                  <img
                                    src={article.coverImage}
                                    alt={article.title}
                                    className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.04]"
                                  />
                                ) : (
                                  <div className="flex h-full w-full items-center justify-center text-[10px] text-gray-500 dark:text-gray-400">
                                    Không có ảnh
                                  </div>
                                )}

                                {/* NUMBER */}
                                <div
                                  className={`absolute left-2 top-2 flex h-6 w-6 items-center justify-center text-[10px] font-bold ${
                                    isSelected
                                      ? "bg-red-600 text-white"
                                      : "bg-black/70 text-white"
                                  }`}
                                >
                                  {String(index + 1).padStart(
                                    2,
                                    "0"
                                  )}
                                </div>
                              </div>

                              {/* =================================================
                                  ARTICLE INFO
                              ================================================== */}
                              <div className="min-w-0 flex-1">
                                <h3
                                  className={`line-clamp-3 text-sm font-semibold leading-5 transition-colors ${
                                    isSelected
                                      ? "text-red-600 dark:text-red-500"
                                      : "text-gray-900 group-hover:text-red-600 dark:text-gray-100 dark:group-hover:text-red-500"
                                  }`}
                                >
                                  {article.title}
                                </h3>

                                <div className="mt-2 flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
                                  <Clock className="h-3.5 w-3.5 shrink-0" />

                                  <span>
                                    {article.publishedAt}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </Link>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>
            </aside>
          )}
        </div>
      </div>
    </div>
  );
}