# v398 — A4 Blizzard 원본(BASE) **검증 완료(현재 인증 인덱스 소유권 범위)**

> **판정은 원본의 실제 역할에 한정한다.** A4의 **현재 KR Retail 12.1.5.70783 Blender/WCL 정상 자격 증명 조건에서 사용되는 4개 Blizzard 인증 인덱스의 원본·SHA·제품 소비 소유권**은 `READY_SCOPED — CURRENT_KR_70783_BLIZZARD_INDEX_BASE_ONLY`. Blizzard에서 개별 장비의 정적 rating, 레이드 아이템의 계절별 WSE, SimC 효과, 사용자별 선택 장비의 전체 장비 DB를 가져왔다는 뜻이 아니다. A7/B~G·최종 USER-E2E는 별도.

## 1. 원본 소유자 → 실제 제품 소비 경로 (새 API·Gate 없음)

| 질문/제품 소비 필드 | 실제 소유자·코드 | 수락된 현재 범위 및 금지된 과장 |
|---|---|---|
| 현재 Keystone 시즌의 공식 `current_season.id` | **Blizzard API** `v155`의 `keystone_season_index`; `v242` source receipt, `v163.build_index.blizzard_keystone_season_id`으로 결과 보존 | 실제 관측 값 18. **DB2 DisplaySeasonID(37)와 동일 숫자라고 가정하지 않는다**. 단독으로 현재 레이드·던전/아이템 소속 전체 증명 불가 |
| Dungeon index / period index / journal-instance index | **Blizzard API** 기존 v155 3개 source index GET; `v242` JSON + sealed `v217` | 모두 현재 빌드 출처·source context. `v163`에서 실제 raid/M+ 선택을 직접 이 세 Blizzard index의 목록으로 확정한다고 주장하지 않는다. `v163`의 WCL→DB2 도감/맵 관계가 별도 선택 |
| 현재 선택 raid boss/M+ dungeon·tier·최초 item ID·장비 class/slot | **WCL authenticated candidate + same-build Wago DB2**, `v163.discover_unique_live_scope/build_index`→`v216._join_authenticated_season_source`→`_fresh_ordinary_gear_source_stage`(`v165/v166/v167`) | v393 실물 10 DB2 table/원본 SHA + v217 stage, raid10/M+8 소스 조인. 장비 후보의 **아이템 ID 원본은 Blizzard 4 index가 아니다**. 개별 조건부 WSE·선택 정확 효과는 별도 A7·B·D |
| 직접 효과 레코드 / 소비품·보석·기름 / SimC 입력 | `v216`의 별도 동일 빌드 `ItemXItemEffect`·`ItemSparse`/SimC source 및 v189→v190, v220/policy-A | 고정 G/J/F/O/E/O·item effect 인증/소비는 이후 범위; **Blizzard index만으로 등재/수치 승인하지 않음** |
| 한국어 **표시명만** | `v332_blizzard_ko_item_labels.py`, 실제 선택된 정확 ID에 한해 `/data/wow/item/{id}` (명시 opt-in). `v167.public_options`는 이미 검증된 시즌 DB2/SimC 후보의 `name_ko`만 선택 첨부 | 추가 HTTP는 **일반 환경 Build의 필수 선행요건 아님**. v332 파일 없음/불일치는 원본 아이템 ID·사용자 선택·예산을 바꾸거나 BASE를 차단하지 않고 표시명만 미노출. 제공 여부·ID·원본 SHA는 v332 별도 검증 |
| 연구용 레이드 encounter loot / crafting Blizzard API | `v154_blizzard_season_loot_index.py`(사용자가 선택한 encounter IDs), `v157_blizzard_craft_probe.py`(옵트인/연구) | **정상 v216 시즌/장비 자동 구축에 필수 의존성으로 결합되어 있지 않다**. 전 encounter/item API를 A4 완료 필수 원본으로 신설하지 않는다 |

## 2. 변경 내용

