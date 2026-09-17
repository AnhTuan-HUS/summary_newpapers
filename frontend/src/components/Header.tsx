"use client";

import { useEffect, useState } from "react";

import Link from "next/link";

import { usePathname } from "next/navigation";

import {
  CalendarDays,
  Menu,
  Moon,
  Search,
  Sun,
  X,
} from "lucide-react";

import { getCategories } from "@/lib/api";

// =====================================================
// KIỂU DỮ LIỆU CATEGORY TỪ DATABASE
// =====================================================

type Category = {
  id: number;
  name: string;
  slug: string;
};

// =====================================================
// CATEGORY MẶC ĐỊNH
//
// Đây chỉ là FALLBACK.
//
// Nếu database có category:
//     → dùng category từ database
//
// Nếu database chưa có category:
//     → dùng danh sách này để menu không biến mất
// =====================================================

const fallbackCategories: Category[] = [
  {
    id: 1,
    name: "Bán dẫn & Vi mạch",
    slug: "ban-dan-vi-mach",
  },
  {
    id: 2,
    name: "Trí tuệ nhân tạo",
    slug: "tri-tue-nhan-tao",
  },
  {
    id: 3,
    name: "Startup & Đầu tư",
    slug: "startup-dau-tu",
  },
  {
    id: 4,
    name: "Xe điện",
    slug: "xe-dien",
  },
  {
    id: 5,
    name: "Điện thoại",
    slug: "dien-thoai",
  },
  {
    id: 6,
    name: "Hạ tầng số",
    slug: "ha-tang-so",
  },
];

// =====================================================
// KIỂU DỮ LIỆU CHO MENU
// =====================================================

type NavigationItem = {
  label: string;
  href: string;
};

