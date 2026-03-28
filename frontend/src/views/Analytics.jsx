import { useState, useEffect } from "react";
import { TrendingUp, TrendingDown, Zap, Inbox, ShieldCheck, AlertTriangle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { motion } from "framer-motion";

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

function HealthBadge({ correctionRate }) {
  if (correctionRate < 3) {
    return <div className="bg-green-50 text-green-700 border border-green-200 px-3 py-1 rounded-full text-xs font-bold shadow-sm">HEALTHY</div>;
  }
  if (correctionRate < 5) {
    return <div className="bg-yellow-50 text-yellow-700 border border-yellow-200 px-3 py-1 rounded-full text-xs font-bold shadow-sm">WARNING</div>;
  }
  return <div className="bg-red-50 text-red-700 border border-red-200 px-3 py-1 rounded-full text-xs font-bold shadow-sm">CRITICAL</div>;
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
    <motion.div initial="hidden" animate="visible" variants={staggerContainer} className="max-w-6xl mx-auto">
      <motion.div variants={fadeIn} className="flex justify-between items-end mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)] animate-pulse"></div>
            <span className="text-[10px] uppercase tracking-[0.15em] text-on-surface-variant font-bold">System Online</span>
          </div>
          <h2 className="text-3xl font-bold tracking-tight text-on-surface">Analytics Overview</h2>
        </div>
        <div className="flex gap-2">
          {!loading && metrics && <HealthBadge correctionRate={metrics.correction_rate} />}
        </div>
      </motion.div>

      {/* Top metric cards */}
      <motion.div variants={staggerContainer} className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {/* IDRR - Large */}
        <motion.div variants={fadeIn} className="col-span-1 md:col-span-1">
          <Card className="bg-white rounded-2xl relative overflow-hidden group border border-surface-container-high shadow-sm hover:shadow-md transition-shadow h-full">
            <CardContent className="p-8 relative z-10 h-full flex flex-col justify-between">
              <div className="flex justify-between items-start mb-4">
                <span className="text-xs font-bold uppercase tracking-widest text-on-surface-variant">IDRR</span>
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <TrendingUp className="text-primary w-4 h-4" />
                </div>
              </div>
              {loading ? (
                <Skeleton className="h-16 w-32 bg-surface-container-high" />
              ) : (
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-extrabold text-on-surface tracking-tighter">
                    {metrics?.idrr_score || 0}<span className="text-primary/50 text-3xl">%</span>
                  </span>
                </div>
              )}
              <p className="text-xs text-on-surface-variant font-medium mt-2">Inbox Decision Reduction Rate</p>
              <div className="mt-6 h-1.5 w-full bg-surface-container rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary rounded-full transition-all duration-1000 ease-out"
                  style={{ width: `${Math.min(metrics?.idrr_score || 0, 100)}%` }}
                ></div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Correction Rate */}
        <motion.div variants={fadeIn}>
          <Card className="bg-white rounded-2xl border border-surface-container-high shadow-sm hover:shadow-md transition-shadow h-full">
            <CardContent className="p-8 h-full flex flex-col justify-between">
              <div className="flex justify-between items-start mb-4">
                <span className="text-xs font-bold uppercase tracking-widest text-on-surface-variant">Correction Rate</span>
                {loading ? null : metrics?.correction_rate >= 5 ? (
                  <div className="w-8 h-8 rounded-full bg-red-50 flex items-center justify-center">
                    <AlertTriangle className="text-red-500 w-4 h-4" />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-full bg-green-50 flex items-center justify-center">
                    <TrendingDown className="text-green-600 w-4 h-4" />
                  </div>
                )}
              </div>
              <div>
                {loading ? (
                  <Skeleton className="h-10 w-24 bg-surface-container-high mb-2" />
                ) : (
                  <span className={`text-4xl font-extrabold tracking-tight block mb-1 ${metrics?.correction_rate >= 5 ? "text-red-500" : "text-on-surface"}`}>
                    {metrics?.correction_rate || 0}<span className="text-2xl text-on-surface-variant">%</span>
                  </span>
                )}
                <p className="text-xs text-on-surface-variant font-medium">
                  Target: &lt; 5% — {loading ? "..." : metrics?.correction_rate < 5 ? "On track" : "Needs attention"}
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Total Automated */}
        <motion.div variants={fadeIn}>
          <Card className="bg-white rounded-2xl border border-surface-container-high shadow-sm hover:shadow-md transition-shadow h-full">
            <CardContent className="p-8 h-full flex flex-col justify-between">
              <div className="flex justify-between items-start mb-4">
                <span className="text-xs font-bold uppercase tracking-widest text-on-surface-variant">Total Handled</span>
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
                <p className="text-xs text-on-surface-variant font-medium">Messages automated</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* Bottom summary cards */}
      <motion.div variants={staggerContainer} className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.div variants={fadeIn}>
          <Card className="bg-white rounded-2xl border border-surface-container-high shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-bold uppercase tracking-widest text-on-surface-variant">Incoming</span>
                <Inbox className="text-on-surface-variant w-5 h-5" />
              </div>
              {loading ? (
                <Skeleton className="h-8 w-20 bg-surface-container-high" />
              ) : (
                <span className="text-3xl font-extrabold text-on-surface tracking-tight">{metrics?.total_incoming || 0}</span>
              )}
              <p className="text-xs text-on-surface-variant font-medium mt-1">Total messages received</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={fadeIn}>
          <Card className="bg-white rounded-2xl border border-surface-container-high shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-bold uppercase tracking-widest text-on-surface-variant">Decisions</span>
                <ShieldCheck className="text-on-surface-variant w-5 h-5" />
              </div>
              {loading ? (
                <Skeleton className="h-8 w-20 bg-surface-container-high" />
              ) : (
                <span className="text-3xl font-extrabold text-on-surface tracking-tight">{metrics?.total_automated || 0}</span>
              )}
              <p className="text-xs text-on-surface-variant font-medium mt-1">Actions taken by layer</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={fadeIn}>
          <Card className="bg-white rounded-2xl border border-surface-container-high shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-bold uppercase tracking-widest text-on-surface-variant">Overrides</span>
                <AlertTriangle className="text-on-surface-variant w-5 h-5" />
              </div>
              {loading ? (
                <Skeleton className="h-8 w-20 bg-surface-container-high" />
              ) : (
                <span className="text-3xl font-extrabold text-on-surface tracking-tight">{metrics?.total_corrections || 0}</span>
              )}
              <p className="text-xs text-on-surface-variant font-medium mt-1">Manual user corrections</p>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
