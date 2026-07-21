import re
from typing import Dict, List, Set


# ==========================================================
# CONFIGURATION
# ==========================================================

# Supported machine prefixes
MACHINE_PREFIXES = [
    "HP",
    "PRV",
    "PMP",
    "CMP",
    "MTR",
    "LIT",
    "PLC",
    "CV",
    "FAN",
    "MIX"
]


# Known departments
DEPARTMENTS = {
    "Maintenance",
    "Production",
    "Quality",
    "Stores",
    "Safety",
    "Engineering",
    "Operations"
}


# Labels that usually contain person names
ROLE_LABELS = [

    "Raised By",
    "Assigned To",
    "Approved By",
    "Reviewed By",
    "Authorised By",
    "Issued By",
    "Issued To",
    "Operator",
    "Operators",
    "Supervisor",
    "Technician",
    "Receiver Signature",
    "Manager Sign"
]


# Things we never want as entities
BLACKLIST = {

    "Actual Work",
    "Actual Output",
    "Output Impact",
    "Production Summary",
    "Quality Notes",
    "Shift Notes",
    "Downtime Record",
    "Completion Remarks",
    "Inventory Issue",
    "Issue Slip",
    "Material Consumed",
    "Work Order",
    "Preventive Maintenance",
    "Hydraulic Press",
    "Pressure Gauge",
    "Pump Line",
    "Shop Floor",
    "Maintenance Engineer",
    "Maintenance Manager",
    "Production Supervisor",
    "Store Manager",
    "Receiver Signature",
    "Technician Sign",
    "Manager Sign",
    "Approved By",
    "Assigned To",
    "Raised By",
    "Reviewed By",
    "Authorised By",
    "Date Raised",
    "Date Completed",
    "Time Taken",
    "Parts Used"
}


# ==========================================================
# HELPERS
# ==========================================================

def clean_text(text: str) -> str:
    """
    Remove OCR artefacts and normalize whitespace.
    """

    text = text.replace("\r", "\n")

    text = re.sub(r"\n+", "\n", text)

    text = re.sub(r"[ \t]+", " ", text)

    return text


def normalize_name(value: str) -> str:

    value = value.strip()

    value = re.sub(r"\s+", " ", value)

    return value.title()


def normalize_machine(machine: str) -> str:
    """
    HP-5 -> HP-05
    LIT-0 -> LIT-00
    """

    match = re.match(r"([A-Za-z]+)-(\d+)([A-Za-z]?)", machine)

    if not match:
        return machine.upper()

    prefix = match.group(1).upper()

    number = int(match.group(2))

    suffix = match.group(3).upper()

    return f"{prefix}-{number:02d}{suffix}"


def unique_sorted(values: Set[str]) -> List[str]:
    return sorted(values)


# ==========================================================
# EMPTY RESULT TEMPLATE
# ==========================================================

def empty_entities():

    return {

        "machines": set(),

        "work_orders": set(),

        "issue_ids": set(),

        "departments": set(),

        "people": set(),

        "dates": set(),

        "times": set()
    }



# ==========================================================
# MACHINE IDS
# ==========================================================

def extract_machine_ids(text: str):

    machines = set()

    prefix_pattern = "|".join(MACHINE_PREFIXES)

    pattern = rf"\b(?:{prefix_pattern})-\d+[A-Za-z]?\b"

    for match in re.findall(pattern, text, flags=re.IGNORECASE):
        machines.add(normalize_machine(match))

    return machines


# ==========================================================
# WORK ORDERS
# ==========================================================

def extract_work_orders(text: str):

    return set(
        re.findall(
            r"\bMWO-\d{4}-\d{4}\b",
            text,
            flags=re.IGNORECASE
        )
    )


# ==========================================================
# ISSUE IDS
# ==========================================================

def extract_issue_ids(text: str):

    return set(
        re.findall(
            r"\bINV-ISSUE-\d{4}-\d{4}\b",
            text,
            flags=re.IGNORECASE
        )
    )


# ==========================================================
# DEPARTMENTS
# ==========================================================

def extract_departments(text: str):

    departments = set()

    for department in DEPARTMENTS:

        if re.search(
            rf"\b{re.escape(department)}\b",
            text,
            flags=re.IGNORECASE
        ):
            departments.add(department)

    return departments


# ==========================================================
# DATES
# ==========================================================

def extract_dates(text: str):

    dates = set()

    patterns = [

        r"\b\d{1,2}-[A-Za-z]{3}-\d{4}\b",

        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",

        r"\b\d{1,2}-\d{1,2}-\d{2,4}\b",

        r"\b\d{1,2}\s+[A-Za-z]+\s+\d{4}\b"

    ]

    for pattern in patterns:

        dates.update(
            re.findall(pattern, text)
        )

    return dates


# ==========================================================
# TIMES
# ==========================================================

def extract_times(text: str):

    return set(
        re.findall(
            r"\b\d{1,2}:\d{2}(?:\s?(?:AM|PM))?\b",
            text,
            flags=re.IGNORECASE
        )
    )


# ==========================================================
# PEOPLE
# ==========================================================

def extract_people(text: str):

    people = set()

    text = clean_text(text)

    for label in ROLE_LABELS:

        pattern = (
            rf"{re.escape(label)}"
            rf"\s*:?\s*"
            rf"([^\n]+)"
        )

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:

            # Remove anything inside brackets
            match = re.sub(r"\(.*?\)", "", match)

            # Split multiple names
            parts = re.split(r",|/| and ", match)

            for part in parts:

                person = normalize_name(part)

                if len(person) < 5:
                    continue

                if person in BLACKLIST:
                    continue

                # Keep only names
                if re.fullmatch(
                    r"[A-Z][a-z]+(?:\s+[A-Z]\.)?(?:\s+[A-Z][a-z]+)+",
                    person
                ):
                    people.add(person)

    return people

# MAIN ENTITY EXTRACTION

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract structured industrial entities from text.

    Returns:
    {
        "machines": [...],
        "work_orders": [...],
        "issue_ids": [...],
        "departments": [...],
        "people": [...],
        "dates": [...],
        "times": [...]
    }
    """

    text = clean_text(text)

    entities = empty_entities()

    entities["machines"].update(
        extract_machine_ids(text)
    )

    entities["work_orders"].update(
        extract_work_orders(text)
    )

    entities["issue_ids"].update(
        extract_issue_ids(text)
    )

    entities["departments"].update(
        extract_departments(text)
    )

    entities["people"].update(
        extract_people(text)
    )

    entities["dates"].update(
        extract_dates(text)
    )

    entities["times"].update(
        extract_times(text)
    )

    # Remove accidental blacklist entries
    for key in entities:

        cleaned = set()

        for value in entities[key]:

            value = value.strip()

            if not value:
                continue

            if value in BLACKLIST:
                continue

            cleaned.add(value)

        entities[key] = unique_sorted(cleaned)

    return entities