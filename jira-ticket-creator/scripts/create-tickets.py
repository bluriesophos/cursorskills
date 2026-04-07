#!/usr/bin/env python3
"""
Create JIRA tickets from a JSON input file using template configuration.

Usage:
    python create-tickets.py template.json tickets.json

    template.json: Output from extract-template.py
    tickets.json:  Array of ticket definitions (see format below)

tickets.json format:
    [
      {
        "summary": "Ticket title",
        "description": "Plain text or ADF object",
        "acceptance_criteria": "Plain text or ADF object",
        "labels": ["optional", "labels"]
      }
    ]

    Description and acceptance_criteria can be:
    - A plain string (auto-converted to ADF paragraph)
    - An ADF document object ({"type":"doc","version":1,"content":[...]})

Output:
    Writes created-tickets.json with the created ticket keys and URLs.
"""

import base64
import gzip
import json
import sys
import urllib.error
import urllib.request


# --- ADF Helpers ---

def text_node(t):
    return {"type": "text", "text": t}


def paragraph(*content):
    return {"type": "paragraph", "content": list(content)}


def adf_doc(*content):
    return {"type": "doc", "version": 1, "content": list(content)}


def to_adf(value):
    """Convert a value to ADF format. Pass-through if already ADF."""
    if value is None:
        return None
    if isinstance(value, dict) and value.get("type") == "doc":
        return value
    if isinstance(value, str):
        paragraphs = []
        for line in value.split("\n"):
            if line.strip():
                paragraphs.append(paragraph(text_node(line)))
            else:
                paragraphs.append(paragraph(text_node(" ")))
        return adf_doc(*paragraphs) if paragraphs else adf_doc(paragraph(text_node(value)))
    return adf_doc(paragraph(text_node(str(value))))


# --- API ---

def get_oauth_token():
    import os
    import subprocess

    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "acli", "-w"],
            capture_output=True, text=True, check=True
        )
        raw = result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: Could not read acli token from macOS keychain.", file=sys.stderr)
        sys.exit(1)

    decoded = base64.b64decode(raw)
    decompressed = gzip.decompress(decoded)
    token_data = json.loads(decompressed.decode("utf-8"))
    return token_data["access_token"]


def api_request(api_base, token, method, path, data=None):
    url = f"{api_base}{path}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            if not resp_body:
                return {}
            return json.loads(resp_body)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return {"_error": True, "_status": e.code, "_body": error_body}


def build_payload(template, ticket):
    fields = {
        "project": {"key": template["project"]},
        "issuetype": {"id": template["issuetype_id"]},
        "summary": ticket["summary"],
    }

    # Description
    desc = ticket.get("description")
    if desc:
        fields["description"] = to_adf(desc)

    # Components from template
    if template.get("components"):
        fields["components"] = [{"id": c["id"]} for c in template["components"]]

    # Epic link from template
    if template.get("epic_link"):
        fields[template["epic_link"]["field_id"]] = template["epic_link"]["value"]

    # Labels
    if ticket.get("labels"):
        fields["labels"] = ticket["labels"]

    # Copy required custom fields from template, with overrides from ticket
    for field_id, field_data in template.get("custom_fields", {}).items():
        # Check if the ticket provides an override for this field
        override_key = field_data["display_name"]
        override_value = ticket.get(override_key) or ticket.get(field_id)

        if override_value:
            if field_data["type"] == "adf":
                fields[field_id] = to_adf(override_value)
            else:
                fields[field_id] = override_value
        elif field_data["type"] == "select":
            fields[field_id] = {"id": field_data["value"]["id"]}
        elif field_data["type"] == "multi_select":
            fields[field_id] = [{"id": v["id"]} for v in field_data["value"]]
        elif field_data["type"] == "adf":
            # ADF fields like Acceptance Criteria — use ticket override or skip
            pass

    # Explicit acceptance_criteria override (common case)
    ac = ticket.get("acceptance_criteria")
    if ac:
        for field_id, field_data in template.get("custom_fields", {}).items():
            if field_data["display_name"] == "Acceptance Criteria":
                fields[field_id] = to_adf(ac)
                break

    return {"fields": fields}


def main():
    if len(sys.argv) < 3:
        print("Usage: python create-tickets.py template.json tickets.json", file=sys.stderr)
        sys.exit(1)

    template_file = sys.argv[1]
    tickets_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "created-tickets.json"

    with open(template_file) as f:
        template = json.load(f)

    with open(tickets_file) as f:
        tickets = json.load(f)

    api_base = template["_api_base"]
    site = template["_site"]
    token = get_oauth_token()

    results = []
    for i, ticket in enumerate(tickets, 1):
        print(f"[{i}/{len(tickets)}] Creating: {ticket['summary']}...")
        payload = build_payload(template, ticket)
        result = api_request(api_base, token, "POST", "/issue", payload)

        if result.get("_error"):
            print(f"  ERROR {result['_status']}: {result['_body']}", file=sys.stderr)
            results.append({"summary": ticket["summary"], "error": result["_body"]})
        else:
            key = result.get("key", "unknown")
            url = f"https://{site}/browse/{key}"
            print(f"  Created: {key} ({url})")
            results.append({"key": key, "url": url, "summary": ticket["summary"]})

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    succeeded = sum(1 for r in results if "key" in r)
    failed = len(results) - succeeded
    print(f"\nDone: {succeeded} created, {failed} failed")
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()
