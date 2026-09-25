"use client";

import { useState } from "react";
import { Send, X } from "lucide-react";

type Message = {
  id: number;
  content: string;
  role: "user" | "bot";
};

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: "bot",
      content:
        "Xin chào! Tôi là Tech Việt AI. Tôi có thể giúp bạn tìm hiểu các tin tức công nghệ.",
    },
  ]);

  const [input, setInput] = useState("");

  function handleSendMessage() {
    const content = input.trim();

    if (!content) return;

    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      content,
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
    ]);

    setInput("");
  }

  return (
    <>
      {/* Chatbot window */}
      {isOpen && (
        <div className="fixed bottom-24 right-4 z-[100] flex h-[520px] w-[380px] flex-col overflow-hidden rounded-xl border border-gray-200 bg-white shadow-2xl dark:border-gray-700 dark:bg-gray-900 sm:right-6">
          
          {/* Header */}
          <div className="flex shrink-0 items-center justify-between border-b border-gray-200 bg-white px-4 py-3 dark:border-gray-700 dark:bg-gray-900">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-full">
                <img
                  src="/mascot/tech-viet-mascot.png"
                  alt="Tech Việt AI"
                  className="h-full w-full object-contain"
                />
              </div>

              <div>
                <h2 className="text-sm font-semibold text-gray-900 dark:text-white">
                  Tech Việt AI
                </h2>

                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Trợ lý công nghệ
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setIsOpen(false)}
              aria-label="Đóng chatbot"
              className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:hover:bg-gray-800 dark:hover:text-white"
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages */}
          <div className="min-h-0 flex-1 overflow-y-auto bg-gray-50 px-4 py-4 dark:bg-[#0B0F19]">
            <div className="space-y-4">
              {messages.map((message) => {
                const isUser = message.role === "user";

                return (
                  <div
                    key={message.id}
                    className={`flex ${
                      isUser ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-6 ${
                        isUser
                          ? "rounded-br-md bg-red-600 text-white"
                          : "rounded-bl-md bg-white text-gray-700 shadow-sm dark:bg-gray-800 dark:text-gray-200"
                      }`}
                    >
                      {message.content}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Input */}
          <div className="shrink-0 border-t border-gray-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-900">
            <form
              onSubmit={(event) => {
                event.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Nhập câu hỏi..."
                className="min-w-0 flex-1 rounded-lg border border-gray-300 bg-gray-50 px-3 py-2.5 text-sm text-gray-900 outline-none transition-colors placeholder:text-gray-400 focus:border-red-500 focus:bg-white dark:border-gray-700 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500 dark:focus:border-red-500 dark:focus:bg-gray-800"
              />

              <button
                type="submit"
                aria-label="Gửi tin nhắn"
                disabled={!input.trim()}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-red-600 text-white transition-colors hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Send size={18} />
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Mascot button */}
      <button
        type="button"
        onClick={() => setIsOpen((current) => !current)}
        aria-label={isOpen ? "Đóng chatbot" : "Mở chatbot"}
        className="fixed bottom-0 right-4 z-[100] flex h-20 w-20 items-center justify-center sm:right-6"
      >
        {isOpen ? (
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white shadow-lg dark:bg-gray-800">
            <X size={24} />
          </div>
        ) : (
          <img
            src="/mascot/tech-viet-mascot.png"
            alt="Mở Tech Việt AI"
            className="h-20 w-20 object-contain -scale-x-100"
          />
        )}
      </button>
    </>
  );
}