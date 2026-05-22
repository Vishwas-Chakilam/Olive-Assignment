import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex items-center justify-between px-6 py-5 max-w-6xl mx-auto w-full">
        <div className="flex items-center gap-2">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-accent2 font-bold">
            O
          </span>
          <span className="font-semibold text-lg">Ollive</span>
        </div>
        <div className="flex gap-3">
          <Link href="/login" className="btn-ghost">
            Sign in
          </Link>
          <Link href="/register" className="btn-primary">
            Get started
          </Link>
        </div>
      </header>

      <section className="flex-1 flex flex-col items-center justify-center px-6 pb-20 text-center max-w-4xl mx-auto">
        <p className="text-xs font-medium uppercase tracking-widest text-accent2 mb-4">
          Inference observability platform
        </p>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6 bg-gradient-to-r from-white via-white to-muted bg-clip-text text-transparent">
          Chat with LLMs.
          <br />
          <span className="bg-gradient-to-r from-accent to-accent2 bg-clip-text text-transparent">
            Log every inference.
          </span>
        </h1>
        <p className="text-muted text-lg max-w-2xl mb-10 leading-relaxed">
          Multi-provider chat, real-time streaming, and a full ingestion pipeline for latency,
          tokens, and errors — built for engineers who care how AI systems run in production.
        </p>
        <div className="flex flex-wrap gap-4 justify-center">
          <Link href="/register" className="btn-primary text-base px-8 py-3">
            Start free →
          </Link>
          <Link href="/login" className="btn-ghost text-base px-8 py-3">
            Sign in
          </Link>
        </div>

        <div className="grid md:grid-cols-3 gap-4 mt-20 w-full text-left">
          {[
            {
              title: "Multi-provider",
              desc: "OpenAI, Gemini, Anthropic, or mock — switch models per conversation.",
            },
            {
              title: "Inference SDK",
              desc: "Every call logs latency, tokens, status, and previews to your database.",
            },
            {
              title: "Live dashboard",
              desc: "Throughput, error rate, and latency charts from real ingestion data.",
            },
          ].map((f) => (
            <div key={f.title} className="glass p-5 shadow-card">
              <h3 className="font-semibold mb-2">{f.title}</h3>
              <p className="text-sm text-muted leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
