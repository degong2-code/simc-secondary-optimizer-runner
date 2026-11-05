# SIMC SECONDARY OPTIMIZER — P3-EE 단일 새 채팅 인계 정본
**인계 시점:** 2026-11-05 KST · **형태:** GitHub 격리 개발 연속성/읽기 전용 복원 · **정책·제품·Work OS 공식 승격 아님**

## 0. 실제 신원 · 신뢰 순서 · 필수 읽기 경로
- Repo: `degong2-code/simc-secondary-optimizer-runner`; isolation: `probe/chat-cache-v035-20261024`. **인계 준비 시 독립 확인:** isolation `c935afc82ab3f1b3e783ab48b89445b6249615f7`; `main` `07133e0aaf738d6e4816a6486057b1cd49c018de`. **이 문서 커밋 후 격리 HEAD가 바뀌므로 새 채팅은 둘을 반드시 다시 독립 조회**한다.
- 최신 검증된 **제품 코드** `3bfe85999604c63d570dd6c16a9ff3370385f2ac`(P3-ED). 확인한 인계 전 격리 HEAD와의 비교는 **후속 문서 3파일만 변경, 제품 코드 변화 없음**. 이후 HEAD도 반드시 GitHub 비교로 판정한다. GitHub 파일 이름, CURRENT 서술, 코드와 Action 영수증의 identity를 구분한다.
- **읽는 순서**: (1) isolation·main HEAD 별도 조회 → (2) 이 문서 → (3) [PROTOCOL](development/PROTOCOL.md) → (4) [INDEX](development/INDEX.md) 관련 capability → (5) 최근 [P3-DX](development/notes/2026-11-05_p3-dx-shared-f-o-native-source-only.md), [DY](development/notes/2026-11-05_p3-dy-source-only-flask-budget-auto-bridge.md), [DZ](development/notes/2026-11-05_p3-dz-independent-optional-g-vs-fo-native.md), [EA](development/notes/2026-11-05_p3-ea-v266-raw-gem-rating-normal-build-bridge.md), [EC](development/notes/2026-11-05_p3-ec-exactly-one-special-gem-policy-correction.md), [ED](development/notes/2026-11-05_p3-ed-v221-source-gems-mandatory-special-preview.md) → (6) 앞선 [P3-DN](development/notes/2026-11-04_p3-dn-v217-staged-source-relation-policy-a.md)/[DM](development/notes/2026-11-04_p3-dm-policy-a-receipts-normal-build-connect.md), [DS](development/notes/2026-11-04_p3-ds-controlled-web-cold-start-acceptance.md)/[DT](development/notes/2026-11-04_p3-dt-controlled-t1-missing-budget-stage.md)/[DU](development/notes/2026-11-05_p3-du-automatic-exact-physical-fo-measurement-worklist.md)/[DV](development/notes/2026-11-05_p3-dv-auto-source-bound-flask-native-opt-in.md) 중 해당 항목 → (7) [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) **최상단 최신 기록** → (8) [개발자 실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md) → (9) [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)와 **그 이후 최신 사용자 직접 결정** → (10) 실제 v216/v212/v222/v220/v196/v221/v266/v268/v271/v278/v281/v277/v098 코드·봉인 원본·Actions/Native.
- 전 인계 [P3-DW](CHAT_CONTINUITY_HANDOFF_20261105_P3_DW_ENGINE_FIRST.md) 및 P3-DO/DF는 **이전 시점**이며, 이 P3-EE가 후속 단일 정본. v1.4.1에 남은 27 DPS/증강 포함 및 구 시즌 보석·J/F/O/Native 수치는 역사 참고만. **유효 지원 범위는 26 DPS, 증강 기원사·탱커·힐러 제외**.

