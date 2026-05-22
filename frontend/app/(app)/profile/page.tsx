"use client";

import { useAuth } from "@/contexts/AuthContext";
import { updateProfile } from "@/lib/api";
import { useState } from "react";

export default function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const [displayName, setDisplayName] = useState(user?.display_name || "");
  const [bio, setBio] = useState(user?.bio || "");
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  if (!user) return null;

  const save = async () => {
    setError("");
    setSaved(false);
    try {
      await updateProfile({ display_name: displayName, bio: bio || null });
      await refreshUser();
      setSaved(true);
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <div className="p-6 md:p-10 max-w-2xl mx-auto w-full">
      <h1 className="text-2xl font-bold mb-1">Profile</h1>
      <p className="text-muted text-sm mb-8">Your public identity on Ollive</p>

      <div className="glass p-8 shadow-card space-y-6">
        <div className="flex items-center gap-5">
          <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-accent to-accent2 flex items-center justify-center text-3xl font-bold shadow-glow">
            {(displayName || user.username)[0].toUpperCase()}
          </div>
          <div>
            <p className="text-lg font-semibold">{displayName || user.username}</p>
            <p className="text-muted text-sm">@{user.username}</p>
            <p className="text-muted text-xs mt-1">{user.email}</p>
          </div>
        </div>

        <div>
          <label className="text-xs text-muted block mb-1">Display name</label>
          <input
            className="input-field"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
        </div>
        <div>
          <label className="text-xs text-muted block mb-1">Bio</label>
          <textarea
            className="input-field min-h-[100px]"
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            placeholder="Tell us about yourself…"
          />
        </div>

        <div className="pt-4 border-t border-line grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-muted text-xs">Member since</p>
            <p>{new Date(user.created_at).toLocaleDateString()}</p>
          </div>
          <div>
            <p className="text-muted text-xs">Default model</p>
            <p>
              {user.default_provider} / {user.default_model}
            </p>
          </div>
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}
        {saved && <p className="text-sm text-accent2">Profile saved.</p>}
        <button onClick={save} className="btn-primary">
          Save profile
        </button>
      </div>
    </div>
  );
}
