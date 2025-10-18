import { Outlet } from "react-router-dom";

const Layout = () => {
  return (
    <div>
      <div className="absolute l-[52px] t-[30px] text-black text-center font-roboto text-[32px] font-medium leading-normal">
        chat toner
      </div>
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
