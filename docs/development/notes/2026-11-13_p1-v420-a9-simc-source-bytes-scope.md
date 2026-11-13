# v420 — 78요소 A9 필수 SimC 원본 파일의 실제 소비 범위 검토

- **Capability:** `SOURCE.SEAL`
- **Keywords:** A9, SimC DBC, generated source, effect/enchant C++, v229, v275, v211, v191, SHA, season, Native, P1
- **Prior evidence:** [A8 실 SHA·스냅샷](2026-11-13_p1-v419-a8-runtime-sha-cache-snapshot-evidence.md), [v417 실제 Windows GJFO→DPS](2026-11-13_p1-v417-bounded-post-bridge-product-e2e-once.md), [v410 v211 소스 수정](2026-11-13_p1-v410-fresh-season-v211-optional-quality-classifier-unbound.md)
- **Decision:** `REUSE` v229 SimC pinned `engine/dbc/generated` 파일과 v275의 v211 원본 효과·마부/보석 입력, SHA/blob 재사용 검증을 필수 A9 원본 기능으로 판정. SimC의 효과 메커니즘을 재검증하거나 실제 실행 바이너리와 소스 커밋의 컴파일 계보 일치를 별도 Gate로 만들지 않는다
- **Changes:** A9 범용/현재 원본/제품 소비 증거를 78요소 정본에 연결하고 다음 검토를 A10으로 갱신. 기존 수집·컴파일·DPS·캐시 코드 변경 없음
- **Verification:** [v409 source focused #43386905854](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43386905854) 60 PASS/0 FAIL에 `v229`, `v257`, `v275` 소스 정확 revision/원본 누락·변조/다른 빌드 음성 회귀 포함. 이후 [v410 소스·마부 연결 #43387395448](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43387395448) 80 PASS/0 FAIL. [v417 현재 Windows 실 Native #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756), tested `89d4810baf5e05f1c5c6f355f39a5f35ca9ec4e7`, SimC 원본에서 v191 컴파일 장비209/티어65/마부 후보772, v212 환경 G2850/J92/F165/O0 → Native3+DPS12·저장 결과 조회 PASS
- **Remaining:** 이번 A9 완료는 소비된 70783 시즌 소스와 다른 빌드·원본 음성 회귀라는 실제 범위에 한한다. A10은 통합 컴파일 출력을 기존 영수증으로 검토. 모든 과거 효과·선택하지 않은 아이템/26전문화/최종 78요소 E2E는 주장하지 않는다
- **Efficiency:** 기존 SHA/Actions·원본 소스 캐시·Native 영수증만 재사용. 신규 원본 수집, DB2, HTTP, SimC Native 및 별도 인증 Gate 0
