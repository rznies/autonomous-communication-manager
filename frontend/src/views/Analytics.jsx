import { useState, useEffect } from "react";
import { TrendingUp, TrendingDown, Zap, Inbox, ShieldCheck, AlertTriangle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

function HealthBadge({ correctionRate }) {
  if (correctionRate < 3) {
    return <Badge className="bg-tertiary/20 text-tertiary border-none text-[10px] font-bold uppercase tracking-widest">Healthy</Badge>;
  }
  if (correctionRate < 5) {
    return <Badge className="bg-warning/20 text-warning border-none text-[10px] font-bold uppercase tracking-widest">Warning</Badge>;
  }
  return <Badge className="bg-error/20 text-error border-none text-[10px] font-bold uppercase tracking-widest">Critical</Badge>;
}

export default function Analytics() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/metrics")
      .then(r => r.json())
      .then(data => {
        setMetrics(data);
        setLoading(false);
      })
      .catch(err => {
        console.warn("Backend not available, using mock data.", err);
        setMetrics({
          idrr_score: 94.2,
          correction_rate: 2.1,
          handled_total: 1284,
          total_incoming: 1362,
          total_automated: 1284,
          total_corrections: 27,
        });
        setLoading(false);
      });
  }, []);

  return (
    <>
      <div className="flex justify-between items-end mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2 rounded-full bg-tertiary animate-pulse"></div>
            <span className="text-[10px] uppercase tracking-[0.2em] text-tertiary font-bold">System Online</span>
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight">Analytics</h2>
        </div>
        <div className="flex gap-2">
          {!loading && metrics && <HealthBadge correctionRate={metrics.correction_rate} />}
        </div>
      </div>

      {/* Top metric cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {/* IDRR - Large */}
        <Card className="col-span-1 md:col-span-1 bg-surface-container-low rounded-sm relative overflow-hidden group border-none">
          <CardContent className="p-6 relative z-10">
            <div className="flex justify-between items-start mb-4">
              <span className="text-xs font-medium uppercase tracking-widest text-on-surface-variant">IDRR</span>
              <TrendingUp className="text-primary w-5 h-5" />
            </div>
            {loading ? (
              <Skeleton className="h-16 w-32 bg-surface-container-high" />
            ) : (
              <div className="flex items-baseline gap-2">
                <span className="text-5xl font-extrabold mono-numeric text-on-surface tracking-tighter">
                  {metrics?.idrr_score || 0}<span className="text-primary/50 text-lg">%</span>
                </span>
              </div>
            )}
            <p className="text-[10px] text-on-surface-variant mt-2 font-mono">Inbox Decision Reduction Rate</p>
            <div className="mt-4 h-1 w-full bg-surface-container-highest rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-primary-container to-primary transition-all"
                style={{ width: `${Math.min(metrics?.idrr_score || 0, 100)}%` }}
              ></div>
            </div>
          </CardContent>
          <div className="absolute -right-12 -top-12 w-48 h-48 bg-primary/5 blur-[80px] rounded-full group-hover:bg-primary/10 transition-colors"></div>
        </Card>

        {/* Correction Rate */}
        <Card className="bg-surface-container-low rounded-sm border-none">
          <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
              <span className="text-xs font-medium uppercase tracking-widest text-on-surface-variant">Correction Rate</span>
              {loading ? null : metrics?.correction_rate >= 5 ? (
                <AlertTriangle className="text-error w-5 h-5" />
              ) : (
                <TrendingDown className="text-tertiary w-5 h-5" />
              )}
            </div>
            {loading ? (
              <Skeleton className="h-10 w-24 bg-surface-container-high mb-2" />
            ) : (
              <span className={`text-4xl font-extrabold mono-numeric tracking-tighter ${metrics?.correction_rate >= 5 ? "text-error" : "text-on-surface"}`}>
                {metrics?.correction_rate || 0}<span className="text-lg text-outline">%</span>
              </span>
            )}
            <p className="text-[10px] text-on-surface-variant mt-2 font-mono">
              Target: &lt; 5% — {loading ? "..." : metrics?.correction_rate < 5 ? "On track" : "Needs attention"}
            </p>
          </CardContent>
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
            <p className="text-[10px] text-on-surface-variant mt-2 font-mono">Total handled</p>
          </CardContent>
        </Card>
      </div>

      {/* Bottom summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-surface-container-low rounded-sm border-none">
          <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
              <span className="text-xs font-medium uppercase tracking-widest text-on-surface-variant">Total Incoming</span>
              <Inbox className="text-on-surface-variant w-5 h-5" />
            </div>
            {loading ? (
              <Skeleton className="h-8 w-20 bg-surface-container-high" />
            ) : (
              <span className="text-2xl font-extrabold mono-numeric text-on-surface tracking-tighter">{metrics?.total_incoming || 0}</span>
            )}
            <p className="text-[10px] text-on-surface-variant mt-2 font-mono">Messages received</p>
          </CardContent>
        </Card>

        <Card className="bg-surface-container-low rounded-sm border-none">
          <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
              <span className="text-xs font-medium uppercase tracking-widest text-on-surface-variant">Automated</span>
              <ShieldCheck className="text-on-surface-variant w-5 h-5" />
            </div>
            {loading ? (
              <Skeleton className="h-8 w-20 bg-surface-container-high" />
            ) : (
              <span className="text-2xl font-extrabold mono-numeric text-on-surface tracking-tighter">{metrics?.total_automated || 0}</span>
            )}
            <p className="text-[10px] text-on-surface-variant mt-2 font-mono">Decisions made by agent</p>
          </CardContent>
        </Card>

        <Card className="bg-surface-container-low rounded-sm border-none">
          <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
              <span className="text-xs font-medium uppercase tracking-widest text-on-surface-variant">Corrections</span>
              <AlertTriangle className="text-on-surface-variant w-5 h-5" />
            </div>
            {loading ? (
              <Skeleton className="h-8 w-20 bg-surface-container-high" />
            ) : (
              <span className="text-2xl font-extrabold mono-numeric text-on-surface tracking-tighter">{metrics?.total_corrections || 0}</span>
            )}
            <p className="text-[10px] text-on-surface-variant mt-2 font-mono">User overrides</p>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
