#!/usr/bin/env python3
"""Tiny offline validator for the GitHub development-continuity ledger.

No native simulation, HTTP, artifact writes, product readiness or GitHub API.
--since BASE is optional: use the explicit logical-task baseline, not main.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "docs/development/"
REQUIRED = (
    "Capability", "Keywords", "Prior evidence", "Decision",
    "Changes", "Verification", "Remaining", "Efficiency",
)
EVIDENCE = {
    "SOURCE_CORROBORATED", "SOURCE_PARTIAL", "SOURCE_UNVERIFIED",
    "CODE_ONLY", "EXECUTED_NATIVE", "HISTORICAL", "POLICY_DOCUMENTED",
}
INTEGRATION = {"INTEGRATED", "NOT_INTEGRATED", "PARTIAL", "NOT_READY"}
KEY = re.compile(r"`([A-Z][A-Z0-9]*(?:\.[A-Z0-9]+)+)`")
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
NOTE_NAME = re.compile(r"\d{4}-\d{2}-\d{2}_[a-z0-9-]+\.md\Z")


def _links(text, *, parent, root):
    """Check only local links; external evidence URLs remain untouched."""
    errors = []
    for dest in LINK.findall(text):
        if "://" in dest or dest.startswith("#"):
            continue
        path = (parent / dest.split("#", 1)[0]).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            errors.append("LINK_MISSING_OR_OUTSIDE:" + dest)
    return errors


def _index(root):
    folder = root / "docs" / "development"
    index = folder / "INDEX.md"
    if not index.is_file():
        return {}, ["INDEX_MISSING"]
    text = index.read_text(encoding="utf8")
    entries = {}
    errors = _links(text, parent=folder, root=root)
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            errors.append("INDEX_COLUMN_COUNT_INVALID")
            continue
        keys = KEY.findall(cells[0])
        if len(keys) != 1 or cells[0] != "`" + keys[0] + "`":
            errors.append("INDEX_CAPABILITY_KEY_INVALID")
            continue
        key = keys[0]
        if key in entries:
            errors.append("INDEX_DUPLICATE_CAPABILITY:" + key)
        if not cells[1] or not cells[4] or not cells[5]:
            errors.append("INDEX_ROW_EMPTY_REQUIRED_FIELD:" + key)
        if cells[2] not in {"`" + x + "`" for x in EVIDENCE}:
            errors.append("INDEX_EVIDENCE_STATUS_INVALID:" + key)
        if cells[3] not in {"`" + x + "`" for x in INTEGRATION}:
            errors.append("INDEX_INTEGRATION_STATUS_INVALID:" + key)
        entries[key] = cells
    if not entries:
        errors.append("INDEX_HAS_NO_CAPABILITY_ROWS")
    return entries, errors


def _note(root, path, valid_keys):
    text = path.read_text(encoding="utf8")
    errors = _links(text, parent=path.parent, root=root)
    if not NOTE_NAME.fullmatch(path.name):
        errors.append("NOTE_NAME_INVALID:" + path.name)
    lines = text.splitlines()
    if len(lines) > 45 or not lines or not lines[0].startswith("# "):
        errors.append("NOTE_MUST_BE_SHORT_WITH_TITLE:" + path.name)
    contents = {}
    for field in REQUIRED:
        matches = re.findall(
            r"^- \*\*" + re.escape(field) + r":\*\* (\S.*)$",
            text, flags=re.MULTILINE,
        )
        if len(matches) != 1:
            errors.append("NOTE_REQUIRED_FIELD:" + path.name + ":" + field)
        else:
            contents[field] = matches[0]
    keys = KEY.findall(contents.get("Capability", ""))
    if not keys:
        errors.append("NOTE_HAS_NO_CAPABILITY:" + path.name)
    for key in keys:
        if key not in valid_keys:
            errors.append("NOTE_CAPABILITY_NOT_INDEXED:" + key)
    if "Decision" in contents and not re.match(
        r"^`(?:REUSE|CONNECT|EXTEND|NEW|STOP)`", contents["Decision"]
    ):
        errors.append("NOTE_DECISION_INVALID:" + path.name)
    return keys, errors


def validate(root=ROOT):
    """Return errors, do not mutate any files."""
    root = Path(root).resolve()
    folder = root / "docs" / "development"
    index_path = folder / "INDEX.md"
    index, errors = _index(root)
    note_dir = folder / "notes"
    if not note_dir.is_dir():
        return errors + ["NOTES_DIRECTORY_MISSING"]
    notes = sorted(note_dir.glob("*.md"))
    if not notes:
        errors.append("NO_DEVELOPMENT_NOTES")
    index_text = index_path.read_text("utf8") if index_path.is_file() else ""
    for note in notes:
        keys, problems = _note(root, note, index)
        errors.extend(problems)
        relative = "notes/" + note.name
        if relative not in index_text:
            errors.append("NOTE_NOT_LINKED_FROM_INDEX:" + note.name)
        # Every affected capability row must link the latest relevant note.
        for key in keys:
            if relative not in index.get(key, [""] * 6)[5]:
                errors.append("NOTE_NOT_LINKED_FROM_CAPABILITY:" + key)
    return errors


def check_changed_files(paths):
    """One note per logical batch, NOT per code-file or intermediate commit."""
    paths = set(paths)
    changed = any(
        p.startswith(("runner/", "tests/", "tools/", "data/",
                      ".github/workflows/"))
        for p in paths
    )
    has_note = any(
        p.startswith(PREFIX + "notes/") and p.endswith(".md")
        for p in paths
    )
    has_index = PREFIX + "INDEX.md" in paths
    return (["TASK_CHANGE_WITHOUT_DEVELOPMENT_NOTE"] if changed and not has_note
            else []) + (
                ["TASK_NOTE_WITHOUT_INDEX_UPDATE"] if has_note and not has_index
                else []
            )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", metavar="TASK_BASE_REF")
    args = parser.parse_args(argv)
    errors = validate()
    if args.since:
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", args.since + "...HEAD"],
                cwd=ROOT, capture_output=True, text=True, check=True,
                timeout=15,
            )
            errors.extend(check_changed_files(result.stdout.splitlines()))
        except (OSError, subprocess.CalledProcessError,
                subprocess.TimeoutExpired):
            errors.append("TASK_BASE_DIFF_UNAVAILABLE")
    for error in errors:
        print("DEV_LEDGER_FAIL", error)
    if errors:
        return 1
    print("DEV_LEDGER_PASS", "OFFLINE_NO_NATIVE_NO_NETWORK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
