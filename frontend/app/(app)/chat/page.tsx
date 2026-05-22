"use client";

import { ChatWindow } from "@/components/ChatWindow";
import { ChatSidebar } from "@/components/ChatSidebar";
import { useAuth } from "@/contexts/AuthContext";
import {
  ApiConnectionError,
  checkBackendHealth,
  deleteConversation,
  fetchConversation,
  fetchConversations,
  fetchProviders,
  streamChat,
  type ConversationSummary,
  type Message,
  type ProviderInfo,
} from "@/lib/api";
import { useCallback, useEffect, useRef, useState } from "react";

export default function ChatPage() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [providers, setProviders] = useState<ProviderInfo[]>([
    { name: "mock", default_model: "mock-gpt" },
  ]);
  const [provider, setProvider] = useState(user?.default_provider || "mock");
  const [model, setModel] = useState(user?.default_model || "mock-gpt");
  const [backendError, setBackendError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (user) {
      setProvider(user.default_provider);
      setModel(user.default_model);
    }
  }, [user]);

  const refreshList = useCallback(async () => {
    try {
      const list = await fetchConversations();
      setConversations(list);
      setBackendError(null);
    } catch (e) {
      if (e instanceof ApiConnectionError) setBackendError(e.message);
      else if ((e as Error).message.includes("401") || (e as Error).message.includes("Session"))
        setBackendError("Session expired — please sign in again.");
      setConversations([]);
    }
  }, []);

  useEffect(() => {
    checkBackendHealth().then((h) => {
      if (!h.ok) setBackendError(h.message ?? "Backend unavailable");
    });
    refreshList();
    fetchProviders().then((p) => {
      if (p.length) setProviders(p);
    });
  }, [refreshList]);

  const loadConversation = async (id: string) => {
    try {
      const detail = await fetchConversation(id);
      setActiveId(id);
      setMessages(detail.messages);
    } catch (e) {
      setBackendError((e as Error).message);
    }
  };

  const handleNew = () => {
    abortRef.current?.abort();
    setActiveId(null);
    setMessages([]);
    setLoading(false);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteConversation(id);
      if (activeId === id) handleNew();
      await refreshList();
    } catch (e) {
      setBackendError((e as Error).message);
    }
  };

  const handleProviderChange = (p: string) => {
    setProvider(p);
    const info = providers.find((x) => x.name === p);
    if (info?.default_model) setModel(info.default_model);
  };

  const handleSend = async (text: string) => {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);
    const controller = new AbortController();
    abortRef.current = controller;
    let convId = activeId;
    let assistantSoFar = "";

    try {
      await streamChat(
        { message: text, conversationId: convId, provider, model },
        {
          onMeta: (data) => {
            convId = data.conversation_id;
            setActiveId(data.conversation_id);
          },
          onToken: (content) => {
            assistantSoFar += content;
            setMessages((prev) => {
              const copy = [...prev];
              const last = copy[copy.length - 1];
              if (last?.role === "assistant")
                copy[copy.length - 1] = { role: "assistant", content: assistantSoFar };
              else copy.push({ role: "assistant", content: assistantSoFar });
              return copy;
            });
          },
          onDone: (content) => {
            setMessages((prev) => {
              const copy = [...prev];
              const idx = copy.findIndex((m, i) => m.role === "assistant" && i === copy.length - 1);
              if (idx >= 0) copy[idx] = { role: "assistant", content };
              else copy.push({ role: "assistant", content });
              return copy;
            });
          },
          onError: (msg) => {
            setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${msg}` }]);
          },
          onCancelled: () => {
            setMessages((prev) => [...prev, { role: "assistant", content: "[Cancelled]" }]);
          },
        },
        controller.signal
      );
      setBackendError(null);
      await refreshList();
    } catch (e) {
      if ((e as Error).name !== "AbortError") {
        const msg = (e as Error).message;
        if (e instanceof ApiConnectionError) setBackendError(msg);
        setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${msg}` }]);
      }
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-0px)] md:h-screen">
      {backendError && (
        <div className="bg-red-500/10 border-b border-red-500/30 text-red-300 text-sm px-4 py-2 text-center shrink-0">
          {backendError}
        </div>
      )}
      <div className="flex flex-1 min-h-0">
        <ChatSidebar
          conversations={conversations}
          activeId={activeId}
          onSelect={loadConversation}
          onNew={handleNew}
          onDelete={handleDelete}
        />
        <ChatWindow
          messages={messages}
          loading={loading}
          providers={providers}
          provider={provider}
          model={model}
          onProviderChange={handleProviderChange}
          onModelChange={setModel}
          onSend={handleSend}
          onCancel={() => {
            abortRef.current?.abort();
            setLoading(false);
          }}
        />
      </div>
    </div>
  );
}
