"use client";

import * as Dialog from "@radix-ui/react-dialog";
import { useQuery } from "@tanstack/react-query";
import { Moon, Search, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Copilot } from "@/components/copilot";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/executive", label: "Executive" },
  { href: "/network", label: "Network" },
  { href: "/scenarios", label: "Scenarios" },
  { href: "/approvals", label: "Approvals" },
  { href: "/data", label: "Data" },
];

export function Shell({ children }: { children: ReactNode }) {
  const { resolvedTheme, setTheme } = useTheme();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const templates = useQuery({ queryKey: ["templates"], queryFn: api.templates });

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const items = useMemo(() => {
    const pages = NAV.map((item) => ({ label: item.label, href: item.href }));
    const scenarios = (templates.data?.templates ?? [])
      .filter((item) => item.status === "live")
      .map((item) => ({ label: item.name, href: `/scenarios/${item.id}` }));
    return [...pages, ...scenarios].filter((item) => item.label.toLowerCase().includes(query.toLowerCase()));
  }, [query, templates.data]);

  return (
    <div className="min-h-screen md:grid md:grid-cols-[240px_1fr]">
      <aside className="border-b border-border bg-card md:min-h-screen md:border-b-0 md:border-r">
        <div className="flex h-14 items-center px-5">
          <Link href="/executive" className="text-sm font-semibold tracking-tight">
            PharmaTwin
          </Link>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-3 pb-3 md:block md:space-y-1 md:px-3">
          {NAV.map((item) => (
            <Link key={item.href} href={item.href} className="block rounded-md px-3 py-2 text-sm hover:bg-muted">
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <div className="min-w-0">
        <header className="flex h-14 items-center justify-between border-b border-border px-4 md:px-6">
          <button
            className="flex items-center gap-2 rounded-md border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground"
            onClick={() => setOpen(true)}
          >
            <Search className="size-3.5" />
            Search
            <span className="font-mono">Ctrl K</span>
          </button>
          <div className="flex items-center gap-3">
            <span className="rounded-md border border-border px-2 py-1 text-xs text-muted-foreground" data-testid="synthetic-badge">
              Synthetic demo data
            </span>
            <button
              aria-label="Toggle colour theme"
              className="rounded-md border border-border p-2"
              onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
            >
              {resolvedTheme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
            </button>
          </div>
        </header>
        <main className="mx-auto max-w-[1600px] p-4 md:p-6">{children}</main>
        <Copilot />
      </div>
      <Dialog.Root open={open} onOpenChange={setOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-foreground/20" />
          <Dialog.Content className="fixed left-1/2 top-24 w-[min(520px,92vw)] -translate-x-1/2 rounded-lg border border-border bg-popover p-3 shadow-[var(--overlay)]">
            <Dialog.Title className="sr-only">Command palette</Dialog.Title>
            <input
              autoFocus
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Jump to a screen or scenario"
              className="w-full rounded-md border border-input bg-card px-3 py-2 text-sm"
            />
            <ul className="mt-2 max-h-80 overflow-auto">
              {items.map((item) => (
                <li key={item.href}>
                  <button
                    className={cn("w-full rounded-md px-3 py-2 text-left text-sm hover:bg-muted")}
                    onClick={() => {
                      setOpen(false);
                      router.push(item.href);
                    }}
                  >
                    {item.label}
                  </button>
                </li>
              ))}
            </ul>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
}
