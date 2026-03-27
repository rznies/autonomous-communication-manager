import { useState, useEffect } from "react";
import { Clock, TrendingUp, Zap, Cpu, ShieldCheck, Mail, MessageSquare, History, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [queue, setQueue] = useState(null);
  const [loading, setLoading] = useState(true);
  const [itemToApprove, setItemToApprove] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch("http://127.0.0.1:8000/api/metrics").then(r => r.json()),
      fetch("http://127.0.0.1:8000/api/queue").then(r => r.json())
    ])
    .then(([metricsData, queueData]) => {
      setMetrics(metricsData);
      setQueue(queueData);
      setLoading(false);
    })
    .catch(err => {
      console.warn("Backend not available, using mock data for visual QA.", err);
      setMetrics({ idrr_score: 94.2, correction_rate: 2.1, handled_total: 1284 });
      setQueue([
        { id: 1, type: "slack", recipient: "#support", title: "Urgent: API Down", score: 98, one_line_summary: "Customer reporting 500 errors on checkout", snippet: "..." },
        { id: 2, type: "email", recipient: "sales@example.com", title: "Enterprise Pricing", score: 85, one_line_summary: "Inquiry about 500+ seat license", snippet: "..." }
      ]);
      setLoading(false);
    });
  }, []);

  const handleApprove = async () => {
    if (!itemToApprove) return;
    try {
      await fetch(`http://127.0.0.1:8000/api/queue/${itemToApprove}/approve`, { method: 'POST' });
      setQueue(q => q.filter(item => item.id !== itemToApprove));
      setMetrics(prev => ({ ...prev, handled_total: prev.handled_total + 1 }));
      setItemToApprove(null);
    } catch (e) {
      console.error(e);
    }
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Pending Approvals */}
        <div className="lg:col-span-2 space-y-4">
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
                  <div className="flex gap-2">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button 
                          variant="outline" 
                          className="flex-1 bg-primary/10 hover:bg-primary/20 text-primary border-none text-[10px] font-bold uppercase tracking-widest rounded-sm"
                          onClick={() => setItemToApprove(item.id)}
                        >
                          Approve & Send
                        </Button>
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
                    <Button variant="secondary" className="px-4 bg-surface-container-highest hover:bg-surface-variant text-on-surface border-none text-[10px] font-bold uppercase tracking-widest rounded-sm">
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
              <div className="p-4 hover:bg-surface-container-high transition-colors">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-mono text-tertiary">14:22:01</span>
                  <Badge className="text-[10px] px-1.5 py-0 rounded-sm bg-error-container/30 text-error font-bold border-none">HIGH</Badge>
                </div>
                <p className="text-xs font-medium text-on-surface mb-1">Triage: Support Slack</p>
                <p className="text-[10px] text-on-surface-variant line-clamp-1">Auto-assigned to Critical Engineering team.</p>
              </div>
              <div className="p-4 hover:bg-surface-container-high transition-colors">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-mono text-on-surface-variant">14:18:45</span>
                  <Badge variant="secondary" className="text-[10px] px-1.5 py-0 rounded-sm bg-surface-container-highest text-on-surface-variant font-bold border-none">LOW</Badge>
                </div>
                <p className="text-xs font-medium text-on-surface mb-1">Triage: GitHub Notification</p>
                <p className="text-[10px] text-on-surface-variant line-clamp-1">Dependabot alert archived - No action needed.</p>
              </div>
              <div className="p-4 hover:bg-surface-container-high transition-colors">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-mono text-on-surface-variant">14:05:12</span>
                  <Badge className="text-[10px] px-1.5 py-0 rounded-sm bg-secondary-container/30 text-secondary font-bold border-none">MED</Badge>
                </div>
                <p className="text-xs font-medium text-on-surface mb-1">Triage: Sales Email</p>
                <p className="text-[10px] text-on-surface-variant line-clamp-1">Drafted custom response for pricing inquiry.</p>
              </div>
            </CardContent>
          </Card>
          <Button variant="ghost" className="w-full py-2 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant hover:text-on-surface hover:bg-transparent transition-colors flex items-center justify-center gap-2">
            View Full Audit Log <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </>
  );
}