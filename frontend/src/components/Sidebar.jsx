import { useState } from "react";
import { NavLink } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Plus, Inbox, BarChart3, Contact, HelpCircle, FileText } from "lucide-react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";

export default function Sidebar({ mobile = false, onNavigate = () => {} }) {
  const [supportOpen, setSupportOpen] = useState(false);
  const [docsOpen, setDocsOpen] = useState(false);

  const shellClassName = mobile
    ? "flex h-full flex-col bg-surface p-4 text-sm"
    : "fixed left-0 top-0 z-50 hidden h-screen w-64 flex-col bg-surface/80 backdrop-blur-xl border-r border-surface-container-high p-4 text-sm antialiased md:flex";

  return (
    <aside className={shellClassName}>
      <div className="mb-6 px-2 flex items-center gap-3">
        <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center shadow-inner">
          <div className="w-2.5 h-2.5 rounded-full bg-white"></div>
        </div>
        <div>
          <h1 className="text-lg font-semibold tracking-tight text-on-surface">Layer</h1>
          <p className="text-[10px] text-on-surface-variant font-mono">v2.1.0</p>
        </div>
      </div>
      
      <Button className="w-full mb-6 bg-primary text-white hover:bg-primary/90 font-medium rounded-lg gap-2 shadow-sm">
        <Plus size={18} />
        New Task
      </Button>

      <ScrollArea className="flex-1 -mx-4 px-4">
        <nav className="space-y-1">
          <NavLink onClick={onNavigate} to="/app/queue" className={({isActive}) => `flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-colors duration-150 ${isActive ? 'text-primary bg-primary/5' : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'}`}>
            <Inbox size={18} />
            Queue
          </NavLink>
          <NavLink onClick={onNavigate} to="/app/metrics" className={({isActive}) => `flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-colors duration-150 ${isActive ? 'text-primary bg-primary/5' : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'}`}>
            <BarChart3 size={18} />
            Analytics
          </NavLink>
          <NavLink onClick={onNavigate} to="/app/contacts" className={({isActive}) => `flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-colors duration-150 ${isActive ? 'text-primary bg-primary/5' : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'}`}>
            <Contact size={18} />
            Contacts
          </NavLink>
        </nav>
      </ScrollArea>
      
      <div className="pt-4 space-y-1 mt-auto">
        <Separator className="bg-surface-container-high mb-4" />
        <button
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-on-surface-variant transition-colors duration-150 hover:bg-surface-container hover:text-on-surface font-medium"
          onClick={() => setSupportOpen(true)}
          type="button"
        >
          <HelpCircle size={18} /> Support
        </button>
        <button
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-on-surface-variant transition-colors duration-150 hover:bg-surface-container hover:text-on-surface font-medium"
          onClick={() => setDocsOpen(true)}
          type="button"
        >
          <FileText size={18} /> Docs
        </button>
      </div>

      <Dialog open={supportOpen} onOpenChange={setSupportOpen}>
        <DialogContent className="bg-surface border border-surface-container-high text-on-surface sm:rounded-2xl">
          <DialogHeader>
            <DialogTitle>Support</DialogTitle>
            <DialogDescription className="text-on-surface-variant">
              Need help with a triage workflow? Start with the docs, then contact the ops owner.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 text-sm text-on-surface-variant bg-surface-container-low p-4 rounded-xl border border-surface-container-high">
            <p>Primary contact: <code className="text-on-surface">support@layer.ai</code></p>
            <p>Escalation: Queue issues, delivery failures, or approval mistakes go to the support channel first.</p>
          </div>
          <DialogFooter className="pt-4">
            <Button
              variant="outline"
              className="rounded-lg"
              onClick={() => {
                setSupportOpen(false);
                setDocsOpen(true);
              }}
            >
              Open Docs
            </Button>
            <Button className="rounded-lg" onClick={() => setSupportOpen(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={docsOpen} onOpenChange={setDocsOpen}>
        <DialogContent className="bg-surface border border-surface-container-high text-on-surface sm:rounded-2xl">
          <DialogHeader>
            <DialogTitle>Docs</DialogTitle>
            <DialogDescription className="text-on-surface-variant">
              Quick references for this prototype.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 text-sm text-on-surface-variant bg-surface-container-low p-4 rounded-xl border border-surface-container-high">
            <p>Frontend: <code className="text-on-surface">npm run dev</code> in <code className="text-on-surface">frontend/</code></p>
            <p>API docs: <code className="text-on-surface">http://127.0.0.1:8000/docs</code></p>
          </div>
          <DialogFooter className="pt-4">
            <a
              className="group/button inline-flex h-9 shrink-0 items-center justify-center rounded-lg border border-border bg-background px-4 text-sm font-medium text-on-surface transition-all hover:bg-surface-container hover:text-foreground shadow-sm"
              href="http://127.0.0.1:8000/docs"
              rel="noreferrer"
              target="_blank"
            >
              Open API Docs
            </a>
            <Button className="rounded-lg" onClick={() => setDocsOpen(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </aside>
  );
}