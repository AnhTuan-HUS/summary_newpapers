"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { Mail } from "lucide-react";
import { getCategories } from "@/api/api";
import { Category } from "@/types";

const fallbackCategories = [
  { id: "1", name: "Bán dẫn & Vi mạch", slug: "ban-dan-vi-mach" },
  { id: "2", name: "Trí tuệ nhân tạo", slug: "tri-tue-nhan-tao" },
  { id: "3", name: "Startup & Đầu tư", slug: "startup-dau-tu" },
  { id: "4", name: "Xe điện", slug: "xe-dien" },
  { id: "5", name: "Điện thoại", slug: "dien-thoai" },
  { id: "6", name: "Hạ tầng số", slug: "ha-tang-so" },
];

const quickLinks = [
  { href: "/", label: "Trang chủ" },
  { href: "/gioi-thieu", label: "Giới thiệu" },
  { href: "/lien-he", label: "Liên hệ" },
  { href: "/chinh-sach-bao-mat", label: "Chính sách bảo mật" },
];

export default function Footer() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
  const [categoriesList, setCategoriesList] = useState<any[]>(fallbackCategories);

  useEffect(() => {
    getCategories()
      .then((data) => {
        if (data && data.length > 0) {
          setCategoriesList(data);
        }
      })
      .catch(() => {});
  }, []);


  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
    if (!isValid) {
      setStatus("error");
      return;
    }
    setStatus("success");
    setEmail("");
  };

  return (
    <footer className="mt-auto bg-[#111827] text-gray-300">
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-12 sm:px-6 md:grid-cols-2 lg:grid-cols-4 lg:px-8">
        <div className="lg:col-span-1">
          <Link href="/" className="text-2xl font-extrabold tracking-tight text-[#DC2626]">
            TECH VIỆT
          </Link>
          <p className="mt-3 text-sm leading-6 text-gray-400">
            Tạp chí công nghệ Việt Nam: bán dẫn, AI, startup, xe điện và hạ tầng số.
          </p>
        </div>

        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-white">
            Liên kết nhanh
          </h2>
          <ul className="mt-4 space-y-2">
            {quickLinks.map((link) => (
              <li key={link.href}>
                <Link href={link.href} className="text-sm hover:text-white">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-white">
            Chuyên mục
          </h2>
          <ul className="mt-4 space-y-2">
            {categoriesList.map((category) => (
              <li key={category.id}>
                <Link
                  href={`/chuyen-muc/${category.slug}`}
                  className="text-sm hover:text-white"
                >
                  {category.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-white">
            Đăng ký nhận tin
          </h2>
          <p className="mt-4 text-sm text-gray-400">
            Nhận bản tin công nghệ mỗi tuần, không spam.
          </p>
          <form onSubmit={handleSubmit} className="mt-4 space-y-3" noValidate>
            <label htmlFor="newsletter-email" className="sr-only">
              Địa chỉ email
            </label>
            <div className="relative">
              <Mail
                className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-gray-500"
                aria-hidden
              />
              <input
                id="newsletter-email"
                type="email"
                value={email}
                onChange={(event) => {
                  setEmail(event.target.value);
                  if (status !== "idle") setStatus("idle");
                }}
                placeholder="email@example.com"
                className="w-full rounded-md border border-gray-700 bg-gray-900 py-2.5 pl-10 pr-3 text-sm text-white outline-none placeholder:text-gray-500 focus:border-[#DC2626] focus:ring-2 focus:ring-[#DC2626]/30"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full rounded-md bg-[#DC2626] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-700"
            >
              Đăng ký
            </button>
            {status === "success" && (
              <p className="text-sm text-green-400" role="status">
                Cảm ơn bạn đã đăng ký nhận bản tin TECH VIỆT.
              </p>
            )}
            {status === "error" && (
              <p className="text-sm text-red-400" role="alert">
                Vui lòng nhập email hợp lệ.
              </p>
            )}
          </form>
        </div>
      </div>

      <div className="border-t border-gray-800">
        <p className="mx-auto max-w-7xl px-4 py-4 text-center text-xs text-gray-500 sm:px-6 lg:px-8">
          © {new Date().getFullYear()} TECH VIỆT. Mọi quyền được bảo lưu.
        </p>
      </div>
    </footer>
  );
}
