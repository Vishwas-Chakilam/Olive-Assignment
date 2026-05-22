"use client";

import type { ConversationSummary } from "@/lib/api";
import clsx from "clsx";

type Props = {
  conversations: ConversationSummary[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
};

export function ChatSidebar({ conversations, activeId, onSelect, onNew, onDelete }: Props) {
  return (
    <aside className="w-72 shrink-0 border-r border-line bg-surface/60 flex flex-col h-full hidden lg:flex">
      <div className="p-4 border-b border-line">
        <button onClick={onNew} className="btn-primary w-full text-sm">
          + New chat
        </button>
      </div>
      <nav className="flex-1 overflow-y-auto p-2 space-y-1">
        {conversations.length === 0 && (
          <p className="text-sm text-muted px-3 py-6 text-center">No chats yet</p>
        )}
        {conversations.map((c) => (
          <div
            key={c.id}
            className={clsx(
              "group flex items-center gap-1 rounded-xl px-3 py-2.5 cursor-pointer transition",
              activeId === c.id
                ? "bg-accent/15 border border-accent/25"
                : "hover:bg-white/5 border border-transparent"
            )}
          >
            <button className="flex-1 text-left min-w-0" onClick={() => onSelect(c.id)}>
              <p className="text-sm truncate font-medium">{c.title}</p>
              <p className="text-xs text-muted mt-0.5">{c.message_count} messages</p>
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(c.id);
              }}
              className="opacity-0 group-hover:opacity-100 text-muted hover:text-red-400 text-xs px-1"
            >
              ✕
            </button>
          </div>
        ))}
      </nav>
    </aside>
  );
}
