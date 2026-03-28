import { useState } from "react";
import { NavLink } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Bot, Plus, Inbox, BarChart3, Contact, HelpCircle, FileText } from "lucide-react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";

export default function Sidebar({ mobile = false, onNavigate = () => {} }) {
  const [supportOpen, setSupportOpen] = useState(false);
  const [docsOpen, setDocsOpen] = useState(false);

  const shellClassName = mobile
    ? "flex h-full flex-col bg-surface p-4 text-sm"
    : "fixed left-0 top-0 z-50 hidden h-screen w-64 flex-col bg-surface p-4 text-sm antialiased md:flex";

  return (
    <aside className={shellClassName}>
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
          <NavLink onClick={onNavigate} to="/queue" className={({isActive}) => `flex items-center gap-3 px-3 py-2 rounded-sm font-medium transition-colors duration-150 ${isActive ? 'text-on-surface bg-surface-container-high' : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'}`}>
            <Inbox size={20} />
            Queue
          </NavLink>
          <NavLink onClick={onNavigate} to="/metrics" className={({isActive}) => `flex items-center gap-3 px-3 py-2 rounded-sm font-medium transition-colors duration-150 ${isActive ? 'text-on-surface bg-surface-container-high' : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'}`}>
            <BarChart3 size={20} />
            Analytics
          </NavLink>
          <NavLink onClick={onNavigate} to="/contacts" className={({isActive}) => `flex items-center gap-3 px-3 py-2 rounded-sm font-medium transition-colors duration-150 ${isActive ? 'text-on-surface bg-surface-container-high' : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'}`}>
            <Contact size={20} />
            Contacts
          </NavLink>
        </nav>
      </ScrollArea>
      
      <div className="pt-4 space-y-1 mt-auto">
        <Separator className="bg-surface-container-high mb-4" />
        <button
          className="flex w-full items-center gap-3 rounded-sm px-3 py-2 text-left text-on-surface-variant transition-colors duration-150 hover:bg-surface-container-high hover:text-on-surface"
          onClick={() => setSupportOpen(true)}
          type="button"
        >
          <HelpCircle size={20} /> Support
        </button>
        <button
          className="flex w-full items-center gap-3 rounded-sm px-3 py-2 text-left text-on-surface-variant transition-colors duration-150 hover:bg-surface-container-high hover:text-on-surface"
          onClick={() => setDocsOpen(true)}
          type="button"
        >
          <FileText size={20} /> Docs
        </button>
      </div>

      <Dialog open={supportOpen} onOpenChange={setSupportOpen}>
        <DialogContent className="bg-surface border border-surface-container-high text-on-surface">
          <DialogHeader>
            <DialogTitle>Support</DialogTitle>
            <DialogDescription className="text-on-surface-variant">
              Need help with a triage workflow? Start with the docs, then contact the ops owner.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 text-sm text-on-surface-variant">
            <p>Primary contact: `support@autonomous-manager.local`</p>
            <p>Escalation: Queue issues, delivery failures, or approval mistakes go to the support channel first.</p>
          </div>
          <DialogFooter className="bg-surface-container-low/60">
            <Button
              variant="outline"
              onClick={() => {
                setSupportOpen(false);
                setDocsOpen(true);
              }}
            >
              Open Docs
            </Button>
            <Button onClick={() => setSupportOpen(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={docsOpen} onOpenChange={setDocsOpen}>
        <DialogContent className="bg-surface border border-surface-container-high text-on-surface">
          <DialogHeader>
            <DialogTitle>Docs</DialogTitle>
            <DialogDescription className="text-on-surface-variant">
              Quick references for this prototype.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 text-sm text-on-surface-variant">
            <p>Frontend: `npm run dev` in `frontend/`</p>
            <p>API docs: `http://127.0.0.1:8000/docs`</p>
            <p>Core routes: Queue, Analytics, Contacts</p>
          </div>
          <DialogFooter className="bg-surface-container-low/60">
            <a
              className="group/button inline-flex h-8 shrink-0 items-center justify-center rounded-lg border border-border bg-background px-2.5 text-sm font-medium text-on-surface transition-all hover:bg-muted hover:text-foreground"
              href="http://127.0.0.1:8000/docs"
              rel="noreferrer"
              target="_blank"
            >
              Open API Docs
            </a>
            <Button onClick={() => setDocsOpen(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </aside>
  );
}
