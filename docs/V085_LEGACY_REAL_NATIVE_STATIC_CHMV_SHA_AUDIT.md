# v085 — historical Shaman/Rogue Native input and JSON2 static-CHMV audit

Date: 2026-10-26 KST. Isolated product-development evidence only. T=G+J+F approved; selected oil O remains outside T. This audit is not original v015/v016 integration or a global optimum certificate.

## Elemental Shaman — five original real Native results

Sources: [v078 first 2 Native](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40198642691), artifact 12600019390, exact ZIP SHA256 c01c75cd5d636109ebfb8b0d496a39b7dbe4907bba678943871deff853323ef2; and [v078B 2 official + 1 scout](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40199040044), artifact 12601146170, exact ZIP SHA256 2bd2c8063a3714f297dbd2bbfc28550498f9c08f5458a2ab11e8b4c7498cb103.

Both original ZIP bytes were independently retrieved through the connected GitHub artifact connector, SHA256 matched the original provider digest, ZIP CRC validated, all five real Native input/JSON2 SHA matched original receipts. Original measured offset on this profile is +165 crit, numerically identical to the **scenario-declared** F crit165 vector; there was NO attempt to independently emulate/certify talents, flasks or procs. G2645+J138+F165=T2948.

| Historical case | Actual injected G+J CHMV | Derived static c = injected + declared F | DPS | SEM |
|---|---|---|---:|---:|
| Official A | 572/737/737/737 | **737/737/737/737** | 199583.42 | 760.82 |
| Official B | 472/837/737/737 | **637/837/737/737** | 197285.94 | 915.90 |
| v015-derived scout | 672/637/737/737 | **837/637/737/737** | 197233.29 | 1068.62 |

All three real outputs match the target T2948 and their own original JSON2 buffed rating fields in this *specific* configuration, though buffed-vs-static identity is not a general product rule. Each row 34 DPS samples. NO NEW SIMC. Independent local receipt: V085_SHAMAN_NATIVE_REUSE_LOCAL_AUDIT.json, SHA256 a6a99fd99d060456dc5c2451d8833299186f81933cac9a8ce95ae3a6f42ff1d8.

**Important external CI limitation:** [v085 Actions first](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40241547648) and [retry](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40241618937) both passed 482 unit tests / 2 skips (484 total) and retrieved the first artifact, but second historic artifact failed with GitHub download-artifact@v4 Bad credentials. This is transport/auth failure, not a Native result or formula failure. GitHub connector fetched same second archive independently. **The new v085 strict current v066.prepare_static code did NOT reach execution/PASS in CI.** Do not report v066 static reacceptance PASS; treat it as blocked while local raw-file SHA/static arithmetic passed.

## Subtlety Rogue — exactly two independently reaudited v075 new Native scouts

Source [v075 Actions](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40190657735), artifact 12598060958, full ZIP SHA256 29232dfc009fe4dc5dc76a86b8905dc969df5ff9914d1ad2e023e3a40aface10. Independently fetched and ZIP SHA+CRC checked; each Native input/JSON2 SHA and actual JSON2 buffed rating/DPS/SEM matches original receipt. Profile-specific G2847+J138+F165=T3150, declared F=(165 crit,0,0,0), O outside T.

| Historical v075 scout | Original injected G+J | Derived static c | DPS | SEM |
|---|---|---|---:|---:|
| E | 1348/913/712/12 | **1513/913/712/12** | 223990.08 | 719.97 |
| F | 648/913/1062/362 | **813/913/1062/362** | 227079.56 | 895.94 |

Both 59 DPS samples and raw sum 2985, static sum 3150. Exact independent local receipt V085_ROGUE_NATIVE_REUSE_LOCAL_AUDIT.json, SHA256 472ddb31751e7e96f2b52eb829b3402762bb9a0fc99a28b8705194c0aced2d60. Historical v075 used 9 earlier Native outputs, **not independently re-downloaded or re-audited here**. Current v066.prepare_static full Rogue preflight NOT independently executed; do not claim complete generic Rogue PASS.

## Boundary

Total local verification: seven original Native cases (5 Shaman, 2 Rogue), zero new SimC; genuine exact SHA and static c arithmetic verification, not proven statistical superiority. Shaman v085 current-v066 CI remains blocked by historic artifact transport. Future high-value work: generalized per-profile F/E attribution, external fixed oil O, 0–2 embellishment exact input, and original v015/v016 product lineage. No separate proc mechanism gates or item recommender. Main, original products and official Work OS/Project Sources unchanged.
