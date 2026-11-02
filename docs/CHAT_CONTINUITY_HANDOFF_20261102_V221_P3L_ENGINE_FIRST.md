# SIMC SECONDARY OPTIMIZER — 새 채팅 인계 2026-11-02 / v221·P3-L

> **인계 후 최신 결정(2026-11-02) — 이 문서의 당시 상태보다 우선:** [P3-AA 최신 통제실험 교정](P3_AA_20261102_SINGLE_ENGINE_FRESH_SEASON_CONTROL_ACCEPTANCE.md), [v1.4.3 개발자 노트 §7](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md), [CURRENT 최상단](CURRENT_PRODUCT_DEVELOPMENT_STATE.md)을 먼저 읽을 것. **하나의 실제 제품 Environment Build 엔진만 개발**하고, 완성 뒤 기존 자료·캐시·영수증 없이 현재 시즌을 새 시즌처럼 구축하는 동일 실행 경로를 시험한다. 신규 Wago DB2/WCL/Blizzard/공개 GitHub/SimC 원본 다운로드는 차단하지 않는다. "SimC-only 최종 통제실험"은 잘못된 이전 해석이다. 이 문서의 역사적 GitHub HEAD/당시 작업 진척도는 실제 ref·CI를 다시 조회하여 확인하고 제품 구현 완료로 읽지 않는다.

> **이 문서는 지금 채팅의 최신 인계 진입점이다.** 과거 v216 인계는 그 당시까지의 증거다. 코드/CI 영수증보다 설계가 앞서 있는 항목을 “구현 완료”로 승격하지 말 것. 새 채팅은 먼저 **읽기·GitHub 실물 검증·복원 보고만** 수행하고 사용자 **“진행”** 전에는 코드 변경·Actions 실행·Native 수행을 하지 않는다.

## 0. GitHub 신분과 읽기 기준 (2026-11-02 실조회)

