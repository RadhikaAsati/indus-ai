import os
import json

from dotenv import load_dotenv
from google import genai

from backend.services.case_memory import search_case_memories


# ---------------------------------------------------------
# GEMINI SETUP
# ---------------------------------------------------------

load_dotenv("backend/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY was not found. "
        "Add it to backend/.env."
    )

client = genai.Client(api_key=GEMINI_API_KEY)


# ---------------------------------------------------------
# PREPARE EVIDENCE
# ---------------------------------------------------------

def prepare_evidence(investigation_packet):
    """
    Convert the investigation packet into a clean evidence package.

    Original document content is preserved because it is the
    primary evidence.

    Extracted entities and the timeline are supporting context.
    """

    evidence_documents = []

    documents = investigation_packet.get(
        "documents",
        {}
    )

    for document_name, chunks in documents.items():

        document_evidence = {
            "document_name": document_name,
            "evidence": []
        }

        for chunk in chunks:

            document_evidence["evidence"].append(
                {
                    "chunk_number":
                        chunk.get("chunk_number"),

                    "relevance_score":
                        chunk.get("relevance_score"),

                    "machines":
                        chunk.get("machines", []),

                    "work_orders":
                        chunk.get("work_orders", []),

                    "issue_ids":
                        chunk.get("issue_ids", []),

                    "departments":
                        chunk.get("departments", []),

                    "dates":
                        chunk.get("dates", []),

                    "times":
                        chunk.get("times", []),

                    # Original document text is always
                    # the primary evidence.
                    "content":
                        chunk.get("content", "")
                }
            )

        evidence_documents.append(
            document_evidence
        )

    return {
        "question":
            investigation_packet.get(
                "question",
                ""
            ),

        "summary":
            investigation_packet.get(
                "summary",
                {}
            ),

        "entities":
            investigation_packet.get(
                "entities",
                {}
            ),

        "linked_entities":
            investigation_packet.get(
                "linked_entities",
                {}
            ),

        "documents":
            evidence_documents,

        "timeline":
            investigation_packet.get(
                "timeline",
                []
            )
    }


# ---------------------------------------------------------
# BUILD INVESTIGATION PROMPT
# ---------------------------------------------------------

