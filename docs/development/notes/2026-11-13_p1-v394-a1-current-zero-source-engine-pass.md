# v394 — A1 확장팩·시즌 **범용 발견 엔진** 현재 ZERO-SOURCE 실증 PASS (미래 시즌 미출시 별도 Gate 없음)

> **범위 엄격 구분:** [최신 직접 사용자 결정](../POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md)에 따라 A1의 **확장팩·현재 활성 시즌/콘텐츠 후보를 코드가 스스로 식별하는 기능**을 `ENGINE_AUTODISCOVERY_PASS — CURRENT_KR_RETAIL_70783_ZERO_SOURCE`로 판정한다. **A7 개별 아이템 시즌 소속/WSE 전체, A10/B/C/GJFO 설치, 사용자 E2E, 실제 미래 시즌 아이템 수치까지 PASS했다는 뜻은 아님.** 78개 원장 해당 행에서 이 구분을 유지한다.

## 1. 신뢰할 원본 영수증과 테스트 HEAD

| 실행 | 코드/원본 범위 | 실제 결과 |
|---|---|---|
| [#43356500862](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43356500862) | 최초 실제 GH Actions, **빈 루트·정상 Blizzard/WCL 시크릿·현재 빌드 자동 탐색** | BPSV 원본 70783 SHA 확인, Blizzard 4 인덱스 HTTP 200/current keystone 18, WCL 2요청 인증 성공. 첫 parser 실패 `WCL_JOURNAL_ID_INVALID` (구 과거 zone 비양수 정수). source stage PENDING, Native0. |
| [#43356817887](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43356817887) | 같은 실제 원본, v390 `journalID` 비양수 sentinel을 **원문 보존/정당한 journal 인식은 양수만** | `WCL_ZONE_EXPANSION_ID_REQUIRED`로 첫 source semantic 결함 이동. 비양수 expansion ID를 임의 현재 확장팩으로 승격하지 않음. |
| [#43357129807](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357129807) | v391 원본 aggregate 진단 | WCL **44 zone** = `FROZEN_POSITIVE_ID=40`, `FROZEN_NONPOSITIVE_ID=2`, `UNFROZEN_POSITIVE_ID=2`. 이름·ID·키 비노출 집계. |
| [#43357314268](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357314268) | v392 딱 **frozen=true 비양수 ID 과거 2개만** scope 후보 제외. 비동결·미확정 expansion 누락은 여전히 fail-close | WCL 42개(동결40/비동결2) **인증 source report SHA `7321eb320f556cd57346ac07bb3722c2e83df09cd378b50a3cfb36af88cb5bc1`**, 기존 v242 stage 봉인/HTTP 8요청, `AUTHENTICATED_SOURCE_DISCOVERED_SEASON_JOIN_PENDING`. |
| **[#43357639329](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329)** / **[원본 요약 아티팩트 #14006193832](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329/artifacts/14006193832)** | **HEAD `b92b11f186fc3201286f8e30a0b4684d1dc0b203`**, 완전 빈 root에서 **v289 → v242/v155/v217 → v161 10 DB2 CSV → v163 동일 빌드 후보 유일 판정 + `build_index` 실제 실행**. 현재 확장팩명/ID, 시즌, 레이드/던전명, 이전 카탈로그·G/J/F/O, 캐시·AI의 수동 판정 **0 주입**. | **`A1_REAL_SOURCE_IDS_AND_DB2_JOIN_OBSERVED`** (빈 root, Native0). 공식 KR Retail **12.1.5.70783** / BPSV SHA `a30d4de410d5ff65a682940077e7b1dc200a6a1deed095dd02676c57a5104440`, Blizzard 실제 현재 Keystone Season ID **18**, WCL expansion ID **7**, 같은 빌드 DB2 장비 ExpansionID **11**, DB2 DisplaySeasonID **37**, RaidJournalTier ID **505**. 유일 레이드 **The Venomous Abyss**, 유일 M+ **Mythic+ Season 2**, 우두머리 **10/10**, M+ 던전 **8/8**, 인덱스 `unknown_count=0`. |
| [#43357352036](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357352036) | v392 A1 값·확장팩명이 바뀌어도 ID 고정 없이 작동하는 합성 회귀 + 기존 v113/DB2 소스/ZIP | Python `6+8+60+3=77` 검사, **76 PASS/1 SKIP/0 FAIL**. 1 SKIP은 별도 외부 DB2 실물 스냅샷을 테스트 프로세스에 마운트할 때만 도는 역사 선택 케이스. 위 #43357639329에서 **그와 별도로 실물 DB2 10개는 실제 다운·조인 완료**. |

### 정확 원본과 효율
- 마지막 Actions source report 원문 SHA `7321eb320f556cd57346ac07bb3722c2e83df09cd378b50a3cfb36af88cb5bc1`, v242 stage 봉인 영수증 SHA `cd9a8cae7e204919e9406f105da0ccab26839d26867b37a6b15fb087a3cd1fca`. DB2 10테이블 **62,280,767 bytes**, `v161/receipt.json` SHA `4a2a63fae00bf6e230c5453a2ab3e3a71fe6df233b92a3d246d352ac5c12d5a6`. 각 10개 테이블 SHA는 위 GitHub 실제 compact artifact에 기재. 인증 및 Wago 원본은 임시 root에만, 저장소/배포 ZIP·사용자 캐시/개인 비밀키·정답 seed 0. **Native0, DPS0, SimC/AI0**, 전체 26전문화/모든 ilvl 재검증 없음.
- 정확 ID 네임스페이스: `Blizzard current keystone=18` ≠ `DB2 DisplaySeasonID=37`, `WCL expansion=7` ≠ `DB2 ItemSparse expansion=11`; 서로 같다고 가정하지 않고 **동시즌 WCL 활성 zone/정확한 M+ 8개 이름 집합/DB2 JournalTier·레이드 장비 클래스2·4 ID·현재 빌드 SHA**로 조인. 0/비양수 없는 확장팩으로 default 금지. WCL schema의 `zones(expansion_id)` 생략·`expansion.id` 등은 공개 [WCL WorldData](https://www.warcraftlogs.com/v2-api-docs/warcraft/worlddata.doc.html)/[Zone](https://www.warcraftlogs.com/v2-api-docs/warcraft/zone.doc.html).
- `#43357639329` receipt의 `a1_engine_autodiscovery_pass=false`는 테스트 스크립트에 **항상 false로 초기화 후 변경하지 않는 자체-인수 미평가 안전 sentinel**이다. 실제 조인 FAIL이나 `v163`의 별도 전체 시즌/아이템 소속 검증 결과가 아니다. **이 문서와 78개 원장의 A1 ENGINE 판정은 v393 원본 성공 + 현재 사용자 합격 정책 + 별도 변경 ID 회귀 대조를 거친 사후 범위 판정**이며 과거 immutable 영수증을 수정하지 않는다.

## 2. 완료된 A1의 범위 / 여전히 미확정인 사항

- **PASS A1 ENGINE 기능:** 정답·AI 개입 없는 소스/시간·필드 의미 기반 KR 공식 빌드 발견, Blizzard 쐐기 시즌 현재 ID, WCL 활성 2개 원본 그룹, 10개 현재 빌드 DB2 CSV 실 원본 기반 유일 활성 레이드/M+/확장팩/DB2 시즌/티어 관계 발견. 다른 이름/ID/날짜·복수/결손 후보 fail-close 회귀; 시즌 출시를 기다리는 미실측 선행 Gate 불필요. v385 시즌 이벤트 같은 빌드 원본 재사용 방지 v113 오프라인 회귀 PASS.
- **A7 및 나머지 별개:** `v163.season_membership_completely_verified=false` 및 `v163.build_index.full_season_completeness_confirmed=false`, `SOURCE_CANDIDATES_WITH_UNRESOLVED_SEASON_CONDITIONS`는 **개별 아이템/WSE 전체 시즌 소속·상품군/선택 G/J/F/O 수치/Native/설치** 미확정을 뜻함. 78 항목의 이후 A7·B~G/최종 ZERO-SOURCE→USER-E2E로 확인. A1의 엔진 발견 PASS를 해당 후속 미확정 때문에 철회하지 않는다. 새로운 시즌 공개 후 호환성·새 원본 정합은 갱신 대상.
- **기록 규칙:** 소스 PASS·범위 PASS·전체 시즌 콘텐츠 PASS·완제품 E2E PASS를 별도 표현. 해당 테스트 전용 GitHub workflow success 자체와 A1 합격 판정도 구별한다. 합격 정책 [정본](../POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md)과 [인계 v386](../../CHAT_CONTINUITY_HANDOFF_20261113_P1_V386_ZERO_SOURCE_GENERALIZATION.md)에 이 근거 연결.

## 3. 다음 작업

**A2 현재 게임 빌드**로 순차 진입한다. v289 공식 BPSV 정체성 → v113 생략된 game_build 자동 연결 → v242 expected_build → v161 Wago CSV/receipt → v163 같은 빌드 검증, 지역 변경/빌드 오류/다른 빌드 캐시 fail-close를 과거 증거와 이번 source v393로 확인하고 불필요한 새 Wago/SimC/Native 반복은 하지 않는다. A2의 적용 범위를 증거로 판정한 다음 A3 진행.

**권한:** 격리 브랜치만 변경. main/v003 immutable/Project UI/Work OS/주 제품 개발 소유권 불변. 앱 TXT 272개 베타 후보/기존 패키저 단일 출처 유지; A1 코드를 별도 완성 폴더에 복제하지 않는다.
