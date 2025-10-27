import { Outlet } from "react-router-dom";

const Layout = () => {
  return (
    <div className="relative">
      <div className="absolute z-10 left-[52px] top-[30px] text-black text-center font-roboto text-[32px] font-medium leading-normal">
        chat toner
      </div>
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
