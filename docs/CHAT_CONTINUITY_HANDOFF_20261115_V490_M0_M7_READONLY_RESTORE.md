# SIMC SECONDARY OPTIMIZER — v490 / M0~M7 제품 우선 독립 인계 정본

> **2026-11-15 개발 시점 스냅샷 / 인계 준비 문서.** GitHub 격리 브랜치 probe/chat-cache-v035-20261024에서 확인한 **작성 직전 HEAD 85a54eefe8f33dea2a23f4b546f54883f5570e69** 기준. 본 인계 커밋 직후 SHA는 달라진다. 새 채팅은 **이 SHA·버전·PASS·다음 작업을 현재 상태로 고정하지 말고** 최신 실제 브랜치 HEAD, CURRENT, Actions, 78 JSON, 관련 코드와 영수증을 다시 읽어야 한다. 별도 사용자 '진행' 전 **첫 응답은 읽기 전용 독립 복원 후 STOP**. 이 문서 작성 자체는 제품 기능 변경, 정식 COMPLETE/Project Sources 적용, main 병합, Native 실행이 아니다.

## 1. 제품 정체성·최신 사용자 승인 방향

- **지원 대상:** 증강 기원사·탱커·힐러를 제외한 정확히 26개 DPS 전문화. 목표 ilvl 기본 334 또는 사용자 지정 **기름 포함 최종 CHMV T**에서 치명·가속·특화·유연의 **최적 관측 절대 rating**을 기존 적응형 SimC DPS로 찾는다. DPS/SEM/95% 판정/관측 1순위/실질적으로 다른 근접 대안/스탯 비율을 함께 제공한다. 전역 최적성 증명으로 과장 금지.
- **일반 사용자 흐름:** 직업·전문화·종족·특성 → 목표 ilvl/수동 T → 장신구 2개, 선택 특수/제작장비·장식 최대2, 보석·영약·기름·기타 검증된 소모품·전투조건 → 프로그램이 같은 시즌 대표 일반 장비·무기·주능력치·티어4pc와 G/J/F/O·프로필 자동 구성 → 기존 적응형 SimC·캐시·취소·재개 → 결과. 사용자의 기존 착용 장비 전체를 요구하거나 그 총량을 기본 분배 예산으로 삼지 않는다.
- **공식 예산:** G 대표 일반 장비·무기, J 검증된 기본 보석, F 검증된 영약, O 선택 기름 고정치. B=G+J+F, T=B+O, c_final=c_base+o. 수동 최종 T 우선(B=T-O). 특수장비 고정 L은 G 안에 있고 하한 보호만, E는 승인 회계대로 한 번, O는 gear_* 한 번, 장신구 고정 정적 스탯은 자유 G 밖. 제작장비 초기 50:50을 L로 잠그지 않는다.
- **동일 시즌 재사용/신시즌 갱신:** 같은 시즌 봉인 정적 아이템 캐시는 SimC revision만으로 자동 폐기하지 않는다. 다른 시즌은 기존 79×2·J/F/O 값을 검증 없이 복사하지 않고 G/J/F/O와 대표 장비·무기·티어를 해당 시즌 근거로 다시 구축한다. DPS 캐시는 실제 바이너리·실행 프로필·장비·전투조건·후보·iterations identity로 분리한다.
- **SimC 책임:** 장비/소모품/proc/APL/DPS 효과는 SimC가 담당한다. 우리 책임은 정확한 ID·ilvl·적용범위·G/J/F/O/L/E·정적 rating/JSON2·실행과 95% 통계·결과/캐시/복구다. 전체 아이템DB/장비 추천/수집 경로/독립 효과 재구현/매 전문화 Native 전수는 범위 밖.
- **자동 등록 정책 A:** 정확한 물리 ID·시즌 빌드·동일 효과와 최고 품질·적용 조건·SimC 입력·CHMV 예산 소유권이 실제 선택 범위에 증명된 옵션만 자동 등록한다. 미검증 선택지는 개별 보류, BASE 정상 실행 차단 금지. 영구 마부 지원, 일반 임시 마부 제외, 무기 기름은 별도 유지. 시즌 특수효과는 선택형 독립 모듈이며 GPT 상시 의존성 없음.

