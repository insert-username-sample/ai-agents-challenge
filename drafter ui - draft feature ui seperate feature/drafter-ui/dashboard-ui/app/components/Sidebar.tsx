import { useLocation, Link } from "@remix-run/react";
import {
  Home,
  Briefcase,
  FileEdit,
  Building2,
  Sparkles,
  Lock,
  BookOpen,
  LayoutTemplate,
  Search,
  Calendar,
  CreditCard,
  ChevronUp,
} from "lucide-react";

export function ClauselyLogo({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      {/* Blue 4-petal interlocking flower/star logo matching mockups */}
      <svg
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full transform transition-transform duration-700 hover:rotate-180"
      >
        <path
          d="M50 15C50 34.33 34.33 50 15 50C34.33 50 50 65.67 50 85C50 65.67 65.67 50 85 50C65.67 50 50 34.33 50 15Z"
          fill="url(#clausely-logo-gradient)"
        />
        <circle cx="50" cy="50" r="12" fill="#FFFFFF" />
        <circle cx="50" cy="50" r="6" fill="#2563EB" />
        <defs>
          <linearGradient id="clausely-logo-gradient" x1="15" y1="15" x2="85" y2="85" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#3B82F6" />
            <stop offset="50%" stopColor="#2563EB" />
            <stop offset="100%" stopColor="#1D4ED8" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}

export default function Sidebar() {
  const location = useLocation();
  const currentPath = location.pathname;

  const navItems = [
    { name: "Home", href: "/", icon: Home },
    { name: "Matters", href: "/matters", icon: Briefcase },
    { name: "Drafting Studio", href: "/editor", icon: FileEdit },
    { name: "Registry Simulator", href: "/registry", icon: Building2 },
    { name: "Strategist", href: "/strategist", icon: Sparkles },
    { name: "Vault", href: "/vault", icon: Lock },
    { name: "Playbooks", href: "/playbooks", icon: BookOpen },
    { name: "Templates", href: "/templates", icon: LayoutTemplate },
    { name: "Research", href: "/research", icon: Search },
    { name: "Calendar", href: "/calendar", icon: Calendar },
    { name: "Billing", href: "/billing", icon: CreditCard },
  ];

  return (
    <aside className="w-[240px] min-w-[240px] h-screen bg-white border-r border-[#E5E7EB] flex flex-col justify-between font-sans select-none z-20">
      {/* Top Section: Logo & Branding */}
      <div>
        <div className="h-16 flex items-center px-6 border-b border-[#E5E7EB]/50">
          <Link to="/" className="flex items-center gap-3">
            <ClauselyLogo className="w-8 h-8 text-[#2563EB]" />
            <span className="text-xl font-bold text-[#111827] tracking-tight flex items-center">
              clausely<span className="text-[#2563EB]">.ai</span>
            </span>
          </Link>
        </div>

        {/* Navigation Items */}
        <nav className="px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.href === "/"
                ? currentPath === "/"
                : currentPath.startsWith(item.href);

            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                  isActive
                    ? "bg-[#EFF6FF] text-[#2563EB] font-semibold shadow-sm shadow-[#2563EB]/5"
                    : "text-[#6B7280] font-medium hover:bg-[#F8F9FA] hover:text-[#111827]"
                }`}
              >
                <Icon
                  className={`w-[18px] h-[18px] ${
                    isActive ? "text-[#2563EB]" : "text-[#6B7280] group-hover:text-[#111827]"
                  }`}
                />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom Section: Plan Upgrade & User Card */}
      <div className="p-4 border-t border-[#E5E7EB]/60 bg-white">
        {/* Free Plan Card */}
        <div className="bg-[#F8F9FA] border border-[#E5E7EB] rounded-xl p-4.5 mb-4 shadow-sm">
          <div className="text-xs font-semibold text-[#111827] uppercase tracking-wider mb-1">
            Free Plan
          </div>
          <div className="text-[11px] text-[#6B7280] mb-3 leading-relaxed">
            Upgrade for unlimited generations
          </div>
          <button className="w-full bg-[#2563EB] hover:bg-[#1d4ed8] text-white text-xs font-semibold py-2 px-4 rounded-lg shadow-sm shadow-blue-500/10 hover:shadow-blue-500/20 active:scale-[0.98] transition-all">
            Upgrade
          </button>
        </div>

        {/* User Card */}
        <div className="flex items-center justify-between p-1.5 rounded-xl border border-[#E5E7EB]/50 hover:bg-[#F8F9FA] transition-all cursor-pointer group">
          <div className="flex items-center gap-3">
            {/* Avatar Initials MK */}
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#2563EB] to-[#1D4ED8] flex items-center justify-center text-white font-semibold text-sm shadow-sm select-none">
              MK
            </div>
            <div className="flex flex-col text-left">
              <span className="text-xs font-bold text-[#111827] group-hover:text-[#2563EB] transition-colors leading-tight">
                Adv. Manas Khobrekar
              </span>
              <span className="text-[10px] font-medium text-[#6B7280] leading-none mt-0.5 truncate max-w-[125px]">
                manas@clausely.ai
              </span>
            </div>
          </div>
          <ChevronUp className="w-4 h-4 text-[#6B7280] group-hover:text-[#111827] transition-colors mr-1" />
        </div>
      </div>
    </aside>
  );
}
