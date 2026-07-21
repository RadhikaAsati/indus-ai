import { useState } from "react";
import "./App.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/* =========================================================
   REUSABLE ACCORDION
   ========================================================= */

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

/* =========================================================
   INVESTIGATION TABS
   ========================================================= */

function InvestigationTabs({
  activeTab,
  setActiveTab,
  hasResult,
}) {
  const tabs = [
    {
      id: "ask",
      number: "01",
      label: "Ask",
      subtitle: "Start investigation",
    },
    {
      id: "findings",
      number: "02",
      label: "Findings",
      subtitle: "What INDUS found",
      locked: !hasResult,
    },
    {
      id: "evidence",
      number: "03",
      label: "Evidence Map",
      subtitle: "How records connect",
      locked: !hasResult,
    },
    {
      id: "uncertainties",
      number: "04",
      label: "Uncertainties",
      subtitle: "What remains unknown",
      locked: !hasResult,
    },
    {
      id: "deep",
      number: "05",
      label: "Deep Dive",
      subtitle: "Inspect full reasoning",
      locked: !hasResult,
    },
  ];

  return (
    <div className="investigation-nav">
      {tabs.map((tab) => {
        const active = activeTab === tab.id;

        return (
          <button
            key={tab.id}
            className={`investigation-tab ${
              active ? "active" : ""
            } ${tab.locked ? "locked" : ""}`}
            disabled={tab.locked}
            onClick={() => {
              if (!tab.locked) {
                setActiveTab(tab.id);
              }
            }}
          >
            <span className="tab-number">{tab.number}</span>

            <span className="tab-copy">
              <strong>{tab.label}</strong>
              <small>{tab.subtitle}</small>
            </span>

            {active && <span className="tab-marker" />}
          </button>
        );
      })}
    </div>
  );
}

