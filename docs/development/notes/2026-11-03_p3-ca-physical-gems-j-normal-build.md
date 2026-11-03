# 2026-11-03 · P3-CA · 실제 일반보석 물리 ID를 기존 J→B/T 정상 Build에 연결

- **Capability:** `J.GEM`, `BUDGET.GJFO`, `PRODUCT.E2E`, `DEV.CONTINUITY`
- **Keywords:** 가변 소켓, v271, gem ID, J, B/T, preflight, v216, v222, 16/7, 16/8
- **Prior evidence:** [PROTOCOL](../PROTOCOL.md)·[INDEX](../INDEX.md); [P3-BZ 67 PASS](2026-11-03_p3-bz-variable-socket-physical-gems-connect.md), [P3-BX Native 4/4](2026-11-03_p3-bx-simc-socket-native-contrast.md). 기존 v271→v139 실제 물리 4색, v216 정상 Build, v262/v222 단일 GJFO/B/T 산술.
- **Decision:** `CONNECT` — 보석 효과·새 예산 엔진/새 인증 Gate 금지. 실제 v271 4색 보정 **이후** 보석 ID별 CHMV 정적 rating 후보 합을 기존 v222 J 증거와 대조한다. 소켓 허용·품질/효과 인증 및 +1 편차 해결로 해석 금지.
- **Changes:** `v271.reconcile_observed_J` ID 일치/수량/합계만 계산한 미승인 후보; 기존 `v216.preflight_new_season_source`는 제공된 ID별 수치와 기존 budget J 일치 검사를 추가하고 `v262→v222`의 수동 T/B/T를 그대로 사용. 기존 정상 `v216.build_environment`의 `profile_stage_receipt.socket_layout`·선택 `fresh_gjfo_evidence`를 같은 preflight로 연결. 구형 6/head/J138 실행경로 불변, READY·정책 A 승격 없음.
- **Verification:** 새 CI 확인 전 `NOT_VERIFIED`; 이전 P3-BZ 67 PASS와 P3-BX 실제 Native 4/4는 `REUSED_HISTORY`에 한정. 이번 신규 게임 HTTP0/Native0. 변경된 회계 경계의 기존 합성 회귀와 신규 focused 시험만 재사용.
- **Remaining:** 실제 새 시즌 GEM 품질·해당 ID 정적 J 소스/스탯 분포와 소켓 게임 조건, 새 G/F/O의 소스 정합은 실제 부족. J 합계 연결과 달리 최종 정책 A 사용자 등록/동일 v098→적응형 SimC 정상 READY/26 DPS E2E 미완료. `240906` +16/+7 ↔ +16/+8 원인 미확정.
- **Efficiency:** 기존 v216 preflight 및 v222 계산만 사용. 최종 ID 최대64개 산술·동일 rows stage 소비, 신규 인증기·외부 HTTP·Native 0. 기존 정적/DPS 캐시 무효화 0, 이전 세션 바이트 보존; 실제 실행시간 측정은 아직 없음.
