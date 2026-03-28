import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";
import { Sheet, SheetContent } from "@/components/ui/sheet";

export default function Layout() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="min-h-screen bg-surface text-on-surface font-body selection:bg-primary/30 antialiased">
      <Sidebar />
      <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
        <SheetContent
          side="left"
          className="w-[88vw] max-w-xs border-surface-container-high bg-surface p-0 text-on-surface"
        >
          <Sidebar mobile onNavigate={() => setMobileNavOpen(false)} />
        </SheetContent>
      </Sheet>
      <TopBar onOpenMobileNav={() => setMobileNavOpen(true)} />
      <main className="px-4 pb-6 pt-20 md:ml-64 md:mt-14 md:p-8">
        <Outlet />
      </main>
    </div>
  );
}
