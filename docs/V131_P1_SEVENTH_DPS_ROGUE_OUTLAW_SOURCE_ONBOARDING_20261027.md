# P1/v131 — first additional DPS specialization: Rogue Outlaw (source connected, real Native pending)

2026-10-27 · isolated development branch `probe/chat-cache-v035-20261024` only.

## Prior user-verified proof kept intact

The user executed the v130 9-module focused offline Windows suite in `새 폴더 (14)`: `Ran 92 tests in 3.170s / OK`, **92 PASS / 0 FAIL / 0 ERROR**, no real Native. Prior user Windows Native6/6 exists for Retribution Paladin, Subtlety Rogue (old save resumed with 3 verified Native caches + 3 new), and Elemental Shaman (fresh v122 profile); each receipt retains its own actual scope. None should be erased or repeated because of source expansion.

## Actual source discovery

The repo's `integration_probes/fixtures` directory contained six executable pinned spec profile files and one ancillary Mage Fire ordinary-gear witness, **not** the other 21 complete MID2 profiles. Searched the public official `simulationcraft/simc` repo: official `midnight` branch includes `profiles/MID2/MID2_Rogue_Outlaw.simc` among broader MID2 sources. Pinned the **exact byte content at official commit `426ad85ecb1c5d9a1af166931478dabf29b42fdd`**, Git blob **`738f7fe64c1d75159b86ecc2e8064dc29c69c203`**, into `integration_probes/fixtures/v131_upstream_mid2_rogue_outlaw_reference.simc`. Git blob is immutable; never use floating upstream HEAD for runnable source without explicit source update.

Source is a full `rogue/spec=outlaw/race=dwarf/role=attack` Midnight season2 SimC file with original talents, APL, Omnium, two source trinkets, 16 gear slots and 5 same-class tier pieces. Original weapons main-hand **268209 one-hand axe** and offhand **275070 one-hand dagger** are supported by the official source and item-type references (Wowhead main-hand Axe and one-hand Dagger). It is **not** an exhaustive weapon legality database or complete season item catalog.

## Source-backed 7th specialization implementation

- `runner/v103_source_observed_weapon_types.py`: exact Outlaw source filename/SHA and 2 weapon IDs/subtypes, no invented alternative weapon forms; source scope now seven.
- `runner/v127_dps_source_metadata.py`: one immutable Outlaw record for source, shared Rogue tier-five IDs, fifth **ordinary chest251159**, static Fcrit165 from the same source-checked Rogue flask type, and existing `v104_shared` producer. Registry cardinality source-matched, not hardwired to six.
- `runner/v104_shared_pinned_rogue_shaman_composer.py`: v104 shared original source/APL parser+emitter now builds third fixed source type **without new profile factory**. Outlaw source tier chest271513 is replaced by prior exact ordinary chest251159, leaving source-pinned tier head/shoulders/hands/legs four-piece. Prior exact source socket on discarded source wrist244576 contains gem240890; same replacement ordinary wrist268240 has already appeared with a socket in actual user Subtlety Native6/6. Source-vetted `source_socket_on_ordinary` retains only matching Outlaw wrist gem240890 on this precise replacement, not any discarded bonus/crafted/random stats. With neck2+ring2+waist1+wrist1, physical six ordinary gems and four colors are passed through v101 for diamond240967.
- `runner/v108_native_consumable_inputs.py`: include *exact whole Omnium* observed in official Outlaw source `136822:1/136823:1/136817:1/136820:1/136814:1`, without inventing rune combinations/independent effect models.
- Generic v101 gear assembly → v098 source-backed user bootstrap → v122 canonical runtime → existing v096/v094 SimC adaptive candidate engine, same cached identity and 95% only, unchanged. Browser defaults discover new `rogue/outlaw`; UI labels it `도적 · 무법 (Native 시험 전)`. No old user session, binary, or output/cache changes.

## Actual GitHub automated offline evidence

The existing v098 `push` workflow was extended (not a new gate) to check v127-v131 exact source and user plan. Several intermediate commits **failed** on a previously unknown source Omnium preset and stale test assumptions about six specs; those failed historical runs were inspected and corrected rather than misreported PASS. **Actions run #40478518640**, commit `cd94619058e2a56ce4f9b58f1d93411e71e4d3dd`: **SUCCESS; Ran 252 tests in 1.231s / OK; Native 0.** This validates an earlier SHA and related source construction, not later updates to the Windows web workflow. The existing v113 Local Web API workflow was extended to the seventh source and its exact Omnium options. **GitHub Actions #40478757369**, commit `872dfafc68d15cd70f75db16b33080ba33830614`, completed **SUCCESS on Ubuntu 24.04/Python3.12 and Windows 2022/Python3.14**, with **40/40 offline tests per OS; Native0**. The earlier v113 failures on unpinned Outlaw Folio option count were corrected before this final PASS. User Windows full end-to-end Native on Outlaw has **NOT** occurred.

## New offline tests / user next step

`tests/test_v131_rogue_outlaw_source_candidate.py` 3 tests cover official source exact SHA, original class/spec/APL/consumables, 16 physical source items/tier/weapons/gems and same v127 metadata usage. `tests/test_v098_target_user_scenario_bootstrap.py` adds a real Outlaw **first-time** internal user plan (fake simc.exe, no Native), B3150/O64/T3214, 4-tier+two hands, six ordinary gems with four colors under diamond240967, v122 json2 placeholder, seal replay, two feasible seeds. Existing 6 other specs retain full source-identity, byte-parity and no-reseed unit tests. `tests/test_v106` and `tests/test_v113` adapt source count from six to seven without changing Native six-call workload.

After all relevant offline CI is green, take one bounded **user Windows** Outlaw UI plan-only Native0 test; if fully source-correct, one real six-candidate Native session then cache reuse only if needed. **Do not represent 7/27 as seven real Native 6/6 acceptances**. This is seven supported source-connected beta choices versus **three** actually user-proven full web Native6/6 specs, and global optimality is never proved.

## Authorization and efficiency

No main merge, immutable v003 change, official Work OS/Shared State or Project Sources/UI promotion. Same-season static cache not invalidated, prior DPS Native cache intact. No item DB, independent proc/APL model, or new optimizer; existing automatic Github Actions push path used. Exact source and focused validation rather than comprehensive native reruns.