## 2. 제품 완성 로드맵과 현재 위치

**사용자가 2026-11-15 승인한 [M0~M7 로드맵](development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md)이 개발 관리 기준이다.** 78개 요소는 완료/증거 계약이지 번호 순 신규 개발 로드맵이 아니다.

| 단계 | 사용자 기능/수락 | 현재 근거 범위(이 인계 당시) |
|---|---|---|
| M0 기존 코드·원본·Native 증거 재사용 | 유효한 역사 증거 확인 뒤 REUSE/STOP | 기준 확보. 과거 전면 재감사 금지 |
| M1 단일 시즌 Environment Build | 정확한 시즌 대표 장비/무기/4pc 및 G/J/F/O 원본 자동 구축 | v216/v217/v212 구축·일부 70783 Native 성공. 엄격 전체 제로소스 미수락 |
| M2 G/J/F/O·B/T·L/E/O·대표 프로필 | 사용자 자동/수동 T·정적 rating·설치 SHA와 일치 | v222/v432/v098 등 구현·일부 실 Native 성공. 시즌·변형 일반화 미완료 |
| **M3 기본 USER→SimC→결과** | 일반 사용자 선택·장신구2·프로필·캐시/재개·95% 결과 통합 | **당면 실제 소비 경계**. v486~v490의 프로필 복구·F/J 설치 SHA/선택 연결 보완. 전체 제품 수락 아님 |
| M4 검증된 선택 기능 자동 등록 | 고품질 소모품·E·장신구/제작/장식·특수모듈 정확 입력/예산/캐시 | 일부 구현, 음식/물약 v484 source-only 미등록. 증거 없으면 선택지만 PENDING |
| M5 26 DPS 범용성/탐색 품질 | 하나의 공통 프로필/적응형 SimC 엔진, 무기·4pc 예외 처리 | 기존 다전문화 Native/탐색/95% 실증 재사용. 전수 Native 새 실행 금지 |
| M6 UI/Windows 배포·저장/복구 | 초보 사용자 입력·환경 갱신·선택·취소/재개·결과 | 웹/API/Windows 일부 시험 있음. v489 안내·v490 실제 JS 핸들러 회귀 PASS(오프라인) |
| M7 단일 엔진 ZERO-SOURCE→USER-E2E | 기존 정답/과거 수집 DB를 주입하지 않고 정상 신규 원본 취득 후 실제 사용자 결과·78 유효 수락 | **PENDING** |

**공식 78 JSON** [여기](development/78_ELEMENT_COMPLETION_CONTRACTS.json): 이 스냅샷 당시 generic=27 PASS/current_source=27 PASS/product_integration=15 PASS/historical=13 PASS, 공식 **15/78 COMPLETE**, policy.next_review=B10, 전체 full_product_e2e=PENDING. **15/78=실제 코드 구현률 19%가 아니다.** 실제 GitHub 78 JSON에서 재확인하고 역사 값으로 취급할 것.

## 3. 직전 실제 코드 수정 및 검증 (v486~v490)