export default function Header() {
  // =====================================================
  // MOBILE MENU
  // =====================================================

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // =====================================================
  // CATEGORY TỪ DATABASE
  // =====================================================

  const [categories, setCategories] = useState<Category[]>([]);

  // =====================================================
  // NGÀY HIỆN TẠI
  // =====================================================

  const [currentDate] = useState(() =>
    new Intl.DateTimeFormat("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }).format(new Date())
  );

  // =====================================================
  // URL HIỆN TẠI
  // =====================================================

  const pathname = usePathname();

  // =====================================================
  // LẤY CATEGORY TỪ DATABASE
  //
  // Luồng:
  //
  // Header
  //    ↓
  // getCategories()
  //    ↓
  // /api/categories
  //    ↓
  // FastAPI
  //    ↓
  // PostgreSQL
  //
  // Header KHÔNG truy cập PostgreSQL trực tiếp.
  // =====================================================

  useEffect(() => {
    async function loadCategories() {
      try {
        const data = await getCategories();

        // Backend trả về danh sách category.
        setCategories(data);
      } catch (error) {
        // Nếu API lỗi thì giữ categories = []
        //
        // Khi đó navigation bên dưới sẽ tự động
        // sử dụng fallbackCategories.
        console.error(
          "Không thể tải danh mục từ database:",
          error
        );
      }
    }

    loadCategories();
  }, []);

  // =====================================================
  // CATEGORY HIỂN THỊ
  //
  // Nếu database có dữ liệu:
  //     → dùng database
  //
  // Nếu database chưa có dữ liệu:
  //     → dùng fallback
  // =====================================================

  const displayCategories =
    categories.length > 0
      ? categories
      : fallbackCategories;

  // =====================================================
  // TẠO NAVIGATION
  //
  // Trang chủ luôn được giữ nguyên.
  //
  // Các mục còn lại được tạo từ category.
  //
  // Ví dụ:
  //
  // category.name = "Bán dẫn & Vi mạch"
  // category.slug = "ban-dan-vi-mach"
  //
  // sẽ tạo:
  //
  // {
  //   label: "Bán dẫn & Vi mạch",
  //   href: "/chuyen-muc/ban-dan-vi-mach"
  // }
  // =====================================================

  const navigation: NavigationItem[] = [
    {
      label: "Trang chủ",
      href: "/",
    },

    ...displayCategories.map((category) => ({
      label: category.name,
      href: `/chuyen-muc/${category.slug}`,
    })),
  ];

  // =====================================================
  // TOGGLE THEME
  // =====================================================

  const toggleTheme = () => {
    const isCurrentlyDark =
      document.documentElement.classList.contains("dark");

    const nextMode = !isCurrentlyDark;

    if (nextMode) {
      document.documentElement.classList.add("dark");

      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");

      localStorage.setItem("theme", "light");
    }
  };

  return (
    <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">

      {/* =====================================================
          HEADER CHÍNH
      ====================================================== */}

      <div className="mx-auto flex max-w-7xl items-center gap-6 px-4 py-4 sm:px-6 lg:px-8">

        {/* ===================================================
            LOGO
        ==================================================== */}

        <Link
          href="/"
          className="w-[150px] flex-shrink-0 leading-none"
        >
          <div className="text-[27px] font-black tracking-tight text-red-600">
            TECH VIỆT
          </div>

          <div className="mt-1 text-xs font-medium text-gray-500 dark:text-gray-400">
            Tạp chí Số & Công nghệ
          </div>
        </Link>

        {/* ===================================================
            SEARCH
        ==================================================== */}

        <div className="hidden min-w-0 flex-1 md:block">

          <div className="mx-auto flex max-w-2xl overflow-hidden rounded-full border border-gray-200 bg-gray-50 transition-colors focus-within:border-gray-300 focus-within:bg-white dark:border-gray-700 dark:bg-gray-900 dark:focus-within:border-gray-600 dark:focus-within:bg-gray-900">

            <div className="flex flex-1 items-center px-4">

              <Search className="mr-3 h-4 w-4 flex-shrink-0 text-gray-400" />

              <input
                type="text"
                placeholder="Tìm kiếm tin tức, bản tin, AI..."
                className="w-full bg-transparent py-2.5 text-sm text-gray-900 outline-none placeholder:text-gray-400 dark:text-gray-100"
              />

            </div>

            <button
              type="button"
              className="bg-red-600 px-6 text-sm font-bold text-white transition-colors hover:bg-red-700"
            >
              TÌM
            </button>

          </div>

        </div>

        {/* ===================================================
            RIGHT ACTIONS
        ==================================================== */}

        <div className="hidden flex-shrink-0 items-center gap-4 md:flex">

          {/* =================================================
              NGÀY
          ================================================== */}

          <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">

            <CalendarDays className="h-3.5 w-3.5 text-gray-400" />

            <span>
              {currentDate}
            </span>

          </div>

          {/* =================================================
              LANGUAGE
          ================================================== */}

          <div className="flex items-center text-xs font-bold">

            <button
              type="button"
              className="text-red-600"
            >
              VI
            </button>

            <span className="mx-1.5 text-gray-300 dark:text-gray-700">
              |
            </span>

            <button
              type="button"
              className="text-gray-400 transition-colors hover:text-gray-900 dark:hover:text-white"
            >
              EN
            </button>

          </div>

          {/* =================================================
              LIGHT / DARK
          ================================================== */}

          <button
            type="button"
            onClick={toggleTheme}
            aria-label="Chuyển đổi giao diện sáng tối"
            className="inline-flex items-center gap-2 rounded-full border border-gray-200 px-4 py-2.5 text-sm font-semibold text-gray-700 transition-colors hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-200 dark:hover:border-gray-600 dark:hover:bg-gray-900"
          >

            {/* LIGHT */}

            <Sun className="h-4 w-4 dark:hidden" />

            <span className="dark:hidden">
              Light
            </span>

            {/* DARK */}

            <Moon className="hidden h-4 w-4 dark:block" />

            <span className="hidden dark:inline">
              Dark
            </span>

          </button>

          {/* =================================================
              LOGIN
          ================================================== */}

          <button
            type="button"
            className="rounded-full bg-gray-900 px-5 py-2.5 text-sm font-bold text-white transition-colors hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-200"
          >
            Đăng nhập
          </button>

        </div>

        {/* ===================================================
            MOBILE MENU BUTTON
        ==================================================== */}

        <button
          type="button"
          onClick={() =>
            setMobileMenuOpen((current) => !current)
          }
          aria-label={
            mobileMenuOpen
              ? "Đóng menu"
              : "Mở menu"
          }
          className="ml-auto rounded-lg p-2 text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-900 md:hidden"
        >

          {mobileMenuOpen ? (
            <X className="h-6 w-6" />
          ) : (
            <Menu className="h-6 w-6" />
          )}

        </button>

      </div>

      {/* =====================================================
          NAVIGATION
      ====================================================== */}

      <nav className="hidden bg-gray-950 dark:bg-black md:block">

        <div className="mx-auto flex max-w-7xl items-center px-4 sm:px-6 lg:px-8">

          <div className="flex min-w-0 flex-1">

            {navigation.map((item) => {

              const isActive =
                pathname === item.href;

              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={`relative whitespace-nowrap px-4 py-3.5 text-sm font-bold transition-colors ${
                    isActive
                      ? "text-red-500"
                      : "text-white hover:text-red-400"
                  }`}
                >

                  {item.label}

                  {isActive && (
                    <span className="absolute bottom-0 left-4 right-4 h-0.5 bg-red-500" />
                  )}

                </Link>
              );
            })}

          </div>

          {/* =================================================
              LIVE TECH FEED
          ================================================== */}

          <div className="ml-4 flex flex-shrink-0 items-center border-l border-gray-700 pl-5">

            <span className="mr-2 h-2 w-2 rounded-full bg-green-500" />

            <span className="text-sm font-bold text-white">
              Live Tech Feed
            </span>

          </div>

        </div>

      </nav>

      {/* =====================================================
          MOBILE MENU
      ====================================================== */}

      {mobileMenuOpen && (

        <div className="border-t border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950 md:hidden">

          {/* =================================================
              MOBILE SEARCH
          ================================================== */}

          <div className="px-4 py-4">

            <div className="flex overflow-hidden rounded-lg border border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900">

              <div className="flex flex-1 items-center px-3">

                <Search className="mr-2 h-4 w-4 text-gray-400" />

                <input
                  type="text"
                  placeholder="Tìm kiếm tin tức..."
                  className="w-full bg-transparent py-2.5 text-sm text-gray-900 outline-none placeholder:text-gray-400 dark:text-gray-100"
                />

              </div>

              <button
                type="button"
                className="bg-red-600 px-4 text-sm font-bold text-white"
              >
                TÌM
              </button>

            </div>

          </div>

          {/* =================================================
              MOBILE DATE + LANGUAGE
          ================================================== */}

          <div className="flex items-center justify-between border-y border-gray-100 px-4 py-3 dark:border-gray-800">

            <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">

              <CalendarDays className="h-3.5 w-3.5 text-gray-400" />

              {currentDate}

            </div>

            <div className="flex items-center text-xs font-bold">

              <button
                type="button"
                className="text-red-600"
              >
                VI
              </button>

              <span className="mx-1.5 text-gray-300 dark:text-gray-700">
                |
              </span>

              <button
                type="button"
                className="text-gray-400"
              >
                EN
              </button>

            </div>

          </div>

          {/* =================================================
              MOBILE NAV
          ================================================== */}

          <nav>

            {navigation.map((item) => {

              const isActive =
                pathname === item.href;

              return (
                <Link
                  key={item.label}
                  href={item.href}
                  onClick={() =>
                    setMobileMenuOpen(false)
                  }
                  className={`block border-b border-gray-100 px-4 py-3.5 text-sm font-semibold dark:border-gray-800 ${
                    isActive
                      ? "text-red-600"
                      : "text-gray-800 dark:text-gray-200"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}

          </nav>

          {/* =================================================
              MOBILE ACTIONS
          ================================================== */}

          <div className="flex gap-3 p-4">

            {/* LIGHT / DARK */}

            <button
              type="button"
              onClick={toggleTheme}
              aria-label="Chuyển đổi giao diện sáng tối"
              className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-gray-200 py-3 text-sm font-semibold text-gray-700 dark:border-gray-700 dark:text-gray-200"
            >

              <Sun className="h-4 w-4 dark:hidden" />

              <span className="dark:hidden">
                Light
              </span>

              <Moon className="hidden h-4 w-4 dark:block" />

              <span className="hidden dark:inline">
                Dark
              </span>

            </button>

            {/* LOGIN */}

            <button
              type="button"
              className="flex-1 rounded-lg bg-gray-900 py-3 text-sm font-bold text-white dark:bg-white dark:text-gray-900"
            >
              Đăng nhập
            </button>

          </div>

        </div>

      )}

    </header>
  );
}