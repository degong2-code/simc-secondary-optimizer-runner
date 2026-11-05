# SIMC SECONDARY OPTIMIZER — P3-EN 단일 새 채팅 인계 정본
**시점:** 2026-11-05 KST · **범위:** GitHub 격리 개발의 독립 복원·인계 · **공식 제품/Project UI/Work OS 승격 아님**

## 0. 실제 기준·우선권·읽기 순서
- GitHub: `degong2-code/simc-secondary-optimizer-runner` / 격리 `probe/chat-cache-v035-20261024`. **문서 작성 직전 독립 조회:** isolation `76e6f45e1a95a4e92acb0a1990851b464d457062`, `main` `07133e0aaf738d6e4816a6486057b1cd49c018de`. **이 문서를 커밋하면 격리 HEAD가 바뀐다. 새 채팅은 두 HEAD를 실제로 다시 별도 조회**하고, 아래 스냅샷을 현재 HEAD라고 단정하지 않는다.
- **직전 검증 제품 코드:** P3-EM 조인 최적화 `0fb6c42cb7e93b1f308f7310141271f0c0d7ec6b`; ledger 교정 `7f52a670a64a1a3bd2364eb84973ce3c86b5a3a5`는 코드 변경 없이 250 PASS. `0fb6c42`→`76e6f45` 비교 결과 **추가 2커밋은 CURRENT·INDEX·P3-EM 노트만**. 정확한 코드 내용은 새 채팅이 재비교.
- **신뢰 우선순위:** 최신 사용자 직접 결정 > [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 및 충돌 없는 v1.4 계열 > GitHub 실제 코드·봉인 원본·실제 Actions/Native 영수증 > CURRENT/기록/인계. 구 v1.4.1의 27 DPS·증강 포함·옛 J/F/O 값은 **역사 참고**. 현재 **26 DPS, 증강 기원사·탱커·힐러 제외**.
- **읽기 순서:** (1) 양 HEAD 독립 조회 → (2) **이 P3-EN** → (3) [PROTOCOL](development/PROTOCOL.md) → (4) [INDEX](development/INDEX.md) 해당 capability → (5) [P3-EF](development/notes/2026-11-05_p3-ef-explicit-no-oil-accounting-proof-waiver.md)/[EG](development/notes/2026-11-05_p3-eg-reuse-existing-same-season-g-for-auto-v222.md)/[EH](development/notes/2026-11-05_p3-eh-v212-dual-g-source-identity.md)/[EI](development/notes/2026-11-05_p3-ei-sealed-gem-property-to-season-input.md)/[EJ](development/notes/2026-11-05_p3-ej-existing-pinned-simc-gem-quality-bridge.md)/[EK](development/notes/2026-11-05_p3-ek-existing-gem-effect-quality-policy-a-connect.md)/[EL](development/notes/2026-11-05_p3-el-policy-a-prepared-options-v196-v212.md)/[EM](development/notes/2026-11-05_p3-em-v266-exact-source-join-cache.md) → (6) 직전 [P3-EE](CHAT_CONTINUITY_HANDOFF_20261105_P3_EE_ENGINE_FIRST.md)의 P3-DX/DY/DZ/EA/EC/ED, P3-DN/DM/DS/DT/DU/DV 및 원본 증거 인덱스 → (7) [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 최상단 → (8) [개발자 실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md) → (9) 승인 v1.4.3 및 후속 사용자 직접 정정 → (10) 실제 `v216/v212/v222/v220/v196/v221/v230/v266/v268/v271/v281/v278/v277/v217/v098` 코드·source SHA·Actions/Native.
- P3-EE/P3-DW/P3-DO는 **과거 단일 정본**. 이번 인계는 이전 내용 전체를 복제하지 않고 실제 추가 변경과 기존 사실의 적용 범위만 연결한다.

## 1. 최종 제품과 현재 완료 판정
- **최종 목적:** 26 DPS 전문화에 공통 재사용 가능한 **하나의 엔진**. 사용자 미래 파밍 목표 ilvl(기본 334) 또는 수동 **최종 T**를 기준으로 치명/가속/특화/유연의 **최적 절대 rating**을 SimC DPS 최대화로 찾고 DPS·SEM·95% 판정(관측 1순위와 통계적 확정 구별)·비율·실질적으로 다른 근접 대안·캐시·취소/재개를 제공. 현재 장비 재분배, 장비 추천/획득 경로, 시즌 전수 DB, 별도 APL/proc/효과 인증기 **제외**.
- **지금의 완료 Gate = 실제 사용자 웹앱의 단일 `v216 Environment Build`**: 새 시즌 정상 수집→대표 일반 장비/무기/티어4 및 시즌 **G/J/F/O 전부 검증**→기존 `v222` 공식 `B=G+J+F`/`T=B+O`·L/E/O 소유권·수동 최종 T 우선→검증된 최고 품질·정책 A 항목의 **실제 사용자 선택지 발행**→`v212` 신규 시즌 버전화 **원자적 설치/READY/T1**. `v098→v096/v094` 사용자별 적응형 DPS는 후속 메인 개발이며 환경 READY의 필수 Gate가 아님.
- **특수 보석 정확히 1개 필수**(종류 선택 가능, 미장착 금지). P3-EB 0개 허용 오류는 P3-EC에서 철회. P3-ED~EK에서 출처 ID/속성/선택 source를 연결했으나 **item ID 존재 또는 품질 숫자만으로 실제 특수 역할·소켓 적합성·최고 품질·공식 J를 승인하지 않는다**.
- **예산:** O는 자유 분배 불가; 명시적 무기 기름 미사용만 O=0/무기 적용성 입증 불필요, 단순 자동 미리보기 O0 가정·원본 미관측과 구별. G Native는 **동일 시즌 유효 참조가 있으면 선택적**, 정확 원본 검증 소유권 유지. 기존 시즌 `79×2`/`J=138`/`F=165`/기름 16+16을 새 시즌 공식 수치로 복사하지 않는다. 동일 시즌 정적 캐시는 SimC revision만으로 폐기 금지.

## 2. Evidence(증명) / Integration(실제 연결) 현황
| 기능·범위 | Evidence: 확인·재사용 가능한 사실 | Integration: 실제 제품 상태 |
|---|---|---|
| 기본 시즌 수집/봉인 `v161/v191/v211/v213/v217`, P3-DS | T0 통제 수집·source SHA/변조 차단·캐시 오프라인 증거 | 이미 구현; **T0 PASS ≠ T1 전체 환경 READY**, 신규 시즌 공식 설치 미완료 |
| 대표 장비/티어/G, P3-DG·DZ·EG·EH | 동일 시즌 G 참조 또는 선택 exact Native, 독립 opt-in, `v212` 대체 G source identity | `v222` numeric source-only와 `v212` 스테이징까지 연결; G의 신규 시즌 실제 공식 범위 인증·대표 티어 설치는 미완료 |
| 보석 J·특수 1, P3-EC/ED/EA/EI/EJ/EK/EM | `v221` ItemID↔GemProperty/색상/최소 ilvl/마부 ID, `v266` 정적 raw 4스탯, `v230` 품질 소스, `v271` 가변 소켓. `v268` 동일 원본 v266 조인 재사용 | 필수 특수1+일반N source-only 입력/정책 A `source_relation`까지 연결. 실제 특수 효과 역할·최고품질의 효과/조건·인게임 합법 소켓·SimC-effective J/공식 J **미완료** |
| F/O, P3-DU~DZ | 기존 후보 발견, 공유 선택적 Native, 손·무기 scope, SHA 캐시; 기존 시즌 한정 Native 관측 | 후보·소스 숫자 경로 **재개발 금지**. 최신 시즌 기본 F 품질/정적 값·실 선택 O 적용 가능성/정식 승인 불충분 |
| `v222` G/J/F/O→B/T | 내부 예산/수동 최종 T, O/L/E 중복 방지, explicit-none 및 same-season G 참조 어댑터 | source-only 계산은 가능하지만 **새 시즌 공식 G/J/F/O/B/T 완비 아님** |
| `v220/v196/v216` 정책 A, P3-DN/DM/EK/EL | 소스 관계·4-family 판정, 최고품질/동일 효과·적용 범위 조건, 설치 **준비 후보** SHA 분리·중복 v220 판정 제거 | 실제 신규 시즌 검증 완료 선택지 **0**, 설치 준비≠실제 UI 발행, `options_published=false` |
| `v212` 새 시즌 환경 | 버전화 source-only stage와 G 원본 타입 구별, 준비 후보 digest 보존, Ubuntu/Windows 오프라인 PASS | 현재 신규 시즌 `STAGED_NOT_INSTALLED`, `official_G/J/F/O/B/T=None`, `environment_ready/installed=false`. **원자적 신규 READY/T1 미완료** |
| `v098/v096/v094` DPS | 기존 적응형 탐색·95%·프로필·캐시 및 과거 조건별 증거 | **후속** 사용자별 제품 통합; 환경 READY 선행 조건 아님 |

**중요:** “원본 증거 부족”과 “이미 증명된 사실의 환경 입력·선택지 연결 미완료”는 다른 과제. 새 Gate/Native 전에 기존 source·계약으로 적용 근거를 전달하거나, **해당 입증이 불필요한 이유**를 정확한 scope로 설명할 수 있는지 검토한다. P3-EF explicit none·EG same-season G가 그 사례다.

## 3. P3-EE 이후 반영된 변경과 검증 영수증
- **P3-EF–EH:** `v222` 명시적 oil OFF 시 O0/무기 적용성 면제; 자동 O0 preview 가정은 면제 아님. 기존 `v222` same-season G 참조를 v216 source-only 예산에 연결해 v277 Native G 필수 중복 제거, `v212` G Native SHA/참조 source SHA 중 정확 하나; 공식 승인/READY로 미승격.
- **P3-EI–EK:** 봉인 v221 GemProperty 속성, v266 4-stat 벡터, v230 item/crafting 품질을 선택 보석에 연결하고 `v220` 기존 정책 A source family와 원본 근거·미충족 3가족을 구분. 최고 품질/특수 역할/실 소켓은 여전히 PENDING; 선택지 자동 발행 없음.
- **P3-EL:** `v196.prepare_verified_fresh_choices`에서 기존 `v220` 4-family 및 품질/동일 효과·사용 범위가 갖춰진 선택지만 **미발행 설치 준비**. `v216`이 단일 v220 판정 결과 재사용, `v212`가 prepared-options digest를 source-only manifest에 보존. 기존 시즌 전용 READY 단순 복사 금지.
- **P3-EM:** 기존 v267 봉인 CSV와 v221 원본 SHA를 매 view 재확인하되 `v266` 전체 CSV join을 `v217`에서 **원본 SHA+코드 지문별 한 번** 처리하고 선택 변경 시 투영만 수행. 기존 캐시 재사용·변조 fail-closed, source-only/공식 J/READY 의미 불변. **현재 최신 제품 코드** `0fb6c42cb7e93b1f308f7310141271f0c0d7ec6b`; ledger 교정 `7f52a670a64a1a3bd2364eb84973ce3c86b5a3a5`, 후속 `76e6f45e…`까지 문서만.
- **최신 focused:** [P3-EM 코드 동일 교정 #41975010008](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41975010008) **250 PASS/0 FAIL·DEV_LEDGER_PASS**; [P3-EM 문서 HEAD #41975213436](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41975213436) **250 PASS/0 FAIL·DEV_LEDGER_PASS**. 최초 [#41974880874](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41974880874) **NOTE_DECISION_INVALID ledger FAIL, 단위 테스트 전 중단**을 역사로 보존; 교정 뒤 PASS.
- **최근 더 넓은 환경 계약**은 **P3-EL 코드 시점** [v212 #41972410751](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41972410751) Ubuntu/Windows 각각 **448 tests = 444 PASS/4 SKIP, Native0**; [P3-EL focused #41972410711](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41972410711) **249 PASS**; [v191→v196 #41972410706](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41972410706) SUCCESS. **P3-EM 전체 코드에 새로 같은 448건을 실행한 결과라고 주장하지 않는다**. 변경 영향이 없는 기존 영수증은 범위에 맞게 재사용한다.
- **Native 역사 증거(조건별):** [소켓 #41601140696](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696), [F/O #41666305288](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666305288)/[#41666925906](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666925906), [무기 원본 #41732744145](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41732744145) 각 SUCCESS. 원래 시즌·빌드·프로필·바이너리/옵션 범위에 한해 사용. **이번 인계 신규 SimC Native·게임 HTTP·제품 코드/테스트 실행 없음; 실제 신규 T1 READY 영수증 없음.**

## 4. 병목·효율·다음 최소 작업
- **실제 병목:** 시즌 특화된 새 기능 부재보다, 기존 source 사실이 **필수 G/J/F/O 공식 출처/품질·게임 적용 조건 → 정책 A 실제 발행 → v212 신규 설치/READY**의 단일 흐름에서 채택되지 못한 것. T0/미승인 숫자·원본 ItemID만 늘려서는 READY 불가. P3-EL prepared는 실제 발표된 선택지 0.
- **이미 구현한 부분의 효율 주의:** `v216` 조정기 약 4,769줄, source-only 단계·진단 구조 중첩; `v268`은 전체 CSV parse 반복을 없앴지만 **원본 SHA 검증용 CSV 바이트 읽기·조인 JSON 검증**은 남음. P3-EM 성능 단축은 호출 횟수 회귀로 증명, 실제 대형 CSV 벤치마크는 아직 없음. 거대 리팩터링/무차별 데이터 수집보다 **실제 프로파일링 결과와 연결부의 한정 개선**을 우선.
1. **단기 A REUSE/CONNECT/NOT_REQUIRED:** INDEX·P3-BH/BX/BZ/BV·P3-DN/DM/DU~DZ·P3-EF~EM·해당 source SHA/Native 조건 선조회. 시즌 G 참조의 실제 유효 빌드/대상, 일반 J+정확 특수1 실 소켓/최고품질/정적 rating, F 최고품질·O 선택 손별 적합성을 **기존 data source/admission contract에 연결**. 증명할 실질 대상이 없는 항목은 scope와 이유를 기록해 면제, 원본 없는 필수 값은 보류. 새 collector/효과 인증/모든 전문화·ilvl Native 전수 **STOP**.
2. **단기 B CONNECT:** 충분한 공식 G/J/F/O를 기존 `v222` 회계에 전달, E/L/O 한 번 귀속·수동 최종 T 우선. 기존 `v220/v196`에 확인된 최고 품질만 **실제** 원자적 발행 후 `v212` 신규 시즌 **설치/READY**; 선택적 아이템 부족은 해당 선택지만 보류하고 유효 기본 환경까지 차단하지 않는다. prepared/source-only의 false를 true로 토글하는 꼼수 금지.
3. **단기 C T1:** 기존 **동일 사용자 웹앱 v216** 정상 Build로 무기록 새 시즌 `T0→공식 예산→선택지→버전화 설치/READY/T1` 통제 인수. [P3-AA](P3_AA_20261102_SINGLE_ENGINE_FRESH_SEASON_CONTROL_ACCEPTANCE.md): 기존 시즌 캐시를 새 시즌 시험 입력으로 재사용하지 않되, 정상 외부 Wago/Blizzard/WCL/SimC 수집은 허용. 통과 후 동일 입력 캐시·취소/재개·SHA 변경 차단 점검; 허용 범위 외 전수 Native/재감사 금지.
4. **장기:** READY 이후 `v098→v096/v094` 기존 적응형 SimC·95% 판정/근접대안·캐시/재개와 26 DPS 공통 UX 연결. 새 탐색기·장비 추천·효과 재구현 금지.
- **모든 변경 자가검증:** “이 변경은 다음 시즌에도 그대로 쓰는 **한 엔진** 완성에 필요한가?” 원본/INDEX/코드/영수증 선조회→Evidence와 Integration 분리→`REUSE/CONNECT/EXTEND/NEW/STOP` 하나 선택→논리적으로 독립 작업 묶기→이전 검증·캐시 재사용→실제 변경 경로 최소 시험. Native/HTTP/Actions 호출·중복 파싱·메모리/I/O·전체 실행시간·구조 복잡화 확인.

## 5. 실제 적용/미적용/권한
- **이번 인계 대상(문서만):** 이 단일 정본, [PROTOCOL](development/PROTOCOL.md) 최신 포인터, [INDEX](development/INDEX.md) `DEV.CONTINUITY`, [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 최상단, [개발자 실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md) 인계 포인터, [P3-EN 작업 노트](development/notes/2026-11-05_p3-en-engine-continuity-handoff.md). 커밋 이후 GitHub 실제 HEAD/변경 파일과 Actions 상태를 다시 확인.
- **미적용/미승격:** 새 기능·제품 코드 수정·실 SimC Native·게임 HTTP·수동 새 CI 요청·T1 수행 없음. 승인 v1.4.3 내용/원본 `v016_SCENARIO_CONTRACT`·`v003` immutable·`main`, ChatGPT Project Sources/Instructions 실제 UI, 공식 Work OS M0/Shared State, MAIN/WORK 권한 및 기존 주 개발 채팅 소유권 **변경하지 않음**. 자동 GitHub Actions가 커밋으로 실행되면 그 실제 결과를 별도로 표시하되 제품 READY로 승격하지 않는다.

## 6. 새 채팅 시작 프롬프트 — 첫 응답 복원 후 즉시 STOP
```text
SIMC SECONDARY OPTIMIZER 프로젝트를 **읽기 전용으로 독립 복원**해.

GitHub 저장소: degong2-code/simc-secondary-optimizer-runner
격리 브랜치: probe/chat-cache-v035-20261024
최신 단일 인계 정본: docs/CHAT_CONTINUITY_HANDOFF_20261105_P3_EN_ENGINE_FIRST.md

먼저 격리 브랜치와 main의 GitHub 실제 HEAD를 **각각 독립 조회**해. 읽는 순서:
1) P3-EN 단일 인계 → 2) docs/development/PROTOCOL.md → 3) docs/development/INDEX.md →
4) P3-EF/EG/EH/EI/EJ/EK/EL/EM 작업 기록 → 5) 역사 P3-EE의 DX/DY/DZ/EA/EC/ED 및 DN/DM/DS/DT/DU/DV 관련 기능별 원본·증거 →
6) docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md → 7) docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md →
8) 승인 v1.4.3·이후 최신 사용자 직접 정정 → 9) 실제 관련 코드·봉인 source SHA/Actions·Native 영수증.

최종 목표는 개별 기능이 아니라 26 DPS(증강·탱커·힐러 제외)에 공통 재사용되는 **하나의 엔진**이다. 목표 ilvl 기본 334 또는 사용자 최종 T에서 최적 CHMV 절대 rating을 SimC DPS로 찾고 DPS/SEM/95% 판정·관측1순위/근접대안·캐시/취소/재개를 제공한다.

지금의 개발·완료 판정 대상은 단일 사용자 웹앱 v216 Environment Build의 시즌 대표 일반 장비·무기·티어4/G/J/F/O 전부 검증 → 기존 v222 B/T 회계 → 검증된 최고 품질·정책 A 실제 사용자 선택지 자동 발행 → v212 시즌 환경 설치/READY·T1이다. 후속 v098→v096/v094 DPS 실행을 Environment READY의 필수 Gate로 만들지 마.

**특수 보석은 정확히 하나 필수**(P3-EB 0개 허용은 폐기, P3-EC/ED 유효). 구 시즌 79×2/J138/F165/기름16+16을 새 시즌 공식 예산으로 복사하지 마. T0 원본 수집·source-only 산술·prepared 옵션·focused PASS를 실제 신규 T1 READY로 오인하지 마.

매 작업 **전에** PROTOCOL/INDEX·기존 작업 기록·원본 바이트·코드·실 Actions/Native를 먼저 검색하고 Evidence와 Integration을 별도 판정해 REUSE/CONNECT/EXTEND/NEW/STOP 중 근거 있는 결정을 내려. 원본 인증이 부족하다면 출처와 입력 데이터 구조를 연결할 수 있는지, 또는 해당 조건에서 **입증이 불필요한지**를 먼저 판단하고 정말 부족한 부분만 보완해. 기존 F/O 후보·Native opt-in, v221/v266/v268/271 보석, v222 예산, v220 정책 A, v217 캐시, v098 적응형 엔진을 중복 개발하지 마. 독립 가능한 작업은 논리적으로 묶고 유효한 동일 조건 PASS·캐시를 재사용해. 변경마다 중복 Native/HTTP/Actions, 메모리/I/O, 전체 시간, 구조 간소화와 “다음 시즌에도 단일 엔진인가?”를 자가점검해.

**첫 응답은 다음만 보고:** 실제 격리/main HEAD와 코드 identity, 최신 Actions/Native와 적용 범위, 최종 목표/현 Environment Build 완료 Gate, Evidence 대 Integration 완료·미완료, 현재 병목/더 효율적인 대안, 간결한 단·장기 로드맵, 미반영·미승격과 권한 제한.

GitHub 코드·원본·영수증을 독립 대조한 복원 보고를 완료하면 **즉시 중단**.
**내가 명시적으로 '진행'이라고 하기 전에는 개발, 코드·문서 수정, GitHub 커밋, 신규 수집, CI/Actions/Native/테스트 실행 또는 공식 승격을 절대 시작하지 마.**
```
