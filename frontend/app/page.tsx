"use client";

import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";

import VoiceButton from "@/components/VoiceButton";

type Incident = {

  id: number;

  event_id: number;

  room_id: number | null;

  vendor_id: number | null;

  person_id: number | null;

  equipment_id: number | null;

  type: string;

  severity: string;

  status: string;

  source: string;

  title: string;

  description: string | null;

  extra_data: Record<string, unknown> | null;

  detected_at: string;

  resolved_at: string | null;

};

type PlanAction = {

  sequence: number;

  action_type: string;

  description: string;

};

type Plan = {

  plan_id: number;

  incident_id: number;

  summary: string;

  rationale: string;

  status: string;

  risk_level: string;

  estimated_cost: number;

  estimated_delay_minutes: number;

  expected_state?: {

    target_room?: string;

    source_room?: string;

    target_room_id?: number;

    source_room_id?: number;

    [key: string]: unknown;

  };

  actions?: PlanAction[];

  simulation_success?: boolean;

};

type AgentResult = {

  thread_id: string;

  status: string;

  approval_request?: {

    type: string;

    message: string;

    plan?: Plan;

  } | null;

  response?: string | null;

  selected_plan?: Plan | null;

  candidate_plans?: Plan[];

  simulated_plans?: Plan[];

  detected_problems?: Record<string, unknown>[];

  predictions?: Record<string, unknown>;

  execution_result?: Record<string, unknown> | null;

  verification_result?: Record<string, unknown> | null;

  recovery_result?: Record<string, unknown> | null;

  approval_status?: string | null;

};

type ExecutionRecord = {

  id: string;

  timestamp: string;

  plan_id: number | null;

  summary: string;

  status: string;

  verified: boolean;

  recovered: boolean;

};

type ActiveView = "agent" | "incidents" | "plans" | "executions";

const API_URL = "http://127.0.0.1:8000";

function severityWeight(severity: string) {

  switch (severity.toUpperCase()) {

    case "CRITICAL":

      return 4;

    case "HIGH":

      return 3;

    case "MEDIUM":

      return 2;

    case "LOW":

      return 1;

    default:

      return 0;

  }

}

function findIncidentForRequest(

request: string,

incidents: Incident[],

): Incident | undefined {

  const normalized = request.toLowerCase();

  let bestIncident: Incident | undefined;

  let bestScore = 0;

  for (const incident of incidents) {

    const haystack = [

      incident.title,

      incident.description ?? "",

      incident.type,

    ]

      .join(" ")

      .toLowerCase();

    let score = 0;

    const tokens = normalized.match(/[a-z0-9-]+/g) ?? [];

    for (const token of tokens) {

      if (token.length >= 4 && haystack.includes(token)) {

        score += 1;

      }

    }

    if (

      normalized.includes("projector") &&

      incident.type === "EQUIPMENT_FAILURE"

    ) {

      score += 5;

    }

    if (

      normalized.includes("crowd") &&

      incident.type === "CROWDING"

    ) {

      score += 5;

    }

    if (

      normalized.includes("double book") &&

      incident.type === "ROOM_DOUBLE_BOOKED"

    ) {

      score += 5;

    }

    if (

      normalized.includes("judge") &&

      incident.type === "PERSON_UNAVAILABLE"

    ) {

      score += 5;

    }

    if (

      normalized.includes("cater") &&

      incident.type === "VENDOR_CANCELLED"

    ) {

      score += 5;

    }

    if (score > bestScore) {

      bestScore = score;

      bestIncident = incident;

    }

  }

  return bestIncident;

}

function severityBadge(severity: string) {

  switch (severity.toUpperCase()) {

    case "CRITICAL":

      return "bg-red-500/15 text-red-300 border border-red-500/30";

    case "HIGH":

      return "bg-orange-500/15 text-orange-300 border border-orange-500/30";

    case "MEDIUM":

      return "bg-yellow-500/15 text-yellow-300 border border-yellow-500/30";

    case "LOW":

      return "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30";

    default:

      return "bg-zinc-800 text-zinc-300 border border-zinc-700";

  }

}

function riskBadge(risk: string) {

  switch (risk.toUpperCase()) {

    case "CRITICAL":

      return "bg-red-500/15 text-red-300 border border-red-500/30";

    case "HIGH":

      return "bg-orange-500/15 text-orange-300 border border-orange-500/30";

    case "MEDIUM":

      return "bg-yellow-500/15 text-yellow-300 border border-yellow-500/30";

    case "LOW":

      return "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30";

    default:

      return "bg-zinc-800 text-zinc-300 border border-zinc-700";

  }

}

function formatTime(timestamp: string) {

  try {

    return new Date(timestamp).toLocaleString();

  } catch {

    return timestamp;

  }

}

function uniquePlans(plans: Plan[]) {

  const seen = new Set<number>();

  return plans.filter((plan) => {

    if (seen.has(plan.plan_id)) {

      return false;

    }

    seen.add(plan.plan_id);

    return true;

  });

}

