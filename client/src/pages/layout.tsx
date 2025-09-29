import { ReactNode } from "react";
import Header from "@/components/ui/header";

/**
 * 공통 레이아웃:
 * - 상단 헤더 고정
 * - 모든 페이지에 일관된 구조 제공
 */
export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50 font-korean">
      <Header />
      {/* Common container */}
      <main className="max-w-6xl px-4 py-8 mx-auto sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
