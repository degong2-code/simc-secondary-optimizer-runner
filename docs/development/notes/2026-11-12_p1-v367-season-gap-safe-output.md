# v367 — v366 시즌 원본 진단의 비밀 문자열 재노출 방지

- **Capability:** `ENVIRONMENT.SEASON`, `DEV.CONTINUITY`, `PRODUCT.E2E`.
- **Keywords:** v367, v366, read-only diagnostic, safe output, original value redaction, WSE, P1-A, no Native.
- **Prior evidence:** v366 진단 도구 GitHub blob `f141e974`, 오프라인4 PASS. 실제 손상 JSON에 임의 `missing`/`requires` 문자열을 넣으면 결과에 그대로 출력되는 회귀를 로컬 재현.
- **Decision:** `CONNECT/FIX` — 진단 출력은 v163 원본의 **허용된 출처/조건 enum**, 숫자 WSE/시즌, v274 실제 컴파일러 입력 키, v216 공통 단계 코드만 노출. 알 수 없는 동적 문자열은 원문 출력 대신 개수로 표시. 새로운 시즌 소속 추정/승격이나 별도 인증 Gate 금지.
- **Changes:** `integration_probes/p1_v366_existing_source_gap_report.py`의 출력 projection에 출처 enum·원본 빌드·시즌 타입 제한, v274/진행 상태 allowlist·기타 요구사항 개수 추가. 악성 dict/자격정보를 문자열로 노출하거나 해시 집합 조회에서 예외가 나지 않도록 검사. `tests/test_p1_v366_existing_source_gap_report.py`에 악성/손상 문자열 비노출 테스트 1개 추가. v163/v216/v274 본체·UI·캐시 불변.
- **Verification:** **이번 로컬 Python unittest 5 PASS / 0 FAIL**; 원본 2개 파일과 로컬 실행 파일의 Git blob SHA 일치. GitHub Actions 신규 실행 **0**, 신규 Native **0**, 신규 인증/원본 수집 **0**. 이는 합성 진단 fixture 실증이지 시즌 JOIN 승인 아님.
- **Remaining:** 사용자 PC 봉인 v217·v163 및 선택된 필수 아이템 증거가 현재 연결된 GitHub에 없으므로 현 시즌 `SOURCE_SEASON_JOIN_PENDING` 유지. 이 진단의 임의 JSON SHA만으로 v217 전체 봉인·원본 진위나 시즌 소속을 인증하지 않는다. 실제 로컬 증거로만 다음 조치 판단.
- **Efficiency:** 기존 진단 1개·테스트 1개만 국소 수정, 신규 외부 I/O·Native·전체 DB·제품 엔진 수정 없음. `main`·원본 불변·v364 UI 동결 유지.
