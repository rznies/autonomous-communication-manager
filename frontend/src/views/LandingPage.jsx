import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Lock, Clock, Filter, Mail, Layers, Command, BellOff, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

export default function LandingPage() {
  // Ensure the body background doesn't bleed through
  useEffect(() => {
    document.body.style.backgroundColor = '#FFFFFF';
    return () => {
      document.body.style.backgroundColor = ''; // Reset on unmount
    };
  }, []);

  return (
    <div className="min-h-screen bg-white text-[#001229] font-sans selection:bg-[#0145F2] selection:text-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-100/50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-semibold text-lg tracking-tight">
            <div className="w-5 h-5 rounded-full bg-[#0145F2] flex items-center justify-center shadow-inner">
              <div className="w-2 h-2 rounded-full bg-white"></div>
            </div>
            Layer
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-500">
            <a href="#problem" className="hover:text-[#001229] transition-colors">The Problem</a>
            <a href="#how-it-works" className="hover:text-[#001229] transition-colors">How it Works</a>
            <a href="#safety" className="hover:text-[#001229] transition-colors">Safety</a>
            <Link to="/app/queue" className="hover:text-[#001229] transition-colors">Sign In</Link>
          </div>
          <Link 
            to="/app/queue" 
            className="bg-[#0145F2] text-white px-5 py-2 rounded-xl text-sm font-medium hover:bg-blue-700 transition-all shadow-sm hover:shadow-md hover:-translate-y-0.5"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-40 pb-20 px-6 relative overflow-hidden">
        {/* Subtle background glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-blue-50 rounded-full blur-[100px] -z-10 opacity-50 pointer-events-none"></div>
        
        <div className="max-w-4xl mx-auto text-center">
          <motion.h1 
            initial="hidden" animate="visible" variants={fadeIn}
            className="text-5xl md:text-7xl font-bold tracking-tight leading-[1.05] mb-6"
          >
            Your inbox should make <br className="hidden md:block"/> decisions before you do.
          </motion.h1>
          
          <motion.p 
            initial="hidden" animate="visible" variants={fadeIn}
            className="text-lg md:text-xl text-gray-500 max-w-2xl mx-auto leading-relaxed mb-10"
          >
            Layer watches your Gmail and Slack, sorts what matters, filters what does not, and brings you only the messages that actually need your judgment.
          </motion.p>
          
          <motion.div 
            initial="hidden" animate="visible" variants={fadeIn}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10"
          >
            <Link to="/app/queue" className="w-full sm:w-auto bg-[#0145F2] text-white px-8 py-3.5 rounded-xl text-base font-semibold hover:bg-blue-700 transition-all shadow-[0_4px_14px_0_rgba(1,69,242,0.25)] hover:shadow-[0_6px_20px_rgba(1,69,242,0.3)] hover:-translate-y-0.5 flex items-center justify-center gap-2">
              See how it works <ArrowRight size={18} />
            </Link>
            <button className="w-full sm:w-auto bg-gray-50 text-[#001229] border border-gray-200 px-8 py-3.5 rounded-xl text-base font-medium hover:bg-gray-100 transition-all">
              Join the waitlist
            </button>
          </motion.div>
          
          <motion.div 
            initial="hidden" animate="visible" variants={fadeIn}
            className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs font-medium text-gray-400 uppercase tracking-wide"
          >
            <span className="flex items-center gap-1.5"><Lock size={14} className="text-gray-300"/> Read-only by default</span>
            <span className="text-gray-200">•</span>
            <span className="flex items-center gap-1.5"><BellOff size={14} className="text-gray-300"/> No auto-sending</span>
            <span className="text-gray-200">•</span>
            <span className="flex items-center gap-1.5"><ShieldCheck size={14} className="text-gray-300"/> Human approval required</span>
          </motion.div>
        </div>

        {/* Hero Product Mockup */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
          className="max-w-5xl mx-auto mt-20 relative z-10"
        >
          <div className="bg-white rounded-2xl shadow-[0_20px_50px_-12px_rgba(0,0,0,0.1)] border border-gray-100 overflow-hidden flex flex-col md:flex-row h-[500px]">
            {/* Sidebar Fake */}
            <div className="w-64 bg-gray-50 border-r border-gray-100 p-4 hidden md:flex flex-col gap-6">
              <div className="flex items-center gap-2 px-2 text-[#001229] font-medium"><Command size={18}/> Queue</div>
              <div className="flex flex-col gap-1">
                <div className="px-3 py-2 rounded-lg bg-white shadow-sm border border-gray-100 text-sm font-medium flex justify-between items-center text-[#0145F2]">
                  <span>Requires Review</span>
                  <span className="bg-[#0145F2] text-white text-[10px] px-2 py-0.5 rounded-full">3</span>
                </div>
                <div className="px-3 py-2 rounded-lg text-sm font-medium text-gray-500 hover:bg-gray-100 flex justify-between items-center">
                  <span>Filtered Noise</span>
                  <span className="text-gray-400 text-xs">42</span>
                </div>
              </div>
            </div>
            {/* Content Fake */}
            <div className="flex-1 p-0 flex flex-col bg-white">
              <div className="h-14 border-b border-gray-100 flex items-center px-6 text-sm font-medium text-gray-400">
                Inbox Triage • 3 items need your attention
              </div>
              <div className="flex-1 p-6 flex flex-col gap-4 overflow-hidden relative">
                
                {/* Email Item 1 */}
                <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm flex gap-4 items-start relative group hover:border-[#0145F2]/30 transition-colors">
                  <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-[#0145F2] font-semibold flex-shrink-0">S</div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-1">
                      <div>
                        <h4 className="font-semibold text-sm">Sarah Jenkins <span className="text-gray-400 font-normal">sarah@investorfirm.com</span></h4>
                        <p className="text-sm font-medium mt-0.5">Term sheet follow up</p>
                      </div>
                      <span className="text-xs text-gray-400">10:42 AM</span>
                    </div>
                    <p className="text-sm text-gray-500 line-clamp-1">Hi there, attaching the updated terms based on our call yesterday. Let me know if...</p>
                    <div className="mt-3 flex gap-2">
                      <div className="bg-[#0145F2]/10 text-[#0145F2] text-xs px-2.5 py-1 rounded-md font-medium flex items-center gap-1">
                        <Layers size={12}/> High Priority Contact
                      </div>
                      <div className="bg-green-50 text-green-600 text-xs px-2.5 py-1 rounded-md font-medium flex items-center gap-1">
                        <CheckCircle2 size={12}/> Draft Prepared
                      </div>
                    </div>
                  </div>
                </div>

                {/* Email Item 2 */}
                <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm flex gap-4 items-start relative opacity-60">
                   <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 font-semibold flex-shrink-0">G</div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-1">
                      <div>
                        <h4 className="font-semibold text-sm">GitHub <span className="text-gray-400 font-normal">noreply@github.com</span></h4>
                        <p className="text-sm font-medium mt-0.5">[rznies/repo] Run failed: Build frontend</p>
                      </div>
                      <span className="text-xs text-gray-400">09:15 AM</span>
                    </div>
                    <p className="text-sm text-gray-500 line-clamp-1">The workflow Build frontend failed. Check logs for more details...</p>
                    <div className="mt-3 flex gap-2">
                      <div className="bg-gray-100 text-gray-500 text-xs px-2.5 py-1 rounded-md font-medium flex items-center gap-1">
                        <Filter size={12}/> Auto-Archived
                      </div>
                    </div>
                  </div>
                </div>

                {/* Gradient fade at bottom */}
                <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-white to-transparent"></div>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* The Problem & Promise */}
      <section id="problem" className="py-24 px-6 bg-gray-50/50 border-y border-gray-100">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-8">
            Most people do not have a message problem. <br/> <span className="text-gray-400">They have a decision problem.</span>
          </h2>
          <div className="text-lg text-gray-500 leading-relaxed space-y-6">
            <p>
              Email and Slack are not just full. They are full of tiny decisions.
              <br/>Reply now or later. Ignore or follow up. Archive or keep.
            </p>
            <p>
              That constant sorting steals hours from your week and keeps you stuck in reaction mode. Today's AI tools help you read faster, but they still leave you to decide everything yourself.
            </p>
          </div>
        </div>
      </section>

      {/* Core Benefits (Bento Box) */}
      <section id="how-it-works" className="py-32 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">The layer between you and the noise.</h2>
            <p className="text-gray-500 max-w-2xl mx-auto text-lg">Instead of starting your day buried in communication, you start with a shorter, cleaner list of what actually matters.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 bg-gray-50 rounded-2xl p-8 border border-gray-100 flex flex-col justify-between group hover:shadow-lg transition-all duration-300">
              <div className="mb-12">
                <Clock className="w-8 h-8 text-[#0145F2] mb-4"/>
                <h3 className="text-xl font-bold mb-2">Less inbox time</h3>
                <p className="text-gray-500">Stop spending your best hours sorting messages that never needed your attention in the first place.</p>
              </div>
              {/* Mini visual */}
              <div className="h-32 bg-white rounded-xl border border-gray-100 p-4 shadow-sm flex items-center justify-center relative overflow-hidden group-hover:-translate-y-1 transition-transform">
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
                <div className="relative z-10 flex items-center gap-3 bg-white px-4 py-2 rounded-lg border border-gray-100 shadow-sm text-sm font-medium text-gray-500">
                  <span className="line-through">Newsletter</span> • <span className="line-through">Updates</span> • <span className="text-[#0145F2]">Investor Intro</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-2xl p-8 border border-gray-100 flex flex-col justify-between group hover:shadow-lg transition-all duration-300">
              <div className="mb-12">
                <Layers className="w-8 h-8 text-[#0145F2] mb-4"/>
                <h3 className="text-xl font-bold mb-2">Fewer missed messages</h3>
                <p className="text-gray-500">Investors, customers, and critical contacts rise to the top automatically.</p>
              </div>
            </div>

            <div className="bg-gray-50 rounded-2xl p-8 border border-gray-100 flex flex-col justify-between group hover:shadow-lg transition-all duration-300">
              <div className="mb-12">
                <Filter className="w-8 h-8 text-[#0145F2] mb-4"/>
                <h3 className="text-xl font-bold mb-2">One decision layer</h3>
                <p className="text-gray-500">Email and Slack stop competing. You get one clear system for both.</p>
              </div>
            </div>

            <div className="md:col-span-2 bg-gray-50 rounded-2xl p-8 border border-gray-100 flex flex-col justify-between group hover:shadow-lg transition-all duration-300">
              <div className="mb-12">
                <Lock className="w-8 h-8 text-[#0145F2] mb-4"/>
                <h3 className="text-xl font-bold mb-2">Control without chaos</h3>
                <p className="text-gray-500">See every action, undo mistakes, and approve anything high-risk before it happens.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Philosophy / Safety */}
      <section id="safety" className="py-24 px-6 bg-[#001229] text-white overflow-hidden relative">
        <div className="absolute top-0 right-0 w-1/2 h-full bg-[#0145F2] blur-[150px] opacity-20 pointer-events-none translate-x-1/2"></div>
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <ShieldCheck className="w-12 h-12 text-[#0145F2] mx-auto mb-6" />
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-8">Built to earn trust slowly.</h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-12 font-light">
            This system starts in read-only mode. It does not send messages on its own. It shows you what it did and why. And when you disagree, you can correct it instantly.
          </p>
          <div className="bg-white/5 border border-white/10 rounded-2xl p-8 max-w-lg mx-auto backdrop-blur-sm">
            <h3 className="text-lg font-medium mb-4 text-white">The Golden Rule:</h3>
            <p className="text-2xl font-semibold text-[#0145F2]">Automation where it is safe,<br/>approval where it matters.</p>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-32 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">Your inbox should not run your day.</h2>
          <p className="text-xl text-gray-500 mb-10">Let the machine sort the noise. Keep the decisions that deserve a human.</p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/app/queue" className="w-full sm:w-auto bg-[#0145F2] text-white px-8 py-4 rounded-xl text-lg font-semibold hover:bg-blue-700 transition-all shadow-lg hover:-translate-y-1">
              Join the waitlist
            </Link>
            <Link to="/app/queue" className="w-full sm:w-auto bg-white text-[#001229] border border-gray-200 px-8 py-4 rounded-xl text-lg font-medium hover:bg-gray-50 transition-all">
              See the product demo
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 px-6 border-t border-gray-100 bg-gray-50 text-center">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 font-semibold text-[#001229]">
            <div className="w-4 h-4 rounded-full bg-[#0145F2]"></div> Layer
          </div>
          <p className="text-sm text-gray-400">The AI decision layer for Gmail and Slack.</p>
          <div className="text-sm text-gray-400">© 2026 Layer Inc.</div>
        </div>
      </footer>
    </div>
  );
}
