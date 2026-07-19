import re
from datetime import datetime


# ---------------------------------------------------------
# DATE PARSING
# ---------------------------------------------------------

def parse_date(date_string):
    """
    Convert supported date strings into datetime objects
    so timeline events can be sorted chronologically.
    """

    if not date_string or date_string == "Unknown":
        return datetime.max

    formats = [
        "%d-%b-%Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d %B %Y",
        "%d %b %Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    return datetime.max


# ---------------------------------------------------------
# TIME PARSING
# ---------------------------------------------------------

def parse_time(time_string):
    """
    Convert time into sortable value.
    Unknown times are placed after known times on the same date.
    """

    if not time_string or time_string == "Unknown":
        return (99, 99)

    match = re.search(
        r"\b(\d{1,2}):(\d{2})(?:\s*(AM|PM))?\b",
        time_string,
        flags=re.IGNORECASE
    )

    if not match:
        return (99, 99)

    hour = int(match.group(1))
    minute = int(match.group(2))
    period = match.group(3)

    if period:
        period = period.upper()

        if period == "PM" and hour != 12:
            hour += 12

        if period == "AM" and hour == 12:
            hour = 0

    return (hour, minute)


# ---------------------------------------------------------
# BASIC TEXT CLEANING
# ---------------------------------------------------------

def clean_text(text):
    """
    Clean formatting noise without changing the meaning
    or joining legitimate words together.

    Important:
    We intentionally do NOT try to repair every broken PDF word.
    The LLM should receive faithful evidence rather than text
    that has been aggressively modified.
    """

    if not text:
        return ""

    text = text.replace("\u00a0", " ")

    # Remove standalone PDF line numbers.
    text = re.sub(
        r"(?m)^\s*\d+\s*$",
        " ",
        text
    )

    # Remove long separator lines.
    text = re.sub(
        r"[-_=]{5,}",
        " ",
        text
    )

    # Convert line breaks/tabs to spaces.
    text = re.sub(
        r"[\r\n\t]+",
        " ",
        text
    )

    # Collapse repeated whitespace only.
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ---------------------------------------------------------
# DOCUMENT DATE
# ---------------------------------------------------------

def get_document_date(chunks):
    """
    Determine the most likely primary date of a document.

    We prefer explicit document-level date fields such as:
        Date : 04-Nov-2024
        PM DATE : 07-Oct-2024
        Date Raised : 04-Nov-2024

    This prevents fields such as:
        Previous PM
        Next PM Due
        Estimated Completion

    from incorrectly becoming the main timeline date.
    """

    preferred_patterns = [
        r"\bPM\s+DATE\s*:\s*(\d{1,2}-[A-Za-z]{3}-\d{4})",
        r"\bDate\s+Raised\s*:\s*(\d{1,2}-[A-Za-z]{3}-\d{4})",
        r"\bDate\s*:\s*(\d{1,2}-[A-Za-z]{3}-\d{4})",
        r"\bDate\s+Raised\s*:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"\bDate\s*:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
    ]

    # Search early chunks first because document headers
    # usually contain the authoritative document date.
    ordered_chunks = sorted(
        chunks,
        key=lambda chunk: chunk.get("chunk_number", 999999)
    )

    for chunk in ordered_chunks:

        content = chunk.get("content", "")

        for pattern in preferred_patterns:

            match = re.search(
                pattern,
                content,
                flags=re.IGNORECASE
            )

            if match:
                return match.group(1)

    # Fallback to extracted dates.
    for chunk in ordered_chunks:

        dates = chunk.get("dates", [])

        if dates:
            return dates[0]

    return "Unknown"


# ---------------------------------------------------------
# DOCUMENT MACHINE
# ---------------------------------------------------------

def get_document_machine(chunks):
    """
    Find the primary equipment/machine for the document.

    Prefer explicit fields such as:
        Equipment : Hydraulic Press HP-05
        Machine   : HP-05

    This avoids treating part numbers, batch IDs and material
    codes as machines.
    """

    ordered_chunks = sorted(
        chunks,
        key=lambda chunk: chunk.get("chunk_number", 999999)
    )

    explicit_patterns = [
        r"\bEquipment\s*:\s*[^\n]*?\b((?:HP|CMP|PMP|MTR)-\d+[A-Z]?)\b",
        r"\bMachine\s*:\s*[^\n]*?\b((?:HP|CMP|PMP|MTR)-\d+[A-Z]?)\b",
        r"\bEquipment\s+ID\s*:\s*[^\n]*?\b((?:HP|CMP|PMP|MTR)-\d+[A-Z]?)\b"
    ]

    for chunk in ordered_chunks:

        content = chunk.get("content", "")

        for pattern in explicit_patterns:

            match = re.search(
                pattern,
                content,
                flags=re.IGNORECASE
            )

            if match:
                return match.group(1).upper()

    # Fallback to validated extracted machine IDs.
    for chunk in ordered_chunks:

        for machine in chunk.get("machines", []):

            if re.fullmatch(
                r"(?:HP|CMP|PMP|MTR)-\d+[A-Z]?",
                machine,
                flags=re.IGNORECASE
            ):
                return machine.upper()

    return "Unknown"


# ---------------------------------------------------------
# VALID MACHINE DETECTION
# ---------------------------------------------------------

def find_machine(text, extracted_machines, document_machine):
    """
    Determine the machine associated with an event.

    Only equipment-like IDs are accepted.

    We intentionally exclude codes such as:
        HYD-46
        LIT-00
        NOV-041
        CB-14A
        PRV-220

    because these may represent materials, batches or parts.
    """

    valid_machine_pattern = (
        r"\b(?:HP|CMP|PMP|MTR)-\d+[A-Z]?\b"
    )

    match = re.search(
        valid_machine_pattern,
        text,
        flags=re.IGNORECASE
    )

    if match:
        return match.group(0).upper()

    for machine in extracted_machines:

        if re.fullmatch(
            valid_machine_pattern,
            machine,
            flags=re.IGNORECASE
        ):
            return machine.upper()

    if document_machine != "Unknown":
        return document_machine

    return "Unknown"


# ---------------------------------------------------------
# EVENT DATE DETECTION
# ---------------------------------------------------------
def find_event_date(text, extracted_dates, document_date):
    """
    Determine the date belonging to an event.

    Priority:
    1. Dates explicitly connected to event language
    2. Document's primary date
    3. Extracted date fallback

    This prevents metadata dates such as Estimated Completion,
    Next PM Due, Previous PM, etc. from being mistaken for the
    actual event date.
    """

    date_pattern = (
        r"(?:"
        r"\d{1,2}-[A-Za-z]{3}-\d{4}|"
        r"\d{1,2}/\d{1,2}/\d{2,4}|"
        r"\d{1,2}-\d{1,2}-\d{2,4}"
        r")"
    )

    # Prefer dates connected to actual event language.
    contextual_patterns = [
        rf"\b(?:observed|occurred|reported|noticed|detected|found)"
        rf".{{0,120}}?\b(?:on|at)\s+({date_pattern})",

        rf"\b(?:on|dated)\s+({date_pattern})"
        rf".{{0,120}}?\b(?:observed|occurred|reported|noticed|detected|found)"
    ]

    for pattern in contextual_patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

        if match:
            return match.group(1)

    # If no event-specific date exists, inherit the primary
    # document date rather than blindly taking another metadata date.
    if document_date != "Unknown":
        return document_date

    # Final fallback.
    if extracted_dates:
        return extracted_dates[0]

    return "Unknown"

# ---------------------------------------------------------
# TIME EVENT EXTRACTION
# ---------------------------------------------------------

def extract_timestamped_events(text):
    """
    Extract narrative events that explicitly begin with a time.

    Example:

        15:20 — HP-05 pressure fluctuation noted again.
        16:45 — Output pace reduced.

    Each becomes a separate timeline event.

    This deliberately ignores header ranges such as:

        Shift : Evening (14:00 – 22:00)

    because they are metadata, not individual events.
    """

    events = []

    pattern = re.compile(
        r"(?:^|\s)"
        r"(\d{1,2}:\d{2}(?:\s*(?:AM|PM))?)"
        r"\s*[—–-]\s*"
        r"(.*?)"
        r"(?="
        r"\s+\d{1,2}:\d{2}(?:\s*(?:AM|PM))?\s*[—–-]"
        r"|$"
        r")",
        flags=re.IGNORECASE | re.DOTALL
    )

    for match in pattern.finditer(text):

        time_value = match.group(1).strip()
        event_text = match.group(2).strip()

        event_text = clean_text(event_text)

        if event_text:
            events.append(
                {
                    "time": time_value,
                    "event": event_text
                }
            )

    return events


# ---------------------------------------------------------
# EMBEDDED TIME DETECTION
# ---------------------------------------------------------

def find_embedded_time(text):
    """
    Detect a meaningful time inside prose.

    Example:
        Issue first observed ... around 09:30.

    Avoid using document metadata fields such as:
        Time : 19:55

    Those describe the document transaction itself and do not
    necessarily represent a separate investigation event.
    """

    contextual_patterns = [
        r"\baround\s+(\d{1,2}:\d{2}(?:\s*(?:AM|PM))?)\b",
        r"\bat\s+(\d{1,2}:\d{2}(?:\s*(?:AM|PM))?)\s*(?:hrs?|hours?)?\b",
        r"\bobserved[^\n.]*?\b(\d{1,2}:\d{2}(?:\s*(?:AM|PM))?)\b",
        r"\breported[^\n.]*?\b(\d{1,2}:\d{2}(?:\s*(?:AM|PM))?)\b"
    ]

    for pattern in contextual_patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1).strip()

    return "Unknown"


