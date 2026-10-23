"use client";
import { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import { RequestReadiness } from "@/components/request-readiness";
import { fetchProfile } from "@/lib/api";

type Reply = {
  answer: string;
  route?: string;
  sources?: { title: string; category: string; chunk: number }[];
  rows?: Record<string, unknown>[];
  sql?: string;
  confirmation_id?: string;
  preview?: unknown;
  result?: unknown;
  status?: string;
  retry_available?: boolean;
};
type Entry = { question: string; reply?: Reply };
const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
export default function CopilotPage() {
  const [workspace, setWorkspace] = useState("readiness");
  const [name, setName] = useState("User"),
    [role, setRole] = useState("EMPLOYEE"),
    [message, setMessage] = useState(""),
    [mode, setMode] = useState("router"),
    [entries, setEntries] = useState<Entry[]>([]),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  useEffect(() => {
    const token = localStorage.getItem("hrms_access_token");
    if (!token) {
      window.location.href = "/login";
      return;
    }
    fetchProfile(token)
      .then((r) => {
        if (r.body && "data" in r.body && r.body.data) {
          setName(r.body.data.name);
          setRole(r.body.data.role);
        }
      })
      .catch(() => setError("Could not load your profile."));
  }, []);
  async function send(text: string, confirmation?: string) {
    if (busy || !text.trim()) return;
    setBusy(true);
    setError("");
    setEntries((old) => [
      ...old,
      { question: confirmation ? "Confirm action" : text },
    ]);
    setMessage("");
    try {
      const response = await fetch(
        base + "/api/v1/chat/" + (confirmation ? "actions" : mode),
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization:
              "Bearer " + localStorage.getItem("hrms_access_token"),
          },
          body: JSON.stringify({
            message: text,
            confirmation_id: confirmation,
          }),
        },
      );
      if (!response.ok)
        throw new Error(
          response.status === 401
            ? "Your session expired. Please sign in again."
            : "The request failed. Please try again.",
        );
      const body = await response.json();
      setEntries((old) =>
        old.map((e, i) =>
          i === old.length - 1 ? { ...e, reply: body.data } : e,
        ),
      );
      if (confirmation && !body.data?.retry_available)
        setEntries((old) =>
          old.map((e) =>
            e.reply?.confirmation_id === confirmation
              ? { ...e, reply: { ...e.reply, confirmation_id: undefined } }
              : e,
          ),
        );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }
  const examples = [
    "What is the sick leave policy?",
    "Show my project assignments",
    "Check my leave balance",
    "Create a ticket for VPN connection failure",
    ...(role !== "EMPLOYEE" ? ["Show employees with Python skills"] : []),
  ];
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <div className="min-w-0 flex-1">
        <Topbar name={name} title="RekhaCB / HR Copilot" />
        <main className="mx-auto max-w-5xl p-4 md:p-8">
          <div className="mb-7 rounded-3xl bg-[#112c31] p-7 text-white">
            <p className="text-xs uppercase tracking-[.25em] text-teal-200">
              RekhaCB / From question to considered action
            </p>
            <h1 className="mt-3 text-3xl font-semibold">
              Every request deserves a clear path.
            </h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-200">
              Ask about HR policies, explore people and projects, or prepare an
              HR request. You review every action before it is submitted.
            </p>
            <span className="mt-5 inline-block rounded-full bg-white/10 px-3 py-1 text-xs">
              Signed in as {role.toLowerCase()}
            </span>
          </div>
          <div
            className="mb-6 flex gap-2 rounded-2xl bg-[#eceee7] p-1"
            role="group"
            aria-label="Workspace"
          >
            <button
              onClick={() => setWorkspace("readiness")}
              aria-pressed={workspace === "readiness"}
              className={`flex-1 rounded-xl p-3 text-sm font-semibold ${workspace === "readiness" ? "bg-white shadow-sm" : "text-slate-500"}`}
            >
              Request Readiness
            </button>
            <button
              onClick={() => setWorkspace("copilot")}
              aria-pressed={workspace === "copilot"}
              className={`flex-1 rounded-xl p-3 text-sm font-semibold ${workspace === "copilot" ? "bg-white shadow-sm" : "text-slate-500"}`}
            >
              Ask the copilot
            </button>
          </div>
          {workspace === "readiness" ? (
            <RequestReadiness />
          ) : (
            <>
              <div className="mb-5 flex flex-wrap gap-2">
                {examples.map((q) => (
                  <button
                    disabled={busy}
                    key={q}
                    onClick={() => setMessage(q)}
                    className="rounded-xl border bg-white px-3 py-2 text-left text-xs hover:border-teal-600"
                  >
                    {q}
                  </button>
                ))}
              </div>
              <div aria-live="polite" className="space-y-5">
                {entries.map((e, i) => (
                  <article
                    key={i}
                    className="rounded-2xl border bg-white p-5 shadow-sm"
                  >
                    <p className="mb-4 text-sm font-medium text-slate-500">
                      You · {e.question}
                    </p>
                    {e.reply ? (
                      <>
                        <p className="mb-2 text-xs font-semibold uppercase text-teal-700">
                          RekhaCB · {e.reply.route}
                        </p>
                        <p className="whitespace-pre-wrap text-sm leading-7">
                          {e.reply.answer}
                        </p>
                        {e.reply.sources?.map((s, n) => (
                          <div
                            key={n}
                            className="mt-3 rounded-lg bg-teal-50 p-3 text-xs"
                          >
                            [{n + 1}] {s.title} · {s.category} · chunk {s.chunk}
                          </div>
                        ))}
                        {e.reply.rows && e.reply.rows.length > 0 && (
                          <div className="mt-4 overflow-x-auto">
                            <table className="w-full text-left text-xs">
                              <thead>
                                <tr>
                                  {Object.keys(e.reply.rows[0]).map((k) => (
                                    <th key={k} className="border-b p-2">
                                      {k}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {e.reply.rows.map((r, j) => (
                                  <tr key={j}>
                                    {Object.entries(r).map(([k, v]) => (
                                      <td className="border-b p-2" key={k}>
                                        {String(v ?? "—")}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                        {e.reply.sql && (
                          <details className="mt-3 text-xs">
                            <summary>Read-only query</summary>
                            <pre className="overflow-auto p-3">
                              {e.reply.sql}
                            </pre>
                          </details>
                        )}
                        {e.reply.preview != null && (
                          <pre className="mt-3 overflow-auto rounded-lg bg-slate-50 p-3 text-xs">
                            {JSON.stringify(e.reply.preview, null, 2)}
                          </pre>
                        )}
                        {e.reply.confirmation_id && (
                          <button
                            disabled={busy}
                            onClick={() =>
                              send("Confirm", e.reply?.confirmation_id)
                            }
                            className="mt-3 rounded-lg bg-teal-800 px-4 py-2 text-sm text-white disabled:opacity-50"
                          >
                            Confirm and submit
                          </button>
                        )}
                        {e.reply.result != null && (
                          <details className="mt-3 text-xs" open>
                            <summary>API result</summary>
                            <pre className="overflow-auto p-3">
                              {JSON.stringify(e.reply.result, null, 2)}
                            </pre>
                          </details>
                        )}
                      </>
                    ) : (
                      <p className="text-sm text-slate-500">
                        {busy
                          ? "Checking your request…"
                          : "No response received. You can try again."}
                      </p>
                    )}
                  </article>
                ))}
              </div>
              {error && (
                <p
                  role="alert"
                  className="mt-4 rounded-lg bg-rose-50 p-3 text-sm text-rose-800"
                >
                  {error}
                </p>
              )}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  send(message);
                }}
                className="mt-6 rounded-2xl border bg-white p-4"
              >
                <label htmlFor="mode" className="text-xs text-slate-500">
                  Assistant mode
                </label>
                <select
                  id="mode"
                  value={mode}
                  onChange={(e) => setMode(e.target.value)}
                  className="ml-3 rounded border p-1 text-xs"
                >
                  <option value="router">Automatic</option>
                  <option value="policy">Policy library</option>
                  <option value="sql">People & projects</option>
                  <option value="actions">HR actions</option>
                </select>
                <label htmlFor="question" className="sr-only">
                  Your HR question
                </label>
                <textarea
                  id="question"
                  maxLength={4000}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="What can I help you with?"
                  className="mt-3 min-h-24 w-full resize-y rounded-lg border p-3 text-sm"
                />
                <div className="flex items-center justify-between gap-3">
                  <span className="text-xs text-slate-500">
                    Answers use your access permissions. Verify important policy
                    decisions with HR.
                  </span>
                  <button
                    disabled={busy || !message.trim()}
                    className="rounded-lg bg-teal-800 px-5 py-2 text-white disabled:opacity-40"
                  >
                    {busy ? "Working…" : "Send"}
                  </button>
                </div>
              </form>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
