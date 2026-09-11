"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

import {
  CalendarDays,
  Menu,
  Search,
  Sun,
  X,
} from "lucide-react";

const navigation = [
  {
    label: "Trang chủ",
    href: "/",
  },
  {
    label: "Bán dẫn & Vi mạch",
    href: "/chuyen-muc/ban-dan-vi-mach",
  },
  {
    label: "Trí tuệ nhân tạo",
    href: "/chuyen-muc/tri-tue-nhan-tao",
  },
  {
    label: "Startup & Đầu tư",
    href: "/chuyen-muc/startup-dau-tu",
  },
  {
    label: "Xe điện",
    href: "/chuyen-muc/xe-dien",
  },
  {
    label: "Điện thoại",
    href: "/chuyen-muc/dien-thoai",
  },
  {
    label: "Hạ tầng số",
    href: "/chuyen-muc/ha-tang-so",
  },
];

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [currentDate, setCurrentDate] = useState("");

  // Lấy URL hiện tại
  const pathname = usePathname();

  useEffect(() => {
    const updateDate = () => {
      const date = new Intl.DateTimeFormat("vi-VN", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      }).format(new Date());

      setCurrentDate(date);
    };

    updateDate();
  }, []);

  return (
    <header className="border-b border-gray-200 bg-white">
      {/* =====================================================
          HEADER CHÍNH
      ====================================================== */}
      <div className="mx-auto flex max-w-7xl items-center gap-6 px-4 py-4 sm:px-6 lg:px-8">
        {/* LOGO */}
        <a
          href="/"
          className="w-[150px] flex-shrink-0 leading-none"
        >
          <div className="text-[27px] font-black tracking-tight text-red-600">
            TECH VIỆT
          </div>

          <div className="mt-1 text-xs font-medium text-gray-500">
            Tạp chí Số & Công nghệ
          </div>
        </a>

        {/* SEARCH */}
        <div className="hidden min-w-0 flex-1 md:block">
          <div className="mx-auto flex max-w-2xl overflow-hidden rounded-full border border-gray-200 bg-gray-50 transition-colors focus-within:border-gray-300 focus-within:bg-white">
            <div className="flex flex-1 items-center px-4">
              <Search className="mr-3 h-4 w-4 flex-shrink-0 text-gray-400" />

              <input
                type="text"
                placeholder="Tìm kiếm tin tức, bản tin, AI..."
                className="w-full bg-transparent py-2.5 text-sm text-gray-900 outline-none placeholder:text-gray-400"
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

        {/* =================================================
            RIGHT ACTIONS
        ================================================== */}
        <div className="hidden flex-shrink-0 items-center gap-4 md:flex">
          {/* NGÀY */}
          <div className="flex items-center gap-1.5 text-xs text-gray-500">
            <CalendarDays className="h-3.5 w-3.5 text-gray-400" />

            <span>{currentDate || "10/09/2026"}</span>
          </div>

          {/* LANGUAGE */}
          <div className="flex items-center text-xs font-bold">
            <button
              type="button"
              className="text-red-600"
            >
              VI
            </button>

            <span className="mx-1.5 text-gray-300">
              |
            </span>

            <button
              type="button"
              className="text-gray-400 transition-colors hover:text-gray-900"
            >
              EN
            </button>
          </div>

          {/* BẢN TIN SÁNG */}
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-full border border-gray-200 px-4 py-2.5 text-sm font-semibold text-gray-700 transition-colors hover:border-gray-300 hover:bg-gray-50"
          >
            <Sun className="h-4 w-4" />

            Bản tin Sáng
          </button>

          {/* LOGIN */}
          <button
            type="button"
            className="rounded-full bg-gray-900 px-5 py-2.5 text-sm font-bold text-white transition-colors hover:bg-gray-800"
          >
            Đăng nhập
          </button>
        </div>

        {/* MOBILE MENU */}
        <button
          type="button"
          onClick={() => setMobileMenuOpen((current) => !current)}
          aria-label={
            mobileMenuOpen
              ? "Đóng menu"
              : "Mở menu"
          }
          className="ml-auto rounded-lg p-2 text-gray-700 hover:bg-gray-100 md:hidden"
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
      <nav className="hidden bg-gray-950 md:block">
        <div className="mx-auto flex max-w-7xl items-center px-4 sm:px-6 lg:px-8">
          <div className="flex min-w-0 flex-1">
            {navigation.map((item) => {
              // Xác định menu hiện tại
              const isActive =
                pathname === item.href;

              return (
                <a
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
                </a>
              );
            })}
          </div>

          {/* LIVE TECH FEED */}
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
        <div className="border-t border-gray-200 bg-white md:hidden">
          {/* MOBILE SEARCH */}
          <div className="px-4 py-4">
            <div className="flex overflow-hidden rounded-lg border border-gray-200 bg-gray-50">
              <div className="flex flex-1 items-center px-3">
                <Search className="mr-2 h-4 w-4 text-gray-400" />

                <input
                  type="text"
                  placeholder="Tìm kiếm tin tức..."
                  className="w-full bg-transparent py-2.5 text-sm outline-none"
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

          {/* MOBILE DATE + LANGUAGE */}
          <div className="flex items-center justify-between border-y border-gray-100 px-4 py-3">
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <CalendarDays className="h-3.5 w-3.5 text-gray-400" />

              {currentDate || "10/09/2026"}
            </div>

            <div className="flex items-center text-xs font-bold">
              <button
                type="button"
                className="text-red-600"
              >
                VI
              </button>

              <span className="mx-1.5 text-gray-300">
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

          {/* MOBILE NAV */}
          <nav>
            {navigation.map((item) => {
              const isActive =
                pathname === item.href;

              return (
                <a
                  key={item.label}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block border-b border-gray-100 px-4 py-3.5 text-sm font-semibold ${
                    isActive
                      ? "text-red-600"
                      : "text-gray-800"
                  }`}
                >
                  {item.label}
                </a>
              );
            })}
          </nav>

          {/* MOBILE ACTIONS */}
          <div className="flex gap-3 p-4">
            <button
              type="button"
              className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-gray-200 py-3 text-sm font-semibold text-gray-700"
            >
              <Sun className="h-4 w-4" />

              Bản tin Sáng
            </button>

            <button
              type="button"
              className="flex-1 rounded-lg bg-gray-900 py-3 text-sm font-bold text-white"
            >
              Đăng nhập
            </button>
          </div>
        </div>
      )}
    </header>
  );
}