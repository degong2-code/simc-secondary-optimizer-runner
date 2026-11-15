# SIMC SECONDARY OPTIMIZER — 제품 취지·실제 소비 범위·과잉 검증 감사 정본

> **2026-11-15 사용자 직접 결정에 따른 상시 개발 판단 기준. 제품 완성까지, 개발 채팅·인계 채팅 모두 적용.**
> 이 문서는 [11월 14일 제품 우선·최소 충분 검증 정책](POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md)을 **실제 과거 작업과 주요 코드에 적용한 감사 기록**이다. 승인 v1.4.3 및 비충돌 v1.4 계열을 변경하지 않으며, 이미 완료된 [v441 78/78 수락조건 감사](78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md)를 다시 수행하라는 지시가 아니다. 근거 없는 PASS, 신규 Gate, 자동 삭제 허가가 아니다.
> **기록 시점** 격리 브랜치 HEAD: `7882bc6d8b0e5f90b28f76b3d6fe52491d03f38b` (v479). 이 SHA와 아래 숫자는 *역사 스냅샷*이다. 차후에는 브랜치 실제 HEAD·코드·[CURRENT](../CURRENT_PRODUCT_DEVELOPMENT_STATE.md)·[78 JSON](78_ELEMENT_COMPLETION_CONTRACTS.json)·Actions/Native 영수증을 먼저 다시 확인한다.

## A. 사용자 제품 목적 — 모든 필요성 판단의 기준

- 26개 DPS 전문화(증강 기원사·탱커·힐러 제외). 미래 목표 ilvl 기본 334 또는 사용자가 지정한 **최종 CHMV T**를 기준으로 치명/가속/특화/유연의 **절대 rating**을 기존 적응형 SimC DPS로 최적화한다.
- 사용자 입력: 직업·전문화·종족·특성, 목표 ilvl/수동 T, 장신구 2개, 선택 특수·제작/장식 최대 2개, 보석/최고 품질 영약/음식/물약/무기 기름/지원 영구 마부/전투 조건. 일반 장비 전체를 입력받지 않음. 현재 착용 장비 스탯 재분배나 장비 추천을 하지 않음.
- 프로그램: 시즌별 대표 일반 장비·무기·티어 4pc, 주능력치/SimC 실행 프로필, **G/J/F/O 자동 구축**, B=G+J+F, T=B+O 및 수동 T 우선, 정확 L/E/O 1회 귀속·고정 하한·JSON2 정합, 선택지/세션/캐시/취소·재개/95% 판정/실제 결과. SimC: 아이템 효과/proc/APL/DPS.
- 기본 환경의 필수 ID/스탯·빌드/출처는 검증한다. *미선택* 추가 소켓·특수효과·시즌 모듈이 미확정인 이유로 검증된 BASE 실행을 막지 않는다. 미검증 *선택된* 기능은 정확한 이유로 fail closed.
- 이번 감사는 검증 수준을 약화하는 결정이 아니다. 정확한 결과와 캐시·재사용을 보존하면서 **제품이 소비하지 않는 것을 검증·수집·관리하지 않는 결정**이다.

## B. 과거에 이미 달성한 일과 추가 반복이 불필요한 일

