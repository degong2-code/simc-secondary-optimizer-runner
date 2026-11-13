# v400 — A6 Wago DB2 원본(BASE) 실 수집 영수증·동일 빌드 봉인/재사용 수락

> **정확 판정:** `READY_SCOPED — CURRENT_KR_70783_WAGO_DB2_TEN_TABLES_BASE_ONLY`. **현재 KR Retail 12.1.5.70783**에서 기존 승인 Wago.tools `v161`의 **10개 필요 DB2 원본 CSV** 실제 수집·각 CSV SHA/크기·빌드/locale/전달 및 실제 `v163` 조인 증거를 재사용한다. 제품 `v216`의 `v217` 봉인/재사용, 소스 수정·빌드 혼합 차단은 실제 오프라인 회귀로 검증했다. **새 시즌 전체 장비/효과·G/J/F/O·A7 WorldStateExpression·전체 제품/Windows E2E를 인증한 것은 아님.**

## 1. 실제 70783 원본 영수증 (이전 실 실행의 재사용, 새 Native/대용량 수집 아님)

- **[#43357639329](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329)** / [compact original artifact #14006193832](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329/artifacts/14006193832): tested HEAD `b92b11f186fc3201286f8e30a0b4684d1dc0b203`. 빈 source root에서 공식 Blizzard BPSV가 **KR Retail 12.1.5.70783** / SHA `a30d4de410d5ff65a682940077e7b1dc200a6a1deed095dd02676c57a5104440`로 자동 발견; Blizzard/WCL 인증 원본 뒤 **`v161.snapshot(folder,build=discovered_build,make_archive=False)`**가 **10개 DB2 CSV, 합계 62,280,767 bytes**를 `wago.tools/db2/{table}/csv?build=12.1.5.70783&locale=enUS` 형태로 실제 수집. 원본 `v161/receipt.json` SHA-256 `4a2a63fae00bf6e230c5453a2ab3e3a71fe6df233b92a3d246d352ac5c12d5a6`; compact artifact에 10개별 CSV SHA/bytes 기록 (원본 CSV·인증 토큰/키 자체는 artifact에 없음). Artifact ZIP digest `sha256:d82b63ef0cd51e2e0bcd6ddeaf6aeb666b7cd1041d14322c588e0ff52902beb2`.
- 같은 실제 실행에서 `v163.discover_unique_live_scope` 및 `v163.build_index`가 **DB2 ExpansionID 11, DisplaySeasonID 37, WCL ExpansionID 7, RaidJournalTier 505**를 독립 namespace로 구분하고 **Raid10/M+8 유일 관계, unknown0** 확인. 즉 DB2 CSV의 유효한 source 빌드·필요 테이블·소스 소비 경로 실증이며, 개별 조건부 item/WSE를 무조건 승인하지 않음.
- **진짜 KR 70783 전체 62MB를 오늘 다시 받거나 `v217` 실제 서버 stage를 새로 생성하지 않았다.** 당시 v393은 standalone `v161.snapshot`→`v163` 실행. 오늘의 `v217` 봉인/캐시와 `v216` 제품 경로 검증은 아래 **별도 오프라인 합성 회귀**이며 이 두 증거를 하나의 실제 Native/Windows End-to-End 실행이라고 과장하지 않는다.

## 2. 기존 제품 경로 분석: REUSE/CONNECT (소스 코드 변경 없음)

1. **`v289` → `v216.collect_wago_new_season_source(expected_game_build)`**: 공식 Retail 빌드를 파라미터로 전달. `v161.BUILD="12.1.5.70575"`는 역사 standalone CLI 기본값이며 **제품 일반 경로는 항상 요청에서 검증한 build를 `snapshot(..., build=expected_game_build)`로 명시**한다. 새 시즌 정답/레이드명/DB2 ID/예산 시드를 넣지 않는다.
2. **`v161.snapshot`**: 고정되어 있는 필요한 10 DB2 source table만 bounded HTTP CSV 스트리밍, 원문 바이트를 받는 동안 SHA256·크기 기록, `receipt.json`에 원본 URL/빌드/enUS/원본 SHA 기록; ZIP 아카이브는 정상 제품에서는 `make_archive=False`. 전체 시즌 DB 크롤링 없음.
3. **`v217.execute_stage`**: `fresh-wago-db2`의 `receipt.json + 10 CSV`(11 output)에 코드 fingerprint·빌드·locale·테이블셋 입력 정체성 봉인. 최초 출력은 각 파일 원문 SHA로 검증, 재사용 시 같은 SHA로 검증 후 다운로드0, 잘못된 빌드·파일 변조·receipt 변조는 차단. `v216`은 **v161 계산한 테이블 SHA/바이트와 v217 봉인 기록을 동일한 파일에 대해 비교**하여 어느 한 쪽의 메타데이터를 믿고 합격하지 않음.
4. **`v163.verify_snapshot(..., verified_tables=v217_metadata)`**: 이미 v217이 파일 바이트를 검증했을 때 동일 빌드·locale·10 source table/바이트 수/원본 메타 일치를 확인하고 **전 CSV를 추가로 SHA 계산하지 않음**. 단, 독립 CLI/비봉인 사용 `verified_tables=None`은 각 10 CSV를 직접 전체 SHA 검사한다. 검증된 상위 호출자 없이 `verified_tables`를 임의 공급한 것이 실제 원본 인증과 같다고 주장하지 않는다.
5. **`v216` → A7 이후**: DB2 raw source만 확보해서 효과/WorldStateExpressionID·사용자 장비·G/J/F/O가 자동 승인되는 것은 아니다. 필요한 테이블/출처를 소비하는 downstream stage에서 선택한 세부 범위·옵션·SimC 입력 검증이 별도 필요.

## 3. 이번 신규 실제 회귀 영수증

- 새 `tests/test_v161_db2_source_provenance_offline.py` **4/4 PASS**: 합성 미래-like 빌드 `13.0.0.88888`의 10개 URL/locale/source identities와 streaming SHA; 독립 `v163.verify_snapshot`의 wrong-build/koKR locale/same-size tamper/size 차단; `v217` 11 source output 봉인·원본 SHA/size 교차 확인·동일-stage 0다운로드 0 receipt writes·다른 빌드 input fingerprint 차단·같은 크기 변조 차단; download size guard 시 COMPLETE receipt 부재. **합성 bytes는 실제 70783 자료를 대체하지 않는다.**
- [실 GitHub focused Actions **#43366468001**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43366468001), tested HEAD `d21cbed88975f2cb471cf91d4583c9b073f27428`, Ubuntu Python 3.12. A2(4)+A4(v155 5, v242 4, v332 5, v154 6)+A5(3)+A1(v155 7, v163 8)+**A6(new v161 4, existing v216 product-path 1)**+v113(60)+v181(3) = **110 실행 시도 / 109 PASS / 1 조건부 SKIP / 0 FAIL**. `v216_environment_build_coordinator.EnvironmentBuildCoordinatorTests.test_live_collector_reuse_by_build_without_old_season_or_native`가 실제 사용자 product-stage 경로의 최초 10 synthetic source HTTP→후속 cache 0요청/0 Native를 확인. `v163`의 1 SKIP은 별도 외부 CSV 파일 마운트 시에만 도는 선택 테스트로, 이미 #43357639329에서 실제 CSV 10개를 다운로드·조인한 독립 증거가 있음.
- **자원:** 이번 신규 Wago HTTP0/Blizzard HTTP0/WCL HTTP0, Native0, SimC 반복0; 합성 오프라인 CI CPU·I/O로 한정. 중복 소스 폴더/최종 파일 수동 복사 없음, 배포 ZIP `v181.select()` 단일 소스 유지. 코드 변경은 **test + focused Actions 연결만**, 기존 v161/v217/v216/v163 효과/예산/수집 로직은 변형하지 않음.

## 4. 판정·다음

**A6 = `READY_SCOPED — CURRENT_KR_70783_WAGO_DB2_TEN_TABLES_BASE_ONLY`**. 현재 실제 빌드 원본과 generic build source/10 tables/원문 SHA·제품 봉인·재사용의 해당 기능 범위를 완료로 판정. 다른 시즌 미출시 실측을 선행 요구하지 않는다.

**A7 = `PENDING_SCOPE`**: 시즌 아이템 소속/WSE 조건을 현재 실제 선택·소비 범위에서 정합 검증. `v163`이 의도적으로 `full_season_completeness_confirmed=False`, `season_membership_completely_verified=False`를 보존하며 선택되지 않은 항목의 미해석을 전역 차단하지 않는다는 정책을 유지. 기존 v393 10 DB2 SHA 및 현재 v216 연결을 재사용하고, 정확한 **제품 선택 범위·WSE 소유자/실제 효과 조건**부터 추적. 새 전 시즌 DB·전 전문화 Native 인증 Gate 불필요.

**권한:** 격리 브랜치만. `main`/v003 immutable/Project UI/Work OS/공식 승격·주 제품 소유권 무변경. 같은 시즌 static source 캐시는 SimC revision만으로 강제 폐기하지 않음.
