#!/usr/bin/env python3
"""
Post-creation tasks: remove assignees, link tickets, and attach files.

Usage:
    python post-create.py template.json created-tickets.json [options]

Options:
    --unassign              Remove assignee from all created tickets
    --link-to KEY           Link all created tickets to KEY (e.g., CPLAT-65215)
    --link-type TYPE        Link type (default: "Relates")
    --attach FILE:KEY       Attach FILE to ticket KEY (repeatable)
    --attach-pattern DIR:N  Attach files matching pattern from DIR
                            (e.g., "docs/tickets:ticket-{n}-*.md" attaches
                            ticket-1-*.md to first ticket, ticket-2-*.md to second)

Examples:
    # Unassign all and link to parent
    python post-create.py template.json created-tickets.json \\
        --unassign --link-to CPLAT-65215

    # Attach specific files
    python post-create.py template.json created-tickets.json \\
        --attach docs/plan-1.md:CPLAT-67326 \\
        --attach docs/plan-2.md:CPLAT-67327

    # Attach files by index (1-based, matching ticket order in created-tickets.json)
    python post-create.py template.json created-tickets.json \\
        --attach-idx 1:docs/plan-1.md \\
        --attach-idx 2:docs/plan-2.md
"""

import base64
import gzip
import json
import os
import sys
import urllib.error
import urllib.request


def get_oauth_token():
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
                return {"_ok": True}
            return json.loads(resp_body)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return {"_error": True, "_status": e.code, "_body": error_body}


def attach_file(api_base, token, issue_key, file_path):
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_data = f.read()

    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    url = f"{api_base}/issue/{issue_key}/attachments"
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-Atlassian-Token": "no-check",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result[0].get("filename", filename)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"  ERROR attaching {filename}: {e.code} {error_body}", file=sys.stderr)
        return None


def parse_args(argv):
    opts = {
        "template_file": None,
        "tickets_file": None,
        "unassign": False,
        "link_to": None,
        "link_type": "Relates",
        "attachments": [],      # [(file_path, issue_key)]
        "attach_by_idx": [],    # [(1-based index, file_path)]
    }

    positional = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--unassign":
            opts["unassign"] = True
        elif arg == "--link-to" and i + 1 < len(argv):
            i += 1
            opts["link_to"] = argv[i]
        elif arg == "--link-type" and i + 1 < len(argv):
            i += 1
            opts["link_type"] = argv[i]
        elif arg == "--attach" and i + 1 < len(argv):
            i += 1
            parts = argv[i].rsplit(":", 1)
            if len(parts) == 2:
                opts["attachments"].append((parts[0], parts[1]))
            else:
                print(f"ERROR: --attach requires FILE:KEY format, got: {argv[i]}", file=sys.stderr)
                sys.exit(1)
        elif arg == "--attach-idx" and i + 1 < len(argv):
            i += 1
            parts = argv[i].split(":", 1)
            if len(parts) == 2:
                opts["attach_by_idx"].append((int(parts[0]), parts[1]))
            else:
                print(f"ERROR: --attach-idx requires N:FILE format, got: {argv[i]}", file=sys.stderr)
                sys.exit(1)
        elif not arg.startswith("-"):
            positional.append(arg)
        else:
            print(f"Unknown option: {arg}", file=sys.stderr)
            sys.exit(1)
        i += 1

    if len(positional) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    opts["template_file"] = positional[0]
    opts["tickets_file"] = positional[1]
    return opts


def main():
    opts = parse_args(sys.argv[1:])

    with open(opts["template_file"]) as f:
        template = json.load(f)

    with open(opts["tickets_file"]) as f:
        created = json.load(f)

    api_base = template["_api_base"]
    token = get_oauth_token()

    # Filter to successfully created tickets
    tickets = [t for t in created if "key" in t]
    if not tickets:
        print("No successfully created tickets found.")
        return

    # Unassign
    if opts["unassign"]:
        print("=== Removing assignees ===")
        for t in tickets:
            print(f"  {t['key']}...", end=" ")
            result = api_request(api_base, token, "PUT", f"/issue/{t['key']}/assignee", {"accountId": None})
            if result.get("_error"):
                print(f"ERROR: {result['_body']}")
            else:
                print("done")

    # Link
    if opts["link_to"]:
        print(f"\n=== Linking to {opts['link_to']} ({opts['link_type']}) ===")
        for t in tickets:
            print(f"  {t['key']} -> {opts['link_to']}...", end=" ")
            result = api_request(api_base, token, "POST", "/issueLink", {
                "type": {"name": opts["link_type"]},
                "inwardIssue": {"key": opts["link_to"]},
                "outwardIssue": {"key": t["key"]},
            })
            if result.get("_error"):
                print(f"ERROR: {result['_body']}")
            else:
                print("done")

    # Attach files by key
    if opts["attachments"]:
        print("\n=== Attaching files (by key) ===")
        for file_path, issue_key in opts["attachments"]:
            print(f"  {os.path.basename(file_path)} -> {issue_key}...", end=" ")
            result = attach_file(api_base, token, issue_key, file_path)
            if result:
                print(f"done ({result})")
            else:
                print("FAILED")

    # Attach files by index
    if opts["attach_by_idx"]:
        print("\n=== Attaching files (by index) ===")
        for idx, file_path in opts["attach_by_idx"]:
            if idx < 1 or idx > len(tickets):
                print(f"  SKIP: index {idx} out of range (1-{len(tickets)})", file=sys.stderr)
                continue
            issue_key = tickets[idx - 1]["key"]
            print(f"  {os.path.basename(file_path)} -> {issue_key} (#{idx})...", end=" ")
            result = attach_file(api_base, token, issue_key, file_path)
            if result:
                print(f"done ({result})")
            else:
                print("FAILED")

    print("\nAll post-creation tasks complete.")


if __name__ == "__main__":
    main()