| 영역·기존 자산 | 확인된 가치·증거 | 앞으로의 결정 |
|---|---|---|
| v155/v161/v163/v165~v167, v191/v211/v213, v216/v217/v212 | 시즌 발견·동일 빌드 원본·장비 후보·환경 설치·SHA 재사용. [v405 실제 자동 후보](notes/2026-11-13_p1-v405-a7-automated-current-source-selection-verified.md), [v400 10-DB2 원본](notes/2026-11-13_p1-v400-a6-db2-ten-table-source-provenance-scoped-ready.md) | **유지/재사용**. 새 시즌 또는 실제 소비 필드가 변할 때만 수집·검증 |
| v222 및 관련 예산·정적 캐시 | 시즌 G/J/F/O, B/T, 최종 rating, L/E/O·장신구 분리 | **유지**, 수동 T 및 고정 하한·중복 방지는 계속 검증 |
| v098/v096/v094, v106, v290/v291/v292/v293, v113 UI | 대표 프로필 → 기존 SimC 적응형 실행 → 캐시·95%·중단/재개·결과 | **유지/연결**, 새 탐색 엔진이나 결과 재생 Native 만들지 않음 |
| 실제 사용자 Native 실행 | 냉기 마법사 수동 T [#42785318578](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42785318578), 풍운 자동 T [#42941245130](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42941245130), 조화 자동 T [#42949922419](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42949922419), 생존 웹·실 DPS [v417 #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756), 선택 4pc 실 Native [v439](notes/2026-11-14_p1-v439-b8-one-real-selected-70783-four-tier-native-e2e.md)·[v440 95% 재판정](notes/2026-11-14_p1-v440-b8-existing-real-json2-95-material-replay.md) | **동일 조건·증명 범위에서 재사용 후 STOP**. 기본 경로를 '처음 입증'하는 Native/합성 검사를 반복하지 않음 |
| v303~v331 탐색 품질 연구 | 당시 비교·탐색 정책·N 기본값 결정의 실측 | **동결/재사용**. 실제 탐색 품질 결함·새 사용자 요구가 없으면 아이디어·SEM 미세조정 연구 확장 중단 |
| v401·v441 78요소 수락·상태 | v441에서 78/78을 재검토하여 **54개 과잉 문구 완화, 24개 유지**. 한 실제 영수증의 여러 요소 공동 귀속 허용 | **관리용으로 유지**. 78개 순서대로 개발·Native 78회 금지. next_review=B10은 원장 판정 순서이지 다음 개발 명령이 아님 |
| v445~v451 | 기본 소켓/보석 J 소유권 및 정확 ID·수치·실패 경계에 실제 기여 | **유지**, 소켓 효과의 독립 재구현과 혼동 금지 |
| v452~v455 | 추가 소켓 사용 주문·SpellEffect 원본과 미확정 상태를 남긴 역사 연구. [v454 실 57MB SpellEffect](notes/2026-11-14_p1-v454-v455-b10-real-spell-and-sealed-v281-j-source.md) | **이력 보존, 내부 주문 연쇄·미선택 추가 소켓 정밀 추적 STOP**. v281 자체는 영약/기름 F/O 연결에 쓰이므로 전체 제거 불가 |
| v457~v478 | 시즌 UI 상태·현재 빌드·설치 SHA·옵션 identity 혼동을 줄인 국소 수정 | **회귀 방지 가치 보존**. 동시에 v477의 UI 설치 장비 카탈로그 강제 조건이 서버 실증보다 과도한지 **점검 후보**, 자동 삭제 아님 |
| v479 | 4 일반보석·O=0·장신구2·수동 T·설치 SHA·95% 출력의 *합성* 오프라인 연결 검사 | **증거로 보존 후 추가 기본 경로 합성 테스트 확장 STOP**. 실제 Native 검증으로 승격 금지 |

- **11월 14일에 이미 '다른 DPS 기본 사용자 E2E 신규 1건 불필요, 기존 영수증 REUSE 후 STOP' 결정이 있었다.** 본 감사가 이를 재확인한다. 과거 PASS가 현재 모든 시즌·26전문화·선택 항목을 입증한 것은 아니라는 경계는 지킨다.
- **기록 당시** 정본 [78 JSON](78_ELEMENT_COMPLETION_CONTRACTS.json)은 15/78 COMPLETE, 전체 엄격 ZERO-SOURCE→USER-E2E PENDING. 이 사실을 중복 Native/DB2를 매 변경마다 실행하라는 지시로 오해하지 않는다.
- **규모 진단(기록 당시 Git tree)**: 1,688 blob, runner Python 206, tests Python 312, Actions workflows 212, 개발 노트 351; `runner/v216_environment_build_coordinator.py` 약 8,091행. 이는 **관리·유지 비용과 중복 경로를 점검할 신호**이지 파일 수만으로 삭제를 승인하는 증거는 아니다.

## C. 구체적 자료·식별자: 제품에서 소비하는지에 따라 판정

| 자료/검사 | 제품 사용·필수 여부 | 권장 처리와 미확정 범위 |
|---|---|---|
| 시즌·게임 빌드, 실제 선택 ItemID/ilvl/부위/옵션, 대표 티어/무기, G/J/F/O, 수동 T, L/E/O, SimC 입력/JSON2, DPS 캐시 identity | **실제 소비·결과 변경** | 엄격 유지. 미관측=0이나 전 시즌 값 무단 대체 금지 |
| Wago DB2 관련 원본 10개 테이블, Blizzard 활성 인덱스, WCL 활성 레이드·쐐기 관계 | **해당 시즌의 실제 소스 선택과 조인에 필요한 부분** | 사용한 원본만 동일 시즌·빌드/SHA 검증. 전체 DB2·전체 콘텐츠·전체 로그는 수집하지 않음 |
| `WorldStateExpressionID` (v163) | **시즌 admission 판정에 사용하지 않는 불투명 진단값** | v404/v405대로 보존·진단만, 수치 의미·내부 효과·모든 WSE 원본 인증 및 필수 Gate 금지. `DisplaySeasonID`·실제 콘텐츠 관계와 구별 |
| v280 Item→사용 SpellID, v281 SpellEffect | **F/O 및 기름 SimC ID 연결에 실제 사용되는 부분 존재** | 실제 F/O owner와 정확한 선택 ID/손 검증만 보존. 추가 소켓 주문 연쇄 추적이나 일반 임시 마부 전수로 확대 금지 |
| `source_only`·`unadmitted`·`PENDING`, source_scope 같은 구분자 | 소비 여부 **필드·호출자별** 다름. 후보 승인과 설치 READY 구별은 필요 | 단지 문자열/필드 존재 때문에 새 검증 금지. 실제 실행 차단·선택지/캐시 identity에 쓰이면 유지; 진단·과거 호환만 쓰면 비차단. 삭제 전 저장/복원 계약 확인 |
| Blizzard 원문 HTTP SHA·WCL GraphQL SHA, v217 receipt | **원본 출처·재사용 무결성에 필요한 검증 존재** | 이미 신뢰된 봉인에서 같은 파일을 매 단계 다시 전체 해싱할 필요는 없음. v400이 v217 후 v163 중복 10 CSV 해싱을 생략한 사례 재사용. HTTP SHA 형식만으로 아이템·효과 승인 금지 |
| SimC 실행 바이너리 버전/SHA | **DPS 캐시와 결과 재현에 필수** | 보존. [v409](notes/2026-11-13_p1-v409-a8-simc-metadata-and-result-snapshot-policy.md)대로 게임 빌드 문자열 완전일치·컴파일 계보 인증·동일 SHA 실행파일 별칭 차단 불필요 |
| 품질 rank/효과 fingerprint/증거 SHA | **최고 품질 사용자 선택지 등록 시 필요한 조건만** | [v371](notes/2026-11-12_p1-v371-policy-a-quality-evidence-contract.md)처럼 같은 효과·사용 조건·적용범위·비열등 수치를 확인. rank·SHA 존재만으로 승인 금지; 선택하지 않은 낮은 품질 전수 인증 금지 |
| SimC temporary_enchant 원본 | **무기 기름은 제품 지원**, 일반 임시 마부는 지원 외 | 내부 구문을 전부 금지하지 않음. 실제 지원 oil에만 적용 손/O/소유권 검증, 일반 임시 마부 옵션은 비노출·미등록 |
| 추가 소켓·촉매·시즌 모듈 | **실제 선택한 조건에서만** | 검증 실패 시 그 변형만 보류. 보편 BASE의 일반 4보석을 불필요하게 막지 않음 |
| 개발 노트 8필드·Capability 최신 링크 및 78개 원장 | **개발 기록**이지 SimC 런타임 입력이 아님 | 78 JSON·v401 최종 상태는 정직하게 유지. 역사 노트 전체 형식을 현재 CI 필수 Gate로 삼는지 재검토; 새 변경 증거만 최소 정합 |
| UI `v477` 설치 카탈로그 봉인·ilvl guard vs v478 서버 설치 SHA 검증 | SHA·빌드·ilvl·선택 F/J/O의 **정확성 필수**, 중복 UI Gate 필요성은 미확정 | *검토 후보*: 서버 확인보다 강한 UI 입력/목록 조회 의존이 정상 실행을 막는지 실 호출 경계·기존 영수증으로 대조. 재현 전 임의 해제 금지 |

## D. 실제 구조 감사에서 드러난 우선 정리 후보

1. **v216 조정기 8,091행**: 정상 시즌 Build의 필수 G/J/F/O·대표 프로필 경로와 과거 연구용 source-only·선택 진단 경로를 함수/호출/출력 소비 기준으로 구분. 덩치 때문에 전면 재작성하거나 v217 캐시·봉인을 해체하지 않는다.
2. **소켓 B10**: `_fresh_attach_existing_v280_socket_preview`는 선택 5+ 소켓일 때만 이미 수집한 v280/v281 receipt 진단을 붙인다. 일반 4보석의 필수 J 경계와 다르다. 주문 효과 추적의 추가 DB2/Native 비용이 **실제 선택 결과를 바꿀 때에만** 조사.
3. **source provenance 이중 인증**: 실제 소비한 동일 원본을 v217/상위 owner가 이미 검증했는데 downstream이 불필요하게 전체 read/hash를 다시 수행하는지 좁게 확인. 다만 원본이 외부에서 변경될 수 있는 경계의 최초 검증은 유지.
4. **UI/서버 중복 차단**: v477-v478 같은 정밀 guard가 검증된 BASE 실행을 잘못 막는지, 새 인자·SHA·저장 세션 호환성 때문에 막는 것은 아닌지 사용자 시나리오 기준으로 검토. 이는 후보이지 확정 결함 아님.
5. **반복 개발 메타데이터 CI**: `tools/check_development_ledger.py`의 기존 198 `DEV_LEDGER_FAIL`은 노트 format/Capability/Decision/INDEX 포인터 오류. 제품 SimC 실패와 다름. 역사 351 노트를 전부 현 템플릿으로 재작성하거나 제품 PASS를 실패로 오인하지 않음. 별도 관리·변경분 중심 검증 검토.
6. **워크플로·노트·분류 상태 누적**: 실제 호출되지 않는 one-shot 실험/진단 워크플로는 신규 표준 시험 목록에서 제외하고 역사 증거로 보존. 삭제는 참조·필요 회귀·배포 호환 확인 이후만.

위 후보에 대해 **모든 함수·필드의 호출자 추적이 끝났다는 주장 금지**. 삭제·runtime Gate 해제·정식 완료 승격은 아직 수행하지 않았다.

## E. 모든 후속 개발·인계에서 사용하는 실전 판단 절차 (새 Gate가 아닌 업무 원칙)

**매 작업은 이 순서로, 필요한 깊이만 확인한다.**

1. **현재 사실**: 지금의 GitHub branch HEAD·CURRENT·관련 실제 함수/테스트·78 JSON·Actions/Native 영수증을 확인. 오래된 '최신' 문서나 이 채팅의 SHA를 고정 사실로 쓰지 않는다.
2. **사용자 가치**: '누가 어떤 입력을 했을 때 지금 무엇이 불가능하고, 수정 후 어떤 결과를 얻는가?'를 1문장으로 명시. 과거 테스트의 반복 PASS만 늘리면 STOP.
3. **실제 소비 경로**: 값/구분자의 **producer → 변환/봉인 → consumer → 사용자 선택·G/J/F/O·프로필·DPS·세션·결과**를 추적. 사용되지 않는 진단은 비차단; 정체성/오염 방지용 필드는 소비자로 인정. 저장 세션/이전 버전 역호환도 소비 범위.
4. **반증**: 잘못된 값이 사용자 결과·안전성·캐시·복원에 실제 영향을 주는가? 단순 자료 존재/이름/형식/시즌 추정만으로 Gate 추가 금지.
5. **기존 증거**: 같은 조건에서 이미 PASS인 실제 Native/Actions·원본/캐시가 있으면 REUSE. 새 실증 요구가 기존 증거와 무엇이 다른지 설명 불가하면 STOP.
6. **선택 격리**: 선택형·미선택 기능 부족은 BASE 차단 금지. 선택한 입력의 미검증은 해당 입력만 정확히 차단.
7. **비용·변경 최소화**: STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW. 새 HTTP·DB2·Native·파일/I/O·CPU·메모리·반복 타임·패키지 복잡성의 증가 이유를 구체화.
8. **수정 영역만 검증**: UI→UI 테스트, 예산→산술/JSON2, source→변경된 source/receipt, 신규 실제 SimC 런타임 경계→필요한 최소 Native. 기본 경로의 동일 Native를 매 버전 반복하지 않음.
9. **종료 보고/STOP**: 코드 변경, 신규 오프라인 PASS, 과거 Native 재사용, 새 Native(실시한 경우만), 미검증·재현되지 않은 의심, HTTP/DB2·캐시 영향, 남은 *실제 사용자 장애*를 분리. 필요 근거 없으면 추가 과제 만들지 않음.

### 판단의 결과를 네 가지로 표시

- **KEEP/REUSE**: 실제 제품 소비·정확성/캐시/호환성에 필요하거나 기존 실증 충분.
- **SIMPLIFY/ISOLATE**: 제품 소비는 있으나 중복 확인/선택 연구가 기본 경로를 과도하게 지연·차단.
- **STOP**: 실제 현재 제품 가치가 없거나 이미 유효한 증거가 충분한 연구·재실측·정밀 검사.
- **CANDIDATE TO REMOVE**: 함수/자료·구분자의 실제 런타임/세션/호환 소비가 없음을 확인한 뒤에만 삭제. 추정으로 삭제 금지.

## F. 권한·승격·인계 연속성

- 최신 사용자 직접 결정 > 최신 승인 제품 정책(v1.4.3 및 비충돌 기준) > 현재 코드/CURRENT/Actions/Native > 과거 인계·연구 노트. 충돌 때는 **현재 코드가 진짜 구현한 것**과 **설계상 의무**를 구분한다.
- [78 JSON](78_ELEMENT_COMPLETION_CONTRACTS.json)·네 축 및 엄격 최종 ZERO-SOURCE→USER-E2E PASS 요구는 보존하되, 이를 매 작업 단계의 추가 Native·모든 미선택 효과 인증 의무로 해석하지 않는다. 상태 변경/기존 원본·main·immutable v003·Project Sources/UI·Work OS 공식 승격에는 별도 권한이 필요하다.
- 주 제품 개발 채팅의 소유권을 인계 문서만으로 이전하지 않는다. 격리 브랜치 작업만 승인된 범위에서 수행한다.
- **향후 독립 인계는 [동적 GitHub 복원·판단 프롬프트](../CHAT_HANDOFF_DYNAMIC_GITHUB_RECONSTRUCTION_20261115.md)를 사용**한다. 새 채팅은 먼저 **읽기 전용 현재 상태 복원** 후 STOP, 별도 명시된 진행/수정 범위에서만 작업한다.
- 감사 판단이 바뀌면 당시 증거·사용자 승인·실제 소비 위치를 이 문서에 **부분 개정**한다. 모든 커밋마다 새로운 감사 문서·Gate·전수 CI를 만들어 중복 기록하지 않는다.

## G. 2026-11-15 감사 마무리: 실제 소비 경계와 과잉 운영 검사 교정

- **v477 UI 카탈로그 범위 검사의 판정: KEEP (현 단계).** `webui/app.js::verifiedInstalledGearScopeMatchesRun`은 화면에서 과거 packaged `v167` 목록을 새 장신구 선택 근거로 오인하지 못하게 한다. 실제 서버 `v113::load_fresh_profile_for_user` 및 `/api/v1/season-gear`는 SHA와 같은 build/ilvl/F/J/O를 별도로 확인한다. 서로 소비하는 경계가 달라 **단순히 중복이라는 이유로 해제하지 않음**. 현재 재현된 정상 사용 차단 사례 없음; 향후 발견 시 최소 수리.
- **과잉 확인 확정: 351개 append-only 역사 개발 노트 전수 형식 검사.** 기본 `tools/check_development_ledger.py` 실행은 8필드/Decision/Capability index 규격을 옛 노트까지 강제해 동일한 198 기존 `DEV_LEDGER_FAIL`로 제품 기능 회귀 단계 이전에 CI가 종료됐다. 이는 SimC/원본/예산 문제가 아니다.
- **변경 결정: NORMAL=현재 INDEX의 링크·행 형식만 확인; `--audit-history` 또는 명시적 구식 `--since`=이전 전체 역사 원장 감사.** 기존 notes/INDEX 및 78요소 계약 파일의 값은 변경하지 않음. focused 워크플로에 원장 스코프 회귀 테스트를 포함하고 기록 관리 실패를 실제 제품 기능 검증과 구분. 역사 노트를 새 템플릿으로 일괄 수정하지 않음.
- **유지 범위:** 선택 F/O에 필요한 `v280/v281` 효과/ID, WSE 진단 비차단, v217 캐시 무결성, v212 설치 SHA, 사용자 프로필 JSON2, 95% 결과 및 캐시·취소·재개. 실제 호출자 확인 없이 v216 코드를 대규모 삭제·재작성하지 않음.
- 이번 범위는 **관리 검사와 그 회귀**에 한정. 새 시즌 Native·대용량 DB2·G/J/F/O 측정·실 사용자 E2E를 새로 수행했다는 주장은 하지 않음. 기존 v441 54 완화/24 유지, 78 JSON 상태, 공식 완료 기준 보존.

### G.1 공통 회귀의 역사 불일치 정리 (v481)

- v480에서 기존 메타데이터 전수 실패가 사라지자 일반 focused suite **682 tests / 4 FAIL·2 ERROR·2 SKIP**가 실제 실행됐다([Actions #43666304243](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43666304243)). 원장 `DEV_LEDGER_PASS CURRENT_INDEX_ONLY` 자체는 확인. 6건은 다음과 같이 원인 분리했다.
- `test_v260`: 역사 `TIER.SEASON=SOURCE_CORROBORATED/NOT_INTEGRATED`를 현재 고정값으로 가정. 현재 INDEX는 `HISTORICAL/PARTIAL`. 고정 과거 숫자가 아니라 현재 INDEX enum/필수 링크를 검사하도록 수정. **실행 제품 상태 변경 아님**.
- `test_p1_oil_positive_bridge`: v096 실제 source verifier가 기존부터 전달하는 **정확한 설치 SHA 인자**를 옛 mock 호출 기대값이 누락. 정확 SHA 검사를 약화하지 않고 기대값을 현재 계약에 일치시킴.
- `test_p3_gt_reuse_existing_socket_item_use_source` 3건: 예전 가짜 v280 stage fixture는 현재 필수 v217 stage id를 충족하지 못함. `test_p3_gw_declared_full_sockets` 1건: 예전 7보석 가정이 현재 추가 소켓 실제 검증 대기 상태와 다름. 둘 다 미선택 5+ 소켓 연구 자료이므로 **공통 기본 CI에서만 분리**, 개별 테스트 코드·역사 FAIL·선택 필요 시 추가 검증은 보존. 실제 선택 5+ 기능을 완료 또는 PASS로 주장하지 않음.
- 공통 CI는 실사용 핵심 연결+현재 인덱스 검증을 계속 확인하지만, 문서만 변경할 때 매번 600+ 오프라인 테스트를 실행하지 않도록 `docs/development/**` push trigger를 제외. 공식 v401 78 JSON·제품 필수 원본·Native 검증은 그대로 독립 실행/보존.

### G.2 감사 종료 판정·제품 개발 재개 기준

- **최종 관련 영수증(2026-11-15)**: [기본 Reusable Offline Actions #43666580045](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43666580045): **673 tests / 671 PASS / 2 SKIP / 0 FAIL**, 원장 `DEV_LEDGER_PASS OFFLINE_NO_NATIVE_NO_NETWORK CURRENT_INDEX_ONLY`. [v401 78 계약 #43666580035](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43666580035) SUCCESS. 이 성공은 **오프라인 기존 코드 회귀**이며 새 Native·G/J/F/O 실측·엄격 ZERO-SOURCE→USER-E2E PASS가 아니다.
- **감사 종료**: WSE 비차단 KEEP, v280/v281 F/O 필수 owner KEEP, v477 UI 선택 근거·v478 서버 SHA 검증 KEEP, 역사 원장 기본 형식 전수 Gate STOP, 오래된 선택 추가 소켓 연구 테스트는 기본 CI에서 분리·선택 시에만 재검토. v216 전체 재작성·미사용 필드 일괄 삭제 없음. 동일 기본 E2E 신규 Native 없이 STOP.
- **제품 개발 재개 판단**: 정상 기본 사용자 최적화 경로는 기존 실제 증거로 재사용. 실제 신규 시즌 사용자 선택에서 현재 `runner/webui/app.js`는 음식·물약·증강룬을 `source_default` 중심으로 제한하며 `runner/v196_current_season_user_catalog.py`의 영구 마부 E는 `NEW_SEASON_E_NOT_VERIFIED`인 범위가 남아 있다. 이는 **실사용 선택 기능 후보**이며 미검증 값/효과를 UI 승인하지 않는다. 먼저 원본·선택 ID·SimC 토큰·품질/CHMV 소유자·이미 확보된 증거를 확인하고 *실제로 가능한 선택지부터* 최소 연결한다. 단순 전체 소모품/마부 목록 전수 인증이나 별도 SimC 효과 검증 Gate는 도입하지 않는다.
- 신규 코드/테스트에서 실제 확인한 첫 사용자 장애가 없으면 기능을 억지로 개발하지 않는다. 정확히 검증된 선택지 하나의 연결이 보이면 그것부터 처리하고, 선택이 없다면 STOP 후 다음 사용자 가치 항목을 검토한다.

## H. 2026-11-15 P1 범용 옵션 등록 — 실제 소비 경계 최소 수정 (v482)

- **현재 원본 상황:** `v191` 음식/물약은 DB2 ItemID 후보(`DB2_ID_ONLY`), `v108`의 food/potion/augmentation은 과거 MID2 SimC 프로필에서 본 토큰 문자열. 그 자체로 현재 시즌 물리 ID·최고 품질·사용 조건·프로필 입증이 아니다. `v220` 정책 A는 이미 consumable을 다룰 수 있지만 인증된 현재 item-level receipt가 없어 일반 선택으로 승인할 수 없음. **새 자동 등록·효과 Gate/전수 Native를 만들지 않는다.**
- **실제 결함:** `/options` 및 UI에서는 source_default만 허용하지만 서버 `v218._verified_fresh_season_consumables`는 v108 historical `SUPPORTED`에 있는 토큰을 *신규 현재 시즌 요청에서 허용*했고, 공개 API가 화면을 우회할 수 있었다.
- **수정:** `v218.current_season_approved_optional_choices()`를 현재 실행 허용 선택지의 공통 원천으로 사용, `v113 /options`와 서버 프로필 생성 사전검사에서 공유. 실제 신규 season item proof가 없으므로 일반 현재 시즌은 `source_default` 및 효과 없음 alias `disabled`만 허용. 검증된 신규 아이템이 나타나면 동일 공통 owner를 v212 등록·SimC 입력과 연결할 예정이며, 그 전에는 과거 토큰을 항목별 하드코딩 승인하지 않는다.
- `v113.plan`은 **세션/프로필/Native 이전**, `prepare_with_internal_special_L`은 정확 L hydration 이전에 검증한다. 사용되지 않는 선택 기능에 새 외부 API, DB2, Native, 대량 파일 검사는 추가하지 않았다. 기존 역사 세션 조회·캐시는 변경하지 않는다.
- **검증 범위:** 서버 direct API plan/start/longrun prepare에서 원래 v108 토큰·임의 신규 token 선택의 공통 실패와 `disabled` 안전 별칭, 기본 HTML UI 허용 목록의 일치. 신규 시즌 소비품 auto registration 완료, item-level source proof 획득, 실제 Native 실행을 **주장하지 않음**.

### H.1 v482 실제 확인 영수증

- 코드: [v482 공통 승인 경계](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/95df7f80b07964e32426ff779fdb8890f7d228ec) + [기존 합성 전달 검증 보정](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/433cb56666e19ee55c98c48a0718444b7e146370). 직접 API 신규 요청이 옛 v108 SimC 문자열만으로 승인되지 않도록 **v113+v218 권한 일치**. 기름·F/J/O·세션 캐시 수정 없음.
- 이번 실행: [v113 #43668705725](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43668705725) Windows/Linux 각각 **389 tests/388 PASS/1 SKIP**, [Reusable #43668705723](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43668705723) **673 tests/671 PASS/2 SKIP**, [v401 #43668705705](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43668705705) SUCCESS. 모든 언급한 PASS는 **오프라인**이며 신규 Native/HTTP/DB2 0.
- **현재 P1 범용 엔진 상태:** 원본 후보 자동 수집 및 공통 v220 정책 A·v098 SimC 입력 엔진 **기존 구현**. 그러나 음식/물약/증강 룬의 신규 시즌 *물리 아이템↔SimC 토큰↔최고 품질·사용 조건*의 실제 일치 영수증은 아직 이 코드 경로에서 제공되지 않아 `source_default`만 승인. 본 코드가 범용 등록 엔진 전부를 완성했다거나 개별 아이템을 등록했다고 주장하지 않음.
