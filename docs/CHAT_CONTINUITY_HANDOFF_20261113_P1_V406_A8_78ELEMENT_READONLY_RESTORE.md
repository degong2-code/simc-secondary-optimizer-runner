# SIMC SECONDARY OPTIMIZER — v406 단일 개발 인계 (2026-11-13)

> **목적:** 길이 제한으로 분기한 채팅에서 78개 요소의 범용/현재 원본/실 제품 통합을 보존해 **A8부터** 개발을 계속하기 위한 독립 인계. **이 문서 자체는 코딩·Native·Actions 신규 PASS나 공식 승격의 증거가 아니다.** 역사적 인계와 대화에서 나온 상태를 최신으로 취급하지 말고, 아래 실제 브랜치·JSON·Actions로 다시 확인한다.
>
> **새 채팅 첫 응답 = 읽기 전용 복원 결과만 보고하고 STOP.** 별도 사용자 `진행` 이전에 GitHub 파일/코드 수정, 테스트·Actions·API·Native 실행, 커밋, 병합, 공식 승격 금지. 이 인계문을 만든 **기존 채팅**은 사용자 요청에 따라 문서 갱신과 인계만 수행했다.

## 1. 실제 GitHub 인계 기준 · 우선권

- 저장소: `degong2-code/simc-secondary-optimizer-runner`.
- 제품 연구/일반 구현 소유 격리 개발 브랜치: `probe/chat-cache-v035-20261024`.
- 인계 작성 직전 실제 개발 브랜치 HEAD: `f61d6c00d6bd9e9404a4822a50ce548d545656d8`. 기준 `main` HEAD: `07133e0aaf738d6e4816a6486057b1cd49c018de`. **이 인계 및 문서 포인터의 자체 커밋은 이후 HEAD를 바꾸므로 새 채팅은 반드시 GitHub에서 다시 HEAD를 읽는다.** 위 SHA는 고정된 개발 관측 스냅샷이지 새 채팅의 확정 최신 HEAD가 아니다.
- 최신 사용자 직접 결정 > [승인 v1.4.3 시즌 G/J/F/O 전자동](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) + 충돌 없는 v1.4/1.4.1/1.4.2 > [78개 기계 판독 완료 계약](development/78_ELEMENT_COMPLETION_CONTRACTS.json)과 실제 격리 코드·Actions/Native·원본 SHA > 역사 인계. **설계·승인과 실제 개발/원본 제품 승격을 혼동하지 않는다.**
- [개발 진입](development/START_HERE.md) → [기능 인덱스](development/INDEX.md) → [코드 지도](development/FILE_MAP.md) → **[상태 정본 JSON](development/78_ELEMENT_COMPLETION_CONTRACTS.json)** → [자동 생성 상태표](development/78_ELEMENT_STATUS_GENERATED.md) → [78개 상세 추적표](development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md) → [v401 완료 정책](development/POLICY_78_ELEMENT_COMPLETION_GATE_V401.md) / [개발 프로토콜](development/PROTOCOL.md) / [승인 결정](development/DECISIONS.md) → [증거 지도](development/EVIDENCE_INDEX.md). 필요한 A8 근거만 추적하고 전체 300개 안팎 과거 노트/Native를 전수 재감사하지 않는다.
- 이전 [v386 기반 누적 인계](CHAT_CONTINUITY_HANDOFF_20261113_P1_V386_ZERO_SOURCE_GENERALIZATION.md)는 2026-11-13 시점의 역사별 변경 안내를 포함한다. 하단의 v403/v404/A1 PENDING 등 **작성 당시 표기**는 본 인계와 최신 계약보다 우선하지 않는다.

## 2. 변하지 않는 제품 목표와 P1 우선순위

**지원:** WoW **26개 DPS 전문화(증강 기원사·탱커·힐러 제외)**. 미래 목표 장비의 ilvl 기본 334 또는 사용자 입력 최종 CHMV `T`에서 **SimC DPS 최대화**로 치명·가속·특화·유연의 절대 rating을 최적화. 예상 DPS, SEM/오차, **95%만** 사용한 통계 판정, **관측상 1순위**와 전역 최적 확정의 차이, 실질적으로 다른 근접 분배 대안, 최종 비율을 제공한다.

