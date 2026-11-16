# SIMC SECONDARY OPTIMIZER — 최신 M1/M2 실증·제품 완성 중심 독립 인계 (2026-11-16)

> **최신 우선 인계 정본. 다음 새 채팅의 첫 응답은 읽기 전용 독립 복원 후 STOP.** 본 기록이 GitHub에 존재하는 것만으로 실제 제품 코드·Native 검증·Project UI 적용·공식 Work OS 승격을 뜻하지 않는다.
>
> 인계 작성 **시작 시점** 격리 브랜치 HEAD: `23856b7e82b7ac85ed594ebe3a3eb06c2da1a493` (M2 CURRENT/로드맵 문서). 마지막 직접 코드/회귀 수정 HEAD `1d217d0df0777f5354371582b0132c700a0fdb96`(신규 v113 테스트). 이 SHA는 **스냅샷**이다. 새 채팅은 먼저 실제 브랜치/HEAD/최근 커밋/Actions를 재확인한다. 인계 문서 추가로 HEAD가 바뀌면 시작 시점 SHA를 최신 HEAD라고 반복하지 않는다.

## 0. 2026-11-16 M2 보존 ZIP 원본 직접 대조 추가 기록 (후속 작업, 신규 Native 0)

- **대조 대상:** 기존 GitHub Actions 원본 artifact v155 **#14219515672**, v523 **#14219371770**, 실제 70783 Native v343 **#13868303468**, v344 **#13897178782**, v417 **#14021859656**를 이 채팅에서 직접 읽음. GitHub branch HEAD 재확인 당시 `d9ed86d7...`이며 제품 코드/캐시는 수정하지 않음.
- **직접 확인한 무결성:** v155 인증 파일 `v155-live-season-api-evidence.json` SHA256=`d6786340acf1dd79695530103fc5ac7671a8c5d69d5589befc7f344bcc49b2d4` (기존 기록과 일치). v523 ZIP 속 원본 `wago/receipt.json` 실제 바이트 SHA256=`f004a82fa9da52646dea49ded14ff6db756d8f903bafd29ce29449d71d9f3c6b` (compact와 일치), 내부 10개 Wago 원본 CSV 각각의 SHA가 해당 receipt 테이블 SHA와 **10/10 일치**. `v522` CurrencyTypes SHA=`c1e91e4e17b622136d7c9a37c597cd0fe2409a2f5ccb494659014b154a04ef1f`는 별도 원본 identity이며 GJFO 설치 SHA가 아님.
- **기존 실 Native 설치 구분:** v343 원본 설치 manifest `5d655836c6f69382a1ca81d72346fa5d71dc78eb2ae029843b49dea532693a02`, v344 `278d3c52d4c9c272d8d2c89d7b02cff4abe05db1639bde80b58b14d99f4f4294`, v417 `2c80286fc487be337984abee707ceb8d0187ab266e78e78dc32620ed4b692475`. 이 아카이브의 내장 원본/JSON2/DPS 영수증에는 **각 실행의 원본 v161/v217 Wago 영수증 바이트·SHA와 `source_compilation.missing`이 없음**. 따라서 같은 빌드·ilvl 및 J/F/G 실증은 인정하지만 v523 Wago source와 이들 설치를 **동일한 exact source identity로 승인할 직접 비교 키가 없다**. 서로 다른 설치 SHA 자체는 결함/원본 변조 증거가 아님.
- **현재 결론:** 신규 코드 결함 또는 새 G/J/F/O 수치 결손을 확정하지 못했으므로 **STOP/REUSE**. 기존 자동 J, G, F/O, B/T, v212를 반복 구현하지 않음. 다음 최소 실증은 실제 사용자 `v113 season-build → v216` 원본 결과에서 `source_inventory`, `source_compilation.status/missing`, `required_core_source_owner_report`, 정확 `v217/v212` 설치/프로필 manifest SHA를 먼저 수집·대조하는 일. 선택형 원본이나 전체 시즌 membership을 새 BASE Gate로 만들지 않음.
- **이번 작업 비용·신분:** GitHub 보존 아카이브 읽기/로컬 해시만 수행, **신규 Native 0, 신규 Wago/Blizzard/WCL source HTTP 0, 신규 DB2 수집 0, 제품 코드/SimC 캐시 변경 0**. 이 기록은 현 시즌 새 물리 설치 성공·M7 완료·78 원장 PASS 변경이 아님.

