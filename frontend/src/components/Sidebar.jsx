import { NavLink } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Bot, Plus, Inbox, BarChart3, Contact, HelpCircle, FileText } from "lucide-react";

export default function Sidebar() {
  return (
    <aside className="h-screen w-64 fixed left-0 top-0 bg-surface font-['Inter'] antialiased tracking-tight text-sm flex flex-col p-4 z-50">
      <div className="mb-6 px-2 flex items-center gap-3">
        <div className="w-8 h-8 rounded-sm bg-primary-container flex items-center justify-center text-on-primary-container">
          <Bot size={20} />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tighter text-on-surface">Autonomous Manager</h1>
          <p className="text-[10px] text-on-surface-variant font-mono">v2.1.0-stable</p>
        </div>
      </div>
      
      <Button className="w-full mb-6 bg-gradient-to-br from-primary to-primary-container text-on-primary hover:opacity-90 font-semibold rounded-sm gap-2">
        <Plus size={18} />
        New Task
      </Button>

      <ScrollArea className="flex-1 -mx-4 px-4">
        <nav className="space-y-1">
          <NavLink to="/queue" className={({isActive}) => `flex items-center gap-3 px-3 py-2 rounded-sm font-medium transition-colors duration-150 ${isActive ? 'text-on-surface bg-surface-container-high' : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'}`}>
            <Inbox size={20} />
            Queue
          </NavLink>
          <NavLink to="/metrics" className={({isActive}) => `flex items-center gap-3 px-3 py-2 rounded-sm font-medium transition-colors duration-150 ${isActive ? 'text-on-surface bg-surface-container-high' : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'}`}>
            <BarChart3 size={20} />
            Analytics
          </NavLink>
          <NavLink to="/contacts" className={({isActive}) => `flex items-center gap-3 px-3 py-2 rounded-sm font-medium transition-colors duration-150 ${isActive ? 'text-on-surface bg-surface-container-high' : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'}`}>
            <Contact size={20} />
            Contacts
          </NavLink>
        </nav>
      </ScrollArea>
      
      <div className="pt-4 space-y-1 mt-auto">
        <Separator className="bg-surface-container-high mb-4" />
        <a className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-colors duration-150 rounded-sm" href="#">
          <HelpCircle size={20} /> Support
        </a>
        <a className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-colors duration-150 rounded-sm" href="#">
          <FileText size={20} /> Docs
        </a>
      </div>
    </aside>
  );
}