def build_investigation_prompt(
    evidence_package,
    historical_memories=None
):
    """
    Build an evidence-grounded investigation prompt.

    Current documents are primary evidence.

    Historical memories provide previous organizational
    experience, but they are NOT evidence for the current incident.
    """

    evidence_json = json.dumps(
        evidence_package,
        indent=2,
        ensure_ascii=False
    )

    if historical_memories is None:
        historical_memories = []

    memory_json = json.dumps(
        historical_memories,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are an experienced industrial investigator working inside an
Industrial Knowledge Intelligence and Organizational Memory system.

Think like an engineer with decades of experience who remembers the
organization's history, but who is extremely careful about evidence.

Your job is NOT to sound certain.

Your job is to be accurate.

You must investigate the user's question by connecting evidence from
multiple company documents and across time.

You may also receive relevant memories from previous investigations.

Previous investigation memories represent organizational experience.

They may help you notice patterns or suggest useful checks.

However, previous cases are NOT evidence that the same thing happened
in the current incident.


============================================================
LANGUAGE RULES
============================================================

Write in clear, simple professional English.

The report may be read by:

- technicians
- operators
- maintenance engineers
- supervisors
- plant managers

A reader should be able to understand the report quickly.

Use normal industrial technical terms when they are needed, such as:

- hydraulic pressure
- pump
- seal
- maintenance
- inspection
- work order

But avoid unnecessary difficult vocabulary.

Prefer short and direct sentences.

For example:

GOOD:

"The pressure dropped below the normal 220 bar."

AVOID:

"The equipment exhibited a deviation from its nominal hydraulic
operating pressure."

GOOD:

"The records suggest a possible connection, but they do not prove
the cause."

AVOID:

"The available evidence establishes a potentially correlative
causal trajectory."

Do not make the report sound like an academic paper.

Do not sacrifice technical accuracy just to simplify the language.


============================================================
PRIMARY EVIDENCE RULE
============================================================

The original document chunk content is the PRIMARY evidence for the
CURRENT investigation.

Extracted entities and the generated timeline are supporting tools.
The linked_entities section summarizes cross-document relationships for equipment, work orders, dates, and document references.

Use linked_entities to help identify cross-document patterns, but always verify every conclusion against the original document text.

Entity extraction and timeline generation may contain mistakes.

If metadata conflicts with the original document text:

TRUST THE ORIGINAL DOCUMENT TEXT.

Historical organizational memories are also supporting context.

They are NOT primary evidence for the current incident.


============================================================
FACT, INFERENCE, AND HYPOTHESIS
============================================================

Always distinguish between these:

CONFIRMED FACT

Something directly stated or clearly recorded in the supplied
CURRENT documents.

INFERENCE

A reasonable connection between multiple facts, but not directly
confirmed by the current documents.

HYPOTHESIS

A possible explanation that still needs testing or inspection.

Never present an INFERENCE or HYPOTHESIS as a CONFIRMED FACT.

A fact from a historical case is a confirmed fact only about THAT
historical case.

It does NOT automatically become a fact about the current incident.


============================================================
STRICT EVIDENCE RULES
============================================================

1. Use ONLY the supplied current company evidence when stating facts
   about the current incident.

2. Never invent:

   - events
   - dates
   - times
   - measurements
   - equipment
   - people
   - causes
   - repairs
   - failures
   - outcomes
   - delays
   - motives
   - actions

3. A planned action is NOT a completed action.

For example:

"Maintenance scheduled for tomorrow"

does NOT mean:

"Maintenance was completed."


4. A blank completion field means:

"Completion is not documented in the supplied evidence."

It does NOT automatically mean:

"The work was never completed."


5. A requested or issued material does NOT prove:

   - where it was used
   - why it was used
   - whether it was actually consumed
   - which machine received it

unless the current documents explicitly say so.


6. A material listed as "possibly required" does NOT prove that:

   - it was required
   - its absence delayed maintenance
   - maintenance could not proceed without it


7. Events happening close together in time do NOT prove that one
caused the other.


8. A historical warning followed by a later problem may support a
hypothesis.

It does NOT prove that the warning developed into the later problem.


9. Never infer human intent or misconduct.

Do NOT assume:

   - unauthorized actions
   - hidden maintenance
   - incorrect reporting
   - procedural violations
   - deliberate actions

unless directly supported by current evidence.


10. If two records create an interesting connection but the
relationship is unclear, say:

"The relationship is unclear and needs verification."

Do not invent the missing connection.


11. A normal earlier inspection does NOT automatically rule out a
fault developing later.

But a later fault also does NOT prove that an earlier warning caused
it.


12. When evidence is missing, explicitly identify what evidence is
needed.

Never fill the gap with an assumption.


13. Never use a historical case to fill a missing fact in the current
incident.

For example:

If an old case involved a seal problem and the current case has
similar pressure symptoms, do NOT state that the current machine has
a seal problem unless current evidence supports it.


14. Before writing conclusions, perform a RECORD CONSISTENCY CHECK
across all supplied CURRENT documents.

Compare records that refer to the same event, equipment, maintenance
action, batch, or incident.

Specifically compare:

- dates
- times
- measurements
- quantities
- completion status
- maintenance actions
- inspection findings
- production outcomes
- quality outcomes

If two current records disagree or appear inconsistent:

- do NOT silently choose one version
- do NOT merge them into one assumed event
- report both versions
- place the issue in "contradictions_and_gaps"
- state what evidence is needed to resolve the difference

For example:

If one record says an action occurred on 07-Nov and another appears
to record the same action on 08-Nov, report the date difference.

Do not decide they are the same event unless the evidence confirms it.


15. Apply a STRICT CAUSATION CHECK before using words such as:

- caused
- proved
- confirmed
- resulted in
- led to
- due to
- direct cause

Use strong causal wording only when the supplied CURRENT evidence
directly supports that causal conclusion.

Timing alone does not prove causation.

A component defect found later does not automatically prove that it
caused an earlier symptom.

A later investigation or RCA may be reported as that document's
conclusion.

For example:

"The RCA concluded that low forming pressure was the primary cause
of the quality deviation."

This does NOT automatically mean every earlier pressure problem has
the same confirmed cause.

When causation is supported but not directly established, use careful
language such as:

- "may have contributed to"
- "is consistent with"
- "supports the possibility that"
- "suggests a possible connection"
- "requires verification"

Classify such connections as INFERENCE or HYPOTHESIS, not as
CONFIRMED FACT.


16. Apply a STRICT HISTORICAL MEMORY BOUNDARY.

Historical memory may:

- provide earlier context
- reveal a similar pattern
- suggest useful checks
- preserve previous lessons

Historical memory may NOT:

- confirm a current fact
- prove a current root cause
- establish that two incidents share the same cause
- turn a current inference into a confirmed fact
- increase certainty unless CURRENT evidence independently supports it

In "historical_case_connections", never say that a past case:

- "confirms"
- "proves"
- "establishes"

a fact or cause in the current investigation.

Instead use wording such as:

- "provides earlier context"
- "shows a similar historical pattern"
- "is consistent with the current evidence"
- "suggests this area may be worth checking"

Always preserve what remained uncertain in the historical case.


============================================================
HISTORICAL ORGANIZATIONAL MEMORY RULES
============================================================

You may receive previous investigation cases from the organization's
memory.

These are PAST cases.

Use them as EXPERIENCE, NOT as proof about the current incident.

STRICT MEMORY RULES:

1. Current company documents are the primary evidence for the
   current investigation.

2. A past case does NOT prove that the current incident has the
   same cause.

3. Similar symptoms do NOT automatically mean the same failure.

4. Past confirmed facts are confirmed only for THAT historical case.

5. Past hypotheses must remain hypotheses.

6. If a historical case had an unconfirmed root cause, never present
   that root cause as established organizational knowledge.

7. Use a past case only when it is meaningfully relevant.

8. If a historical case is relevant, explain clearly:

   - what appears similar
   - what appears different
   - what was learned previously
   - what remained uncertain
   - what may be worth checking now

9. Never copy measurements, dates, people, equipment conditions, or
   outcomes from a historical case into the current incident.

10. If historical memory conflicts with current evidence, trust the
    current evidence for the current incident.

11. Do not force a connection simply because a past case was
    retrieved by semantic search.

Semantic similarity means:

"This case may be worth reviewing."

It does NOT mean:

"This case has the same cause."


Think like an experienced engineer saying:

"I have seen something similar before, so this may be worth checking."

Do NOT reason like:

"I have seen this before, therefore the cause must be the same."


============================================================
INVESTIGATION METHOD
============================================================

Analyze the current evidence across documents and across time.

Look for:

- what happened
- when it happened
- which equipment was involved
- earlier warning signs
- repeated abnormalities
- changes over time
- maintenance history
- production impact
- quality impact
- safety impact
- inventory or material constraints
- unresolved or undocumented actions
- contradictions between records
- missing evidence
- possible root causes

Connect evidence across departments only when the current documents
support a meaningful relationship.

Then review relevant historical memories.

If a historical case is meaningfully related:

- compare it carefully with the current case
- identify useful lessons
- preserve its uncertainty
- suggest checks only when appropriate

Do not let historical memory override current evidence.


Before producing the final JSON, perform a final evidence audit:

1. Check every CONFIRMED FACT:

   Is it directly supported by current evidence?

2. Check every causal statement:

   Does current evidence actually establish causation, or should the
   wording be changed to an inference or hypothesis?

3. Check all current records for conflicting:

   - dates
   - times
   - measurements
   - quantities
   - statuses
   - maintenance actions
   - inspection findings
   - production outcomes
   - quality outcomes

4. Check every historical case connection:

   Is historical memory being used only as context and experience,
   never as proof of the current incident?

5. If records disagree, preserve the disagreement explicitly in
   "contradictions_and_gaps".

Accuracy is more important than producing a neat or fully resolved
story.

It is acceptable for an investigation to end with uncertainty.


============================================================
ROOT CAUSE RULES
============================================================

Generate root-cause HYPOTHESES from the CURRENT evidence.

Historical memories may help suggest a hypothesis worth checking,
but they cannot confirm that hypothesis.

Do NOT force a root cause.

Do NOT claim a root cause is confirmed unless the supplied current
evidence explicitly confirms it.

For every hypothesis include:

- evidence supporting it
- evidence that weakens or limits it
- what must be checked to confirm or reject it

Use confidence carefully.

HIGH:

Strong direct CURRENT evidence supports the explanation, with little
important missing evidence.

MEDIUM:

Several current facts support the explanation, but important
verification is still missing.

LOW:

The explanation is possible, but evidence is limited or indirect.

A similar historical case alone is NOT enough to raise root-cause
confidence.

If physical inspection, testing, repair findings, or failure
confirmation is still missing, be cautious about using HIGH
root-cause confidence.


============================================================
CONFIDENCE RULE
============================================================

Do not confuse:

INCIDENT CONFIDENCE

"Are we confident that the reported event happened?"

with:

ROOT-CAUSE CONFIDENCE

"Are we confident that we know why it happened?"

An incident can be very well documented while its root cause remains
uncertain.

The final investigation confidence must reflect the certainty of the
CURRENT investigation conclusions, not simply:

- the amount of documentation
- the existence of a similar historical case


============================================================
SOURCE RULES
============================================================

Every important factual finding about the current incident must
include its CURRENT document source.

Use:

- document name
- chunk number

Only cite document names and chunk numbers that exist in the supplied
CURRENT evidence.

Do not create fake citations.

Do NOT cite a historical case as if it were a current source
document.

Historical cases should be referenced separately by their case ID
when discussing organizational experience.


============================================================
ORGANIZATIONAL MEMORY
============================================================

At the end, create a short organizational memory summary.

This summary should preserve what a future engineer should remember
from the CURRENT investigation.

Only preserve lessons supported by current evidence.

Do NOT convert an unconfirmed hypothesis into a permanent lesson.

For example, if a seal failure is only suspected, do NOT store:

"Seal failure caused the pressure problem."

Instead store something like:

"Earlier seal wear and later pressure instability appeared in the
same equipment history. The relationship was not confirmed and
should be checked if similar symptoms occur again."

If a previous case helped the investigation, you may mention that a
similar historical pattern exists.

However, preserve differences and uncertainty.

The organization's memory must preserve uncertainty as well as
knowledge.


============================================================
USER QUESTION
============================================================

{evidence_package.get("question", "")}


============================================================
CURRENT COMPANY EVIDENCE
============================================================

{evidence_json}


============================================================
RELEVANT PAST INVESTIGATION MEMORIES
============================================================

{memory_json}


============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use exactly this top-level structure:

{{
  "case_title": "",

  "executive_assessment": "",

  "confirmed_facts": [
    {{
      "finding": "",
      "sources": [
        {{
          "document": "",
          "chunk_number": 0
        }}
      ]
    }}
  ],

  "incident_reconstruction": [
    {{
      "date": "",
      "time": "",
      "event": "",
      "significance": "",
      "sources": [
        {{
          "document": "",
          "chunk_number": 0
        }}
      ]
    }}
  ],

  "historical_warning_signals": [
    {{
      "signal": "",
      "why_it_matters": "",
      "sources": [
        {{
          "document": "",
          "chunk_number": 0
        }}
      ]
    }}
  ],

  "historical_case_connections": [
    {{
      "case_id": "",
      "case_title": "",
      "similarities": "",
      "differences": "",
      "previous_learning": "",
      "previous_uncertainty": "",
      "relevance_to_current_case": ""
    }}
  ],

  "cross_document_connections": [
    {{
      "connection": "",
      "interpretation": "",
      "classification": "CONFIRMED FACT or INFERENCE",
      "sources": [
        {{
          "document": "",
          "chunk_number": 0
        }}
      ]
    }}
  ],

  "root_cause_hypotheses": [
    {{
      "hypothesis": "",
      "confidence": "HIGH or MEDIUM or LOW",
      "supporting_evidence": "",
      "contradicting_or_limiting_evidence": "",
      "verification_needed": "",
      "sources": [
        {{
          "document": "",
          "chunk_number": 0
        }}
      ]
    }}
  ],

  "operational_impact": [
    {{
      "impact": "",
      "sources": [
        {{
          "document": "",
          "chunk_number": 0
        }}
      ]
    }}
  ],

  "contradictions_and_gaps": [
    {{
      "issue": "",
      "why_it_matters": "",
      "needed_evidence": ""
    }}
  ],

  "recommended_next_actions": [
    {{
      "action": "",
      "reason": "",
      "priority": "HIGH or MEDIUM or LOW"
    }}
  ],

  "investigation_confidence": {{
    "level": "HIGH or MEDIUM or LOW",
    "reason": ""
  }},

  "organizational_memory_summary": ""
}}

For historical_case_connections:

- Include only genuinely relevant past cases.
- If no past case is meaningfully relevant, return an empty list.
- Never force a historical connection merely because memory search
  returned a result.

Do not include Markdown.

Do not include text outside the JSON object.
"""

    return prompt


# ---------------------------------------------------------
# CLEAN GEMINI RESPONSE
# ---------------------------------------------------------

def clean_json_response(text):
    """
    Remove Markdown code fences if they appear unexpectedly.
    """

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


# ---------------------------------------------------------
# GENERATE INVESTIGATION CASE
# ---------------------------------------------------------

def generate_investigation_case(
    investigation_packet
):
    """
    Main LLM reasoning function.

    Investigation packet
            ↓
    Prepare current evidence
            ↓
    Search relevant historical case memories
            ↓
    Current evidence + organizational experience
            ↓
    Evidence-grounded Gemini reasoning
            ↓
    Structured Investigation Case File
    """

    try:

        # -------------------------------------------------
        # PREPARE CURRENT EVIDENCE
        # -------------------------------------------------

        evidence_package = prepare_evidence(
            investigation_packet
        )

        question = investigation_packet.get(
            "question",
            ""
        )

        # -------------------------------------------------
        # SEARCH GRANDPA'S PAST EXPERIENCE
        # -------------------------------------------------

        historical_memories = search_case_memories(
            question,
            n_results=3
        )

        # -------------------------------------------------
        # BUILD PROMPT WITH BOTH SOURCES
        # -------------------------------------------------

        prompt = build_investigation_prompt(
            evidence_package,
            historical_memories
        )

        # -------------------------------------------------
        # GEMINI REASONING
        # -------------------------------------------------

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={
                "temperature": 0.1,
                "response_mime_type":
                    "application/json"
            }
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        cleaned_response = clean_json_response(
            response.text
        )

        case_file = json.loads(
            cleaned_response
        )

        return {
            "success": True,

            # Useful for testing/debugging now and
            # showing historical recall later in the UI.
            "historical_memories_found":
                len(
                    historical_memories
                ),

            "historical_memory_cases": [
                {
                    "case_id":
                        memory.get(
                            "case_id",
                            ""
                        ),

                    "case_title":
                        memory.get(
                            "case_title",
                            ""
                        ),

                    "distance":
                        memory.get(
                            "distance"
                        )
                }

                for memory in
                historical_memories
            ],

            "case_file":
                case_file
        }

    except json.JSONDecodeError as error:

        return {
            "success": False,
            "error":
                "Gemini returned invalid JSON.",
            "details":
                str(error)
        }

    except Exception as error:

        return {
            "success": False,
            "error":
                "Investigation reasoning failed.",
            "details":
                str(error)
        }