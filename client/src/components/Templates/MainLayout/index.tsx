import { Header } from "@/components/Organisms/Header";
import { Outlet } from "react-router-dom";

const MainLayout = () => {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow py-8 mx-auto">
        <Outlet />
      </main>
    </div>
  );
};
export default MainLayout;
