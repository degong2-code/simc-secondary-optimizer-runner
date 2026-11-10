# SIMC SECONDARY OPTIMIZER — P3-HAW 단일 최신 새 채팅 인계 (2026-11-10 KST)

**지위:** 종전 [P3-HAV](CHAT_CONTINUITY_HANDOFF_20261109_P3_HAV_ENGINE_FIRST_RESTORE.md)는 역사 기록으로 보존한다. 본 P3-HAW가 **새 채팅 최신 단일 진입점**이다. GitHub 문서 갱신은 ChatGPT Project Sources UI 등록, Work OS 승격, `main` 병합, immutable `v003` 변경, 원본 `v016` 직접 통합이 아니다.

## 1. 정확한 복원·우선순위

- Repo `degong2-code/simc-secondary-optimizer-runner`, 격리 `probe/chat-cache-v035-20261024`.
- **인계 작성 전 독립 HEAD:** 격리 `d8bcf4cd256a4562daea44da3ebe8d891f911992`, `main` `07133e0aaf738d6e4816a6486057b1cd49c018de`. **본 문서 커밋 후 격리 HEAD가 이동하므로 반드시 두 브랜치를 다시 각각 직접 조회**하고 최신 커밋·Actions와 대조한다.
- 읽기 순서: **① 본 인계 ② [단일 A~G 최신 상태표](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md) 최상단+A~G ③ [PROTOCOL](development/PROTOCOL.md)·[INDEX](development/INDEX.md) ④ [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 최신 보충 ⑤ [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)·[실행 개발자 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md) ⑥ [P3-HAW 증거 대사](development/notes/2026-11-10_p3-haw-handoff-evidence-reconciliation.md)와 [실제 무이력 Build 노트](development/notes/2026-11-10_p1-four-ordinary-real-zero-history-ready.md) ⑦ 기존 P3-HAV/HAU, P1 설치·영약·기름·캐시, [P2 속도 적응22점·다중영역 실험](development/notes/2026-11-10_p2-multiregion-throughput22-opt-in.md)·[선택형 격자 구현](development/notes/2026-11-10_p2-percentage-grid-opt-in-engine.md)·[적응형 격자 원설계](development/notes/2026-11-10_p2-percentage-grid-proportional-normalization.md)·[사용자 상한 60%](development/notes/2026-11-10_p2-user-configurable-final-stat-cap-and-grid-study.md)·[P2 신뢰성 정책](development/notes/2026-11-09_p2-opt-reliability-first-open-search-policy.md)·[실 Native10 대사](development/notes/2026-11-09_p2-real-native-ten-case-region-audit.md)·[합성 6형상 비교](development/notes/2026-11-09_p2-multimodal-equal-count-offline-audit.md) ⑧ 실제 원본·코드·GitHub Actions/Native 영수증·캐시.**
- 최신 사용자 직접 결정 > 승인 v1.4.3·비충돌 승인 정책 > GitHub 현재 코드/영수증·CURRENT > 이전 인계. **기존 역사 `PENDING` ≠ 현재 미구현**. 구현·offline·실 Native·사용자 웹 E2E·미실증을 섞지 않는다.

## 2. 최종 제품 목적·불변 계약

**26개 DPS 전문화(증강·탱커·힐러 제외)**가 목표 ilvl 기본 **334** 또는 사용자가 지정한 **기름 포함 최종 T**를 기준으로 SimC DPS가 최대가 되는 **치명/가속/특화/유연 절대 rating**을 찾는 **하나의 재사용 가능한 시즌 환경 구축 + 최적화 엔진**. 결과는 관측 1순위, DPS·SEM, **95% 판정의 적용 범위**, 실질적으로 다른 근접 대안, 스탯 비율, 캐시·취소·재개. 관측 최고와 전역 최적 증명은 다르다.

`B=G+J+F`, `T=B+O`, `c_final=c_base+o`; 수동 최종 T가 우선, O는 고정 비자유분배·단일 반영, L/E 정확 고정 하한/예산 소유권. 새 사용자 세션의 개별 최종 rating 상한은 기본 `floor(0.60*T)` 이하·사용자 조정 가능; 상한 필드 없는 기존 legacy 세션은 기존 `<50%` 유지. 새로운 시즌의 G/J/F/O에 70783 수치나 79×2 역사값을 검증 없이 복사하지 않는다. 기본 보석은 **치명·가속·특화·유연 일반보석 각각 1개(총4), 특수보석 필수 아님**. 최고 품질·정확 ID·효과/조건이 증명된 사용자 옵션만 정책 A에 따라 등록. 불충분 선택지는 보류하되 검증된 기본 환경 차단 금지.

사용자는 직업·전문화·종족·특성/목표 ilvl 또는 T·장신구2·선택 특수장비·장식≤2·보석/영약/기름/소모품·전투 조건을 지정. 내부에서 대표 일반 장비/무기/4티어/주능력/SimC 프로필 생성. 전체 현재 장비 재분배·장비 조합/획득 추천·전체 시즌 DB는 범위 밖. SimC가 아이템 효과/proc/APL/DPS를 담당하며 독립 효과 인증 Gate·독자 DPS 엔진 금지. 같은 시즌 정적 아이템 캐시는 SimC revision만으로 폐기하지 않으며 DPS 캐시는 정확 바이너리/프로필/옵션/후보/O/전투조건/iterations로 분리한다.

## 3. A~G 현재 구현·실증과 미완료 범위

| 영역 | 확인된 구현·영수증 | 아직 입증하지 않은 범위 |
|---|---|---|
| **A 환경 G/J/F/O·정책 A** | `v216/v217/v222/v212` 존재. **동일 라이브 70783·Ret334 빈 workspace** 실제 source→G/J/F **Native3**→v212 READY, `G2850/J92/F165/O0/B=T3107`, 일반보석4/특수 없음 [#42664089225](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42664089225). `v196/v220` 품질·정책 A 등록 체계 구현 | **미래 다른 시즌** 최초 수집·G/J/F/O·선택지 품질 전주기/일반성; 검증 없이 전부 READY 주장 금지 |
| **B 26 DPS** | 기본 물리 프로필 **26/26 SimC 수용** [#40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357) | 모든 전문화의 모든 고급 옵션·사용자 장기 Native 미실증 |
| **C 보석/영약/기름·L/E** | 신규 기본 일반보석4·`J92` 실 최초 Build. 70783 주무기 기름 `O=32`, 사용자 수동 T3500→B3468·웹 실 DPS [#42598051977](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42598051977) | 일부 L/E·선택적 소모품·다른 기름/시즌 품질 정확 조합 미검증 |
| **D Build·프로필·사용자 UI** | 빈 root **`LocalJobs.build_season_environment`→v216→v212→`load_fresh_profile_for_user` PASS**, 정확 설치본 SHA·보석 변형 구분. 기존 검증 영약/기름 선택 UI | 이번 일반보석4 프로필의 **실 DPS Native는 실행하지 않음**. 첫 사용자 GUI 클릭·미확정 시즌 품목 전체 자동 발행은 별도 |
| **E v290/v291 탐색/95%** | 실 **8 scout×35 + 2 confirm×320** Native10 [#42501052586](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42501052586), 합법 0-rating·국소 소진 전역 fallback; 신규 적응형 백분율 격자/비례 정규화는 [v298 선택형 실험 코드](development/notes/2026-11-10_p2-percentage-grid-opt-in-engine.md)로 연결, 기본 v290/사용자 웹 미전환 | **우선 다음 연구:** 실제 SimC 처리량에 따라 기준점 해상도(초기 11개)를 조절하고, bounded proportional redistribution을 구현·비교; 여러 유망 영역과 미탐색 영역을 함께 정밀화. 고점 누락·선택편향·종료/근접 대안 품질도 평가. [최신 opt-in/합성 감사](development/notes/2026-11-10_p2-percentage-grid-opt-in-engine.md): 112회 합성6형상 3유리/2동률/1열위(좁은 off-axis 고점), 혼합도 미해결; **기본 v290 승격 금지**, 실 SimC 새 Native0. 전역 최적·가족단위 95% 보증은 없음 |
| **F 캐시·취소·재개** | Native10 교차 Job 실측 캐시 신규 Native0 [#42504040076](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42504040076), 양의 O 실제 웹 세션 일부 성공 | 새로운 사용자 PC·장시간 다종 조합 안정성 전체 검증 아님 |
| **G Windows·웹** | 웹·UI/Windows 패키징 offline, 다른 O>0 사용자 HTTP→SimC DPS 실증 [#42598051977](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42598051977) | 실제 Windows PC 클릭·처음 GUI→일반보석4 장기 DPS·일부 옵션 연결 미실증 |

**기준 영수증 경계:** 무이력 70783 [#42664089225](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42664089225) **SUCCESS**, compiler missing=[]·requires=[]·source sealed, Native3(상한3), 소켓4/일반4종, v212 설치 및 사용자 프로필 PASS. [Artifact #13694734495](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42664089225/artifacts/13694734495). 선행 [#42663890986](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42663890986) 실패는 워크플로 바이너리 SHA 경로 오류/Native0이며 제품 실패가 아님. 인계 작성 전 최종 코드·문서 focused [#42664990314](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42664990314) **526 tests = 524 PASS/2 SKIP/0 FAIL·DEV_LEDGER_PASS**. 다른 실 O>0 웹 DPS는 **171141.52 / SEM734.76** (별도 조건), 이번 4보석 기본의 DPS로 전용 금지. P2 두 확인 후보 185438.66±280.54와 182070.77±302.13/명목 95% 비교는 **선택 쌍 한정**; 실제 국소최댓값의 개수나 전역 최적을 증명하지 않는다. 합성 다봉형 6형상 비교는 동일 112회 요청 기준 5동률/기존1 우세/새0 우세, **실 SimC 우위 증거 아님**.

## 4. 최근 변경·병목·효율 판단

- `17d9fce`: 기본 일반보석4→J→프로필 연결, `fe73eed`: 설치본/보석변형 SHA 재사용 경계, `7f2f244`: 구현/실증/미결함/검증공백 구분, `5d598d→b334d0`: 시험 전용 최초 Build, `d8bcf4`: 최초 실증·역사 미완료 상태 교정. **마지막 정상 Build 시험에서 runner 제품 코드 신규 변경0**.
- **환경 기본 엔진의 현 시즌 첫 무이력 Build는 실증됐다.** 이전 70783/Ret/Native3 무조건 반복·대규모 환경 엔진 재작성은 **STOP**. 미출시 미래 시즌/미등록 품목/개인 Windows E2E는 **미실증·선택적 제품 백로그**로 보존. 실제 새 시즌이 도래하거나 현 경로의 재현 결함이 나타나면 기존 Build를 사용해 그 부분만 CONNECT/EXTEND; 미실증=미구현 취급 금지.
- **현재 중심 병목은 P2 최적화 결과 발견 품질과 증거 충분성**: 최신 사용자 승인 설계는 각 자유 B 축의 백분율 기준점(초기 11개, 고정 아님)→가장 큰 grid-sum shell→B로 비례 확대→상한/하한 초과분 bounded 비례 재배분→정수 총량 보정·중복 제거다. 기준점 수는 실제 SimC 평균 처리시간/iterations/병렬 처리량/계산 예산으로 조절한다. v298 선택형 후보/비례 경계/정수화·v291 opt-in은 구현했으나 사용자 기본값 전환 및 실 Native 품질 비교는 미완료이며, 기존 v290과 동등 Native/iterations 예산으로 탐색 누락·다중 고점·선택편향을 비교해야 한다. Native/CPU 절약이나 SEM 자체가 목표가 아님.
- 매 작업 전에 **기능 INDEX/PROTOCOL/CURRENT→기존 소스·코드·Native/Actions·정적/DPS 캐시** 선조회. `REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP` 중 선택하고 (1) 제품 최종 목적 필요성 (2) 최신 사용자 승인 (3) 시즌/26 DPS 재사용성 (4) 기존 증거 충족 여부 (5) Native 중복·CPU·메모리·I/O/네트워크·캐시·시간 절감 확인. 독립 작업은 묶고 같은 완료 기준·역사 영수증 재사용, 바뀐 범위만 최소 검증. 특정 보석·효과의 일회성 인증·새 탐색 엔진 목적화 금지. 실제 품질 증거가 있으면 알고리즘 **교체 가능**, 기존 방법을 성역화하지 않는다.

## 5. 장단기 로드맵

- **단기:** P2 v290/v291 실제 Native10·정확 캐시·P2-OPT 정책·기존 합성6형상·0 경계·global fallback 선검토. [승인된 백분율 격자·비례 정규화](development/notes/2026-11-10_p2-percentage-grid-proportional-normalization.md)를 바탕으로 기존 후보 생성과 연결할 최소 설계를 구체화하고, pilot SimC 처리량으로 기준점 수/초기 후보 예산을 결정한다. 다중 영역·미탐색 유지와 95% 선택편향/근접 대안의 **동일 조건 평가 기준** 수립. 선택형 코드의 offline 검증과 실제 후보당 Native 처리시간 pilot을 진행하되, 기존 소스/캐시 재사용 및 Native 무조건 전수 실행 **STOP**.
- **중기:** 선택형 v298/v291 후보 생성·비례 정규화의 offline 경계/정수/중복/legacy 회귀와 동일 조건·동일 iterations/Native 예산 실 SimC 품질 비교 후 기본 전환 여부 결정. 더 나은 결과가 입증되면 v290/v291을 REPLACE 가능. 캐시·취소·재개·95% 적용범위 보존. 특정 최종 스탯 rating 고정은 별도 미래 사용자 제약으로 설계.
- **장기:** 실제 다른 새 시즌이 공개되면 **동일 시즌 환경 엔진**으로 새 원본/G/J/F/O/정책 A를 재결정·실증, 26 DPS로 확대, Windows 실제 사용자 원클릭·장기 최적화/고급 선택지 실용성 검증. 새 시즌을 미리 증명하려는 불가능한 Gate 금지.

## 6. 새 채팅 시작 프롬프트 (첫 읽기 전용 복원 후 즉시 STOP)

~~~text
SIMC SECONDARY OPTIMIZER 프로젝트를 읽기 전용으로 독립 복원하라.

저장소 degong2-code/simc-secondary-optimizer-runner
격리 probe/chat-cache-v035-20261024
최신 단일 인계 docs/CHAT_CONTINUITY_HANDOFF_20261110_P3_HAW_OPTIMIZER_RESUME_ENGINE_FIRST.md

먼저 격리와 main의 실제 최신 HEAD를 각각 독립 조회해라. 인계 전 기준은 격리 d8bcf4cd256a4562daea44da3ebe8d891f911992, main 07133e0aaf738d6e4816a6486057b1cd49c018de였으나 인계 커밋으로 격리 HEAD가 이동한다. 실제 최신 커밋/Actions와 대조하라.

자료 순서: P3-HAW → PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md 최상단/A~G → development/PROTOCOL.md·INDEX.md → CURRENT_PRODUCT_DEVELOPMENT_STATE.md → 승인 v1.4.3·DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md → 2026-11-10_p3-haw-handoff-evidence-reconciliation.md / 2026-11-10_p1-four-ordinary-real-zero-history-ready.md → P2 최신 [선택형 격자 구현](development/notes/2026-11-10_p2-percentage-grid-opt-in-engine.md)·[적응형 격자 원설계](development/notes/2026-11-10_p2-percentage-grid-proportional-normalization.md)·[상한 정책](development/notes/2026-11-10_p2-user-configurable-final-stat-cap-and-grid-study.md)·P2-OPT 품질 정책/Native10/합성 다봉형·역사 P3-HAV → 코드·원본·Actions/Native 영수증·캐시.

최종 제품은 26 DPS용 범용 시즌 환경 G/J/F/O 구축 + SimC 최적 절대 CHMV rating 엔진(기본 ilvl334/수동 최종 T, B=G+J+F/T=B+O, 기름 O 고정, L/E 중복 금지). 새 세션 개별 상한 기본60% 이하·사용자 설정, legacy <50% 보존. P2 후보 설계는 적응형 백분율 기준점·비례 정규화·상한/하한 재배분; 초기 11개는 실제 SimC 처리량에 따라 22/31/41까지 가변; v298/v299/v291은 선택형 실험 코드 구현, 기존 v290 기본·일반 웹은 미전환. 좁은 off-axis 고점 발견/동등 iterations 개선 미입증. 기본 일반보석 치명·가속·특화·유연 각1/특수보석 미필수. 장비 추천/현재 장비 재분배/전체 시즌 DB/별도 SimC 효과 인증 Gate 금지.

이미 기존 엔진으로 빈 작업공간의 실제 라이브 70783 Ret334/일반보석4 G2850/J92/F165/O0 B=T3107 Native3→설치 READY/검증 프로필 PASS [#42664089225]. 최신 관련 offline #42664990314 524 PASS/2 SKIP. 이것은 미출시 새 시즌·4보석 실 DPS·개인 Windows GUI 전주기 실증은 아니다. 과거 O>0 실 웹 DPS #42598051977, 기본 26/26 #40972829357, P2 Native10 #42501052586 및 실 캐시 #42504040076은 각 범위에서 재사용한다.

환경 엔진 대형 재개발/같은 70783 원본·Native 반복을 STOP. 현재 주력은 승인된 적응형 백분율 격자·비례 정규화 설계를 기존 v290/v291에 연결하고, 실제 SimC 처리량에 따라 기준점 수를 조절하며, 여러 유망/미탐색 영역을 동일 Native/iterations 예산으로 비교하는 P2. 코드를 만들기 전에 INDEX/원본/코드/영수증/캐시를 먼저 확인하고 REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP; 완성 엔진 목적·승인 일치·26전문화/미래 시즌 재사용성·중복 Native/CPU/메모리/I/O/캐시/시간 자가점검. 독립 작업 묶음 처리/기존 증거/동일 검증 재사용·변경분만 최소 시험. 알고리즘 고정 금지, 더 좋은 결과 품질 근거가 있으면 교체 가능.

**첫 응답에서는 복원 결과만** 보고하라. 실제 HEAD, 최신 정책·A~G/실 영수증 범위·완료/미완료·현재 병목·효율 대안·장단기 로드맵을 구분해 보고한 뒤 **즉시 중단**하라. 사용자의 별도 '진행' 전에는 코드·문서 수정/테스트/외부 수집/Actions·Native 실행/커밋·병합/공식 승격/Project UI·Work OS 변경을 시작하지 마라. main·v003 immutable·원본 v016·주 제품 개발 소유권을 보존하라.
~~~