- Repository: [degong2-code/simc-secondary-optimizer-runner](https://github.com/degong2-code/simc-secondary-optimizer-runner), **Public**.
- Isolation branch: **`probe/chat-cache-v035-20261024`**, 이 인계 **작성 직전** HEAD `d521e400401024fc55b5c698fe120c972090fecc`. 이 인계 문서 커밋으로 HEAD는 달라지므로 **절대로 해당 SHA를 최신 HEAD로 고정하지 말고 ref 재조회**.
- `main` HEAD `07133e0aaf738d6e4816a6486057b1cd49c018de`; no merge. `v003` immutable / original `v016` / Work OS M0 / MAIN 소유권 / repository visibility의 승격·변경 없음.
- **현재 승인 우선순위:** 최신 사용자 직접 결정 > [v1.4.3 최신 보충 기준](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 및 충돌 없는 v1.4.x 승인 정책 > [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 및 실제 GitHub 코드·Actions/Native 영수증 > 역사 인계.
- 사용자는 최신 **Project Instructions를 직접 적용**했다고 보고했고 GitHub 승인 개발 기준·Project Sources 등록을 허용했다. **GitHub v1.4.3 등록 확인**, 하지만 이번 채팅에서 조회 가능한 Project 파일에는 **2026-10-29 v1.4.1 업로드 사본만** 보였고 v1.4 원문·v1.4.3의 **Project Sources 등록 영수증은 미확인**. 현재 입력의 프로젝트 지침은 적용됐지만 *파일이 Project UI에 저장됐다*고 추정하면 안 된다. 기존 업로드 v1.4.1의 27 DPS/증강 포함 문구는 **폐기**; GitHub corrected 2026-10-31 + v1.4.3가 최신이다.

## 1. 장기 목표와 지속 자가검증

**핵심 원칙: 개별 기능을 넣는 것이 아니라, 새로운 시즌·옵션에서 해당 기능을 정확하고 반복 가능하게 구현하는 엔진을 만든다.** 매 작업의 시작/끝에서 “특정 아이템용 예외 코드를 만드는가, 아니면 공통 source→classification→exact join→verification→versioned environment→SimC 실행 경로를 완성하는가?”를 자가검증한다.

제품: **정확히 26 DPS 전문화**(증강 기원사·탱커·힐러 제외). 사용자는 직업/전문화/종족/특성, 목표 ilvl(기본 334) 또는 수동 최종 T, 장신구 2개, 특수장비, 장식 최대 2개, 최고 품질 검증된 보석/영약/음식, 기름, 전투조건 등을 입력한다. 내부에서 일반 대표 장비·무기·티어 4세트·주능력치·SimC 프로필/예산을 만든다. 현재 장비 재분배/전체 시즌 DB/장비 조합·파밍 경로 추천은 범위 밖.

SimC DPS 최적화의 출력은 4종 CHMV **절대 rating**, 비율, 예상 DPS, SEM, **95%** 비교, 관측 1위와 통계적 우위 확정의 차이, 실제로 다른 근접 대안. 전역 최적해 증명 없는 결과를 확정이라고 하지 않는다. SimC가 APL·장비/장신구/장식/보석의 효과·proc·DPS를 소유; 우리 코드가 해당 효과를 재구현하거나 독립 효과 인증 Gate를 만들지 않는다. 기존 **v093/v094/v095 적응형 엔진**과 캐시/취소/재개/결과를 재사용하고 새로운 optimizer/collector/profile generator를 만들지 않는다.

## 2. 최신 승인 예산/품질/특수 시스템 정책 (반드시 그대로 적용)

- **시즌 갱신은 J/F/O만이 아니라 G 포함**: 동일 시즌·빌드 대표 일반 장비/무기/티어와 목표 ilvl의 G, 최고 품질 기본 보석 J, 영약 F, 선택 기름 고정 O를 원본과 증거로 결정. `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. 새 시즌 값으로 B/T **자동 갱신**. 필수 G/J/F/O 미확정이면 Environment Build 정상 완료라고 하지 않는다. 검증 안 된 선택 항목만 보류하며 나머지 정상 환경은 막지 않는다.
- **현재 시즌 참고값은 새 시즌에 복사 금지**: 79×2 Native 유래 rounded ilvl B, J=138, F=165, 기름 무기당 치명16/가속16. 유효한 동일 시즌·동일 조건의 측정·캐시는 재사용하고 실제 부족한 증거만 최소 비용 Native 확인; 전 전문화×전 ilvl 재실행 금지.
- **수동 최종 T 우선**: `B=T-O`로 내부 변환하고 J/F·L/E/O 하한 및 가능성 검증. 정확한 선택 특수장비 L은 이미 G/B 안의 하한, 이중 가산 금지. 정적 영구마부 E도 승인 회계대로 한 번만(마부 없는 자동 ilvl 기준에 한해 추가 E), 수동 T에 재가산 금지. 장신구 정적 gear 레코드 부재는 UNKNOWN(0 아님). 제작장비 최초 50:50을 L로 잠그지 않는다.
- **품질:** 같은 효과·동일 적용 범위·동일 사용 조건이며 모든 관련 수치에서 상위 품질 우월성까지 검증했을 때 **최고 품질만 UI**. 이름·아이템레벨·품질 이름으로 동등성 추정 금지. 소스 원본은 필요한 범위에서 보존.
- **마부:** 영구 마부는 검증·선택 대상. **일반 임시 마부는 제외**, 단 **무기 기름은 별도 O 설정으로 유지**(SimC 직렬화에 `temporary_enchant`가 쓰여도 예외).
- **특수 시즌/확장팩 콘텐츠:** Omnium Folio 등은 핵심 DB와 별도의 선택형 ON/OFF 모듈. OFF 시 프로필/예산에서 완전 제거; 상태/버전/옵션은 캐시/세션 정체성에 포함. Environment Build 완료 후 필요하면 GPT에 **별도** 특수모듈 업데이트 요청을 안내할 뿐 자동 GPT 호출/영구 의존성 금지.
- **정책 A:** 정확한 ID·소스·빌드·SimC 입력·물리적 적용 조건·CHMV 회계 소유권 증거가 모두 맞으면 수동 건별 승인 없이 신규 사용자 옵션 **자동 등록**. 검증 부족·충돌은 해당 항목만 보류. v220 판정/preview만으로 실제 UI 등록 완료로 표시하지 않는다.

## 3. 최신 구현 진척 — 새로 할 필요 없는 것

1. **시즌 장비/대표 프로필:** 기존 v161/v163/v165/v166/v167/v168/v169, v098/v139, 26/26 계획 공급원, 고정 L의 v208·Native 캐시. 기존 26 DPS 물리 프로필 SimC 스모크는 실증이 있으나 26/26 적응형 최적화 E2E는 아님.
2. **소스 파이프라인:** v189/v190 + v191→v211→v213→v196. 같은 빌드 provenance·SHA, 높은 품질 부분 추림, 마부 38행·일반 장비 511행 등 후보·분류. 발견 행=승인 옵션이 아님. v213은 장비/마부/장식/임시/보석 원본 join 상태와 미해결을 fail-closed 보고, 이전 카탈로그 호환성 보존. **임시 마부 117행은 역사 소스 자료지만 현재 제품 지원 범위에서 제외**.
3. **Environment/실행:** v212 manifest/dependency DAG → v216 installed-v213 Environment Build API/UI → v217/v218 SHA-sealed 단계 및 기존 v098 `run_manifest` worker handoff. 변경 source/세션 identity와 회수·resume 경로, stage reuse skip(동일 조건 추가 profile 생성 0회) offline 검증. v219은 실제 HTTP Plan 첫 실행과 재사용 3회 비용을 Ubuntu/Windows에서 **비영속 계측**; 메모리·DPS 실사용 시간 개선 수치로 일반화 금지.
4. **Policy A v220:** 정확 ID/slot/build/revision/catalog SHA와 네 가지 내부 증거를 함께 검사하는 **순수 판정 함수**. 현재 v196은 read-only preview; source proof/CHMV input 수용/actual atomic option publication은 **미연결**. 일반 `temporary_enchant` 자동 승격은 정책상 차단, 기름은 별도 유지.
5. **v221 보석 관계:** 현재 빌드 `12.1.5.70575`, Wago `Item`·`ItemSparse` 두 CSV만 일회 source 조회, source SHA·빌드·SimC generated `gem_property_id` 관계 검증. **75개 정확한 물리 item ↔ gem-property relation** 산출(사용자 선택권 75개가 아님). 소켓 제약/SimC gem 입력/CHMV J/최고 품질/시즌 적합성 추가 검증 전 UI 자동 허용 **0**. 원본 CSV는 보관/패키징하지 않았으며 작은 증거 artifact만 보존.
6. **v1.4.3 / P3-K / P3-L:** `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md`에 최신 G/J/F/O 정책 등록. `docs/P3_K_20261102_...`의 과거 “J/F/O” 표현을 G 포함 최신 정책으로 교정. **정책 문서 완성 = 예산 자동 갱신 구현 완료가 아니다.**

## 4. 실제 검증 증거 (범위와 재사용 여부 구분)

| 근거 | 실제 영수증 | 해석 / 다시 하지 않을 작업 |
|---|---|---|
| **v176 26개 물리 Native smoke** | [#40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357) `native-all-26` SUCCESS; 로그 `FINISHED_ALL_26_PHYSICAL_PASS`. 이전 Paladin 1건 재사용, 다른 25건 실측. artifact #12941461212는 2026-11-05 만료 예정 | ilvl334/35-iterations 프로필 수용 **스모크**, 26/26 적응형 DPS 전역 최적화 증거 아님. 유효 범위에서 재사용 |
| **v213 원본 키·카탈로그** | [#41360273361](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41360273361) SUCCESS, artifact [#13104842881](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41360273361/artifacts/13104842881), embedded manifest SHA `b837e24a3c593be7e9f681bc82d2a845ffddfb52dfc15b4875654f510ac98f15` | 기존 same-build 소스 재사용, 새 Native0, 후보를 사용자에게 무단 등록하지 않음. Artifact 2027-01-30 만료 예정 |
| **v220 정책 A 판정** | [v212 #41361157043](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41361157043) Windows/Ubuntu 성공 | pure policy contract; **UI 실제 신규 자동 게시 미완료** |
| **v221 GEM join** | [#41362149724](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41362149724) SUCCESS, artifact [#13106070626](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41362149724/artifacts/13106070626) SHA256 `55a7e34a36aa7ae47cd7cc00412e7db9d0c64b08b9951315abc425c9412c4326` | **75 exact source relations**, user-admitted 0, Native0. Evidence artifact 2026-11-15 만료 예정. 원본 CSV 보관하지 않음 |
| **v221 offline contract** | [#41361848175](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41361848175), Ubuntu/Windows 각각 **78 tests PASS** | 실제 Native/DPS 시험 아님 |
| **최신 정책 코드/CI** | [#41367669540](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41367669540), Ubuntu/Windows 각각 **79 tests PASS** | v220 일반 임시 마부 auto-admission 제외; 신규 Native0 |
| **로컬 API/Windows 패키지** | [v113 #41315265626](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41315265626), [v181 #41361156911](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41361156911), [v182 #41361156921](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41361156921) 각각 SUCCESS. v181 artifact [#13105011863](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41361156911/artifacts/13105011863) 2026-11-08 만료 예정 | extracted Windows CMD + loopback HTTP 검증. **실제 사용자 PC GUI/SimC Build→Start→progress/cancel/resume 인수 아님**. v181/v182 실행은 v220 코드 시점, v221 이후 새 패키지 수용을 주장하면 안 됨 |
| **Stage 중복 생성 회피** | [v113 #41268981093](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41268981093) 성공, v219 실제 HTTP 계측 | Windows 가짜 바이너리 초기 약 440ms/재사용 약 11~14ms; `Path.read_bytes` 한정 I/O 측정, 실사용 속도·메모리 절감 실증 아님 |

**보존할 실패 이력:** 초도 raw-key 보존 CI 커밋 `4815f382`의 #41360182... 계열 FAIL은 구형 v213 audit 호환/상태 필드 덮어쓰기 문제였다. `62eeed94`에서 교정, 다음 #413602733xx PASS. 초기 실패 기록을 지우거나 성공으로 고쳐 쓰지 말 것. 현 날짜의 문서 전용 HEAD `d521e400` 이후 새로운 기능 CI/Native가 없다는 것과 실제 최신 `79`건 오프라인 PASS를 구별한다.

## 5. 미완료·차단·주의할 경계

- **P0 — 핵심 시즌 예산 자동 구축 미구현:** 현 `v089` 79×2 같은 시즌 근사 B, `v108` J138/F165, `v091` oil O(치명16·가속16/무기)가 현재 시즌 고정. `v216`은 **INSTALLED_VERSIONED_ARTIFACT_ONLY, refresh_performed=false**. 즉, 새로운 시즌 G/J/F/O 전체 수집·정확 검증·B/T 자동 갱신이 원클릭 Build에 합쳐지지 않았다. 새 시즌 G가 불명확한데 READY라 표기하지 말 것.
- **P1 — 최고 품질/선택지 발행 미완료:** 음식/영약/보석의 모든 품질 동등성·정량 스탯/source↔SimC 입력을 검증하는 공통 연결 부족. v220은 preview이며 실제 validator receipts producer → UI choice → user input → profile/runtime의 **원자적 발행 경로 미완성**. 기존 영구 마부 7967 제한은 기존 실제 선택 상태일 뿐 최신 정책 A의 영구적인 사용자 수동 승인 의무가 아니다. 정적 E는 승인 회계에만 포함.
- **P1 — 특정 source joins:** v221 75 gem item-property relations는 더 이상의 의미로 승격하지 말 것. 필요한 소켓·입력·CHMV·시즌/품질 검증이 남았다. 장식(효과↔제작 item↔physical slot), 일부 영구 무기 마부(손·무기 하위 종류)도 정확 근거가 부족하다. **일반 임시 마부 117개 완전 조인은 최신 사용자 정책상 진행 대상이 아니다**; oil 관련 적용 조건만 계속 해결.
- **P1/P2 — 특수 콘텐츠:** `v108` Omnium 입력 직결. 별도 ON/OFF 모듈/정체성/GPT 갱신 안내 경로 미구현.
- **제품 인수:** Windows 사용자의 로컬 SimC 설치 상태에서 실 Build→Start→progress→cancel→resume/복원·결과 통합 미완료; CI mock/ZIP/HTTP 및 26 physical smoke는 대신할 수 없음. 26/26 adaptive Native 최적화 전수 입증은 미완료이며 **무조건 Native 반복할 이유는 없음**.
- **Project Sources:** 위에서 설명한 새 v1.4.3 실제 Project Source 파일 등록 검증 미완료. 문서 커밋과 사용자의 권한 승인을 UI 적용 완료로 혼동하지 않는다.
- **원본 v016:** 사용자 보고 제품 원본 기준. 원본 바이트/해당 범위 검증 전 “원본 v016 직접 통합” 완료 주장하지 말 것.
- **시즌 변경 시 과거 증거:** artifact 만료나 source revision 변경만으로 동일 시즌 정적 캐시 폐기하지 않음. 캐시 참조의 정체성·검증 영역을 따져 부분 무효화한다.

## 6. 다음 작업 순서 및 더 효율적인 구현안

**단기 (개발 가능 묶음 단위)**

1. **G/J/F/O 통합 계약의 작은 수직 시험**: 기존 v191/v211/v213 소스/예산/버전 계약을 바탕으로 `season_budget(G,J,F,O)→B/T` 산출·수동 T·L/E/O 이중 계상·새 시즌 미검증 fail-closed를 오프라인으로 묶어서 검증한다. 현재 하드코딩된 현재 시즌 숫자를 시즌별 검증 입력으로 이동하고, 새 시즌 요청은 기존 workflow_dispatch→원본 artifact 검증/설치 경로를 재사용한다. **새 season collector나 optimizer를 설계하지 말 것**.
2. **변경 원본의 필요한 범위만 보충**: 일반 대표 장비/무기 G 참조와 최고 품질 J/F, 기름 O의 실제 source/정적 기준이 부족한 부분에만 집중하여 동일 빌드 ID·효과·수치 관계를 확인. 이전 v221과 같은 **좁은 원본 표·열 요청 + 정확 SHA + 작은 영수증** 패턴을 재사용하고 무조건 시즌 전체 장비 DB를 늘리지 않는다. 이 1·2는 독립 오프라인 검증 준비를 **한 묶음으로 처리**하되 실제 외부 source/Native는 결손만 최소 실행.
3. **정책 A·최고 품질의 최소 수직 경로**: 증거가 실제로 충분한 **하나의 대표 선택 항목 유형**에 대해 same-build source→quality equivalence→v220 판정→v196 user catalog/validator→v098/v212 profile→SimC input까지 연결. 기존 profile generator/optimizer를 재사용. 다른 카테고리는 동일 엔진 계약을 확장해 해결하며 item-by-item 코드 작성 금지.
4. **선택형 특수 모듈/Windows acceptance**: Omnium ON/OFF 프로필·예산 완전 격리 및 세션/캐시 identity 검증, 완료 단계 GPT 수동 갱신 안내. 이미 CI에서 지원되는 Build/Start/status/cancel/resume 경로를 실제 Windows SimC에서 **한 개 대표 시나리오**로 수용 시험. 실제 필요할 때만 Native 추가.

**장기:** 시즌·확장팩 변경 시 위 엔진이 같은 계약을 이용해 검증된 G/J/F/O 예산, 대표 프로필, 최고 품질 옵션 및 선택형 모듈 상태를 최신화하고, 26 DPS의 기존 적응형 SimC로 정확한 출력/재개까지 이어지는 **완결된 사용자 흐름**.

**효율/완료 원칙:** 독립 항목은 묶어 구현·동일 기준으로 회귀 검증; 과도하게 큰 결합 작업은 논리적 패치·검증 경계로 나눔(반드시 한 번에 하나씩은 아님). 매 변경마다 *실행시간/중복 network·Native/캐시/메모리/I/O/구조 단순화*를 점검. 실제 변경으로 무효화된 최소 증거만 재실행. 구현 코드, 오프라인 PASS, 재사용한 역사 Native, 아직 미구현, 선택지의 증거 수준을 분리 보고.

## 7. 새 채팅 필수 읽기 순서 (최소 중복)

1. **이 파일 전체** (`docs/CHAT_CONTINUITY_HANDOFF_20261102_V221_P3L_ENGINE_FIRST.md`)를 읽고, 저장소 공개 여부·현재 HEAD·main HEAD·최근 Actions·아티팩트 만료를 **실제 재조회**.
2. `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` **맨 위 최신 P3-L부터 P3-E 및 변경된 최신 구간**, 과거가 뒤에 붙어 있으므로 오래된 미완료·HEAD 문구를 우선하지 말 것.
3. `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md` **전체**와 `docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md`; 그다음 충돌 없는 v1.4.2, **GitHub 교정본** `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.1_DPS_ONLY_SCOPE_CORRECTION_20261031.md`, `docs/DPS26_SCOPE_CORRECTION_20261031.md`. 오래된 Project 업로드 `20261029`의 27 DPS 표기를 사용하지 말 것.
4. `docs/P3_ENVIRONMENT_BUILDER_TARGET_ARCHITECTURE_20261031.md` **§12**, `docs/P3C_V208_START_RECEIPT_AND_WINDOWS_PACKAGE_ACCEPTANCE_20261031.md` **§7**, 그리고 필요할 때만 **역사** `docs/CHAT_CONTINUITY_HANDOFF_20261031_V216.md`.
5. 실제 연결만 확인: `runner/v089_*`, `v091_*`, `v108_*`, `v191_*`, `v211_*`, `v213_*`, `v216_*`, `v217/v218`, `v220_*`, `v221_*`, `v196_*`, `v098_*`, `v106_*`, `v113_*`. Actions는 §4 명시 실제 범위만 믿고 필요할 때만 로그를 확장 조회.
6. **복원 보고 후 사용자 “진행”을 기다린다.** 첫 응답에서 새로운 코드·커밋·Actions·Native·UI 조작을 하지 않는다.

## 8. 새 채팅 시작 프롬프트 (복사해서 사용)

> 너는 SIMC SECONDARY OPTIMIZER 프로젝트의 기존 개발을 그대로 이어받는다.
>
> **첫 행동**은 GitHub 격리 브랜치 `degong2-code/simc-secondary-optimizer-runner` / `probe/chat-cache-v035-20261024`의 `docs/CHAT_CONTINUITY_HANDOFF_20261102_V221_P3L_ENGINE_FIRST.md` 전체를 읽는 것이다. 최신 HEAD·main·repository visibility·Actions·Native/Artifacts 유효 범위를 실제로 조회하고 인계와 대조하라. 이어서 본 인계 §7 읽기 순서대로 CURRENT, 최신 승인 v1.4.3, 엔진 개발자 보충 지침, 교정된 DPS26 범위 문서, P3 §12·P3-C §7을 읽어라.
>
> **제품 목표:** 정확히 26 DPS(증강 기원사/탱커/힐러 제외), 미래 목표 ilvl 기본 334 또는 수동 최종 T에서 기존 적응형 SimC DPS 엔진으로 최적 절대 CHMV rating, DPS/SEM/95% 판정, 관측 1순위와 실질적 근접 대안을 찾는다. 일반 사용자는 전체 장비를 입력하지 않는다. 새 optimizer/collector/profile generator/effect calculation engine은 만들지 않는다.
>
> **최우선 자가검증 원칙:** 개별 기능을 더하는 개발이 아니라 **기능을 구현하고 반복 검증·업데이트하는 범용 엔진**을 개발하는가? 작업 전후 이 질문에 답하라. 독립 작업은 효율적으로 묶되, 작업이 지나치게 크면 검증 가능한 작은 패치로 나누어라. 과거 동일 acceptance의 통과 영수증을 재사용하고 실제 변경에 필요한 최소 회귀/Native만 실행하라.
>
> **최신 정책:** 시즌별 G/J/F/O **전체**를 동일 시즌 원본에서 자동 구축하고 `B=G+J+F`, `T=B+O`로 통합 갱신. 수동 최종 T 우선, L/E/O 중복 방지. 유효 동일 시즌 79×2 참조/J138/F165/oil16+16은 새 시즌에 검증 없이 복사하지 않음. 동등효과·범위의 최고 품질만 UI, 일반 임시 마부 제외·무기 기름 유지, 정책 A 검증 완료 자동 등록, Omnium 등 독립 ON/OFF 모듈+GPT 수동 업데이트 안내, SimC가 효과/proc/APL/DPS 계산, 통계는 95%만 사용.
>
> **상태 오인 금지:** 현 v216은 설치된 v213 artifact 기반 Build이지 새 시즌 자동 refresh가 아님. v220은 판정/읽기 전용 preview이지 선택지 자동 게시 완료가 아님. v221의 75건은 물리 아이템-보석속성 관계이지 75개 보석 사용 승인이나 J 검증이 아님. 26개 Native 물리 smoke는 26/26 적응형 E2E가 아님. 패키지 CI는 사용자 Windows PC 수용시험이 아님. Project Instructions 등록과 Project Sources 파일 업로드는 별도다.
>
> **다음 개발 후보:** (1) 새 시즌 G/J/F/O 동시 구축·B/T 계산 계약과 부족 자료 fail-closed, 기존 요청 기반 refresh 접합, (2) 원본·효과·품질의 정확한 관계를 최소 보충한 정책 A 선택지 자동 발행 수직 경로, (3) 선택형 특수 시스템과 Windows 실제 Build/Start/progress/cancel/resume 인수. 기존 v191→v211→v213·v089/v091/v108·v098/v093/v094/v095·v212/v216/v217/v218 및 캐시를 재사용하라. 모든 변경마다 Native/중복 수집/캐시/메모리/I/O/실행시간/구조 단순화를 점검하라.
>
> `main`, v003 immutable, 원본 v016, repository visibility, 실제 Project Sources/Instructions UI, 공식 Work OS M0/Shared State/MAIN 권한은 별도 사용자 승인 없이 변경하지 않는다.
>
> **첫 응답에는** 복원한 최신 상태, 완료/미완료, 실제 영수증의 적용 범위, 막힌 점, 단·장기 로드맵과 가장 효율적인 다음 묶음 작업을 **자연어로 보고한다. 이후 어떤 구현·추가 실행도 하지 말고 사용자의 “진행”을 반드시 기다려라.**

---

**인계 파일 자체는 구현/검증 영수증이 아니다. 매 새 채팅에서 라이브 HEAD/CI를 재조회한다.**