- **v242**: `blizzard_source_lineage(report)`를 **부작용 없는 진단 함수**로 추가하고 정상 `collect` 결과에 `blizzard_source_lineage`를 출력. `v155`가 실제 HTTP response body에서 읽은 `original_http_body.raw_response_sha256/raw_response_bytes`에 대해 네 인덱스의 유효 SHA 형식·바이트 범위·`HTTP_200` 여부를 확인하며, 이전 봉인 source에 네 raw SHA가 없다면 `blizzard_index_originals_verified=false`로 정확히 남긴다. 인증 source stage 또는 사용자가 선택한 아이템 자체를 독자 승인하는 신규 Gate가 아니다.
- `selected_item_id_and_stats_blizzard_proof_claimed=false`, `selected_item_data_owner=SAME_BUILD_WAGO_DB2_AND_PINNED_SIMC_DOWNSTREAM`, `optional_ko_name_owner=V332_ID_BOUND_DISPLAY_ONLY`, `current_season_membership_certified_here=false`를 분리 보고. 정확한 아이템/기름/특수장비와 시즌 WSE 미인증을 조용히 올리지 않는다.
- **오래된 테스트 오류 복원**: `tests/test_v155_season_api_probe_offline.py`가 v387에서 제거된 `select_midnight_expansion` 및 `midnight_zones`를 계속 기대했다. 이를 범용 `zones[].expansion_id` 및 `ALL_WCL_EXPANSIONS` 계약으로 고쳤다. 연구/역사 테스트에서도 현재 시즌명 하드코딩을 부활시키지 않는다.
- **실제 독립 테스트**: `tests/test_v242_blizzard_source_lineage_offline.py` 신규: 네 body SHA 출처 소유권, 불완전 과거 원본은 미인증으로 보고, `v217` 실제 stage 1회 봉인·다음 동일 빌드 재실행 시 **네트워크0/Native0·영수증 SHA 동일**, 인증 키 기록 0. `tests/test_v332_blizzard_ko_item_labels.py` 기존 standalone unittest import 경로만 교정하고 한국어 이름 파일이 없을 때도 `v167.public_options` **ID/후보/slot 불변, 새 API0** 검사 추가.

## 3. 확인된 영수증 · PASS 범위

- **실제 현재 Blizzard 응답 바이트**: [Actions #43359408019](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43359408019), 4개 GET `HTTP_200`, 각 바이트 크기/SHA-256은 [v397 상세 원본](2026-11-13_p1-v397-a4-blizzard-original-http-body-provenance-progress.md)에 기록. `v242` source stage 봉인 성공. v155/v242 코드 변경 이후 실제 source-only 재실행도 [Actions #43363969292](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43363969292)에서 정상 완료 (원본 네 SHA를 별개 아이템 수치 증명으로 사용하지 않음).
- **첫 새 focused CI FAIL(원인 확인)**: [Actions #43364082035](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43364082035) A4 v155 **5 PASS**, 신규 v242 **4 PASS**; 기존 v332 standalone 테스트가 `runner/`를 import path에 추가하지 않아 `ModuleNotFoundError: v155_season_api_probe`. 이는 소스 오류가 아닌 독립 테스트 경로 오류로 해당 테스트 한 파일에서 바로잡음. 실패 영수증은 삭제/숨김 처리하지 않음.
- **최종 새 focused Python 실제 PASS**: [Actions #43364420119](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43364420119) tested `5d5af73907c3a912e1a7ded46e1e1e5d46696a65`, Ubuntu Python 3.12, `v289 4 + v155 old5 + v242 new4 + v332 5 + v154 6 + v155 all-expansion7 + v163 8 + v113 60 + v181 3 = 102` 시도, **101 PASS / 1 SKIP / 0 FAIL**. `v163`의 1 SKIP은 외부 실물 DB2 snapshot 별도 마운트 조건; 별도 [v393 실제 10 DB2 원본 유일 조인](2026-11-13_p1-v394-a1-current-zero-source-engine-pass.md)은 완료된 실제 증거로 재사용. 가상 카탈로그 v213은 패키지 CI fixture일 뿐 ZERO-SOURCE로 승격하지 않는다.
- **자원·안전:** 새 Native0, 새 대규모 DB2/26스펙 반복0, 원본 Blizzard 4개 index/API URL·사이즈 제한 불변, **원본 복사/별도 배포 폴더0**. v242 read-only lineage는 기존 source report 단일 로드 후 계산하며 블리자드 개인 키/OAuth 토큰/원문 응답 미기록. main/v003/Project UI/공식 승격 변경 없음.

## 4. 판정 및 다음 ID

**A4 = `READY_SCOPED — CURRENT_KR_70783_BLIZZARD_INDEX_BASE_ONLY`**. 조건: 정상 승인 API 권한의 현재 실 원본 4 인덱스 SHA/HTTP 증거, 기존 v242/v217 seal, `v163/v216`에서 현재 활성 선택 콘텐츠와 item ID의 **서로 다른 원본 소유권**을 코드 및 테스트로 확인. 다른 시즌 데이터 미출시를 이유로 이 기능을 미완료 처리하지 않는다.

**미검증 또는 별도 항목:** 새로운 원본을 쓸 때의 공급자 API 호환성, 특정 유저 선택의 item/consumable 수치 소스, 시즌 멤버십·WSE(A7), 현재 전체 G/J/F/O B/T 설치, SimC/USER-E2E, 선택적 v332 한글 공식 품목 이름 범위. 이들은 A4 BASE 인덱스의 합격을 철회하는 조건이 아니라 각각 해당 제품 소비 항목에서 검증한다.

**다음 = A5 WCL 원본(BASE)**: A1/A3/v155의 실 authenticated all-expansion/선택 raid10·M+8 source 및 v163 same-build 조인 증거를 재사용하고, WCL 원문 HTTP SHA의 제공자 소유권과 stage 재사용·요청량 상한을 최소 검증. 새 전 확장팩 대량 HTTP/DB2/Native 반복은 하지 않는다.
