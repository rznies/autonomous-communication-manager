import { useState, useEffect } from "react";
import { ShieldCheck, Users, Mail, MessageSquare, Bot, UserCheck } from "lucide-react";
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

function ClassBadge({ relationshipClass }) {
  const styles = {
    FREQUENT: "bg-primary/10 text-primary border-primary/20",
    PERIODIC: "bg-blue-50 text-blue-700 border-blue-200",
    TRANSACTIONAL: "bg-gray-100 text-gray-700 border-gray-200",
    AUTOMATED: "bg-surface-container text-on-surface-variant border-surface-container-high",
  };
  return (
    <Badge className={`${styles[relationshipClass] || styles.PERIODIC} border text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded shadow-sm`}>
      {relationshipClass}
    </Badge>
  );
}

export default function Contacts() {
  const [contacts, setContacts] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/contacts")
      .then(r => r.json())
      .then(data => {
        setContacts(data);
        setLoading(false);
      })
      .catch(err => {
        console.warn("Backend not available, using mock data.", err);
        setContacts([
          { id: "alice@engineering.com", relationship_class: "FREQUENT", importance_score: 15.0, interaction_count: 42, is_protected: false },
          { id: "bot@notifications.github.com", relationship_class: "AUTOMATED", importance_score: 1.2, interaction_count: 200, is_protected: false },
          { id: "investor@vc.com", relationship_class: "FREQUENT", importance_score: 20.0, interaction_count: 8, is_protected: true },
          { id: "recruiter@agency.io", relationship_class: "TRANSACTIONAL", importance_score: 3.5, interaction_count: 5, is_protected: false },
          { id: "team-lead@company.com", relationship_class: "FREQUENT", importance_score: 18.0, interaction_count: 67, is_protected: false },
          { id: "noreply@calendar.google.com", relationship_class: "AUTOMATED", importance_score: 1.0, interaction_count: 150, is_protected: false },
        ]);
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
          <h2 className="text-3xl font-bold tracking-tight text-on-surface">Contacts Directory</h2>
        </div>
        <div className="flex gap-2">
          {!loading && contacts && (
            <div className="bg-surface-container-low border border-surface-container-high px-4 py-2 rounded-lg text-xs font-medium text-on-surface-variant flex items-center gap-2 shadow-sm">
              <Users size={14} className="text-primary" />
              {contacts.length} Tracked Entities
            </div>
          )}
        </div>
      </motion.div>

      {/* Contacts list */}
      <motion.div variants={staggerContainer} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loading ? (
          <>
            <Skeleton className="h-[120px] w-full bg-surface-container-high rounded-2xl" />
            <Skeleton className="h-[120px] w-full bg-surface-container-high rounded-2xl" />
            <Skeleton className="h-[120px] w-full bg-surface-container-high rounded-2xl" />
            <Skeleton className="h-[120px] w-full bg-surface-container-high rounded-2xl" />
          </>
        ) : contacts?.map(contact => (
          <motion.div variants={fadeIn} key={contact.id}>
            <Card
              className={`bg-white border-surface-container-high hover:border-primary/30 hover:shadow-md transition-all duration-200 group rounded-2xl shadow-sm overflow-hidden ${contact.is_protected ? "ring-1 ring-primary/20" : ""}`}
            >
              <CardContent className="p-6 relative">
                {contact.is_protected && (
                  <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-bl from-primary/10 to-transparent pointer-events-none rounded-tr-2xl"></div>
                )}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-surface-container-low border border-surface-container-high flex items-center justify-center flex-shrink-0 shadow-sm">
                      {contact.relationship_class === "AUTOMATED" ? (
                        <Bot className="w-5 h-5 text-on-surface-variant" />
                      ) : contact.relationship_class === "FREQUENT" ? (
                        <UserCheck className="w-5 h-5 text-primary" />
                      ) : (
                        <Mail className="w-5 h-5 text-on-surface-variant" />
                      )}
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="text-sm font-semibold text-on-surface truncate">{contact.id}</h4>
                        {contact.is_protected && (
                          <ShieldCheck className="w-4 h-4 text-primary flex-shrink-0" />
                        )}
                      </div>
                      <div className="flex items-center gap-3">
                        <ClassBadge relationshipClass={contact.relationship_class} />
                        <span className="text-[10px] text-on-surface-variant font-medium flex items-center gap-1">
                          <MessageSquare className="w-3 h-3" />
                          {contact.interaction_count}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0 pl-4">
                    <div className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">Affinity</div>
                    <span className="text-3xl font-extrabold text-on-surface tracking-tighter block leading-none">
                      {contact.importance_score}
                    </span>
                  </div>
                </div>
                
                <div className="mt-5 h-1.5 w-full bg-surface-container rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-1000 ease-out"
                    style={{ width: `${Math.min((contact.importance_score / 25) * 100, 100)}%` }}
                  ></div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  );
}
