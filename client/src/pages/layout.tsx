import { ReactNode } from "react";
import Header from "@/components/ui/header";

/**
 * Common Layout:
 * - Fixed top header
 * - Provides a consistent structure for all pages
 */
export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <Header />
      {/* Common container */}
      <main className="max-w-6xl px-4 py-8 mx-auto sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
