"use client";

import { useState } from "react";
import { X } from "lucide-react";

import { register } from "@/api/auth";

type RegisterModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onOpenLogin: () => void;
};

export default function RegisterModal({
  isOpen,
  onClose,
  onOpenLogin,
}: RegisterModalProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");

    // Kiểm tra mật khẩu xác nhận trước khi gọi backend
    if (password !== confirmPassword) {
      setError("Mật khẩu xác nhận không khớp.");
      return;
    }

    setIsLoading(true);

    try {
      const result = await register({
        name,
        email,
        password,
      });

      console.log("Đăng ký thành công:", result);

      onClose();
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Đăng ký thất bại.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/40 px-4">
      <div className="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl dark:bg-gray-900">
        {/* Nút đóng */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Đóng đăng ký"
          className="absolute right-4 top-4 flex h-9 w-9 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:hover:bg-gray-800 dark:hover:text-white"
        >
          <X size={20} />
        </button>

        {/* Tiêu đề */}
        <div className="mb-6 pr-10">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
            Đăng ký
          </h2>

          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Tạo tài khoản Tech Việt của bạn.
          </p>
        </div>

        {/* Form */}
        <form className="space-y-4" onSubmit={handleSubmit}>
          {/* Họ tên */}
          <div>
            <label
              htmlFor="register-name"
              className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Họ và tên
            </label>

            <input
              id="register-name"
              type="text"
              placeholder="Nhập họ và tên"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition-colors placeholder:text-gray-400 focus:border-red-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500"
            />
          </div>

          {/* Email */}
          <div>
            <label
              htmlFor="register-email"
              className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Email
            </label>

            <input
              id="register-email"
              type="email"
              placeholder="Nhập email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition-colors placeholder:text-gray-400 focus:border-red-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500"
            />
          </div>

          {/* Mật khẩu */}
          <div>
            <label
              htmlFor="register-password"
              className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Mật khẩu
            </label>

            <input
              id="register-password"
              type="password"
              placeholder="Tạo mật khẩu"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition-colors placeholder:text-gray-400 focus:border-red-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500"
            />
          </div>

          {/* Xác nhận mật khẩu */}
          <div>
            <label
              htmlFor="register-confirm-password"
              className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Xác nhận mật khẩu
            </label>

            <input
              id="register-confirm-password"
              type="password"
              placeholder="Nhập lại mật khẩu"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              required
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition-colors placeholder:text-gray-400 focus:border-red-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500"
            />
          </div>

          {/* Thông báo lỗi */}
          {error && (
            <p className="text-sm text-red-600">
              {error}
            </p>
          )}

          {/* Đăng ký */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-lg bg-red-600 py-2.5 text-sm font-medium text-white transition-colors hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoading ? "Đang đăng ký..." : "Đăng ký"}
          </button>
        </form>

        {/* Đăng nhập */}
        <div className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
          Đã có tài khoản?{" "}
          <button
            type="button"
            onClick={onOpenLogin}
            className="font-medium text-red-600 hover:text-red-700"
          >
            Đăng nhập
          </button>
        </div>
      </div>
    </div>
  );
}