"use client";

import Link from "next/link";
import { BrandLogo } from "@/components/brand-logo";
import { usePathname } from "next/navigation";
import {
  Bell,
  CalendarClock,
  CalendarDays,
  CalendarPlus2,
  CircleDollarSign,
  FileText,
  LayoutDashboard,
  ScrollText,
  Ticket,
  UserCircle2,
  Users,
  Vote,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { icon: ScrollText, label: "RekhaCB Copilot", href: "/ai-copilot" },
  { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard" },
  { icon: Users, label: "Employees", href: "/employees" },
  { icon: UserCircle2, label: "My Profile", href: "/me" },
  { icon: FileText, label: "My Documents", href: "/me/documents" },
  { icon: CircleDollarSign, label: "Finance", href: "/finance" },
  { icon: CalendarClock, label: "Attendance", href: "/attendance" },
  { icon: CalendarPlus2, label: "Leaves", href: "/leaves" },
  { icon: Bell, label: "Announcements", href: "/announcements" },
  { icon: ScrollText, label: "HR Policies", href: "/hr-policies" },
  { icon: Vote, label: "Polls", href: "/polls" },
  { icon: CalendarDays, label: "Team Calendar", href: "/team-calendar" },
  { icon: Ticket, label: "Tickets", href: "/tickets" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-72 border-r border-slate-900/80 bg-gradient-to-b from-[#0f1b33] via-[#0c1730] to-[#081121] md:block">
      <div className="border-b border-white/5 px-4 pb-4 pt-6 text-center">
        <div className="text-left px-4">
          <Link
            href="/dashboard"
            aria-label="RekhaCB home"
            className="block rounded focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300"
          >
            <BrandLogo className="w-56" />
          </Link>
          <p className="mt-2 text-xs text-slate-400">
            Your people operations workspace
          </p>
        </div>
      </div>
      <nav className="space-y-1 px-3 py-4">
        {navItems.map((item) => (
          <Link
            key={item.label}
            href={item.href}
            className={cn(
              "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-slate-300 transition hover:bg-white/5 hover:text-white",
              item.href !== "#" &&
                pathname.startsWith(item.href) &&
                "bg-gradient-to-r from-indigo-500/20 to-transparent text-white ring-1 ring-indigo-400/20",
            )}
          >
            <span
              className={cn(
                "inline-flex h-8 w-8 items-center justify-center rounded-lg bg-transparent transition group-hover:bg-white/5",
                item.href !== "#" &&
                  pathname.startsWith(item.href) &&
                  "bg-indigo-400/10",
              )}
            >
              <item.icon className="h-4 w-4" />
            </span>
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
