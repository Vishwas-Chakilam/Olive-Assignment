"use client";

import { useAuth } from "@/contexts/AuthContext";
import { updateProfile } from "@/lib/api";
import { fetchProviders, type ProviderInfo } from "@/lib/api";
import { useEffect, useState } from "react";

const themes = [
  { id: "dark", label: "Dark (default)" },
  { id: "midnight", label: "Midnight" },
  { id: "ocean", label: "Ocean" },
];

export default function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [defaultProvider, setDefaultProvider] = useState(user?.default_provider || "mock");
  const [defaultModel, setDefaultModel] = useState(user?.default_model || "mock-gpt");
  const [theme, setTheme] = useState(user?.theme || "dark");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetchProviders().then(setProviders);
  }, []);

  useEffect(() => {
    if (user) {
      setDefaultProvider(user.default_provider);
      setDefaultModel(user.default_model);
      setTheme(user.theme);
    }
  }, [user]);

  const save = async () => {
    await updateProfile({
      default_provider: defaultProvider,
      default_model: defaultModel,
      theme,
    });
    await refreshUser();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="p-6 md:p-10 max-w-2xl mx-auto w-full">
      <h1 className="text-2xl font-bold mb-1">Settings</h1>
      <p className="text-muted text-sm mb-8">Customize your chat defaults and appearance</p>

      <div className="space-y-6">
        <section className="glass p-6 shadow-card space-y-4">
          <h2 className="font-semibold text-sm uppercase tracking-wide text-muted">LLM defaults</h2>
          <div>
            <label className="text-xs text-muted block mb-1">Default provider</label>
            <select
              className="input-field"
              value={defaultProvider}
              onChange={(e) => {
                setDefaultProvider(e.target.value);
                const p = providers.find((x) => x.name === e.target.value);
                if (p?.default_model) setDefaultModel(p.default_model);
              }}
            >
              {providers.map((p) => (
                <option key={p.name} value={p.name}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-muted block mb-1">Default model</label>
            <input
              className="input-field"
              value={defaultModel}
              onChange={(e) => setDefaultModel(e.target.value)}
            />
          </div>
        </section>

        <section className="glass p-6 shadow-card space-y-4">
          <h2 className="font-semibold text-sm uppercase tracking-wide text-muted">Appearance</h2>
          <div className="grid gap-2">
            {themes.map((t) => (
              <label
                key={t.id}
                className={`flex items-center gap-3 rounded-xl border px-4 py-3 cursor-pointer transition ${
                  theme === t.id ? "border-accent/50 bg-accent/10" : "border-line hover:bg-white/5"
                }`}
              >
                <input
                  type="radio"
                  name="theme"
                  value={t.id}
                  checked={theme === t.id}
                  onChange={() => setTheme(t.id)}
                  className="accent-accent"
                />
                <span className="text-sm">{t.label}</span>
              </label>
            ))}
          </div>
          <p className="text-xs text-muted">Theme preference is saved to your profile (visual themes coming soon).</p>
        </section>

        <button onClick={save} className="btn-primary">
          {saved ? "Saved ✓" : "Save settings"}
        </button>
      </div>
    </div>
  );
}
