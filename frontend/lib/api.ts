import { authHeaders, getToken } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Message = { role: "user" | "assistant" | "system"; content: string };

export type ConversationSummary = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
};

export type ConversationDetail = {
  id: string;
  title: string;
  messages: Message[];
};

export type ProviderInfo = { name: string; default_model: string | null };

export type UserProfile = import("./auth").UserProfile;

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: UserProfile;
};

export class ApiConnectionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiConnectionError";
  }
}

async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const headers: Record<string, string> = {
    ...authHeaders(),
    ...(init?.headers as Record<string, string> | undefined),
  };
  if (init?.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  try {
    return await fetch(`${API_BASE}${path}`, { ...init, headers });
  } catch (e) {
    const msg = (e as Error).message;
    if (msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
      throw new ApiConnectionError(
        `Cannot reach backend at ${API_BASE}. Run scripts\\start-backend.bat in a separate terminal.`
      );
    }
    throw e;
  }
}

export async function registerUser(data: {
  email: string;
  username: string;
  password: string;
  display_name?: string;
}): Promise<AuthResponse> {
  const res = await apiFetch("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err.detail;
    const msg = typeof detail === "string" ? detail : Array.isArray(detail) ? detail[0]?.msg : "Registration failed";
    throw new Error(msg || `Registration failed (${res.status})`);
  }
  return res.json();
}

export async function loginUser(data: { email: string; password: string }): Promise<AuthResponse> {
  const res = await apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Login failed");
  }
  return res.json();
}

export async function fetchMe(): Promise<UserProfile> {
  const res = await apiFetch("/auth/me");
  if (!res.ok) throw new Error("Session expired");
  return res.json();
}

export async function updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
  const res = await apiFetch("/auth/me", { method: "PATCH", body: JSON.stringify(data) });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Update failed");
  }
  return res.json();
}

export async function checkBackendHealth(): Promise<{
  ok: boolean;
  database?: string;
  message?: string;
}> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) return { ok: false, message: `Backend returned ${res.status}` };
    const data = await res.json();
    return {
      ok: data.status === "ok",
      database: data.database,
      message: data.database === "connected" ? undefined : "Database not connected",
    };
  } catch (e) {
    return { ok: false, message: (e as Error).message };
  }
}

export async function fetchConversations(): Promise<ConversationSummary[]> {
  if (!getToken()) return [];
  const res = await apiFetch("/conversations");
  if (res.status === 401) throw new Error("Session expired");
  if (!res.ok) throw new Error("Failed to load conversations");
  return res.json();
}

export async function fetchConversation(id: string): Promise<ConversationDetail> {
  const res = await apiFetch(`/conversations/${id}`);
  if (!res.ok) throw new Error("Failed to load conversation");
  return res.json();
}

export async function deleteConversation(id: string): Promise<void> {
  const res = await apiFetch(`/conversations/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete conversation");
}

export async function fetchProviders(): Promise<ProviderInfo[]> {
  try {
    const res = await fetch(`${API_BASE}/providers`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.providers;
  } catch {
    return [];
  }
}

export async function fetchMetrics() {
  const res = await apiFetch("/metrics");
  if (!res.ok) throw new Error("Failed to load metrics");
  return res.json();
}

export type StreamHandlers = {
  onMeta: (data: { conversation_id: string; request_id: string }) => void;
  onToken: (content: string) => void;
  onDone: (content: string) => void;
  onError: (message: string) => void;
  onCancelled?: () => void;
};

export async function streamChat(
  params: {
    message: string;
    conversationId?: string | null;
    provider?: string;
    model?: string;
  },
  handlers: StreamHandlers,
  signal?: AbortSignal
): Promise<void> {
  const res = await apiFetch("/chat", {
    method: "POST",
    body: JSON.stringify({
      message: params.message,
      conversation_id: params.conversationId || null,
      provider: params.provider,
      model: params.model,
      stream: true,
    }),
    signal,
  });

  if (!res.ok) {
    const errText = await res.text();
    let detail = errText;
    try {
      const parsed = JSON.parse(errText);
      detail = parsed.detail ?? parsed.message ?? errText;
    } catch {
      /* raw */
    }
    throw new Error(typeof detail === "string" ? detail : `Chat failed (${res.status})`);
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      try {
        const data = JSON.parse(line.slice(6));
        if (data.type === "meta") handlers.onMeta(data);
        else if (data.type === "token") handlers.onToken(data.content);
        else if (data.type === "done") handlers.onDone(data.content);
        else if (data.type === "error") handlers.onError(data.message);
        else if (data.type === "cancelled") handlers.onCancelled?.();
      } catch {
        /* ignore */
      }
    }
  }
}
