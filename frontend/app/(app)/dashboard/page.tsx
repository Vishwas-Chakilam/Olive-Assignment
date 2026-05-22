"use client";

import { ApiConnectionError, checkBackendHealth, fetchMetrics } from "@/lib/api";
import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Metrics = {
  total_requests: number;
  success_count: number;
  error_count: number;
  error_rate: number;
  avg_latency_ms: number;
  requests_per_minute: number;
  total_tokens: number;
  by_provider: Record<string, number>;
  latency_series: { time: string; avg_latency_ms: number }[];
  throughput_series: { time: string; requests: number }[];
  error_series: { time: string; errors: number; error_rate: number }[];
};

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="glass p-5 shadow-card">
      <p className="text-xs text-muted uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-bold mt-2 bg-gradient-to-r from-white to-muted bg-clip-text text-transparent">
        {value}
      </p>
      {sub && <p className="text-xs text-muted mt-1">{sub}</p>}
    </div>
  );
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      const health = await checkBackendHealth();
      if (!health.ok) {
        setError(health.message ?? "Backend unavailable");
        setMetrics(null);
        return;
      }
      try {
        const data = await fetchMetrics();
        setMetrics(data);
        setError(
          data.total_requests === 0
            ? "No inference logs yet. Send chat messages from the Chat page first."
            : null
        );
      } catch (e) {
        setError(e instanceof ApiConnectionError ? e.message : (e as Error).message);
        setMetrics(null);
      }
    };
    load();
    const id = setInterval(load, 10000);
    return () => clearInterval(id);
  }, []);

  const providerData = metrics
    ? Object.entries(metrics.by_provider).map(([name, count]) => ({ name, count }))
    : [];

  return (
    <div className="p-6 md:p-10 max-w-6xl mx-auto w-full">
      <h1 className="text-2xl font-bold mb-1">Observability</h1>
      <p className="text-muted text-sm mb-8">Inference metrics from the ingestion pipeline</p>

      {error && (
        <div className="glass border-amber-500/30 bg-amber-500/10 text-amber-200 text-sm px-4 py-3 rounded-xl mb-6">
          {error}
        </div>
      )}

      {metrics && metrics.total_requests > 0 && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard label="Avg latency" value={`${metrics.avg_latency_ms} ms`} />
            <StatCard label="Throughput" value={`${metrics.requests_per_minute} /min`} />
            <StatCard
              label="Error rate"
              value={`${(metrics.error_rate * 100).toFixed(1)}%`}
              sub={`${metrics.error_count} errors`}
            />
            <StatCard label="Tokens" value={metrics.total_tokens.toLocaleString()} />
          </div>

          <div className="grid lg:grid-cols-2 gap-6 mb-6">
            <div className="glass p-5 h-72 shadow-card">
              <h2 className="text-sm font-medium text-muted mb-4">Latency</h2>
              <ResponsiveContainer width="100%" height="85%">
                <LineChart data={metrics.latency_series}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#8b8ca8" }} />
                  <YAxis tick={{ fill: "#8b8ca8" }} />
                  <Tooltip contentStyle={{ background: "#141422", border: "1px solid rgba(255,255,255,0.1)" }} />
                  <Line type="monotone" dataKey="avg_latency_ms" stroke="#7c5cff" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="glass p-5 h-72 shadow-card">
              <h2 className="text-sm font-medium text-muted mb-4">Throughput</h2>
              <ResponsiveContainer width="100%" height="85%">
                <BarChart data={metrics.throughput_series}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#8b8ca8" }} />
                  <YAxis tick={{ fill: "#8b8ca8" }} />
                  <Tooltip contentStyle={{ background: "#141422", border: "1px solid rgba(255,255,255,0.1)" }} />
                  <Bar dataKey="requests" fill="#22d3ee" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {providerData.length > 0 && (
            <div className="glass p-5 h-64 shadow-card">
              <h2 className="text-sm font-medium text-muted mb-4">By provider</h2>
              <ResponsiveContainer width="100%" height="85%">
                <BarChart data={providerData}>
                  <XAxis dataKey="name" tick={{ fill: "#8b8ca8" }} />
                  <YAxis tick={{ fill: "#8b8ca8" }} />
                  <Tooltip contentStyle={{ background: "#141422", border: "1px solid rgba(255,255,255,0.1)" }} />
                  <Bar dataKey="count" fill="#7c5cff" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}

      {!metrics && !error && <p className="text-muted">Loading metrics…</p>}
    </div>
  );
}
