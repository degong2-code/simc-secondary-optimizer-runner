# SIMC SECONDARY OPTIMIZER — P3-HAC 2026-11-09 단일 연속성 인계

**지위:** GitHub 격리 개발 상태의 **읽기 전용 복원 정본**. 새 채팅에서 첫 응답은 독립 검증·목표·장단기 로드맵·미완료를 보고한 뒤 STOP. 사용자의 새 메시지 **'진행' 전에는 코드·문서 변경, 수집, Actions/CI 실행, Native, 커밋·승격을 일절 시작하지 않는다.** 이 문서를 작성한 행위는 Project Sources/Instructions UI 실제 등록, 제품 출시, `main` 병합, v003 immutable, 원본 v016, Work OS M0/Shared State 적용이 아니다.

## 1. 식별·증거 권위·최소 읽기 순서

- 저장소: `degong2-code/simc-secondary-optimizer-runner`; 개발 격리 브랜치: `probe/chat-cache-v035-20261024`.
- **인계 문서 작성 직전 독립 조회:** 격리 HEAD `ec9050e50e3d77f8579c39bc4bff38bd1f950efc`; `main` HEAD `07133e0aaf738d6e4816a6486057b1cd49c018de`. 이 문서를 추가한 커밋은 격리 HEAD를 바꾸므로 **새 채팅은 둘을 별도로 다시 조회**한다. 당시 마지막 기능/시험 HEAD는 P3-HAB `ec9050e5`이며, 마지막 실 Native 영수증은 아래 P3-HY의 검증 범위에 한정한다.
- **읽기 순서:** (0) 격리/main HEAD 각각 독립 조회 → (1) **이 P3-HAC 단일 인계** → (2) `docs/development/PROTOCOL.md` 맨 위 / `docs/development/INDEX.md`의 A3·B1~B3·C1~C4·D1~D3·E1~E3·F1/F2 및 `OPTIMIZER.POLICY`, `PRODUCT.E2E` → (3) `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` **맨 위 2026-11-09/P3-HAB/HAA/HZ/HY/HX/HW 및 HN/HR/HS/HT/HU/HV 항목만** → (4) `docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md` 상단과 승인 `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md`, 사용자 후속 직접 결정 → (5) 이 문서에 나열된 노트·실제 해당 코드/테스트/Actions/Native 원본. P3-HM 이하 인계와 전체 P3 역사 순회 금지.
- 권위: **최신 사용자 직접 결정 > 비충돌 최신 승인 설계 v1.4.3 및 v1.4 계열 > 실제 GitHub 코드·CURRENT·Actions/Native 증거 > 과거 인계/보존 스냅샷.** 첨부 v1.4.1 원문의 '27개 DPS/증강 포함'은 역사 오기. 현재 **26개 DPS 전문화만**, 증강 기원사·탱커·힐러 제외. 문서에 오래된 '미완료'가 남아 있으면 작성 당시 시점의 기록으로 읽는다.

## 2. 하나의 재사용 엔진: 최종 목적과 제품 계약

사용자가 **미래 목표 아이템레벨(기본334, 지원 목표 범위는 실제 최신 코드 확인) 또는 직접 지정한 최종 CHMV 총량 T**를 선택하면, SimC 실제 DPS로 **치명·가속·특화·유연 절대 rating**을 탐색하고 관측 1순위 DPS·SEM·95% 판정·실질적으로 다른 근접 대안·비율을 출력한다. 전역 최적해를 입증하지 못하면 확정이라고 쓰지 않는다. 현재 착용 장비 재분배, 장비 조합 추천, 획득 경로, 전체 시즌 장비 DB 구축, 독자 APL/아이템 효과·proc 시뮬레이터는 제외.

