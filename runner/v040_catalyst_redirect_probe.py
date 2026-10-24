#!/usr/bin/env python3
"""Bounded v040 native test of 12.1 catalyst: tier item ID + original-item stat redirection.

Two 334-ilvl diagnostic variants, never to be treated as an item recommendation,
user selection, gear budget calibration, or global CHMV optimization. The optional
bonus 13846 has published upstream SimC usage; its 334-ilvl meaning is *unproven*
until native output validates it. Original v032/v039 modules are unchanged.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

import pilot
import v039_venomkeeper_bare_probe as prior

TIER_HEAD = 271564
ORIGINAL_SPECIAL_HEAD = 271874
ITEM_ILVL = 334
BIN_SHA = prior.PINNED_BIN_SHA256
SOURCE_REV = '7bc10711b5'
RUNE_BUFF = 'rune_of_critical_power'
TIER_BUFF = 'cumulative_power'
PROC_BUFF = 'venomcursed_mastery'
PROC_SPELL = 1307922
MAGE_GLOVES = 'hands=v020_hands_268243,id=268243,ilevel=334,source=local'
UPSTREAM_344_HEAD = ('head=crown_of_the_primal_leywarden,id=271564,'
                     'bonus_id=13335/13668/13846/13848,ilevel=344,'
                     'gem_id=240983,enchant_id=7961,redirected_base_stats=271874')
VARIANTS = {
    'minimal_334': 'head=crown_of_the_primal_leywarden,id=271564,ilevel=334,source=local,redirected_base_stats=271874',
    # 13846 is independently present in official Priest/Mage MID2 catalyzed profiles.
    # This use at ilevel334 is a *trial*, not attested live-game bonus assignment.
    'bonus_13846_334': 'head=crown_of_the_primal_leywarden,id=271564,ilevel=334,source=local,bonus_id=13846,redirected_base_stats=271874',
}
SCHEMA = 'v040_catalyst_same_slot_native_v1'

class Refused(ValueError):
    pass

def require(value: bool, code: str):
    if not value:
        raise Refused(code)

def digest(buf: bytes) -> str:
    return hashlib.sha256(buf).hexdigest()

def make_profile(baseline: str, variant: str, out_json: pathlib.Path) -> str:
    require(variant in VARIANTS, 'UNAUTHORIZED_VARIANT')
    require(baseline.count(prior.EXACT_OLD_HEAD) == 1, 'BASELINE_HEAD_CHANGED')
    require(baseline.count(MAGE_GLOVES) == 1, 'BASELINE_GLOVES_CHANGED')
    require(baseline.count(prior.HASTE_RUNE) == 1, 'BASELINE_RUNE_CHANGED')
    require(baseline.count('json2=') == 0, 'BASELINE_OUTPUT_ALREADY_PRESENT')
    source = baseline.replace(prior.EXACT_OLD_HEAD, VARIANTS[variant]).replace(prior.HASTE_RUNE, prior.CRIT_RUNE)
    lines = ['iterations=60' if x.startswith('iterations=') else x for x in source.splitlines()]
    require(sum(x.startswith('head=') for x in lines) == 1, 'MULTIPLE_HEAD_ITEMS')
    require(sum(x.startswith('hands=') for x in lines) == 1, 'MULTIPLE_HAND_ITEMS')
    require(sum(x.startswith('iterations=') for x in lines) == 1, 'ITERATIONS_NOT_FIXED')
    require(MAGE_GLOVES in lines, 'GLOVES_MUST_REMAIN_NON_TIER')
    require(prior.CRIT_RUNE in lines and prior.HASTE_RUNE not in lines, 'CRIT_RUNE_REQUIRED')
    head = next(x for x in lines if x.startswith('head='))
    require(head == VARIANTS[variant], 'HEAD_PROVENANCE_CHANGED')
    require('ilevel=334' in head and 'redirected_base_stats=271874' in head, 'REDIRECTED_SOURCE_NOT_FIXED')
    require('gem_id=' not in head and 'enchant' not in head, 'HEAD_MODIFIERS_OUT_OF_SCOPE')
    lines.append('json2=' + str(out_json.resolve()))
    return '\n'.join(lines) + '\n'

def _single_id(raw: str, key: str):
    values = [token.split('=', 1)[1] for token in raw.split(',') if token.startswith(key + '=')]
    require(all(re.fullmatch(r'\d+', x) for x in values), 'ENCODED_' + key.upper() + '_NOT_NUMERIC')
    require(len(values) == 1, 'ENCODED_' + key.upper() + '_NOT_UNIQUE')
    return int(values[0])

def inspect_json2(payload: bytes, variant: str) -> dict:
    require(variant in VARIANTS, 'UNKNOWN_VARIANT')
    obj = json.loads(payload)
    require(obj.get('report_version') == '2.0.0', 'NOT_JSON2')
    require(str(obj.get('git_revision', '')).startswith(SOURCE_REV), 'SIMC_REVISION_CHANGED')
    chars = (obj.get('sim') or {}).get('players') or []
    require(len(chars) == 1, 'INVALID_PLAYER_COUNT')
    ch = chars[0]
    require(ch.get('specialization') == 'Arcane Mage' and ch.get('race') == 'dwarf', 'SPEC_RACE_CHANGED')
    gear = ch.get('gear') or {}
    head = gear.get('head') or {}
    require(head.get('ilevel') == ITEM_ILVL, 'HEAD_ILEVEL_CHANGED')
    encoded = head.get('encoded_item', '')
    require(_single_id(encoded, 'id') == TIER_HEAD, 'HEAD_NO_LONGER_TIER_ITEM')
    require(_single_id(encoded, 'redirected_base_stats') == ORIGINAL_SPECIAL_HEAD, 'REDIRECT_ID_MISSING')
    if variant == 'minimal_334':
        require('bonus_id=' not in encoded, 'MINIMAL_PROFILE_HAS_BONUSES')
    else:
        require('bonus_id=13846' in encoded, 'BENEFIT_BONUS_NOT_RETAINED')
    require('gem_id=' not in encoded and 'enchant_id=' not in encoded, 'HEAD_UNEXPECTED_MODIFIERS')
    for k in ('crit_rating', 'haste_rating', 'versatility_rating'):
        require(int(head.get(k, 0)) == 0, 'REDIRECT_STATIC_WRONG:' + k)
    # Fixed floor 201 was already independently obtained from an unmodified bare ID 271874 at level334.
    require(int(head.get('mastery_rating', 0)) == 201, 'REDIRECT_MASTERY_NOT_EQUAL_BARE_201')
    require(_single_id(gear.get('hands', {}).get('encoded_item', ''), 'id') == 268243,
            'NON_TIER_GLOVES_WERE_REPLACED')
    for slot, id_ in [('shoulders', 271562), ('chest', 271567), ('legs', 271563)]:
        require(_single_id(gear.get(slot, {}).get('encoded_item', ''), 'id') == id_, 'OTHER_TIER_PIECE_CHANGED:' + slot)
    buffs = {b.get('name'): b for b in ch.get('buffs', [])}
    require(RUNE_BUFF in buffs and 'rune_of_burning_haste' not in buffs, 'WRONG_RUNE')
    require(TIER_BUFF in buffs, 'NO_TIER_4PC_NATIVE_BUFF')
    proc = buffs.get(PROC_BUFF)
    proc_active = proc is not None and proc.get('spell') == PROC_SPELL and (proc.get('start_count') or 0) > 0
    evidence = {
        'variant': variant,
        'tier_item_id': TIER_HEAD,
        'original_special_item_id': ORIGINAL_SPECIAL_HEAD,
        'ilevel': ITEM_ILVL,
        'observed_bare_secondary': {k: int(head.get(k, 0)) for k in ['crit_rating', 'haste_rating', 'mastery_rating', 'versatility_rating']},
        'tier4_buff_observed': True,
        'crit_rune_observed': True,
        'proc_buff_observed_and_triggered': bool(proc_active),
        'proc_spell_id_observed': proc.get('spell') if proc is not None else None,
        'proc_start_count': proc.get('start_count') if proc is not None else None,
        'proc_uptime_pct': proc.get('uptime') if proc is not None else None,
        'native_json2_sha256': digest(payload),
        'dps_not_comparable': True,
        'bonus_ilevel334_game_provenance_attested': False,
        'effect_dynamic_rating_magnitudes_validated': False,
        'item_user_selected': False,
        'no_global_optimum_claim': True,
    }
    return evidence

def run(binary: pathlib.Path, output: pathlib.Path) -> int:
    output.mkdir(parents=True, exist_ok=True)
    record = {
        'schema': SCHEMA, 'status': 'BLOCKED', 'native_simc_attempted': 0,
        'max_native_simc_calls': 2, 'test_only': True,
        'source_profile_ilevel': 334, 'official_control_ilevel': 344,
        'not_a_user_gear_selection': True, 'main_workflow_unchanged': True,
        'dps_comparison_authorized': False, 'real_game_bonus_334_attested': False,
        'full_special_effect_stat_deltas_confirmed': False,
        'cache_kind': 'PINNED_BINARY_ONLY',
        'variants': [],
    }
    try:
        require(binary.is_file(), 'PINNED_BINARY_NOT_FOUND')
        require(digest(binary.read_bytes()) == BIN_SHA, 'PINNED_BINARY_HASH_MISMATCH')
        source, fixture = pilot.source()
        prior.verify_preconditions(source, binary)
        record['reference_input_sha256'] = fixture['portable_input_sha256']
        record['pinned_simc_binary_sha256'] = BIN_SHA
        for variant in ('minimal_334', 'bonus_13846_334'):
            case_dir = output / variant
            case_dir.mkdir(parents=True, exist_ok=True)
            simc_input = (case_dir / 'input.simc').resolve()
            simc_output = (case_dir / 'result.json').resolve()
            simc_input.write_text(make_profile(source, variant, simc_output), encoding='utf-8')
            case = {'variant': variant, 'input_sha256': digest(simc_input.read_bytes()), 'status': 'STARTED'}
            record['variants'].append(case)
            record['native_simc_attempted'] += 1
            (output / 'V040_PROGRESS_RECEIPT.json').write_text(json.dumps(record, indent=2) + '\n')
            p = subprocess.run([str(binary), str(simc_input)], cwd=binary.parent,
                               stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, timeout=100)
            (case_dir / 'stdout.txt').write_text(p.stdout)
            (case_dir / 'stderr.txt').write_text(p.stderr)
            case['exit_code'] = p.returncode
            require(p.returncode == 0, 'NATIVE_SIMC_EXIT_' + str(p.returncode))
            require(simc_output.is_file() and simc_output.stat().st_size > 1000, 'RESULT_JSON2_MISSING')
            case['native'] = inspect_json2(simc_output.read_bytes(), variant)
            case['status'] = 'PASS_STATIC_AND_4PC' if not case['native']['proc_buff_observed_and_triggered'] else 'PASS_STATIC_AND_4PC_AND_PROC'
        both = record['variants']
        record['both_native_static_and_tier_verified'] = all(x['status'].startswith('PASS_') for x in both)
        record['any_proc_preserved_334'] = any(x['native']['proc_buff_observed_and_triggered'] for x in both)
        record['status'] = ('PASS_334_REDIRECT_STATIC_TIER_AND_PROC_OBSERVED_NOT_FULL_EFFECT'
                            if record['any_proc_preserved_334']
                            else 'PARTIAL_334_REDIRECT_STATIC_TIER_ONLY_PROC_UNVERIFIED')
    except Exception as e:
        record['status'] = 'BLOCKED'
        record['error'] = type(e).__name__ + ': ' + str(e)
    (output / 'V040_NATIVE_RECEIPT.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print('V040_RESULT', record['status'], 'native_calls', record['native_simc_attempted'], flush=True)
    return 0 if record['status'].startswith(('PASS_', 'PARTIAL_')) else 3

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--binary', type=pathlib.Path, required=True)
    p.add_argument('--output', type=pathlib.Path, required=True)
    a = p.parse_args()
    sys.exit(run(a.binary.resolve(), a.output.resolve()))