## 1. 프로젝트의 목적과 정책 우선권

- **사용자 실제 목적:** WoW **26개 DPS 전문화만**(증강 기원사·탱커·힐러 제외) 대상으로 해당 시즌 미래 파밍 목표 아이템레벨 또는 수동 **기름 포함 최종 CHMV 총량 T**에서 **SimC DPS 최대화로 관측된 치명·가속·특화·유연의 절대 rating**을 찾는다. DPS, SEM, **95%만**, 관측 1순위와 통계적 우위 확정 여부, 실질적으로 다른 근접 대안 및 비율을 함께 제공한다. 전역 최적임을 주장하지 않는다.
- **일반 사용자 흐름:** 직업·전문화·종족·특성, 자동 시즌 기본 목표 ilvl 또는 사용자가 지정한 ilvl/최종 T, 장신구 2개, 선택 특수장비·제작장비·장식 최대 2개, 최고 품질 보석·영약·음식·물약·기름·영구 마부·전투조건. 내부가 대표 일반 장비·무기·4pc·주능력치/SimC 프로필을 구성. 현재 장비 전수 입력, 현재 착용 보조스탯 합계를 기본 재분배, 장비 조합 추천·파밍 경로·전체 아이템 DB는 **제품 목적이 아님**.
- **승인 산식:** `G`(목표 ilvl 대표 일반 장비/무기), `J`(검증된 기본 보석), `F`(검증된 최고 영약), `O`(실제 적용한 고정 기름). `B=G+J+F`, `T=B+O`, `c_final=c_base+o`; **사용자 수동 T 최우선** → `B=T-O`. 선택 특수장비의 정확 L은 G 내부 고정 하한이지 추가 합산이 아니다. 영구 마부 E 및 기름 O는 승인 예산/gear_*에 한 번만, 장신구 정적 스탯은 자유 G 밖, 제작 초깃값 50:50은 L 잠금이 아님.
- **새 시즌 자동화:** G/J/F/O와 함께 **기본 목표 ilvl(일반 Myth 강화 트랙 정상 최고 등급)**을 매 시즌 실제 원본으로 판단. **334는 70783 Midnight Season 2에 대한 검증된 예시**이지 미래 시즌 고정 기본값이 아니다. 사용자 수동 ilvl/T는 보호. source 불일치·모호·인증 결손이면 임의 추정/과거 수치 승계 대신 구체적 PENDING + 수동 ilvl 경로. 수동 ilvl이라고 그 ilvl의 G/J/F/O 검증을 면제하지 않는다.
- **SimC 책임:** 아이템·proc·APL·장식·DPS는 SimC. 우리 코드는 정확한 ID/ilvl/옵션/빌드/원본·SHA, 대표 장비, 정적 CHMV·L/E/O, Native JSON2 정합, 후보/SEM/95%·캐시/취소·재개/결과에 책임. 효과 동작 재구현 또는 별도 인증 Gate 금지.
- 권위: **최신 사용자 직접 결정 > 승인 v1.4.3/비충돌 정책 > GitHub 코드/CURRENT/Actions·Native 실증 > 과거 인계/노트**. v1.4.1 등 예전 노트의 '27 DPS·증강 포함' 및 예전 시즌 'J=138' 같은 역사 숫자를 최신 사용자 범위/70783 새 예산으로 복제하지 않는다.

## 2. 반드시 읽을 위치와 실제 증거를 찾는 순서