## 1. 최종 제품과 현재 제품 Gate
- 최종 목표는 **개별 기능이 아니라 다음 시즌에도 그대로 재사용되는 하나의 엔진**이다. 미래 파밍 목표 ilvl(기본 334) 또는 사용자가 지정한 **최종 T**에서 치명/가속/특화/유연 **절대 rating**으로 **SimC DPS 최대화**, 관측 1순위와 95% 유의 판정 분리, DPS·SEM·비율·실질적으로 다른 근접 대안·캐시·취소·재개. 26 DPS 공통. 사용자 현재 전체 장비 재분배, 장비/획득 경로 추천, 시즌 전체 아이템 DB, 자체 APL·proc·효과 재구현/새 효과 인증 Gate **제외**.
- **현 개발 대상/완료 기준 = 실제 사용자 웹앱의 동일 `v216 Environment Build`**. 새 시즌 정상 수집→시즌 대표 일반 장비·무기·티어4와 **G/J/F/O 전부** 원본·정적 검증→기존 `v222` **B=G+J+F, T=B+O** / L·E·O 중복 방지 / 사용자 수동 최종 T 우선→검증된 최고 품질·정책 A 대상 `v220/v196` 실제 발행→`v212` 시즌 환경 설치/READY와 동일 엔진 T1. `v098→v096/v094` 사용자별 적응형 DPS 실행은 **후속 메인 개발**, 현재 Environment Build READY의 필수 Gate **아님**.
- **특수 보석은 정확히 1개 필수**(2026-11-05 최신 사용자 직접 교정). 종류/시즌 ID 선택 가능 ≠ 미장착 허용. P3-EB의 무특수 구현은 [P3-EC](development/notes/2026-11-05_p3-ec-exactly-one-special-gem-policy-correction.md)에서 철회; 이후 [P3-ED](development/notes/2026-11-05_p3-ed-v221-source-gems-mandatory-special-preview.md)는 필수1 + 일반N을 새 동일빌드 ID로 **미승인 source-only** 연결. 단순 ItemID 존재 ≠ 실제 특수 유형·품질·인게임 소켓·효과·정적 J 승인.
- **예산·시즌 안전:** `O` 고정/비자유분배; E/L/G·O는 각각 한 번만 회계, 장신구 고정치는 자유 G 밖. 새 시즌에 구 시즌 79×2/B, J=138/F=165/기름 치명16+가속16을 인증값처럼 복사 금지. exact G Native는 선택 경로. 정적 캐시는 같은 시즌 SimC revision 변경만으로 폐기 금지. 서로 다른 DPS 조건은 엄격한 SHA/cache identity. 기본 영구 마부는 검증 대상, 일반 임시 마부 제외, 무기 기름은 별도 지원; 선택적 음식/물약·시즌 모듈 미검증 때문에 검증된 기본 환경까지 막지 않음.

## 2. Evidence ≠ Integration · 최근 개발 현황
| 재사용 가능한 실제 코드/증거 | **Evidence** | **Integration/현재 상태와 다음 판정** |
|---|---|---|
| `v161/v191/v211/v213/v217/v241/v216`; [P3-DS](development/notes/2026-11-04_p3-ds-controlled-web-cold-start-acceptance.md) | 통제 최소 시즌 원본 T0 수집·봉인, SHA/캐시/변조 차단 오프라인 PASS | **T0 PASS ≠ 전체 T1 READY**; 실제 최신 시즌 기본 예산 및 설치는 미완료, 기존 source collector 재개발 **STOP** |
| `v233/234/241/254/271/277/285/286`, gear/tier source SHA·[P3-DG](development/notes/2026-11-04_p3-dg-v191-gear-tier-raw-sha-link.md) | 대표 장비·무기·티어 후보 및 일부 G Native·소켓 stage/identity, code+부분 증거 | 새 시즌 대표 G 유효 범위, 기본 J/소켓·티어 4 검증/공식 승인·설치 연결 **미완료**; exact G optional |
| `v221/v266/v268→v271` [P3-EA](development/notes/2026-11-05_p3-ea-v266-raw-gem-rating-normal-build-bridge.md)/[EC](development/notes/2026-11-05_p3-ec-exactly-one-special-gem-policy-correction.md)/[ED](development/notes/2026-11-05_p3-ed-v221-source-gems-mandatory-special-preview.md) | 선택된 최대64 ID의 동일빌드 봉인 v221 관계, v266 raw 정적 숫자 투영, 필수 특수1개+일반N v139/v098 source-only 프로필 연결, 기존 역사 4색 보존 | 원본 아이템 존재·raw EffectPointsMin은 **특수 역할·품질·실 SimC rating·적법 소켓 인증 아님**. 정확한 **최고 품질 기본 J/특수1·소켓 적용조건 증거와 공식 J 승격/자동 기본 배치 미완료** |
| `v281/v278/v286`, [P3-DU/DV/DX](development/notes/2026-11-05_p3-dx-shared-f-o-native-source-only.md) | 봉인 F/O 후보 자동 발견, F/O 선택적 측정, 공유 최대 8 신규 Native/Build·기름 hands, 캐시/측정 identity | **이미 구현**: 후보 발견/F/O opt-in 재작성 **STOP**. 정확한 같은 시즌 F 최고품질/효과 범위·O 손별 무기 적합성/실 정적 값·공식 등록 **PENDING** |
| [P3-DY](development/notes/2026-11-05_p3-dy-source-only-flask-budget-auto-bridge.md)/[DZ](development/notes/2026-11-05_p3-dz-independent-optional-g-vs-fo-native.md) | 단일 F 관측 가족+G/J→기존 v222 **O=0 가정인 미승인 숫자 시나리오**, v281 최대128 cached rows; F/O와 exact G **독립 opt-in** | **O=0은 미리보기 가정**이지 공식 기름 없음 인증 아님. 과거 P3-DW의 “F/O 측정에 G Native 필수”는 **구버전 설명—폐기**. 정확 G/O/품질·공식 B/T 미완료 |
| `v222/v212/v220/v196`, [P3-DN/DM/DQ/DR/DT](development/notes/2026-11-04_p3-dt-controlled-t1-missing-budget-stage.md) | 기존 회계·출처 SHA/선택지 정책 A 판정 primitive·버전화 source-only 환경 stage | 코드에서 `v212.compile_fresh_source_environment`은 `FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED`, `official_G/J/F/O/B/T=None`, `environment_ready/installed/options_published=False`; `v196`은 eligible도 **UNPUBLISHED**. **공식 예산·정책 A 실제 발행·원자적 설치/READY·T1 모두 미완료** |
| `v098/v096/v094`, v177/adaptive cache·SEM/95% | 내부 적응형 실행/프로필·부분 오프라인 검증 및 유효 과거 Native | 최종 사용자별 26 DPS 제품 통합은 **후속**, 현재 환경 구축 Gate에 포함하지 않음 |

