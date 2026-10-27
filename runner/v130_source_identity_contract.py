#!/usr/bin/env python3
"""P1 common, source-pinned SimC identity/APL/talent read-only contract.

All six supported inputs are exact source fixtures; this is not a class/spec
inference engine. Keep source-specific validation errors/thresholds unchanged.
Weapon, tier/fifth, APL mechanics, item effects and DPS remain elsewhere.
"""
from __future__ import annotations
import hashlib
import v127_dps_source_metadata as registry
import v129_common_source_fields as fields

class SourceIdentityBlocked(ValueError):
    pass

def need(ok,reason):
    if not ok:
        raise SourceIdentityBlocked(reason)

def git_blob(source):
    raw=source.encode("utf8")
    return hashlib.sha1(
        b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw
    ).hexdigest()

def verify(source,key,expected_blob,markers,*,min_actions,
           strict_greater=False,hash_error,identity_error,apl_error,
           talents_error=None,fail=None):
    """Validate strict SHA/identity and original APL, talents if requested.

    Returns verbatim original action statements and talent string values.
    An exact Git blob is independently checked against the typed registry.
    Never synthesize talent, APL or arbitrary item IDs.
    """
    gate=fail or need
    gate(registry.get(key).source_git_blob==expected_blob,
         "SOURCE_IDENTITY_REGISTRY_SHA_DRIFT:"+"/".join(key))
    gate(git_blob(source)==expected_blob,hash_error)
    gate(all(part in source for part in markers),identity_error)
    actions=fields.matching_lines(source,"actions")
    count_ok=(len(actions)>min_actions if strict_greater
              else len(actions)>=min_actions)
    gate(count_ok and sum(a.startswith("actions=") for a in actions)==1,
         apl_error)
    talents=[line.partition("=")[2] for line in
             fields.matching_lines(source,"talents=")]
    if talents_error is not None:
        gate(len(talents)==1,talents_error)
    return actions,talents
