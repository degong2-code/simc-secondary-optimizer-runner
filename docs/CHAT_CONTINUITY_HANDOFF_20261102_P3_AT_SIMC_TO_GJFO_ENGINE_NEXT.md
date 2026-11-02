# SIMC SECONDARY OPTIMIZER — 2026-11-02 P3-AT → 시즌 G/J/F/O 연속 개발 인계 정본

**용도:** 사용자 요청에 따른 새 채팅용 단일 최신 복원 문서. 직전 연속 개발을 그대로 이어받는다. 역사 문서/P3-AF를 최신 인계로 착각하거나, 코드를 초기화하거나, 완료된 증거를 처음부터 전수 감사하지 않는다.

**개발 코드 기준:** `ef0466541ce59149e5d69a765b7361d2a86f2c16` (P3-AT 문서까지 확인한 2026-11-02 현재 기능 HEAD). 이 인계 문서의 새 커밋은 문서·포인터만 변경한다. 새 채팅은 실제 원격 HEAD를 재확인한다.
**저장소:** `degong2-code/simc-secondary-optimizer-runner`, 격리 브랜치 `probe/chat-cache-v035-20261024`. 당시 `main=07133e0aaf738d6e4816a6486057b1cd49c018de`, 저장소 public. main/원본 불변 자료/Project UI/공식 Work OS는 변경하지 않는다.

## 1. 최신 승인 설계와 정확한 제품 목표

