#!/usr/bin/env python3
"""v122 unified SimC runtime/profile format for all supported DPS archetypes.

Specialization-specific APL, physical item IDs and weapon rules remain data;
the *new session* layout and Native output contract are common. Never silently
upgrade or overwrite an already sealed legacy session. No Native calls.
"""
from __future__ import annotations
import v055_simc_item_selection as items
import v063_numeric_injection as numeric

SCHEMA="v122_common_simc_profile_format_v1"
# Stable for new sessions regardless of Python hash randomization, class or spec.
SLOT_ORDER=tuple(sorted(items.SLOTS))
JSON2_PLACEHOLDER="__SIMC_NATIVE_RESULT_PATH_REPLACED_PER_CANDIDATE__"

class ProfileFormatBlocked(ValueError):pass

def need(ok,code):
    if not ok:raise ProfileFormatBlocked(code)

def order_rows(rows,*,legacy):
    """Return source order for sealed historical sessions; otherwise canonical."""
    need(type(rows) is dict and rows and set(rows)<=set(SLOT_ORDER)
         and all(type(row) is dict and row.get("slot")==slot
                 for slot,row in rows.items()),
         "INVALID_PROFILE_EQUIPMENT_ROWS")
    return dict(rows) if legacy else {slot:rows[slot] for slot in SLOT_ORDER
                                     if slot in rows}

def finalize(profile,*,legacy):
    """Keep legacy bytes or standardize candidate-output placeholder.

    In both cases the generated *Native request* is validated separately with
    exactly one json2=, iterations= and four gear_* lines by v063. A legacy
    profile without json2= is read-only compatibility, never a new-format
    profile and never a reason to delete a user session.
    """
    need(type(profile) is str and profile.endswith("\n"),
         "PROFILE_TEXT_REQUIRED")
    lines=profile.splitlines()
    count=lambda prefix:sum(line.startswith(prefix) for line in lines)
    need(count("iterations=")==1 and count("json2=")<=1,
         "PROFILE_RUNTIME_SETTINGS_NOT_UNIQUE")
    if legacy:
        numeric.input_parts(profile,allow_missing_json2_template=True)
        return profile
    canonical="json2="+JSON2_PLACEHOLDER
    if count("json2=")==1:
        lines=[canonical if line.startswith("json2=") else line
               for line in lines]
    else:
        lines.append(canonical)
    output="\n".join(lines)+"\n"
    numeric.input_parts(output)  # new sessions must contain exactly one json2=
    return output