| 버전 | 실제 사용자 접점·변경 | 현재 검증/한계 |
|---|---|---|
| v486 | '시즌 환경 구축' 후 설치 예산 READY이나 v113 실행 프로필 스냅샷이 사라진 경우, 명시적 자동 기본 구축만 기존 v216 Build로 다시 진입. 조회-only 캐시는 그대로 | [코드 9f27588c](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/9f27588cfd2bf782843d2723a03a22b1c610da42), v113 오프라인 PASS. 신규 Native 아님 |
| v487 | 위 복구를 실제 v217 봉인·재시작 후 v113 스냅샷 복원·중복 Build 없음까지 회귀 | [테스트 32ef445a](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/32ef445a56afa76df35034b614c3d9b6ef2c8ded), v216 실 원본/Native 구축은 모의 대체 |
| v488 | 같은 빌드/ilvl/O=0인데 여러 F/J v212 설치본이 있을 때 일반 환경 Build가 최신 파일을 임의 선택하던 문제 차단. 정확 SHA 지정은 유지 | [코드 070bbd5c](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/070bbd5c1b1b6b219fe6ae0f32e14a7ce4aeb08e), 오프라인 PASS |
| v489 | 다중 F/J 설치 차단 시 UI 오류코드만 보여주던 문제: 기존 '기타 직접 입력·고급 옵션 → 영약 변경 → 선택 환경 검증·준비' 위치 안내 | [UI 554f470b](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/554f470bcdae55b0203f4c5031dbb471ce18e3ee), UI/API 오프라인 PASS |
| **v490** | 기존 검증된 영약을 고르면 **같은 F ItemID의 기본 4보석/O=0 설치본 SHA가 정확히 한 개일 때만** 해당 v212 설치로 장신구 원본/세션 선택을 다시 결합. 임의 G/F 재측정 없이 기존 exact SHA 조회 | [기능 05e9946e](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/05e9946eca354cb402585598d0e8a46ab7f193d4) · [실제 JS handler 오프라인 회귀 0b5c5111](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/0b5c5111bbe83f42e699380506f36c417780ba1b). 아래 검사 범위 참조 |

**v490 현재 소비 체인:** 사용자 '영약 변경' → 기존 GET verified-oil-loadouts의 추가 verified_base_flask_installs(정확 설치 SHA/F/J, O=0/일반4소켓에만) → UI에서 유일한 조건일 때 exact GET season-gear로 장신구·선택장비 데이터 갱신 → 기존 옵션 카탈로그 소비 → 일반 buildRequest/v113.plan 서버의 정확한 SHA·F/J/O·보석·캐시 identity 재검증 → 기존 SimC 실행. 같은 F인데 여러 J 설치본이 있거나 O/소켓/빌드가 다르면 예전 설치 SHA로 임의 승인하지 않고 차단. **새 장비/선택지/효과 엔진 없음.**

