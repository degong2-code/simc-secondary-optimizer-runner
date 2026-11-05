# 개발 연속성 규약 · 2026-11-03 사용자 직접 교정

**권위:** 최신 사용자 직접 결정. 이 문서는 GitHub 격리 브랜치의 **개발/인계 운영 규약**이며 승인된 제품 설계 v1.4.3의 원문, main, immutable v003, 원본 v016, Project UI/Work OS를 변경하지 않는다.

**환경 입력 관련 필수 선조회:** 레벨·종족·특성·음식/물약/증강·보석/가변 소켓·영약/기름·Omnium·품질/정책 A 작업 전에 [2026-11-04 환경 구축 입력 12항목 책임표](ENVIRONMENT_BUILD_INPUT_SCOPE_20261104.md)를 읽고, 각 항목의 REUSE/CONNECT/EXTEND/STOP·기본 G/J/F/O와 선택형 기능 경계를 확인한다. 이 문서는 승인 원문 교체가 아닌 기존 정책과 구현을 구분하는 개발 색인이다. 특히 P3-BN SimC 기본 level 및 P3-BZ 기존 가변 socket_plan 구현을 재개발하지 않는다.

## P3-FK 현재 단일 인계·읽기 전용 새 채팅 (2026-11-05)

**현재 인계 정본:** [P3-FK 엔진 연속성](../CHAT_CONTINUITY_HANDOFF_20261105_P3_FK_ENGINE_FIRST_RESTORE.md). 이전 P3-EV/ES/EN/EE/DW/DO는 작성 당시의 역사 정본. 새 채팅은 **격리/main HEAD 각각 독립 조회 → P3-FK → 이 PROTOCOL → INDEX E3/E2/E1·C1~C4 → CURRENT 상단/개발자 실행 노트 → P3-FJ/FI/FH/FG/FD/FE 및 필요한 E* → 해당 실제 코드·봉인 원본·Actions/Native** 순서로 좁혀 본다. **새 채팅 첫 답변은 읽기 전용 복원 보고 후 STOP**, 명시적 '진행' 이전 수정·수집·CI/Native/테스트·승격 전면 금지.

**제품 변경 경계:** P3-FJ는 v232 봉인 기본 소켓과 v271 특수보석 정확 1개+일반 N개 장착 위치를 **역할별 ID 제공 시** 연결했고 focused 270 PASS. **보석 정확 역할/ItemID source-owner 자동 선택과 실 신규 시즌 READY/T1은 아직 미완료**. P3-FD~FG J/F 원본 조건부 v222 설치 및 P3-FH 발견 최대 F opt-in·P3-FE source_relation 재사용은 기존 자산. 새로운 소켓/보석 엔진·기능 게이트 재개발 금지. 목적은 다음 시즌 26 DPS 공통 엔진 하나.

## P3-EV 당시 최신 인계/실행 경계 (2026-11-05)

