"use client";

import { useAuth } from "@/contexts/AuthContext";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function RegisterPage() {
  const { register, user, loading } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && user) router.replace("/chat");
  }, [user, loading, router]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await register({
        email,
        username,
        password,
        display_name: displayName || username,
      });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-10">
      <div className="glass w-full max-w-md p-8 shadow-card">
        <Link href="/" className="flex items-center gap-2 mb-8">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-accent2 text-sm font-bold">
            O
          </span>
          <span className="font-semibold">Create your account</span>
        </Link>

        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="text-xs text-muted mb-1 block">Display name</label>
            <input
              className="input-field"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Optional"
            />
          </div>
          <div>
            <label className="text-xs text-muted mb-1 block">Username</label>
            <input
              className="input-field"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
            />
          </div>
          <div>
            <label className="text-xs text-muted mb-1 block">Email</label>
            <input
              type="email"
              className="input-field"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="text-xs text-muted mb-1 block">Password</label>
            <input
              type="password"
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
          <button type="submit" className="btn-primary w-full" disabled={submitting}>
            {submitting ? "Creating…" : "Create account"}
          </button>
        </form>

        <p className="text-sm text-muted text-center mt-6">
          Already have an account?{" "}
          <Link href="/login" className="text-accent2 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
