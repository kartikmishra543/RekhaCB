"use client";
import { useState } from "react";

type Plan = {
  leave_type: string;
  start_date: string;
  end_date: string;
  reason: string;
  is_half_day: boolean;
  half_day_period: string | null;
};
type Review = {
  status: string;
  headline: string;
  can_prepare: boolean;
  plan: Plan;
  checks: { key: string; state: string; title: string; detail: string }[];
  impact: {
    requested_days: number;
    available_days: number;
    projected_days: number;
    pending_days: number;
    counting_rule: string;
  };
  evidence: {
    answer: string;
    sources: { title: string; category: string; chunk: number }[];
  };
  approval_path: string;
  receipt: {
    fingerprint: string;
    generated_at: string;
    scope: string;
    meaning: string;
  };
};
type Proposal = {
  confirmation_id: string;
  preview: { tool: string; payload: Plan };
  readiness: Review;
};
const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const stateStyle: Record<string, string> = {
  pass: "border-teal-200 bg-teal-50 text-teal-950",
  warn: "border-amber-200 bg-amber-50 text-amber-950",
  block: "border-rose-200 bg-rose-50 text-rose-950",
  info: "border-slate-200 bg-slate-50 text-slate-700",
};
const stateLabel: Record<string, string> = {
  pass: "Checked",
  warn: "Review",
  block: "Blocked",
  info: "Next step",
};
function initialDate() {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}
export function RequestReadiness() {
  const [plan, setPlan] = useState<Plan>(() => ({
    leave_type: "CASUAL",
    start_date: initialDate(),
    end_date: initialDate(),
    reason: "",
    is_half_day: false,
    half_day_period: null,
  }));
  const [review, setReview] = useState<Review | null>(null),
    [baseline, setBaseline] = useState<Review | null>(null),
    [proposal, setProposal] = useState<Proposal | null>(null),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [result, setResult] = useState<{
      status: string;
      answer: string;
      result?: unknown;
    } | null>(null),
    [showBrief, setShowBrief] = useState(false);
  function update(p: Partial<Plan>) {
    setPlan((old) => ({ ...old, ...p }));
    setReview(null);
    setProposal(null);
    setResult(null);
    setError("");
  }
  async function request(path: string, body: unknown) {
    const response = await fetch(base + path, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("hrms_access_token"),
      },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      if (response.status === 401)
        throw new Error("Your session expired. Please sign in again.");
      if (response.status === 422)
        throw new Error("Check your dates, reason and half-day settings.");
      throw new Error("Could not check the request. Please try again.");
    }
    return response.json();
  }
  async function analyze(prepare = false) {
    setBusy(true);
    setError("");
    setProposal(null);
    setResult(null);
    try {
      const body = await request(
        "/api/v1/readiness/" + (prepare ? "prepare" : "analyze"),
        plan,
      );
      if (prepare && body.success) {
        setProposal(body.data);
        setReview(body.data.readiness);
      } else {
        setReview(body.data);
        if (prepare)
          setError(body.error?.message || "Resolve blocking checks first.");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }
  async function confirm() {
    if (!proposal || busy) return;
    setBusy(true);
    setError("");
    try {
      const body = await request("/api/v1/chat/actions", {
        message: "Confirm checked leave request",
        confirmation_id: proposal.confirmation_id,
      });
      setResult(body.data);
      if (!body.data?.retry_available) setProposal(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Submission failed");
      setProposal(null);
    } finally {
      setBusy(false);
    }
  }
  function exportReview() {
    if (!review) return;
    const blob = new Blob(
      [
        JSON.stringify(
          { project: "RekhaCB", review, comparison: baseline },
          null,
          2,
        ),
      ],
      { type: "application/json" },
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "rekhacb-request-review.json";
    a.click();
    URL.revokeObjectURL(url);
  }
  const brief = review
    ? `Leave request for review\n${review.plan.leave_type}: ${review.plan.start_date} to ${review.plan.end_date}${review.plan.is_half_day ? " (" + review.plan.half_day_period + ")" : ""}\nReason: ${review.plan.reason}\nRequested: ${review.impact.requested_days} days; available at review: ${review.impact.available_days}; projected: ${review.impact.projected_days}.\n${review.approval_path}\nReview notes: ${
        review.checks
          .filter((c) => c.state === "warn" || c.state === "block")
          .map((c) => c.detail)
          .join(" ") || "No warnings in this snapshot."
      }\nPolicy references: ${review.evidence.sources.map((s) => s.title + " (chunk " + s.chunk + ")").join(", ") || "None retrieved"}\nSnapshot: ${review.receipt.fingerprint.slice(0, 16)}. This is a readiness review, not an approval.`
    : "";
  return (
    <section aria-labelledby="studio-heading" className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-[1fr_1.1fr]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            analyze();
          }}
          className="rounded-3xl border border-[#ded9cd] bg-[#fffdf7] p-5 md:p-7"
        >
          <p className="text-xs font-semibold uppercase tracking-[.2em] text-teal-800">
            01 / Plan your request
          </p>
          <h2
            id="studio-heading"
            className="mt-3 text-2xl font-semibold text-[#173b35]"
          >
            Know before you submit.
          </h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Test a leave plan against your actual HR records. Nothing is
            submitted during a check.
          </p>
          <div className="mt-5 space-y-4">
            <label className="block text-sm font-medium">
              Leave type
              <select
                disabled={busy}
                value={plan.leave_type}
                onChange={(e) => update({ leave_type: e.target.value })}
                className="mt-1 w-full rounded-xl border bg-white p-3"
              >
                <option value="CASUAL">Casual leave</option>
                <option value="SICK">Sick leave</option>
                <option value="EARNED">Earned leave</option>
              </select>
            </label>
            <div className="grid grid-cols-2 gap-3">
              <label className="text-sm font-medium">
                From
                <input
                  required
                  disabled={busy}
                  type="date"
                  value={plan.start_date}
                  onChange={(e) => update({ start_date: e.target.value })}
                  className="mt-1 w-full rounded-xl border bg-white p-3"
                />
              </label>
              <label className="text-sm font-medium">
                Through
                <input
                  required
                  disabled={busy}
                  type="date"
                  value={plan.end_date}
                  onChange={(e) => update({ end_date: e.target.value })}
                  className="mt-1 w-full rounded-xl border bg-white p-3"
                />
              </label>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                disabled={busy}
                type="checkbox"
                checked={plan.is_half_day}
                onChange={(e) =>
                  update({
                    is_half_day: e.target.checked,
                    half_day_period: e.target.checked ? "FIRST_HALF" : null,
                    end_date: e.target.checked
                      ? plan.start_date
                      : plan.end_date,
                  })
                }
              />{" "}
              I only need half a day
            </label>
            {plan.is_half_day && (
              <label className="block text-sm">
                Which half?
                <select
                  disabled={busy}
                  value={plan.half_day_period || "FIRST_HALF"}
                  onChange={(e) => update({ half_day_period: e.target.value })}
                  className="ml-3 rounded border p-2"
                >
                  <option value="FIRST_HALF">First half</option>
                  <option value="SECOND_HALF">Second half</option>
                </select>
              </label>
            )}
            <label className="block text-sm font-medium">
              Reason
              <textarea
                required
                minLength={3}
                maxLength={500}
                disabled={busy}
                value={plan.reason}
                onChange={(e) => update({ reason: e.target.value })}
                placeholder="A short reason for your approver"
                className="mt-1 min-h-24 w-full rounded-xl border bg-white p-3"
              />
            </label>
            <button
              disabled={busy}
              className="w-full rounded-xl bg-[#173b35] px-4 py-3 font-medium text-white disabled:opacity-40"
            >
              {busy ? "Checking your records…" : "Check request readiness"}
            </button>
          </div>
          <p className="mt-3 text-xs leading-5 text-slate-500">
            Uses the HRMS calendar-day rule. Weekends count. Only your own leave
            records are checked.
          </p>
        </form>
        <div
          aria-live="polite"
          className="rounded-3xl border bg-white p-5 md:p-7"
        >
          <p className="text-xs font-semibold uppercase tracking-[.2em] text-teal-800">
            02 / Follow the evidence
          </p>
          {!review ? (
            <div className="py-12">
              <div
                className="mb-5 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-[#f0eee4] text-2xl text-teal-900"
                aria-hidden="true"
              >
                ↗
              </div>
              <h3 className="text-2xl font-medium">
                A clear path, not a mystery score.
              </h3>
              <p className="mt-3 text-sm leading-7 text-slate-500">
                Your review will show balance impact, date conflicts, pending
                commitments, policy references and the approval path. Change
                your dates to explore another option.
              </p>
            </div>
          ) : (
            <>
              <h3 className="mt-3 text-xl font-semibold">{review.headline}</h3>
              <div className="my-5 grid grid-cols-3 gap-2">
                {[
                  ["Available", review.impact.available_days],
                  ["Requested", review.impact.requested_days],
                  ["After request", review.impact.projected_days],
                ].map(([label, value]) => (
                  <div
                    key={String(label)}
                    className="rounded-xl bg-[#f5f4ed] p-3"
                  >
                    <p className="text-[11px] text-slate-500">{label}</p>
                    <p className="mt-1 text-2xl font-semibold text-teal-950">
                      {value}
                      <span className="ml-1 text-xs font-normal">days</span>
                    </p>
                  </div>
                ))}
              </div>
              <ol className="space-y-3">
                {review.checks.map((c, i) => (
                  <li
                    key={c.key}
                    className={`rounded-xl border p-3 ${stateStyle[c.state]}`}
                  >
                    <div className="flex justify-between gap-3">
                      <h4 className="text-sm font-semibold">
                        {String(i + 1).padStart(2, "0")} · {c.title}
                      </h4>
                      <span className="text-[10px] font-semibold uppercase">
                        {stateLabel[c.state]}
                      </span>
                    </div>
                    <p className="mt-1 text-xs leading-5">{c.detail}</p>
                  </li>
                ))}
              </ol>
            </>
          )}
        </div>
      </div>
      {error && (
        <p
          role="alert"
          className="rounded-xl bg-rose-50 p-4 text-sm text-rose-800"
        >
          {error}
        </p>
      )}
      {review && (
        <>
          <div className="grid gap-5 md:grid-cols-2">
            <div className="rounded-2xl border bg-white p-5">
              <p className="text-xs font-semibold uppercase tracking-widest text-teal-800">
                Policy evidence
              </p>
              <div className="mt-3 space-y-2">
                {review.evidence.sources.length ? (
                  review.evidence.sources.map((s, i) => (
                    <p key={i} className="rounded-lg bg-teal-50 p-3 text-sm">
                      [{i + 1}] {s.title} · chunk {s.chunk}
                    </p>
                  ))
                ) : (
                  <p className="text-sm text-slate-500">
                    No supporting references found.
                  </p>
                )}
              </div>
              <details className="mt-3 text-sm">
                <summary className="cursor-pointer">
                  Read retrieved policy context
                </summary>
                <p className="mt-3 whitespace-pre-wrap text-xs leading-6">
                  {review.evidence.answer}
                </p>
              </details>
            </div>
            <div className="rounded-2xl border bg-[#f5f4ed] p-5">
              <p className="text-xs font-semibold uppercase tracking-widest text-teal-800">
                What if I change my dates?
              </p>
              <p className="mt-3 text-sm leading-6 text-slate-600">
                Pin this review, edit the plan, then check again to compare the
                impact. Each option uses current records.
              </p>
              <button
                disabled={busy}
                onClick={() => setBaseline(review)}
                className="mt-3 rounded-lg border border-teal-900 px-3 py-2 text-sm"
              >
                Pin as comparison
              </button>
              {baseline && (
                <div className="mt-3 text-sm">
                  <p>
                    Pinned: {baseline.plan.start_date} →{" "}
                    {baseline.plan.end_date} · {baseline.impact.requested_days}{" "}
                    days
                  </p>
                  <p className="mt-2 font-semibold">
                    Current plan changes projected balance by{" "}
                    {review.impact.projected_days -
                      baseline.impact.projected_days}{" "}
                    days.
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    Includes any record changes since the pinned review.
                  </p>
                </div>
              )}
            </div>
          </div>
          <div className="rounded-3xl border border-teal-900/15 bg-[#173b35] p-5 text-white md:p-7">
            <p className="text-xs uppercase tracking-[.2em] text-teal-200">
              03 / Leave a useful handoff
            </p>
            <h3 className="mt-3 text-2xl font-medium">
              The context travels with the request.
            </h3>
            <p className="mt-2 text-sm leading-6 text-teal-50">
              Prepare a reviewable request, export the evidence snapshot, or use
              a short brief when speaking with your approver.
            </p>
            <div className="mt-5 flex flex-wrap gap-3">
              <button
                disabled={
                  busy ||
                  !review.can_prepare ||
                  !!proposal ||
                  result?.status === "completed"
                }
                onClick={() => analyze(true)}
                className="rounded-xl bg-[#e4bc79] px-4 py-3 text-sm font-semibold text-[#173b35] disabled:opacity-40"
              >
                Prepare checked request
              </button>
              <button
                onClick={exportReview}
                className="rounded-xl border border-white/30 px-4 py-3 text-sm"
              >
                Export review JSON
              </button>
              <button
                onClick={() => setShowBrief((v) => !v)}
                className="rounded-xl border border-white/30 px-4 py-3 text-sm"
              >
                {showBrief ? "Hide" : "Show"} approver brief
              </button>
            </div>
            {showBrief && (
              <textarea
                readOnly
                aria-label="Approver brief"
                value={brief}
                className="mt-4 min-h-56 w-full rounded-xl bg-white p-4 text-xs leading-6 text-slate-800"
              />
            )}
            <p className="mt-4 break-all text-[10px] text-teal-100">
              Review {review.receipt.fingerprint.slice(0, 16)} ·{" "}
              {new Date(review.receipt.generated_at).toLocaleString()} ·
              Snapshot only; not an approval or signature.
            </p>
          </div>
        </>
      )}
      {proposal && (
        <div className="rounded-2xl border border-amber-300 bg-amber-50 p-5">
          <h3 className="font-semibold">
            Final review · nothing submitted yet
          </h3>
          <pre className="mt-3 overflow-auto text-xs leading-6">
            {JSON.stringify(proposal.preview.payload, null, 2)}
          </pre>
          <div className="mt-4 flex gap-3">
            <button
              disabled={busy}
              onClick={confirm}
              className="rounded-lg bg-teal-900 px-4 py-2 text-sm text-white disabled:opacity-40"
            >
              Confirm and submit
            </button>
            <button
              disabled={busy}
              onClick={() => setProposal(null)}
              className="rounded-lg border px-4 py-2 text-sm"
            >
              Discard proposal
            </button>
          </div>
          <p className="mt-3 text-xs text-slate-600">
            Checks run again at confirmation. The HR API makes the final
            validation.
          </p>
        </div>
      )}
      {result && (
        <div role="status" className="rounded-2xl border bg-white p-5">
          <h3 className="font-semibold">
            {result.status === "completed"
              ? "Request submitted"
              : "Request needs attention"}
          </h3>
          <p className="mt-2 text-sm">{result.answer}</p>
          {result.result != null && (
            <pre className="mt-3 overflow-auto text-xs">
              {JSON.stringify(result.result, null, 2)}
            </pre>
          )}
          <a
            href="/leaves"
            className="mt-4 inline-block text-sm font-medium text-teal-800 underline"
          >
            Open Leaves to verify status →
          </a>
        </div>
      )}
    </section>
  );
}
