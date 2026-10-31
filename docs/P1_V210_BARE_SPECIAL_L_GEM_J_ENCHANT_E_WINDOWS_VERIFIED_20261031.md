# P1 v210 — selected special base L distinct from gem J / enchant E (2026-10-31)

## Why this change exists

The P1 v208/v209 path measured exact selected-special native static L but
blocked a user-selected special if the internally generated representative
item carried gem/enchant options. In particular, shaman/elemental ilvl331
neck item 268250 had the legitimate source-gemmed option
`gem_id=240900/240900`, and old v062 rightly blocked incorrectly locking
the whole decorated static item as L.

Current v210 changes **stat provenance, not SimC effects, optimizer, or user
gear selection**:

1. v098 generates the full actual user representative profile, with gems,
   enchant, tier, trinkets, consumables, oil, class talents and scenario.
2. For each **selected special** (including tagged catalyst special-tier
   items), v062 defines the exact **bare** item identity by removing ONLY
   `gem_id`, `enchant`, `enchant_id` while preserving the same
   season/item_id/ilevel/slot and all intrinsic options (`bonus_id`,
   `redirected_base_stats`, `context`, `content_tuning`, etc).
   An existing decorated record is **never** substituted for a missing
   bare record. Unobserved base L never becomes 0.
3. On an explicit user Start, v208 composes one temporary physical Native
   profile from the original v098 full profile, replaces **only still
   missing selected special slots** with their exact undecorated variants,
   checks original item identity and SimC local-source input, and parses
   only those exact slot records through existing v046 Native JSON2.
   One Native can serve multiple selected specials in the same user source.
   The immutable static cache snapshot stores the **bare identity**.
4. v062 builds fixed per-stat L and G from the Native-observed bare variant;
   J/E are not locked as L nor added again to the reference B/T. The original
   full gear identity stays in `native_gear_stats.identity` for unchanged
   strict v064 profile matching, while
   `native_gear_stats.numeric_source_identity` links to bare L evidence.
   The existing `v094` adaptive simulator and user profile retain the full
   original gem/enchant inputs. **This is not a new SimC effect evaluator.**
5. Other unselected nontrinket gear and static trinket policy are unchanged.
   v208 still never runs a Native in Plan, only on Start when an exact bare
   selected special record is missing, and never overwrites the previous
   static cache or old sealed sessions.

## Exact verification and evidence

- [Ubuntu + Windows v210 focused #41152031433](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41152031433)
  **127 PASS / 0 FAIL on each OS, 0 new Native**. This covers exact
  bare-vs-decorated record selection, old v062 fixture paths including
  catalyst tier, source-gemmed neck physical input, cache reuse,
  original HTTP plan/start, session identity, nonCHMV enchant option,
  unchanged user UI and full v098 profile binding.
- Existing v098 regression after profile-vs-numeric identity separation
  [#41151976759](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41151976759):
  SUCCESS. Initial transition runs #41151823432, #41151877886,
  #41151912296 and #41151964967 **failed** while the numeric source and
  actual equipped profile identity were accidentally conflated.
  These failures remain historical and were corrected by retaining
  `identity=full equipped`, `numeric_source_identity=bare`.
- [Real SHA-pinned Windows v210 #41152171198](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41152171198):
  SUCCESS, job `124390957066`, original source commit
  `4ee7842846ae50b340f6f5c2df6b127691beb4a0`.
  **One** sample: elemental shaman ilvl331, source-listed special neck
  item `268250`. Actual DPS profile kept
  `gem_id=240900/240900`, while the physical L Native queried exactly
  `{season:midnight_s2,item_id:268250,ilevel:331,slot:neck,options:{}}`.
  Native-observed fixed **L={crit:93,haste:305,mastery:0,vers:0}**.
  **Static Native1 + DPS Native6 + 6/6 verified cache replay**,
  extra static/DPS Native0. Automatic reference **B3110,T3142**;
  observed first-choice DPS `202301.8300481545`,
  SimC SEM `346.17525001684186`; confidence **95%**,
  **global optimum not proven**. Never claim this is a paired 95% DPS
  improvement over the ungemmed v209 cloak setup.
- Original v210 small GitHub artifact #`13023806394` ZIP SHA
  `43b384800b74918eea6ad71569537ad66c84d53b0f56aecc5c0869d3f0666cf4`
  was downloaded and inspected. Full static Native JSON2 SHA and six
  original DPS case SHA, official SimC exe SHA and sampled item identities
  are preserved without exposing full profile bytes in
  [v210 successor JSON](V210_WINDOWS_GEMMED_SPECIAL_BARE_L_REAL_NATIVE_SUCCESSOR_20261031.json).

## Still not claimed

This one real sample is **not** blanket native proof for every special
equipment ID, every catalyst/source/bonus, all 26 DPS specs, all enchant
families or Windows GUI mouse clicks. Dedicated SimC effects/procs belong to
SimC. Other permanent static rating enchant E applied to the same selected
special has not been separately admitted as a general UI feature by v202.
No full-season new item collection, manual-filler user requirement, 26-wide
Native replay, main merge, v003 modification, original v016 integration,
Project UI installation or Work OS authority change.

**Next P1:** keep v210 as shared product path; add small tests only for
previously unobserved intrinsic option/bonus/catalyst combinations if a real
user choice fails. Separately, P2 source-import SimC details for the remaining
37 season enchants without rebuilding proc mechanics or repeating the full
26×38 Native matrix.
