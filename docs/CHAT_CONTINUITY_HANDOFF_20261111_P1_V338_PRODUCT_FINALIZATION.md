# SIMC SECONDARY OPTIMIZER — v338 제품 완성 단계 · 최신 독립 인계 정본
**기준:** 2026-11-11 KST. **역할:** 이 시점의 단일 최신 인계·새 채팅 첫 읽기 자료. 이전 [v331 연구 종료 인계](CHAT_CONTINUITY_HANDOFF_20261111_P2_V331_PRODUCT_FINALIZATION.md)는 역사 기준으로 보존한다. 이 문서 작성 자체는 새 Native·제품 최종 완성·공식 승격 증거가 아니다.

## 1. 현재 환경·권한·실제 HEAD
- GitHub repo: degong2-code/simc-secondary-optimizer-runner. 작업 브랜치: probe/chat-cache-v035-20261024. **인계 작성 직전 실제 HEAD df5d74b9d6f6a065616a631691a561a148ff1d4e**. 기준 main **07133e0aaf738d6e4816a6486057b1cd49c018de**. 비교 당시 diverged, ahead 3613 / behind 7. **본 인계 커밋으로 HEAD는 바뀌므로 반드시 다시 조회**한다.
- 작업 권한: 주 제품 개발 연속성을 위한 격리 브랜치. MAIN/WORK 공식 제품 주도권 이전이 아니다. main 병합, v003 immutable, 원본 v016 바이트 변경, Project Sources/Instructions 실제 적용, Work OS M0/Shared State, 공식 승격은 **별도 권한**이다. GitHub 문서를 써도 Project UI에 등록했다고 추정하지 않는다.
- 정책 우선권: 최신 사용자 직접 결정 > [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 및 비충돌 v1.4 계열 > 실제 코드·CURRENT·Actions/Native 증거 > 역사 인계. 실제 적용 여부는 별도. 역사 v1.4.1의 27 DPS/증강 포함 문구는 폐기, **26 DPS·증강/탱커/힐러 제외**.
- 기존 주 제품 개발 채팅에서 사용자가 새 채팅으로 인계하라고 직접 지시했다. 새 채팅 첫 응답은 **읽기 전용 복원 보고 후 STOP**. 별도 "진행" 전 코드·문서·테스트·Native·외부 API·Actions·커밋·병합·승격 금지.

## 2. 제품 목적·불변 입력/출력
- 목표 ilvl 기본 334 또는 사용자가 입력한 **최종 T**로 미래 파밍 목표 CHMV(치명·가속·특화·유연) **절대 rating**의 SimC DPS를 최대화한다. 사용자의 현재 장비 재분배, 장비 조합/획득 추천, 시즌 전체 장비 DB는 제외.
- 일반 사용자가 입력: 직업·DPS 전문화·종족·특성, 목표 ilvl/수동 T, 장신구 2, 선택 특수효과 장비, 장식 최대 2, 검증된 보석/영약/음식/물약/마부/기름/전투 조건. 대표 일반 장비·주능력·무기·티어4·SimC 프로필을 내부 구성. 업로드 프로필은 캐릭터 정보 추출 선택 기능이며 현재 장비/총량을 복사하지 않는다.
- B=G+J+F, T=B+O, c_final=c_base+o. 새 시즌엔 **G까지 포함** G/J/F/O를 그 시즌 원본으로 구축. 수동 최종 T 우선. 고정 L은 G에 포함·보호, E/O는 승인된 회계에서 각 1회; 장신구 고정치는 자유 G 밖, 미관측 gear≠0; 제작장비 초기 50:50/보석·영약 최초 스탯 분배는 자유 CHMV 하한이 아님.
- SimC는 아이템·proc·효과·APL·DPS 담당; 본 제품은 정확한 ID/ilvl/옵션, 총량·고정치·JSON2 rating, 후보·캐시·취소·재개·95% 판정 담당. 출력: 관측 1순위 절대 CHMV·비율·DPS·SEM·95% 우위 확인 여부·실질적으로 다른 근접 대안. 전역 최적·다중선택95 확정 과장 금지.
- 최고 품질만 표시하는 조건은 **동일 효과·사용 조건·범위가 원본으로 입증된 경우**. 사용자 공식 한국어 명칭은 단발 UI 번역이 아닌 시즌 환경 구축 엔진의 검증·자동 등록 연동 대상이다. 이름 확인은 효과/품질/사용 가능성 승인 자체가 아님. 정확한 SimC 토큰/ID·DPS 캐시 identity는 표시명과 분리한다.
- 기본 엔진 v290, 새 v293 세션 탐색 **N56/확인 N320**, 구 세션 N 필드 없으면 **legacy35**로 해석. N은 CHMV 1개당 iterations, 시작 후보 수가 아니다. 구 캐시·세션 폐기/재해석 금지. 탐색 발견·누락 방지 우선, 5~10분은 soft 목표, 95% 통계는 최종 검증용.

## 3. 코드/테스트 재사용 지도 (재개발 금지)
| 기능 | 주 코드 | 기존 증거 진입 |
|---|---|---|
| 시즌 수집/봉인/원본 실패 처리 | [v161](../runner/v161_wago_db2_snapshot.py), [v217](../runner/v217_stage_execution_engine.py), [v216](../runner/v216_environment_build_coordinator.py) | [v338](development/notes/2026-11-11_p1-v338-negative-season-source-recovery.md) |
| G/J/F/O·Policy A·설치/프로필 | [v222](../runner/v222_season_budget_contract.py), [v212](../runner/v212_environment_manifest.py), [v098](../runner/v098_target_user_scenario_bootstrap.py), [v139](../runner/v139_pure_target_profile_composer.py) | [v337](development/notes/2026-11-11_p1-v337-real-coldstart-environment-ko-reuse.md) |
| 공식 아이템명/게임 용어 | [v335](../runner/v335_environment_official_ko_localization.py), [v336](../runner/v336_environment_ko_playable_terms.py), [공식 77 아이템](data/current_season_gear_ko_KR_verified.json), [공식 64 용어](data/current_season_playable_terms_ko_KR_verified.json) | [v332~v336](development/EVIDENCE_INDEX.md) |
| 사용자 웹/SimC/탐색/재개 | [v113](../runner/v113_local_web_api.py), [v096](../runner/v096_unified_product_entry.py), [v094](../runner/v094_durable_inclusive_adaptive_runner.py), [v290](../runner/v290_multiscale_adaptive_policy.py), [v291](../runner/v291_durable_multiscale_session.py), [v293](../runner/v293_local_longrun_session.py) | [v334](development/research_receipts/p1_v334_survival_primary_n56_native_compact.json) |
| 사용 UI/배포 | [webui](../runner/webui), [Windows 패키저](../integration_probes/v181_windows_beta_packager.py) | [Chrome v333/v336·Windows CI](development/EVIDENCE_INDEX.md) |

**검색 순서:** [START_HERE](development/START_HERE.md) → [INDEX A~G](development/INDEX.md) → [FILE_MAP](development/FILE_MAP.md) → [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md) → [DECISIONS](development/DECISIONS.md) · [PROTOCOL](development/PROTOCOL.md). 최신 현재 판정은 [PRODUCT_CANONICAL_STATUS](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md) 상단, 누적 과거 상황만 필요하면 [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md)에서 필요한 부분만 확인. 2026-11-11 v331 원본 연구 영수증은 [compact](development/research_receipts/p2_v331_unholy_fixed_N_343_native_compact.json)로 보존.

## 4. 완료·검증·미실증의 정확한 경계
| 항목 | 현재 판정 | 원본 증거와 한계 |
|---|---|---|
| 시즌 환경 빌드·설치·대표 프로필 엔진 | **구현 + 현재 70783 한 조건 실제 Native PASS** | [v337 #43000049793](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43000049793): 완전히 빈 **설치 root**에서 Ret334 일반 보석4, G2850/J92/F165/O0, B=T3107, 환경 Native3·프로필 READY. 동일 빌드 패키지 원본/기존 검증 SimC 바이너리·언어 시드는 재사용. **다음 시즌 전체 원본 최초 실측 아님**. |
| 원본·현지화 재사용 및 원본 불일치 | **실 환경 재사용 PASS + 통제 실패 차단 PASS** | v337 최초 한국어 항목5→재실5, 두 번째 Native0/API0, 타 빌드 무단명칭·변조 거부. 첫 [#42999037211](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42999037211)에서 항목5→1 결함 발견, v113 검증 프로필의 보석4 ID를 복원하여 수정/재실증. |
| 공식 한국어 이름 자동 구축 | **v335/v336 구현·현재 조건 검증** | [Blizzard 실제 아이템명 77/77 #42980205042](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42980205042), [공식 직업13+DPS26+종족25=64/64 #42992243293](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42992243293), [실 Chrome #42993300954](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42993300954). 같은 빌드 캐시 SHA·한글 표시, SimC 입력 영문/ID 유지. **새 시즌 전체 선택 품목/품질 실증은 아님**. |
| 사용자 N56 실행·통계 | **기본 코드 적용·실 SimC 한 조건 PASS** | [v331 N 실측343](development/research_receipts/p2_v331_unholy_fixed_N_343_native_compact.json) 이후 N56 기본, legacy35 유지. [v334 생존 #42983978567](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42983978567): 자동 T3107, 탐색 DPS Native12, DPS173172.97 SEM305.82 관측 CHMV1072/38/1577/420. **95% 선택쌍 방향 미확정·전역 최적 증명 아님·사용자 64회 전체 런 아님**. |
| 필수 외부 원본 수집 중단→복원 / 필수 예산 증거 누락 | **v338 통제 오프라인 PASS** | [웹 양 OS #43019927281](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43019927281): 필수 Wago DB2 503→안전한 HTTP422·v217 RUNNING→전체10표 재수집/봉인→3차 동일 요청 다운로드0. 별도 [v212 양 OS #43019927318](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43019927318): G/J/F/O 각 누락 설치 차단, 변조·같은 빌드 무단 교정 차단. **가상 12.2.0.99999 최소 CSV로 READY false**, 새 시즌 READY PASS 아님. 신규 Native0. |
| UI·Windows 배포, 캐시·취소·재개 | **핵심 구현·CI·부분 실제품 경로 PASS** | Chrome #42983424219/#42993300954, Windows ZIP HTTP/오프라인 CI, 과거 Native 캐시·재개 영수증 [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md). **사용자 개인 Windows에 실제 SimC 설치→시작→취소·재개→64회 완료→최종 결과 확인 전주기 미실증**. 미실증을 미구현으로 오판 금지. |
| v338 직후 정합성 | **공통 오프라인 PASS** | [#43019927299](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43019927299) 660 tests·2 SKIP·0 FAIL, [최신 HEAD 공통 #43021347607](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43021347607) 동일 660/2SKIP/0FAIL·개발 ledger PASS; **이 인계 문서 작성은 신규 Native0**. |

**재현·수정된 결함:** v337 보석 현지화 ID worklist 축소 5→1은 실제 재현 후 수정·5→5 재실증; v338 필수 Wago HTTP 실패가 일반 ValueError/OSError로 사용자에게 부정확하게 노출되던 경계를 안정된 오류 코드로 수정·오프라인 검증. **현재 이 두 결함의 수정 후 재발 증거 없음**.
**아직 미구현이라고 단정하지 말 것:** 다른 시즌·선택 조합의 실 Native 미실증은 기능이 없다는 뜻이 아니다. 현재 재현된 신규 미해결 중대 버그는 이 인계 시점의 확인된 증거에서 특정되지 않았다.

## 5. 이번 채팅의 사용자 결정과 시행착오
1. **공식 한국어 명칭 확인은 Environment Build 엔진의 필수 과정**이다. v332의 77개 1회 조회만으로 완료를 선언하지 말고 v335 아이템명 및 v336 직업·전문화·종족 공식 ID 소스·증분/불변 SHA 캐시로 통합. 현지화는 표시 데이터이며 선택 허가/효과/예산과 분리. 새 시즌/품목 추가 시 검증된 최고 품질 선택지와 연결.
2. 다음 시즌의 원본이 아직 없으므로 **현재 실제 시즌 무이력 설치 + 동일 빌드 무중복 재실행 + 통제 누락·변조 시험**이 현실적인 사전 수용 실험. 빈 설치 root는 역사적 동일 시즌 소스·정확 바이너리까지 모두 없다는 의미가 아니다. 실제 미래 시즌 준비 PASS라고 과장하지 않는다.
3. 첫 v337에는 기존 설치 재사용이 보석 원본을 누락해 공식명 scope가 5→1로 축소. **원본 소유권은 봉인된 v113 대표 프로필**로 복원; 명칭 캐시에서 ID를 역추론하는 우회는 금지. 같은 환경 두 번째 호출 Native/API0과 scope까지 동일해야 한다.
4. v338에서 필수 CSV 전송 실패를 별도 안전 코드로 표시하고 stage RUNNING 영수증을 살려 원래 수집 경로로 복원했다. 임의 빌드 T0 fixture의 헤더 CSV만으로 시즌 완료 판정 금지. v212 필수 G/J/F/O 제거 실험과 선택적 항목 보류/손상 격리를 분리.
5. 기존 연구 v331 종료 → 제품 완성 우선. v290/N56/320과 정확한 레거시 세션·DPS 캐시 보존. 추가 탐색 엔진 연구/전수 Native/이름 수집 일괄 재시작 STOP. 실제 재현 결함 또는 새 소스 요구가 있을 때만 최소 재검증.

## 6. 정확한 다음 개발 시작점과 로드맵
**현재 병목:** 신규 시즌 원본 부재 자체가 아니라 **최종 Windows 실사용 흐름·검증된 선택 항목/문구의 연결 완성**, 그리고 새 시즌 때 실제 원본으로 최초 Build할 준비다.

**P1 (REUSE/CONNECT):** [웹 API](../runner/v113_local_web_api.py) + [웹 UI](../runner/webui) + [Windows 패키징](../integration_probes/v181_windows_beta_packager.py) 기준, 사용자 입력→로컬 SimC 연결→한 번 시작 N56→진행/취소/재개→결과/영수증 재열기 경로의 실제 미검증 부분만 추적. 필요한 경우 범위 한정 자동 Windows E2E/1개 실제 DPS 시험. 이전 Chrome/Native 캐시·증거 재사용. 시각·한국어 선택지의 미세 UX 결함은 재현 시만 수정.
**P2 (CONNECT/VERIFY):** 검증된 장신구·특수장비·영약·기름·보석·장식·마부 선택 메뉴와 v335 공식명 생성물의 연결 상태를 소스별 확인. 전 시즌 전체 목록/품질 원본 자동 구축이라는 기존 엔진 책임을 재개발하지 말 것. 실제 필요한 좁은 실패 케이스만 시험. 동일 시즌 GJFO/77/64 증거 반복 금지.
**새 시즌 최초 공개 시 (VERIFY):** 새 게임 빌드/SimC 바이너리·대표 장비/티어/정적 G/J/F/O·선택지/한글 공식 원본 출처 확보→v216 기존 단일 Environment Build empty install→v222/v212 B/T·L/E/O/품질 검증→v335/v336→v113/대표프로필→최소 실제 SimC JSON2 및 캐시/재개. 필수 미확정 시 READY 금지, 선택적 미확정만 보류. **동일 조건 Native 전수 반복하지 않음**.
**장기:** Windows 배포본 실사용/지원 안내·제품 버전 확정; 시즌/모듈별 데이터 증분 갱신과 기존 증거·캐시 호환 유지. 프로젝트 주도권·보호된 원본·main·공식 승격은 별도 승인.

## 7. 자원·증거·권한 운영
- 같은 시즌 정적 DB/아이템 소스는 SimC revision만 바뀐 이유로 폐기하지 않는다. 정확한 게임 빌드·원본 SHA·아이템 변형 identity를 보존. 정적 DB 교정은 명시 요청·증거가 있을 때만. DPS 캐시는 실제 SimC binary/revision·프로필/장비/옵션/모듈·CHMV/O·전투조건·iterations에 따라 분리.
- v331 343 Native·v337 3+3 환경 Native·v334 12 DPS Native를 다시 하지 않는다. 실 CI PASS와 RAW Native 입력·JSON2·SHA 검증을 별도 기록하고, 과거 artifact 일부는 만료된다. Git tracked compact 원본과 실행 링크·캐시 원본을 우선 재사용.
- 한 작업의 REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP 판단, 중복 API/Native·CPU·메모리·I/O·실행시간·세션 취소/재개·캐시 identity 검토. CODE_IMPLEMENTED / OFFLINE_PASS / REAL_NATIVE_PASS / USER_WEB_E2E_PASS / NOT_PROVEN / REPRODUCED_BUG를 분리.
- 신규 실증을 시작하기 전 최신 GitHub HEAD·Action·원본/비밀 정보 권한 확인. 본 인계 자체는 새 소스 수집/Native/Actions를 요구하지 않는다.

## 8. 다음 채팅 읽는 순서 (처음부터 전수 감사 금지)
1. **본 최신 단일 인계**.
2. [START_HERE](development/START_HERE.md) → [INDEX](development/INDEX.md) → [FILE_MAP](development/FILE_MAP.md) → [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md).
3. [PRODUCT_CANONICAL_STATUS](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md) 상단 A~G 최신 보충, [DECISIONS](development/DECISIONS.md), [PROTOCOL](development/PROTOCOL.md).
4. [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 및 충돌 없는 이전 정책. Project UI 적용 여부 확인 불가시 미확인.
5. 최신 v337/v338 노트 및 [영구 v337 실증](development/research_receipts/p1_v337_zero_history_gjfo_ko_compact.json), [v331 연구](development/research_receipts/p2_v331_unholy_fixed_N_343_native_compact.json), [v334 제품 실제 Native](development/research_receipts/p1_v334_survival_primary_n56_native_compact.json). 필요한 파일/테스트·CURRENT 일부만 추가 탐색.

## 9. 새 채팅 독립 복원용 시작 프롬프트
~~~text
SIMC SECONDARY OPTIMIZER 프로젝트를 최신 실제 GitHub 상태로 읽기 전용 독립 복원하라.

저장소: degong2-code/simc-secondary-optimizer-runner
개발 격리 브랜치: probe/chat-cache-v035-20261024
인계 작성 직전 HEAD: df5d74b9d6f6a065616a631691a561a148ff1d4e (인계 커밋으로 변경됨)
main 기준: 07133e0aaf738d6e4816a6486057b1cd49c018de
최신 단일 인계:
docs/CHAT_CONTINUITY_HANDOFF_20261111_P1_V338_PRODUCT_FINALIZATION.md

실제 GitHub 두 HEAD와 해당 최신 Actions 영수증을 반드시 다시 확인하라. 먼저 최신 인계 → docs/development/START_HERE.md → INDEX.md → FILE_MAP.md → EVIDENCE_INDEX.md → PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md의 상단 최신 보충 → DECISIONS.md → PROTOCOL.md → 승인 v1.4.3 → 필요한 v337/v338 원본만 읽어라. 누적 CURRENT/오래된 인계 전수 감사를 하지 말라.

최종 목적은 26개 DPS 전문화에서 기본 ilvl334 또는 수동 최종 T의 CHMV 절대 rating을 SimC DPS로 최대화하는 제품 완성이다. B=G+J+F, T=B+O, 새 시즌 G/J/F/O 전체 자동 구축, 수동 T 우선, L/E/O 중복 금지, SimC 효과/APL/DPS 책임, 결과 DPS·SEM·95%·관측 1순위·근접 대안·비율을 유지한다. 현재 장비 재분배/장비조합 추천/전 시즌 장비 DB/증강·탱커·힐러 지원은 제외한다.

기존 v216/v212 환경 엔진·v335/v336 공식 한국어 자동 구축·대표프로필/선택 기능·v290 탐색·v293 새 N56/320 및 legacy35·캐시·취소/재개·웹 UI/Windows 패키저를 재개발하지 말라. v337 현 시즌 빈 설치 root 실 Native3/공식명5/게임용어64 및 반복 Native/API0 PASS, v338 필수 원본 장애→안전 코드→재시도·봉인/필수 GJFO 누락 차단 오프라인 PASS를 정확히 구별하라. 두 실험은 미래 시즌 전체 READY 증거가 아니다. v334 생존 Native12는 전체 64호출/전역 최적/95% 확증이 아니다.

당면 우선순위: 실제 남은 Windows 사용자 경로(설정·실행·취소/재개·최종 결과)와 사용자 선택지/공식 한국어 표시 연결의 재현된 결함만 CONNECT/FIX, 기존 증거 재사용, 최소 범위 검증. 새 시즌이 공개되기 전 가짜 빌드 READY로 일반화를 주장하거나 Native 전수를 반복하지 말라. REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP 우선 판단. main/immutable v003/원본 v016/Project UI/Work OS/공식 승격은 별도 권한이며, MAIN/WORK 운영 권한을 인수하지 말라.

새 채팅 **첫 응답은 읽기 전용 독립 복원 보고만** 한다. 실제 최신 HEAD, 완료/부분 완료/오프라인 PASS/실 Native PASS/미실증·결함, 핵심 최신 v337·v338 영수증, 현재 병목, 단기·장기 로드맵, 권한을 보고한 뒤 **즉시 STOP**한다. 내가 별도로 "진행"을 승인하기 전까지 코드·문서 수정, 테스트, 외부 수집, Native, Actions, 고비용 작업, 커밋·병합·공식 승격을 절대 시작하지 않는다.
~~~