# ---------------------------------------------------------
# CHECK IF CHUNK IS ONLY HEADER / METADATA
# ---------------------------------------------------------

def is_header_only_chunk(text):
    """
    Identify chunks that mostly contain document metadata.

    We still preserve useful document context elsewhere,
    but avoid creating fake timeline events from shift ranges.
    """

    lowered = text.lower()

    narrative_keywords = [
        "reported",
        "observed",
        "fluctuation",
        "breakdown",
        "reduced",
        "completed",
        "deferred",
        "issued",
        "shortage",
        "nil",
        "maintenance scheduled",
        "showing",
        "recommend",
        "minor wear",
        "consumption",
        "topped up",
        "no leaks",
        "pressure",
        "output impact"
    ]

    if any(keyword in lowered for keyword in narrative_keywords):
        return False

    metadata_keywords = [
        "supervisor",
        "operators",
        "location",
        "department",
        "authorised by",
        "issued by",
        "issued to",
        "pm schedule",
        "log period",
        "reviewed by"
    ]

    metadata_count = sum(
        1 for keyword in metadata_keywords
        if keyword in lowered
    )

    return metadata_count >= 2


# ---------------------------------------------------------
# TIMELINE EVENT CREATION
# ---------------------------------------------------------

def create_event(
    date,
    time,
    machine,
    document_name,
    chunk,
    event_text
):
    """
    Create standardized timeline event.
    """

    return {
        "date": date,
        "time": time,
        "machine": machine,
        "document": document_name,
        "chunk_number": chunk.get(
            "chunk_number",
            -1
        ),
        "relevance_score": chunk.get(
            "relevance_score",
            0
        ),
        "event": clean_text(event_text)
    }


