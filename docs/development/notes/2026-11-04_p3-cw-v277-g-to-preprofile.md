# 2026-11-04 · P3-CW · 기존 Native G → 동일 Build 프리프로필 산술 접합

- **Capability:** `G.NUMERIC`, `BUDGET.GJFO`, `PRODUCT.E2E`
- **Keywords:** P3-CW, v277, G, Native, v216, preprofile, v222, target ilvl, source-only, missing G, seal
- **Prior evidence:** [PROTOCOL](../PROTOCOL.md)→[INDEX](../INDEX.md)→[P3-CU](2026-11-04_p3-cu-zero-history-budget-user-target.md) 178 PASS, [P3-CG](2026-11-03_p3-cg-zero-history-native-g.md) 기존 `v277→v236/v234` Native·캐시, `v222` 10-rating 단위 표준화 및 `v216.preflight_new_season_source`. 실제 P3-CO/CP·P3-BX 수치/원본은 역사 증거만 재사용.
- **Decision:** `CONNECT` — 새로운 G 측정기/예산 엔진을 만들지 않고 `v277`이 이 Build에서 이미 확인한 숫자 관측을 원래 `v216→v222` 경계에 전달한다. 기존 J/F/O 및 원본 인증 부족은 그대로 `PENDING`.
- **Changes:** `v216._reuse_v277_G_in_preprofile`는 v277 숫자/표준화/ilvl/JSON2·Native/profile/binary SHA·미승격 조건을 점검하고 G-only source 후보를 반환. 내부 same-build 예산 evidence가 J/F/O를 포함하되 G가 빠졌다면 v222의 G 하나만 기존 Native에서 채워 산술 검사한다. G가 이미 있으면 Native와 일치해야 하며 충돌은 차단한다. 정상 zero-history Build 소스 컴파일 후 같은 preflight 호출을 재사용; 새로운 collector/프로필/인증 Gate 없음.
- **Verification:** 신규 4개 합성 source-only focused 회귀(숫자만, JFO 없는 상태/누락 G 자동 연결/서로 다른 G SHA/ilvl mismatch) 및 기존 P3-CU 6개 포함. **실제 새 Native/HTTP 호출 0**; Actions run/pass 수는 실제 실행 영수증 확인 전 `NOT_VERIFIED`. 이전 [P3-CU 178 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41744042859)는 기준 코드의 재사용 역사 증거이며 이번 코드 변경 PASS라고 주장하지 않는다.
- **Remaining:** G source-only numeric 관측만으로 시즌 공식 G/J/F/O 승인, 최고 품질·무기손/ilvl·고정 L/E/O, `v222` 증거 인증·정책 A 자동 등록·`v098→v094` 적응형 E2E 및 신규 설치 통제시험은 완료되지 않았다. `v277` 성공 status도 바이너리의 게임 빌드 독립 인증을 뜻하지 않음.
- **Efficiency:** 기존 v277 JSON/receipt와 v222 산술 재사용, 새 Native0·Wago/HTTP0, B/T의 별도 알고리즘 없음, 신규 대용량 CSV 재스캔·아이템 DB·캐시 폐기 없음. 기존 main/immutable/Project Sources/Work OS 권한 유지.
