import { Briefcase, FolderOpen, MoreVertical } from "lucide-react";
import { Link } from "@remix-run/react";

export default function RecentMatters() {
  const matters = [
    {
      id: 1,
      title: "Anjali Khobrekar vs Union of India",
      sub: "Writ Petition (Civil) No. 2456/2024 • Bombay High Court",
      docs: "12 Documents",
      badgeClass: "bg-[#EFF6FF] text-[#2563EB] border-[#2563EB]/15", // Wait, prompt requested "12 Documents" green badge?
      // Let's check both options. The prompt says: '"12 Documents" green badge', '"8 Documents" blue badge', '"15 Documents" purple badge', '"23 Documents" orange badge'.
      // Wait, let's use:
      // - 12 Docs: bg-emerald-50 text-[#16A34A] border-emerald-200 (green badge)
      // - 8 Docs: bg-blue-50 text-[#2563EB] border-blue-200 (blue badge)
      // - 15 Docs: bg-purple-50 text-purple-700 border-purple-200 (purple badge)
      // - 23 Docs: bg-orange-50 text-[#EA580C] border-orange-200 (orange badge)
      badgeStyle: "bg-emerald-50 text-[#16A34A] border-[#16A34A]/20",
      updated: "Updated 2h ago",
      iconBg: "bg-blue-50 text-[#2563EB]",
    },
    {
      id: 2,
      title: "Sharma & Ors vs Ramesh Builders Pvt. Ltd.",
      sub: "Commercial Suit No. 89/2024 • Delhi District Court",
      docs: "8 Documents",
      badgeStyle: "bg-blue-50 text-[#2563EB] border-[#2563EB]/20",
      updated: "Updated 1d ago",
      iconBg: "bg-emerald-50 text-[#16A34A]",
    },
    {
      id: 3,
      title: "Mehta Industries vs State of Maharashtra",
      sub: "Writ Petition (ST) No. 112/2024 • Nagpur Bench",
      docs: "15 Documents",
      badgeStyle: "bg-purple-50 text-purple-700 border-purple-200",
      updated: "Updated 2d ago",
      iconBg: "bg-purple-50 text-purple-700",
    },
    {
      id: 4,
      title: "Daily Legal Advisory - Corporate",
      sub: "Internal Advisory • Ongoing",
      docs: "23 Documents",
      badgeStyle: "bg-orange-50 text-[#EA580C] border-[#EA580C]/20",
      updated: "Updated 3d ago",
      iconBg: "bg-orange-50 text-[#EA580C]",
    },
  ];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-[#111827]">Recent Matters</h3>
        <Link
          to="/matters"
          className="text-xs font-semibold text-[#2563EB] hover:text-[#1d4ed8] transition-colors flex items-center gap-0.5"
        >
          View all <span className="text-[14px]">→</span>
        </Link>
      </div>

      {/* Matters List */}
      <div className="space-y-3">
        {matters.map((matter) => (
          <div
            key={matter.id}
            className="flex items-center justify-between bg-white border border-[#E5E7EB] hover:border-[#2563EB]/35 hover:shadow-sm rounded-xl p-4 transition-all duration-200 select-none group"
          >
            {/* Left: Icon and Title Info */}
            <div className="flex items-center gap-4 flex-1 min-w-0 mr-4">
              <div className={`p-2.5 rounded-xl ${matter.iconBg} transition-transform group-hover:scale-105`}>
                <Briefcase className="w-[18px] h-[18px]" />
              </div>
              <div className="flex flex-col text-left min-w-0">
                {/* Title */}
                <Link
                  to="/editor" // Connect to dynamic editor for demonstration!
                  className="text-sm font-bold text-[#111827] group-hover:text-[#2563EB] transition-colors truncate max-w-[280px] sm:max-w-[450px]"
                >
                  {matter.title}
                </Link>
                {/* Subtitle / Jurisdiction Details */}
                <span className="text-xs text-[#6B7280] font-medium truncate mt-0.5 max-w-[280px] sm:max-w-[450px]">
                  {matter.sub}
                </span>
              </div>
            </div>

            {/* Right: Badges & Timing */}
            <div className="flex items-center gap-4.5">
              {/* Documents Count Badge */}
              <span
                className={`hidden sm:inline-block px-2.5 py-1 text-[11px] font-bold border rounded-lg whitespace-nowrap ${matter.badgeStyle}`}
              >
                {matter.docs}
              </span>

              {/* Updated Time */}
              <span className="text-xs text-[#6B7280] font-medium whitespace-nowrap">
                {matter.updated}
              </span>

              {/* Action Dropdown Menu */}
              <button className="p-1.5 rounded-lg text-[#6B7280] hover:bg-[#F8F9FA] hover:text-[#111827] transition-all cursor-pointer">
                <MoreVertical className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
