import { Header } from "@/components/Organisms/Header";
import { Outlet } from "react-router-dom";

const MainLayout = () => {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow max-w-6xl px-4 py-8 mx-auto sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
};
export default MainLayout;