1. **본 문서**, `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` **맨 앞 최신 기록**, `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md`, `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`.
2. `docs/development/INDEX.md` → `FILE_MAP.md` → `EVIDENCE_INDEX.md`로 기능을 찾고, **실제 생산자 함수 → 호출자 → 소비자/캐시 → Actions·Native 영수증**을 확인한다. 일부 이름만 읽고 "미구현" 단정 금지.
3. `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md`, `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md`.
4. 이번 M1의 실제 영수증 `docs/development/research_receipts/p1_v523_live_70783_v155_v161_v163_v522_join_compact.json`, 기존 v343/v344/v417/v439 조건 일치 Native 영수증, 최신 M2 SHA 소유자 코드 `runner/v113_local_web_api.py`·`runner/webui/app.js`, `runner/v522_myth_target_currency_source.py`, `runner/v216_environment_build_coordinator.py`.
5. 역사 핸드오프 `docs/CHAT_CONTINUITY_HANDOFF_20261116_M0_M7_PRIORITY_READONLY_RESTORE.md`는 **11월 16일 초기** 개발 스냅샷이다. 당시 M1 미완료 표현을 최근 M1 실 원본 성공보다 우선하지 말 것. `LAST-Q&A(5).txt`는 최신 M2 사용자 전달 보조 자료, 자체 GitHub/CI 검증 대체 아님.

## 3. 이번 채팅에서 실제 진전된 M1/M2와 비용 (반복 개발 금지)

### M1 — 시즌 자동 기본 ilvl: 현재 70783 원본 실증 성공, 새 시즌 일반화는 별도

