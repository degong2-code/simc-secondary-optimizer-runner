# 2026-11-05 · P3-EF · 명시적 기름 미사용의 무의미한 무기 입증 의존성 제거

- **Capability:** `BUDGET.GJFO`, `O.OIL`, `ENVIRONMENT.WEB`
- **Keywords:** P3-EF, explicit no oil, O zero, no oil, not required, v222, v216, no Native
- **Prior evidence:** [PROTOCOL](../PROTOCOL.md)→[INDEX](../INDEX.md)→[P3-DZ](2026-11-05_p3-dz-independent-optional-g-vs-fo-native.md)→[P3-EE](../../CHAT_CONTINUITY_HANDOFF_20261105_P3_EE_ENGINE_FIRST.md). 기존 `v216`의 명시 빈 `oil_item_ids_by_hand`와 `v222`의 O=0 산술 보존.
- **Decision:** `CONNECT` + `NOT_REQUIRED`: **명시적 미사용**이면 적용 기름/무기/손이 없으므로 무기 적용성 Native·마스크 인증이 필요 없음. 원본 미관측 O는 미사용과 다르고 선택된 실제 기름은 기존 적용 검증 유지. 새 효과 Gate·구시즌 O 상수 사용 `STOP`.
- **Changes:** `v222.explicit_no_oil_component`는 빈 선택을 catalog identity에 묶어 결정론적 SHA/고정 O0를 산출. `v222.preprofile_budget`은 정확히 그 컴포넌트에서만 무기 검증 의존성을 제외하고 사유를 기록. 기존 `v216` 선택형 원본→`v222` 경로에서 재사용. G/J/F 검증·수동 T 우선·L/E/O 중복방지·캐시/기존 시즌 호출은 그대로. source-only 출력은 READY가 아님.
- **Verification:** 신규 `test_v222` 명시 NONE·수동 T·미승인·위조/누락/선택손 차단 및 `test_v287` 기존 경로 연결 검사. **현재 신규 테스트 NOT_RUN/NOT_VERIFIED**, 기존 P3-ED 집중 243 PASS/0 FAIL, v212 각 441 PASS/4 SKIP는 역사 재사용. 실 Native/외부 게임 HTTP 신규 0.
- **Remaining:** 동일 시즌 G/J/F, 선택한 기름 O의 실제 적용, 최고 품질·특수 보석 정확 1개·소켓, 정책 A 발행·v212 시즌 설치 READY·T1은 미완료. 이번 변경은 공통 검증 의존성 하나의 제거이며 T1 인증이 아님.
- **Efficiency:** 미사용 O에 대해 추가 Native/무기 적용 검사 불필요. 신규 HTTP/Native/DB/반복 수집 없음, 소규모 SHA 1회. main/v003/v016/Project UI·Work OS/기존 개발 소유권 미변경.
