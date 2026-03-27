import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";

export default function Layout() {
  return (
    <div className="min-h-screen bg-surface text-on-surface font-body selection:bg-primary/30 antialiased">
      <Sidebar />
      <TopBar />
      <main className="ml-64 mt-14 p-8">
        <Outlet />
      </main>
    </div>
  );
}
