# v399 — A5 WCL 원본(BASE) 현재 ZERO-SOURCE 구조 검증: 2개 GraphQL 원문 및 DB2 경계 READY

> **판정:** `READY_SCOPED — CURRENT_KR_70783_WCL_GRAPHQL_BASE_ONLY`. 실제 WCL 확장팩 목록·전체 zone **원문 HTTP response** 2개와 각각의 **GraphQL request body** SHA256을 정상 WCL API 자격 증명 하에서 엔진이 직접 확보하고, 기존 v242/v217 봉인 및 v163 동일 빌드 DB2 선정 관계를 확인했다. 이는 WCL만으로 현재 모든 아이템·장비·raid 시즌 소속을 인증했다는 말이 아니다. 미래 미출시 시즌에서 다시 실측해야만 이 코드 기능이 합격한다는 별도 Gate는 두지 않는다.

## 1. 실제 출처, 실행 HEAD, 영수증

| 증거 | 범위·실측 결과 |
|---|---|
| [WCL source-only 실제 GitHub Actions #43365490208](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43365490208) | tested HEAD `b4dc028c661a6e5effee8db99b5ad58fa70dacfa`. 정상 인증 WCL 자격 증명, 공식 KR Retail 빌드 **12.1.5.70783** (Blizzard BPSV SHA `a30d4de410d5ff65a682940077e7b1dc200a6a1deed095dd02676c57a5104440`), Blizzard 4 데이터 + WCL GraphQL 2 요청, 네트워크 범위 합계 기존 8(OAuth 2 포함). `AUTHENTICATED_SOURCE_DISCOVERED_SEASON_JOIN_PENDING`은 WCL 단독 결과이며 아래 DB2 증거가 따로 존재. Native0. |
| WCL `expansion_index` | **296 bytes**, GraphQL request-body SHA256 `ee42860a946c1e5a740d5ecfe17ec1922e45fd8e58eb6dc40c71fdaf81368617`, **원문 HTTP response SHA256 `417bcf6818ea7c288151a1f8752402a4456edd44a975f7037302d66dbbb4ad33`** |
| WCL `all_expansion_zones` | **23,857 bytes**, request-body SHA256 `377f720590ba5b6f6412185ed7eaf386fe6f3ad2df72fdc0e1cf455d44a05f09`, **원문 HTTP response SHA256 `f2603768896e37772a168fe35104e55e08e95ac3029b158b7795d55648474007`** |
| [새 raw provenance compact artifact #14010345906](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43365490208/artifacts/14010345906) | GitHub artifact ZIP SHA256 `e409cbe04f0375a0e76d2d7863177a5a43ed0cba014998dac8d56e0ac8bcffea`. WCL 원본 response bytes 자체·OAuth·사용자 키는 영수증에 저장하지 않음, 해시/길이/요청 정체성·source scope만 저장. |
| [기존 strict ZERO-SOURCE DB2 자동 조인 #43357639329](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329) | 별도 독립 실물 A1/A3 증거 **재사용**, 같은 현 빌드의 WCL 활성 2 zone, WCL expansion 7 ≠ DB2 item expansion 11, DB2 DisplaySeason37, Blizzard current Keystone18, raid10/M+8 **유일 관계**. A5의 WCL 성공과 실제 시즌 소속·아이템 승인 증거는 별개 경로에서 결합됨. 신규 10개 DB2 CSV 다운로드 불필요. |
| [국소 Python Actions #43365447503](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43365447503) | tested `0bc84c7bb14b636cb703244b6495946b6506cb23`, Ubuntu 3.12, 10묶음 총 **105개 시도 / 104 PASS / 1 SKIP / 0 FAIL**. A5 신규 `v242` WCL 3/3 PASS. 유일 SKIP은 외부 DB2 CSV 별도 마운트 선택 케이스. |

## 2. 기존 제품 기능과 정확한 소스 소유권

- **v155의 두 GraphQL 요청은 이전과 동일**: `{worldData{expansions{id name}}}`와 `worldData.zones {id name frozen expansion{id} encounters{id name journalID}}`. 확장팩명·시즌ID·레이드 이름을 정답으로 주입하지 않는다. `frozen=True`이고 확장팩 ID 불명확한 과거 zone 2개는 A1 검증대로만 후보 제외; 비동결/미해석 후보는 fail closed.
- **v155에 추가한 증거:** `report.wcl.original_graphql_http_bodies.{expansion_index,all_expansion_zones}` 각각에 `request_body_sha256`, `raw_response_sha256`, `raw_response_bytes`. `source_proof`의 기존 max 1.5MB/12초 제약 유지, OAuth token에는 source proof 인자를 전달하지 않는다. GraphQL POST payload는 고정 query+variables만 포함; Authorization header/토큰 원문/해시는 저장하지 않는다. **신규 API 호출 0**.
- **v242 `wcl_source_lineage`:** 위 두 키에 정확한 SHA/바이트 유효성·두 응답 존재·source status를 읽기 전용으로 반환. 과거 WCL source report에 원문 SHA가 없으면 `wcl_original_graphql_bodies_verified=false`, 기존 stage를 소급 인증하지 않는다. `additional_graphql_requests=0`, `native_calls=0`, `season_membership_certified_here=false`, `exact_same_build_db2_join_required=true`. 기존 v217 stage SHA/입력 fingerprint/캐시를 재사용하며 **새 효과/시즌 인증 Gate 없음**.
- **실제 소비:** `v163.wcl_zone_sources`→`discover_unique_live_scope`→`build_index`가 활성 WCL raid/M+ 후보를 사용해 동시즌 Wago DB2의 `MythicPlusSeasonTrackedMap`, `JournalInstance`, `JournalEncounter`, `ItemSparse`와 유일하게 조인. `v216._join_authenticated_season_source`가 같은 빌드/원본 SHA로 봉인. **WCL expansion.id를 DB2 ExpansionID로 그대로 대입하거나 WCL `frozen=false`만으로 시즌 완성/개별 WSE item을 승인하지 않는다.**
- **회귀 신규 `tests/test_v242_wcl_source_lineage_offline.py`**: 2 OAuth+4 Blizzard+2 WCL 네트워크 상한, 응답 원문 바이트/실제로 보낸 GraphQL body SHA 독립 대조, 다른 확장팩명/ID, 원본 누락/손상 fail-close, v217 같은 build sealed source 0재수집/0 Native·동일 receipt SHA, 비밀키/토큰 비기록. 기존 A1/A3/Blizzard/패키징 회귀 10개 묶음을 함께 실행.
- **구성 효율:** WCL 원본 2개 HTTP bytes를 이미 한 번 읽을 때만 해시 계산. 원문 중복 파일·별도 완성 `.py` 폴더·추가 시즌 효과 엔진/DB2 재수집/SimC Native 없음. 패키저 `v181.select()`에서 현재 v155/v242 파일을 단일 원본으로 포함.

## 3. 범위 판정 및 다음 ID

**A5 `READY_SCOPED — CURRENT_KR_70783_WCL_GRAPHQL_BASE_ONLY`**. 현재 실제 원본 2 GraphQL SHA·요청 정체성과 제품 소비의 WCL→DB2 연결이 있는 만큼, 공개되지 않은 미래 시즌 데이터 미측정이라는 이유로 A5 범용 기능을 미완료 처리하지 않는다.

**별도/미완료:** A7 개별 장비 시즌/WSE 검증, A6 DB2 동일 빌드 정적 원본 전체 SHA·재사용 수락, A8/A9 SimC source, G/J/F/O 자동 BUILD·B/T 및 사용자 E2E. 오늘 실제 WCL 성공으로 새 시즌 미공개 아이템의 숫자를 인증했다고 과장하지 않는다.

**다음: A6 DB2 원본(BASE)**. 이미 [v393 Actions #43357639329](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329)에서 실제 10테이블/62,280,767bytes SHA 다운로드·동일 빌드 검증 성공. 이를 읽기 전용으로 재사용하여 `v161` 원본 receipt 10 SHA·v217 cache reuse/test·제품 소비 `v216/v163`의 경계를 정확 재검증, 부족한 회귀만 보완. 62MB 중복 재다운로드/26-spec Native 반복 없음.

**권한:** 격리 브랜치만 변경; main/v003/Project UI/Work OS 공식 승격·기존 주 제품 채팅 소유권 변경 없음.