- 일반 사용자는 **전체 일반 장비를 고르지 않는다**. 직업/전문화/종족/특성, 목표 ilvl 또는 수동 최종 T, 장신구 2, 선택 특수효과 장비, 장식 최대 2, 보석·영약·음식·물약·무기 기름·전투조건을 지정한다. 업로드 SimC 프로필은 선택한 캐릭터/특성 추출용이지 현재 착용 장비 및 총량을 목표로 복사하지 않는다. 대표 일반 장비/5 티어 부위 중 충돌 없는 4세트/무기/주능력치/실행 SimC 프로필은 내부에서 준비한다.
- **예산:** `G` 대표 일반 장비·무기, `J` 기본 보석, `F` 최고 품질 영약, `O` 적용 기름의 고정 vector. `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. 새 시즌엔 G까지 포함 전부 원본 기반 갱신. **사용자 수동 최종 T 우선**. 선택 장비 정적 고정 `L`은 G 내, E/O도 기존 승인 회계에 따라 **중복 가산 금지**. 장신구 정적 gear 레코드 미관측은 수치 0 증명 또는 선택 차단이 아니다.
- **SimC 소유:** 정확 아이템 효과/발동/proc/APL/DPS. 우리 코드는 현재 시즌 소스→환경/상세 ID·옵션→정적 rating/Native JSON2 확인→기존 적응형 탐색·95%·캐시·취소/재개·Windows UI/출력을 연결한다. 새 APL/아이템 발동 엔진, 별도 효과 인증 Gate, 전체 시즌 장비 DB, 파밍/획득 경로·장비 조합 추천으로 확대하지 않는다.
- 최우선 P1은 **시즌 G/J/F/O 자동 환경 구축 → B/T·정확 대표 프로필/선택 장비 → 기존 SimC 적응형 실행 → Windows 사용자 결과**를 하나로 완성하는 것. 새 알고리즘/모델·SEM 과잉 정밀화·미선택 전수 수집/새 정책 Gate보다 기존 함수 재사용과 끊긴 연결 최소 수정을 우선한다.

## 3. 78개 요소 완료 계약 — 최신 실제 판정

정본 [`78_ELEMENT_COMPLETION_CONTRACTS.json`](development/78_ELEMENT_COMPLETION_CONTRACTS.json)의 정확히 **A1~A11, B1~B12, C1~C14, D1~D9, E1~E9, F1~F7, G1~G10, H1~H6 = 78개**를 유지. 단일 번호당 Native 인증 1회가 아니다.

| 축 | 인계 기준 실제 PASS | 유의사항 |
|---|---:|---|
| `generic` | **7/78 (A1~A7)** | 범용 발견·수집·현재 출처 선정 기능의 범위 한정; 미래 미출시 시즌 실측 필요 없음 |
| `current_source` | **7/78 (A1~A7)** | 현재 KR 70783 해당 원본 SHA·소비 관계, 전체 gear/예산 또는 DPS 증명 아님 |
| `historical` | **3/78 (A10,A11,G2)** | 당시 특정 조건의 Native/설치 영수증; 현재/범용 PASS 대체 금지 |
| `product_integration` | **0/78** | 완료 축을 보류하고 이후 실제 USER-E2E 경로에서 확인 |
| **요소 완전 COMPLETE** | **0/78** | generic·current_source·product_integration 필요한 축 모두 충족 전 완료 주장 금지 |
| 최종 실제 사용자 ZERO-SOURCE→USER-E2E | **PENDING** | 현재 시즌 빈 루트→자동 환경→SimC DPS/SEM/95%→캐시/재개 전주기 아직 불합격/미수행 구별 |

- `policy.next_review = "A8"`. A7은 `generic=PASS,current_source=PASS,product_integration=PENDING`. **A7 제품 통합 미완료라는 이유로 A8/A9의 독립 개발을 무조건 중단하지 않되, 제품 완료 판정에서 놓치지 않는다.**
- [v401 기계 검사기](../integration_probes/v401_completion_contract_gate.py), [부정 테스트](../tests/test_v401_completion_contract_gate.py), [정책 Actions](../.github/workflows/p1_v401_completion_contract_policy_gate.yml)의 JSON ↔ 생성표 ↔ 78개 상세 표 1:1 대조를 통과해야 상태 변경 가능. 다른 ID 영수증 복사/현재 source만으로 generic PASS/N/A 무증거 선언/제품 E2E 성급한 PASS를 금지. **Actions 정책 PASS는 진짜 Native/실 원본 E2E를 대신하지 않는다.**
- 제품 기능 존재 여부/지난 제품 E2E는 위 **신규 78축의 0/78을 이유로 미구현이라고 오판하면 안 된다**. v290/v291/v293 적응형 실행, v341 Windows Native, v343/344 설치 등 기존 실험을 [증거 지도](development/EVIDENCE_INDEX.md)로 재사용하고 유효 범위를 따로 기록한다.

## 4. 가장 최근 완료 A7 — v405 실증 범위 정확히 유지

**원본/사용자 선택 통합:** [v405 정확 범위 노트](development/notes/2026-11-13_p1-v405-a7-automated-current-source-selection-verified.md), `runner/v405_a7_selected_source_contract.py::assess`를 `runner/v216_environment_build_coordinator.py`의 **정상** Build 흐름에 접속. 기존 `v163→v165→v166→v167`의 상품 후보(내부 일반 장비 포함)를 동일 빌드·시즌·정확 itemID 및 raid/M+/craft 출처로 원본 대조한 후 `v217`에서 봉인·SHA/0추가HTTP 재사용. 생성된 공용 선택지가 실제 원본 ID·정확 source의 부분집합인지 엔진이 판정하며, GPT/사용자/시드 season-ID·item-ID 수동 분류 0.

**현재 실 원본:** [GitHub Actions #43375839959](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43375839959) 실제 job `a7-real-source` **SUCCESS**, tested HEAD `349986e8c816523240816abe51b8497c6882921a`, KR Retail `12.1.5.70783`, 현재 실제 WCL Raid53/M+55, DB2 Expansion11/DisplaySeason37, 활성 레이드10보스/쐐기8던전. 10개 Wago DB2 CSV **62,280,767 bytes를 이 A7 실물 시험에서 1회 실제 수집**; 외부 API/SimC 비밀키 및 원본 아이템을 영수증에 무분별하게 공개하지 않음. **원본 434개 → 자동 출처 대조 209개 → 사용자 공개 후보 134개(장신구18/특수효과 장비10/제작장비106)**; 완성 아이템/효과·최종 등록 승인 또는 USER SimC 실측이 아니다. [원본 압축 artifact #14014072785](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43375839959/artifacts/14014072785) SHA와 상세 단계 SHA는 v405 노트. `same_source_reused_without_extra_http=true`; **A7 신규 Native 0회**, G/J/F/O 실제 이번 테스트 완료/사용자 프로필 생성/최종 DPS는 0.
- [합성+기존 회귀 Actions #43375459029](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43375459029) job SUCCESS, tested `2a2fbc06444a47b160d9ff4f9a43f08b7619248c`, **144 시도/141 PASS/3 선택 원본 마운트 SKIP/0 FAIL**. 가상 다른 빌드/시즌/raid/IDs·원본 위조·cache 봉인 정합만 해당, 실제 사용자 Native E2E 아님.
- [완료 계약 정책 CI #43377017734](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43377017734), 실제 job SUCCESS, **16 PASS/0 FAIL**, 인계 전 `V401_COMPLETION_CONTRACT_VALID items 78 ... next A8 ... full_E2E PENDING` 로그를 재조회했다. 이 인계 문서만 새로 기록하면 새로운 제품 source/Native PASS가 늘지 않는다.

**중요한 폐기 결정 — v403의 WSE 차단 철회:** [v404 사용자 승인·원인](development/notes/2026-11-13_p1-v404-a7-wse-diagnostic-only-source-first-membership.md). WSE `WorldStateExpressionID` 양수/0/None/불형식은 **보조 진단 메타데이터**이지 아이템 현재 시즌 소속/사용자 후보/내부 표준 장비의 필수 인증 또는 차단 조건이 아니다. 실제 active raid/M+ 관계 + same-build DB2 Item/Journal/DisplaySeason/원본 ID로 판정. WSE 읽기 어려움·미선택 아이템 WSE 확인을 앱 실행 지연 Gate로 복원 금지. 다른 시즌/미맵핑 소스·잘못된 ID는 계속 fail-closed. 런타임 AI·GPT 수동 아이템 판정은 금지.

## 5. 다음 작업 — A8의 시작점과 인계 후 `진행` 절차

**A8 실제 계약:** `SimC revision`, BASE; **“정확한 revision·소스/실행 바이너리 빌드 관계”**; `generic=PENDING/current_source=PENDING/product_integration=PENDING` (원장 기준). 기존 코드가 있으므로 **미구현이라고 단정하지 말 것.**

- 첫 `진행` 시 [A8 원장 행](development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md)의 수락 조건과 기존 코드 **`runner/v229_simc_only_source_seed.py`(정확 git 40hex revision, Git Tree/blob identity), `runner/v275_pinned_simc_compiler_inputs.py`(기존 v229 sealed source/manifest·게임 빌드), `runner/v241_fresh_source_stage_adapter.py`(expected SimC revision/게임 빌드/각 파일 SHA), `runner/v217_stage_execution_engine.py`, `runner/v216_environment_build_coordinator.py`**, 실제 설치 Windows SimC 바이너리 identity·JSON2를 [FILE_MAP](development/FILE_MAP.md)·[증거 지도](development/EVIDENCE_INDEX.md)에서 추적한다.
- **REUSE → CONNECT → EXTEND → REPLACE → NEW → STOP**: 이미 구현/검증된 source revision과 정확 실행 바이너리 SHA·게임 빌드 관계, 실행 가능한 환경에서의 캐시 무효화·불일치 차단, 현재 제품 소비자가 실제로 검증값을 읽는지 확인. 먼저 기존 테스트/Native receipt/버전과 코드 경계를 좁혀 정리해 각 축 판정. 불충분한 축만 최소 변형 회귀/실 바이너리 확인. **새 SimC revision downloader나 전 전문화 Native 반복을 기본 과제로 만들지 않는다.**
- A8 이후 **A9 SimC 원본 파일** (`runner/v275` 외 필요한 DBC·생성 데이터·효과/마부 입력), 이후 A10/A11 기존 v383 Native 역사 증거와 연결. 독립적으로 검증 가능한 요소는 순차 진행, 의존성이 필요한 product_integration은 PENDING 유지하되 이후 기능 통합 때 누락 없이 재평가.
- 차후 G/J/F/O(새 시즌마다 **G 포함**), 5티어 중 4pc 유동·대표 무기/주능력치, 최고 품질 선택지·Policy A 자동 등록, 사용자 manual T·L/E/O 정확 수치, v212 설치와 v098 프로필 → **기존 v290/v291/v293 최적화**→ Windows 웹 결과, 캐시·취소/재개·최종 95%·대안까지 연결. 기능별 출처/수치가 빠진 항목만 보류하고 검증된 기본 환경을 불필요하게 차단하지 않는다.

## 6. 엄격한 최종 ZERO-SOURCE USER-E2E는 별도 검증

모든 78개를 서류상 PASS로 만들기보다, 사용자 친화적 **한 번의 실제 제품 흐름**이 완성돼야 한다. 현재 출시된 실제 시즌에서 깨끗한 root(이전 완성 DB·seasonID·itemID·예산·설치/프로필·DPS 캐시·GPT 수동판단 주입 없음)와 정상 인증된 Blizzard/WCL/Wago/SimC 원본·실 실행바이너리로 **현 빌드/확장팩/활성 콘텐츠 자동 탐색 → 대표 일반 장비·5티어4pc→G/J/F/O/B/T 자동 예산 → 선택 USER 변형·정확 SimC 프로필→ Native JSON2 rating→기존 적응형 DPS/SEM/관측1순위/95%/근접 대안→저장·취소/재개·캐시/Windows 출력**까지 검증한다.
- 최초 신규 시즌이나 새 모델의 실제 미래 소스 원본을 현재 미리 실측할 수 없음은 **범용 코드 불합격 사유가 아님**. 현재 ZERO-SOURCE 실증+다른 시즌/빌드/ID 합성 회귀의 기능 범위만 PASS하고, 실제 사용자/SimC 통합은 별도.
- 최종 E2E 이전에도 가능한 짧은 수직 user-path 검증을 점진적으로 진행하되, 동시즌 정적 item cache를 SimC revision만으로 삭제하거나 실/native 반복, 네트워크 중복 수집, 전 26전문화 E2E 무조건 반복하지 않는다.
- 오류 발생 시 **원본 단계→정확 source/셋팅 SHA→연결된 78 ID→첫 불일치/실패 코드→기존 증거** 순으로 추적. `PENDING`, 실제 `FAIL`, 차단된 외부 입력, 역사 PASS를 분리한다. 기존 제품 최신 원본 `v016_SCENARIO_CONTRACT`은 사용자 보고 기준이며 격리 GitHub에서 원본 바이트 직접 통합 완료로 표시하지 않는다.

## 7. 문서·작업 효율 및 권한

- 변경 시 실제 무효화 범위만 테스트하고, 진척의 **구현/코드 합성 PASS/실 현재 시즌 원본 PASS/Native 실측/제품 USER-E2E/역사 재사용/미관측/미구현**을 분리 기록. CPU/메모리/I/O/다운로드·CI 시간·Native 호출 수 검토. 인계 자체로 DB2 62MB/Native/API를 반복하지 않는다.
- 정보 정본: **현 상태는 JSON**, 고정 승인 설계는 v1.4.3, 소스별 영수증은 기존 v394–v405 노트/Actions, 상세 지도는 INDEX·FILE_MAP·EVIDENCE_INDEX. 중복 문서/새 gate 프레임워크를 만들지 않는다. 과거 v403 차단/과거 A6 PENDING·3 generic/옛 v365 WSE 정책을 최신으로 복원하지 않는다.
- 격리 개발은 허용되나 **`main` 병합, v003 immutable 수정, Project Instructions/Sources UI 실제 적용, 공식 Work OS M0/Shared State/승격, WEQUIP authority, 다른 주 제품 개발 채팅의 소유권 변경**은 별도 사용자 권한. GitHub에 정책을 기록한 사실만으로 Project UI 반영을 주장하지 않는다.

## 8. 새 채팅 독립 시작 프롬프트 원칙

1. 새 채팅에서 본 인계와 최신 GitHub HEAD/JSON·Actions를 독립적으로 다시 읽는다.
2. **첫 응답은 읽기 전용 상태 복원 보고만**: 실제 HEAD, 78축 7/7/3/0 기준 최신 확인, A7 v405 실제 원본/합성·비제품 통합 범위, WSE 비차단, A8 기존 코드/증거 재사용, 병목·단기/장기 로드맵·남은 통합. 읽기 전용 중 외부 원본/Native API 직접 수집이나 테스트/Actions 실행은 하지 않는다.
3. **첫 응답 후 STOP.** 사용자가 별도 `진행`을 명시해야만 A8 개발 검토·검증 및 격리 브랜치 수정·커밋을 시작한다. 기존 history가 아닌 실제 코드/검증으로 A8 PASS 여부를 판단한다.

**END — v406 single handoff; not product promotion.**