# ---------------------------------------------------------
# DUPLICATE REMOVAL
# ---------------------------------------------------------

def deduplicate_timeline(timeline):
    """
    Remove exact or near-exact duplicate timeline events.
    """

    unique = []
    seen = set()

    for event in timeline:

        normalized_event = re.sub(
            r"\s+",
            " ",
            event["event"].lower()
        ).strip()

        key = (
            event["date"],
            event["time"],
            event["machine"],
            normalized_event
        )

        if key not in seen:

            seen.add(key)

            unique.append(event)

    return unique


# ---------------------------------------------------------
# MAIN TIMELINE BUILDER
# ---------------------------------------------------------

def build_timeline(investigation_packet):
    """
    Build an evidence-grounded chronological timeline.

    Important design principle:

    The timeline is NOT a replacement for the original evidence.

    It is only an additional structured view that helps the LLM
    understand chronology.

    Original retrieved chunks remain untouched inside:
        investigation_packet["documents"]

    Therefore the final LLM receives:
        1. original evidence
        2. extracted entities
        3. structured timeline
    """

    timeline = []

    documents = investigation_packet.get(
        "documents",
        {}
    )

    for document_name, chunks in documents.items():

        document_date = get_document_date(
            chunks
        )

        document_machine = get_document_machine(
            chunks
        )

        for chunk in chunks:

            raw_content = chunk.get(
                "content",
                ""
            )

            if not raw_content.strip():
                continue

            cleaned_content = clean_text(
                raw_content
            )

            extracted_dates = chunk.get(
                "dates",
                []
            )

            extracted_machines = chunk.get(
                "machines",
                []
            )

            # -------------------------------------------------
            # 1. Extract explicit timestamped narrative events.
            # -------------------------------------------------

            timestamped_events = extract_timestamped_events(
                raw_content
            )

            if timestamped_events:

                for item in timestamped_events:

                    event_text = item["event"]

                    event_date = find_event_date(
                        event_text,
                        extracted_dates,
                        document_date
                    )

                    machine = find_machine(
                        event_text,
                        extracted_machines,
                        document_machine
                    )

                    timeline.append(
                        create_event(
                            date=event_date,
                            time=item["time"],
                            machine=machine,
                            document_name=document_name,
                            chunk=chunk,
                            event_text=event_text
                        )
                    )

                continue

            # -------------------------------------------------
            # 2. For non-timestamped chunks, preserve useful
            #    evidence as contextual timeline entries.
            # -------------------------------------------------

            if is_header_only_chunk(
                cleaned_content
            ):
                continue

            event_date = find_event_date(
                raw_content,
                extracted_dates,
                document_date
            )

            embedded_time = find_embedded_time(
                raw_content
            )

            machine = find_machine(
                raw_content,
                extracted_machines,
                document_machine
            )

            timeline.append(
                create_event(
                    date=event_date,
                    time=embedded_time,
                    machine=machine,
                    document_name=document_name,
                    chunk=chunk,
                    event_text=cleaned_content
                )
            )

    # ---------------------------------------------------------
    # REMOVE DUPLICATES
    # ---------------------------------------------------------

    timeline = deduplicate_timeline(
        timeline
    )

    # ---------------------------------------------------------
    # CHRONOLOGICAL SORTING
    # ---------------------------------------------------------

    timeline.sort(
        key=lambda event: (
            parse_date(
                event["date"]
            ),
            parse_time(
                event["time"]
            ),
            event["document"],
            event["chunk_number"]
        )
    )

    return timeline