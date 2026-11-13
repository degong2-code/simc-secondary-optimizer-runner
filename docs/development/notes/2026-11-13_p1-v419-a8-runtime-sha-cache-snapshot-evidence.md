# v419 — 78요소 A8 실행 SHA·DPS 캐시·결과 스냅샷 기능별 검토

- **Capability:** `SOURCE.SEAL`
- **Keywords:** A8, SimC SHA, revision, DPS cache, result snapshot, v106, v291, v293, 95%, current source, generic, product
- **Prior evidence:** [v409 A8 범위 결정](2026-11-13_p1-v409-a8-simc-metadata-and-result-snapshot-policy.md); [v417 실제 70783 Windows](2026-11-13_p1-v417-bounded-post-bridge-product-e2e-once.md); 기존 v407 역사 원본 영수증
- **Decision:** `REUSE` 실제 사용자 실행 파일 SHA/버전 기록·정확 DPS 캐시 identity·기존 결과 스냅샷 조회만 A8 수락 조건으로 사용. SimC↔게임 빌드 일치·컴파일 계보 인증 Gate 없음
- **Changes:** A8 generic/current_source/product_integration에 **각 범위 검증** PASS 근거 연결, 역사 PASS 독립 보존. 기존 v401 next_review 하드코딩을 소스 검토 순차 선택으로 고쳐 A9 진행. JSON/상세 추적표/자동 생성 상태표 동기화
- **Verification:** [실 Windows #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756) tested `89d4810baf5e05f1c5c6f355f39a5f35ca9ec4e7`, 환경 Native3+DPS Native12, binary SHA `1fc927d2be7f1b6064c75f004b5b22245b064a6b3e56e572af4048ba822a986d`, [원본 저장 결과](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756/artifacts/14021859656), 실제 95% 결과 API. [v113 Linux/Windows #43391249405](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43391249405) 각 331 PASS/1 SKIP, 서로 다른 SimC 실행 파일 bytes·revision→별도 세션, 같은 SHA 별칭 재사용, cache-only·저장 결과 읽기 재실행0 회귀 포함. 이 변경의 v401 CI 별도 확인
- **Remaining:** 공식 다음 요소 `A9`; 나머지 77요소 및 전체 제품 E2E 완료는 미주장. 특수 L/기타 선택 효과는 해당 요소에서만 검토
- **Efficiency:** 기존 실제 Native 및 기존 multi-OS 회귀만 재사용, 신규 Native/원본 수집 0, 기존 결과/캐시 파일 변경 0

A8 기능적 범용성은 특정 시즌 번호의 동일성보다 **사용자 입력·바이너리 바이트·revision을 바꾸었을 때 캐시를 구별하고, 저장 결과는 SimC 없이 읽는 것**으로 검토했다. 다른 시즌의 장비 원본 수집은 A9 이후 해당 요소에서 담당한다.
