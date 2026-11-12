# v373 — v211 정적 품질 비교에서 원본 rank 계열 누락/변조 차단

- **Capability:** `ENVIRONMENT.SEASON`, `ENCHANT.QUALITY`, `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** v373, v211, pinned SimC full family, quality rank omission, fail closed, optional source evidence.
- **Prior evidence:** v372 HEAD `aa1c590d70b8f2b4c0379dcd0b86dde28ae473e9`, 새 `_fresh_static_quality_source_only`는 v191 raw family 행만 선택해 비교; pinned SimC 원본에 있는 낮은 등급의 토큰을 v191에서 바꾸거나 행을 생략하면 해당 행이 가족에서 빠져 비교 누락 위험. 이는 실제 업로드 70783에서 재현한 결함이 아니라 합성 원본 변조 사례에서 확인한 코드 결함.
- **Decision:** 원본 v191 전체 랭크 보존과 v211 동일 빌드 pinned SimC 계열 **완전 일치**가 없으면 수치 비교를 승인 가능한 정보로 해석하지 않는다. 선택 옵션 품질만 보류하고 정상 시즌 공통 구축·G/J/F/O를 차단하는 새 Gate는 만들지 않는다.
- **Changes:** v211 비교 함수가 선택 토큰/장비 class/물리 mask/subclass에 대응하는 **pinned `permanent_enchant.inc`의 모든 rank·enchant_id 계열**을 역으로 추출하고 v191 원본 행과 정확히 대조. 누락/재라벨 시 `FRESH_QUALITY_FULL_PINNED_RANK_FAMILY_COVERAGE_DRIFT`; 기존 v211 선택 후 분류는 정상 지속, 품질 관측만 `OPTIONAL_SOURCE_QUALITY_COMPARISON_PENDING`. v239 합성 테스트에 낮은 등급 토큰 변조 및 나머지 후보 분류의 비차단 추가.
- **Verification:** 기존 Windows 패키지의 v211 파서와 **해당 새 품질 비교 함수 동일 로직**을 격리 경로에서 로컬 Python으로 구성·실행한 합성 **6 PASS / 0 FAIL**(정적 비열등, 높은 rank 수치 열등, scaling 보류, 적용조건 불일치, raw 원본 부재, 하위 rank 누락/재라벨 차단). 처음 누락/재라벨 사례 1 FAIL을 발견한 뒤 국소 수정하고 6/6 재실행한 결과. 이는 **저장소 전체 v239/v240 unittest 또는 Actions/Windows 실증이 아님**. GitHub 새 CI/Native/HTTP/DB2 수집 0.
- **Remaining:** raw DBC의 정적 조건을 비교한 source-only 관측값이며 실제 물리 마부 ItemID의 해당 시즌 소속·사용 조건과 SimC 적용 증거는 여전히 미인증. 사용자 UI 선택지 승인/READY로 승격하지 않는다. 동일 시즌 v217 cache/Native 재사용, 전체 A~G 전역 완성/현재 시즌 JOIN/G/J/F/O READY는 별도 PENDING.
- **Efficiency:** v211 정적 품질 비교 계열 대조와 기존 테스트만 국소 보강. 새 API·AI·캐시 폐기·시즌 전수 Native 0.
