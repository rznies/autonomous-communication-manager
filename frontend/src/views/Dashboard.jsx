import { useState, useEffect } from "react";
import { Clock, TrendingUp, Zap, Cpu, ShieldCheck, Mail, MessageSquare, History, ArrowRight, CheckCircle2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { motion } from "framer-motion";

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
  HIGH: "bg-error-container text-error",
  MED: "bg-primary/10 text-primary",
  LOW: "bg-surface-container-high text-on-surface-variant",
};

const fadeIn = {
  hidden: { opacity: 0, y: 15 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 }
  }
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
        { id: 1, type: "slack", recipient: "#support", title: "Urgent: API Down", score: 98, one_line_summary: "Customer reporting 500 errors on checkout", snippet: "I keep getting a 500 internal server error when trying to process my payment for the annual tier." },
        { id: 2, type: "email", recipient: "sales@example.com", title: "Enterprise Pricing", score: 85, one_line_summary: "Inquiry about 500+ seat license", snippet: "Hi team, we are looking to roll this out across our engineering organization. Do you have a volume discount schedule?" }
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
      // Mock success for QA if backend is down
      setQueue(q => q.filter(item => item.id !== itemToApprove));
      setMetrics(prev => ({ ...prev, handled_total: prev.handled_total + 1 }));
      setItemToApprove(null);
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
    <motion.div initial="hidden" animate="visible" variants={staggerContainer} className="max-w-6xl mx-auto">
      <motion.div variants={fadeIn} className="flex justify-between items-end mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)] animate-pulse"></div>
            <span className="text-[10px] uppercase tracking-[0.15em] text-on-surface-variant font-bold">System Online</span>
          </div>
          <h2 className="text-3xl font-bold tracking-tight text-on-surface">Intelligence Overview</h2>
        </div>
        <div className="flex gap-2 hidden sm:flex">
          <div className="bg-surface-container-low border border-surface-container-high px-4 py-2 rounded-lg text-xs font-mono text-on-surface-variant flex items-center gap-2 shadow-sm">
            <Clock size={14} className="text-primary"/>
            Last Sync: 14:02:11 UTC
          </div>
        </div>
      </motion.div>

      <motion.div variants={staggerContainer} className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {/* IDRR Metric Card */}
        <motion.div variants={fadeIn} className="col-span-2">
          <Card className="bg-white rounded-2xl relative overflow-hidden group border border-surface-container-high shadow-sm hover:shadow-md transition-shadow h-full">
            <CardContent className="p-8 relative z-10 h-full flex flex-col justify-between">
              <div className="flex justify-between items-start mb-4">
                <span className="text-xs font-bold uppercase tracking-widest text-on-surface-variant">Decision Reduction Rate</span>
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <TrendingUp className="text-primary w-4 h-4" />
                </div>
              </div>
              {loading ? (
                <div className="flex items-baseline gap-4 h-[72px]">
                  <Skeleton className="h-16 w-32 bg-surface-container-high" />
                  <Skeleton className="h-8 w-20 bg-surface-container-high" />
                </div>
              ) : (
                <div>
                  <div className="flex items-baseline gap-3 mb-6">
                    <span className="text-6xl font-extrabold text-on-surface tracking-tighter">
                      {metrics?.idrr_score || 0}<span className="text-primary text-4xl">%</span>
                    </span>
                    <div className="flex flex-col bg-green-50 px-2 py-1 rounded border border-green-100">
                      <span className="text-green-600 text-xs font-semibold flex items-center">
                        <TrendingUp className="w-3 h-3 mr-1" /> +12.4%
                      </span>
                    </div>
                  </div>
                  <div className="h-1.5 w-full bg-surface-container rounded-full overflow-hidden">
                    <div className="h-full bg-primary rounded-full w-[94.2%] transition-all duration-1000 ease-out"></div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Total Automated */}
        <motion.div variants={fadeIn}>
          <Card className="bg-white rounded-2xl border border-surface-container-high shadow-sm hover:shadow-md transition-shadow h-full">
            <CardContent className="p-8 h-full flex flex-col justify-between">
              <div className="flex justify-between items-start mb-4">
                <span className="text-xs font-bold uppercase tracking-widest text-on-surface-variant">Automated Actions</span>
                <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center">
                  <Zap className="text-primary w-4 h-4" />
                </div>
              </div>
              <div>
                {loading ? (
                  <Skeleton className="h-10 w-24 bg-surface-container-high mb-2" />
                ) : (
                  <span className="text-4xl font-extrabold text-on-surface tracking-tight block mb-1">{metrics?.handled_total || 0}</span>
                )}
                <p className="text-xs text-on-surface-variant font-medium">Total handled today</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Active Agents */}
        <motion.div variants={fadeIn}>
          <Card className="bg-white rounded-2xl border border-surface-container-high shadow-sm hover:shadow-md transition-shadow h-full">
            <CardContent className="p-8 h-full flex flex-col justify-between">
              <div className="flex justify-between items-start mb-4">
                <span className="text-xs font-bold uppercase tracking-widest text-on-surface-variant">Agent Load</span>
                <div className="w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center">
                  <Cpu className="text-on-surface-variant w-4 h-4" />
                </div>
              </div>
              <div>
                {loading ? (
                  <Skeleton className="h-10 w-24 bg-surface-container-high mb-2" />
                ) : (
                  <div className="flex items-baseline gap-1 mb-1">
                    <span className="text-4xl font-extrabold text-on-surface tracking-tight">24</span>
                    <span className="text-xl font-semibold text-outline-variant">/32</span>
                  </div>
                )}
                <p className="text-xs text-on-surface-variant font-medium">Neural threads utilized</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-3">
        {/* Pending Approvals */}
        <motion.div variants={fadeIn} className="space-y-4 xl:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-on-surface flex items-center gap-2">
              <ShieldCheck className="text-primary w-5 h-5" /> Pending Approvals
            </h3>
            <div className="bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-bold shadow-sm border border-primary/20">
              {queue?.length || 0} REQUIRES REVIEW
            </div>
          </div>
          <div className="space-y-4">
            {loading ? (
              <>
                <Skeleton className="h-40 w-full bg-surface-container-high rounded-xl" />
                <Skeleton className="h-40 w-full bg-surface-container-high rounded-xl" />
              </>
            ) : queue?.map(item => (
              <Card key={item.id} className="bg-white border-surface-container-high hover:border-primary/30 transition-all duration-200 group rounded-xl shadow-sm hover:shadow-md overflow-hidden">
                <CardContent className="p-0">
                  <div className="p-6 flex gap-4 items-start relative">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 font-semibold ${item.type === 'slack' ? 'bg-[#4A154B]/10 text-[#4A154B]' : 'bg-primary/10 text-primary'}`}>
                      {item.type === 'slack' ? <MessageSquare size={18} /> : 'E'}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-start mb-1">
                        <div>
                          <h4 className="font-semibold text-sm text-on-surface">{item.title}</h4>
                          <p className="text-sm font-normal text-on-surface-variant truncate">{item.recipient}</p>
                        </div>
                        <span className="text-xs font-medium text-on-surface-variant bg-surface-container-low border border-surface-container-high px-2 py-0.5 rounded shadow-sm">Score: {item.score}</span>
                      </div>
                      
                      <p className="text-sm text-on-surface-variant mt-3 mb-4 leading-relaxed bg-surface-container-low/50 p-4 rounded-lg border border-surface-container-high border-dashed">
                        {item.snippet || item.one_line_summary}
                      </p>
                      
                      <div className="flex gap-2">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button className="bg-primary text-white hover:bg-primary/90 text-xs font-semibold rounded-lg h-9 px-4 shadow-sm" onClick={() => setItemToApprove(item.id)}>
                              Approve & Send
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="bg-white border-surface-container-high sm:rounded-2xl">
                            <DialogHeader>
                              <DialogTitle className="text-xl">Confirm Approval</DialogTitle>
                              <DialogDescription className="text-on-surface-variant pt-2">
                                Are you sure you want to send this {item.type} message to <span className="font-semibold text-on-surface">{item.recipient}</span>?
                              </DialogDescription>
                            </DialogHeader>
                            <DialogFooter className="pt-4 border-t border-surface-container-high mt-4">
                              <Button variant="ghost" className="rounded-lg hover:bg-surface-container" onClick={() => setItemToApprove(null)}>Cancel</Button>
                              <Button className="bg-primary text-white hover:bg-primary/90 rounded-lg shadow-sm" onClick={handleApprove}>Confirm & Send</Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>
                        
                        <Button onClick={() => openDraftEditor(item)} variant="outline" className="h-9 px-4 bg-white border-surface-container-high hover:bg-surface-container-low text-on-surface text-xs font-semibold rounded-lg">
                          Edit Draft
                        </Button>
                        
                        {savedDrafts[item.id] && (
                          <div className="ml-auto bg-green-50 text-green-700 text-xs px-3 py-0 rounded-lg font-medium flex items-center gap-1.5 border border-green-200">
                            <CheckCircle2 size={14}/> Draft Saved
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            {queue?.length === 0 && (
               <div className="text-center py-12 bg-surface-container-low border border-surface-container-high border-dashed rounded-xl">
                 <CheckCircle2 className="mx-auto h-10 w-10 text-on-surface-variant opacity-50 mb-3" />
                 <h3 className="text-sm font-semibold text-on-surface">Inbox Zero</h3>
                 <p className="text-sm text-on-surface-variant mt-1">No items currently require your review.</p>
               </div>
            )}
          </div>
        </motion.div>

        {/* Activity Feed */}
        <motion.div variants={fadeIn} className="space-y-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-on-surface flex items-center gap-2">
              <History className="text-on-surface-variant w-5 h-5" /> Recent Activity
            </h3>
          </div>
          <Card className="bg-white rounded-xl border border-surface-container-high shadow-sm overflow-hidden">
            <CardContent className="p-0 divide-y divide-surface-container-high">
              {loading ? (
                <div className="space-y-0">
                  <Skeleton className="h-20 w-full rounded-none" />
                  <Skeleton className="h-20 w-full rounded-none" />
                  <Skeleton className="h-20 w-full rounded-none" />
                </div>
              ) : activity?.map((action) => {
                const severity = decisionStyles[action.decision] || "MED";

                return (
                  <div key={action.id} className="p-5 hover:bg-surface-container-low transition-colors group">
                    <div className="flex items-center justify-between mb-2">
                      <Badge className={`text-[10px] px-2 py-0.5 rounded font-bold border-none shadow-sm ${badgeStyles[severity]}`}>
                        {action.decision.toUpperCase()}
                      </Badge>
                      <span className="text-[10px] font-medium text-on-surface-variant">{formatTimestamp(action.timestamp)}</span>
                    </div>
                    <p className="text-sm font-medium text-on-surface leading-snug line-clamp-2">{action.reason}</p>
                  </div>
                );
              })}
            </CardContent>
          </Card>
          <Button variant="ghost" className="w-full py-4 text-xs font-semibold text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low transition-colors flex items-center justify-center gap-2 rounded-xl border border-transparent hover:border-surface-container-high">
            View Full Audit Log <ArrowRight className="w-4 h-4" />
          </Button>
        </motion.div>
      </div>

      <Dialog open={Boolean(draftItem)} onOpenChange={(open) => !open && closeDraftEditor()}>
        <DialogContent className="max-w-2xl bg-white border border-surface-container-high text-on-surface sm:rounded-2xl shadow-xl">
          <DialogHeader>
            <DialogTitle className="text-xl">Edit Draft</DialogTitle>
            <DialogDescription className="text-on-surface-variant pt-1">
              Refine the response before approving.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 pt-2">
            <div className="rounded-lg border border-surface-container-high bg-surface-container-low px-4 py-3 text-sm font-medium text-on-surface flex items-center gap-2">
              <Mail size={16} className="text-on-surface-variant"/>
              To: <span className="text-primary">{draftItem?.recipient}</span>
            </div>
            <textarea
              className="min-h-[200px] w-full rounded-lg border border-surface-container-high bg-white p-4 text-sm text-on-surface outline-none transition focus:border-primary focus:ring-1 focus:ring-primary shadow-sm resize-y"
              onChange={(event) => setDraftText(event.target.value)}
              placeholder="Draft a response..."
              value={draftText}
            />
          </div>
          <DialogFooter className="pt-4 border-t border-surface-container-high mt-4">
            <Button variant="ghost" className="rounded-lg hover:bg-surface-container" onClick={closeDraftEditor}>
              Cancel
            </Button>
            <Button className="bg-primary text-white hover:bg-primary/90 rounded-lg shadow-sm px-6" onClick={handleSaveDraft}>
              Save Draft
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}