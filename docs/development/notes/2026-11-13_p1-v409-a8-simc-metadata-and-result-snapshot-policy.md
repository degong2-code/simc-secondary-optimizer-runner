# v409 — SimC 실행 식별·저장 결과 스냅샷 간소화

- **Capability:** `SOURCE.SEAL` (A8; 결과·캐시 정체성 vs 시즌 예산 원본)
- **Keywords:** A8, SimC binary SHA, version metadata, result snapshot, DPS cache, v106, v291, v293
- **Prior evidence:** [v407 역사 범위](2026-11-13_p1-v407-a8-historical-source-binary-identity-and-alias-guard.md), [v408 경로 확인](2026-11-13_p1-v408-a8-user-plan-session-resume-binary-alias-guard.md), 기존 v106/v291/v293 캐시·결과 저장
- **Decision:** `REUSE` 기존 SimC SHA/결과 스냅샷만 유지, 과잉 인증은 `STOP`. 최신 사용자 결정: SimC와 게임 빌드 번호 일치, 실행 바이너리의 컴파일 계보 인증 불필요. 실제 사용 SimC 버전/리비전·SHA만 기록해 후보별 DPS 캐시를 구분한다. 결과 재현 실행보다 스냅샷 표시를 기본으로 한다
- **Changes:** v407/v408에서 추가한 v277/v113 심볼릭 링크 별칭 차단 제거. SHA가 동일한 실행 파일의 별칭은 같은 기존 세션/Native 캐시 이용. A8 JSON 수락 조건·상태 추적표/정책 개정. 결과 스냅샷 엔진·데이터 복제 없음
- **Verification:** 초기 v409 집중 회귀에서 plan 별칭 재사용 PASS, 사후 manifest 수정 회귀는 기존 프로필 불변성 봉인으로 차단(정상). 테스트를 원래 요청 별칭→봉인된 세션→재개로 바로잡아 재실행. 78계약 JSON/추적표 표기도 동기화; 기존 v342/v344 실 영수증은 역사 범위만 재사용
- **Remaining:** A8 generic/current_source/product_integration PENDING 유지(무증거 승격 금지). 불필요한 계보 인증 작업은 종료하고 시즌 G/J/F/O→대표 프로필→SimC DPS 통합 P1을 진행한다
- **Efficiency:** 새 Native/DB2/HTTP 0, 새 엔진·결과 파일 0, SHA-기반 기존 캐시와 결과 영수증 재사용

## 실제 적용 기준

1. 시즌별 대표 장비·보석·영약·기름과 G/J/F/O의 정확한 원본·ID·정적 수치·중복 방지는 필수.
2. 실행에 사용한 SimC 버전/바이너리 SHA는 세션·DPS 캐시에 기록. 게임 빌드 문자열이 같음을 강제하지 않고, 빌드 관계/컴파일 출처의 독립 증빙을 별도 Gate로 만들지 않는다.
3. 일반 실행은 `V106_USER_RESULT.json`, 장기 실행은 `V291_RESULT.json`에 이미 저장한 관측 최고 CHMV, DPS, SEM, 95% 및 설정으로 결과 표시. 읽기 API는 SimC Native를 다시 실행하지 않는다.
4. 기존 실행 오류는 직접 전달하며, 검증이라는 명목으로 정상 실행 경로를 차단하지 않는다.

**권한:** 격리 브랜치만 변경. main·v003 immutable·Project UI·공식 승격은 미변경.
