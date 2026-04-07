#!/usr/bin/env python3
"""
Extract project configuration and required fields from a JIRA template ticket.

Usage:
    python extract-template.py CPLAT-65215

Output:
    Writes template.json to current directory with project, components,
    issue type, epic link, and all required custom field values.

Requires:
    - acli installed and authenticated (run any `acli jira` command first)
    - macOS (reads OAuth token from keychain via acli config)
"""

import base64
import gzip
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
import yaml


def get_cloud_id():
    config_path = os.path.expanduser("~/.config/acli/jira_config.yaml")
    if not os.path.exists(config_path):
        print("ERROR: acli jira config not found at ~/.config/acli/jira_config.yaml", file=sys.stderr)
        print("Run 'acli jira auth login' first.", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    profiles = config.get("profiles", [])
    if not profiles:
        print("ERROR: No profiles found in acli jira config.", file=sys.stderr)
        sys.exit(1)

    return profiles[0]["cloud_id"], profiles[0]["site"]


def get_oauth_token():
    config_path = os.path.expanduser("~/.config/acli/global_auth_config.yaml")
    if not os.path.exists(config_path):
        print("ERROR: acli auth config not found.", file=sys.stderr)
        sys.exit(1)

    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "acli", "-w"],
            capture_output=True, text=True, check=True
        )
        raw = result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: Could not read acli token from macOS keychain.", file=sys.stderr)
        print("Run any 'acli jira' command to refresh authentication.", file=sys.stderr)
        sys.exit(1)

    try:
        decoded = base64.b64decode(raw)
        decompressed = gzip.decompress(decoded)
        token_data = json.loads(decompressed.decode("utf-8"))
        return token_data["access_token"]
    except Exception as e:
        print(f"ERROR: Could not decode acli token: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_issue(api_base, token, issue_key):
    url = f"{api_base}/issue/{issue_key}?expand=names"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        if e.code == 401:
            print("ERROR: OAuth token expired. Run any 'acli jira' command to refresh.", file=sys.stderr)
        else:
            print(f"ERROR: {e.code} fetching {issue_key}: {body}", file=sys.stderr)
        sys.exit(1)


def extract_template(issue_data):
    fields = issue_data.get("fields", {})
    names = issue_data.get("names", {})

    template = {
        "_source_key": issue_data["key"],
        "project": fields["project"]["key"],
        "issuetype_id": fields["issuetype"]["id"],
        "issuetype_name": fields["issuetype"]["name"],
    }

    # Components
    components = fields.get("components", [])
    if components:
        template["components"] = [{"id": c["id"], "name": c["name"]} for c in components]

    # Epic Link (customfield_10014)
    epic_link = fields.get("customfield_10014")
    if epic_link:
        template["epic_link"] = {"field_id": "customfield_10014", "value": epic_link}

    # Parent
    parent = fields.get("parent")
    if parent:
        template["parent"] = {"key": parent["key"], "summary": parent["fields"].get("summary", "")}

    # Scan for select-type custom fields that have values (potential required fields)
    # These are fields with {"self":..., "value":..., "id":...} structure
    custom_fields = {}
    for field_id, value in fields.items():
        if not field_id.startswith("customfield_"):
            continue
        if value is None:
            continue

        display_name = names.get(field_id, field_id)

        if isinstance(value, dict) and "id" in value and "value" in value and "self" in value:
            custom_fields[field_id] = {
                "display_name": display_name,
                "type": "select",
                "value": {"id": value["id"], "value": value["value"]},
            }
        elif isinstance(value, dict) and value.get("type") == "doc":
            custom_fields[field_id] = {
                "display_name": display_name,
                "type": "adf",
                "value": value,
            }
        elif isinstance(value, list) and value and isinstance(value[0], dict) and "id" in value[0] and "value" in value[0]:
            custom_fields[field_id] = {
                "display_name": display_name,
                "type": "multi_select",
                "value": [{"id": v["id"], "value": v["value"]} for v in value],
            }

    template["custom_fields"] = custom_fields

    return template


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract-template.py <ISSUE-KEY>", file=sys.stderr)
        print("Example: python extract-template.py CPLAT-65215", file=sys.stderr)
        sys.exit(1)

    issue_key = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "template.json"

    print(f"Extracting template from {issue_key}...")

    cloud_id, site = get_cloud_id()
    api_base = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3"

    token = get_oauth_token()
    issue_data = fetch_issue(api_base, token, issue_key)
    template = extract_template(issue_data)

    # Add API metadata for downstream scripts
    template["_api_base"] = api_base
    template["_site"] = site

    with open(output_file, "w") as f:
        json.dump(template, f, indent=2)

    print(f"\nTemplate saved to {output_file}")
    print(f"  Project:    {template['project']}")
    print(f"  Type:       {template['issuetype_name']} (id: {template['issuetype_id']})")
    if template.get("components"):
        names = ", ".join(c["name"] for c in template["components"])
        print(f"  Components: {names}")
    if template.get("epic_link"):
        print(f"  Epic:       {template['epic_link']['value']}")
    print(f"  Custom fields: {len(template['custom_fields'])}")

    # Flag likely required fields
    likely_required = ["Acceptance Criteria", "Update Instructions", "Components"]
    found = []
    for fid, fdata in template["custom_fields"].items():
        if fdata["display_name"] in likely_required:
            found.append(f"    {fid} ({fdata['display_name']}): {fdata['type']}")
    if found:
        print(f"\n  Likely required fields (include in ticket payloads):")
        for f in found:
            print(f)


if __name__ == "__main__":
    main()
