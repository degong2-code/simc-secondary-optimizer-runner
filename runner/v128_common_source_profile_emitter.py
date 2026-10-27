#!/usr/bin/env python3
"""Byte-preserving SimC source-to-representative-profile line emitter (P1).

The sole owner of source-line filtering and runtime/gear serialization for
six current, source-backed DPS inputs. v127 holds metadata; the existing
source adapters still validate APL, exact items/weapon types and options.
This module never calls Native, touches files or models item effects.
"""
from __future__ import annotations
import v055_simc_item_selection as items

class SourceEmissionBlocked(ValueError):
    pass

def emit(source,overrides,rows,slot_order,*,blank_before_overrides,
         need=None,check_duplicate_overrides=False):
    """Emit exactly the previous v082/v083/v084/v104 layouts.

    blank_before_overrides=True: v082/v083/v084 preserve one explicit
    separator before runtime settings. False: v104 historically emits
    immediately after its source pre-gear lines. In both layouts, source
    line order, user/SimC APL and original comments remain untouched.
    """
    if not (type(source) is str and type(overrides) is dict
            and type(rows) is dict and
            type(slot_order) in (list,tuple) and
            type(blank_before_overrides) is bool and
            set(slot_order)==set(rows) and
            len(slot_order)==len(rows) and
            all(type(k) is str and type(v) is str
                for k,v in overrides.items())):
        raise SourceEmissionBlocked("INVALID_SOURCE_EMISSION_CONTRACT")
    if need is None:
        def need(ok,why):
            if not ok:raise SourceEmissionBlocked(why)
    result=[]
    seen=set()
    allowed_slots=set(slot_order)
    for line in source.splitlines():
        if line.startswith("# Gear Summary"):
            break
        key,sep,_=line.partition("=")
        if sep and not line.startswith("#") and key in overrides:
            if check_duplicate_overrides:
                need(key not in seen,"DUPLICATE_SOURCE_OVERRIDE:"+key)
                seen.add(key)
            continue
        if sep and key in allowed_slots|{"temporary_enchant"}:
            continue
        result.append(line)
    if blank_before_overrides:
        result.append("")
    result.extend(key+"="+value for key,value in overrides.items())
    result.extend(items.equipment_line(slot,rows[slot]["item_id"],
                      rows[slot]["ilevel"],rows[slot]["options"])
                  for slot in slot_order)
    return "\n".join(result).rstrip()+"\n"