function App() {
  const [activePage, setActivePage] = useState("Investigate");

  const [investigateTab, setInvestigateTab] =
    useState("ask");

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

  /* =========================================================
     RUN INVESTIGATION
     ========================================================= */

  const runInvestigation = async () => {
    if (!question.trim()) {
      setError("Enter an investigation question first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setInvestigateTab("ask");

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

      if (data?.reasoning_result?.success !== false) {
        setInvestigateTab("findings");
      }
    } catch (err) {
      console.error(err);

      setError(
        "Could not connect to the INDUS AI investigation engine."
      );
    } finally {
      setLoading(false);
    }
  };

  /* =========================================================
     RESULT MAPPING
     ========================================================= */

  const reasoning = result?.reasoning_result || {};
  const caseFile = reasoning?.case_file || {};

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

  const reasoningFailed =
    result && reasoning?.success === false;

  const reasoningError =
    reasoning?.details ||
    reasoning?.error ||
    "Evidence retrieval completed, but AI reasoning could not complete.";

  const topRootCause =
    rootCauses.find((item) =>
      String(item?.confidence || "")
        .toLowerCase()
        .includes("high")
    ) || rootCauses[0];

  const topImpact = impacts[0];

  const getLevelClass = (level = "") => {
    const value = String(level).toLowerCase();

    if (value.includes("high")) return "high";
    if (value.includes("medium")) return "medium";
    if (value.includes("low")) return "low";

    return "neutral";
  };

  const resetInvestigation = () => {
    setResult(null);
    setError("");
    setInvestigateTab("ask");
  };

  /* =========================================================
     OVERVIEW
     ========================================================= */

  const renderOverview = () => (
    <div className="workspace-page overview-page">
      <section className="page-intro">
        <p className="section-label">KNOWLEDGE BRAIN</p>

        <h3>
          Industrial knowledge that becomes more useful
          every time you investigate.
        </h3>

        <p>
          INDUS AI connects scattered operational records,
          investigates incidents across departments, and
          preserves validated learning as organizational memory.
        </p>

        <button
          className="primary-action"
          onClick={() => {
            setActivePage("Investigate");
            setInvestigateTab("ask");
          }}
        >
          Start an Investigation
          <span>→</span>
        </button>
      </section>

      <section className="knowledge-flow">
        <div className="flow-stage">
          <span className="flow-number">01</span>

          <div>
            <span className="flow-label">KNOWLEDGE</span>

            <h4>Connect industrial records</h4>

            <p>
              Maintenance logs, production records, quality
              reports, customer complaints and engineering data.
            </p>
          </div>
        </div>

        <div className="flow-arrow">→</div>

        <div className="flow-stage featured">
          <span className="flow-number">02</span>

          <div>
            <span className="flow-label">INTELLIGENCE</span>

            <h4>Investigate across evidence</h4>

            <p>
              Discover relationships, reconstruct incidents,
              expose contradictions and reason about likely causes.
            </p>
          </div>
        </div>

        <div className="flow-arrow">→</div>

        <div className="flow-stage">
          <span className="flow-number">03</span>

          <div>
            <span className="flow-label">MEMORY</span>

            <h4>Preserve what was learned</h4>

            <p>
              Previous investigations become historical context
              for future engineers without becoming false proof.
            </p>
          </div>
        </div>
      </section>

      <section className="overview-grid">
        <article className="overview-panel dark-panel">
          <p className="section-label light-label">
            WHY INDUS AI
          </p>

          <h4>
            Your organization already knows more than any
            single engineer can remember.
          </h4>

          <p>
            The problem is that knowledge is scattered across
            documents, departments and years. INDUS AI turns
            those disconnected records into an investigation-ready
            knowledge system.
          </p>
        </article>

        <article className="overview-panel">
          <span className="panel-symbol">⌕</span>

          <h4>Evidence-first reasoning</h4>

          <p>
            Findings remain connected to source records,
            uncertainty stays visible, and missing evidence
            is explicitly identified.
          </p>
        </article>

        <article className="overview-panel">
          <span className="panel-symbol">∞</span>

          <h4>Institutional continuity</h4>

          <p>
            Lessons do not disappear when experienced engineers
            retire, teams change or incidents fade from memory.
          </p>
        </article>
      </section>
    </div>
  );

  /* =========================================================
     DOCUMENTS
     ========================================================= */

  const renderDocuments = () => (
    <div className="workspace-page documents-page">
      <section className="page-intro compact-intro">
        <p className="section-label">
          CONNECTED KNOWLEDGE
        </p>

        <h3>
          Build the knowledge INDUS can investigate.
        </h3>

        <p>
          Add operational records to the Knowledge Brain.
          Indexed documents become searchable evidence for
          future investigations.
        </p>
      </section>

      <section className="upload-workspace">
        <div className="upload-icon">+</div>

        <p className="section-label">ADD KNOWLEDGE</p>

        <h4>Drop industrial records here</h4>

        <p>
          PDF, TXT, CSV and XLSX documents can be extracted,
          indexed and connected to the Knowledge Brain.
        </p>

        <button
          className="primary-action"
          type="button"
        >
          Choose Files
          <span>+</span>
        </button>

        <span className="upload-note">
          Upload connection will use the existing indexing
          pipeline.
        </span>
      </section>

      <section className="document-library">
        <div className="section-heading-row">
          <div>
            <p className="section-label">
              KNOWLEDGE LIBRARY
            </p>

            <h4>Indexed evidence sources</h4>
          </div>

          <span className="library-status">
            <span className="status-dot"></span>
            Knowledge Brain Ready
          </span>
        </div>

        <div className="document-placeholder">
          <div className="document-placeholder-icon">
            ▤
          </div>

          <div>
            <h5>
              Document library connection comes next
            </h5>

            <p>
              Your existing indexed records remain safely stored
              in ChromaDB. We will connect this workspace to the
              backend document list and upload route next.
            </p>
          </div>
        </div>
      </section>
    </div>
  );

  /* =========================================================
     MEMORY
     ========================================================= */

  const renderMemory = () => (
    <div className="workspace-page memory-page">
      <section className="page-intro compact-intro">
        <p className="section-label">
          ORGANIZATIONAL MEMORY
        </p>

        <h3>
          Experience should survive beyond the people
          who originally learned it.
        </h3>

        <p>
          INDUS AI preserves previous investigations as
          historical knowledge that can guide future reasoning.
        </p>
      </section>

      <section className="memory-principle">
        <div className="memory-principle-mark">M</div>

        <div>
          <p className="section-label">
            AN IMPORTANT DISTINCTION
          </p>

          <h4>
            Historical context is guidance — never current proof.
          </h4>

          <p>
            Similar past incidents can reveal recurring patterns
            and useful verification steps. INDUS AI keeps that
            knowledge separate from evidence belonging to the
            current investigation.
          </p>
        </div>
      </section>

      {historicalCases.length > 0 ? (
        <section className="memory-library">
          <div className="section-heading-row">
            <div>
              <p className="section-label">
                RELATED CASES
              </p>

              <h4>Knowledge already preserved</h4>
            </div>
          </div>

          {historicalCases.map((item, index) => (
            <article
              className="memory-record"
              key={index}
            >
              <div className="memory-record-number">
                {String(index + 1).padStart(2, "0")}
              </div>

              <div>
                <span className="memory-case-id">
                  {item.case_id || "HISTORICAL CASE"}
                </span>

                <h5>
                  {item.case_title ||
                    "Historical industrial investigation"}
                </h5>

                <span className="historical-context-tag">
                  HISTORICAL CONTEXT
                </span>
              </div>
            </article>
          ))}
        </section>
      ) : (
        <section className="empty-memory">
          <span>◉</span>

          <h4>Organizational memory is ready.</h4>

          <p>
            Related historical cases discovered during an
            investigation will appear here.
          </p>

          <button
            className="secondary-action"
            onClick={() => {
              setActivePage("Investigate");
              setInvestigateTab("ask");
            }}
          >
            Go to Investigate
          </button>
        </section>
      )}
    </div>
  );

  /* =========================================================
     ASK TAB
     ========================================================= */

  const renderAskTab = () => (
    <div className="investigate-tab-page tab-enter">
      {!result && (
        <section className="investigation-hero">
          <div className="hero-copy">
            <div className="hero-kicker">
              <span className="hero-line"></span>
              INDUSTRIAL KNOWLEDGE INTELLIGENCE
            </div>

            <h3>
              Ask what happened.
              <br />
              <span>Trace why.</span>
            </h3>

            <p>
              INDUS AI investigates across scattered industrial
              records, connects evidence through time and tells
              you what is known, what is likely and what still
              needs proof.
            </p>
          </div>

          <div className="hero-intelligence-mark">
            <div className="brain-ring ring-one"></div>
            <div className="brain-ring ring-two"></div>

            <div className="brain-core">
              <span>I</span>
            </div>

            <span className="orbit-label label-one">
              EVIDENCE
            </span>

            <span className="orbit-label label-two">
              MEMORY
            </span>

            <span className="orbit-label label-three">
              REASONING
            </span>
          </div>
        </section>
      )}

      <section
        className={
          result
            ? "question-workspace compact"
            : "question-workspace"
        }
      >
        <div className="question-heading">
          <div>
            <p className="section-label">
              INVESTIGATION WORKSPACE
            </p>

            <h4>
              What do you need to understand?
            </h4>
          </div>

          <div className="brain-status">
            <span className="status-dot"></span>
            Knowledge Brain Connected
          </div>
        </div>

        <textarea
          value={question}
          onChange={(e) =>
            setQuestion(e.target.value)
          }
          placeholder="Ask an industrial question across maintenance, production, quality, customer and historical records..."
        />

        <div className="question-footer">
          <span>
            Evidence retrieval · Cross-record reasoning ·
            Organizational memory
          </span>

          <div className="investigation-actions">
            {result && (
              <button
                className="secondary-action"
                onClick={resetInvestigation}
              >
                New Investigation
              </button>
            )}

            <button
              className="primary-action"
              onClick={runInvestigation}
              disabled={loading}
            >
              {loading ? (
                "Investigating..."
              ) : (
                <>
                  Run Investigation
                  <span>→</span>
                </>
              )}
            </button>
          </div>
        </div>
      </section>

      {error && (
        <div className="error-message">
          <strong>Connection problem</strong>
          <span>{error}</span>
        </div>
      )}

      {loading && (
        <section className="analysis-status">
          <div className="analysis-orbit">
            <span></span>
          </div>

          <div>
            <p className="section-label">
              INVESTIGATION IN PROGRESS
            </p>

            <h4>Connecting the evidence...</h4>

            <p>
              INDUS is discovering relevant records, expanding
              across connected documents, checking historical
              memory and building an evidence-grounded case.
            </p>
          </div>
        </section>
      )}

      {!result && !loading && (
        <section className="capability-strip">
          <article>
            <span>01</span>

            <h5>Connect</h5>

            <p>
              Find relationships hidden across departments
              and document systems.
            </p>
          </article>

          <article>
            <span>02</span>

            <h5>Reason</h5>

            <p>
              Separate confirmed facts, hypotheses,
              contradictions and missing proof.
            </p>
          </article>

          <article>
            <span>03</span>

            <h5>Remember</h5>

            <p>
              Use past investigations as context without
              confusing history with current evidence.
            </p>
          </article>
        </section>
      )}
    </div>
  );

  /* =========================================================
     FINDINGS TAB
     ========================================================= */

  const renderFindingsTab = () => (
    <div className="investigate-tab-page tab-enter">
      <section className="case-header">
        <div className="case-header-main">
          <div className="case-overline">
            <span>INVESTIGATION COMPLETE</span>

            <span className="case-divider"></span>

            <span>CURRENT EVIDENCE</span>
          </div>

          <h3>
            {caseFile?.case_title ||
              "Industrial Investigation"}
          </h3>

          <p className="case-question">
            {question}
          </p>
        </div>

        <div
          className={`confidence-seal ${getLevelClass(
            confidence?.level
          )}`}
        >
          <span className="confidence-level">
            {confidence?.level || "ANALYZED"}
          </span>

          <span>CONFIDENCE</span>
        </div>
      </section>

      <section className="intelligence-strip">
        <div>
          <strong>
            {investigationSummary?.documents_consulted ??
              investigationSummary?.documents_discovered ??
              "—"}
          </strong>

          <span>Sources</span>
        </div>

        <div>
          <strong>
            {investigationSummary?.evidence_found ??
              investigationSummary?.semantic_matches_found ??
              confirmedFacts.length}
          </strong>

          <span>Evidence</span>
        </div>

        <div>
          <strong>
            {historicalMemoriesFound}
          </strong>

          <span>Related Memory</span>
        </div>

        <div
          className={
            contradictions.length > 0
              ? "needs-attention"
              : ""
          }
        >
          <strong>
            {contradictions.length}
          </strong>

          <span>Unresolved</span>
        </div>
      </section>

      <section className="finding-section">
        <div className="section-intro">
          <p className="section-label">
            INVESTIGATION VERDICT
          </p>

          <h3>
            What INDUS found.
          </h3>

          <p>
            The strongest explanation supported by the
            currently connected evidence.
          </p>
        </div>

        <div className="finding-layout">
          <div className="causal-path">
            <div className="cause-node start-node">
              <span className="node-type">
                STRONGEST EXPLANATION
              </span>

              <h4>
                {topRootCause?.hypothesis ||
                  "Further verification required"}
              </h4>

              {topRootCause?.confidence && (
                <span
                  className={`evidence-state ${getLevelClass(
                    topRootCause.confidence
                  )}`}
                >
                  {topRootCause.confidence} CONFIDENCE
                </span>
              )}
            </div>

            <div className="cause-line">
              <span>↓</span>
            </div>

            <div className="cause-node evidence-node">
              <span className="node-type">
                EVIDENCE SUPPORT
              </span>

              <p>
                {topRootCause?.supporting_evidence ||
                  caseFile?.executive_assessment ||
                  "Connected evidence supports this explanation."}
              </p>
            </div>

            {topImpact && (
              <>
                <div className="cause-line">
                  <span>↓</span>
                </div>

                <div className="cause-node impact-node">
                  <span className="node-type">
                    OPERATIONAL CONSEQUENCE
                  </span>

                  <h4>
                    {topImpact?.impact ||
                      "Operational impact identified."}
                  </h4>
                </div>
              </>
            )}
          </div>

          <aside className="executive-finding">
            <p className="section-label">
              EXECUTIVE ASSESSMENT
            </p>

            <p>
              {caseFile?.executive_assessment ||
                "The investigation connected evidence across the available industrial records."}
            </p>

            {confidence?.reason && (
              <div className="confidence-explanation">
                <span>
                  WHY THIS CONFIDENCE
                </span>

                <p>{confidence.reason}</p>
              </div>
            )}
          </aside>
        </div>
      </section>

      {timeline.length > 0 && (
        <section className="finding-section">
          <div className="section-intro">
            <p className="section-label">
              CAUSE → EFFECT
            </p>

            <h3>
              The incident in one glance.
            </h3>

            <p>
              A simplified view of the key sequence reconstructed
              from the evidence.
            </p>
          </div>

          <div className="evidence-journey">
            {timeline
              .slice(0, 4)
              .map((item, index) => (
                <article
                  className="journey-event"
                  key={index}
                >
                  <div className="journey-top">
                    <span className="journey-date">
                      {item.date ||
                        "DATE UNKNOWN"}
                    </span>

                    <span className="journey-index">
                      {String(index + 1).padStart(
                        2,
                        "0"
                      )}
                    </span>
                  </div>

                  <div className="journey-node-row">
                    <span className="journey-node"></span>

                    {index !==
                      Math.min(
                        timeline.length,
                        4
                      ) -
                        1 && (
                      <span className="journey-line"></span>
                    )}
                  </div>

                  <h4>
                    {item.event ||
                      "Evidence event"}
                  </h4>

                  {item.significance && (
                    <p>{item.significance}</p>
                  )}
                </article>
              ))}
          </div>
        </section>
      )}

      <button
        className="next-investigation-view"
        onClick={() =>
          setInvestigateTab("evidence")
        }
      >
        <span>
          <small>NEXT</small>
          See how the records connected
        </span>

        <strong>→</strong>
      </button>
    </div>
  );

  /* =========================================================
     EVIDENCE MAP TAB
     ========================================================= */

  const renderEvidenceTab = () => (
    <div className="investigate-tab-page tab-enter">
      <section className="section-intro">
        <p className="section-label">
          CONNECTED EVIDENCE
        </p>

        <h3>
          One incident.
          <br />
          Multiple records.
        </h3>

        <p>
          INDUS reconstructs the story by connecting events
          that may originally have lived in separate operational
          records.
        </p>
      </section>

      {timeline.length > 0 ? (
        <section className="evidence-map">
          <div className="evidence-spine"></div>

          {timeline.map((item, index) => (
            <article
              className={`evidence-event ${
                index % 2 !== 0
                  ? "reverse"
                  : ""
              }`}
              key={index}
            >
              <div
                className={`evidence-point ${
                  index ===
                  Math.floor(
                    timeline.length / 2
                  )
                    ? "critical"
                    : ""
                }`}
              >
                <span>
                  {String(index + 1).padStart(
                    2,
                    "0"
                  )}
                </span>
              </div>

              <div
                className={`evidence-card ${
                  index ===
                  Math.floor(
                    timeline.length / 2
                  )
                    ? "critical-card"
                    : ""
                }`}
              >
                <span className="source-type">
                  EVIDENCE EVENT
                </span>

                <time>
                  {item.date ||
                    "DATE UNKNOWN"}

                  {item.time &&
                    item.time !== "Unknown" &&
                    ` · ${item.time}`}
                </time>

                <h3>
                  {item.event ||
                    "Connected evidence event"}
                </h3>

                {item.significance && (
                  <p>{item.significance}</p>
                )}
              </div>
            </article>
          ))}
        </section>
      ) : (
        <section className="empty-memory">
          <span>⌕</span>

          <h4>
            No structured timeline was returned.
          </h4>

          <p>
            Cross-document evidence is still available in the
            Deep Dive.
          </p>
        </section>
      )}

      {connections.length > 0 && (
        <section className="deep-investigation">
          <Accordion
            label="WHY THESE RECORDS CONNECT"
            title="Cross-Document Connections"
            count={connections.length}
            defaultOpen={true}
          >
            <div className="connection-list">
              {connections.map(
                (item, index) => (
                  <article
                    className="connection-card"
                    key={index}
                  >
                    <div className="connection-number">
                      {String(
                        index + 1
                      ).padStart(2, "0")}
                    </div>

                    <div>
                      <div className="connection-meta">
                        <span>
                          EVIDENCE CONNECTION
                        </span>

                        {item.classification && (
                          <span className="classification-tag">
                            {
                              item.classification
                            }
                          </span>
                        )}
                      </div>

                      <h5>
                        {item.connection}
                      </h5>

                      {item.interpretation && (
                        <p>
                          {
                            item.interpretation
                          }
                        </p>
                      )}
                    </div>
                  </article>
                )
              )}
            </div>
          </Accordion>
        </section>
      )}

      <section className="evidence-insight">
        <span>
          WHY CONNECTIONS MATTER
        </span>

        <p>
          A single document may contain only one part of an
          incident. INDUS looks across records and time to reveal
          the larger operational story while keeping the original
          evidence separate.
        </p>
      </section>

      <button
        className="next-investigation-view"
        onClick={() =>
          setInvestigateTab("uncertainties")
        }
      >
        <span>
          <small>NEXT</small>
          See what INDUS refuses to assume
        </span>

        <strong>→</strong>
      </button>
    </div>
  );

  /* =========================================================
     UNCERTAINTIES TAB
     ========================================================= */

  const renderUncertaintiesTab = () => (
    <div className="investigate-tab-page tab-enter">
      <section className="section-intro">
        <p className="section-label">
          EVIDENCE BOUNDARY
        </p>

        <h3>
          What INDUS will not assume.
        </h3>

        <p>
          Strong investigation means separating what the
          evidence supports from what still requires proof.
        </p>
      </section>

      <section className="unresolved-section">
        <div className="unresolved-heading">
          <div>
            <p className="section-label">
              OPEN QUESTIONS
            </p>

            <h3>
              What remains unresolved?
            </h3>

            <p>
              These gaps prevent INDUS from claiming more
              certainty than the evidence supports.
            </p>
          </div>

          <div className="unresolved-total">
            <strong>
              {contradictions.length}
            </strong>

            <span>
              OPEN QUESTIONS
            </span>
          </div>
        </div>

        {contradictions.length > 0 ? (
          <div className="unresolved-list">
            {contradictions.map(
              (item, index) => (
                <article
                  className="unresolved-item"
                  key={index}
                >
                  <div className="unresolved-number">
                    {String(
                      index + 1
                    ).padStart(2, "0")}
                  </div>

                  <div className="unresolved-body">
                    <span className="conflict-state">
                      UNRESOLVED EVIDENCE
                    </span>

                    <h4>
                      {item.issue ||
                        "Evidence gap detected"}
                    </h4>

                    {item.why_it_matters && (
                      <p>
                        {
                          item.why_it_matters
                        }
                      </p>
                    )}

                    {item.needed_evidence && (
                      <div className="verify-next">
                        <span>
                          WHAT WOULD RESOLVE IT
                        </span>

                        <p>
                          {
                            item.needed_evidence
                          }
                        </p>
                      </div>
                    )}
                  </div>
                </article>
              )
            )}
          </div>
        ) : (
          <div className="memory-notice">
            <strong>
              No major contradiction was explicitly returned.
            </strong>

            <p>
              This does not mean every causal detail is proven.
              Review confidence limits and verification needs
              before treating hypotheses as confirmed causes.
            </p>
          </div>
        )}
      </section>

      {rootCauses.length > 0 && (
        <section className="deep-investigation">
          <div className="section-intro">
            <p className="section-label">
              HYPOTHESES VS PROOF
            </p>

            <h3>
              What is likely is not always what is proven.
            </h3>
          </div>

          <div className="hypothesis-grid">
            {rootCauses.map(
              (item, index) => (
                <article
                  className="hypothesis-card"
                  key={index}
                >
                  <div className="hypothesis-top">
                    <span className="hypothesis-number">
                      H
                      {String(
                        index + 1
                      ).padStart(2, "0")}
                    </span>

                    <span
                      className={`evidence-state ${getLevelClass(
                        item.confidence
                      )}`}
                    >
                      {item.confidence ||
                        "UNRATED"}
                    </span>
                  </div>

                  <h5>
                    {item.hypothesis}
                  </h5>

                  {item.contradicting_or_limiting_evidence && (
                    <div className="analysis-block limitation">
                      <span>
                        LIMITS / UNCERTAINTY
                      </span>

                      <p>
                        {
                          item.contradicting_or_limiting_evidence
                        }
                      </p>
                    </div>
                  )}

                  {item.verification_needed && (
                    <div className="analysis-block verify">
                      <span>
                        WHAT WOULD VERIFY IT
                      </span>

                      <p>
                        {
                          item.verification_needed
                        }
                      </p>
                    </div>
                  )}
                </article>
              )
            )}
          </div>
        </section>
      )}

      <button
        className="next-investigation-view"
        onClick={() =>
          setInvestigateTab("deep")
        }
      >
        <span>
          <small>NEXT</small>
          Inspect the complete investigation
        </span>

        <strong>→</strong>
      </button>
    </div>
  );

  /* =========================================================
     DEEP DIVE TAB
     ========================================================= */

  const renderDeepDiveTab = () => (
    <div className="investigate-tab-page tab-enter">
      <section className="section-intro">
        <p className="section-label">
          FULL INVESTIGATION
        </p>

        <h3>
          Inspect the reasoning.
        </h3>

        <p>
          Nothing has been removed. Explore the complete
          hypotheses, facts, timeline, connections, historical
          context and recommended actions.
        </p>
      </section>

      <section className="deep-investigation">

        {/* ROOT CAUSES */}

        {rootCauses.length > 0 && (
          <Accordion
            label="CAUSAL ANALYSIS"
            title="Root Cause Hypotheses"
            count={rootCauses.length}
            defaultOpen={true}
          >
            <div className="hypothesis-grid">
              {rootCauses.map(
                (item, index) => (
                  <article
                    className="hypothesis-card"
                    key={index}
                  >
                    <div className="hypothesis-top">
                      <span className="hypothesis-number">
                        H
                        {String(
                          index + 1
                        ).padStart(2, "0")}
                      </span>

                      <span
                        className={`evidence-state ${getLevelClass(
                          item.confidence
                        )}`}
                      >
                        {item.confidence ||
                          "UNRATED"}
                      </span>
                    </div>

                    <h5>
                      {item.hypothesis}
                    </h5>

                    {item.supporting_evidence && (
                      <div className="analysis-block confirmed">
                        <span>
                          SUPPORTING EVIDENCE
                        </span>

                        <p>
                          {
                            item.supporting_evidence
                          }
                        </p>
                      </div>
                    )}

                    {item.contradicting_or_limiting_evidence && (
                      <div className="analysis-block limitation">
                        <span>
                          LIMITS / UNCERTAINTY
                        </span>

                        <p>
                          {
                            item.contradicting_or_limiting_evidence
                          }
                        </p>
                      </div>
                    )}

                    {item.verification_needed && (
                      <div className="analysis-block verify">
                        <span>
                          VERIFY NEXT
                        </span>

                        <p>
                          {
                            item.verification_needed
                          }
                        </p>
                      </div>
                    )}
                  </article>
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
                  <article
                    className="connection-card"
                    key={index}
                  >
                    <div className="connection-number">
                      {String(
                        index + 1
                      ).padStart(2, "0")}
                    </div>

                    <div>
                      <div className="connection-meta">
                        <span>
                          EVIDENCE CONNECTION
                        </span>

                        {item.classification && (
                          <span className="classification-tag">
                            {
                              item.classification
                            }
                          </span>
                        )}
                      </div>

                      <h5>
                        {item.connection}
                      </h5>

                      {item.interpretation && (
                        <p>
                          {
                            item.interpretation
                          }
                        </p>
                      )}
                    </div>
                  </article>
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
                  <article
                    className="timeline-item"
                    key={index}
                  >
                    <div className="timeline-marker">
                      <span className="timeline-dot"></span>

                      {index !==
                        timeline.length - 1 && (
                        <span className="timeline-line"></span>
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
                          {
                            item.significance
                          }
                        </p>
                      )}
                    </div>
                  </article>
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
                  <article
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
                  </article>
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
            <div className="impact-list">
              {impacts.map(
                (item, index) => (
                  <article
                    className="impact-record"
                    key={index}
                  >
                    <span>
                      {String(
                        index + 1
                      ).padStart(2, "0")}
                    </span>

                    <p>
                      {item.impact}
                    </p>
                  </article>
                )
              )}
            </div>
          </Accordion>
        )}

        {/* WARNINGS */}

        {warnings.length > 0 && (
          <Accordion
            label="EARLY INDICATORS"
            title="Historical Warning Signals"
            count={warnings.length}
          >
            <div className="warning-list">
              {warnings.map(
                (item, index) => (
                  <article
                    className="warning-record"
                    key={index}
                  >
                    <span className="warning-index">
                      W
                      {String(
                        index + 1
                      ).padStart(2, "0")}
                    </span>

                    <div>
                      <h5>
                        {item.signal}
                      </h5>

                      <p>
                        {
                          item.why_it_matters
                        }
                      </p>
                    </div>
                  </article>
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
              <strong>
                Historical context — not current proof.
              </strong>

              <p>
                Previous cases may reveal recurring patterns
                and useful verification paths, but INDUS AI
                does not treat them as evidence for the
                current incident.
              </p>
            </div>

            {historicalCases.length > 0 && (
              <div className="memory-case-list">
                {historicalCases.map(
                  (item, index) => (
                    <article
                      className="memory-case"
                      key={index}
                    >
                      <span className="memory-icon">
                        M
                      </span>

                      <div>
                        <span className="memory-case-id">
                          {item.case_id ||
                            `CASE ${
                              index + 1
                            }`}
                        </span>

                        <h5>
                          {item.case_title ||
                            "Historical investigation"}
                        </h5>

                        <span className="historical-context-tag">
                          HISTORICAL CONTEXT
                        </span>
                      </div>
                    </article>
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
                      <article
                        className="historical-card"
                        key={index}
                      >
                        {title && (
                          <h5>
                            {title}
                          </h5>
                        )}

                        {description && (
                          <p>
                            {
                              description
                            }
                          </p>
                        )}
                      </article>
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
                  <article
                    className="action-card"
                    key={index}
                  >
                    <div className="action-number">
                      {String(
                        index + 1
                      ).padStart(2, "0")}
                    </div>

                    <div className="action-body">
                      <div className="action-top">
                        <h5>
                          {item.action}
                        </h5>

                        <span
                          className={`evidence-state ${getLevelClass(
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
                  </article>
                )
              )}
            </div>
          </Accordion>
        )}
      </section>

      {/* KNOWLEDGE PRESERVED */}

      {caseFile?.organizational_memory_summary && (
        <section className="knowledge-preserved">
          <div className="knowledge-symbol">
            ∞
          </div>

          <div>
            <p className="section-label">
              KNOWLEDGE PRESERVED
            </p>

            <h3>
              What the organization should remember.
            </h3>

            <p>
              {
                caseFile.organizational_memory_summary
              }
            </p>
          </div>
        </section>
      )}
    </div>
  );

  /* =========================================================
     INVESTIGATE PAGE
     ========================================================= */

  const renderInvestigate = () => (
    <>
      <InvestigationTabs
        activeTab={investigateTab}
        setActiveTab={setInvestigateTab}
        hasResult={
          !!result && !reasoningFailed
        }
      />

      {reasoningFailed ? (
        <section className="reasoning-failure">
          <div className="failure-mark">
            !
          </div>

          <div className="failure-content">
            <p className="section-label">
              EVIDENCE RETRIEVED · REASONING INTERRUPTED
            </p>

            <h3>
              The evidence is safe.
              <br />
              Reasoning needs another attempt.
            </h3>

            <p>
              INDUS AI successfully searched the connected
              knowledge base, but the reasoning engine could
              not complete this investigation.
            </p>

            <div className="failure-stats">
              <div>
                <strong>
                  {investigationSummary?.documents_consulted ??
                    investigationSummary?.documents_discovered ??
                    "—"}
                </strong>

                <span>
                  Documents retrieved
                </span>
              </div>

              <div>
                <strong>
                  {investigationSummary?.evidence_found ??
                    investigationSummary?.semantic_matches_found ??
                    "—"}
                </strong>

                <span>
                  Evidence items found
                </span>
              </div>
            </div>

            <button
              className="primary-action"
              onClick={runInvestigation}
              disabled={loading}
            >
              Retry Investigation
              <span>→</span>
            </button>

            <details className="technical-error">
              <summary>
                Technical details
              </summary>

              <p>{reasoningError}</p>
            </details>
          </div>
        </section>
      ) : (
        <>
          {investigateTab === "ask" &&
            renderAskTab()}

          {investigateTab === "findings" &&
            result &&
            renderFindingsTab()}

          {investigateTab === "evidence" &&
            result &&
            renderEvidenceTab()}

          {investigateTab ===
            "uncertainties" &&
            result &&
            renderUncertaintiesTab()}

          {investigateTab === "deep" &&
            result &&
            renderDeepDiveTab()}
        </>
      )}
    </>
  );

  /* =========================================================
     APP
     ========================================================= */

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            I
          </div>

          <div>
            <h1>INDUS AI</h1>

            <p>
              Industrial Intelligence
            </p>
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
              <strong>
                Knowledge Brain
              </strong>

              <p>
                System operational
              </p>
            </div>
          </div>
        </div>
      </aside>

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
            Knowledge Brain Active
          </div>
        </header>

        <section className="content">
          {activePage === "Overview" &&
            renderOverview()}

          {activePage === "Investigate" &&
            renderInvestigate()}

          {activePage === "Documents" &&
            renderDocuments()}

          {activePage === "Memory" &&
            renderMemory()}
        </section>
      </main>
    </div>
  );
}

export default App;