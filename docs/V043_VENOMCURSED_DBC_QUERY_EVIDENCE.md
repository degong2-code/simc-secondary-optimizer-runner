# v043 — Venomcursed spell-query evidence and limits

Status: **PASS of bounded pinned SimC DBC spell queries**; no product integration and no policy promotion.

## Source and method

- GitHub Actions [#40121991730](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40121991730); pinned Linux SimC cache HIT; no compilation; 150 offline tests (148 PASS, 2 SKIP); two query-only SimC processes, zero combat simulations.
- Pinned SimC source commit: `7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd`; binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`.
- Exact commands, fixed values: `spell_query=spell.id=1307922@334` and `spell_query=spell.id=1307923@334`. This queries a spell-data scaling level, **not** the converted item configuration.
- Native v042 combat JSON2 showed static item mastery +201 and the Venomcursed buff's presence/uptime but did not give the buff's stat delta directly.

## Pinned DBC query output

| Spell/effect | Observed result | Limits |
|---|---|---|
| Buff 1307922 effect #1 (1336193) | Mastery rating channel; reported scaled field 0 | Buff record alone is not the dynamic applied amount |
| Buff 1307922 effect #2 (1336194) | Crit, haste, versatility channels; reported scaled field 0 | Not a claim that the combat buff has zero effect |
| Driver 1307923 effect #1 (1336195) | **Scaled Value +362.9923**, coefficient 1.264787 | Pinned DBC value at requested 334, not an independently sampled in-combat stat change |
| Driver 1307923 effect #2 (1336196) | **Scaled Value −60.49704**, coefficient −0.210792 | Same limitation |

The pinned SimC implementation `venomcursed()` uses `effect.driver()->effectN(1).average(effect)` and `effectN(2).average(effect)` for a `stat_buff_t`. The source links DBC effects to the runtime mechanism, but no controlled combat before/after-stat measurement has yet independently established equality to the values above in the actual converted level-334 trial.

These **dynamic** values are distinct from the **static** +201 mastery already found on item 271874 and redirected to tier item 271564 in earlier Native receipts. They are not added to the static gear CHMV budget.

## Independent evidence

Artifact ID `12571616882`; six archive entries; ZIP CRC PASS; SHA256 `b4b7699f827ebf8c6abf41a2e244959b6e0d97e32b01ac77c81d06b200ddd291`. Independent 16/16 byte, signature, source and scope checks PASS. Machine receipt: [V043_INDEPENDENT_DBC_ACCEPTANCE.json](V043_INDEPENDENT_DBC_ACCEPTANCE.json).

## Outstanding work

- Verify actual in-combat stat effects on the pinned 334 experimental scenario by a bounded method, without treating the DBC-query values as independently measured applied values.
- Obtain real-game evidence for the **catalyzed** 334 item bonus list, gem/socket rules and itemlevel scaling; do not promote diagnostic bonus 13846.
- Resolve the official v1.0 `T=G+J+F`, unapproved oil-inclusive candidate, and 3182/3184 provenance through actual SimC budget attribution first.
- v016–v031: reported complete / not independently verified here. v016 ↔ GitHub v032–v043 lineage and integration remain unverified.
- All future tests must separately report **test success**, **product code integration**, **official policy promotion**.

No main, Project Sources, Instructions, CURRENT/Shared State, Work OS M0 or v003 immutable changes.
