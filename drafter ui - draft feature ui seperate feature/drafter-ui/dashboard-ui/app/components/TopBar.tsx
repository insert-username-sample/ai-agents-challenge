import { Search, Bell, HelpCircle, Plus, ChevronDown } from "lucide-react";

interface TopBarProps {
  onToggleSidebar?: () => void;
}

export default function TopBar({ onToggleSidebar }: TopBarProps) {
  return (
    <header className="h-16 border-b border-[#E5E7EB] bg-white px-6 flex items-center justify-between select-none z-10">
      {/* Left: Collapsible Button or Search */}
      <div className="flex items-center gap-4 flex-1">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="p-1.5 rounded-lg text-[#6B7280] hover:bg-[#F8F9FA] hover:text-[#111827] transition-all lg:hidden"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        )}

        {/* Search Bar - styled with exact high-fidelity details */}
        <div className="relative max-w-md w-full group">
          <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
            <Search className="w-4 h-4 text-[#6B7280] group-focus-within:text-[#2563EB] transition-colors" />
          </div>
          <input
            type="text"
            placeholder="Search matters, documents, clauses..."
            className="w-full bg-[#F8F9FA] border border-[#E5E7EB] hover:border-[#6B7280]/30 focus:border-[#2563EB] focus:bg-white text-sm text-[#111827] placeholder-[#6B7280] pl-10 pr-12 py-2 rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
          <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none">
            <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-medium text-[#6B7280] bg-white border border-[#E5E7EB] rounded shadow-sm">
              ⌘K
            </kbd>
          </div>
        </div>
      </div>

      {/* Right Side: Notification Icon, Help Center, & New Matter Action Button */}
      <div className="flex items-center gap-3 ml-4">
        {/* Help Question Icon Button */}
        <button className="p-2 rounded-lg text-[#6B7280] hover:bg-[#F8F9FA] hover:text-[#111827] relative transition-all group">
          <HelpCircle className="w-[19px] h-[19px]" />
          <span className="absolute bottom-[-30px] right-0 bg-[#111827] text-white text-[10px] py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap shadow-md">
            Help & Documentation
          </span>
        </button>

        {/* Notification Bell with Badge (3) */}
        <button className="p-2 rounded-lg text-[#6B7280] hover:bg-[#F8F9FA] hover:text-[#111827] relative transition-all group">
          <Bell className="w-[19px] h-[19px]" />
          <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-[#EA580C] text-white text-[9px] font-bold flex items-center justify-center border border-white">
            3
          </span>
          <span className="absolute bottom-[-30px] right-0 bg-[#111827] text-white text-[10px] py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap shadow-md">
            3 Notifications
          </span>
        </button>

        {/* Divider */}
        <div className="w-[1px] h-6 bg-[#E5E7EB] mx-1"></div>

        {/* "+ New Matter" dropdown button in blue */}
        <div className="relative group">
          <button className="bg-[#2563EB] hover:bg-[#1d4ed8] text-white text-xs font-bold px-3.5 py-2 rounded-lg flex items-center gap-1.5 shadow-sm shadow-blue-500/10 active:scale-[0.98] transition-all">
            <Plus className="w-4 h-4" />
            <span>New Matter</span>
            <ChevronDown className="w-3.5 h-3.5 text-blue-200" />
          </button>
        </div>
      </div>
    </header>
  );
}
