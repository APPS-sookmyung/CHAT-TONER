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
      {/* 공통 컨테이너 */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
