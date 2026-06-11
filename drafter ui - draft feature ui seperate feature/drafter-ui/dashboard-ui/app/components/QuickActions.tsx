import { FileText, Shield, Building, Sparkles } from "lucide-react";
import { Link } from "@remix-run/react";

export default function QuickActions() {
  const actions = [
    {
      title: "Draft Document",
      desc: "From intent",
      icon: FileText,
      color: "text-[#2563EB]",
      bg: "bg-[#EFF6FF]",
      border: "border-[#EFF6FF]/60",
      href: "/editor",
    },
    {
      title: "Review Document",
      desc: "Check risks & clauses",
      icon: Shield,
      color: "text-[#2563EB]",
      bg: "bg-blue-50/50",
      border: "border-blue-50",
      href: "/review",
    },
    {
      title: "Registry Check",
      desc: "Pre-file validation",
      icon: Building,
      color: "text-[#2563EB]",
      bg: "bg-blue-50/50",
      border: "border-blue-50",
      href: "/registry",
    },
    {
      title: "Ask Legal AI",
      desc: "Get instant answers",
      icon: Sparkles,
      color: "text-[#2563EB]",
      bg: "bg-blue-50/50",
      border: "border-blue-50",
      href: "/chat",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {actions.map((action) => {
        const Icon = action.icon;
        return (
          <Link
            key={action.title}
            to={action.href}
            className="flex items-center gap-4 bg-white border border-[#E5E7EB] hover:border-[#2563EB]/40 hover:shadow-md rounded-xl p-4.5 cursor-pointer select-none transition-all active:scale-[0.99] group"
          >
            <div className={`p-3 rounded-xl ${action.bg} ${action.color} group-hover:scale-105 transition-transform`}>
              <Icon className="w-5 h-5" />
            </div>
            <div className="flex flex-col text-left">
              <span className="text-sm font-bold text-[#111827] group-hover:text-[#2563EB] transition-colors leading-tight">
                {action.title}
              </span>
              <span className="text-xs text-[#6B7280] font-medium leading-none mt-1">
                {action.desc}
              </span>
            </div>
          </Link>
        );
      })}
    </div>
  );
}