**단일 인계 정본:** [P3-EV 환경 설치 엔진 인계](../CHAT_CONTINUITY_HANDOFF_20261105_P3_EV_ENGINE_INSTALL_RESTORE.md). 다음 채팅은 격리/main HEAD를 각각 독립 조회 → P3-EV → 이 규약 → [INDEX 기능 라이브러리](INDEX.md)의 **E3→E2→E1**, 필요 시 B3/C4/D1/D2만 → [CURRENT](../CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 최상단 → P3-EU/ET/EV 노트 및 실제 코드·봉인 원본·CI/Native. 기존 P3-ES/EN/EE는 **역사 인계**이며 전체 P3 기록의 순차적 재감사는 금지한다.

**최상위 개발 목표의 흔들림 금지:** 26 DPS 공통의 **다음 시즌에도 재사용 가능한 자동 환경 구축·DPS 최적화 엔진**을 완성한다. 이번 시즌의 숫자를 고정하는 것은 목표가 아니며 현재 시즌을 '신규 시즌'으로 보고 처음부터 정상 Build를 수행하는 **실제 T1 시험**은 엔진을 검증하는 수단이다. 현 P3-EU에서 `v216` 내부 검증 입력 provider → `v222/v196/v212` → `v217` 설치/재개 **합성 경로는 연결 완료**, 그러나 실제 자동 source-owner 공급자·실 제품 T1은 미완료다. 문자열 `VALID_SAME_SEASON_SOURCE`, callable 형태나 합성 READY가 출처 검증을 대체하지 않는다. 증거 부족·원본 미연결·선택 항목 불필요를 먼저 구별하고 불필요한 Gate/수집/Native 재개발을 금지한다.

**새 채팅 첫 동작은 읽기 전용 독립 복원 보고 후 STOP.** 사용자 명시적 `진행` 전에는 코드·문서 수정/커밋, 신규 원본 수집·CI/Actions/Native/테스트 실행, 공식 Project UI·Work OS/원본 승격 금지. 일반 개발도 기존 주 제품 개발 채팅 소유권 원칙을 따른다.

## 최신 운영법 · P3-ES 기술 자산 중심 탐색 (2026-11-05)

**현재 탐색 정본:** [기능별 라이브러리 INDEX](INDEX.md) — A~G 상위/하위 영역의 **재사용 함수·증거 적용 범위·미연결·재개발 금지**부터 확인한다. 16개 기존 Capability 키는 이 파일 하단의 6열 호환 표로 보존하며, 기존 수백 개 작업 번호의 상세 원문은 [2026-11-05 INDEX 스냅샷](HISTORICAL_INDEX_20261105_PRE_LIBRARY.md)과 개별 notes에서만 조회한다. 이 새 지도는 증거 인증이 아닌 검색 최적화다.

**작업 라우팅:** 환경 신규 READY는 `E3→E2→E1`, 필요 시 `B3/C4/D1/D2`만. 보석은 `C1~C4`, 시즌 수집은 `A1~A3`, 사용자 최적화는 `F1/F2`, 인계는 `G2`부터. 현재 코드의 PENDING만으로 **실제 소스 부족**을 추정하지 않고 기존 소스 미전달/선택 항목 미요구/검증 미완료를 구분한다.

**갱신 정책:** 작업 번호를 표에 시간순 누적하지 않는다. 기능 행의 현재 함수·확립된 Evidence/적용 범위·Integration·다음 최소 결손만 갱신하고, 하단 기존 Capability 행에는 **해당 키에 속하는 최신 노트 1개 링크**를 유지한다. 이전 인계·실패·영수증은 삭제하지 않고 역사 스냅샷에 보관한다. 이미 있는 코드·캐시·Native/Actions를 재사용한 뒤 필요한 것만 EXTEND한다.

**새 채팅 단일 진입점:** [P3-ES 자산 라이브러리 인계](../CHAT_CONTINUITY_HANDOFF_20261105_P3_ES_ASSET_LIBRARY.md). 아래 P3-EN/EE/DW/DO의 '현재 정본' 표기는 **작성 당시 역사 기록**이다. 새 채팅은 양 HEAD 독립 조회→P3-ES→PROTOCOL→관련 INDEX 영역→CURRENT 상단→실 코드/원본/CI·Native; 첫 응답 복원 후 사용자 `진행` 전 **STOP**. 현재 제품 T1 READY·공식 G/J/F/O/실제 정책 A 발행은 미완료.

## 매 논리적 작업 묶음마다 필수: 4단계

1. **선조회(작성·추가 검증보다 먼저).** [INDEX.md](INDEX.md)의 해당 **A~G 기능 하위 영역**을 먼저 선택하고, 대응하는 16키 `Capability`와 키워드·구현 함수·Evidence 범위를 좁혀 관련 **기존 원본 영수증과 실제 코드**만 확인한다. 필요하면 GitHub 전체 코드/역사 기록으로 좁혀 검색한다. 검색어가 없으면 새 고정 capability 키를 추가한다. **현재 코드의 `false`, `PENDING`, 미완료 문구만으로 원본 증거 부재를 단정하지 않는다.**
2. **문제 구분·재사용 결정.** `Evidence`(어떤 사실을 어떤 시즌/빌드/옵션까지 확립했는가)와 `Integration`(제품에 연결되었는가)를 **따로** 판정한다. `REUSE`(이미 증명/구현된 부분), `CONNECT`(연결만 미완료), `EXTEND`(실제 부족한 근거만 보완), `NEW`(기존 대응 없음), `STOP`(불필요/범위 외) 중 하나와 근거를 선택한다. 새 인증 Gate·새 Native/HTTP는 실제 누락된 사실과 기존 증거로 해결 불가능한 이유가 특정된 경우에만 검토한다.
3. **한 작업 = 한 짧은 GitHub 노트.** `notes/YYYY-MM-DD_<task-slug>.md`를 작업 전부터 기록해 작업 범위·재사용 근거·결정·변경·시험·남은 과제·효율을 작성하고, 해당 라이브러리 기능 행의 현재 구현/남은 결손과, 하단 16키 표의 해당 `Last note` 링크 **1개**를 갱신한다. 이전 P3 작업을 시간순으로 라이브러리에 계속 추가하지 않는다. 독립 가능한 여러 세부 작업은 하나의 **논리적 묶음**에 포함 가능하다. 파일별·커밋별 문서를 만들지 않는다. 기존 기록의 사실 오류는 후속 기록에서 교정하고 과거 영수증·실패 이력을 삭제하지 않는다. 새 GitHub 커밋 또는 작업 종료 전에 기록을 반영한다.
4. **인계는 P3-ES와 라이브러리 우선.** 새 채팅: 양 HEAD → P3-ES 인계 → 이 규약 → INDEX의 관련 A~G 하위 영역·Capability 행 → 필요할 때만 해당 note → 원본 영수증/코드 순서로 읽는다. `CURRENT`의 `미완료` 요약만으로 개발을 시작하지 않는다. 인계에는 **재사용 가능한 완료 사실·정확한 적용 범위 / 연결 미완료 / 실제 소스 부족 / 다음 최소 작업 / 검증 방식**을 각각 명시한다.

## 짧은 기록의 정형 필드

[노트 양식](TEMPLATE.md)의 8개 필드(`Capability`, `Keywords`, `Prior evidence`, `Decision`, `Changes`, `Verification`, `Remaining`, `Efficiency`)는 **모두 필수**, 본문은 가능한 20줄 내외, 최대 45줄. 기존 문서/Actions/커밋을 링크로 가리키며 내용을 중복 복사하지 않는다. `Verification`에는 **새 실행 PASS/FAIL, 역사 증거 재사용, 이번에 하지 않은 HTTP/Native**를 분리한다. CI 미확인이면 `NOT_RUN/NOT_VERIFIED`라고 쓴다.

**충돌 처리:** 인덱스는 증거 **위치와 요약**이지 원본보다 높은 진실 출처가 아니다. 최신 사용자 결정 > 승인 설계 > 해당 코드/실제 원본·Native·Actions 영수증 > 인덱스·인계 요약. 반례가 발견되면 관련 note에 교정·범위를 기록하고 INDEX 상태를 수정한다.

**경량 안전장치:** `python tools/check_development_ledger.py`로 INDEX/노트 구조·링크·상태를 네트워크/Native 없이 검사한다. `--since <task-base-ref>`는 해당 작업 범위의 코드·테스트 변경에 노트가 포함되었는지 점검한다. 이는 제품 READY/효과 인증 Gate나 반복 CI/Native 시험이 아니다. 작업 기준 커밋을 명시하지 않는 한 임의로 옛 main 전체 diff를 검사하지 않는다.

**성능·설계:** 기존 원본·동일 시즌 SHA/검증 결과·캐시·Native/CI를 재사용하고, 실제로 부족한 범위만 보완한다. 새 코드 변경마다 중복 HTTP/Native, 캐시 무효화, 메모리/I/O, 전체 시간·구조 간결성을 평가한다. 장기 목표는 **26 DPS용 하나의 재사용 가능한 시즌 G/J/F/O Environment Build → B/T → 기존 적응형 SimC**이며 별도 효과 엔진/전수 장비 DB/추가 인증기 개발이 아니다.

## 새 채팅 인계 복원 동작 · P3-DO 최신 (2026-11-04)

새 채팅 단일 진입점은 [P3-DO 인계](../CHAT_CONTINUITY_HANDOFF_20261104_P3_DO_ENGINE_FIRST.md). 기존 [P3-DF](../CHAT_CONTINUITY_HANDOFF_20261104_P3_DF_ENGINE_RESTORE.md)는 역사 인계다. 격리/main HEAD 각각 독립 조회 → PROTOCOL → INDEX → P3-DN/P3-DM 및 관련 노트 → CURRENT/실행 노트/승인 v1.4.3 → 코드·원본·Actions/Native 영수증 순서로 **읽기 전용** 복원. P3-DG 이후 gear/tier raw SHA 연결·P3-DK 가변 소켓 연결을 다시 미구현으로 되돌리지 않는다.

**최신 P3-DN:** [v212 #41790639319](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41790639319) Ubuntu/Windows 각각 444 tests(440 PASS/4 SKIP)/0 FAIL, [focused #41790639275](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41790639275) 226 PASS/DEV_LEDGER_PASS. 기존 봉인 source_relation 1 family만 연결; `simc_input/product_input/chmv_budget`와 실제 선택지 발행·새 시즌 READY·26 DPS Native E2E는 미완료. 인계 작성/등록은 제품 통합·Native PASS가 아니다.

**새 채팅 첫 응답은 HEAD·핵심 증거·완료/미완료·병목·효율·로드맵·권한 복원 보고 후 STOP. '진행' 이전 개발/코드·문서 수정/커밋/수집/CI·Actions·Native/테스트·공식 승격 금지.** GitHub 문서는 Project UI/Work OS 등록이나 main 병합 증거가 아니다.

## 새 채팅 인계 복원 동작 · P3-DW 최신 (2026-11-05)

- 새 채팅의 **단일 정본**: [P3-DW](../CHAT_CONTINUITY_HANDOFF_20261105_P3_DW_ENGINE_FIRST.md). 위 P3-DO는 역사 기록. 최신 격리/main HEAD를 각각 독립 조회한 뒤 PROTOCOL→INDEX→P3-DN/DM·P3-DS/DT/DU/DV→CURRENT→개발자 실행 노트→승인 v1.4.3→실제 코드/Actions·Native 증거 순서로 읽는다.
- **지금의 완료 Gate:** 하나의 웹앱 `v216` Environment Build가 G/J/F/O·B/T·정책 A 검증 선택지·시즌 설치/READY를 만든다. 이미 개발된 사용자별 v098/v096/v094 DPS 최적화 실행은 **후속 메인 기능**이므로 환경 READY 선행 Gate가 아니다. 최종 제품 목표는 26 DPS 공통 하나의 엔진.
- P3-DV 코드/오프라인 PASS는 자동 F 후보 측정 연결까지의 증거이지 최고품질·예산 승인 또는 전체 T1 READY가 아니다. 새 채팅 첫 답변은 **읽기 전용 복원 보고만** 하고 **'진행' 전 일체 수정·CI/Native/게임 HTTP/테스트·승격 금지**.


## 새 채팅 인계 복원 동작 · P3-EE 후속 정본 (2026-11-05)

- **가장 최근 단일 진입점**: [P3-EE](../CHAT_CONTINUITY_HANDOFF_20261105_P3_EE_ENGINE_FIRST.md), [작업 기록](notes/2026-11-05_p3-ee-engine-continuity-handoff.md). 위 P3-DW/DO는 이전 인계 시점 기록이다. 격리/main 실제 HEAD 각각 조회 → P3-EE → 이 규약 → INDEX → 최근 P3-DX/DY/DZ/EA/EC/ED 및 관련 P3-DN/DM/DS/DT/DU/DV → CURRENT → 개발자 실행 노트 → 승인 v1.4.3 + 최신 사용자 직접 정정 → 실제 코드·원본·CI/Native 영수증 순서.
- **제품 핵심:** 다음 시즌에도 쓰이는 **26 DPS 공통 하나의 엔진**. 현재 T1 Gate는 사용자 웹 `v216` 새 시즌 G/J/F/O → `v222` 공식 B/T → 정책 A 최고 품질 선택지 실제 발행 → `v212` 설치·READY. 후속 `v098/v096/v094` DPS 실행을 환경 READY 필수 Gate로 만들지 않는다. **특수 보석은 정확히 1개 필수**, P3-EB의 0개 허용은 P3-EC에서 철회. P3-ED는 동일 빌드 물리 ID 확인 **source-only**, 실제 품질/효과/소켓 인증 아님.
- 첫 응답은 **GitHub 양 HEAD·실제 영수증·Evidence/Integration 완료/미완료·효율·단기/장기 로드맵·권한**을 독립 복원해 보고한 뒤 **STOP**. 사용자 명시적 **'진행' 이전 문서/코드 수정·커밋·원본 수집·Actions/Native/테스트/공식 승격 전면 금지**.


## 새 채팅 인계 복원 동작 · P3-EN 최종 후속 정본 (2026-11-05)

- **현재 단일 진입점:** [P3-EN](../CHAT_CONTINUITY_HANDOFF_20261105_P3_EN_ENGINE_FIRST.md) / [노트](notes/2026-11-05_p3-en-engine-continuity-handoff.md). P3-EE/DW/DO는 각 시점의 역사 인계이며 삭제하지 않는다. 격리/main 실제 HEAD를 각각 조회 → P3-EN → PROTOCOL → INDEX → P3-EF~EM·선행 P3-DX~ED/DN~DV → CURRENT/실행 노트/승인 v1.4.3 → 실제 원본·코드·Actions/Native를 독립 대조한다.
- 최신 작업 P3-EM의 동일 원본 v266 조인 재사용 **250 PASS**, 이전 P3-EL v212 양 OS **444 PASS/4 SKIP는 역사 범위**. 이는 제품 T1/공식 GJFO·Policy A 발행/READY가 아니다. 최종 목표는 **26 DPS 공통 재사용 가능한 단일 엔진**; 특수 gem 정확 1개 필수, v098 DPS는 환경 READY 이후. 작업 전 Evidence/Integration 분리하고 REUSE/CONNECT/EXTEND/NEW/STOP, 원본·검증 선조회, 논리적 묶음/캐시·효율 점검 필수.
- **새 채팅은 첫 응답에서 복원 보고 후 즉시 STOP. 사용자 '진행' 전 개발·문서/코드 수정·커밋·HTTP/Native/CI/Actions/테스트·공식 승격 금지.** 이 문서 갱신 자체는 Project UI/Work OS/main 적용 증거가 아니다.
