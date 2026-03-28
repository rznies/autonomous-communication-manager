import { Menu, Search, Bell, ChevronDown, Command } from "lucide-react";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";

export default function TopBar({ onOpenMobileNav }) {
  return (
    <header className="fixed inset-x-0 top-0 z-40 flex h-16 items-center justify-between border-b border-surface-container-high bg-white/80 px-4 backdrop-blur-xl md:left-64 md:px-6 transition-all">
      <div className="flex items-center gap-4 md:gap-0">
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 text-on-surface-variant hover:bg-surface-container hover:text-on-surface md:hidden"
          onClick={onOpenMobileNav}
        >
          <Menu className="h-5 w-5" />
          <span className="sr-only">Open navigation</span>
        </Button>
        <span className="mr-0 text-sm font-semibold text-on-surface md:mr-8 hidden md:block">Dashboard</span>
        
        {/* Apple-style search bar */}
        <div className="group hidden w-72 items-center rounded-lg border border-surface-container-high bg-surface-container-low px-3 py-2 shadow-sm transition-all focus-within:border-primary/30 focus-within:ring-2 focus-within:ring-primary/10 sm:flex hover:bg-white hover:border-surface-container-highest">
          <Search className="text-on-surface-variant w-4 h-4 mr-2" />
          <input className="bg-transparent border-none outline-none focus:ring-0 text-sm w-full text-on-surface p-0 placeholder:text-outline-variant font-medium" placeholder="Search across apps..." type="text"/>
          <div className="flex items-center gap-0.5 text-[10px] text-on-surface-variant font-medium bg-surface-container px-1.5 py-0.5 rounded border border-surface-container-high">
            <Command size={10} />K
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3 md:gap-6">
        <nav className="hidden space-x-6 font-['Inter'] text-sm font-medium lg:flex">
          <a className="text-primary border-b-2 border-primary pb-[21px] pt-[21px]" href="#">Overview</a>
          <a className="text-on-surface-variant hover:text-on-surface transition-all pb-[21px] pt-[21px]" href="#">Activity</a>
          <a className="text-on-surface-variant hover:text-on-surface transition-all pb-[21px] pt-[21px]" href="#">Settings</a>
        </nav>
        
        <div className="flex items-center gap-2 md:gap-4">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="h-9 w-9 rounded-full text-on-surface-variant hover:text-on-surface hover:bg-surface-container relative">
                  <Bell className="h-5 w-5" />
                  <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full border-2 border-white"></span>
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Notifications</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          
          <div className="flex cursor-pointer items-center gap-2.5 rounded-full border border-surface-container-high bg-surface-container-lowest py-1.5 pl-1.5 pr-3 transition-all hover:bg-surface-container-low hover:border-surface-container-highest active:scale-[0.98] shadow-sm md:pr-4">
            <Avatar className="w-7 h-7 ring-2 ring-white">
              <AvatarImage src="https://ui-avatars.com/api/?name=Steve+Jobs&background=0F172A&color=fff" alt="user avatar"/>
              <AvatarFallback className="text-xs bg-primary text-white font-medium">SJ</AvatarFallback>
            </Avatar>
            <span className="hidden text-sm font-semibold text-on-surface sm:inline">Steve</span>
            <ChevronDown className="w-4 h-4 text-on-surface-variant opacity-70" />
          </div>
        </div>
      </div>
    </header>
  );
}
