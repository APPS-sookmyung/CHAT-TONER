import { Header } from "@/components/Organisms/Header";
import { Outlet } from "react-router-dom";

const MainLayout = () => {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow flex flex-col items-center py-4 mx-auto w-full max-w-7xl px-8">
        <Outlet />
      </main>
    </div>
  );
};
export default MainLayout;