- 기존 `v289` Retail 빌드, `v155` Blizzard/WCL 인증 활성 시즌, `v161/v217` Wago DB2 CSV/봉인, `v163` 현재 시즌·활성 레이드 조인, **선택적 추가** `v522` CurrencyTypes 화폐 문구를 재사용/최소 확장했다. **새 시즌 DB 엔진 아님.**
- 인증 [v155 Actions #43852847676](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43852847676): Blizzard current keystone season 18, WCL Midnight Season 2 / The Venomous Abyss. 기존 인증 영수증을 재사용한 [v523 실 원본 조인 #43853612242](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43853612242): build `12.1.5.70783`, Wago 필수 10 CSV 62,280,767 bytes, DB2 DisplaySeasonID 37 / raid tier 505 / M+ 8 / raid bosses 10. `v522` 실제 CurrencyTypes `3441`·`3446` 두 ID는 **같은 일반 Myth 321–334**(별도 제작 318–331/특수 보상 최고 344와 혼동 금지). 정확한 기본 ilvl **334** source-only 성공.
- 실제 Wago CurrencyTypes SHA256 `c1e91e4e17b622136d7c9a37c597cd0fe2409a2f5ccb494659014b154a04ef1f`; v161 receipt SHA256 `f004a82fa9da52646dea49ded14ff6db756d8f903bafd29ce29449d71d9f3c6b`. 두 동일 Myth 레코드 정상 dedup, 서로 다른 시즌/강화 상한은 PENDING. HTML/잘못된 CSV는 봉인 전 차단. **full_season_completeness_confirmed=false**이나 기본 제품에 불필요한 시즌 전수 DB Gate를 신설하지 않음.
- v523 실 Wago 수집은 기존 인증을 **재호출하지 않았고 신규 SimC Native 0회**. 원본 ZIP artifact #14219371770은 기록상 **2026-11-18 10:59 UTC 만료 예정**. 다음 채팅은 원본 필요 시 가용성 확인 후 재사용하고, 문서 compact 영수증을 원본 전체 ZIP으로 가장하지 않는다. 실 수집 반복은 관련 변경이 실제 무효화한 부분에만.

### M2 — 자동 ilvl의 출처 SHA를 기존 G/J/F/O Build까지 전달: 코드/오프라인 PASS

- 제품 코드 추적에서 `target_ilevel → v216 시즌 G/J/F/O → v222 B/T → v212 정확 SHA 설치 → v218/v098/v096 사용자 대표 프로필` 경로는 **이미 구현**되어 있음을 확인. 새 G·J·예산·SimC 엔진 작성 금지.
- **실제 연결 누락만 수정:** `v113 /myth-target`의 `currency_csv_sha256`가 UI state에만 머물러 `/season-build`에 전달되지 않던 문제. [API `bb508e94`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/bb508e94186a672d8d01fd58b62893d4c2616411)에서 `auto_myth_target_source_sha256` 추가, `v522.verify`로 동일 build·기존 v161 receipt·CSV 원본 SHA를 **기존 설치 재사용 또는 새 원본/예산 Build 이전** 검증하고 변경·파손이면 fail-closed. [UI `9026cddc`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/9026cddc7b28591837688c41aa40f6906615a598) 전송, [web 결과 `3eae90d8`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/3eae90d85afbfff0aa292dec3064face1d0c118b) source SHA 진단. **수동 ilvl/수동 최종 T는 새로운 자동 source SHA 의존성 없음**. 자동 선택에는 기존 game-build drift 검사도 유지.
- [기존 v113 Win/Ubuntu #43864065490](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43864065490), [v182 UI #43864065528](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43864065528), [v181 Windows ZIP #43864065505](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43864065505), [focused reuse #43864065506](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43864065506) **SUCCESS**. 마지막 HEAD 23856b7e의 [78 계약 #43864809933](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43864809933) **SUCCESS**. 과도기 `593abdd5`에서 focused check 취소(cancellation) 기록이 있으나 마지막 `1d217d0` 실행의 해당 작업 성공을 재확인했다. **이번 최신 M2 변경 신규 HTTP·DB2·SimC Native 모두 0회**, 저장된 소형 CSV 로컬 SHA 확인만 추가. M2 신규 실제 물리 G/J/F/O 설치 SUCCESS로 승격하지 않는다.
- **기존 70783/334 Native(정확 조건 한정):** G=2850, J=92(일반 보석 4×23), F=165, O=0 → B=T=3107의 v343/v344/v417 실증. v344 환경 Native3 + 적응형 DPS Native64, v417 등 다른 정확 입력의 이전 Native 결과는 **그 당시 원본 SHA·대표 장비/특성/프로필/SimC 바이너리 identity에 한정**. 현재 v523 Wago SHA와 과거 G/J/F/O manifest SHA가 완전히 같은지 확인 전, '둘 다 ilvl334'만으로 새 v212 설치에 값을 복사/승격하지 않는다.
- **반드시 J 중복 개발 방지:** 기존 `v221 → v268/v266 → v271 → v216 → v222/v212` 일반보석 source·최고 품질·스탯 합계·`gem_id` 장착 경로 및 기존 실증 J92가 있다. 단일 명목 JSON을 보고 "J 엔진 미구현"이라 단정한 과거 인계/해석은 잘못이다. 신규 시즌 원본 수치 미검증 ≠ 기능 자체 부재.

## 4. 공식 M0~M7 진척 및 단 하나의 최우선 작업

| 단계 | 최신 확인 범위 | 다음 판단 |
|---|---|---|
| M0 기존 증거·정본 | source·캐시·Actions/Native 계보, 기술지도 있음 | REUSE/STOP; 역사 전면 재감사 금지 |
| **M1 시즌 원본/대표 목표** | **70783 인증 Blizzard/WCL + 실제 Wago CurrencyTypes → Myth 기본 ilvl334 source-only PASS**; 다른 시즌 자동화 전체·대표 4pc/G/J/F/O 일반화는 아직 미수락 | 동일 시즌 영수증 재사용; M2의 실제 설치에 필요한 빠진 필수 source owner만 확인 |
| **M2 G/J/F/O→B/T→v212** | 기존 예산/프로필 엔진 존재, source build·SHA 바인딩 회귀 PASS; 70783 과거 Native 실증 있음 | **최우선**: 실제 v523 원본과 기존 설치 source identity 대조, 최초 미확정 필수 항목만 고쳐 정상 v212 설치까지 확인 |
| M3 사용자 SimC·결과 | 70783 Windows Native 실제 기본 경로 성공, 캐시/중단·재개/95%·작업자 보호 구현·회귀 PASS | 동일 조건 REUSE/STOP; 새 실제 장애만 최소 FIX |
| M4 선택 장비·효과 | 검증/자동등록 경로 일부 있음 | 선택한 item/옵션만 실정합, 미선택 PENDING은 BASE 비차단 |
| M5 26 DPS 물리 유형 | 여러 무기·티어·전문화 실증, 26 전체 실 Native 수락 아님 | 진짜 신규 구조만 유형별 최소 검증 |
| M6 Windows 사용 품질 | v113 UI/API, v181 ZIP, 취소·재개·재열기 기반과 오프라인 PASS | 신규 사용자 첫 설치·오류·복구·UX 최소 수락 |
| M7 ZERO-SOURCE→USER-E2E | **PENDING** | 최후 단일 정상 경로로 실제 제품 수락, 역사 캐시/seed를 시험에서 격리 |

- `78_ELEMENT_COMPLETION_CONTRACTS.json` 78개, 축별 PASS `generic 27 / current_source 27 / product_integration 15 / historical 13`; **공식 15/78 COMPLETE**(3개 현재 기능·제품 축 기준; historical은 별도 기록), `policy.next_review=B10`, `full_product_e2e=PENDING`. **15/78은 제품 구현률 19%가 아니고 B10은 실제 개발 작업 순번이 아니다.**
- **딱 하나의 다음 작업(M2):** 먼저 **실제 70783 v523 authenticated+Wago source identity**와 기존 v343/v344/v417/v439 원본·Native 정적/예산 설치 identity를 비교. `v113→v216` 실 사용자 기본 요청, `v217/v191/v211/v213` 컴파일 입력, `v277` G, `v266/v271` J, `v281/v278` F, 선택 기름 O(미선택이면 0), `v222` B/T, `v212` 설치 SHA 중 **최초 실제 미충족 필수 source 또는 생산자→소비자 연결 하나**를 찾는다. `source_inventory`, `source_compilation.missing`, 정확한 same-build SHA/manifest 및 유효한 기존 캐시를 먼저 확인. 재현된 차단이 없으면 새 엔진·추가 Gate 만들지 말고 STOP/REUSE. 실제 필수 자료가 없는 경우에만 최소 수집/Native; 선택형 불확실성은 BASE 불필요 차단 금지.
- M2 결합이 실증되면 M4 선택지/정확 static L/E/O, M5 변경된 물리 유형, M6 사용자 Windows 품질, **마지막 M7** 순서. M3가 이미 성공한 경로를 재구현하지 않는다.

## 5. 상시 개발·인계 유의사항 — 특히 장기 프로젝트 중복 개발 방지

1. **매 기능 전 기존 것 찾기:** `INDEX → FILE_MAP → EVIDENCE_INDEX → 실제 생산자/호출자/소비자 → 과거 commits/Actions/Native/캐시`. 이름이 다른 동일 책임 기능, 미연결, 부분 구현, 단지 시험 미완료를 구별한다. **PENDING=미구현 아님.** 일부 파일만 읽고 새 엔진 착수 금지.
2. **판단 순서 `STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW`.** 이미 구현된 보석 J/시즌 수집/예산/대표 프로필/최적화/통계/캐시/복구를 반복 개발하지 않는다. 지난 오류가 재발하지 않도록 GitHub CURRENT·기술지도에 어디서 생산하고 어디서 소비되는지 기록한다.
3. **변경 전 사용자 관점·비용 설명:** (a) 사용자가 누르는 버튼/내부 흐름 정확 위치, (b) 실제 차단과 사용자가 얻는 개선, (c) 기존 코드·source·영수증 재사용, (d) 불필요한 수집/Native·새 기능 STOP, (e) Native·HTTP/DB2·CPU/RAM/I/O·캐시·실행시간 영향/최소 회귀. 형식적 새 승인 Gate가 아니다.
4. **시즌/예산 정확성:** 334·과거 B 참조/79×2·기름 16/16·J138·F165는 **다른 시즌으로 자동 복사 금지**. 같은 시즌에서도 동일 ilvl ≠ 동일 G/F/J/manifest/SHA. 보석·영약 최고 품질은 조건·효과·동일 빌드 근거가 있을 때 등록. 선택 특수장비 L, 정적 E, 고정 O를 중복 가산하지 않음.
5. **실증 등급 분리:** 구현됨 / 오프라인 PASS / 기존 Native 영수증 재사용 / 새 Native 실측 / 정확 GJFO 설치 / UI 실제 E2E / 공식 완료를 항상 따로 명시. `full_season_completeness=false`나 인증 없는 선택 상품 때문에 검증된 기본 환경을 무단 차단하지 않음. 실제 SimC 오류는 원문으로 보고; proc/APL 효과 독립 인증 Gate 신설 금지.
6. **기본 실행비:** 기존 same-season 정적 캐시를 SimC revision만으로 지우지 않는다. DPS 캐시는 바이너리·프로필/장비·후보·O·전투·iterations 정확 identity로 구분. 다운로드/원본 저장·Native 반복 최소화. 임시 일회성 검증 작업이 끝나면 영구 런타임 의존성으로 남기지 않고 영수증만 기록.
7. **범위/권한:** 새 적응형 엔진, 전체 시즌 장비 DB, 장비 추천·파밍 경로, 별도 효과 인증, 26 DPS 무조건 Native 전수, SEM 미세화·78 전수 재감사·불필요한 Work OS Gate 금지. **격리 브랜치 개발만 허용**. 사용자 승인 없이 `main` 병합, v003 immutable 변경, 원본 `v016_SCENARIO_CONTRACT` 변경/직접 통합 주장, Project Sources/UI 실제 적용 주장, 공식 Work OS M0/Shared State 승격, WEQUIP 영구 의존, MAIN/WORK/다른 채팅의 소유권 이전 금지. **인계 자체는 공식 승격 지시가 아니다.**

## 6. 새 채팅의 첫 응답 절차 — 엄격히 READ ONLY → STOP

새 채팅은 최신 GitHub 브랜치/HEAD와 최근 Actions(해당 SHA에 연결된 **완료·실패·취소** 구분), 본 문서와 CURRENT 최상단, 로드맵, 78 JSON 및 관련 실제 Native/실 시즌 영수증을 **읽기 전용으로 독립 복원**한다. 첫 응답은 아래 **7개 내용만 간결하게** 보고하고 **STOP**한다.

1. 현재 격리 브랜치·HEAD·최근 커밋/Actions 및 인증된 이번 M1/M2 소스 범위
2. 사용자가 실제 이용 가능한 기능과 아직 막히는 부분
3. 과거 **실 Native**·새 **실 Wago/Blizzard/WCL**·최근 **오프라인 PASS** 정확 구분
4. M0~M7 위치, 78계약 `15/78`과 `full_product_e2e=PENDING` 확인
5. 진짜 필수 미완료, 선택 항목만 보류 가능한 부분, 실제 확인된 결함
6. **다음 한 작업: M2 실제 원본·예산·v212 설치 동일성 검증의 첫 필수 차단 확인** 및 STOP/REUSE 기준
7. 미확인 증거·비용·권한 경계

**첫 응답에서 금지:** 코드/문서 수정, GitHub commit/PR, 테스트·Actions/Native/HTTP/DB2 실행, 캐시 폐기, 원본/공식 승격. **사용자가 이후 별도로 "진행"한 경우에만** HEAD를 다시 확인하고 단일 실제 장애를 최소 수정. 이 문서의 작성은 새 사용자 제품/SimC 통합 완료 선언이 아니다.
