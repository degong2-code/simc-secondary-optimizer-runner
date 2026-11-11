# P2 2026-11-11 — 실제 Native 18회, 35/120/320 반복 비용 실측

- **Capability:** `OPTIMIZER.POLICY`, `DEV.CONTINUITY`.
- **Keywords:** SimC, v315, 18 real Native, 35/120/320, iterations, startup, wall-clock, IDEA-001.
- **Prior evidence:** [v314 source proof](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42846073820) and [original compact 18 timings](../research_receipts/p2_20261111_18_native_request_cost.json).
- **Decision:** `REUSE` original v290 35/320 until 120-step or precision cadence improves actual confirmed DPS per wall/iterations.
- **Changes:** Preserve 18 measured request timings linked to two existing v314 profiles in Git research ledger; source and binary pinned.
- **Verification:** 18 real local SimC Native cost measurements, 2 specs × 3 iteration levels × 3 repeats; NOT new-profile optimizer A/B.
- **Remaining:** Verify v316/v317 trace and test novel-specialization algorithm comparison at equal iterations and wall time.
- **Efficiency:** No repeated season DB scrape or 26-spec Native sweep; 120 extra phase not introduced.

- **IDEA-001 고도화**, 새로운 알고리즘 ID는 추가하지 않음. **Native 실측18회**, 알고리즘 간 공정 DPS A/B **0회**.
- 기존 v314 신규 프로필 연구 원본 `arcane_mage__narrow`와 `beast_mastery_hunter__narrow`의 **동일 CHMV/아이템/특성/전투조건**을 보존했다. 각 원본 input SHA는 [소형 실측 표](../research_receipts/p2_20261111_18_native_request_cost.json)에 있고, binary SHA `6b83e4d5d2216faf91511fb00ae712cdf4cc0224b0c83107e8c9c7358c24bfc6` 확인.
- `iterations=35,120,320`과 출력 JSON2 경로만 교체해 각 전문화×iteration마다 3회씩 실제 SimC 실행, 총18회. JSON2 원본 player DPS samples=34/119/319 확인. SimC 소스·revision `c20e2ad52e`, threads1, single target 300s.
- 실제 실행 호스트 Linux AMD EPYC 9V74, 현재 container 5 CPU 할당 보고. 이것은 GitHub Actions·Windows 사용자 PC의 실행시간이라고 과장하지 않는다.

| 전문화 | 35회 process wall 중앙 | 120회 | 320회 | 320/35 시간비 | 120/320 시간비 |
|---|---:|---:|---:|---:|---:|
| 비전 마법사 | 0.159053초 | 0.431128초 | 0.956375초 | 6.013배 | 45.08% |
| 야수 사냥꾼 | 0.193648초 | 0.476049초 | 1.070229초 | 5.527배 | 44.48% |

**판정:** 단순 iteration 비율 320/35=9.14를 그대로 '추가 후보 9개'로 환산하지 않는다. 본 두 기존 프로필에서는 320회 1건 실행시간으로 35회 약5.5~6건을 실행할 수 있었다. 외부 process overhead와 SimC 내부 reported WallSeconds는 다르며 n120 간헐적 scheduling outlier도 관측되었다.

**120 중간 승급의 비용 기준:** 120회 중간 측정 후 다시 320회 측정하는 2-call 전략은 처음부터 320회 측정하는 1-call 전략보다 후보당 약44.5~45.1% 추가 비용. 단순 wall 기준으로 120 screening을 받은 후보 중 최종 320까지 올라가는 비율이 약54.9~55.5% 미만이어야 시간 절감 가능성이 있고, 진짜 고점 제거 위험을 별도로 입증해야 한다. 해당 숫자는 본 호스트·두 프로필에만 해당.

**현재 결정:** v290 기본 및 v291 scout/precision 35/320 exact identity 유지. 먼저 v316 실 Native trace 영수증 확인과 기존 v290 정밀 확인 **횟수·시점만 opt-in으로 조정하는 ablation**을 진행한다. 120 단계는 본 결과만으로 기본 도입하지 않는다. 다른 알고리즘 전역 고점 우위/95% 확정/새 사용자 5~10분 성능 개선은 미실증.

**보존:** 18회 compact 실제 시간값·원본 source SHA를 [Git-tracked 연구 원본](../research_receipts/p2_20261111_18_native_request_cost.json)으로 저장. 로컬 full raw receipt SHA는 compact에 남겼지만 **전체 Native JSON2 및 로컬 확장 리포트 원본이 GitHub에 영구 복사되었다고 주장하지 않는다.**