- 장기 핵심은 **특정 기능 하나를 구현하는 일이 아니라, 기능을 새 시즌마다 원본에서 반복 구축·검증·갱신하는 하나의 Environment DB Build 엔진** 완성이다. 기존 수집기/분류기/대표 프로필/적응형 SimC를 재사용하며 별도 제품·새 최적화 엔진·새 proc/APL 효과 계산 엔진을 만들지 않는다.
- 목표 ilvl(기본 334) 또는 사용자의 **최종 CHMV 총량 T**로 미래 파밍 목표인 치명·가속·특화·유연의 **DPS 최대 절대 rating**을 찾는다. 26 DPS 전문화만 지원하고 **증강 기원사, 탱커, 힐러 제외**. 장비 조합·드롭 경로 추천이나 현재 장비 스탯 재분배가 아니다. 사용자가 모든 장비를 직접 고르지 않는다.
- 한 번의 일반 Build: 게임 시즌/빌드·SimC revision → 정상 Wago/Blizzard/WCL/검증된 공개 데이터 새 수집 및 정체성 → 시즌 대표 장비/무기/티어 → **G/J/F/O 전체 자동 구축** → `B=G+J+F`·`T=B+O` → 최고품질·적용범위 검증 후 **정책 A 자동 등록** → 내부 SimC 프로필·환경 설치 → 사용자 Start 시 기존 adaptive SimC DPS/SEM/**95%**·의미 있는 근접 대안/캐시/취소·재개. 시즌별 G를 누락한 J/F/O만의 갱신은 요구 미달.
- 수동 최종 T가 자동 값보다 우선, `B=T-O`. 기름 O는 적용 손·무기 조건이 맞는 고정 비자유분배 rating이며 `gear_*`에 **한 번만** 반영. 특수장비 L은 G 안에 이미 포함되고 하한만 보호; 정확한 영구마부 E의 추가도 소유권에 따라 한 번만, 수동 T에서는 재가산 금지. 장신구 고정 수치는 자유 G 밖, 미관측≠0. 제작장비 초기 50:50은 L 잠금 아님. 정상 SimC가 효과/proc/APL/DPS를 계산.
- 새 시즌 원본/Native 확인 없이 과거 **v089 79×2 참조, J=138, F=165, 무기당 O=16 crit+16 haste**를 새 시즌 확정값으로 사용하지 않는다. exact Native G는 선택적 정밀 경로이며 전 전문화×전 ilvl 일괄 Native Gate가 아니다.
- 보석/영약/음식 등의 낮은 품질을 숨길 수 있는 조건은 동일 효과·사용 조건·범위가 검증되고 높은 품질이 모든 관련 수치에서 비열등할 때뿐. 일반 임시 마부 범위 제외, **무기 기름**은 별도 지원. Omnium 등 시즌 고유 시스템은 선택형 모듈, 자동 GPT 런타임 의존 금지.
- 최종 제로기존자료 시험은 **똑같은 제품 Build 엔진**으로 기존 DB/캐시/영수증/수동 정답이 없는 새 설치 상태에서 실행한다. **정상 외부 새 원본 다운로드는 허용**. 출력 먼저 봉인 후 이전 시즌과 비교; 별도 SimC-only 최종 시험 생성 금지.

## 2. 반드시 이 순서로 읽기 (권한·시간 절약)

1. **이 문서 전문**. 다음 채팅 첫 응답에 필요한 기준·증거·실제 다음 작업이 여기 있다.
2. `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` **최상단 P3-AT와 P3-AS/AR/AQ** 및 실제 최신 상태. 오래된 누적 CURRENT 항목은 그 당시 스냅샷.
3. 승인 정책: `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md`, `docs/DPS26_SCOPE_CORRECTION_20261031.md`, `docs/P3_AA_20261102_SINGLE_ENGINE_FRESH_SEASON_CONTROL_ACCEPTANCE.md`, `docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md`, `docs/P3_ENVIRONMENT_BUILDER_TARGET_ARCHITECTURE_20261031.md`. 이전 사용자 첨부 **v1.4.1 20261029**는 27 DPS/증강 포함이라는 폐기 문구가 있으므로 최신 범위에 인용하지 않는다. 교정된 v1.4.1 20261031과 승인 v1.4.3의 충돌 없는 부분만 적용.
4. 최근 원본 연구·구현의 정확한 차이: `docs/P3_AT_20261102_NORMAL_SIMC_SOURCE_INTEGRATION.md` → `docs/P3_AS_20261102_DB2_RAID_TIER_TO_SIMC_EXACT_ID_BRIDGE.md` → `docs/P3_AR_20261102_RAID_BONUS_TREE_TIER_SEASON_CORROBORATION.md` → `docs/P3_AQ_20261102_TIER_TOKEN_BASE_ILVL_SOURCE_PROOF.md`. 이름 먼저 검색하던 옛 P3-AL/AM은 역사 자료.
5. 코드: `runner/v216_environment_build_coordinator.py`, `v161/v163` → `v245` → `v250` → `v251` → `v229/v231`; 그리고 다음 구현에 필요한 `v165/v166/v167/v169`, `v224/v225/v226/v227/v228`, `v232/v233/v236`, `v221/v222`, `v098/v212`, 기존 `v093/v094/v095`만 필요한 연결부를 읽는다. 정확한 API/스키마는 현재 코드가 기준.
6. **실제 Actions jobs/logs**: 실제 Wago↔SimC exact join [#41455991413](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41455991413), 정상 v216→v229 원본 source [#41457632768](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41457632768), 최종 오프라인 Ubuntu+Windows [#41457357814](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41457357814), API [#41457357665](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41457357665), Windows Beta [#41457357885](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41457357885), UI [#41457357707](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41457357707). 적용 범위가 안 바뀐 증거는 다시 실행하지 않는다.

## 3. 직전 연속 구현 흐름과 완료된 실제 사실

`v216 normal Build` → 같은 빌드 `v161` Wago DB2 수집, `v242/v155` Blizzard/WCL, `v163` 레이드/쐐기 출처 → `v245` DB2-우선 직업·전문화·2/4세트·5부위 티어 **후보** → `v250` 인증된 현재 레이드 장비/토큰과 보너스 트리 그룹으로 13×5 후보 관측 리더 → `v251` 13직업/65개 물리 ID 후보 → 기존 `v229` pinned SimC 생성 원본 취득 → `v251/v231` **정확한 세트/클래스/5 ID/2·4 보너스 set_option** 대조.

- **티어 이름 먼저 찾는 웹 파서는 정상 Build에서 폐기**됐다. `v243`은 역사 코드. Wago의 `build=`는 게임 빌드 전체 DB2 스냅샷이지 활성 시즌 필터가 아니므로, 구/신시즌 티어 공존 가능. 아이템 ID가 크거나 ItemSparse 기본 ilvl이 높다고 자동 시즌 확정 금지.
- 과거 S1 65개 티어의 Wago 같은빌드 기본 ilvl은 **197**, 다음 S2 65개는 **219**. 실제 현재 레이드 전리품 118개 중 101개가 S2 세트와 보너스 그룹 `614–618` 겹침, 이전 S1 세트는 `608–612`. 이 그룹은 시즌 고유 공식 플래그는 아니어서 현재 시즌 자동 승격은 **미완료**.
- **실원본 cross-provider PASS**: Wago `12.1.5.70575`의 `ItemSet` SHA `0ae48ff20e117ba0d4bc30d6934819b752785cca0d61cbb0b5812ed99bd19bc6`, SimC exact commit `710c2408bfd3ae4df71b8cd55cdf01f63fd6c926`의 `item_set_bonus.inc` SHA `3f05a2df338c92f315af9d6b6b47eb3b03171a72630ed852d9a661a7da7c99bc`. S1 `1978–1990`, S2 `2055–2067` 각각 13직업×5 실물 ID와 SimC 정의 일치. SimC option `midnight_season_1` / `midnight_season_2`는 **정확한 ID 매칭 결과로 관측된 출력**이지 이름 검색 입력이 아니다. [#41455991413](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41455991413).
- **실제 source stage PASS**: 명시된 SimC source commit/빌드 아래 정상 v216 래퍼가 기존 v229 collector 재사용. 첫 실행 Git tree 4 + blob 3 = **7 HTTP**, immutable blob 및 SHA 확인, sealed v217; 동일 입력 재실행 **0 HTTP** / `REUSED_VERIFIED`. 실원본 receipt SHA `a223c1cbd27aab60d734644b8a7580e4dbd22cb9912d504121c4b797c2c7ac7a`; `item_data.inc`를 받지 않음, Native0. [#41457632768](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41457632768).
- **합성 통합/회귀 PASS**: [#41457357814](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41457357814) Ubuntu·Windows 각각 **360 tests, 0 FAIL, 4 SKIP**, Native 산출물 없음. 별도 API/Windows beta/UI Actions 각 SUCCESS. 이 결과는 코드·synthetic 연결 범위이며 완성 신규 시즌 E2E가 아니다.
- #41457527529 일회용 조사 워크플로 초기 실패는 `runner` import path 누락, 수정 뒤 #41457632768 PASS. 실패 기록 보존. 두 P3-AT 마지막 run의 GitHub Actions 다운로드 Artifact는 REST 확인 결과 **각 0개**; 읽을 수 있는 GitHub jobs/logs와 repo 문서가 영수증. 일회성 workflow YAML은 P3-AT HEAD에서 제거됨.
- 과거 Native 한 번 [#41396545012](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41396545012)에서 CHMV 정적 **G=2847** 수치 관측은 맞지만 일반 장비/무기가 옛 `Sinful Gladiator` PvP 아이템으로 섞였다. **FAIL_ACTIVE_SEASON_REPRESENTATIVE_AUTHENTICATION**이므로 현재 시즌 G/참조값으로 승인·사용 금지. 다시 같은 혼합 대표 G Native를 측정하지 않는다.
- 기존 [#40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357) 26 DPS 물리 SimC smoke는 역사 증거일 뿐 26-DPS 신규 시즌 adaptive E2E 근거 아님.

## 4. 실제 미완료·차단과 최소 다음 작업

**핵심 부족:** (a) 티어 observed cohort의 공식 활성 시즌 최종 소속/대표 프로필 승인, (b) 특히 대표 **일반 장비·무기 시즌 provenance** (과거 v232의 PvP 혼합 실패를 막아야 함), (c) 동일 시즌 **G/J/F/O 전체 원본·품질·정적 rating**, (d) 기존 v222와 B/T/L/E/O/수동 T의 사용자 예산 통합, (e) 정책 A 최고품질 선택지→v212 설치·v098 대표 프로필→기존 adaptive SimC 26 DPS 실사용 E2E. 현재 `ENVIRONMENT_READY`, 최종 제로베이스 인수 PASS 아님. SimC 원본 수집 PASS만으로 `item_data.inc`/주능력치/무기 성능·정적 G가 되는 것도 아님.

**가장 자연스러운 후속 개발:** 사용자의 '진행' 이후, 기존 v216→v251 정확한 13×5 자료를 새로 수집하지 말고, 기존 `v163/v165–v169`의 **현재 시즌 출처가 확인되는 일반 장비·무기**를 `v226/v232` 대표 선택에 결합한다. 목표 첫 범위는 한 직업/목표 ilvl(예 334), 역사 혼합 PvP 후보가 재등장하면 **즉시 PENDING**, 유효 후보만 다음 단계. G는 기존 `v225/v226/v227/v228/v232/v233/v236`를 재사용하고 부족한 정확한 변형만 소량 Native. 병행 가능한 소스 조사로 `v221/v190/v224/v225`의 **최고 품질 보석 J·영약 F·무기 기름 O·영구 마부 E** 필수 ID/옵션/수치·적용 손·동일 빌드 근거를 묶어 처리한다. 검증되면 **기존 v222**로 G/J/F/O→B/T, 선택 L/E/O를 한 번 반영하고 수동 T 우선. v220/213/196 정책 A 선택지, v212/216 설치·v098 프로필, 기존 v093–v095 adaptive DPS와 연결한다.

**효율 원칙:** 독립 작업은 안전하게 묶되 검증/실패 경계는 분리. 기존 수집기·v217 stage seal·Native/cache·95%/취소/재개·완료 기준 재사용. 같은 빌드/소스 identity 재요청 0 목표, 정적 시즌 cache는 SimC rev만으로 무효화하지 않고 DPS 캐시는 정확 바이너리·전체 프로필·O·전투·iterations로 분리. Native를 일률적 26전문화×전 ilvl 반복하지 않는다. 새로운 기능별 엔진/별도 프로필 빌더/효과 인증 Gate/전체 시즌 장비 추천 DB/WEQUIP 운영 의존 금지.

**단기 로드맵:** 대표 일반 장비·무기/티어 동일시즌 증거 → **G/J/F/O 전부 신규 출처 확정** → 기존 v222 B/T·고정치·수동 T → 최고 품질 정책 A·설치/프로필 → 기존 적응형 SimC/Windows Start/결과/재개 → **완성된 동일 Build**에 대한 기존 자료 없는 통제시험. 
**장기:** 새로운 시즌마다 같은 요청이 새 데이터로 반복 성공하는 **환경 DB 구축 엔진**. 그 시즌이 아닌 값을 조용히 사용하지 않고 정확한 실패/보류 상태 반환.

## 5. 승인·권한·완료 상태

- 최신 사용자 직접 결정 > 승인 v1.4.3 및 충돌 없는 v1.4 계열 > 실제 GitHub HEAD/CURRENT/Actions/Native > 역사 메모. 첨부 옛 v1.4.1(27 DPS)은 제품 정책 아님.
- 코드 구현 / 합성 CI PASS / 실원본 PASS / 실 Native PASS / 역사 재사용 증거 / PENDING / 미승격 / Project UI 실제 적용은 서로 다른 상태. 원본 `v016_SCENARIO_CONTRACT` 바이트 직접 통합은 미입증. GitHub 문서는 Project Sources 등록이나 공식 Work OS M0/Shared State 승인과 다름.
- 실 제품 개발의 기존 주 채팅 소유권을 신설된 MAIN/WORK가 빼앗지 않음. 사용자가 이번에 **새 개발 채팅으로 인계를 요청**한 범위에서만 계속한다. ⌁main⌁, v003 immutable, 원본 v016, repo visibility, Project Instructions/Sources UI, 공식 Work OS, 타 프로젝트 WEQUIP authority를 별도 지시 없이 변경하지 않음.

## 6. 새 채팅의 첫 응답 — 복원만 보고하고 '진행' 대기

읽기/검증만 한다. **새 채팅 첫 응답에서 구현/커밋/Actions 재실행/Native/실제 원본 신규 수집 금지.** 원격 HEAD/main, 승인 26 DPS/단일 엔진, 완료 P3-AT source-only·실원본과 synthetic 범위, 미완료 G/J/F/O 및 실프로필, 효율적인 다음 작업, 장·단기 로드맵, 권한 경계만 간결하게 사용자에게 보고한다. 보고 후 **즉시 멈추고 사용자의 명시적인 '진행'을 기다린다.** 과거 수치 재감사/확인용 질문 반복 금지.

---

## 7. 새 채팅 시작 프롬프트 (복사해서 사용)

너는 SIMC SECONDARY OPTIMIZER의 **진행 중이던 개발을 그대로 이어받는** ChatGPT다. 새 프로젝트를 시작하거나 이미 검증한 티어 수집을 반복하지 마라.

첫 응답은 **복원 보고 전용**이다. 먼저 GitHub `degong2-code/simc-secondary-optimizer-runner` 격리 브랜치 `probe/chat-cache-v035-20261024`의 **`docs/CHAT_CONTINUITY_HANDOFF_20261102_P3_AT_SIMC_TO_GJFO_ENGINE_NEXT.md` 전문**을 읽고, 그 §2 필독 순서대로 CURRENT, 최신 승인 v1.4.3·DPS26·P3-AA·엔진 노트·목표 아키텍처, P3-AT/P3-AS/P3-AR 및 실제 HEAD/main과 GitHub Actions jobs/logs를 확인해라. 이전 P3-AF는 역사 인계다. 불필요한 파일 전수 읽기와 Native 재검증은 하지 마라.

**장기 목표는 기능 하나를 덧붙이는 일이 아니라 새 시즌마다 해당 기능을 재구축·검증·갱신하는 단일 Environment DB '기능 구현 엔진' 개발이다. 매 단계 목표에 부합하는지 자가점검해라.** 목표 ilvl 기본 334 또는 수동 최종 T에서 26 DPS(증강·탱커·힐러 제외)의 최적 CHMV 절대 rating을 SimC DPS로 찾는다. 일반 사용자는 모든 장비를 선택하지 않는다. 정상 Build에서 외부 원본 신규 수집→같은 시즌 대표 gear/weapon/4티어→**G/J/F/O 전체 자동 구축**→B/T·L/E/O/수동 T 정합→동일 효과 최고 품질 정책 A 선택지 자동 등록→v212/v098 내부 대표 프로필→기존 적응형 SimC DPS/SEM/95%/실질 근접 대안·캐시·취소·재개를 연결한다. 새 장비 추천 DB·proc/APL 엔진·새 optimizer 금지.

**직전 구현을 보존해라:** v216→v245 DB2-first 티어→v250 현재 레이드 보너스 그룹→v251 정확한 13직업 65 ID→기존 v229 실제 SimC 3개 generated source→v231 set option 정확한 ID 매칭. Wago 12.1.5.70575/SimC commit 710c2408bfd3ae4df71b8cd55cdf01f63fd6c926의 S1·S2 각 65개 실원본 일치, v229 실제 소스 최초 7 HTTP/동일 재실행 0, Ubuntu/Windows 각 360 tests/0 FAIL/4 SKIP. 하지만 활성 시즌 65개 최종 승격, 대표 일반 장비·무기 시즌 증명, item_data/ G/J/F/O/B/T, 사용자 프로필·새 시즌 E2E는 아직 미완료. G2847 과거 Native는 혼합 옛 PvP 일반장비 때문에 해당 시즌 승인 G가 아니다. 옛 v089/J138/F165/O16+16을 신시즌에 복사하거나 티어 이름 검색으로 되돌리지 마라.

**후속 구현은 내 '진행' 이후:** v163/v165–v169의 출처가 확인된 같은 시즌 일반장비/무기→기존 v226/v232 대표 선택 및 최소 Native G; 동시에 기존 v221/v190/v224/v225의 최고 품질 J/F/O 검증; 기존 v222 B/T→v212/v098 및 adaptive SimC. **독립 작업은 묶어서 처리**하되 동일 완료 판정·stage seal·캐시·기존 CI/Native 증거를 재사용하고, 호출 수·메모리·I/O·중복 실행·전체 실행시간/구조 단순화를 매 변경마다 검토해라. 합성/실원본/Native/미완료/미승격을 정확히 구분해라. 최종 빈 자료 통제시험은 *완성된 같은 일반 Build*를 쓰고 외부 새 수집은 허용, 기존 수집자료·캐시/영수증 입력은 금지한다.

지금은 **읽기·검증·복원 결과만 보고**해라: 제품 취지, 실제 HEAD/main, 최신 완료와 미완료, 증거 범위, 핵심 장애·장단기 로드맵·가장 효율적인 다음 작업·권한 경계를 간결하게 설명해라. **반드시 여기서 멈추고 내 '진행'을 기다려라.** 첫 응답에서 구현·커밋·Actions/Native·새 실원본 수집 금지. main/불변 자료/Project Sources/UI/Work OS 권한은 별도 승인 없이 변경하지 마라.
