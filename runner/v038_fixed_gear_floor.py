#!/usr/bin/env python3
"""v038: conservative selected-special-equipment CHMV fixed-floor admission.

No gear optimization, no new item DB and no assumption that ordinary or crafted
item stats are locked. Does NOT make a player-choice authority out of a JSON2.
For real use, the selected-special-item list and clean, independently attested
SimC item provenance must be provided. Fail closed on missing evidence.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pathlib
import re
import sys
from dataclasses import dataclass

STATS = ('crit_rating', 'haste_rating', 'mastery_rating', 'versatility_rating')
OIL = (16, 16, 0, 0)  # v037 pinned scenario only; not a universal oil policy
PINNED_SIMC = '7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd'
PINNED_BINARY = '64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e'
TRINKET_SLOTS = frozenset(('trinket1', 'trinket2'))
EXCLUDED_ITEM_OPTIONS = frozenset(('gem_id', 'enchant', 'crafted_stats', 'bonus_id', 'socket'))


class AdmissionBlocked(ValueError):
    pass


def require(value, reason):
    if not value:
        raise AdmissionBlocked(reason)


def vector(value, name):
    require(type(value) is dict and set(value) == set(STATS), name + '_KEYS_INVALID')
    require(all(type(value[k]) is int and 0 <= value[k] <= 100000 for k in STATS), name + '_VALUES_INVALID')
    return tuple(value[k] for k in STATS)


def objvec(value):
    return dict(zip(STATS, value))


def source_sha(blob: bytes):
    return hashlib.sha256(blob).hexdigest()


def _identity(encoded):
    require(type(encoded) is str, 'ENCODED_ITEM_MISSING')
    ids = re.findall(r'(?:^|,)id=(\d+)(?:,|$)', encoded)
    require(len(ids) == 1, 'AMBIGUOUS_ITEM_ID')
    tokens = encoded.split(',')
    for token in tokens:
        option = token.split('=', 1)[0].strip().lower()
        require(option not in EXCLUDED_ITEM_OPTIONS, 'BARE_ITEM_NOT_ISOLATED:' + option)
    return int(ids[0])


def bare_item_stats(native_json_bytes: bytes, native_sha: str, selected: dict):
    """Extract *bare* item stats; never infer special-effect classification.

    Must be a separately attested, zero-enchant/zero-gem/zero-crafted-stats
    native item capture; sample v037 combat JSON2 is NOT such evidence.
    """
    require(type(native_json_bytes) is bytes, 'NATIVE_BYTES_REQUIRED')
    require(type(native_sha) is str and re.fullmatch('[0-9a-f]{64}', native_sha), 'EVIDENCE_DIGEST_INVALID')
    require(source_sha(native_json_bytes) == native_sha, 'NATIVE_EVIDENCE_SHA_CHANGED')
    doc = json.loads(native_json_bytes)
    require(doc.get('report_version') == '2.0.0', 'NATIVE_REPORT_VERSION_CHANGED')
    require(str(doc.get('git_revision', '')).startswith(PINNED_SIMC[:10]), 'NATIVE_SIMC_COMMIT_CHANGED')
    players = (doc.get('sim') or {}).get('players') or []
    require(len(players) == 1, 'NATIVE_PLAYER_CARDINALITY')
    gear = players[0].get('gear') or {}
    slot = selected['slot']
    require(slot not in TRINKET_SLOTS and slot in gear, 'NOT_ELIGIBLE_NONTRINKET_SLOT')
    item = gear[slot]
    require(_identity(item.get('encoded_item')) == selected['item_id'], 'SELECTED_ITEM_ID_MISMATCH')
    require(item.get('ilevel') == selected['ilevel'], 'SELECTED_ITEM_LEVEL_MISMATCH')
    # The native gear object can include modifiers absent from encoded_item in
    # future JSON2 schemas. Do not silently treat them as innate stats.
    require(not any(x in item for x in ('gems', 'enchants', 'crafted_stats', 'socket_bonus')),
            'BARE_ITEM_NATIVE_MODIFIER_PRESENT')
    stats = {}
    for k in STATS:
        value = item.get(k, 0)
        require(type(value) is int and 0 <= value <= 100000, 'NATIVE_ITEM_STAT_INVALID:' + k)
        stats[k] = value
    require(sum(stats.values()) > 0, 'NATIVE_ITEM_HAS_NO_SECONDARY')
    return stats


def selected_item_contract(spec):
    require(type(spec) is dict and set(spec) == {'slot', 'item_id', 'ilevel', 'selection_provenance', 'native_json_sha256', 'effect_classification'}, 'ITEM_CONTRACT_SHAPE')
    require(type(spec['slot']) is str and spec['slot'] not in TRINKET_SLOTS, 'TRINKETS_ARE_EXTERNAL')
    require(type(spec['item_id']) is int and spec['item_id'] > 0, 'INVALID_ITEM_ID')
    require(type(spec['ilevel']) is int and 1 <= spec['ilevel'] <= 1000, 'INVALID_ILEVEL')
    require(spec['effect_classification'] == 'SELECTED_SPECIAL_NONTRINKET_MANUALLY_REVIEWED', 'ITEM_NOT_REVIEWED_SPECIAL')
    require(spec['selection_provenance'] == 'USER_SELECTED_ITEM_EXPLICITLY', 'ITEM_SELECTION_NOT_ATTESTED')
    require(type(spec['native_json_sha256']) is str and re.fullmatch('[0-9a-f]{64}', spec['native_json_sha256']), 'EVIDENCE_SHA_REQUIRED')
    return spec


def collect_verified_floor(items, evidence_by_sha):
    require(type(items) is list and len(items) >= 1 and len(items) <= 8, 'VERIFIED_SELECTION_REQUIRED')
    require(type(evidence_by_sha) is dict, 'NATIVE_EVIDENCE_STORE_REQUIRED')
    total = [0, 0, 0, 0]
    seen_slots, seen_items = set(), set()
    records = []
    for raw in items:
        s = selected_item_contract(raw)
        require(s['slot'] not in seen_slots and s['item_id'] not in seen_items, 'DUPLICATE_SELECTED_ITEM')
        seen_slots.add(s['slot']); seen_items.add(s['item_id'])
        digest = s['native_json_sha256']
        require(digest in evidence_by_sha, 'MISSING_INDEPENDENT_BARE_ITEM_JSON2')
        entry = bare_item_stats(evidence_by_sha[digest], digest, s)
        for i,k in enumerate(STATS): total[i] += entry[k]
        records.append({'slot':s['slot'], 'item_id':s['item_id'], 'ilevel':s['ilevel'], 'native_bare_secondary':entry, 'native_json_sha256':digest})
    return {'schema':'v038_native_special_item_floor_v1',
            'status':'BARE_ITEM_SECONDARIES_EXTRACTED_FROM_DECLARED_SELECTION',
            'special_fixed_rating':objvec(total), 'selected_item_count':len(records),
            'items':records, 'selection_is_external_contract_not_inferred_from_json2':True,
            'actual_user_selection_independently_verified_by_tool':False,
            'nonstat_item_effects_verified':False,
            'real_product_authority_promoted':False}


def enforce_constraints(manual_total, manual_minimum, special_locked):
    """No double count: L is already IN the manual total, oil also IN total.

    E (trinkets and enchantments) is intentionally excluded. c >= L + oil,
    and manual candidate floor is independent: c >= manual minimum.
    """
    require(type(manual_total) is int and 2500 <= manual_total <= 4000, 'MANUAL_TOTAL_UNSUPPORTED')
    manual = vector(manual_minimum, 'MANUAL_MINIMUM')
    locked = vector(special_locked, 'SPECIAL_LOCK')
    floor = tuple(max(manual[i], OIL[i] + locked[i]) for i in range(4))
    cap = manual_total // 2
    require(all(f <= cap for f in floor), 'FIXED_FLOOR_EXCEEDS_50PCT_CAP')
    require(sum(floor) <= manual_total, 'FIXED_FLOOR_EXCEEDS_TOTAL')
    require(sum(OIL) + sum(locked) <= manual_total, 'SPECIAL_FLOOR_DOUBLE_COUNT_OR_EXCESS')
    return {'schema':'v038_candidate_fixed_floor_v1',
            'target_total_rating':manual_total, 'manual_minimum':objvec(manual),
            'special_item_locked_in_total':objvec(locked), 'oil_already_in_total':objvec(OIL),
            'effective_candidate_minimum':objvec(floor),
            'free_rating_after_fixed_special_and_oil':manual_total-sum(locked)-sum(OIL),
            'external_trinket_enchant_rating_added_to_total':False,
            'no_double_count_of_locked_stats':True,
            'stat_limit_is_pilot_50pct':True}


def check_candidate(vec, contract):
    require(type(vec) in (list,tuple) and len(vec)==4 and all(type(x) is int for x in vec), 'CANDIDATE_INVALID')
    floor = vector(contract['effective_candidate_minimum'], 'EFFECTIVE_MINIMUM')
    require(sum(vec) == contract['target_total_rating'], 'CHMV_TOTAL_MISMATCH')
    require(all(floor[i]<=vec[i]<=contract['target_total_rating']//2 for i in range(4)), 'LOCKED_FLOOR_OR_CAP_BREACH')
    return True


def pinned_native_result(doc, candidate, contract):
    """Only confirms candidate final vector, not selected item effects."""
    require(doc.get('report_version')=='2.0.0' and str(doc.get('git_revision','')).startswith(PINNED_SIMC[:10]), 'JSON2_NATIVE_IDENTITY_CHANGED')
    ps=(doc.get('sim') or {}).get('players') or []
    require(len(ps)==1, 'NATIVE_PLAYER_CARDINALITY')
    observed=(ps[0].get('collected_data') or {}).get('buffed_stats',{}).get('stats',{})
    require(all(type(observed.get(k)) in (int,float) for k in STATS), 'JSON2_STATS_ABSENT')
    values=tuple(int(round(observed[k])) for k in STATS)
    check_candidate(candidate, contract)
    require(values==tuple(candidate), 'NATIVE_FINAL_RATING_MISMATCH')
    return {'status':'PASS_CANDIDATE_CHMV_AND_FLOOR_ONLY','final_rating':objvec(values),
            'special_item_effects_verified':False}


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--request',type=pathlib.Path,required=True)
    ap.add_argument('--evidence-directory',type=pathlib.Path)
    ap.add_argument('--output',type=pathlib.Path,required=True)
    args=ap.parse_args(argv)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    try:
        spec=json.loads(args.request.read_text())
        require(set(spec)=={'schema','manual_total','manual_minimum','selected_special_equipment'}, 'V038_REQUEST_SHAPE')
        require(spec['schema']=='v038_original_selected_special_floor_v1', 'V038_SCHEMA_CHANGED')
        store={}
        if args.evidence_directory and args.evidence_directory.is_dir():
            for path in args.evidence_directory.glob('*.json'):
                blob=path.read_bytes()
                store[source_sha(blob)]=blob
        floor=collect_verified_floor(spec['selected_special_equipment'],store)
        record={'status':'OFFLINE_BARE_ITEM_FLOOR_INSPECTED_NOT_NATIVE_OPTIMIZED',
                'bare_item_evidence':floor,
                'candidate_contract':enforce_constraints(spec['manual_total'],spec['manual_minimum'],floor['special_fixed_rating'])}
        code=0
    except (AdmissionBlocked, ValueError, KeyError, TypeError) as ex:
        record={'status':'BLOCKED','reason':type(ex).__name__+':'+str(ex),
                'native_simc_executed':False,'real_item_fixed_floor_verification_complete':False}
        code=3
    args.output.write_text(json.dumps(record,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print(record['status'],record.get('reason',''))
    return code

if __name__=='__main__':
    raise SystemExit(main())
