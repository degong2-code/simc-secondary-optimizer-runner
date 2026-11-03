> **2026-11-03 P3-BX 소켓 자동 발견 규칙:** SimC C++ 기본 `socket_color[]`와 `ITEM_BONUS_SOCKET` type6는 해당 아이템 및 실제 `bonus_id`가 제공하는 소켓 개수를 판독할 수 있다. 하지만 실제 [Native 4/4 반례](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696): 소켓 선언 없는 가슴에 `gem_id`만 지정하면 Crit+16/Haste+8 적용, 1소켓 ID 13750을 가슴/어깨에 강제 부착해도 정상 실행. 따라서 **SimC 실행 성공만으로 게임 소켓 구성 유효성을 승인하지 말 것**. 새 시즌의 소켓 추가 수단이 적용 가능한 장비 부위/조건만 작게 환경 자료로 확정하고, 아이템 기본/변형 소켓 수 + 사용자 최종 선택을 기존 대표 프로필/J에 연결. 6~7개는 이번 시즌 사례일 뿐 엔진 상수가 아님. [P3-BX 노트](development/notes/2026-11-03_p3-bx-simc-socket-native-contrast.md).
>

> **2026-11-03 최신 통합 원칙 (P3-BW):** 보석·영약·음식·기름·영구 마부의 효과 수치 책임은 SimC에 있다. 신규 시즌에는 과거 J/F/O·무기당 16/16을 복사하거나 DB2 EffectPointsMin을 SimC 최종 rating으로 추정하지 말 것. 기존 v198 Native 비교 및 v269 SimC JSON2 precombat 정적 CHMV 관측을 재사용하고, 고정 rating이 실제 존재하는 경우에만 v222 회계의 소유 스탯으로 연결한다. Proc/조건부 효과는 재구현하지 않음; 선택 아이템·품질/적용 손은 원본 정확 ID·SimC 토큰으로 결정. 추가 마부 CSV 소스는 기본 다운로드하지 않으며 필요 시 opt-in. 중복 소스/Native Gate 만들지 않음. 재사용 가능한 최신 오프라인 자동 CI [#41594997300](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41594997300) 38 PASS/0 FAIL은 **해당 집중 테스트 범위**만 증명한다. [P3-BW 노트](development/notes/2026-11-03_p3-bw-simc-json2-effect-rating-delta.md) 및 [INDEX](development/INDEX.md) 선조회.
>

> **2026-11-03 최신 사용자 직접 설계 교정 (P3-BU, 역사 v1.4.3 비충돌 유지):** G는 **목표 ilvl별 대표 일반 장비의 보조능력치 정적 총량**이며 *현재 시즌 획득 여부는 수치 적합성의 필수조건이 아니다*. 동일 ilvl/해당 슬롯·무기 구조의 무효과 일반 장비로 구성하고 SimC Native 정적 합계를 10 rating 단위 반올림한다. 주스탯(힘/민첩/지능), 방어구 재질, 직업/전문화 착용 가능, 무기 형태, 비특수효과·일반 보조능력치 예산은 반드시 확인한다. WSE/Localbots/과거 시즌 소속 미확정은 **G 거부 사유가 아니라 실제 SimC 대표 프로필의 출처·안전 우선순위 기록**이다. 현재 시즌 장비가 있으면 SimC 안정성상 우선 사용하지만 신규 시즌 인증 Gate를 추가하지 않는다. 실전 티어4세트·효과·선택 특수장비·장신구는 계속 정확한 SimC 입력이 필요. `v232→v233→v234→v216→v262/v222` 기존 체계 사용, G numerical fit과 전체 G/J/F/O 및 최종 제품 READY를 구별. [P3-BU 노트](development/notes/2026-11-03_p3-bu-generic-g-physical-not-season-gate.md)·[INDEX](development/INDEX.md) 선조회 필수. 이번 반영은 격리 브랜치 GitHub 문서·코드일 뿐 Project UI/Sources 실제 적용이나 main 승격이 아니다.
>

> **2026-11-03 P3-BQ 최신 인계 정본(이전 P3-BO 역사 인계보다 우선):** [CHAT_CONTINUITY_HANDOFF_20261103_P3_BQ_EVIDENCE_FIRST_LEDGER.md](CHAT_CONTINUITY_HANDOFF_20261103_P3_BQ_EVIDENCE_FIRST_LEDGER.md). 모든 새 채팅은 위 [개발 연속성 규약](development/PROTOCOL.md)과 [증거/연결 분리 INDEX](development/INDEX.md)를 이전 미완료 목록보다 먼저 읽고, 새 개발 착수 전 관련 과거 소스·코드·검증 영수증을 검색한다. 완료 사실이 제품에 미연결된 것과 원본 사실 미확정을 구별하고, 작업마다 짧은 노트와 INDEX를 갱신한다. 이전 P3-BO 인계는 역사 스냅샷이며 이 문서 포인터가 최신이다.
>

> **2026-11-03 최신 사용자 직접 개발 효율 교정 — 인계·개발 노트 영구 적용:** 코드/검증 작업 전 **[개발 연속성 규약](development/PROTOCOL.md) → [기능별 증거·미완료 INDEX](development/INDEX.md) → 해당 원본/Actions 영수증 → 관련 코드** 순서로 확인한다. **[P3-BQ 실제 교정 기록](development/notes/2026-11-03_p3-bq-continuity-correction.md)**이 선례. `false/PENDING`은 과거 원본 증거 부족과 현재 제품 연결 미완료를 구별하지 못하므로 그대로 신규 조사 명령으로 삼지 않는다. 기존 시즌 티어 **기초 ilvl 197/219×65, 현재 레이드 그룹 101/118, SimC 정확 13직업×5부위** 재사용, 새 인증 엔진·Native/원본 재수집 기본 금지. **논리적 작업 묶음마다** 원본/상태 선조회→REUSE/CONNECT/EXTEND/NEW/STOP 결정→짧은 구조화 GitHub 노트 1개와 INDEX 갱신→인계 반영 필수. 해당 규약을 새 채팅에서도 먼저 읽어야 한다. `python tools/check_development_ledger.py`(선택 `--since TASK_BASE_REF`)로 구조와 작업 변경 대비 노트 누락 점검. 본 교정은 개발 운영 규약이지 새 제품 READY/효과 인증 Gate가 아니며 GitHub 기록이 Project UI 적용 증거도 아니다.
>

> **2026-11-03 최신 실행·새 채팅 인계: [P3-BO 단일 정본](CHAT_CONTINUITY_HANDOFF_20261103_P3_BO_ENGINE_GJFO_NEXT.md).** 아래 P3-BF/P3-AT 인계 포인터는 역사 안내. 최신 사용자 선택 입력은 종족 미입력 `dwarf`(직업 불가 시 명시 종족 필요), 특성 미입력 기존 대표, 일반 `level=` 생략/SimC MAX_LEVEL; 장비·소모품·기름·영구 마부 및 G/J/F/O는 우리 환경 엔진이 관리. P3-BO는 v216의 기존 v189/v190 음식/물약 소스 후보 연결 및 430/206/142/UI 합성 CI 범위 PASS까지만, 실제 G/J/F/O→B/T→정책 A→READY·DPS E2E는 미완료. 이전 WSE 전용 연구/레벨 자체 추론/별도 최적화 엔진을 다시 시작하지 말 것. 독립 G·J/F/O는 묶어 처리하되 검증은 독립, 기존 영수증과 같은 완료 기준 재사용. 최초 새 채팅에서는 읽기·복원·검증만 하고 사용자 **"진행"** 전에는 구현·Actions·Native·원본 수집 금지. 승인 v1.4.3 본문, main/v003/v016/Project UI/Work OS 불변.
>
>
> **2026-11-03 새 채팅 최신 실행 인계 (P3-BF, 승인 설계 본문 불변):** [CHAT_CONTINUITY_HANDOFF_20261103_P3_BF_ENGINE_GJFO_NEXT.md](CHAT_CONTINUITY_HANDOFF_20261103_P3_BF_ENGINE_GJFO_NEXT.md)가 이 파일에 남은 P3-AT/P3-AF/v221 인계 포인터보다 최신이다. 실측 P3-AT→BA Wago·SimC 출처, 같은 시즌 SimC 버전 변경의 정적 DB 유지, P3-BE v212와 P3-BF v106 세션·실행 revision 분리 및 실제 Actions 409/194/139/focused2 PASS를 구별한다. **완료하지 않은 핵심은 동일 시즌 대표 G/J/F/O 전체 자동 산출/검증 → 기존 v222 B/T → 정책 A 최고 품질 선택지 → 정상 사용자 환경·대표 프로필 → 기존 적응형 SimC DPS/SEM/95% E2E**. 최종 목표는 **반복 가능한 범용 Environment DB 구축 엔진**이지 시즌별 기능 수작업이 아니다. 독립 수집/검증은 효율적으로 묶되 출처·예산·UI/Native 완료 판정은 분리하고, 동일 검증 기준과 기존 source/cache/Native 영수증을 재사용한다. 매 변경마다 HTTP/Native 중복·캐시·메모리·I/O·실행시간/구조 단순화 점검. **새 채팅 첫 응답은 복원·검증 보고 후 중단하고 사용자 ‘진행’을 기다림**. 이 갱신은 GitHub 개발자 노트 포인터만 변경하며 승인 v1.4.3 정책 내용/Project UI·main·Work OS 승격·신규 Native 실행을 뜻하지 않는다.
>

> **최신 실행·연속 개발 인계 포인터 (2026-11-02 P3-AT):** [CHAT_CONTINUITY_HANDOFF_20261102_P3_AT_SIMC_TO_GJFO_ENGINE_NEXT.md](CHAT_CONTINUITY_HANDOFF_20261102_P3_AT_SIMC_TO_GJFO_ENGINE_NEXT.md)가 이 파일에 남아 있는 P3-AF·v221 당시 인계 안내보다 최신이다. 한 Build에서 기존 v229 실제 SimC source 7→0 HTTP·v251 exact-ID 후보 연결까지 완료되었으나 대표 일반장비 시즌 근거/G/J/F/O·B/T·사용자 Start E2E는 미완료. 새 채팅 **첫 턴 복원 보고만**, '진행' 전 구현·Actions·Native 중지. 승인 설계·개발 소유권·권한 정책 변경 없음.

# SIMC SECONDARY OPTIMIZER — 개발자 실행 원칙 보충 (2026-11-02)

> **새 채팅 인계 정본 갱신(2026-11-02, P3-AF):** [CHAT_CONTINUITY_HANDOFF_20261102_P3_AF_V216_TO_FRESH_BUILD_NEXT.md](CHAT_CONTINUITY_HANDOFF_20261102_P3_AF_V216_TO_FRESH_BUILD_NEXT.md)가 P3-AB→P3-AC→P3-AD→P3-AE 연속 개발 이후 최신 복원 순서·실물 HEAD·증거/미구현·시작 프롬프트를 소유한다. 아래에 남은 “v221·P3-L 인계에서 단일 관리”는 당시의 역사적 안내이며 최신 정본을 대신하지 않는다. **다음 첫 복원 응답은 읽기/검증/보고만 하고 사용자 '진행' 전 코드·Actions·Native 수정·실행 금지.** 이후 일반 Build 요청에 신규 source fetch→기존 v191→v211→v213→v196→v216, G/J/F/O→v222→v212·v098를 **같은 엔진**으로 이어가며 과거 v216의 정상 미완료 차단을 우회하지 않는다.

> **최신 사용자 직접 교정 / 단일 엔진 통제실험 (2026-11-02):** [P3-AA](P3_AA_20261102_SINGLE_ENGINE_FRESH_SEASON_CONTROL_ACCEPTANCE.md), [v1.4.3 최신 §7](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)을 최우선으로 읽는다. 최종 시험은 정상 실사용 **같은 Environment Build 엔진**을 현재 시즌에 대한 **기존 데이터·캐시·영수증 없이** 실행하는 것이다. Wago DB2·Blizzard·WCL·공개 GitHub·SimC의 **신규 원본 수집은 허용**한다. 이전의 "SimC-only 최종 시험" 또는 외부 네트워크 차단 해석을 반복하지 않는다. v229~v237은 제한된 조사용 부품이며 별도 최종 제품 엔진을 만들지 않는다.

> 승인 설계 원본 [v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)의 내용을 변경하지 않는 **실행/인계용 보충**. 최신 작업 상태와 새 채팅 프롬프트는 [v221·P3-L 인계](CHAT_CONTINUITY_HANDOFF_20261102_V221_P3L_ENGINE_FIRST.md)에서 단일 관리한다. 구형 v216 인계는 역사 자료다.

## 유일하게 가장 중요한 자가검증 원칙

**프로그램의 특정 기능을 넣는 데 집중하지 말고, 그 기능을 지속적·반복적·검증 가능하게 구현하는 엔진을 만들어라.**

시즌 아이템별 정적 예외/수동 등록/별도 SimC 효과 계산/새 최적화 엔진/중복 collector/profile generator가 늘어나면 설계 이탈 여부를 먼저 평가한다. 원본 취득 → source identity/버전 → 타입화 정규화 → 정확한 관계 검증 → 승인 자동 등록/보류 → 시즌 예산(G/J/F/O)/B/T → 기존 profile/SimC 실행으로 이어지는 공통 엔진을 강화한다. 새 기능 하나는 동일한 규칙이 다음 시즌과 다른 아이템에도 적용될 수 있어야 한다.

## 작업 묶음 및 증거 재사용

- **독립 작업은 묶어 처리**해 GitHub 호출·빌드·검증을 줄이되, 크거나 복잡한 작업은 감사 가능한 패치/시험 경계로 나누어 실패 위치가 보이게 한다. 무조건 모든 작업을 한 번에 또는 한 번에 하나만 하는 방식 모두 지양.
- 동일한 입력 계약·검증 로직·완료 판정은 재사용하며, 기존 Native·cache·Actions 영수증이 유효한 범위에서 시험 반복 금지. 초도 실패와 수정 후 PASS는 구별.
- 매 코드 변경은 기능적 정확성 **및** 네트워크/Native 호출량, 중복 실행, 캐시 무효화 범위, 메모리, 파일 I/O, 시간, 구조 단순화·전체 사용자 소요시간을 검토한다.
- 구현 완료/오프라인 PASS/실제 Native PASS/재사용한 역사 영수증/미구현/정책 승인/Project Sources 적용을 **별도 상태**로 기록. source row나 handler 검출을 사용 가능 아이템/효과 인증 완료로 승격하지 않는다.
- 새 시즌 G가 확인되지 않으면 Environment Build 정상 완료를 선언하지 않는다. 선택 옵션만 불완전하면 그 옵션만 보류. 기본 대표 입력·G/J/F/O/CHMV 정합성은 필수.
- SimC의 proc/효과/APL/DPS 책임은 유지한다. 오직 정확한 ID/ilvl/조건, Native JSON2 정적 rating, budget/고정치, DPS·SEM·95%, 실행·결과·캐시를 우리 코드가 맡는다.

## 개발 순서의 효율적 기본값

**같은 시즌 source/예산 identity → G/J/F/O 자동 산출/검증 → B/T 재계산 → 검증된 최고 품질/정확한 조건의 정책 A 자동 등록 → 사용자별 대표 프로필→기존 적응형 SimC→결과/취소/재개.**

이미 구현된 v191→v211→v213, v220/v221, v089/v091/v108, v098, v212/v216/v217/v218, v093/v094/v095를 우선 재사용한다. **현재 구현된 데이터·검증과 앞으로의 목표를 혼동하지 않는다.**

새 채팅에서는 실물 상태 복원·증거 대조·첫 보고까지만 하고, 사용자의 **“진행”** 이후에만 구현한다. GitHub 격리 브랜치 한정 개발 소유권 및 main/immutable/Project UI/Work OS 보호 경계 유지.