**v490 증거:** [v113 API #43687903975](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43687903975) Windows/Ubuntu 각 **398 tests SUCCESS**, [v182 UI #43687903977](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43687903977), [공통 #43687904018](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43687904018), [Windows ZIP/HTTP #43687903993](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43687903993), [78 JSON 일관성 #43687903976](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43687903976) **SUCCESS**, HEAD 문서 커밋 [#43688137759](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43688137759) 계약 검사 SUCCESS. 위 ACTIONS는 **오프라인·통제된 테스트 환경 성공**, 새 실제 시즌 클릭→SimC USER-E2E PASS로 해석 금지. 이번 기능 변경의 신규 Native/DB2/외부 수집 **0**. 기존 v343 70783/334/G2850/J92/F165/O0 및 v417/v439/v440 같은 시즌 실제 Native·JSON2·95% 증거는 해당 정확 범위에서만 REUSE. 역사 영수증의 실측 조건은 [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md)와 [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md)를 먼저 확인.

**아직 미완료:** 같은 물리 F에 서로 다른 검증 J 설치본 여러 개를 고급 UI에서 정확히 선택하는 경로는 구현하지 않음(현재 fail-closed). O>0·특수보석/소켓 변경·실 신규 시즌/26전문화 전체 조합에 대한 v490 양성 실증 없음. 이는 선택 옵션 보류이며 필수 BASE 실패를 입증하는 자료가 아니다. v484의 음식/물약 물리 ID↔SimC generated DBC 조회는 **source-only**이고 등록 증거(정확한 토큰·효과 동일·최고 품질·조건·CHMV) 미비: v220/212/UI 자동 등록 아님. 미선택 항목이 BASE를 차단하지 않도록 유지.

## 4. 실제 코드·기록 지도 (필요한 부분만 조회)

- **원본·환경·예산:** runner/v216_environment_build_coordinator.py, v217_stage_execution_engine.py, v212_environment_manifest.py, v222_season_budget_contract.py, v432_selected_4pc_budget_bridge.py.
- **사용자 API·화면:** runner/v113_local_web_api.py (build_season_environment/verified-oil-loadouts/plan/season-gear), runner/webui/app.js 및 index.html; 최근 테스트 tests/test_v113_local_web_api_offline.py / test_v114_local_web_ui_offline.py.
- **사용자 옵션·프로필·실행:** runner/v220_catalog_auto_admission.py, v218_v098_profile_stage_adapter.py, v098_target_user_scenario_bootstrap.py, v096_unified_product_entry.py, 기존 v094/v290/v291/v292/v293/v106. 선택 ID/고정 L/E/O·실제 SimC 실행과 캐시는 각 단계 원 소유자가 검증.
- **원본 선택형 후보:** v190/v280/v281/v484 (물리 원본/SimC DBC 후보 ≠ 자동 제품 등록).
- **증거/결정/지도:** [FILE_MAP](development/FILE_MAP.md), [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md), [DECISIONS](development/DECISIONS.md), [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md), [78 JSON](development/78_ELEMENT_COMPLETION_CONTRACTS.json). README 및 역사 노트의 'latest'는 해당 시점 역사 자료.

## 5. 사용자 최신 직접 결정 — 모든 엔진 변경 전 실제 소비 위치 설명

**2026-11-15 승인, [상시 정책](development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md) 첫 줄에 GitHub 반영 완료.** 엔진 신설/수정/복구/새 검증을 **시작하기 전에** 항상 사용자에게 짧게:
1. 실제 이용 단계(어느 버튼/입력과 다음 단계 사이, 직접 접하지 않으면 내부 소비 위치).
2. 누가 어떤 입력에서 무엇을 못 하고, 수정하면 무엇이 좋아지는지.
3. 기존 코드·원본·캐시·Native로 해결 가능한지.
4. 정책상 불필요하거나 과도한 부분, STOP/보류 이유.
5. Native·HTTP/DB2·CPU/메모리/I/O·캐시·유지비와 최소 수정·검증 범위.
**개발 소통 규칙**이지 추가 사용자 승인 요구, 제품 런타임 Gate, 새 78 요소가 아니다. 관련 결함이 없으면 STOP/REUSE 판단을 그대로 보고. 하나의 F/전문화 ID 하드코딩을 범용 지원이라 하지 말 것.

## 6. 다음 작업의 우선순위 — 상태 의존, 강제 과제 금지

**첫 목표 후보 (새 채팅 READ-ONLY 판정 후 사용자 '진행' 필요):**
- M3 사용자 실제 **선택한 영약·장신구2→동일 정확 v212 SHA·J/F/O·4소켓→v113.plan→적응형 SimC/결과/재개** 경로를 v490 변경의 생산자→소비자 관점에서 검토. 이미 398 API/실제 JS handler 오프라인과 기존 동등 Native가 검증한 부분은 **REUSE/STOP**, 실제 불일치나 필요한 추가 사용자 선택 하나만 최소 CONNECT/FIX. 신규 Native/웹 수집을 '인계 뒤 재검증' 용도로 하지 않는다.
- 사용자 BASE를 차단하는 문제가 없다면 **M1~M2 동일 시즌·새 시즌 단일 Environment Build의 필수 G/J/F/O, 수동 T, 정확한 설치본·예산 회계**에 미완성 소비 경계가 있는지 확인. 기존 현재 시즌 실측과 분리된 신규 시즌 값을 추정하지 않는다.
- **M4는 증거 있는 선택 옵션만** 기존 정책 A→v212→v218/v098에 연결. F가 여러 J 설치본에 걸치는 경우 별도 조합 선택 UX는 실제 사용자 가치·적용 검증·캐시 호환을 확인한 뒤 최소 EXTEND, 그 전까지 PENDING/STOP. 음식/물약·증강룬·영구 E·특수장비는 새 자료 수집을 앞세우지 말고 미사용이면 해당 항목만 보류.
- M5/M6의 실제 대표 경계·배포/복구 결함은 병행 수리. M7 엄격 ZERO-SOURCE→USER-E2E 최종 수락은 마지막; 모든 PASS/버전 숫자를 진척으로 오해 금지.

**항상 판단 순서:** STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW. 임의 78 next_review/B10 업무화·역사 351 노트 전수 감사·미선택 효과 SpellEffect 연쇄·새 알고리즘·모든 전문화 Native 반복은 금지. G/F 측정 재사용을 명목으로 검증된 설치 예산 숫자만 복사해 새 v113 프로필을 승인하는 우회도 금지.

## 7. 개발·검증·권한과 종료 조건

- 현재 저장소는 **격리 개발**이며 이 채팅에서 GitHub 쓰기와 일반 제품 개발을 했다는 사실이 주 제품 소유권을 main/MAIN/WORK에 이전하는 승인은 아니다. 별도 승인 없이 main 병합, immutable v003 변경, 원본 v016 파일 통합/변경, Project Sources·Instructions UI 실제 적용 주장, Work OS 공식 M0/Shared State·승격 금지.
- 다음 채팅의 첫 요청은 **GitHub 최신 브랜치/HEAD·CURRENT·정책·실제 코드·Actions/Native·78 상태의 읽기 전용 독립 복원 보고만** 수행한다. **코드·문서·CI/테스트 실행·새 HTTP/DB2·Native·커밋 금지**. 사용자 별도 '진행' 지시 뒤 그 시점 최신 상태와 권한을 다시 확인하고 개발한다.
- 인계 작업 자체는 기존 정본에 새 정보만 기록한다. 현재/옛 역사 인계들의 '최신·다음·PENDING'을 그대로 복사하지 않는다. 불확정 사항은 미확인으로 표시하고 기록한 실증·임시 테스트·제품 최종 수락의 경계를 분리한다.

## 8. 새 채팅의 읽기 순서

1. 현재 실제 개발 브랜치와 최신 HEAD 조회, 최근 commits/Actions 확인. main을 대체 정본으로 임의 채택 금지.
2. [상시 제품 우선·사용자 단계 선설명 정책](development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md), [제품 소비·중단 감사](development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md), [최신 승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md).
3. [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md)의 최신 부분, [로드맵 M0~M7](development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md), [78 JSON](development/78_ELEMENT_COMPLETION_CONTRACTS.json)·[v441 필요성 감사](development/78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md).
4. 이 **시점 인계서**, [동적 인계 프로토콜](CHAT_HANDOFF_DYNAMIC_GITHUB_RECONSTRUCTION_20261115.md), 필요한 [FILE_MAP](development/FILE_MAP.md)·[EVIDENCE_INDEX](development/EVIDENCE_INDEX.md)·[DECISIONS](development/DECISIONS.md).
5. 바뀐 실제 생산자→소비자 코드, 테스트, v490 등 관련 Actions/Native 영수증을 **관련 범위만** 열어 독립 대조. 전수 회고 금지.

### 새 채팅 첫 응답 요구

'실제 HEAD 및 이력 → 제품 목적/현재 실제 사용자 기능 → v486~v490 변경/오프라인 검증과 기존 Native 재사용·미실증 → 필수 M1~M3 vs 선택 M4 보류 → 15/78의 최신 실제 상태와 M0~M7 위치 → 비용 대비 가장 높은 실제 다음 장애 후보/STOP할 불필요한 작업 → 권한·미확인'을 간결히 보고하고 **STOP**. 최초 요청을 사용자 '진행'으로 해석하지 않는다.
