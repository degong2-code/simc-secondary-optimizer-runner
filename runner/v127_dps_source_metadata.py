#!/usr/bin/env python3
"""v127 source-backed DPS metadata registry — data, never a DPS engine.

Source-pinned archetypes (six prior, expanding only with exact evidence); not a gear DB or a claim of
coverage for the other 21 DPS specs. All effects/APL/DPS remain in SimC.
Source-specific fixture PRODUCERS are legacy adapters until source parsing
can be unified without changing the pinned source or existing Native bytes.
"""
from __future__ import annotations
from dataclasses import dataclass
import re

import v103_source_observed_weapon_types as observed

SCHEMA="v127_source_backed_dps_archetype_metadata_v1"
STAT_KEYS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
TIER_SLOTS=("head","shoulders","chest","hands","legs")

@dataclass(frozen=True)
class Archetype:
    character_class: str
    spec: str
    armor_family: str
    source_fixture: str
    source_git_blob: str
    producer_id: str
    weapon_form: str
    tier_five: tuple[tuple[str,int], ...]
    fifth_ordinary: tuple[str,int]
    flask_F: tuple[int,int,int,int]

    @property
    def key(self):
        return self.character_class,self.spec

    def tier_ids(self):
        return dict(self.tier_five)

    def fifth_replacement(self):
        slot,ordinary=self.fifth_ordinary
        return slot,self.tier_ids()[slot],ordinary

    def flask_vector(self):
        return dict(zip(STAT_KEYS,self.flask_F))

# Every ID/source below was already pinned by v082/v083/v084/v086/v104/v103.
# Moving this data must not change historical source/profile/Native receipts.
SOURCE_BACKED=(
    Archetype("warrior","fury","plate",
       "v082_upstream_mid2_warrior_fury_reference.simc",
       "3225992ed5b754ad5d61e8b785d9d859f1eed1be",
       "v082_fury","dual_two_hand",
       (("head",271456),("shoulders",271454),("chest",271459),
        ("hands",271457),("legs",271455)),
       ("legs",271878),(0,165,0,0)),
    Archetype("paladin","retribution","plate",
       "v083_upstream_mid2_paladin_retribution_reference.simc",
       "864e857c5d8cdbaa5b03939f077fcb657a4784aa",
       "v083_retribution","single_two_hand",
       (("head",271465),("shoulders",271463),("chest",271468),
        ("hands",271466),("legs",271464)),
       ("legs",271878),(0,165,0,0)),
    Archetype("mage","frost","cloth",
       "v084_upstream_mid2_mage_frost_reference.simc",
       "b787824a95020a7cdd0934ed5e004695726db138",
       "v084_frost","one_hand_frill",
       (("head",271564),("shoulders",271562),("chest",271567),
        ("hands",271565),("legs",271563)),
       ("head",271874),(165,0,0,0)),
    Archetype("hunter","beast_mastery","mail",
       "v079_upstream_mid2_hunter_beast_mastery_reference.simc",
       "fd9399a7ee0c9c39a362ba31a0d8308e3e000490",
       "v086_fixed_mail","ranged",
       (("head",271492),("shoulders",271490),("chest",271495),
        ("hands",271493),("legs",271491)),
       ("head",249317),(0,165,0,0)),
    Archetype("rogue","outlaw","leather",
       "v131_upstream_mid2_rogue_outlaw_reference.simc",
       "738f7fe64c1d75159b86ecc2e8064dc29c69c203",
       "v104_shared","dual_one_hand",
       (("head",271510),("shoulders",271508),("chest",271513),
        ("hands",271511),("legs",271509)),
       ("chest",251159),(165,0,0,0)),
    Archetype("rogue","subtlety","leather",
       "v068_upstream_mid2_rogue_subtlety_reference.simc",
       "b704e6326959432a82d14a6b774c79183d5b2af4",
       "v104_shared","dual_one_hand",
       (("head",271510),("shoulders",271508),("chest",271513),
        ("hands",271511),("legs",271509)),
       ("chest",251159),(165,0,0,0)),
    Archetype("shaman","elemental","mail",
       "v078_upstream_mid2_shaman_elemental_reference.simc",
       "c92d111e37bd684647e4637dcfef3ccb92864cde",
       "v104_shared","one_hand_shield",
       (("head",271483),("shoulders",271481),("chest",271486),
        ("hands",271484),("legs",271482)),
       ("head",249317),(165,0,0,0))
)
BY_SPEC={entry.key:entry for entry in SOURCE_BACKED}

class SourceMetadataBlocked(ValueError):pass

def need(value,reason):
    if not value:raise SourceMetadataBlocked(reason)

def validate():
    """Strict read-only source scope: no invented 27-spec coverage."""
    need(len(SOURCE_BACKED)==len(BY_SPEC) and len(SOURCE_BACKED)>=6 and
         set(BY_SPEC)==set(observed.EXECUTABLE_SOURCES),
         "REGISTERED_SOURCE_SPEC_SCOPE_DRIFT")
    for entry in SOURCE_BACKED:
        key=entry.key
        tier=entry.tier_ids()
        filename,sha,form=observed.SOURCE[key]
        need(type(entry.source_fixture) is str
             and entry.source_fixture==filename.rsplit("/",1)[-1]
             and entry.source_git_blob==sha
             and re.fullmatch("[0-9a-f]{40}",sha) is not None,
             "REGISTERED_SOURCE_PROVENANCE_DRIFT:"+"/".join(key))
        need(entry.weapon_form==form and
             set(observed.OBSERVED[key])==set(observed.SLOTS_FOR_FORM[form]),
             "REGISTERED_WEAPON_SOURCE_DRIFT:"+"/".join(key))
        need(len(entry.tier_five)==5 and set(tier)==set(TIER_SLOTS)
             and len(set(tier.values()))==5 and
             all(type(i) is int and i>0 for i in tier.values()),
             "REGISTERED_FIVE_TIER_NOT_SOURCE_BACKED:"+"/".join(key))
        slot,tier_id,ordinary_id=entry.fifth_replacement()
        need(slot in tier and tier_id==tier[slot]
             and type(ordinary_id) is int and ordinary_id>0,
             "REGISTERED_FIFTH_ORDINARY_NOT_PINNED:"+"/".join(key))
        need(type(entry.flask_F) is tuple and
             len(entry.flask_F)==4 and
             all(type(x) is int and x>=0 for x in entry.flask_F)
             and sum(entry.flask_F)==165,
             "REGISTERED_FLASK_STATIC_F_DRIFT:"+"/".join(key))
    return True

def get(key):
    need(key in BY_SPEC,"REGISTERED_ARCHETYPE_NOT_SOURCE_BACKED")
    return BY_SPEC[key]
