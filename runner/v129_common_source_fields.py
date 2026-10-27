#!/usr/bin/env python3
"""P1 source-profile field extraction shared by six source-backed archetypes.

Read-only parsing. Does not infer item compatibility, model SimC effects, or
normalize APL. Original source SHA, exact weapon/gear/tier, duplicate guards
and profile-byte sealing remain the caller's responsibility.
"""
from __future__ import annotations
import re

class SourceFieldsBlocked(ValueError):
    pass

def _need(need,ok,code):
    if not ok:
        if need is not None:
            need(False,code)
        raise SourceFieldsBlocked(code)

def settings(source,keys,*,need=None,duplicate_prefix=None):
    """Extract listed original top-level source fields, preserving values.

    Optional duplicate check retains the v104 exact diagnostic string.
    The caller separately enforces source-specific missing/identity rules.
    """
    result={}
    for line in source.splitlines():
        key,sep,value=line.partition("=")
        if sep and key in keys:
            if duplicate_prefix is not None:
                _need(need,key not in result,duplicate_prefix+key)
            result[key]=value
    return result

def matching_lines(source,prefix):
    """Return original ordered SimC statements verbatim (incl. actions+=)."""
    return [line for line in source.splitlines() if line.startswith(prefix)]

def equipment(source,slots,*,need=None,duplicate_prefix,
              missing_id_prefix,include_gem_enchant=False):
    """Read declared source gear IDs in original slot order.

    - v082/v083/v084: original regex id= search within the gear value.
    - v104: original comma-field parser, which also retains gem/enchant.
    Output IDs must still be checked against exact 15/16 slots and source
    weapon IDs by the calling adapter.
    """
    ids={}
    mods={}
    allowed=set(slots)
    for line in source.splitlines():
        if line.startswith("# Gear Summary"):
            break
        slot,sep,value=line.partition("=")
        if not sep or slot not in allowed:
            continue
        _need(need,slot not in ids,duplicate_prefix+slot)
        if include_gem_enchant:
            fields=value.split(",")
            identifiers=[x[3:] for x in fields[1:] if x.startswith("id=")]
            good=(len(identifiers)==1 and identifiers[0].isdigit())
            _need(need,good,missing_id_prefix+slot)
            ids[slot]=int(identifiers[0])
            mods[slot]={}
            for field in fields[1:]:
                k,_,v=field.partition("=")
                if k in ("gem_id","enchant","enchant_id") and v:
                    mods[slot][k]=v
        else:
            found=re.search(r"(?:^|,)id=(\d+)(?:,|$)",value)
            _need(need,found is not None,missing_id_prefix+slot)
            ids[slot]=int(found.group(1))
    return ids,mods
