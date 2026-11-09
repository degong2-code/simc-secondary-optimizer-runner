# SIMC SECONDARY OPTIMIZER — P3-HAU 단일 새 채팅 인계 정본 (2026-11-09 KST)

**지위:** GitHub 격리 브랜치의 최신 실제 상태를 읽기 전용 대조한 인계. 이전 P3-HAT 정본을 *대체하는 최신 진입 포인터*이지 과거 A~G 기록/승인 정책/영수증의 삭제·재승격이 아니다. 이 인계 작업은 문서 변경만; 코드·Native·테스트 새 실행 없음. GitHub 파일 작성 ≠ ChatGPT Project UI 적용/Work OS 공식 승격/main 병합.

## 1. 독립 HEAD 기준·최소 읽기 순서

- 저장소 `degong2-code/simc-secondary-optimizer-runner`; 격리 `probe/chat-cache-v035-20261024`.
- **인계 전 실제 독립 HEAD:** 격리 `0686f0b8cfe63ff68d7d796d08e8eb02682232a8`, `main` `07133e0aaf738d6e4816a6486057b1cd49c018de`. 이 문서를 커밋하면 격리 HEAD가 이동한다. 다음 채팅은 **두 ref 각각 독립 조회** 후 이 기준과 최신 compare/Actions를 재검증한다.
- **읽기 순서:** ① 본 단일 인계 → ② [현재 판정 P3-HAI](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md) 최신 보충 + A~G 표 → ③ [PROTOCOL](development/PROTOCOL.md) + [INDEX](development/INDEX.md) 기능별 재사용 기록 → ④ [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 최상단 → ⑤ [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) + [실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md) + 최신 사용자 직접 결정 → ⑥ [이 인계의 증거 대사](development/notes/2026-11-09_p3-hau-handoff-evidence-reconciliation.md) 및 [P1 기름 엔진 기록](development/notes/2026-11-09_p1-oil-70783-precombat-gear-source-bridge.md), [P3-HAR](development/notes/2026-11-09_p3-har-user-manual-t-real-native-probe.md), [P3-HAS](development/notes/2026-11-09_p3-has-current-season-oil-zero-ui-default.md), [P3-HAO](development/notes/2026-11-09_p3-hao-p1-value-first-verification-economy.md), [P2-OPT](development/notes/2026-11-09_p2-opt-reliability-first-open-search-policy.md) → 변경된 실제 코드·Actions/Native 영수증만.
- 우선권: **최신 사용자 직접 결정 > 승인 설계 > 실제 GitHub 코드·CURRENT·Actions/Native > 과거 인계/영수증**. 특히 과거 v1.4.1의 27 DPS/증강 포함, 구 시즌 J138·F165·기름16/16 일반화, 과거 웹 HTTP422·O>0 미연결 서술은 역사이다. 현재는 **26 DPS, 증강·탱커·힐러 제외**.

## 2. 제품의 유일한 최종 목적·회계

**하나의 재사용 가능한 엔진:** 미래 목표 ilvl(기본334) 또는 사용자가 지정한 **기름 포함 최종 CHMV `T`**에서 26 DPS 전문화의 SimC DPS를 최대화할 **치명·가속·특화·유연 절대 rating**을 찾는다. 예상 DPS/SEM/95% 우위 확정 여부·관측 1순위·실질적으로 다른 근접 대안·비율, SHA 캐시·진행·취소·재개·로컬 웹 실행을 제공한다. 사용자 입력은 직업·전문화·종족·특성, ilvl 또는 수동 T, 장신구2·선택 특수장비·장식 최대2·시즌 검증 보석/영약/기름·전투 조건; 대표 일반 장비·무기·티어4·주능력치는 엔진이 만든다. 현재 착용 장비 재분배, 장비 조합·파밍 추천, 전 시즌 아이템 전수 DB는 목적이 아니다.

- `B=G+J+F`; `T=B+O`; `c_final=c_base+o`, **O는 적용 손에서 한 번만 반영/자유분배 불가**. 사용자 수동 T 우선 `B=T−O`, 정확한 L/E 하한·고정치 중복 금지, 각 최종 rating은 **엄격히 T/2 미만**. 장신구 정적 스탯은 자유 G 밖; 제작 초기 50:50 배분은 L이 아님. O0 기본 환경은 선택적 O 미검증으로 차단하지 않는다.
- 새 시즌에는 대표 장비·무기·티어와 **G/J/F/O 모두 새 빌드의 원본/증거로 구축**하고 B/T를 갱신. 검증된 최고 품질/동일효과만 정책 A로 추가 수동 승인 없이 등록. 일반 임시 마부 제외, **무기 기름**은 별도 지원; DK 영구 룬벼리기는 원본 기반 선택. 시즌 특수 콘텐츠는 선택 모듈. 기존 시즌 수치나 cache를 다음 시즌 검증값으로 복사하지 않는다.
- SimC가 장비 효과/proc/APL/DPS를 계산. 별도 효과 인증 Gate, 기름 자체 스케일링/직업 특성 효과 재구현 금지. 결과의 **95%만** 사용, 관측상 우위 ≠ 통계 우위 ≠ 전역 최적 보증. P2 탐색 알고리즘·step/L1/종료 규칙은 바꿀 수 있다; **발견 충분성·누락 위험·결과 신뢰성**이 CPU 시간보다 우선.

## 3. 엔진 A~G 최신 실증·미완료 (과거 HAI 표와 병합해서 읽을 것)

| 기능 | 현재 재사용 가능한 구현·실증 | 끝나지 않은 부분/증거 한계 |
|---|---|---|
| **A 시즌 원본·G/J/F/O·B/T·정책A** | 기존 v161/v191/v211/v213/v216/v222/v212/v217; [실 70783 Ret334 환경](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42460255527) `G2850 J92 F165 O0 B=T3107`, Native3, v212 READY. 선택 O 관련 v281/v286/v296/조건부 v297 소스 소유자→동일 v222/v212 설치 코드 추가 | 새 시즌 전체 G/J/F/O 자동 구축의 최초 완전 사용자 흐름, 선택 O>0 실제 검증 설치·다품종 최고 품질 자동 등록 **미실증** |
| **B 대표 장비·DK/26 DPS** | [26/26 기본 물리 프로필 SimC 수용](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357). DK 현 70783 [SimC 원본 룬 ID 7개·캐시 재조회0](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42573280844) 및 [냉기/부정 명시 룬 각1 Native PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42574047929); 시즌 룬 웹 고정 ID 제거 | DK 기본 룬 자동 선정·실 사용자 DK 전체 최적화·26/26 웹 장기 DPS **미증명** |
| **C 보석/기름/L/E/옵션** | 현 실 70783 기본 J92/F165/O0. 기름 품질2 Phoenix Oil 주무기에서 [SimC *precombat total gear* OFF/ON Native2](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42582755601) **치명+16/가속+16**(해당 빌드·프로필 한정). **과거 냉법 buffed 16/17은 O 근거 제외**. v281 물리ID/품질, v286 무기·손, v296 원본, v297 조건부 precombat Native/기존 v278 SHA 캐시 → v216 source owner. 검증 손·아이템 ID 일치 필요 | 16/16을 모든 기름·시즌 상수로 승격 금지. 사용자가 O>0 선택해 v216→v212 설치·프로필·DPS 실 E2E, L/E 및 일부 사용자 옵션 연결, 기름 종류의 **일반 사용자용 목록** 미완료 |
| **D 웹/수동 T/DPS** | [HAR 실 웹→로컬 SimC](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42552942329): Ret334 수동 최종 T3500·O0 → 치834/가998/특834/유834, **DPS171497.55 SEM641.55**, DPS Native2, prepare/run/resume/cache-only/result 성공 | 이 2회는 전역 최적·26전문화·O>0 최종 사용자 실행 증거 아님; 사용자 Windows PC 실제 클릭 미증명 |
| **E 탐색·95%** | 기존 v290/v291/v094, [8×35 scout+2×320 confirm Native10](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42501052586) 기존 확인쌍 제한 증거; 95% 표현 | 전역 탐색 충분성/다봉형 누락·선택편향·결과 신뢰성 우월성 미증명. 2000회/스텝/L1 고정 Gate 아님 |
| **F 설치·캐시·취소/재개** | [v291/v292 교차-job 기존 DPS10 재사용 신규0](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42504040076). 최신 v216/v113: **시즌+ilvl+선택 손별 물리 기름 ItemID+봉인 Manifest SHA** 기반 설치 캐시·세션 복원; 같은 손에 후보 여러 개면 임의 최신 파일 선택 금지, O0/legacy packaged 유지 | 재개·SHA 정체성 코드/오프라인 PASS ≠ O>0 사용자 실 Native·Windows 직접 사용 완료 |
| **G 로컬 웹·사용 UI·제품 조립** | v113 FastAPI, v106/v098/v096, v181 Windows source ZIP·loopback HTTP, v182 UI. 새 시즌 고급 입력에서 기름 **정확한 물리 ItemID**를 손별 전달(브라우저에서 raw O rating/증거 제출 불가). [최신 코드 수정 후 관련 Windows/web/product suite](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42589425679) 성공 | **친화적 기름 품목 dropdown/검증 품질 옵션·O>0 실 웹 DPS 장기 E2E·Windows 사용자의 PC 직접 실행**은 미완료 |

### 최신 수정의 정확한 구분

- [`2db39479`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/2db39479ee5c39224f528ba910499002a124e815) 및 [`49cca1db`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/49cca1db69ce0a6703ba4bf8388d7b6ae579b65f): 별도 특례가 아니라 **기존 시즌 원본·검증 손→v222/v212·수동 T** 선택 O 소유권 연결.
- [`b059e84a`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/b059e84a912712b69525a9936ff11bfbb9ffc378) / [`a97a921d`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/a97a921da21411395229aaa8cbdd44b9a34c1e64) / [`d383bfd6`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/d383bfd6fddc611b69e4036483711abc98103b30): 선택 oil 물리 ID·손·설치·복원·현재 웹 고급 입력의 **범용 identity** 교정. 동일 season/ilvl의 다른 O 설치를 임의로 사용하지 않음.
- `d383bfd6` 최초 web/v177/v180/v181/v182 일부 **FAIL**([예: web #42588929970](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42588929970)): fresh O0 fixture와 구형 packaged 경로를 잘못 묶는 회귀. [`0a97318e`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/0a97318e1d04649115b4e4697a9c38d8b1e8b92f)에서 O0 fixture/legacy 보존 범위만 교정 → [웹 #42589425542](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42589425542), [Windows #42589425679](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42589425679), [v177 #42589425687](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42589425687), [v180 #42589425705](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42589425705) **SUCCESS**.
- **최신 검증 코드 HEAD** `0686f0b8cfe63ff68d7d796d08e8eb02682232a8`: [focused #42589837701](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42589837701) **522 tests = 520 PASS + 2 SKIP + 0 FAIL**, `DEV_LEDGER_PASS`; GitHub에서 **신규 SimC Native0**. 이 CI는 UI 사용자 실제 O>0 DPS 실행 증거가 아님. 기록 전용 `0686f0b8`은 앞선 code `0a97318e`의 동일 기능 상태.
- **코드/테스트 기록은 그 HEAD에 한정**. 이전 시즌 79×2·옛 16/17·초기 웹422/만료 SHA/ZIP은 정식 다음 빌드 근거가 아니며 무작정 다시 측정할 이유 없음.

## 4. 병목 및 짧은 로드맵·효율적 대안

**단기 P1 — 재사용 엔진 사용자 흐름 완결:**
1. **REUSE/CONNECT:** 기존 INDEX·실 코드·source/receipt/cache 선조회. 검증된 시즌 선택 O가 실제 **사용자 입력→v216/v222/v212 정확한 양의 O 환경→v113/v106/v098/v096 SimC profile→DPS/SEM/95% 결과→취소·재개·캐시**로 지나가는지 미연결만 고친다. 이미 준비된 수집·정적 숫자·영수증을 다시 만들지 않는다. 사용자 원본 없는 기름은 보류; 정상 O0 유지.
2. **CONNECT:** 최고 품질·실제 동등효과가 검증된 시즌 기름을 사람 친화적 품목 목록으로 노출하고, 현재 고급 물리 ID 입력은 보조 경로로 보존. L/E/기타 사용자 옵션도 기존 범용 선택 계약에 누락된 곳만 연결.
3. **제품 관점 완료 검사:** 정말 아직 실증되지 않은 통합 경로가 있을 때만 **기존 공통 회귀 + 최소 대표 실 E2E**를 선택. 70783 Phoenix Oil 16/16·DK 두 프로필·HAR T3500·26/26 기본 물리 수용을 반복 입증하지 않는다. 직접 Windows 사용자 PC 완료는 별도.

**중기 P2:** 처음부터 새 최적화 엔진·고정 스텝/L1/종료 규칙을 만들지 말 것. 기존 v290/v291/v094·Native/캐시를 재사용해 **상당히 다른 최적 후보의 발견 충분성·다봉형 누락·95% 선택편향**의 실패 가능성부터 다룬다. 더 나은 탐색법 발견 시 기존 방식 교체 허용. CPU·호출 수·SEM 단독은 성공 척도가 아님.

**장기:** 동일 단일 시즌 Build/최적화/로컬 웹 엔진을 **26 DPS·미래 시즌**에 재사용. G/J/F/O·대표 장비·모듈·옵션 목록만 검증된 새 시즌 자료로 갱신. 원본 v016_SCENARIO_CONTRACT 직접 통합은 원본 바이트·영수증 확인 전 주장 금지; `main` 병합·Project UI/Work OS 별도 사용자 권한.

**매 작업 공통 판단:** `REUSE → CONNECT → EXTEND → REPLACE → NEW → STOP`의 최소비용 선택. **중복 소스/Native·per-item 전용 게이트·바이너리 과거 SHA 재현·매번 전수 26 DPS 시험 금지**. 독립 작업 묶음 처리, 동일 완료 검증 기준/기존 증거 재사용, 변경된 범위만 회귀. 정확성·효과 소유권·캐시 identity를 희생한 빨리 통과는 허용되지 않는다.

## 5. 새 채팅 시작 프롬프트 — 복사하여 사용

~~~text
SIMC SECONDARY OPTIMIZER 프로젝트를 **읽기 전용으로 독립 복원**하라.

저장소: degong2-code/simc-secondary-optimizer-runner
격리 브랜치: probe/chat-cache-v035-20261024
최신 단일 인계 정본: docs/CHAT_CONTINUITY_HANDOFF_20261109_P3_HAU_ENGINE_FIRST_RESTORE.md

우선 격리 브랜치와 main의 실제 HEAD를 각각 독립 조회하고, 인계 준비 전 격리 HEAD 0686f0b8cfe63ff68d7d796d08e8eb02682232a8, main HEAD 07133e0aaf738d6e4816a6486057b1cd49c018de 및 인계 문서 최신 커밋과 대조하라. 최신 diff·Actions 상태를 확인하되 첫 응답에서는 실행/수정을 시작하지 말 것.

읽기 순서: 본 P3-HAU → docs/PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md 최신 보충과 A~G → docs/development/PROTOCOL.md·INDEX.md → docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md → 승인 v1.4.3·실행 개발자 노트·최신 사용자 직접 결정 → P3-HAU 증거 대사, P1 oil 70783 엔진 기록, P3-HAR/P3-HAS/P3-HAO/P2-OPT → 변경된 실제 코드·Native/Actions 영수증/캐시. 이전 단일 인계 P3-HAT는 역사 정본으로 보존.

최종 목표는 개별 기능의 축적이 아니라 **26 DPS를 위한 하나의 재사용 가능한 최적화 엔진 완성**이다. 목표 ilvl(기본 334) 또는 사용자 지정 기름 포함 최종 CHMV T에서 SimC DPS 최대화의 치명·가속·특화·유연 **절대 rating**을 구하고 DPS·SEM·95%·관측 1순위와 실질적으로 다른 근접 대안·캐시·취소/재개까지 제공한다. 효과/APL/proc/DPS는 SimC가 책임진다. B=G+J+F, T=B+O, 수동 T 우선, O는 자유분배 불가/한 번만 반영, L/E 하한, 각 최종 rating<T/2, 기름 없는 O0 정상 흐름은 보존한다.

매 작업 전에 반드시 기존 기능별 INDEX와 개발 기록/원본/실제 코드/Actions·Native 영수증·정적/DPS 캐시를 **선조회**하라. REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP 중 효율적인 방향을 결정하고 독립 작업은 묶어 처리하며 동일 완료 검증·과거 증거를 재사용하라. **'이번 기름'만을 위한 추가 특례 시험이나 Gate, 이미 증명한 16/16 반복 Native, 새 최적화 엔진, 새 시즌 전 아이템·26 DPS 전수 Native 반복을 만들지 마라.** 엔진 전체의 정확성·단순성·중복 호출·CPU·메모리·I/O·캐시 identity와 장기 확장성을 점검하라.

최신 확인: 격리 0686f0b8, focused #42589837701 520 PASS/2 SKIP·ledger PASS, 교정된 v113/web/Windows/v177/v180 #425894... SUCCESS; 그 이전 d383bfd 일부 실패는 역사이며 코드 0a97318e에서 O0/legacy 호환을 교정. 실 70783 Ret334 O0 환경 G2850/J92/F165/T3107 Native3, 수동 최종 T3500 실 웹 DPS Native2 성공 #42552942329(171497.55 DPS, SEM641.55); 기름 품질2 Phoenix Oil 주무기 70783 SimC 전투 전 정적 치16/가16 #42582755601(과거 냉법 buffed 16/17을 O 근거로 쓰지 말 것); DK 룬 원본/한정 Native도 존재. v281/v286/v296/조건부 v297→v216/v222/v212와 v113/v106/v098/v096에 기름 손별 물리 ID·프로필·설치 SHA identity 연결 코드 구현, 최고품질 품목 UI/실 O>0 웹 DPS 종단·L/E 일부·26/26 웹 장기 탐색·사용자 Windows PC 직접 실행 및 P2 탐색 발견 충분성은 미완료. 코드 CI 통과=실 제품 종단 완료가 아니다.

P1: 기존 단일 시즌 환경 Build의 검증된 선택 O→실 사용자 세션→B/T→SimC→결과/재개 연결의 실제 부족한 부분만 정리. 확인된 옵션을 사용자 친화적으로 노출, 미검증 항목은 해당 항목만 보류. P2: 탐색 **결과의 신뢰성·미탐색 개선해 누락 위험** 우선, 특정 거리·스텝·알고리즘·종료 기준은 비구속적. 장기: 26 DPS·미래 시즌으로 동일 엔진 재사용. main, v003 immutable, 원본 v016, Project UI/공식 Work OS/MAIN·주 제품 개발 채팅 권한 보존.

**첫 응답은 복원 보고만 하라.** 실제 HEAD, 최신 승인 정책, 핵심 증거의 적용 범위, 완료/미완료·병목과 더 효율적인 대안, 간결한 장·단기 로드맵을 독립 대조하고 즉시 STOP. 사용자가 별도로 **'진행'**이라고 하기 전에는 코드·문서 수정, 테스트/수집, Actions/Native 실행, 커밋·병합, 승격·Project UI·Work OS 변경을 시작하지 마라.
~~~
