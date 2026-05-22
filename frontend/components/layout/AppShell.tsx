"use client";

import { useAuth } from "@/contexts/AuthContext";
import clsx from "clsx";
import Link from "next/link";
import { usePathname } from "next/navigation";

const nav = [
  { href: "/chat", label: "Chat", icon: "💬" },
  { href: "/dashboard", label: "Metrics", icon: "📊" },
  { href: "/profile", label: "Profile", icon: "👤" },
  { href: "/settings", label: "Settings", icon: "⚙️" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen">
      <aside className="hidden md:flex w-64 flex-col border-r border-line bg-surface/50 backdrop-blur-xl p-4 shrink-0">
        <Link href="/" className="flex items-center gap-2 px-2 py-3 mb-6">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-accent2 text-sm font-bold">
            O
          </span>
          <div>
            <p className="font-semibold text-sm">Ollive</p>
            <p className="text-xs text-muted">Inference OS</p>
          </div>
        </Link>

        <nav className="flex-1 space-y-1">
          {nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition",
                pathname === item.href
                  ? "bg-accent/20 text-white border border-accent/30"
                  : "text-muted hover:bg-white/5 hover:text-foreground"
              )}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="mt-auto pt-4 border-t border-line">
          <div className="flex items-center gap-3 px-2 py-2 mb-2">
            <div className="h-9 w-9 rounded-full bg-gradient-to-br from-accent to-accent2 flex items-center justify-center text-xs font-bold">
              {(user?.display_name || user?.username || "?")[0].toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium truncate">{user?.display_name}</p>
              <p className="text-xs text-muted truncate">@{user?.username}</p>
            </div>
          </div>
          <button onClick={logout} className="btn-ghost w-full text-xs">
            Sign out
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="md:hidden flex items-center justify-between border-b border-line px-4 py-3 bg-surface/80 backdrop-blur">
          <Link href="/chat" className="font-semibold text-sm">
            Ollive
          </Link>
          <div className="flex gap-2 text-xs">
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  "px-2 py-1 rounded-lg",
                  pathname === item.href ? "bg-accent/20" : "text-muted"
                )}
              >
                {item.icon}
              </Link>
            ))}
          </div>
        </header>
        <main className="flex-1 min-h-0">{children}</main>
      </div>
    </div>
  );
}
