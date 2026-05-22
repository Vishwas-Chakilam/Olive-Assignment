"use client";

import {
  clearAuth,
  getStoredUser,
  getToken,
  setAuth,
  type UserProfile,
} from "@/lib/auth";
import { fetchMe, loginUser, registerUser } from "@/lib/api";
import { useRouter } from "next/navigation";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

type AuthContextValue = {
  user: UserProfile | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    username: string;
    password: string;
    display_name?: string;
  }) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const refreshUser = useCallback(async () => {
    if (!getToken()) {
      setUser(null);
      return;
    }
    try {
      const profile = await fetchMe();
      setUser(profile);
      setAuth(getToken()!, profile);
    } catch {
      clearAuth();
      setUser(null);
    }
  }, []);

  useEffect(() => {
    const stored = getStoredUser();
    if (stored && getToken()) setUser(stored);
    refreshUser().finally(() => setLoading(false));
  }, [refreshUser]);

  const login = async (email: string, password: string) => {
    const res = await loginUser({ email, password });
    setAuth(res.access_token, res.user);
    setUser(res.user);
    router.push("/chat");
  };

  const register = async (data: {
    email: string;
    username: string;
    password: string;
    display_name?: string;
  }) => {
    const res = await registerUser(data);
    setAuth(res.access_token, res.user);
    setUser(res.user);
    router.push("/chat");
  };

  const logout = () => {
    clearAuth();
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
