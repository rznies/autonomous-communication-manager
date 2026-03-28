import { useState, useEffect } from "react";
import { ShieldCheck, Users, Mail, MessageSquare, Bot, UserCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

function ClassBadge({ relationshipClass }) {
  const styles = {
    FREQUENT: "bg-primary/15 text-primary",
    PERIODIC: "bg-secondary/15 text-secondary",
    TRANSACTIONAL: "bg-tertiary/15 text-tertiary",
    AUTOMATED: "bg-surface-container-highest text-on-surface-variant",
  };
  return (
    <Badge className={`${styles[relationshipClass] || styles.PERIODIC} border-none text-[10px] font-bold uppercase tracking-widest`}>
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
    <>
      <div className="flex justify-between items-end mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2 rounded-full bg-tertiary animate-pulse"></div>
            <span className="text-[10px] uppercase tracking-[0.2em] text-tertiary font-bold">System Online</span>
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight">Contacts</h2>
        </div>
        <div className="flex gap-2">
          {!loading && contacts && (
            <Badge variant="outline" className="bg-surface-container-low px-4 py-2 rounded-sm text-xs font-mono text-on-surface-variant flex items-center gap-2 border-none">
              <Users size={14} />
              {contacts.length} contacts tracked
            </Badge>
          )}
        </div>
      </div>

      {/* Contacts list */}
      <div className="space-y-3">
        {loading ? (
          <>
            <Skeleton className="h-20 w-full bg-surface-container-high rounded-sm" />
            <Skeleton className="h-20 w-full bg-surface-container-high rounded-sm" />
            <Skeleton className="h-20 w-full bg-surface-container-high rounded-sm" />
            <Skeleton className="h-20 w-full bg-surface-container-high rounded-sm" />
          </>
        ) : contacts?.map(contact => (
          <Card
            key={contact.id}
            className={`bg-surface-container-low border-transparent hover:border-outline-variant/30 transition-all group rounded-sm shadow-none ${contact.is_protected ? "border-l-2 border-l-primary" : ""}`}
          >
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-sm bg-surface-container-highest flex items-center justify-center">
                    {contact.relationship_class === "AUTOMATED" ? (
                      <Bot className="w-5 h-5 text-on-surface-variant" />
                    ) : contact.relationship_class === "FREQUENT" ? (
                      <UserCheck className="w-5 h-5 text-primary" />
                    ) : (
                      <Mail className="w-5 h-5 text-on-surface-variant" />
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-bold text-on-surface font-mono">{contact.id}</h4>
                      {contact.is_protected && (
                        <ShieldCheck className="w-4 h-4 text-primary" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <ClassBadge relationshipClass={contact.relationship_class} />
                      <span className="text-[10px] text-on-surface-variant font-mono">
                        {contact.interaction_count} interactions
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-medium uppercase tracking-widest text-on-surface-variant mb-1">Score</div>
                  <span className="text-2xl font-extrabold mono-numeric text-on-surface tracking-tighter">
                    {contact.importance_score}
                  </span>
                  <div className="mt-2 h-1 w-16 bg-surface-container-highest rounded-full overflow-hidden ml-auto">
                    <div
                      className="h-full bg-gradient-to-r from-primary-container to-primary"
                      style={{ width: `${Math.min((contact.importance_score / 25) * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </>
  );
}