export default function Home() {

  const [activeView, setActiveView] =

    useState<ActiveView>("agent");

  const [incidents, setIncidents] =

    useState<Incident[]>([]);

  const [loading, setLoading] =

    useState(true);

  const [agentLoading, setAgentLoading] =

    useState(false);

  const [approvalLoading, setApprovalLoading] =

    useState(false);

  const [error, setError] =

    useState<string | null>(null);

  const [agentError, setAgentError] =

    useState<string | null>(null);

  const [agentResult, setAgentResult] =

    useState<AgentResult | null>(null);

  const [userInput, setUserInput] =

    useState("");

  const [selectedIncidentId, setSelectedIncidentId] =

    useState<number | null>(null);

  const [executionHistory, setExecutionHistory] =

    useState<ExecutionRecord[]>([]);
  
    const [speaking, setSpeaking] = useState(false);

  const lastSpokenResponseRef =
    useRef<string | null>(null);

  function speakResponse(text: string) {
  if (typeof window === "undefined") {
    return;
  }

  if (!("speechSynthesis" in window)) {
    return;
  }

  window.speechSynthesis.cancel();

  const cleanedText = text
    .replace(/^#{1,6}\s*/gm, "")
    .replace(/\*\*/g, "")
    .replace(/\*/g, "")
    .replace(/`/g, "")
    .replace(/\n+/g, ". ");

  const utterance =
    new SpeechSynthesisUtterance(cleanedText);

  utterance.rate = 1.0;
  utterance.pitch = 1.0;
  utterance.volume = 1.0;

  utterance.onstart = () => {
    setSpeaking(true);
  };

  utterance.onend = () => {
    setSpeaking(false);
  };

  utterance.onerror = () => {
    setSpeaking(false);
  };

  window.speechSynthesis.speak(
    utterance,
  );
}

function stopSpeaking() {
  if (
    typeof window !== "undefined" &&
    "speechSynthesis" in window
  ) {
    window.speechSynthesis.cancel();
  }

  setSpeaking(false);
}

useEffect(() => {
  const response = agentResult?.response;

  if (!response) {
    return;
  }

  if (
    lastSpokenResponseRef.current === response
  ) {
    return;
  }

  lastSpokenResponseRef.current = response;

  speakResponse(response);

  return () => {
    if (
      typeof window !== "undefined" &&
      "speechSynthesis" in window
    ) {
      window.speechSynthesis.cancel();
    }

    setSpeaking(false);
  };
}, [agentResult?.response]);

  useEffect(() => {

    async function loadIncidents() {

      try {

        setLoading(true);

        const response = await fetch(

          `${API_URL}/api/v1/incidents`,

        );

        if (!response.ok) {

          throw new Error(

            `API returned ${response.status}`,

          );

        }

        const data: Incident[] =

          await response.json();

        setIncidents(data);

        setError(null);

      } catch (err) {

        console.error(err);

        setError(

          "Unable to connect to the NexCord backend.",

        );

      } finally {

        setLoading(false);

      }

    }

    loadIncidents();

  }, []);

  const openIncidents = incidents.filter(

    (incident) =>

incident.status.toUpperCase() === "OPEN",

  );

  const highestRiskIncident =

    [...openIncidents].sort(

      (a, b) =>

        severityWeight(b.severity) -

        severityWeight(a.severity),

    )[0];

  const allPlans = uniquePlans([

    ...(agentResult?.candidate_plans ?? []),

    ...(agentResult?.simulated_plans ?? []),

  ]);

  async function reloadIncidents() {

    try {

      const response = await fetch(

        `${API_URL}/api/v1/incidents`,

      );

      if (!response.ok) {

        return;

      }

      const data: Incident[] =

        await response.json();

      setIncidents(data);

    } catch (err) {

      console.error(err);

    }

  }

  async function simulateResponse(

customRequest?: string,

incidentOverride?: Incident,

  ) {

    const targetIncident =

incidentOverride ??

      (customRequest?.trim()

        ? findIncidentForRequest(

customRequest,

            incidents,

          ) ?? highestRiskIncident

        : highestRiskIncident);

    if (!targetIncident) {

      setAgentError(

        "NexCord could not identify an incident to investigate.",

      );

      return;

    }

    try {

      setAgentLoading(true);

      setAgentError(null);

      setAgentResult(null);

      setSelectedIncidentId(targetIncident.id);

      let userRequest =

        customRequest?.trim() ||

        `Investigate and resolve this incident: ${targetIncident.title}`;

      if (

        !customRequest?.trim() &&

        targetIncident.type === "CROWDING"

      ) {

        userRequest =

          "The AI Workshop is overcrowded. Find the safest room with enough capacity and resolve the issue.";

      }

      const threadId =

        `ui-${targetIncident.id}-${Date.now()}`;

      const response = await fetch(

        `${API_URL}/api/v1/agent/run`,

        {

          method: "POST",

          headers: {

            "Content-Type":

              "application/json",

          },

          body: JSON.stringify({

            user_request: userRequest,

            event_id: targetIncident.event_id,

            approved_by_person_id: 1,

            thread_id: threadId,

          }),

        },

      );

      if (!response.ok) {

        throw new Error(

          `Agent API returned ${response.status}`,

        );

      }

      const data: AgentResult =

        await response.json();

      setAgentResult(data);

      setActiveView("agent");

    } catch (err) {

      console.error(err);

      setAgentError(

        "NexCord could not start the response analysis.",

      );

    } finally {

      setAgentLoading(false);

    }

  }

  

  async function submitUserRequest(

event: FormEvent<HTMLFormElement>,

  ) {

    event.preventDefault();

    const request = userInput.trim();

    if (!request) {

      return;

    }

    setUserInput("");

    await simulateResponse(request);

  }

  function handleVoiceTranscript(text: string) {
  const normalized = text
    .trim()
    .toLowerCase();

  if (!normalized) {
    return;
  }

  // When NexCord is waiting for approval, interpret
  // spoken approval/rejection as the human decision.
  if (
    agentResult?.status ===
    "AWAITING_APPROVAL"
  ) {
    const approveCommand =
      /\b(approve|approved|approve it|approve that|go ahead|execute|execute it|yes|confirm|confirmed)\b/.test(
        normalized,
      );

    const rejectCommand =
      /\b(reject|rejected|reject it|cancel|cancel it|no|deny|denied|don't execute|do not execute)\b/.test(
        normalized,
      );

    if (approveCommand && !rejectCommand) {
      void respondToApproval(true);
      return;
    }

    if (rejectCommand && !approveCommand) {
      void respondToApproval(false);
      return;
    }
  }

  // Otherwise treat the transcript as a normal user request.
  setUserInput(text);
  void simulateResponse(text);
}

function speakApprovalResult(
  approved: boolean,
  data: AgentResult,
  plan: Plan | null,
) {
  if (!approved) {
    speakResponse(
      "The plan was rejected. No operational changes were made.",
    );
    return;
  }

  const executionResult =
    data.execution_result;

  const verificationResult =
    data.verification_result;

  const recoveryResult =
    data.recovery_result;

  if (
    executionResult?.success === true &&
    verificationResult?.success === true
  ) {
    speakResponse(
      `Approved. ${plan?.summary ?? "The response plan"} was executed successfully and the resulting state was verified.`,
    );
    return;
  }

  if (
    executionResult &&
    executionResult.success === false &&
    recoveryResult?.success === true
  ) {
    speakResponse(
      `The approved plan could not be completed successfully. NexCord performed recovery actions and restored the previous operational state.`,
    );
    return;
  }

  if (
    executionResult?.success === false
  ) {
    speakResponse(
      `The approved plan failed during execution. NexCord did not complete the requested operational change.`,
    );
    return;
  }

  speakResponse(
    `The decision was approved, but NexCord could not confirm the final execution state.`,
  );
}


  async function respondToApproval(
  approved: boolean,
) {
  if (!agentResult?.thread_id) {
    return;
  }

  try {
    setApprovalLoading(true);
    setAgentError(null);

    const plan =
      agentResult.selected_plan ??
      agentResult.approval_request?.plan ??
      null;

    const response = await fetch(
      `${API_URL}/api/v1/agent/resume`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify({
          thread_id:
            agentResult.thread_id,
          approved,
        }),
      },
    );

    if (!response.ok) {
      throw new Error(
        `Agent resume API returned ${response.status}`,
      );
    }

    const data: AgentResult =
      await response.json();

    /*
     * The response returned by /resume may contain
     * the same analysis text that was already spoken.
     *
     * Mark it as already spoken so the response
     * effect does not replay it.
     */
    lastSpokenResponseRef.current =
      data.response ?? null;

    setAgentResult(data);

    if (approved) {
      const executionSucceeded =
        data.execution_result?.success === true;

      const verificationSucceeded =
        data.verification_result?.success === true;

      const recoverySucceeded =
        data.recovery_result?.success === true;

      setExecutionHistory((current) => [
        {
          id: `${Date.now()}-${data.thread_id}`,
          timestamp: new Date().toISOString(),
          plan_id: plan?.plan_id ?? null,
          summary:
            plan?.summary ??
            "Approved NexCord response plan",
          status: executionSucceeded
            ? "EXECUTED"
            : "EXECUTION_FAILED",
          verified:
            verificationSucceeded,
          recovered:
            recoverySucceeded,
        },
        ...current,
      ]);
    } else {
      setExecutionHistory((current) => [
        {
          id: `${Date.now()}-${data.thread_id}`,
          timestamp: new Date().toISOString(),
          plan_id: plan?.plan_id ?? null,
          summary:
            plan?.summary ??
            "NexCord response plan rejected",
          status: "REJECTED",
          verified: false,
          recovered: false,
        },
        ...current,
      ]);
    }

    /*
     * Speak the decision result rather than replaying
     * the original analysis.
     */
    speakApprovalResult(
      approved,
      data,
      plan,
    );

    await reloadIncidents();

    setActiveView("agent");
  } catch (err) {
    console.error(err);

    setAgentError(
      "NexCord could not process the approval decision.",
    );
  } finally {
    setApprovalLoading(false);
  }
}

  function openIncidentInAgent(incident: Incident) {

    setSelectedIncidentId(incident.id);

    setUserInput(

      `Investigate this incident: ${incident.title}`,

    );

    setActiveView("agent");

  }

  function renderPlanCard(

plan: Plan,

showControls = false,

  ) {

    const isSelected =

      agentResult?.selected_plan?.plan_id ===

      plan.plan_id;

    return (

      <div

key={plan.plan_id}

className={`rounded-2xl border p-5 ${

          isSelected

            ? "border-zinc-600 bg-zinc-900"

            : "border-zinc-800 bg-zinc-950/60"

        }`}

      >

        <div className="flex flex-col gap-4">

          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">

            <div>

              <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">

                {isSelected

                  ? "Selected plan"

                  : "Candidate plan"}{" "}

                #{plan.plan_id}

              </div>

              <h3 className="mt-2 text-lg font-semibold text-white">

                {plan.summary}

              </h3>

            </div>

            <span

className={`w-fit rounded-full px-3 py-1 text-xs font-medium ${riskBadge(

                plan.risk_level,

              )}`}

            >

              {plan.risk_level} RISK

            </span>

          </div>

          <p className="text-sm leading-6 text-zinc-400">

            {plan.rationale}

          </p>

          <div className="grid gap-3 sm:grid-cols-3">

            <div className="rounded-xl bg-zinc-900 p-3">

              <div className="text-xs text-zinc-500">

                Cost

              </div>

              <div className="mt-1 text-sm font-medium text-white">

                ₹

                {plan.estimated_cost.toLocaleString()}

              </div>

            </div>

            <div className="rounded-xl bg-zinc-900 p-3">

              <div className="text-xs text-zinc-500">

                Delay

              </div>

              <div className="mt-1 text-sm font-medium text-white">

                {plan.estimated_delay_minutes} min

              </div>

            </div>

            <div className="rounded-xl bg-zinc-900 p-3">

              <div className="text-xs text-zinc-500">

                Simulation

              </div>

              <div

className={`mt-1 text-sm font-medium ${

                  plan.simulation_success

                    ? "text-emerald-300"

                    : "text-red-300"

                }`}

              >

                {plan.simulation_success

                  ? "PASSED"

                  : "FAILED"}

              </div>

            </div>

          </div>

          {plan.expected_state && (

            <div className="grid gap-3 sm:grid-cols-2">

              {plan.expected_state.source_room && (

                <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-3">

                  <div className="text-xs text-zinc-500">

                    Source

                  </div>

                  <div className="mt-1 text-sm text-zinc-200">

                    {plan.expected_state.source_room}

                  </div>

                </div>

              )}

              {plan.expected_state.target_room && (

                <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-3">

                  <div className="text-xs text-zinc-500">

                    Target

                  </div>

                  <div className="mt-1 text-sm text-zinc-200">

                    {plan.expected_state.target_room}

                  </div>

                </div>

              )}

            </div>

          )}

          {plan.actions &&

            plan.actions.length > 0 && (

              <div>

                <div className="mb-3 text-xs uppercase tracking-[0.16em] text-zinc-500">

                  Actions

                </div>

                <div className="space-y-2">

                  {plan.actions

                    .slice()

                    .sort(

                      (a, b) =>

                        a.sequence - b.sequence,

                    )

                    .map((action) => (

                      <div

key={`${plan.plan_id}-${action.sequence}-${action.action_type}`}

className="rounded-xl bg-zinc-900 p-3"

                      >

                        <div className="text-xs font-medium text-zinc-300">

                          {action.action_type}

                        </div>

                        <div className="mt-1 text-sm leading-5 text-zinc-500">

                          {action.description}

                        </div>

                      </div>

                    ))}

                </div>

              </div>

            )}

          {showControls &&

            isSelected &&

            agentResult?.status ===

              "AWAITING_APPROVAL" && (

              <div className="border-t border-zinc-800 pt-5">

                <div className="mb-3 text-sm text-zinc-400">

                  NexCord will not execute this

                  plan without your approval.

                </div>

                <div className="flex flex-col gap-3 sm:flex-row">

                  <button

type="button"

onClick={() =>

                      respondToApproval(true)

                    }

disabled={approvalLoading}

className="rounded-xl bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-50"

                  >

                    {approvalLoading

                      ? "Processing..."

                      : "Approve & Execute"}

                  </button>

                  <button

type="button"

onClick={() =>

                      respondToApproval(false)

                    }

disabled={approvalLoading}

className="rounded-xl border border-zinc-700 px-5 py-3 text-sm font-medium text-zinc-300 transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50"

                  >

                    Reject

                  </button>

                </div>

              </div>

            )}

        </div>

      </div>

    );

  }

  function renderAgentView() {

    return (

      <div className="space-y-6">

        <div>

          <div className="text-sm text-zinc-500">

            Human-in-the-loop operations agent

          </div>

          <h2 className="mt-1 text-3xl font-semibold tracking-tight text-white">

            NexCord Agent

          </h2>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-zinc-500">

            Ask NexCord about incidents, risks,

            schedules, resources, or response

            plans. NexCord analyzes first and

            waits for approval before making

            operational changes.

          </p>

        </div>

        {selectedIncidentId && (

          <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 px-4 py-3 text-sm">

            <span className="text-zinc-500">

              Investigating incident

            </span>{" "}

            <span className="font-medium text-zinc-200">

              #{selectedIncidentId}

            </span>

          </div>

        )}

        <div className="rounded-3xl border border-zinc-800 bg-zinc-900 p-6 shadow-2xl shadow-black/20 lg:p-8">

          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-sm font-bold text-black">

              N

            </div>

            <div>

              <div className="font-medium text-white">

                NexCord

              </div>

              <div className="flex items-center gap-2 text-xs text-zinc-500">

                <span className="h-2 w-2 rounded-full bg-emerald-400" />

                Agent ready

              </div>

            </div>

          </div>

          <div className="mt-8 min-h-[180px]">

            {!agentResult && !agentLoading && (

              <div className="flex min-h-[160px] items-center justify-center text-center">

                <div>

                  <div className="text-4xl">◌</div>

                  <h3 className="mt-4 text-lg font-medium text-zinc-200">

                    What is happening?

                  </h3>

                  <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-zinc-500">

                    Ask about a problem such as a

                    projector failure, room conflict,

                    crowding, vendor cancellation, or

                    staffing issue.

                  </p>

                </div>

              </div>

            )}

            {agentLoading && (

              <div className="flex min-h-[160px] items-center justify-center">

                <div className="text-center">

                  <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-zinc-700 border-t-white" />

                  <p className="mt-4 text-sm text-zinc-400">

                    NexCord is analyzing the event...

                  </p>

                </div>

              </div>

            )}

            {agentResult && (

              <div className="space-y-5">

                <div className="flex flex-wrap items-center gap-3">

                  <span

className={`rounded-full px-3 py-1.5 text-xs font-medium ${

                      agentResult.status ===

                      "AWAITING_APPROVAL"

                        ? "bg-yellow-500/10 text-yellow-300"

                        : agentResult.status ===

                            "REJECTED"

                          ? "bg-red-500/10 text-red-300"

                          : "bg-emerald-500/10 text-emerald-300"

                    }`}

                  >

                    {agentResult.status}

                  </span>

                  {agentResult.approval_status && (

                    <span className="rounded-full bg-zinc-800 px-3 py-1.5 text-xs text-zinc-400">

                      Approval:{" "}

                      {agentResult.approval_status}

                    </span>

                  )}

                </div>

                {agentResult.response && (
                  <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
                    <div className="mb-4 flex items-center justify-between gap-4">
                      <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">
                        Agent analysis
                      </div>

                      <div className="flex items-center gap-2">
                        {speaking && (
                          <span className="text-xs text-zinc-500">
                            Speaking...
                          </span>
                        )}

                        <button
                          type="button"
                          onClick={() =>
                            speaking
                              ? stopSpeaking()
                              : speakResponse(agentResult.response ?? "")
                          }
                          className="rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-300 transition hover:bg-zinc-800"
                        >
                          {speaking ? "Stop" : "🔊 Speak"}
                        </button>
                      </div>
                    </div>

                    <div className="whitespace-pre-wrap text-sm leading-7 text-zinc-300">
                      {agentResult.response}
                    </div>
                  </div>
                )}

                {agentResult.selected_plan && (

                  <div>

                    <div className="mb-3 text-xs uppercase tracking-[0.16em] text-zinc-500">

                      Response plan

                    </div>

                    {renderPlanCard(

                      agentResult.selected_plan,

                      true,

                    )}

                  </div>

                )}

                {!agentResult.selected_plan &&

                  agentResult.status ===

                    "NO_VALID_PLAN" && (

                    <div className="rounded-2xl border border-yellow-500/20 bg-yellow-500/5 p-5">

                      <div className="font-medium text-yellow-200">

                        No executable plan was found.

                      </div>

                      <p className="mt-2 text-sm leading-6 text-yellow-100/60">

                        NexCord analyzed the event

                        but did not identify a safe,

                        executable response plan.

                      </p>

                    </div>

                  )}

                {agentResult.approval_status ===

                  "REJECTED" && (

                  <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-5">

                    <div className="font-medium text-red-200">

                      Plan rejected

                    </div>

                    <p className="mt-2 text-sm leading-6 text-red-100/60">

                      No operational changes were

                      authorized by this decision.

                    </p>

                  </div>

                )}

                {agentResult.execution_result && (

                  <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-5">

                    <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">

                      Execution state

                    </div>

                    <div className="mt-4 flex items-center gap-3">

                      <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />

                      <span className="text-sm font-medium text-emerald-300">

                        Execution completed

                      </span>

                    </div>

                  </div>

                )}

                {agentResult.verification_result && (

                  <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5">

                    <div className="text-xs uppercase tracking-[0.16em] text-emerald-300/60">

                      Verification

                    </div>

                    <div className="mt-3 flex items-center gap-3">

                      <span className="text-lg">

                        ✓

                      </span>

                      <span className="text-sm font-medium text-emerald-300">

                        Result verified against the

                        expected state.

                      </span>

                    </div>

                  </div>

                )}

                {agentResult.recovery_result && (

                  <div className="rounded-2xl border border-blue-500/20 bg-blue-500/5 p-5">

                    <div className="text-xs uppercase tracking-[0.16em] text-blue-300/60">

                      Recovery

                    </div>

                    <div className="mt-3 text-sm text-blue-200">

                      Recovery actions were

                      required and completed.

                    </div>

                  </div>

                )}

              </div>

            )}

          </div>

          <form

onSubmit={submitUserRequest}

className="mt-8"

          >

            <div className="rounded-2xl border border-zinc-700 bg-zinc-950 p-2">

              <div className="flex items-center gap-2">

                <input

value={userInput}

onChange={(event) =>

                    setUserInput(

                      event.target.value,

                    )

                  }

placeholder="Ask NexCord what is happening..."

className="min-w-0 flex-1 bg-transparent px-3 py-3 text-sm text-zinc-100 outline-none placeholder:text-zinc-600"

                />

                <VoiceButton
                  onTranscript={handleVoiceTranscript}
                />

                <button

type="submit"

disabled={

                    agentLoading ||

                    !userInput.trim()

                  }

className="rounded-xl bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-40"

                >

                  {agentLoading

                    ? "Analyzing..."

                    : "Send"}

                </button>

              </div>

            </div>

            <div className="mt-3 text-xs text-zinc-600">

              NexCord analyzes first, simulates a

              response, and requires explicit human

              approval before execution.

            </div>

          </form>

        </div>

        <div className="grid gap-4 md:grid-cols-3">

          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-5">

            <div className="text-xs uppercase tracking-[0.15em] text-zinc-500">

              Active incidents

            </div>

            <div className="mt-3 text-3xl font-semibold text-white">

              {openIncidents.length}

            </div>

            <div className="mt-1 text-sm text-zinc-500">

              Currently open

            </div>

          </div>

          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-5">

            <div className="text-xs uppercase tracking-[0.15em] text-zinc-500">

              Highest severity

            </div>

            <div className="mt-3 text-3xl font-semibold text-white">

              {highestRiskIncident?.severity ??

                "NONE"}

            </div>

            <div className="mt-1 text-sm text-zinc-500">

              Among open incidents

            </div>

          </div>

          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-5">

            <div className="text-xs uppercase tracking-[0.15em] text-zinc-500">

              Backend

            </div>

            <div className="mt-3 text-3xl font-semibold text-white">

              {error

                ? "DOWN"

                : loading

                  ? "..."

                  : "ONLINE"}

            </div>

            <div className="mt-1 text-sm text-zinc-500">

              FastAPI operational state

            </div>

          </div>

        </div>

      </div>

    );

  }

  function renderIncidentsView() {

    return (

      <div className="space-y-6">

        <div>

          <div className="text-sm text-zinc-500">

            Operational state

          </div>

          <h2 className="mt-1 text-3xl font-semibold text-white">

            Incidents

          </h2>

          <p className="mt-2 text-sm text-zinc-500">

            Active operational problems reported

            by NexCord&apos;s backend.

          </p>

        </div>

        {loading && (

          <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6 text-sm text-zinc-400">

            Loading incidents...

          </div>

        )}

        {!loading && incidents.length === 0 && (

          <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6 text-sm text-zinc-500">

            No incidents found.

          </div>

        )}

        {!loading && incidents.length > 0 && (

          <div className="grid gap-4 lg:grid-cols-2">

            {incidents.map((incident) => (

              <button

key={incident.id}

type="button"

onClick={() =>

                  openIncidentInAgent(

                    incident,

                  )

                }

className="text-left"

              >

                <div className="h-full rounded-2xl border border-zinc-800 bg-zinc-900/70 p-5 transition hover:border-zinc-600 hover:bg-zinc-900">

                  <div className="flex items-start justify-between gap-4">

                    <div>

                      <div className="text-xs uppercase tracking-[0.15em] text-zinc-500">

                        Incident #

                        {incident.id}

                      </div>

                      <h3 className="mt-2 text-lg font-semibold text-white">

                        {incident.title}

                      </h3>

                    </div>

                    <span

className={`rounded-full px-3 py-1.5 text-xs font-medium ${severityBadge(

                        incident.severity,

                      )}`}

                    >

                      {incident.severity}

                    </span>

                  </div>

                  <p className="mt-4 text-sm leading-6 text-zinc-400">

                    {incident.description ??

                      "No description provided."}

                  </p>

                  <div className="mt-5 flex flex-wrap gap-2">

                    <span className="rounded-lg bg-zinc-800 px-3 py-1.5 text-xs text-zinc-300">

                      {incident.type}

                    </span>

                    <span className="rounded-lg bg-zinc-800 px-3 py-1.5 text-xs text-zinc-400">

                      Event {incident.event_id}

                    </span>

                    <span className="rounded-lg bg-zinc-800 px-3 py-1.5 text-xs text-zinc-400">

                      {incident.status}

                    </span>

                  </div>

                  <div className="mt-5 text-xs text-zinc-600">

                    Click to investigate with NexCord →

                  </div>

                </div>

              </button>

            ))}

          </div>

        )}

      </div>

    );

  }

  function renderPlansView() {

    return (

      <div className="space-y-6">

        <div>

          <div className="text-sm text-zinc-500">

            Agent planning

          </div>

          <h2 className="mt-1 text-3xl font-semibold text-white">

            Plans

          </h2>

          <p className="mt-2 text-sm text-zinc-500">

            Candidate and simulated response

            plans generated during the current

            agent session.

          </p>

        </div>

        {!agentResult && (

          <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-8 text-center">

            <div className="text-lg font-medium text-zinc-200">

              No agent plans yet

            </div>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-zinc-500">

              Ask NexCord to analyze an incident.

              Generated plans will appear here.

            </p>

            <button

type="button"

onClick={() =>

                setActiveView("agent")

              }

className="mt-5 rounded-xl bg-white px-5 py-3 text-sm font-medium text-black hover:bg-zinc-200"

            >

              Open Agent

            </button>

          </div>

        )}

        {agentResult &&

          allPlans.length === 0 && (

            <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-8">

              <div className="text-lg font-medium text-zinc-200">

                No executable plans found

              </div>

              <p className="mt-2 text-sm leading-6 text-zinc-500">

                NexCord completed its analysis but

                did not generate a valid response

                plan for this incident.

              </p>

            </div>

          )}

        {allPlans.length > 0 && (

          <div className="space-y-4">

            {allPlans.map((plan) =>

              renderPlanCard(

                plan,

                true,

              ),

            )}

          </div>

        )}

      </div>

    );

  }

  function renderExecutionsView() {

    const currentExecution =

      agentResult?.execution_result;

    const currentVerification =

      agentResult?.verification_result;

    const currentRecovery =

      agentResult?.recovery_result;

    return (

      <div className="space-y-6">

        <div>

          <div className="text-sm text-zinc-500">

            Execution lifecycle

          </div>

          <h2 className="mt-1 text-3xl font-semibold text-white">

            Executions

          </h2>

          <p className="mt-2 text-sm text-zinc-500">

            Current execution state and decisions

            from this browser session.

          </p>

        </div>

        {agentResult && (

          <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">

            <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">

              Current agent execution

            </div>

            <div className="mt-5 space-y-4">

              <div className="flex items-center gap-3">

                <div

className={`flex h-9 w-9 items-center justify-center rounded-full ${

                    agentResult.approval_status ===

                    "REJECTED"

                      ? "bg-red-500/10 text-red-300"

                      : "bg-emerald-500/10 text-emerald-300"

                  }`}

                >

                  {agentResult.approval_status ===

                  "REJECTED"

                    ? "×"

                    : "1"}

                </div>

                <div>

                  <div className="text-sm font-medium text-zinc-200">

                    Approval

                  </div>

                  <div className="text-xs text-zinc-500">

                    {agentResult.approval_status ??

                      "PENDING"}

                  </div>

                </div>

              </div>

              <div className="h-px bg-zinc-800" />

              <div className="flex items-center gap-3">

                <div

className={`flex h-9 w-9 items-center justify-center rounded-full ${

                    currentExecution

                      ? "bg-emerald-500/10 text-emerald-300"

                      : "bg-zinc-800 text-zinc-500"

                  }`}

                >

                  2

                </div>

                <div>

                  <div className="text-sm font-medium text-zinc-200">

                    Execution

                  </div>

                  <div className="text-xs text-zinc-500">

                    {currentExecution

                      ? "Completed"

                      : "Not executed"}

                  </div>

                </div>

              </div>

              <div className="h-px bg-zinc-800" />

              <div className="flex items-center gap-3">

                <div

className={`flex h-9 w-9 items-center justify-center rounded-full ${

                    currentVerification

                      ? "bg-emerald-500/10 text-emerald-300"

                      : "bg-zinc-800 text-zinc-500"

                  }`}

                >

                  3

                </div>

                <div>

                  <div className="text-sm font-medium text-zinc-200">

                    Verification

                  </div>

                  <div className="text-xs text-zinc-500">

                    {currentVerification

                      ? "Verified"

                      : "Not verified"}

                  </div>

                </div>

              </div>

              <div className="h-px bg-zinc-800" />

              <div className="flex items-center gap-3">

                <div

className={`flex h-9 w-9 items-center justify-center rounded-full ${

                    currentRecovery

                      ? "bg-blue-500/10 text-blue-300"

                      : "bg-zinc-800 text-zinc-500"

                  }`}

                >

                  4

                </div>

                <div>

                  <div className="text-sm font-medium text-zinc-200">

                    Recovery

                  </div>

                  <div className="text-xs text-zinc-500">

                    {currentRecovery

                      ? "Recovery completed"

                      : "Not required"}

                  </div>

                </div>

              </div>

            </div>

          </div>

        )}

        {executionHistory.length === 0 ? (

          <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-8 text-center">

            <div className="text-lg font-medium text-zinc-200">

              No execution history yet

            </div>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-zinc-500">

              When you approve or reject a plan,

              NexCord will record that decision

              here for the current browser session.

            </p>

          </div>

        ) : (

          <div className="space-y-3">

            {executionHistory.map((record) => (

              <div

key={record.id}

className="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-5"

              >

                <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

                  <div>

                    <div className="text-xs uppercase tracking-[0.15em] text-zinc-500">

                      {record.plan_id

                        ? `Plan #${record.plan_id}`

                        : "Agent decision"}

                    </div>

                    <div className="mt-2 font-medium text-zinc-100">

                      {record.summary}

                    </div>

                    <div className="mt-2 text-xs text-zinc-600">

                      {formatTime(

                        record.timestamp,

                      )}

                    </div>

                  </div>

                  <span

className={`w-fit rounded-full px-3 py-1.5 text-xs font-medium ${

                      record.status === "EXECUTED"

                        ? "bg-emerald-500/10 text-emerald-300"

                        : record.status ===

                            "REJECTED"

                          ? "bg-red-500/10 text-red-300"

                          : "bg-yellow-500/10 text-yellow-300"

                    }`}

                  >

                    {record.status}

                  </span>

                </div>

                {record.status ===

                  "EXECUTED" && (

                  <div className="mt-4 flex flex-wrap gap-2">

                    <span className="rounded-lg bg-zinc-800 px-3 py-1.5 text-xs text-zinc-400">

                      Execution complete

                    </span>

                    {record.verified && (

                      <span className="rounded-lg bg-emerald-500/10 px-3 py-1.5 text-xs text-emerald-300">

                        ✓ Verified

                      </span>

                    )}

                    {record.recovered && (

                      <span className="rounded-lg bg-blue-500/10 px-3 py-1.5 text-xs text-blue-300">

                        Recovery completed

                      </span>

                    )}

                  </div>

                )}

              </div>

            ))}

          </div>

        )}

        <button

