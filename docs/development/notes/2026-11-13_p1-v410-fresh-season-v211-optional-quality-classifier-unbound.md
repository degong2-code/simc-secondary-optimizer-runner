# v410 — P1 새 시즌 G/J/F/O 구축의 v211 원본 분류 연쇄 차단 복구

- **Capability:** `ENVIRONMENT.WEB`
- **Keywords:** P1, season G/J/F/O, source, v211, v212, optional quality, v213, profile, no Native
- **Prior evidence:** [v409 A8 범위 간소화](2026-11-13_p1-v409-a8-simc-metadata-and-result-snapshot-policy.md); [기존 v113 오프라인 CI #43386905830](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43386905830)에서 v212 테스트 2건 `NameError: quality_source_only`
- **Decision:** `CONNECT` existing optional source-only highest-rank comparison to original v211 fresh-season compiler; no new effect verifier, no mandatory quality Gate
- **Changes:** `compile_fresh_season`에서 `_fresh_static_quality_source_only`를 실제 호출하고 기존 `SourceBlocked` fallback을 보존. 잘못 들어간 이전 시즌 `compile_catalog`의 미사용·정의되지 않은 `season` 참조 제거. v213/v212의 기존 source-only 결과 필드는 유지
- **Verification:** Existing focused `test_v211`, `test_v239`, `test_v240`, `test_v212` coverage on this commit; new Native 0. CI 결과로 PASS/FAIL 별도 판정
- **Remaining:** 실제 시즌 G/J/F/O 데이터 완성 및 사용자 프로필/SimC DPS 통합은 여전히 제품 실행 영수증 필요. 이 소스-only 수정 자체를 완성으로 승격하지 않음
- **Efficiency:** 중복 Native 0, HTTP/DB2 0 from code; optional raw family quality only when source includes raw ranks, in-memory parse, no new file/cache keys. 기존 stage/cache 재사용

## 원인

오류는 SimC 빌드·SHA 불일치가 아니라 새 시즌 일반 분류기가 이미 존재하는 품질 비교 결과 변수를 할당하지 않은 단순 연결 누락이다. 또한 이전 시즌 호환 경로에 `season`과 `candidates` 스코프가 맞지 않는 미사용 블록이 삽입돼 있었다. 둘 다 기존 코드를 옮겨 바로잡고 새로운 작업 체계를 추가하지 않는다.