일반 사용자는 직업·전문화·종족·특성, 목표 ilvl/수동 최종 T, 장신구2, 선택 특수효과장비, 장식 최대2, 소켓·보석·영약·음식·물약·증강·무기 기름·전투 조건, 시즌 선택 모듈을 고른다. 대표 일반 방어구·무기·주능력치·티어4/SimC 실행 프로필은 **내부** 생성. SimC 프로필 업로드는 캐릭터·특성 복원용 선택 사항.

**공식 회계:** `G` 대표 일반 장비·무기, `J` 일반보석, `F` 최고품질 영약, `O` 적용 가능한 무기 기름 고정 수치; `B=G+J+F; T=B+O; c_final=c_base+o`. 수동 **최종 T** 우선, O는 비자유분배, 선택 특수장비 고정 `L` 및 영구마부 `E`의 예산 소유권/하한·이중 가산 방지, 장신구 고정 스탯은 자유 G 밖. 일반 보석 최소4종+사용자 선택 특수 1개로 선언 소켓 최소5부터 전부 실제 배치; **효과는 SimC가 직접 계산**, J/효과를 임의 추정하거나 별도 효과 인증 Gate 금지. 동일 시즌 정적 원본은 revision만 바뀌었다고 폐기하지 않고, DPS 캐시는 exact binary·profile·candidate·options·iterations·environment identity별 분리.

**2026-11-08 최신 사용자 스탯 경계:** 최종 기름 포함 `T`의 **각 스탯은 엄격히 50% 미만**: `c_final[s] <= (T-1)//2` (정수), `c_base[s] <= (T-1)//2 - O[s]`. 사용자 fraction이 이를 완화할 수 없음. E/L/O 고정 하한이 제약과 충돌하면 Native 전에 차단. [P3-HAB](development/notes/2026-11-08_p3-hab-strict-final-half-rating-cap.md).

**2026-11-08 직접 최적화 결정:** 6회의 v094 SimC 후보 평가는 **환경·접합·정적/통계 로직의 작은 smoke 시험**, 제품의 탐색 상한 아님. 실사용은 수백~수천 후보의 효율 높은 **global coverage → noisy multiscale local search → 선택적 95% 정밀 확인/근접 대안**, 재사용형 영속 실행기/캐시·중지/재개/예산/시간 종료. 2,000 **Native 후보 호출**은 2,000 **iterations**와 구별하며 목표 소비량이 아니라 사용자 설정 최대 예산이다. 새 효과 메커니즘·APL 재구현 금지.

## 3. 제품 영역별 실제 완료 vs 미완료

