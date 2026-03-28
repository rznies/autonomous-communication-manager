import { Menu, Search, Bell, ChevronDown } from "lucide-react";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";

export default function TopBar({ onOpenMobileNav }) {
  return (
    <header className="fixed inset-x-0 top-0 z-40 flex h-14 items-center justify-between border-b border-surface-container-high bg-surface/80 px-4 backdrop-blur-xl md:left-64 md:px-6">
      <div className="flex items-center gap-3 md:gap-0">
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface md:hidden"
          onClick={onOpenMobileNav}
        >
          <Menu className="h-4 w-4" />
          <span className="sr-only">Open navigation</span>
        </Button>
        <span className="mr-0 text-sm font-black text-on-surface md:mr-8">AUTONOMOUS AI</span>
        <div className="group hidden w-64 items-center rounded-sm border border-transparent bg-surface-container-lowest px-3 py-1.5 transition-all focus-within:border-primary/20 sm:flex">
          <Search className="text-on-surface-variant w-3.5 h-3.5 mr-2" />
          <input className="bg-transparent border-none outline-none focus:ring-0 text-xs w-full text-on-surface p-0 placeholder:text-outline/50" placeholder="Quick Search" type="text"/>
          <span className="text-[10px] text-outline/40 font-mono">⌘K</span>
        </div>
      </div>

      <div className="flex items-center gap-3 md:gap-6">
        <nav className="hidden space-x-6 font-['Inter'] text-xs font-medium uppercase tracking-widest lg:flex">
          <a className="text-on-surface-variant hover:text-on-surface transition-all" href="#">Workspace</a>
          <a className="text-primary-container border-b border-primary-container pb-1" href="#">Agent Active</a>
        </nav>
        
        <div className="flex items-center gap-2 md:gap-4">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger
                render={<Button variant="ghost" size="icon" className="h-8 w-8 text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high" />}
              >
                <Bell className="h-4 w-4" />
              </TooltipTrigger>
              <TooltipContent>
                <p>Notifications</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          
          <div className="flex cursor-pointer items-center gap-2 rounded-full bg-surface-container-high py-1 pl-1 pr-2 transition-all active:scale-[0.98] md:pr-3">
            <Avatar className="w-6 h-6">
              <AvatarImage src="https://lh3.googleusercontent.com/aida-public/AB6AXuCYxyplhPAPwqnOqpmNiQ4-PeRuRuw7hoSn3KDf2XB-Z_upQgks_FbH0PPm9JVED_zgEXlE3eWk6MIV87YfVGiFFMfgUlwBfwMBSRtqlYW0frYrzLgIORqmoS0JAnXKl-JDqXqGXf67AB1aDspNUkM-2WelrYvbi-BGxv2dBfVeI27eJwcVq5NtGwkMLVgPhOnFka69vUVv-XW1Df__hln3ctQmZkNkGSOC1gAt-2HGu_1qUbyk2WvrNfMCK3mWeYVu3Ri02En3HkQ-" alt="user avatar"/>
              <AvatarFallback className="text-[10px] bg-primary text-on-primary">DV</AvatarFallback>
            </Avatar>
            <span className="hidden text-[10px] font-bold text-on-surface sm:inline">DR. VECTOR</span>
            <ChevronDown className="w-3 h-3 text-on-surface-variant" />
          </div>
        </div>
      </div>
    </header>
  );
}
