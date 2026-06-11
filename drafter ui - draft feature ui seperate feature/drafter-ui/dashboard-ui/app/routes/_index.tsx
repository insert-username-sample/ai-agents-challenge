import { useState } from "react";
import Sidebar, { ClauselyLogo } from "~/components/Sidebar";
import TopBar from "~/components/TopBar";
import QuickActions from "~/components/QuickActions";
import RecentMatters from "~/components/RecentMatters";
import ClauselyAIPanel from "~/components/ClauselyAIPanel";
import { ChevronDown, Send } from "lucide-react";
import { Link } from "@remix-run/react";

export default function DashboardIndex() {
  const [draftText, setDraftText] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-[#F8F9FA] text-[#111827] overflow-hidden font-sans">
      {/* Sidebar: Left Navigation Panel (240px wide) */}
      <div
        className={`fixed inset-y-0 left-0 transform ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } lg:relative lg:translate-x-0 transition-transform duration-300 z-30`}
      >
        <Sidebar />
      </div>

      {/* Sidebar Overlay (Mobile) */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 bg-[#111827]/40 backdrop-blur-xs z-25 lg:hidden"
        ></div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {/* Top Header Bar */}
        <TopBar onToggleSidebar={() => setSidebarOpen(true)} />

        {/* Scrollable Content Container */}
        <main className="flex-1 overflow-y-auto px-6 py-8 space-y-8 custom-scrollbar">
          {/* Greeting Section */}
          <div className="text-left space-y-1 select-none">
            <h1 className="text-2xl font-extrabold text-[#111827] tracking-tight flex items-center gap-1.5">
              Good morning, Manas <span className="animate-bounce">👋</span>
            </h1>
            <p className="text-sm font-semibold text-[#6B7280]">
              What are you drafting today?
            </p>
          </div>

          {/* Draft Input Card - Central Scaffolder */}
          <div className="bg-white border border-[#E5E7EB] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow relative">
            <div className="flex items-start gap-4">
              {/* Spinning Petal Logo on the Left */}
              <div className="w-12 h-12 rounded-xl bg-blue-50/60 flex items-center justify-center text-[#2563EB] shadow-sm select-none">
                <ClauselyLogo className="w-9 h-9 text-[#2563EB]" />
              </div>

              {/* Input Area */}
              <div className="flex-1">
                <textarea
                  value={draftText}
                  onChange={(e) => setDraftText(e.target.value)}
                  placeholder="Describe what you need to draft..."
                  rows={2}
                  className="w-full text-base font-medium text-[#111827] placeholder-[#6B7280] bg-transparent resize-none border-none outline-none focus:ring-0 leading-relaxed"
                />
                <p className="text-xs text-[#6B7280] font-medium text-left select-none mt-1">
                  e.g., Draft a rent agreement for a 11-month lease in Mumbai
                </p>
              </div>
            </div>

            {/* Bottom Controls Row */}
            <div className="flex items-center justify-between border-t border-[#E5E7EB] mt-5 pt-4.5 select-none">
              <div className="flex flex-wrap items-center gap-3.5">
                {/* Jurisdiction dropdown */}
                <div className="relative">
                  <select className="text-xs font-bold text-[#111827] bg-[#F8F9FA] hover:bg-[#E5E7EB]/50 border border-[#E5E7EB] py-1.5 pl-3.5 pr-8 rounded-lg appearance-none outline-none cursor-pointer transition-colors">
                    <option>Jurisdiction: Maharashtra</option>
                    <option>Jurisdiction: Delhi</option>
                    <option>Jurisdiction: Karnataka</option>
                  </select>
                  <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#6B7280] pointer-events-none" />
                </div>

                {/* Language dropdown */}
                <div className="relative">
                  <select className="text-xs font-bold text-[#111827] bg-[#F8F9FA] hover:bg-[#E5E7EB]/50 border border-[#E5E7EB] py-1.5 pl-3.5 pr-8 rounded-lg appearance-none outline-none cursor-pointer transition-colors">
                    <option>Language: English</option>
                    <option>Language: Marathi</option>
                    <option>Language: Hindi</option>
                  </select>
                  <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#6B7280] pointer-events-none" />
                </div>
              </div>

              {/* Arrow Send Button & ⌘Enter Label */}
              <div className="flex items-center gap-3">
                <kbd className="hidden sm:inline-block px-2 py-0.5 text-[10px] font-bold text-[#6B7280] bg-[#F8F9FA] border border-[#E5E7EB] rounded-md shadow-sm">
                  ⌘ Enter
                </kbd>
                <Link
                  to="/editor" // Redirects to interactive document editor for experience!
                  className="bg-[#2563EB] hover:bg-[#1d4ed8] text-white p-2.5 rounded-xl shadow-sm shadow-blue-500/10 hover:shadow-blue-500/20 active:scale-95 transition-all"
                >
                  <Send className="w-4.5 h-4.5" />
                </Link>
              </div>
            </div>
          </div>

          {/* Quick Actions Grid */}
          <QuickActions />

          {/* Recent Matters List */}
          <RecentMatters />
        </main>
      </div>

      {/* Clausely AI Right Panel (340px wide) */}
      <div className="hidden xl:block">
        <ClauselyAIPanel />
      </div>
    </div>
  );
}
