import { useState } from "react";
import {
  FileEdit,
  Shield,
  Sparkles,
  Lock,
  BookOpen,
  X,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  ExternalLink,
  Check,
  AlertTriangle,
} from "lucide-react";

export default function ClauselyAIPanel() {
  const [activeTab, setActiveTab] = useState<"draft" | "review" | "strategy" | "vault" | "playbook">("draft");
  const [inputText, setInputText] = useState("");
  const [citationsExpanded, setCitationsExpanded] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [draftGenerated, setDraftGenerated] = useState(true); // Default loaded for fidelity

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (e.target.value.length <= 500) {
      setInputText(e.target.value);
    }
  };

  const tabs = [
    { id: "draft", label: "Draft", icon: FileEdit },
    { id: "review", label: "Review", icon: Shield },
    { id: "strategy", label: "Strategy", icon: Sparkles },
    { id: "vault", label: "Vault", icon: Lock },
    { id: "playbook", label: "Playbook", icon: BookOpen },
  ] as const;

  const laws = [
    { name: "Bharatiya Nyaya Sanhita 2024", type: "Primary", badgeStyle: "bg-emerald-50 text-[#16A34A] border-emerald-100" },
    { name: "Maharashtra Stamp Act 1958", type: "Primary", badgeStyle: "bg-emerald-50 text-[#16A34A] border-emerald-100" },
    { name: "Code of Civil Procedure 1908", type: "Secondary", badgeStyle: "bg-gray-100 text-[#6B7280] border-gray-200" },
    { name: "Registration Act 1908", type: "Secondary", badgeStyle: "bg-gray-100 text-[#6B7280] border-gray-200" },
  ];

  return (
    <aside className="w-[340px] min-w-[340px] h-screen bg-white border-l border-[#E5E7EB] flex flex-col justify-between select-none relative font-sans">
      {/* Scrollable Upper Area */}
      <div className="flex-1 overflow-y-auto pb-[50px] custom-scrollbar">
        {/* Header */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-[#E5E7EB]">
          <h2 className="text-base font-bold text-[#111827]">Clausely AI</h2>
          <button className="p-1 rounded-lg text-[#6B7280] hover:bg-[#F8F9FA] hover:text-[#111827] transition-all">
            <X className="w-4.5 h-4.5" />
          </button>
        </div>

        {/* Dynamic Nav Tabs */}
        <div className="flex border-b border-[#E5E7EB]">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 py-2 flex flex-col items-center justify-center border-b-2 gap-1 text-[10px] font-bold tracking-tight transition-all duration-200 ${
                  isActive
                    ? "border-[#2563EB] text-[#2563EB]"
                    : "border-transparent text-[#6B7280] hover:text-[#111827] hover:bg-[#F8F9FA]"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Specific Content */}
        {activeTab === "draft" && (
          <div className="p-5 space-y-5">
            {/* Area: Draft Input Box */}
            <div className="space-y-2">
              <label className="text-[11px] font-bold text-[#111827] uppercase tracking-wider block">
                What do you need to draft?
              </label>
              <div className="relative border border-[#E5E7EB] rounded-xl bg-[#F8F9FA] focus-within:bg-white focus-within:border-[#2563EB] focus-within:ring-2 focus-within:ring-blue-100 transition-all p-3 shadow-inner">
                <textarea
                  value={inputText}
                  onChange={handleTextChange}
                  placeholder="e.g., Draft a limitation clause for an NDA under Maharashtra jurisdiction"
                  className="w-full text-xs text-[#111827] bg-transparent resize-none h-20 placeholder-[#6B7280] outline-none focus:ring-0 leading-relaxed"
                />
                <div className="flex items-center justify-between border-t border-[#E5E7EB]/40 pt-2 mt-1 select-none">
                  <span className="text-[10px] text-[#6B7280] font-medium">
                    Ctrl + Enter to generate
                  </span>
                  <span className="text-[10px] text-[#6B7280] font-semibold">
                    {inputText.length}/500
                  </span>
                </div>
              </div>
            </div>

            {/* Inputs & Dropdowns */}
            <div className="grid grid-cols-2 gap-3.5">
              <div>
                <label className="text-[10px] font-bold text-[#6B7280] mb-1.5 block">Jurisdiction</label>
                <div className="relative">
                  <select className="w-full text-xs font-semibold bg-white border border-[#E5E7EB] py-2 pl-3 pr-8 rounded-lg appearance-none outline-none focus:border-[#2563EB] cursor-pointer">
                    <option>Maharashtra</option>
                    <option>Delhi</option>
                    <option>Karnataka</option>
                  </select>
                  <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#6B7280] pointer-events-none" />
                </div>
              </div>

              <div>
                <label className="text-[10px] font-bold text-[#6B7280] mb-1.5 block">Language</label>
                <div className="relative">
                  <select className="w-full text-xs font-semibold bg-white border border-[#E5E7EB] py-2 pl-3 pr-8 rounded-lg appearance-none outline-none focus:border-[#2563EB] cursor-pointer">
                    <option>English</option>
                    <option>Marathi</option>
                    <option>Hindi</option>
                  </select>
                  <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#6B7280] pointer-events-none" />
                </div>
              </div>
            </div>

            {/* Generate Button */}
            <button
              onClick={() => {
                setIsGenerating(true);
                setTimeout(() => {
                  setIsGenerating(false);
                  setDraftGenerated(true);
                }, 1000);
              }}
              className="w-full bg-[#2563EB] hover:bg-[#1d4ed8] text-white text-xs font-bold py-2.5 px-4 rounded-xl flex items-center justify-center gap-1.5 shadow-sm shadow-blue-500/10 active:scale-[0.98] transition-all cursor-pointer"
            >
              <Sparkles className="w-4.5 h-4.5 animate-pulse" />
              <span>{isGenerating ? "Generating..." : "Generate Clause"}</span>
            </button>

            {/* Recent Draft Section */}
            {draftGenerated && (
              <div className="space-y-3 pt-1">
                <div className="text-[11px] font-bold text-[#111827] uppercase tracking-wider block">
                  Recent Draft
                </div>

                {/* Clause Card */}
                <div className="border border-[#E5E7EB] rounded-xl p-4 space-y-3 bg-white shadow-sm hover:shadow-md transition-shadow">
                  {/* Card Title & Risk Badge */}
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#111827]">Limitation Clause</span>
                    <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-orange-50 text-[10px] font-bold text-[#EA580C] border border-orange-100">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#EA580C]"></span>
                      Risk 4/10
                    </span>
                  </div>

                  {/* Body Text */}
                  <p className="text-xs text-[#6B7280] leading-relaxed font-medium text-left">
                    Neither party shall be liable for any indirect, incidental, consequential or special damages arising out of or relating to this Agreement...
                  </p>

                  {/* Expandable Citations */}
                  <div className="border-t border-[#E5E7EB]/50 pt-2.5">
                    <button
                      onClick={() => setCitationsExpanded(!citationsExpanded)}
                      className="text-xs font-semibold text-[#2563EB] hover:text-[#1d4ed8] flex items-center gap-1 focus:outline-none transition-colors"
                    >
                      {citationsExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      <span>2 verified citations</span>
                    </button>

                    {/* Citations List */}
                    {citationsExpanded && (
                      <div className="mt-2.5 pl-4 border-l-2 border-[#2563EB]/20 space-y-2 text-left">
                        <div className="text-[11px] text-[#6B7280] leading-normal font-medium">
                          <strong className="text-[#111827]">Section 73, Indian Contract Act 1872</strong> - Governs compensation for loss or damage caused by breach of contract.
                        </div>
                        <div className="text-[11px] text-[#6B7280] leading-normal font-medium">
                          <strong className="text-[#111827]">Bombay High Court Rules</strong> - Standard limitations on indirect damage recoveries in commercial litigation.
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Control Buttons */}
                  <div className="grid grid-cols-3 gap-2 border-t border-[#E5E7EB]/50 pt-3">
                    <button className="flex items-center justify-center gap-1 border border-[#16A34A]/30 bg-emerald-50/20 text-[#16A34A] hover:bg-emerald-50 text-[11px] font-bold py-1.5 rounded-lg active:scale-95 transition-all">
                      <Check className="w-3.5 h-3.5" />
                      <span>Accept</span>
                    </button>
                    <button className="flex items-center justify-center gap-1 border border-[#E5E7EB] text-[#6B7280] hover:bg-[#F8F9FA] hover:text-[#111827] text-[11px] font-bold py-1.5 rounded-lg active:scale-95 transition-all">
                      <RefreshCw className="w-3 h-3" />
                      <span>Regenerate</span>
                    </button>
                    <button className="flex items-center justify-center border border-red-200 text-red-500 hover:bg-red-50 py-1.5 rounded-lg active:scale-95 transition-all">
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Applicable Law Section */}
            <div className="space-y-3.5 pt-1">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-[#111827] uppercase tracking-wider block">
                  Applicable Law
                </span>
                <button className="flex items-center gap-0.5 text-[10px] font-bold text-[#6B7280] hover:text-[#111827] border border-[#E5E7EB] px-2 py-0.5 rounded-md bg-white">
                  <span>MH-DISTRICT</span>
                  <ChevronDown className="w-3 h-3 text-[#6B7280]" />
                </button>
              </div>

              {/* Laws List */}
              <div className="space-y-2">
                {laws.map((law) => (
                  <div
                    key={law.name}
                    className="flex items-center justify-between p-2.5 rounded-xl border border-[#E5E7EB]/60 bg-[#F8F9FA]/40 hover:bg-[#F8F9FA] transition-all cursor-pointer group"
                  >
                    <span className="text-xs font-bold text-[#111827] group-hover:text-[#2563EB] transition-colors truncate max-w-[170px] text-left">
                      {law.name}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className={`text-[9px] font-extrabold px-2 py-0.5 rounded border tracking-wider uppercase ${law.badgeStyle}`}>
                        {law.type}
                      </span>
                      <ExternalLink className="w-3.5 h-3.5 text-[#6B7280] group-hover:text-[#111827]" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Fixed Footer Status Bar */}
      <div className="absolute bottom-0 left-0 right-0 h-[45px] bg-[#F8F9FA] border-t border-[#E5E7EB] px-4 flex items-center justify-between select-none">
        <span className="text-[10px] font-extrabold text-[#111827] bg-[#E5E7EB]/60 hover:bg-[#E5E7EB] transition-colors px-2 py-0.5 rounded border border-[#E5E7EB] select-none tracking-wider">
          BNS-2024-v1
        </span>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-semibold text-[#6B7280]">
            Ctrl+Shift+C for commands
          </span>
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#16A34A] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#16A34A]"></span>
          </span>
        </div>
      </div>
    </aside>
  );
}
