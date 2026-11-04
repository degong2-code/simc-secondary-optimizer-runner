# SIMC SECONDARY OPTIMIZER — P3-DW 새 채팅 단일 인계 정본
**작성 기준:** 2026-11-05 KST · **구분:** 격리 개발 연속성 인계 / 코드·실 Native·게임 수집 미실행 / 미승격

## 0. 신원 및 복원 순서
- Repository: `degong2-code/simc-secondary-optimizer-runner`; isolation branch: `probe/chat-cache-v035-20261024`.
- **인계 준비 전 확인한 코드·기록 HEAD:** `5c335a0eb60c86217af98f89ddc57e25348500e7`; **main HEAD:** `07133e0aaf738d6e4816a6486057b1cd49c018de`. 이 문서 작성으로 격리 HEAD가 다시 이동하므로 **새 채팅은 두 HEAD를 독립적으로 재조회**할 것. 현재 정본 여부는 브랜치의 파일 내용과 Actions commit SHA로 검증. `main`과 비교하지 않은 채 동일하다고 추정하지 않음.
- 읽기 순서: (1) 두 GitHub HEAD 독립 조회 → (2) [PROTOCOL](development/PROTOCOL.md) → (3) [INDEX](development/INDEX.md) 해당 capability → (4) [P3-DN](development/notes/2026-11-04_p3-dn-v217-staged-source-relation-policy-a.md)/[P3-DM](development/notes/2026-11-04_p3-dm-policy-a-receipts-normal-build-connect.md), [P3-DS](development/notes/2026-11-04_p3-ds-controlled-web-cold-start-acceptance.md)→[P3-DT](development/notes/2026-11-04_p3-dt-controlled-t1-missing-budget-stage.md)→[P3-DU](development/notes/2026-11-05_p3-du-automatic-exact-physical-fo-measurement-worklist.md)→[P3-DV](development/notes/2026-11-05_p3-dv-auto-source-bound-flask-native-opt-in.md) → (5) [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 최신 머리말 → (6) [개발자 실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md) → (7) [최신 승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 및 최신 사용자 직접 변경 → (8) 실제 코드/원본/Native·Actions 영수증.
- [P3-DO](CHAT_CONTINUITY_HANDOFF_20261104_P3_DO_ENGINE_FIRST.md), P3-DF와 이전 인계는 **역사**이며 P3-DW가 후속 정본. v1.4.1의 **27 DPS/증강 포함 문구는 과거 스냅샷**: 유효 대상 **26 DPS, 증강·탱커·힐러 제외**.

## 1. 제품의 최종 목표 vs 이번 구축 범위
제품 최종 목표는 **개별 아이템 기능이 아닌 26개 DPS 전문화에 공통 적용되는 재사용 가능한 하나의 엔진**. 기본 목표 ilvl 334 또는 수동 최종 CHMV 총량에서 SimC DPS 최대의 **치명·가속·특화·유연 절대 rating**을 구하고, 비율·DPS·SEM·**95%** 관측 1순위/확정 여부·실질적으로 다른 근접 대안·캐시·취소·재개를 제공한다. 현재 장비 재분배·장비 조합/획득 경로 추천·전체 시즌 장비 DB/자체 APL·효과 인증 엔진은 범위 외.
**지금 개발 완료 기준은 웹앱의 동일 `v216 Environment Build`:** 빈 시즌에서 원본을 스스로 수집·봉인→대표 일반 장비/무기/티어4→동일 시즌 **G/J/F/O 전체** 자동 산출/검증→기존 `v222` **B=G+J+F, T=B+O**, 고정 L/E/O·수동 최종 T 회계→정책 A 최고 품질 검증 선택지만 `v220/v196/v212` 실제 발행→버전화 환경 설치·**READY**. 사용자가 이후 정보를 입력하여 `v098→v096/v094`로 DPS를 최적화하는 작업은 **후속 메인 제품 개발**이며 Environment Build READY 선행 Gate가 아니다.
같은 시즌의 정확한 물리 ID·소켓·영약/기름·정적 rating과 SimC 책임을 유지한다. **구 시즌 G 참조/J138/F165/O16+16을 새 시즌 인증값으로 복사하지 않는다**. 일반 임시 마부는 제외, 무기 기름 지원. 선택 마부/음식/물약·Omnium 미확정으로 검증된 기본 환경을 일괄 차단하지 않는다.

## 2. Evidence와 Integration 분리 — 재사용 가능한 성과
| 영역 | 확보된 증거/코드 — REUSE | 제품 연결·승인 상태 |
|---|---|---|
| 원본 수집·봉인 | `v161/v191/v211/v213/v217/v241/v216`, 정본 SHA·단계 영수증·재요청 재사용. [P3-DS T0](development/notes/2026-11-04_p3-ds-controlled-web-cold-start-acceptance.md) 웹 API→진짜 수집/봉인, 합성 외부 10 CSV, 변조 차단 | **T0 PASS**, 통제한 최소 입력의 원본 단계만. 정상 동일 시즌 완전 입력으로 READY까지 **T1 미통과** |
| 대표 장비·티어/G·J | `v233/v234/v254/v271/v139/v277/v285/v286`, [P3-DK](development/notes/2026-11-04_p3-dk-v271-variable-socket-v098-bridge.md) 가변 소켓, P3-DG gear/tier 원본 SHA. SimC 기본 캐릭터 레벨 정책 [P3-BN](P3_BN_20261103_SIMC_DEFAULT_LEVEL_OPTIONAL_CHARACTER_AND_ENGINE_OWNED_ITEMS.md) | 동시즌 정확 G/J/소켓 합법성·최고 품질 기본 배치 **승인/자동 설치 미완료**. 새 캐릭터 레벨/소켓 엔진 **STOP** |
| F/O 자동 소스 | `v281` 원본 ID→SimC 토큰, `v278` 정적 before/after JSON2, 손별 oil mask; [P3-DU](development/notes/2026-11-05_p3-du-automatic-exact-physical-fo-measurement-worklist.md) 신규 정확 F/O 후보 worklist | **CONNECT 완료:** 후보 목록 자동 추출; 후보가 사용자 선택지로 등록되는 것은 아님. O 측정/무기 적합성, F 품질·효과 조건 **미완료** |
| F Native opt-in | [P3-DV](development/notes/2026-11-05_p3-dv-auto-source-bound-flask-native-opt-in.md) `v113` 웹 선택→`v216._auto_F_native_from_sealed_v281`→기존 `v278` 캐시/Native. 기본 OFF·F 선택 시 기존 G binary 필요·정상 반환 경로 신규 F Native 최대 8/요청 | **오프라인 모의 시험 PASS**, 이번 실제 Native 0. F 물리 입력·실측/최고 품질·공식 예산 승인 **아님**. 실패시 실제 호출 계수/원문 확인 필요 |
| 예산·매니페스트 | `v222` 수치 미리보기, [P3-DQ/DR](development/notes/2026-11-04_p3-dq-v212-versioned-season-environment-source-stage.md) source-only 버전화 `v212`+G/J/F/O SHA, `v217` 재사용. [P3-DT](development/notes/2026-11-04_p3-dt-controlled-t1-missing-budget-stage.md) 미관측 수치만 PENDING, 원본 단계 유지 | **공식 G/J/F/O/B/T, L/E/O 검증·정책 A 실제 발행·환경전용 설치/READY는 미완료**. `source_only`를 READY로 승격 금지 |
| 선택지/후속 DPS | `v220` 정책 A 판단기, `v196` eligible UNPUBLISHED; 기존 `v098→v096/v094` 적응형 DPS·SEM/95%·캐시/취소/재개 증거 | P3-DN `source_relation` 가족만 선연결, `simc_input/product_input/chmv_budget`와 실제 옵션 발행 미완료. 신규 26 DPS 전체 E2E는 미확인이고 **현재 Environment Build의 완료 Gate 밖** |

## 3. 이번 인계 직전 최신 Actions/Native — 적용 범위
코드 검증 커밋 `88537c7f9ace451b7c69f04d53475457cb5982b5`에서 [focused #41932094998](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41932094998) **230 PASS/0 FAIL+DEV_LEDGER_PASS**, [v212 #41932095074](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41932095074) Ubuntu/Windows **각 445 tests(441 PASS/4 SKIP), 0 FAIL + NATIVE0**, [웹 API #41932094995](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41932094995) 양 OS **각 213 PASS**, [웹 UI #41932095008](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41932095008) 양 OS 각 **93+87+2 PASS**, [Windows #41932095007](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41932095007) Python 3.12/3.14 각 **147 PASS**.
이번 P3-DW 인계 작업은 **DOCS_ONLY**, 신규 Actions/CI/게임 HTTP/SimC Native/제품 테스트 **0회**. 기존 P3-DV도 **신규 실제 Native/게임 HTTP 0회**. 과거 기존 시즌 F/O Native [A](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666305288)·[B](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666925906), [소켓](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696)·[무기](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41732744145)는 **증거가 적용되는 동일 시즌·빌드·변형만** 재사용. T0 PASS, 연결 단위 오프라인 PASS, 실제 시즌의 T1 READY PASS는 서로 다름.

## 4. 실제 병목·효율적 개발 순서
가장 큰 병목은 **미확정 원본 전수 부족이 아니라 수집된 동일 시즌 입력→기본 J/F/O의 품질·적용 조건 판정→공식 G/J/F/O·B/T→검증 선택지 발행·시즌 설치 READY의 단일 경로 미연결**. 새 collector·마부 인증기·시즌 전체 DB/별도 최적화 엔진을 만들지 않는다.
- **단기 1 (CONNECT):** `v216` 내 기존 `v271/v278/v281/v285/v286`와 `v220`에 **필요한 동일빌드/고품질/소켓/무기 조건 evidence**를 연결; 기존 봉인 SHA/Native 영수증의 유효 범위 먼저 확인. 자동 후보 발굴/측정은 기존 경로를 재사용하고 불확정은 항목별 PENDING. 이번 DV의 F opt-in을 새 Gate로 확대하지 않는다.
- **단기 2 (CONNECT/EXTEND):** 정확 필수 G/J/F/O를 기존 `v222` 승인 회계(B/T, L/E/O 소유권, 사용자 최종 T 우선)로 연결하고 `v220/v196/v212`의 **실제 기본 환경 설치/선택지 발행/READY**를 구현. 필수 예산 불명확→READY 금지; **선택적 마부 하나 미검증→그 항목만 미발행**.
- **단기 3 (수용시험):** **동일 실제 제품 엔진**으로 격리 빈 시즌의 T1 Cold Start→전체 설치→동일 입력 REUSE→원본 변경/손상/중단 재개·부분 보류를 통제 검증. 이후 [P3-AA](P3_AA_20261102_SINGLE_ENGINE_FRESH_SEASON_CONTROL_ACCEPTANCE.md) 기준 기존 데이터 미사용·정상 Wago/Blizzard/WCL/SimC 새 수집과 봉인 후 독립 비교. 통제 합성 입력/기존 역사 증거는 **실제 새 시즌 데이터 합격의 증거가 아님**.
- **장기:** 안정적인 웹 Environment Build를 완성한 뒤, 이미 구축된 `v098/v096/v094`를 재사용해 일반 사용자 26 DPS의 목표 절대 rating·DPS·SEM/95%·대안·캐시/취소·재개를 통합. 26×전 ilvl Native 전수 반복·SEM 미세 최적화·장비 추천 금지.
각 작업 **기록/INDEX 선조회→Evidence/Integration 구분→REUSE/CONNECT/EXTEND/NEW/STOP→논리적으로 묶어 최소 변경→기존 PASS 재사용·변경한 경로만 검증**. 비용: Native/HTTP·캐시 폐기·I/O·메모리·전체 시간·코드 복잡도 검토. 실제 게임 사실 추가 조사나 새 Native 실측이 필요하면 **기존 영수증 적용범위를 먼저 확인하고 사용자와 논의**.

## 5. 미반영·미승격·권한
- 승인 v1.4.3은 **기준 문서**이지 사용자 Project UI에 실제 업로드 완료했다는 증거가 아님. 이 인계에서 승인 문서 원문 수정 없음.
- GitHub **격리 브랜치 문서만** 갱신; `main`, 원본 `v016_SCENARIO_CONTRACT` 바이트·immutable `v003`, 공식 Work OS M0/Shared State·Project Sources/Instructions UI, MAIN/WORK authority **수정·승격 없음**.
- 새 채팅의 최초 응답은 **GitHub 양 HEAD·최신 Actions/Native·핵심 코드·미완료 상태 독립 복원 보고**만 하고 즉시 중단. 사용자의 **'진행'** 전에는 코드·문서 수정/커밋/수집/CI·Actions·Native/테스트 실행/공식 승격 **전부 금지**.

## 6. 새 채팅 시작 프롬프트
```text
SIMC SECONDARY OPTIMIZER를 읽기 전용으로 독립 복원해.
저장소 degong2-code/simc-secondary-optimizer-runner / 격리 probe/chat-cache-v035-20261024.
먼저 GitHub 격리와 main의 실제 HEAD를 각각 새로 조회한 다음, docs/CHAT_CONTINUITY_HANDOFF_20261105_P3_DW_ENGINE_FIRST.md → docs/development/PROTOCOL.md → docs/development/INDEX.md → P3-DN/DM 및 P3-DS/DT/DU/DV 관련 기록 → docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md → docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md → 최신 승인 v1.4.3 → 실제 코드·원본·Actions/Native 영수증 순서로 대조해.

최종 목표는 26 DPS 전문화에 재사용되는 하나의 엔진으로 목표 최종 CHMV 절대 rating/DPS·SEM·95%·근접 대안·캐시/취소·재개를 제공하는 것이다. 하지만 지금 개발/완료 판정 대상은 사용자 웹앱의 단일 v216 '시즌 환경 구축 엔진'이다. 시즌별 대표 장비·무기·티어4/G/J/F/O 전체 자동 구축 → v222 B/T → 검증된 최고 품질 정책 A 선택지 자동 발행 → 시즌 설치/READY까지가 현재 Gate이며, 사용자별 v098→v096/v094 DPS 최적화는 후속 개발이지 이 Gate가 아니다.

작업 전 기능별 INDEX·기존 노트·원본 바이트/코드·실제 영수증을 먼저 조회하고 Evidence와 Integration을 분리해 REUSE/CONNECT/EXTEND/NEW/STOP으로 판정해. P3-DU 자동 F/O 측정 후보와 P3-DV 명시 opt-in F Native 연결을 다시 만들지 마. T0와 부분 오프라인 PASS를 T1 전체 READY로 승격하지 말고, 구시즌 G/J/F/O 숫자를 새시즌 검증값으로 사용하지 마. 개별 기능보다 재사용 가능한 '엔진'을 계속 자가점검하고, 독립 작업은 묶어 처리하며 동일 기준 검증·과거 유효 증거·캐시를 재사용하고 중복 Native/HTTP/Actions·I/O·메모리·시간·구조 복잡화를 최소화해.

첫 응답에서는 실제 두 HEAD와 최신 검증, 최종 제품 목적, Evidence/Integration별 완료·미완료, 핵심 병목과 효율적인 대안, 단기·장기 로드맵, 미반영·미승격·권한 경계를 간결히 보고한 뒤 즉시 중단해. 내가 명시적으로 '진행'하기 전에는 개발, 코드·문서 수정, GitHub 커밋, 신규 수집, CI/Actions/Native/테스트 실행 또는 공식 승격을 절대 하지 마.
```
