import { useState } from "react";
import "./App.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000";

function Accordion({
  title,
  label,
  count,
  defaultOpen = false,
  children,
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <section className={`accordion ${open ? "open" : ""}`}>
      <button
        className="accordion-header"
        onClick={() => setOpen(!open)}
      >
        <div>
          <span className="accordion-label">{label}</span>
          <h4>{title}</h4>
        </div>

        <div className="accordion-right">
          {count !== undefined && count !== null && (
            <span className="accordion-count">{count}</span>
          )}

          <span className="accordion-arrow">
            {open ? "−" : "+"}
          </span>
        </div>
      </button>

      {open && (
        <div className="accordion-content">
          {children}
        </div>
      )}
    </section>
  );
}

function App() {
  const [activePage, setActivePage] =
    useState("Investigate");

  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const menuItems = [
    { name: "Overview", icon: "⌂" },
    { name: "Investigate", icon: "⌕" },
    { name: "Documents", icon: "▤" },
    { name: "Memory", icon: "◉" },
  ];

  const runInvestigation = async () => {
    if (!question.trim()) {
      setError("Enter an investigation question first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/investigation?query=${encodeURIComponent(
          question
        )}`
      );

      if (!response.ok) {
        throw new Error("Investigation request failed.");
      }

      const data = await response.json();

      console.log("INDUS AI RESULT:", data);

      setResult(data);
    } catch (err) {
      console.error(err);

      setError(
        "Could not connect to the INDUS AI investigation engine."
      );
    } finally {
      setLoading(false);
    }
  };

  const reasoning =
    result?.reasoning_result || {};

  const caseFile =
    reasoning?.case_file || {};

  const investigationSummary =
    result?.summary ||
    result?.investigation_packet?.summary ||
    {};

  const confidence =
    caseFile?.investigation_confidence || {};

  const confirmedFacts =
    caseFile?.confirmed_facts || [];

  const rootCauses =
    caseFile?.root_cause_hypotheses || [];

  const contradictions =
    caseFile?.contradictions_and_gaps || [];

  const timeline =
    caseFile?.incident_reconstruction || [];

  const connections =
    caseFile?.cross_document_connections || [];

  const historicalConnections =
    caseFile?.historical_case_connections || [];

  const actions =
    caseFile?.recommended_next_actions || [];

  const impacts =
    caseFile?.operational_impact || [];

  const warnings =
    caseFile?.historical_warning_signals || [];

  const historicalCases =
    reasoning?.historical_memory_cases || [];

  const historicalMemoriesFound =
    reasoning?.historical_memories_found || 0;

  const getLevelClass = (level = "") => {
    const value = String(level).toLowerCase();

    if (value.includes("high")) return "high";
    if (value.includes("medium")) return "medium";
    if (value.includes("low")) return "low";

    return "neutral";
  };

  /*
    Build a short visual trace from the real
    incident reconstruction.

    We deliberately show only up to 4 major
    milestones here. The full timeline remains
    available below.
  */

  const evidenceTrace =
    timeline.length > 0
      ? timeline.slice(0, 4)
      : [];

  const topRootCause =
    rootCauses.find(
      (item) =>
        String(item.confidence)
          .toLowerCase()
          .includes("high")
    ) || rootCauses[0];

  const topImpact =
    impacts[0];

  const resetInvestigation = () => {
    setResult(null);
    setError("");
  };

  return (
    <div className="app">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-mark">
            I
          </div>

          <div>
            <h1>INDUS AI</h1>
            <p>Industrial Intelligence</p>
          </div>

        </div>

        <nav className="navigation">

          <p className="nav-label">
            WORKSPACE
          </p>

          {menuItems.map((item) => (
            <button
              key={item.name}
              className={
                activePage === item.name
                  ? "nav-item active"
                  : "nav-item"
              }
              onClick={() =>
                setActivePage(item.name)
              }
            >
              <span className="nav-icon">
                {item.icon}
              </span>

              {item.name}
            </button>
          ))}

        </nav>

        <div className="sidebar-footer">

          <div className="system-status">

            <span className="status-dot"></span>

            <div>
              <strong>Knowledge Brain</strong>
              <p>System operational</p>
            </div>

          </div>

        </div>

      </aside>

      {/* MAIN */}

      <main className="main-content">

        <header className="topbar">

          <div>
            <p className="eyebrow">
              INDUSTRIAL KNOWLEDGE INTELLIGENCE
            </p>

            <h2>{activePage}</h2>
          </div>

          <div className="topbar-status">
            <span className="status-dot"></span>
            AI Engine Online
          </div>

        </header>

        <section className="content">

          {activePage === "Investigate" ? (
            <>

              {/* LANDING HERO */}

              {!result && (
                <div className="hero">

                  <div className="hero-badge">
                    AI-POWERED INVESTIGATION
                  </div>

                  <h3>
                    Turn scattered industrial
                    records into{" "}
                    <span>
                      actionable intelligence.
                    </span>
                  </h3>

                  <p>
                    Ask a question across maintenance,
                    production, quality, inventory and
                    historical records. INDUS AI connects
                    the evidence for you.
                  </p>

                </div>
              )}

              {/* QUESTION WORKSPACE */}

              <div
                className={
                  result
                    ? "investigation-card compact"
                    : "investigation-card"
                }
              >

                <div className="card-heading">

                  <div>
                    <p className="section-label">
                      INVESTIGATION WORKSPACE
                    </p>

                    <h4>
                      What do you need to investigate?
                    </h4>
                  </div>

                  <span className="knowledge-chip">
                    Unified Knowledge Brain
                  </span>

                </div>

                <textarea
                  value={question}
                  onChange={(e) =>
                    setQuestion(e.target.value)
                  }
                  placeholder="Example: Investigate the surface finish and flatness quality problems affecting Pump Line 2..."
                />

                <div className="investigation-footer">

                  <p>
                    Searches connected evidence and
                    organizational memory.
                  </p>

                  <div className="investigation-actions">

                    {result && (
                      <button
                        className="secondary-button"
                        onClick={resetInvestigation}
                      >
                        New Investigation
                      </button>
                    )}

                    <button
                      className="investigate-button"
                      onClick={runInvestigation}
                      disabled={loading}
                    >
                      {loading
                        ? "Investigating..."
                        : (
                          <>
                            Run Investigation
                            <span>→</span>
                          </>
                        )}
                    </button>

                  </div>

                </div>

              </div>

              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}

              {loading && (
                <div className="analysis-status">

                  <div className="analysis-loader"></div>

                  <div>
                    <strong>
                      INDUS AI is investigating
                    </strong>

                    <p>
                      Discovering relevant records,
                      connecting evidence, checking
                      organizational memory and building
                      the case...
                    </p>
                  </div>

                </div>
              )}

              {/* LANDING CAPABILITIES */}

              {!result && !loading && (
                <div className="capabilities">

                  <div className="capability-card">
                    <span className="capability-number">
                      01
                    </span>

                    <h5>
                      Cross-Document Reasoning
                    </h5>

                    <p>
                      Connect maintenance, production,
                      quality and customer records
                      automatically.
                    </p>
                  </div>

                  <div className="capability-card">
                    <span className="capability-number">
                      02
                    </span>

                    <h5>
                      Evidence-First Analysis
                    </h5>

                    <p>
                      Trace important findings back to
                      the records that support them.
                    </p>
                  </div>

                  <div className="capability-card">
                    <span className="capability-number">
                      03
                    </span>

                    <h5>
                      Organizational Memory
                    </h5>

                    <p>
                      Learn from previous investigations
                      without treating historical cases
                      as current proof.
                    </p>
                  </div>

                </div>
              )}

              {/* RESULTS */}

              {result && (
                <div className="results-dashboard">

                  {/* COMPACT CASE HEADER */}

                  <section className="result-header compact-result">

                    <div className="result-title-area">

                      <p className="section-label">
                        INVESTIGATION COMPLETE
                      </p>

                      <h3>
                        {caseFile?.case_title ||
                          "Industrial Investigation"}
                      </h3>

                    </div>

                    <div
                      className={`confidence-badge ${getLevelClass(
                        confidence?.level
                      )}`}
                    >
                      <span>
                        {confidence?.level ||
                          "ANALYZED"}
                      </span>

                      CONFIDENCE
                    </div>

                  </section>

                  {/* METRICS */}

                  <section className="metrics-grid compact-metrics">

                    <div className="metric-card">
                      <span className="metric-value">
                        {
                          investigationSummary
                            ?.documents_consulted ??
                          investigationSummary
                            ?.documents_discovered ??
                          "—"
                        }
                      </span>

                      <span className="metric-label">
                        Documents
                      </span>
                    </div>

                    <div className="metric-card">
                      <span className="metric-value">
                        {
                          investigationSummary
                            ?.evidence_found ??
                          investigationSummary
                            ?.semantic_matches_found ??
                          confirmedFacts.length
                        }
                      </span>

                      <span className="metric-label">
                        Evidence Items
                      </span>
                    </div>

                    <div className="metric-card">
                      <span className="metric-value">
                        {historicalMemoriesFound}
                      </span>

                      <span className="metric-label">
                        Past Cases
                      </span>
                    </div>

                    <div className="metric-card">
                      <span className="metric-value">
                        {contradictions.length}
                      </span>

                      <span className="metric-label">
                        Gaps / Conflicts
                      </span>
                    </div>

                  </section>

                  {/* FAST ANSWER */}

                  <section className="quick-intelligence">

                    <div className="quick-card cause-card">

                      <div className="quick-card-top">
                        <span className="quick-icon">
                          RC
                        </span>

                        <span className="quick-label">
                          MOST LIKELY ROOT CAUSE
                        </span>
                      </div>

                      <h4>
                        {topRootCause?.hypothesis ||
                          "Root cause requires further verification."}
                      </h4>

                      {topRootCause?.confidence && (
                        <span
                          className={`level-pill ${getLevelClass(
                            topRootCause.confidence
                          )}`}
                        >
                          {topRootCause.confidence}
                        </span>
                      )}

                    </div>

                    <div className="quick-card impact-card">

                      <div className="quick-card-top">
                        <span className="quick-icon">
                          IM
                        </span>

                        <span className="quick-label">
                          OPERATIONAL IMPACT
                        </span>
                      </div>

                      <h4>
                        {topImpact?.impact ||
                          "Impact assessed from connected industrial records."}
                      </h4>

                    </div>

                  </section>

                  {/* EXECUTIVE SUMMARY */}

                  {caseFile?.executive_assessment && (
                    <section className="executive-snapshot">

                      <div className="snapshot-heading">

                        <div>
                          <p className="section-label">
                            WHAT HAPPENED
                          </p>

                          <h4>
                            Executive Assessment
                          </h4>
                        </div>

                        <span className="current-evidence-chip">
                          Current Evidence
                        </span>

                      </div>

                      <p>
                        {caseFile.executive_assessment}
                      </p>

                    </section>
                  )}

                  {/* EVIDENCE TRACE */}

                  {evidenceTrace.length > 0 && (
                    <section className="evidence-trace-section">

                      <div className="trace-heading">

                        <div>
                          <p className="section-label">
                            EVIDENCE TRACE
                          </p>

                          <h4>
                            How the incident unfolded
                          </h4>
                        </div>

                        <span className="neutral-chip">
                          CROSS-RECORD VIEW
                        </span>

                      </div>

                      <div className="evidence-trace">

                        {evidenceTrace.map(
                          (item, index) => (
                            <div
                              className="trace-step"
                              key={index}
                            >

                              <div className="trace-node">
                                {index + 1}
                              </div>

                              {index <
                                evidenceTrace.length - 1 && (
                                <div className="trace-connector">
                                  <span>→</span>
                                </div>
                              )}

                              <div className="trace-card">

                                <span className="trace-date">
                                  {item.date ||
                                    "Date unknown"}
                                </span>

                                <h5>
                                  {item.event}
                                </h5>

                                {item.significance && (
                                  <p>
                                    {item.significance}
                                  </p>
                                )}

                              </div>

                            </div>
                          )
                        )}

                      </div>

                      <p className="trace-note">
                        This view summarizes major milestones.
                        Open the full timeline below for the
                        complete incident reconstruction.
                      </p>

                    </section>
                  )}

                  {/* ATTENTION */}

                  {contradictions.length > 0 && (
                    <section className="attention-summary">

                      <div className="attention-symbol">
                        !
                      </div>

                      <div className="attention-copy">
                        <span>
                          ATTENTION REQUIRED
                        </span>

                        <h4>
                          {contradictions.length} unresolved{" "}
                          {contradictions.length === 1
                            ? "evidence issue"
                            : "evidence issues"}
                        </h4>

                        <p>
                          INDUS AI found conflicting records
                          or missing evidence that should be
                          verified before final closure.
                        </p>
                      </div>

                      <span className="attention-count">
                        {contradictions.length}
                      </span>

                    </section>
                  )}

                  {/* DEEP INVESTIGATION */}

                  <div className="deep-analysis-heading">

                    <div>
                      <p className="section-label">
                        DEEP INVESTIGATION
                      </p>

                      <h3>
                        Explore the reasoning
                      </h3>

                      <p>
                        Expand only the evidence you want
                        to inspect.
                      </p>
                    </div>

                  </div>

                  {/* CONFLICTS */}

                  {contradictions.length > 0 && (
                    <Accordion
                      label="ATTENTION REQUIRED"
                      title="Record Conflicts & Missing Evidence"
                      count={contradictions.length}
                      defaultOpen={true}
                    >

                      <div className="stack-list">

                        {contradictions.map(
                          (item, index) => (
                            <div
                              className="conflict-card"
                              key={index}
                            >

                              <div className="conflict-icon">
                                !
                              </div>

                              <div>
                                <h5>
                                  {item.issue ||
                                    "Evidence gap detected"}
                                </h5>

                                {item.why_it_matters && (
                                  <p>
                                    {item.why_it_matters}
                                  </p>
                                )}

                                {item.needed_evidence && (
                                  <div className="needed-evidence">
                                    <strong>
                                      Evidence needed
                                    </strong>

                                    <span>
                                      {item.needed_evidence}
                                    </span>
                                  </div>
                                )}
                              </div>

                            </div>
                          )
                        )}

                      </div>

                    </Accordion>
                  )}

                  {/* ROOT CAUSES */}

                  {rootCauses.length > 0 && (
                    <Accordion
                      label="CAUSAL ANALYSIS"
                      title="Root Cause Hypotheses"
                      count={rootCauses.length}
                    >

                      <div className="hypothesis-grid">

                        {rootCauses.map(
                          (item, index) => (
                            <div
                              className="hypothesis-card"
                              key={index}
                            >

                              <div className="hypothesis-top">

                                <span
                                  className={`level-pill ${getLevelClass(
                                    item.confidence
                                  )}`}
                                >
                                  {item.confidence ||
                                    "UNRATED"}
                                </span>

                                <span className="hypothesis-number">
                                  H{index + 1}
                                </span>

                              </div>

                              <h5>
                                {item.hypothesis}
                              </h5>

                              {item.supporting_evidence && (
                                <div className="evidence-block">
                                  <strong>
                                    Supporting evidence
                                  </strong>

                                  <p>
                                    {
                                      item.supporting_evidence
                                    }
                                  </p>
                                </div>
                              )}

                              {item.contradicting_or_limiting_evidence && (
                                <div className="limitation-block">
                                  <strong>
                                    Limits / uncertainty
                                  </strong>

                                  <p>
                                    {
                                      item
                                        .contradicting_or_limiting_evidence
                                    }
                                  </p>
                                </div>
                              )}

                              {item.verification_needed && (
                                <div className="verification-block">
                                  <strong>
                                    Verify next
                                  </strong>

                                  <p>
                                    {
                                      item.verification_needed
                                    }
                                  </p>
                                </div>
                              )}

                            </div>
                          )
                        )}

                      </div>

                    </Accordion>
                  )}

                  {/* CONNECTIONS */}

                  {connections.length > 0 && (
                    <Accordion
                      label="KNOWLEDGE CONNECTIONS"
                      title="Cross-Document Connections"
                      count={connections.length}
                    >

                      <div className="connection-list">

                        {connections.map(
                          (item, index) => (
                            <div
                              className="connection-card"
                              key={index}
                            >

                              <div className="connection-line">
                                <span></span>
                                <span></span>
                                <span></span>
                              </div>

                              <div>

                                <div className="connection-card-top">

                                  <span className="connection-index">
                                    CONNECTION {index + 1}
                                  </span>

                                  {item.classification && (
                                    <span className="classification-chip">
                                      {item.classification}
                                    </span>
                                  )}

                                </div>

                                <h5>
                                  {item.connection}
                                </h5>

                                {item.interpretation && (
                                  <p>
                                    {item.interpretation}
                                  </p>
                                )}

                              </div>

                            </div>
                          )
                        )}

                      </div>

                    </Accordion>
                  )}

                  {/* TIMELINE */}

                  {timeline.length > 0 && (
                    <Accordion
                      label="INCIDENT RECONSTRUCTION"
                      title="Full Investigation Timeline"
                      count={`${timeline.length} events`}
                    >

                      <div className="timeline">

                        {timeline.map(
                          (item, index) => (
                            <div
                              className="timeline-item"
                              key={index}
                            >

                              <div className="timeline-marker">

                                <span className="timeline-dot">
                                </span>

                                {index !==
                                  timeline.length - 1 && (
                                  <span className="timeline-line">
                                  </span>
                                )}

                              </div>

                              <div className="timeline-content">

                                <div className="timeline-date">
                                  {item.date ||
                                    "Date unknown"}

                                  {item.time &&
                                    item.time !==
                                      "Unknown" && (
                                      <span>
                                        {item.time}
                                      </span>
                                    )}
                                </div>

                                <h5>
                                  {item.event}
                                </h5>

                                {item.significance && (
                                  <p>
                                    {item.significance}
                                  </p>
                                )}

                              </div>

                            </div>
                          )
                        )}

                      </div>

                    </Accordion>
                  )}

                  {/* FACTS */}

                  {confirmedFacts.length > 0 && (
                    <Accordion
                      label="VERIFIED EVIDENCE"
                      title="Confirmed Facts"
                      count={confirmedFacts.length}
                    >

                      <div className="facts-list">

                        {confirmedFacts.map(
                          (item, index) => (
                            <div
                              className="fact-card"
                              key={index}
                            >

                              <span className="fact-check">
                                ✓
                              </span>

                              <div>
                                <p>
                                  {item.finding}
                                </p>

                                {item.sources?.length >
                                  0 && (
                                  <div className="source-tags">

                                    {item.sources.map(
                                      (
                                        source,
                                        sourceIndex
                                      ) => (
                                        <span
                                          key={
                                            sourceIndex
                                          }
                                        >
                                          {
                                            source.document
                                          }

                                          {source.chunk_number !==
                                            undefined &&
                                            ` · chunk ${source.chunk_number}`}
                                        </span>
                                      )
                                    )}

                                  </div>
                                )}
                              </div>

                            </div>
                          )
                        )}

                      </div>

                    </Accordion>
                  )}

                  {/* IMPACT */}

                  {impacts.length > 0 && (
                    <Accordion
                      label="BUSINESS IMPACT"
                      title="Operational Impact"
                      count={impacts.length}
                    >

                      <div className="simple-grid">

                        {impacts.map(
                          (item, index) => (
                            <div
                              className="simple-card"
                              key={index}
                            >
                              <span className="simple-index">
                                {String(
                                  index + 1
                                ).padStart(2, "0")}
                              </span>

                              <p>
                                {item.impact}
                              </p>
                            </div>
                          )
                        )}

                      </div>

                    </Accordion>
                  )}

                  {/* WARNING SIGNALS */}

                  {warnings.length > 0 && (
                    <Accordion
                      label="EARLY INDICATORS"
                      title="Historical Warning Signals"
                      count={warnings.length}
                    >

                      <div className="simple-grid">

                        {warnings.map(
                          (item, index) => (
                            <div
                              className="warning-card"
                              key={index}
                            >
                              <h5>
                                {item.signal}
                              </h5>

                              <p>
                                {item.why_it_matters}
                              </p>
                            </div>
                          )
                        )}

                      </div>

                    </Accordion>
                  )}

                  {/* MEMORY */}

                  {(historicalMemoriesFound > 0 ||
                    historicalConnections.length >
                      0) && (
                    <Accordion
                      label="ORGANIZATIONAL MEMORY"
                      title="Related Historical Knowledge"
                      count={historicalMemoriesFound}
                    >

                      <div className="memory-notice">
                        Historical cases guide the
                        investigation and reveal recurring
                        patterns. They are not treated as
                        current-case proof.
                      </div>

                      {historicalCases.length > 0 && (
                        <div className="memory-case-list">

                          {historicalCases.map(
                            (item, index) => (
                              <div
                                className="memory-case"
                                key={index}
                              >

                                <span className="memory-icon">
                                  M
                                </span>

                                <div>
                                  <span className="memory-case-id">
                                    {item.case_id ||
                                      `CASE ${index + 1}`}
                                  </span>

                                  <h5>
                                    {item.case_title ||
                                      "Historical investigation"}
                                  </h5>
                                </div>

                              </div>
                            )
                          )}

                        </div>
                      )}

                      {historicalConnections.length >
                        0 && (
                        <div className="historical-connections">

                          {historicalConnections.map(
                            (item, index) => {
                              const title =
                                item.connection ||
                                item.pattern ||
                                item.similarity ||
                                item.relationship;

                              const description =
                                item.interpretation ||
                                item.relevance ||
                                item.explanation ||
                                item.details;

                              if (
                                !title &&
                                !description
                              ) {
                                return null;
                              }

                              return (
                                <div
                                  className="historical-card"
                                  key={index}
                                >
                                  {title && (
                                    <h5>{title}</h5>
                                  )}

                                  {description && (
                                    <p>
                                      {description}
                                    </p>
                                  )}
                                </div>
                              );
                            }
                          )}

                        </div>
                      )}

                    </Accordion>
                  )}

                  {/* ACTIONS */}

                  {actions.length > 0 && (
                    <Accordion
                      label="DECISION SUPPORT"
                      title="Recommended Next Actions"
                      count={actions.length}
                      defaultOpen={true}
                    >

                      <div className="action-list">

                        {actions.map(
                          (item, index) => (
                            <div
                              className="action-card"
                              key={index}
                            >

                              <div className="action-number">
                                {index + 1}
                              </div>

                              <div className="action-body">

                                <div className="action-top">
                                  <h5>
                                    {item.action}
                                  </h5>

                                  <span
                                    className={`level-pill ${getLevelClass(
                                      item.priority
                                    )}`}
                                  >
                                    {item.priority ||
                                      "ACTION"}
                                  </span>
                                </div>

                                <p>
                                  {item.reason}
                                </p>

                              </div>

                            </div>
                          )
                        )}

                      </div>

                    </Accordion>
                  )}

                  {/* CONFIDENCE */}

                  {confidence?.reason && (
                    <section className="confidence-summary">

                      <div
                        className={`confidence-circle ${getLevelClass(
                          confidence.level
                        )}`}
                      >
                        {confidence.level || "AI"}
                      </div>

                      <div>
                        <p className="section-label">
                          INVESTIGATION CONFIDENCE
                        </p>

                        <h4>
                          {confidence.level ||
                            "Analyzed"}
                        </h4>

                        <p>
                          {confidence.reason}
                        </p>
                      </div>

                    </section>
                  )}

                  {/* LEARNING */}

                  {caseFile?.organizational_memory_summary && (
                    <section className="learning-summary">

                      <p className="section-label">
                        KNOWLEDGE PRESERVED
                      </p>

                      <h4>
                        Organizational Learning
                      </h4>

                      <p>
                        {
                          caseFile
                            .organizational_memory_summary
                        }
                      </p>

                    </section>
                  )}

                </div>
              )}

            </>
          ) : (
            <div className="placeholder-page">

              <p className="section-label">
                {activePage.toUpperCase()}
              </p>

              <h3>{activePage}</h3>

              <p>
                This workspace will be connected
                in the next step.
              </p>

            </div>
          )}

        </section>

      </main>

    </div>
  );
}

export default App;