| 영역 | 최신 실증/재사용할 함수·증거 | 범위·남은 문제 |
|---|---|---|
| A: 시즌 데이터·캐시·봉인 | `v161/v229/v191/v211/v213/v217`와 별도 정적·DPS 캐시. 시즌/패치 same-content 정적 재사용 [P3-FX]. | 다음 신규 시즌 G/J/F/O 원본 확보~등록을 26개 전부 자동 완료했다고 주장 금지; Project UI 미확인 |
| B: 대표 장비·G/주스탯·티어 | `v230/v232/v277/v216`. 정확 빌드 **12.1.5.70783**, ilvl334 Ret/Enh 실제 Native 사례의 G2850. 고양 JSON2에서 티어 2pc/4pc, 민첩·레이드 버프 실 관측 [P3-HT]. | 다른 전문화/ilvl·선택장비의 정확 G, L/E/O 옵션별 실 입증 범위 구분; G2850 보편값 아님 |
| C/D: 소켓 J·영약 F·O/모듈 | `v271/v278/v281/v108`, 특수1+일반4 → J92; flask ItemID241324 F165; 현재 고양 Windfury/Flametongue로 oil OFF O0. 기존 [P3-HU] food/potion/augmentation/Omnium 실 JSON2. | 최고품질 UI/Policy A·다른 소비품·기름 유효 무기 조건은 적용 범위별 검증; 새 시즌에 J92/F165 복사 금지 |
| E: 환경 예산·설치 | `v216→v222→v212/v217` 실제 `environment_ready=true,installed=true`, **G2850/J92/F165/O0/B=T3107** 한 시즌/한 ilvl 조건 [#42460255527](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42460255527). | 미래 시즌 전 과정과 다수 전문화 READY는 아직 전면 실증 아님 |
| F: 사용자 SimC DPS | `v098→v096→v094` Ret 실 E2E [#42466284163](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42466284163) ~159089±258; Enh 소모품/Omnium ON 실 E2E [#42472633337](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42472633337) ~182928±282, Native6·실 JSON2 tier/raid/consumables 감사. 기존 26 DPS/타 ilvl의 역사 Native도 INDEX 증거 적용 범위 내 재사용. | **관측 1위/95% 확인 pair는 전역 최적 아님**, 웹 사용자 입력→장기 Start/취소·재개/후보 대안 최종 완성 별도 |
| G: 생산형 최적화 | `v290_multiscale_adaptive_policy.py` (순수 제안), `v291_durable_multiscale_native_runner.py` (기존 v093→v065/v091 Native 평가·SHA 봉인/JSONL/checkpoint/replay). [#42482151972](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42482151972) **v291 Native2+재개1+cache-only0** 실제 성공. `stage_extended_manifest`와 합성 9후보/2000 예산 [#42482697729](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42482697729), `v290` history extrema 1회 개선 [#42484953240](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42484953240). | **>6회 실제 연속 Native 탐색 NOT_RUN**. 2000은 typed/synthetic 설정, 실 Native 전수·수렴·속도/DPS 향상 입증 아님. v291은 scout/confirm 두 iteration 유형만, v290 제안의 더 높은 정밀화 iterations와 계약 간극 존재 |

위 행의 과거 특정 PASS는 해당 환경·바이너리·프로필·조건·SHA 범위에서만 재사용. 역사 실패/기존 증거를 부당하게 삭제하거나 동일 조건 Native 전체 반복 금지.

## 4. 인계 직전 최신 커밋과 검증 영수증

- 개발 격리 최종 기능 HEAD `ec9050e50e3d77f8579c39bc4bff38bd1f950efc` (**P3-HAB 정수 strict <50% cap 및 역사 v202 fixture 수정**). 이전 기능 `da00bcda` P3-HAA(지연 rescanning 제거), `49a86ae9` P3-HZ typed longrun 소스 준비/Native3 영수증, `b0be8254` P3-HY 실 2+1. **이번 인계 문서 커밋은 새 기능·Native 결과를 만들지 않는다.**
- 최신 offline [#42486217556](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42486217556) **462 tests 실행, 460 PASS/2 SKIP, 0 FAIL**, `DEV_LEDGER_PASS`, **Native0**. [#42485996396](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42485996396) 460 PASS/2 SKIP. 별도 [v202 #42485996335](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42485996335) 11 PASS, [v182 #42485996603](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42485996603) SUCCESS, [v181 #42485996329](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42485996329) SUCCESS. 최초 3 FAIL은 옛 62.7% fixture가 strict cap 위반한 것으로, 교정 후 PASS; 실패 영수증 보존.
- **실 Native:** [P3-HN READY #42460255527](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42460255527), [P3-HR DPS Ret #42466284163](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42466284163), [P3-HU Enh full consumables #42472633337](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42472633337), [P3-HT exact DPS JSON2 #42470887863](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42470887863), [P3-HV axis coverage #42475536108](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42475536108), [P3-HY v291 Native3 #42482151972](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42482151972) 및 artifact **13618226243**. P3-HY 3개 중 `(1,165,1,2940)`와 `(1,165,2940,1)`는 **그 뒤 승인된 strict 50%-미만 정책 위반**이므로 현재 적합 후보·결과로 재사용하지 않는다. 이 실행은 정책 변경 *전* Native 경로·재개 확인 역사 증거일 뿐, 새 strict cap 하의 실제 Native PASS가 아니다.
- 가장 최근 실측 성능 변화가 검증되었다고 과장하지 말 것. 이전 다른 Native6과 DPS 숫자 차이는 독립 확률 시뮬레이션 비교이며, 95% 전역 우위 증거가 아니다.

## 5. 가장 가까운 병목 / 중복 방지 의사결정

1. **P0 — 새 정책 기준 장기 Native 검증:** 선행 검사로 최신 HEAD의 v061 strict cap·v065 bounds·v063 injection·v290 proposer·v291 recorder를 짧게 대조한다. 기존 동일 시즌 검증 바이너리/시즌 환경, SHA cache, source manifest를 재사용해 **최종 50% 미만 후보**로 독립 v291 세션을 시작한다. 이전 P3-HY의 2940-rating 케이스를 현 적합 세션에 재생하지 않는다. 첫 7~12 후보 Native를 계획된 일괄 예산 내에서 실행하고 JSON2 rating/primary, tier/raid/consumables·원본 입력 SHA·replay0·취소/재개를 검증. 총 2000을 처음부터 소모하지 않는다.
2. **P0 — v290↔v291 iteration ladder 일치:** 현재 v290 `_precision_action`는 `confirmation_iterations` 초과 배수 iteration을 계획할 수 있으나 v291 `_mode`는 두 단계(scout/confirm) 정확 identity만 허용. 새 자체 SimC scheduler 대신 **기존 typed budget·cache identity 확장** 또는 두단계 정책적 clamp를 설계하고, 유효하지 않은 후보/정밀화 Native 반복을 차단.
3. **P1 — 효율·통계:** 네 스탯 3자유도에서 coverage, 다양성, DPS 개선량/**SimC CPU-second**·Native 호출·iterations·SEM·95%/다중비교 승자 편향·의미 있는 분배 대안을 같은 예산으로 벤치마크. 전역 최적 증명 불가를 결과에 표시; 수렴·시간·사용자 예산 종료를 명시. 대형 반복은 현 후보 정책과 재개형 엔진을 먼저 활용, 새 효과 Gate 금지.
4. **P1 — 일반 제품 단일 경로:** 검증된 시즌 G/J/F/O/기름·수동T·L/E 및 최고품질 사용자 선택지 → 기존 `v098/v096` 승인 manifest → opt-in v291 장기 작업/진행·취소·재개·SHA 캐시 → DPS/SEM/95%/관측1위/근접대안 UI. 기존 `v113` 웹·Windows 빌드 활용; 새 범용 UI/엔진 중복 제작 금지.

**효율적 대안:** 전체 코드를 다시 짜거나 26전문화×모든 ilvl×2,000 Native 일괄 실행하는 대신, strict-cap 호환을 먼저 점검하고 **하나의 source-locked 고양 또는 징벌 세션**으로 7~12회/취소·재개를 검증한 다음 동일 예산 하 비교, 문제가 난 최소 컴포넌트만 수정한다.

## 6. 장기/단기 로드맵 및 완료 판정

- **단기:** (1) 정책/실행기 iteration identity·strict cap 맞춤 → (2) 진짜 >6 Native+중단·재개·캐시·통계 교차증거 → (3) 런타임/품질 비교와 적응형 종료 → (4) 일반 사용자 입력·시즌 선택지·웹 Start/Cancel/Resume 결과 통합.
- **중기:** 시즌 자동 원본→G/J/F/O·E/L/보석/기름→B/T→Policy A 검증 최고품질 옵션 발행→v212 READY 설치→v291 장기 SimC를 **한 계약**으로 완성. 증거가 있는 전문화/다른 ilvl만 증분 실측.
- **장기:** 다음 확장팩/시즌에도 동일 재사용 엔진이 바뀐 시즌 원본만 새로 확보하고 기존 정적 캐시/효과/SimC 책임을 분리한 채 **26개 DPS 전문화**에 제공. 제품 완성 기준: 실제 사용자 조건에서 최종 절대 rating·통계/대안·진행/중지/재개/캐시·오류 원문/결과 재열기가 동작. 실 Native 증거 없는 전수 지원 주장 금지.

**모든 작업 공통:** 먼저 INDEX의 관련 기능/기존 source·cache·코드·실제 영수증 검색 → `REUSE/CONNECT/EXTEND/NEW/STOP` 명시 → 독립 작업을 묶되 최소 변경 → 동일 검증 기준(오프라인 회귀, 해당 Native subset, source/JSON2 SHA, 환경 READY, 캐시·취소/재개, 95% 적용 범위) 재사용 → **구현 완료/새 PASS/역사 재사용/미구현을 분리**하여 CURRENT·INDEX·작업 노트를 갱신. Native·중복·I/O·메모리·실시간/CPU·구조 복잡도 검토.

## 7. 권한·반영 구분

- 본 인계의 GitHub 문서·PROTOCOL·INDEX·CURRENT·개발자 실행노트 갱신은 **격리 브랜치 개발 문서 범위**이다. 만약 실제 업데이트 결과가 존재하지 않으면 수행했다고 주장하지 않는다.
- 승인 v1.4.3 원문·ChatGPT Project Instructions/Sources UI, `main`, immutable v003, 원본 제품 v016, 공식 Work OS M0/Shared State, WEQUIP 운영 authority는 임의 변경·승격하지 않는다.
- 주 제품 개발 소유권을 다른 채팅/MAIN/WORK가 무단 이전받지 않는다. **이 새 채팅은 현재 상태를 독립 복원하는 읽기 전용 단계**로 시작하며 사용자가 별도로 `진행`이라고 하기 전 실행하지 않는다.

## 8. 새 채팅 첫 메시지 — 그대로 복사

> SIMC SECONDARY OPTIMIZER를 **읽기 전용으로 독립 복원**해. GitHub `degong2-code/simc-secondary-optimizer-runner`, 격리 브랜치 `probe/chat-cache-v035-20261024`, 최신 단일 인계 `docs/CHAT_CONTINUITY_HANDOFF_20261109_P3_HAC_MULTISCALE_ENGINE_RESTORE.md`. 먼저 격리 브랜치 HEAD와 `main` HEAD를 각각 독립 조회하고 인계의 작성 직전 HEAD와 대조해. 읽기 순서: 이 인계 → `docs/development/PROTOCOL.md` 상단 → `docs/development/INDEX.md` 관련 영역 및 OPTIMIZER.POLICY/PRODUCT.E2E → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 최상단 → 승인 v1.4.3/개발자 실행 노트 → 실제 해당 코드·최근 Actions/Native SHA 영수증. 과거 자료 전체를 처음부터 감사하지 말고 기존 기능/원본/캐시/CI·Native를 먼저 검색하여 증거 재사용 범위와 제품 연결 미완료를 구분해. 최신 직접 결정의 **26 DPS, 시즌 G/J/F/O 자동 구성과 T/B, 5+ 소켓, 기름/L/E/O, 최종 각 스탯 50% 미만, 6회는 smoke이고 실사용 장기 v290/v291 알고리즘을 개발**한다는 기준을 적용해. 목표는 개별 기능이 아닌 다음 시즌도 재사용 가능한 **하나의 엔진 완성**이며 매 작업 전 선조회, 독립 작업 묶음 처리, 동일 완료 검증/기존 증거 재사용, 불필요한 Native·재수집·새 Gate 금지를 자가점검해. 첫 응답에는 독립 복원 결과, 실제 HEAD, 검증된 완료/미완료·병목 및 장단기 로드맵과 **더 효율적인 다음 작업 대안**을 간결하게 보고하고 그 즉시 중단해. **내가 '진행'이라고 말하기 전에는 코드/문서 수정·개발·수집·GitHub Actions/CI/Native/테스트 실행·커밋·main 병합·Project UI/Work OS 승격을 일절 시작하지 마.**
