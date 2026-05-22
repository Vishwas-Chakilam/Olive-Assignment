"use client";

import type { Message, ProviderInfo } from "@/lib/api";
import clsx from "clsx";
import { useEffect, useRef, useState } from "react";

type Props = {
  messages: Message[];
  loading: boolean;
  providers: ProviderInfo[];
  provider: string;
  model: string;
  onProviderChange: (p: string) => void;
  onModelChange: (m: string) => void;
  onSend: (text: string) => void;
  onCancel: () => void;
};

export function ChatWindow({
  messages,
  loading,
  providers,
  provider,
  model,
  onProviderChange,
  onModelChange,
  onSend,
  onCancel,
}: Props) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const submit = () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    onSend(text);
  };

  return (
    <div className="flex flex-col flex-1 min-w-0 h-full bg-background/40">
      <header className="flex flex-wrap items-center gap-3 px-4 md:px-6 py-4 border-b border-line">
        <select
          value={provider}
          onChange={(e) => onProviderChange(e.target.value)}
          className="input-field w-auto min-w-[120px] py-2"
          disabled={loading}
        >
          {providers.map((p) => (
            <option key={p.name} value={p.name}>
              {p.name}
            </option>
          ))}
        </select>
        <input
          value={model}
          onChange={(e) => onModelChange(e.target.value)}
          className="input-field flex-1 max-w-md py-2"
          placeholder="e.g. gemini-2.5-flash"
          disabled={loading}
        />
      </header>

      <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-5">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center max-w-md mx-auto">
            <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-accent/30 to-accent2/20 flex items-center justify-center text-2xl mb-4">
              ✦
            </div>
            <p className="text-lg font-medium">Start a conversation</p>
            <p className="text-sm text-muted mt-2">
              Every reply is logged with latency, tokens, and status to your observability pipeline.
            </p>
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={clsx(
              "max-w-[88%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap shadow-card",
              m.role === "user"
                ? "ml-auto bg-gradient-to-br from-accent to-accent/80 text-white"
                : "mr-auto glass border border-line"
            )}
          >
            {m.content}
          </div>
        ))}
        {loading && (
          <div className="mr-auto glass rounded-2xl px-4 py-3 text-sm text-muted flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-accent2 animate-pulse" />
            Generating…
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <footer className="p-4 border-t border-line bg-surface/40">
        <div className="flex gap-3 max-w-3xl mx-auto">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submit();
              }
            }}
            rows={2}
            placeholder="Ask anything…"
            className="input-field flex-1 resize-none"
            disabled={loading}
          />
          {loading ? (
            <button onClick={onCancel} className="rounded-xl bg-red-500/20 border border-red-500/40 text-red-300 px-5 py-2 text-sm font-medium shrink-0 hover:bg-red-500/30">
              Stop
            </button>
          ) : (
            <button onClick={submit} disabled={!input.trim()} className="btn-primary shrink-0 self-end">
              Send
            </button>
          )}
        </div>
      </footer>
    </div>
  );
}