**개발 중단/역사 교정:** P3-EB의 “특수 보석 미장착 허용” 코드·성공한 242 tests는 **오류 요구사항의 역사 기록**이며 P3-EC에서 rollback. 새 특수보석 ID를 허용한 P3-ED도 *실제 인게임 역할·품질 증거*까지 자동 발행하지 않는다. `v216` 모듈 머리의 오래된 “recollection/Native 없음” 설명은 구현 당시 주석이므로 현재 함수 본문·실행 영수증을 우선한다.

## 3. 검증 receipt — 같은 SHA/조건만 재사용
- **최신 검증 코드 `3bfe85999604c63d570dd6c16a9ff3370385f2ac`:** [focused #41952509428](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41952509428) **243 PASS/0 FAIL·DEV_LEDGER_PASS**; [v212 #41952509430](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41952509430) Ubuntu/Windows 각각 **445 tests = 441 PASS/4 SKIP, NATIVE0**; [v098 #41952509403](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41952509403) **374 PASS**; [API #41952509395](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41952509395) 각 **214 PASS**; [UI #41952509407](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41952509407) 각 **93+88+2 PASS**; [Windows #41952509351](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41952509351) 각 **148 PASS + localhost 3 Plan restore**; [v180 #41952509387](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41952509387) offline SUCCESS, optional Native-six job **SKIPPED**. Actions 11 workflows 모두 SUCCESS. 이 값은 실제 Actions/jobs/logs로 재확인한 결과.
- 역사 [P3-EC #41949970604](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41949970604) **240 PASS**(P3-EB rollback), [P3-EA #41945241274](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41945241274) **239 PASS**, [P3-DZ #41943267465](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41943267465) **236 PASS**, [P3-DY #41940098545](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41940098545) **235 PASS**, [P3-DX #41937405565](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41937405565) **232 PASS**; 범위별 역사 증거로만 재사용, 합쳐서 전체 제품 PASS라고 하지 않는다. CI 도중 교정한 ledger/expectation FAIL도 각각 해당 note에 보존됨.
- 기존 같은 시즌/특정 바이너리의 실제 Native [소켓 #41601140696](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696), [F/O A #41666305288](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666305288), [F/O B #41666925906](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666925906), [무기 #41732744145](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41732744145)는 **그때의 시즌·프로필·바이너리·item ID/변형·조건에만** 유효. 신규 시즌 기본 J/F/O/READY를 인증하지 않음.
- **이번 P3-EE 인계는 문서만 변경:** 신규 코드·실 Native·외부 게임 HTTP·제품 테스트·Actions/CI **0회**. 상기 영수증은 전부 **과거 실행 재사용**이며 “이번에 새로 PASS”로 표기 금지. 완료를 선언할 **실제 T1 환경 READY PASS 영수증 없음**.

## 4. 현재 병목과 더 효율적인 다음 최소 작업
**핵심 병목:** 새로운 보석/영약·기름 기능 부족보다 **원본에서 검증한 같은 시즌 사실(특수 gem 종류 정확 1개+최고품질·실 소켓·정적 J, G 유효값, F/O 품질·손별 조건)과 실제 정책 A 발행/공식 B/T/환경 설치 경계**가 연결되지 않은 것. 최신 P3-ED는 ID 존재 확인까지만 해결. source-only preview를 반복 확대해도 READY는 완성되지 않는다.
1. **단기 A — REUSE/CONNECT:** INDEX·P3-BH/BX/BZ/BV/EA/EC/ED, P3-DN/DM/DU~DZ 및 봉인 source·실 Native 범위를 우선 비교. J의 특수 보석 **1개 필수** 유형/품질·사용 소켓/일반 보석 실 정적 rating, F 최고 품질·O 손별 무기조건, G 기존 같은 시즌 참조 또는 exact 소스의 정확 적용 범위를 **작은 provenance/admission 필드로** 연결. 새 collector·새 일반 아이템 DB·다전문화 Native 전수 **STOP**. 실제 원본이 없는 조건은 항목별 보류하고 원문·SHA와 정확 부족 사실 기록. *같은 시즌*에서만 기존 실측 재사용.
2. **단기 B — CONNECT:** 기존 `v222`를 유효 공식 G/J/F/O·E/L/O 소유권/수동 최종 T/중복방지에 연결→기존 `v220` 판정기로 **검증된 최고 품질만** `v196` 실제 목록 발행→`v212` 버전화 환경 **원자적 설치/READY**. **필수 예산 미확정이면 READY 불가**. 선택적 항목 미확정이면 그 항목만 보류. `v212` source-only stage의 false 필드를 단순 true로 바꾸는 행위 **금지**.
3. **단기 C — 통제 수용:** 위 **동일 사용자 웹 `v216` Build**로 빈 시즌 T1 정상 수집→봉인→검증→실제 설치/READY→동일 요청 REUSE·변경 SHA invalidation·부분 보류/취소·재개를 최소 격리 검증. [P3-AA](P3_AA_20261102_SINGLE_ENGINE_FRESH_SEASON_CONTROL_ACCEPTANCE.md) 준수: **기존 시즌 스냅샷/캐시를 새 시즌 시험 입력으로 재사용 금지**, 정상 엔진의 새 외부 데이터 수집은 허용. 단 T0나 소수 source-only synthetic PASS를 T1로 표기 금지.
4. **장기:** READY 이후 기존 `v098/v096/v094` adaptive SimC와 목표 절대 rating, DPS·SEM·95%/대안·cache/중단 재개, 26 DPS 공통 실사용 웹·Windows 결과를 통합. 새 최적화 엔진/효과 재구현/무차별 Native 반복 불필요.

모든 작업 전에 **기존 기록·INDEX·원본 바이트·코드·Native/Actions 영수증 선조회 → Evidence/Integration 별도 판정 → `REUSE/CONNECT/EXTEND/NEW/STOP` → 독립 작업 논리적으로 묶음 → 이전 PASS·정적/DPS 캐시 재사용 → 변경된 최소 경로만 검증**. 매번 HTTP/Native 호출 수·중복·캐시 무효화·RAM·I/O·전체 실행시간·복잡도 및 **“다음 시즌에도 하나의 엔진으로 동작하는가?”**를 명시 자가점검.

## 5. 실제 반영·미반영/권한
- **반영 대상:** 이 P3-EE 단일 인계 파일과 `docs/development/PROTOCOL.md`, `docs/development/INDEX.md`, `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md`, `docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md`, [P3-EE 짧은 기록](development/notes/2026-11-05_p3-ee-engine-continuity-handoff.md)을 **격리 브랜치에만** 갱신. 실제 커밋·반영 SHA는 브랜치 재조회로 확인; 문서 작성 자체를 Project UI 등록으로 주장 금지.
- **미반영/미승격:** 새 제품 기능·Native·외부 게임 HTTP·Actions 재실행 없음. 사용자 승인 v1.4.3 원문·원본 `v016_SCENARIO_CONTRACT` 및 immutable `v003`, `main`, 공식 Work OS M0/Shared State·Project Sources/Instructions UI, MAIN/WORK authority **수정·공식 승격 없음**. 현재 주 제품 개발 채팅의 기존 소유권은 변경하지 않음.
- GitHub 코드/노트/Actions는 Project UI 적용·공식 예산 승인·T1 전체 READY PASS의 대체 영수증이 아님. 모든 초회 복원 정보는 새 채팅이 실시간 GitHub로 독립 비교할 것.

## 6. 새 채팅 시작 프롬프트 — 첫 응답은 복원 보고 후 STOP
```text
SIMC SECONDARY OPTIMIZER 프로젝트를 **읽기 전용으로 독립 복원**해.

저장소: degong2-code/simc-secondary-optimizer-runner
격리 브랜치: probe/chat-cache-v035-20261024

먼저 격리 브랜치와 main의 실제 GitHub HEAD를 **각각 독립 조회**해.
최신 단일 인계 정본: docs/CHAT_CONTINUITY_HANDOFF_20261105_P3_EE_ENGINE_FIRST.md
읽기 순서: 새 인계 → docs/development/PROTOCOL.md → docs/development/INDEX.md → P3-DX/DY/DZ/EA/EC/ED 노트 → 관련 P3-DN/DM/DS/DT/DU/DV 및 원본·검증 이력 → docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md → docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md → 최신 승인 v1.4.3 및 이후 사용자 직접 정정 → 실제 관련 코드·봉인 원본·Actions/Native 영수증.

최종 목적은 **26 DPS 전문화(증강·탱커·힐러 제외)에 공통 적용되는 재사용 가능한 단일 엔진**으로 목표 ilvl/최종 T 기반 CHMV 절대 rating을 SimC DPS로 최적화하고 SEM·95% 판정·관측 1순위/근접 대안·캐시·취소·재개를 제공하는 것이다. 개별 기능 개발 자체가 최종 목적이 아님을 계속 자가점검해.

**현재 완료 Gate**는 단일 사용자 웹앱 v216 Environment Build에서 대표 일반 장비·무기·티어4/시즌별 G/J/F/O 자동 검증 → 기존 v222 B/T 회계 → 검증된 최고 품질/정책 A 실제 선택지 발행 → v212 시즌 환경 설치/READY·T1이다. 이후 v098→v096/v094 사용자별 DPS 최적화는 이 Gate 밖의 후속 개발이다. 특수 보석은 **정확히 하나 필수**, 종류만 선택 가능. P3-EB ‘없어도 됨’은 사용자 정정으로 폐기됐고 P3-EC/ED가 유효하다.

**매 작업 전** INDEX·기존 노트·원본 코드/영수증 선조회; Evidence와 Integration 분리; REUSE/CONNECT/EXTEND/NEW/STOP 판정; 이미 있는 F/O 후보·Native opt-in, v221/v266/v268 보석 ID, v271 가변 소켓, v222 계산, v220 결정기를 다시 만들지 마. 독립 작업은 논리적으로 묶고 동일 완료 기준·기존 유효 PASS/캐시를 재사용하며 Native/HTTP/Actions 중복, I/O·메모리·시간·구조 복잡화를 매번 검토해. 구 시즌 J138/F165/79×2/O16+16 수치를 새 시즌 검증값으로 옮기지 마. T0 원본 봉인과 source-only/offline PASS를 T1 전체 READY로 혼동하지 마. 실제 v212 official_G/J/F/O/B/T null / 설치 false 및 v196 미발행 상태를 임의로 승격하지 마.

**첫 응답은 다음만:** 실제 격리/main HEAD, 최신 Actions·Native 영수증과 적용 범위, 최종 제품/현 Gate, Evidence vs Integration의 완료·미완료, 현 병목과 더 효율적인 대안, 간결한 단기·장기 로드맵, 미반영·미승격·권한 제한. GitHub 코드·상태·원본을 **독립 대조한 복원 결과**를 보고하고 즉시 STOP.
**내가 명시적으로 '진행'하기 전에는 개발·코드/문서 수정·GitHub 커밋·신규 원본 수집·CI/Actions/Native/테스트 실행·공식 승격을 절대 시작하지 마.**
```
