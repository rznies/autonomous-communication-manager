import { useState, useEffect } from "react";
import { Clock, TrendingUp, Zap, Cpu, ShieldCheck, Mail, MessageSquare, History, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

const fallbackActivity = [
  { id: "fallback-1", decision: "urgent", reason: "Investor email identified, flagged for review", timestamp: Date.now() / 1000, is_reversible: true },
  { id: "fallback-2", decision: "archive", reason: "Dependabot alert archived, no action needed", timestamp: Date.now() / 1000 - 240, is_reversible: true },
  { id: "fallback-3", decision: "normal", reason: "Sales inquiry drafted for pricing review", timestamp: Date.now() / 1000 - 900, is_reversible: true },
];

const decisionStyles = {
  urgent: "HIGH",
  archive: "LOW",
  normal: "MED",
  low: "LOW",
};

const badgeStyles = {
  HIGH: "bg-error-container/30 text-error",
  MED: "bg-secondary-container/30 text-secondary",
  LOW: "bg-surface-container-highest text-on-surface-variant",
};

function formatTimestamp(timestamp) {
  return new Date(timestamp * 1000).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [queue, setQueue] = useState(null);
  const [activity, setActivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [itemToApprove, setItemToApprove] = useState(null);
  const [draftItem, setDraftItem] = useState(null);
  const [draftText, setDraftText] = useState("");
  const [savedDrafts, setSavedDrafts] = useState({});

  const openDraftEditor = (item) => {
    setDraftItem(item);
    setDraftText(savedDrafts[item.id] ?? `Reply to ${item.recipient} about ${item.title}.`);
  };

  const closeDraftEditor = () => {
    setDraftItem(null);
    setDraftText("");
  };

  useEffect(() => {
    Promise.all([
      fetch("/api/metrics").then(r => r.json()),
      fetch("/api/queue").then(r => r.json()),
      fetch("/api/activity").then(r => r.json()),
    ])
    .then(([metricsData, queueData, activityData]) => {
      setMetrics(metricsData);
      setQueue(queueData);
      setActivity(activityData);
      setLoading(false);
    })
    .catch(err => {
      console.warn("Backend not available, using mock data for visual QA.", err);
      setMetrics({ idrr_score: 94.2, correction_rate: 2.1, handled_total: 1284 });
      setQueue([
        { id: 1, type: "slack", recipient: "#support", title: "Urgent: API Down", score: 98, one_line_summary: "Customer reporting 500 errors on checkout", snippet: "..." },
        { id: 2, type: "email", recipient: "sales@example.com", title: "Enterprise Pricing", score: 85, one_line_summary: "Inquiry about 500+ seat license", snippet: "..." }
      ]);
      setActivity(fallbackActivity);
      setLoading(false);
    });
  }, []);

  const handleApprove = async () => {
    if (!itemToApprove) return;
    try {
      const response = await fetch(`/api/queue/${itemToApprove}/approve`, { method: 'POST' });
      const data = await response.json();

      setQueue(q => q.filter(item => item.id !== itemToApprove));
      setMetrics(prev => ({ ...prev, handled_total: prev.handled_total + 1 }));
      if (data.action) {
        setActivity(prev => [data.action, ...(prev ?? [])]);
      }
      setItemToApprove(null);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSaveDraft = () => {
    if (!draftItem) return;

    setSavedDrafts((current) => ({
      ...current,
      [draftItem.id]: draftText,
    }));
    closeDraftEditor();
  };

  return (
    <>
      <div className="flex justify-between items-end mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2 rounded-full bg-tertiary animate-pulse"></div>
            <span className="text-[10px] uppercase tracking-[0.2em] text-tertiary font-bold">System Online</span>
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight">Intelligence Overview</h2>
        </div>
        <div className="flex gap-2">
          <Badge variant="outline" className="bg-surface-container-low px-4 py-2 rounded-sm text-xs font-mono text-on-surface-variant flex items-center gap-2 border-none">
            <Clock size={14} />
            Last Sync: 14:02:11 UTC
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {/* IDRR Metric Card */}
        <Card className="col-span-2 bg-surface-container-low rounded-sm relative overflow-hidden group border-none">
          <CardContent className="p-6 relative z-10">
            <div className="flex justify-between items-start mb-4">
              <span className="text-xs font-medium uppercase tracking-widest text-on-surface-variant">Inbox Decision Reduction Rate</span>
              <TrendingUp className="text-primary w-5 h-5" />
            </div>
            {loading ? (
              <div className="flex items-baseline gap-4 h-[72px]">
                <Skeleton className="h-16 w-32 bg-surface-container-high" />
                <Skeleton className="h-8 w-20 bg-surface-container-high" />
              </div>
            ) : (
              <div className="flex items-baseline gap-4">
                <span className="text-6xl font-extrabold mono-numeric text-on-surface tracking-tighter">
                  {metrics?.idrr_score || 0}<span className="text-primary/50">%</span>
                </span>
                <div className="flex flex-col">
                  <span className="text-tertiary text-xs font-mono flex items-center">
                    <TrendingUp className="w-3.5 h-3.5 mr-1" /> +12.4%
                  </span>
                  <span className="text-[10px] text-outline">vs last 24h</span>
                </div>
              </div>
            )}
            <div className="mt-6 h-1 w-full bg-surface-container-highest rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-primary-container to-primary w-[94.2%]"></div>
            </div>
          </CardContent>
          {/* Background Glow */}
          <div className="absolute -right-12 -top-12 w-48 h-48 bg-primary/5 blur-[80px] rounded-full group-hover:bg-primary/10 transition-colors"></div>
        </Card>

        {/* Total Automated */}
        <Card className="bg-surface-container-low rounded-sm border-none">
          <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
              <span className="text-xs font-medium uppercase tracking-widest text-on-surface-variant">Automated Actions</span>
              <Zap className="text-tertiary w-5 h-5" />
            </div>
            {loading ? (
              <Skeleton className="h-10 w-24 bg-surface-container-high mb-2" />
            ) : (
              <span className="text-4xl font-extrabold mono-numeric text-on-surface tracking-tighter">{metrics?.handled_total || 0}</span>
            )}
            <p className="text-[10px] text-on-surface-variant mt-2 font-mono">Total handled today</p>
          </CardContent>
        </Card>

        {/* Active Agents */}
        <Card className="bg-surface-container-low rounded-sm border-l-2 border-primary-container border-y-0 border-r-0">
          <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
              <span className="text-xs font-medium uppercase tracking-widest text-on-surface-variant">Agent Load</span>
              <Cpu className="text-on-surface-variant w-5 h-5" />
            </div>
            {loading ? (
              <Skeleton className="h-10 w-24 bg-surface-container-high mb-2" />
            ) : (
              <span className="text-4xl font-extrabold mono-numeric text-on-surface tracking-tighter">
                24<span className="text-lg text-outline">/32</span>
              </span>
            )}
            <p className="text-[10px] text-on-surface-variant mt-2 font-mono">Neural threads utilized</p>
          </CardContent>
        </Card>
      </div>

       <div className="grid grid-cols-1 gap-8 xl:grid-cols-3">
         {/* Pending Approvals */}
         <div className="space-y-4 xl:col-span-2">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-bold uppercase tracking-[0.15em] flex items-center gap-2">
              <ShieldCheck className="text-primary w-5 h-5" /> Pending Approvals
            </h3>
            <Badge variant="outline" className="bg-primary/10 text-primary border-none rounded-full text-[10px] font-bold">
              {queue?.length || 0} ACTION REQUIRED
            </Badge>
          </div>
          <div className="space-y-3">
            {loading ? (
              <>
                <Skeleton className="h-32 w-full bg-surface-container-high rounded-sm" />
                <Skeleton className="h-32 w-full bg-surface-container-high rounded-sm" />
              </>
            ) : queue?.map(item => (
              <Card key={item.id} className="bg-surface-container-high border-transparent hover:border-outline-variant/30 transition-all group rounded-sm shadow-none">
                <CardContent className="p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-sm bg-surface-container-highest flex items-center justify-center">
                        {item.type === 'slack' ? (
                          <MessageSquare className="w-4 h-4 text-[#4A154B]" />
                        ) : (
                          <Mail className="w-4 h-4 text-on-surface-variant" />
                        )}
                      </div>
                      <div>
                        <h4 className="text-xs font-bold text-on-surface">{item.title}</h4>
                        <p className="text-[10px] text-on-surface-variant">{item.type.charAt(0).toUpperCase() + item.type.slice(1)}: {item.recipient}</p>
                      </div>
                    </div>
                    <div className="text-[10px] font-mono text-outline">Score: {item.score}</div>
                  </div>
                     <div className="bg-surface-container-lowest p-3 rounded-sm text-xs font-mono text-on-surface-variant mb-4 leading-relaxed line-clamp-2 font-bold">
                       {item.one_line_summary || item.snippet || "No summary available"}
                     </div>
                     {savedDrafts[item.id] && (
                       <div className="mb-4 rounded-sm border border-primary/20 bg-primary/8 px-3 py-2 text-[10px] font-mono text-primary">
                         Draft updated and ready to review.
                       </div>
                     )}
                     <div className="flex gap-2">
                       <Dialog>
                      <DialogTrigger
                        render={<Button variant="outline" className="flex-1 bg-primary/10 hover:bg-primary/20 text-primary border-none text-[10px] font-bold uppercase tracking-widest rounded-sm" />}
                        onClick={() => setItemToApprove(item.id)}
                      >
                        Approve & Send
                      </DialogTrigger>
                      <DialogContent className="bg-surface border-surface-container-highest">
                        <DialogHeader>
                          <DialogTitle>Confirm Approval</DialogTitle>
                          <DialogDescription className="text-on-surface-variant">
                            Are you sure you want to approve this {item.type} message to {item.recipient}? This action cannot be undone.
                          </DialogDescription>
                        </DialogHeader>
                        <DialogFooter>
                          <Button variant="ghost" className="text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high" onClick={() => setItemToApprove(null)}>Cancel</Button>
                          <Button variant="default" className="bg-primary text-on-primary hover:bg-primary/90" onClick={handleApprove}>Confirm & Send</Button>
                        </DialogFooter>
                      </DialogContent>
                       </Dialog>
                      <Button onClick={() => openDraftEditor(item)} variant="secondary" className="px-4 bg-surface-container-highest hover:bg-surface-variant text-on-surface border-none text-[10px] font-bold uppercase tracking-widest rounded-sm">
                        Edit Draft
                      </Button>
                     </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Activity Feed */}
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-bold uppercase tracking-[0.15em] flex items-center gap-2">
              <History className="text-tertiary w-5 h-5" /> Recent Activity
            </h3>
          </div>
           <Card className="bg-surface-container-low rounded-sm border-none overflow-hidden">
             <CardContent className="p-0 divide-y divide-[#1c1c1c]">
               {loading ? (
                 <div className="space-y-3 p-4">
                   <Skeleton className="h-16 w-full bg-surface-container-high rounded-sm" />
                   <Skeleton className="h-16 w-full bg-surface-container-high rounded-sm" />
                   <Skeleton className="h-16 w-full bg-surface-container-high rounded-sm" />
                 </div>
               ) : activity?.map((action) => {
                 const severity = decisionStyles[action.decision] || "MED";

                 return (
                   <div key={action.id} className="p-4 hover:bg-surface-container-high transition-colors">
                     <div className="flex items-center justify-between mb-1 gap-2">
                       <span className="text-[10px] font-mono text-on-surface-variant">{formatTimestamp(action.timestamp)}</span>
                       <Badge className={`text-[10px] px-1.5 py-0 rounded-sm font-bold border-none ${badgeStyles[severity]}`}>
                         {severity}
                       </Badge>
                     </div>
                     <p className="text-xs font-medium text-on-surface mb-1">Triage: {action.decision}</p>
                     <p className="text-[10px] text-on-surface-variant line-clamp-2">{action.reason}</p>
                   </div>
                 );
               })}
             </CardContent>
           </Card>
          <Button variant="ghost" className="w-full py-2 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant hover:text-on-surface hover:bg-transparent transition-colors flex items-center justify-center gap-2">
            View Full Audit Log <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <Dialog open={Boolean(draftItem)} onOpenChange={(open) => !open && closeDraftEditor()}>
        <DialogContent className="max-w-xl bg-surface border border-surface-container-high text-on-surface">
          <DialogHeader>
            <DialogTitle>Edit Draft</DialogTitle>
            <DialogDescription className="text-on-surface-variant">
              Review the outbound message before an operator approves it.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="rounded-sm border border-surface-container-high bg-surface-container-low px-3 py-2 text-[10px] font-mono text-on-surface-variant">
              {draftItem?.recipient} · {draftItem?.title}
            </div>
            <textarea
              className="min-h-40 w-full rounded-sm border border-surface-container-high bg-surface-container-low p-3 text-sm text-on-surface outline-none transition focus:border-primary/40"
              onChange={(event) => setDraftText(event.target.value)}
              placeholder="Draft a response..."
              value={draftText}
            />
          </div>
          <DialogFooter className="bg-surface-container-low/60">
            <Button variant="outline" onClick={closeDraftEditor}>
              Cancel
            </Button>
            <Button onClick={handleSaveDraft}>Save Draft</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