type="button"

onClick={() =>

            setActiveView("agent")

          }

className="rounded-xl border border-zinc-700 px-5 py-3 text-sm font-medium text-zinc-200 transition hover:bg-zinc-800"

        >

          Back to Agent

        </button>

      </div>

    );

  }

  function renderView() {

    switch (activeView) {

      case "incidents":

        return renderIncidentsView();

      case "plans":

        return renderPlansView();

      case "executions":

        return renderExecutionsView();

      case "agent":

      default:

        return renderAgentView();

    }

  }

  return (

    <main className="min-h-screen bg-zinc-950 text-zinc-100">

      <div className="flex min-h-screen">

        {/* Sidebar */}

        <aside className="hidden w-64 shrink-0 flex-col border-r border-zinc-800 bg-zinc-950 px-5 py-6 md:flex">

          <div>

            <div className="flex items-center gap-3">

              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white text-sm font-bold text-black">

                N

              </div>

              <div>

                <div className="text-lg font-semibold tracking-tight text-white">

                  NexCord

                </div>

                <div className="text-[10px] uppercase tracking-[0.14em] text-zinc-600">

                  Operations AI

                </div>

              </div>

            </div>

            <nav className="mt-10 space-y-1.5">

              <button

type="button"

onClick={() =>

                  setActiveView("agent")

                }

className={`w-full rounded-xl px-3.5 py-3 text-left text-sm font-medium transition ${

                  activeView === "agent"

                    ? "bg-white text-black"

                    : "text-zinc-400 hover:bg-zinc-900 hover:text-white"

                }`}

              >

                Agent

              </button>

              <button

type="button"

onClick={() =>

                  setActiveView("incidents")

                }

className={`w-full rounded-xl px-3.5 py-3 text-left text-sm font-medium transition ${

                  activeView === "incidents"

                    ? "bg-white text-black"

                    : "text-zinc-400 hover:bg-zinc-900 hover:text-white"

                }`}

              >

                Incidents

                {openIncidents.length > 0 && (

                  <span

className={`float-right rounded-full px-2 py-0.5 text-[10px] ${

                      activeView ===

                      "incidents"

                        ? "bg-black/10 text-black"

                        : "bg-zinc-800 text-zinc-400"

                    }`}

                  >

                    {openIncidents.length}

                  </span>

                )}

              </button>

              <button

type="button"

onClick={() =>

                  setActiveView("plans")

                }

className={`w-full rounded-xl px-3.5 py-3 text-left text-sm font-medium transition ${

                  activeView === "plans"

                    ? "bg-white text-black"

                    : "text-zinc-400 hover:bg-zinc-900 hover:text-white"

                }`}

              >

                Plans

              </button>

              <button

type="button"

onClick={() =>

                  setActiveView("executions")

                }

className={`w-full rounded-xl px-3.5 py-3 text-left text-sm font-medium transition ${

                  activeView === "executions"

                    ? "bg-white text-black"

                    : "text-zinc-400 hover:bg-zinc-900 hover:text-white"

                }`}

              >

                Executions

              </button>

            </nav>

          </div>

          <div className="mt-auto rounded-2xl border border-zinc-800 bg-zinc-900/60 p-4">

            <div className="text-[10px] uppercase tracking-[0.16em] text-zinc-600">

              System

            </div>

            <div className="mt-3 flex items-center gap-2 text-sm text-zinc-300">

              <span className="h-2 w-2 rounded-full bg-emerald-400" />

              All systems operational

            </div>

            <div className="mt-2 text-xs text-zinc-600">

              Human approval required

            </div>

          </div>

        </aside>

        {/* Main application */}

        <section className="min-w-0 flex-1">

          <header className="border-b border-zinc-800 bg-zinc-950/95 px-5 py-5 backdrop-blur lg:px-10">

            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

              <div>

                <div className="text-sm text-zinc-600">

                  GITAM TechFest 2026

                </div>

                <h1 className="mt-1 text-2xl font-semibold tracking-tight text-white">

                  {activeView ===

                    "agent" &&

                    "NexCord Agent"}

                  {activeView ===

                    "incidents" &&

                    "Operational Incidents"}

                  {activeView ===

                    "plans" &&

                    "Response Plans"}

                  {activeView ===

                    "executions" &&

                    "Execution State"}

                </h1>

              </div>

              <div className="flex items-center gap-3">

                <div className="flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-400">

                  <span

className={`h-2 w-2 rounded-full ${

                      error

                        ? "bg-red-400"

                        : "bg-emerald-400"

                    }`}

                  />

                  {error ? "API DOWN" : "LIVE"}

                </div>

              </div>

            </div>

            {/* Mobile navigation */}

            <div className="mt-5 flex gap-2 overflow-x-auto md:hidden">

              {(

                [

                  ["agent", "Agent"],

                  ["incidents", "Incidents"],

                  ["plans", "Plans"],

                  ["executions", "Executions"],

                ] as const

              ).map(([value, label]) => (

                <button

key={value}

type="button"

onClick={() =>

                    setActiveView(value)

                  }

className={`shrink-0 rounded-xl px-4 py-2 text-sm font-medium transition ${

                    activeView === value

                      ? "bg-white text-black"

                      : "bg-zinc-900 text-zinc-400"

                  }`}

                >

                  {label}

                </button>

              ))}

            </div>

          </header>

          <div className="px-5 py-7 lg:px-10 lg:py-10">

            {error && (

              <div className="mb-6 rounded-2xl border border-red-900 bg-red-950/30 p-4 text-sm text-red-300">

                {error}

              </div>

            )}

            {agentError && (

              <div className="mb-6 rounded-2xl border border-red-900 bg-red-950/30 p-4 text-sm text-red-300">

                {agentError}

              </div>

            )}

            {renderView()}

          </div>

        </section>

      </div>

    </main>

  );

}
