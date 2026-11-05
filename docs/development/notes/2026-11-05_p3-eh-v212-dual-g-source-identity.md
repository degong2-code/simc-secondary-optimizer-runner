# 2026-11-05 · P3-EH · v212가 G의 두 실제 원본 경로를 구별하여 재사용

- **Capability:** `ENVIRONMENT.WEB`, `BUDGET.GJFO`
- **Keywords:** P3-EH, v212, v222, Native G optional, alternative source identities.
- **Prior evidence:** [PROTOCOL](../PROTOCOL.md) → [INDEX](../INDEX.md) → [P3-EG](2026-11-05_p3-eg-reuse-existing-same-season-g-for-auto-v222.md) → `runner/v212_environment_manifest.py::compile_fresh_source_environment`. P3-EG G 참조를 출력해도 v212가 `G_native_json2_sha256`만 필수로 요구한 실제 계약 충돌.
- **Decision:** `CONNECT`, 신규 Gate `STOP`: `G_native_json2_sha256` 또는 `G_same_season_reference_source_sha256` **정확히 하나**만 허용. 두 개 동시 제출/둘 다 없음/형식 위반은 차단. J/F/O 동일 출처 identity 필수 유지.
- **Changes:** 기존 `v212.compile_fresh_source_environment`의 receipt identity 판정만 교정, 유효한 source-only manifest의 G 원본 종류를 보존. 추가 Native, 별도 인증/시즌 데이터셋, UI 입력, DPR/캐시 로직 증설 없음.
- **Verification:** `tests/test_v212_environment_manifest.py`에 분리 SHA/매니페스트 불변성·양쪽 혼합/누락/위조 차단 회귀 추가. 현재 신규 실행 결과 **NOT_RUN/NOT_VERIFIED**, 기존 P3-ED Actions/Native 역사 증거만 재사용. 환경 READY·정식 item 선택지 발행·T1 PASS 아님.
- **Remaining:** 실제 동일 시즌 원본 인증, 최고 품질 J/F·필수 특수 보석 1개/소켓, 실 기름 O 무기 적용, 정책 A 발행, v212 환경 설치/READY 및 T1. main/v003/v016/Project UI/주 개발 채팅 불변.
- **Efficiency:** 기존 v212 identity 검사 한 번만 교정. 새 API/CSV 수집·Native·반복 검증/캐시 삭제 0; 선택된 SHA map은 기존 버전화 manifest의 소규모 JSON에만 저장.
