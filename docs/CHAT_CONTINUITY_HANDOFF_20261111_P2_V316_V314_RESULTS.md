# SIMC SECONDARY OPTIMIZER — P2 v316 / v314 독립 복원 단일 인계 정본
**기준:** 2026-11-11 KST · **지위:** 이번 P2 채팅의 최신 인계. 이 문서를 만들었다는 사실은 공식 승격·Project UI 적용·제품 완성을 뜻하지 않음.

## 1. 현재 GitHub, 기준 HEAD와 권한
- Repo: `degong2-code/simc-secondary-optimizer-runner`.
- Isolated: `probe/chat-cache-v035-20261024`, **본 인계 작성 직전 HEAD** `c1ef62363edba4be2900e49e11f5a417a0ae0b24`.
- `main` HEAD `07133e0aaf738d6e4816a6486057b1cd49c018de`. 이번 인계 커밋과 링크 갱신으로 격리 HEAD는 변경되므로 **새 채팅에서 두 HEAD를 반드시 다시 조회**. ahead/behind는 이번 조사에서 인증 못함.
- 우선권: 최신 사용자 직접 결정 > 최신 승인 v1.4.1 DPS-only 및 [v1.4.3 GJFO 정책](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) > 실제 코드·Actions/Native·[CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) > 과거 인계. **26 DPS**만 지원(증강·탱·힐 제외). 사용자가 업로드한 역사 v1.4.1의 “27 DPS/증강 포함”은 최신 결정과 불일치하므로 현재 정책이 아님. GitHub 문서·파일 제공만으로 Project UI 적용 증명 안 됨.
- **기존 주 제품 개발 채팅**이 전체 제품 구현/일반 SimC 시험을 계속 소유한다. 이 격리 P2 연구·문서 갱신은 별도 허용 범위. 별도 승인 없이 `main`, immutable v003, 제품 원본 v016, 공식 Work OS M0·Shared State, Project Sources/Instructions/UI, 제품 정책 기본 v290을 변경·승격하지 않는다.
- **검색 순서:** 본 단일 인계 → [START_HERE](development/START_HERE.md) → [제품 A~G 정본](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md) (기존 머리의 11/10 최신 표시는 역사 정보) → [INDEX](development/INDEX.md) → [FILE_MAP](development/FILE_MAP.md) → [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md) → [DECISIONS](development/DECISIONS.md) → [PROTOCOL](development/PROTOCOL.md) → CURRENT 필요한 부분 → 승인 정책과 아래 P2 노트/Actions. 900KB 이상 누적 CURRENT 전수 재독 금지. 기존 [P2 v305 인계](CHAT_CONTINUITY_HANDOFF_20261110_P2_FRESH_FROST_V305_NEXT.md), [P3-HAX 인계](CHAT_CONTINUITY_HANDOFF_20261110_P3_HAX_ADAPTIVE_MULTI_REGION_NEXT.md)는 역사 자료.

## 2. 제품 목적, 범위 및 승인 회계
26개 DPS에서 목표 ilvl 기본334 또는 **사용자 수동 최종 T**를 기준으로, 미래 파밍 목표가 될 치명/가속/특화/유연 **절대 rating의 SimC DPS 최대화**. 출력: 절대 rating·비율·예상 DPS·SEM·95% 판정·관측 1순위·충분히 다른 근접 대안·캐시/취소/재개. 관측 최고는 **전역 최적 증명 아님**. 장비 조합/파밍 경로 추천, 현재 착용 장비 전수 입력·재분배, 시즌 전체 장비 DB는 제외.
- 사용자 선택: 직업/전문화/종족/특성, 목표 ilvl/수동 T, 장신구 2, 특수장비, 장식 최대2, 검증된 최고 품질 보석·영약·기름·소모품, 전투조건. 업로드 SimC 프로필은 캐릭터/특성 추출용 선택 입력이며 현재 장비와 총량을 목표 예산으로 복사하지 않는다. 대표 일반 장비·무기·티어4·주능력치·SimC 입력은 내부 생성.
- **B=G+J+F, T=B+O, c_final=c_base+o**. 수동 T 우선. O는 적용 가능한 손/무기의 고정 비자유분배 스탯으로 `gear_*`에서 한 번만; 정확 L은 G/B에 이미 들어 있어 하한 보호만, 다시 가산 금지; 정적 E도 중복 가산 금지. 장신구 고정 스탯은 자유 G 밖, 정적 gear 레코드 없음≠0; 제작장비 최초 50:50 스탯은 L이 아님.
- 새 시즌 **G/J/F/O 전부** 동일 시즌·빌드 원본/증거로 재구축하고 B/T 재계산. 역사 79×2/J138/F165/기름16·16 등을 새 시즌에 무단 복사하지 않는다. exact Native G 선택 경로는 유지하되 전수 선행 Gate 아님. 같은 시즌 정적 캐시는 SimC revision만으로 폐기 금지; DPS 캐시는 바이너리·프로필·옵션·후보·iterations·O·전투조건 identity 구분.
- 현 실증 70783 Ret334 기본 사례 **일반 4보석 치/가/특/유 각1, 특수보석 필수 아님**, O0, G2850/J92/F165/B=T3107. 영구 마부 포함, 일반 임시 마부 제외(무기 기름 별도 지원), 확장팩 특수 시스템은 선택 모듈. 동일 효과/조건/범위가 증명된 최고 품질만 사용자 선택지에 자동 등록.
- 효과·proc·APL·DPS는 **SimC가 책임**. 별도 효과 엔진·지원 인증 Gate 만들지 않는다. 우리 책임은 입력/대표 프로필·회계·정적 JSON2 rating·후보/95 통계·캐시/재개.

## 3. 제품 기능별 코드와 검증 신분
| 영역 | 기존 진입점/재사용 | 확인된 범위와 미실증 |
|---|---|---|
| A~E 시즌 Build·READY | `runner/v161`, `v191`, `v213`, `v217`, `v216`, `v212`, `v222`, `v220`, `v196` | 현 시즌 원본→GJFO→설치/신규 대표 프로필 실제 Native3 [#42664089225](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42664089225). 미래 시즌 첫 GJFO 자동 Build·전체 옵션 미실증. |
| 장비/보석/영약/기름 | `v167/v230/v232/v251/v277`; `v221/v266/v271`; `v281/v278/v285/v286/v295/v296` | 현재 검증 빌드의 4보석·GJF/O 소스 및 Native 영수증 재사용; 새 시즌의 수치는 새 증거 필요. |
| F 제품 사용자 입력→SimC | `v113` 사용자/웹 → `v098/v139` 프로필 → `v096/v094` Native → **기본 `v290/v291`** 최적화 → `v292/v293` 캐시/재개 | 기본 26개 물리 프로필 SimC 수용 [#40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357), 일부 신규 사용자 Native/웹 검증. 26전문화 각각의 실제 최적화 품질, Windows 최종 실사용 GUI 미실증. |
| P2 v313/314 | `runner/v313_multispec_matrix_contract.py`, `runner/v314_fresh_eight_spec_matrix_contract.py`, `integration_probes/p2_v313*`, `p2_v314*` | 실제 신규 제품 시나리오 v290-v312 각 A/B. v313 **8/8**, v314 **15/16 완전 + 1시간상한 부분**. 같은 Native 횟수라도 같은 iterations가 아니다. |
| P2 v315 | `integration_probes/p2_v315_iteration_wall_real_receipt_analysis_offline.py` | Native 원본 10조건 **기술적 비용 대사 PASS**, 새 Native0. 요청당 고정비/iteration slope 미식별. |
| P2 **v316** | `runner/v316_optin_case_time_trace.py`와 v291 opt-in 통합, 해당 tests | 요청별 단계별 monotonic timing·5/10분 확인 후보 판정 **구현 및 합성 OFFLINE PASS**, 신규 **실 Native trace 0건**. |

**검증 등급:** CODE_IMPLEMENTED ≠ OFFLINE_PASS ≠ REAL_NATIVE_PASS ≠ USER_WEB_E2E_PASS. 증거 부재를 재현된 결함이라 하지 않는다. v316 신규 테스트의 초기 import-alias 불일치로 합성 테스트 2건 실패했으나 코드가 아닌 test 참조 수정 후 최신 회귀 PASS; 현재 제품 Native 재현 결함으로 분류 금지.

## 4. P2 새 실측 원본 결과·경계
1. **v312 단일 신규 Warlock A/B:** [실 Native #42838011084](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42838011084) v290 각1008 / 69,765 iterations/270.490초/320확인 최고 182000.24±SEM253.46, v312 각1008 /39,840 iterations/285.557초/181384.94±238.71. 명목95 우위 미확정, 1008 calls=동일 계산량 아님.
2. **v313 4 DPS×2:** [실 Native #42843524976](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42843524976) **SUCCESS 8/8 FULL**(냉법, 분전, 야냥, 정술). v290 관측 우세6/v312 2, 선택쌍 명목95 확정0. [기록](development/notes/2026-11-11_p2-v313-four-spec-eight-distribution-fair-comparison.md).
3. **v314 신규 8 DPS×2:** [실 Native #42846073820](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42846073820), 집계 원본 artifact `13791573260`, **workflow SUCCESS, 16개 receipt 발견, 15개 FULL 1008/1008, 1개 PARTIAL**. 대상 사격/야수 사냥꾼, 비전/냉기/화염 법사, 냉기 죽기, 잠행/암살 도적. 15 FULL 중 v290 관측 우세11/v312 4, 상대 v312 확인 DPS 개선 중앙값 **-0.107684%**, 95 확정0. `assassination_rogue__wide`: 실행 상한 약540초/arm; **v290 786 Native·53,730 iterations vs v312 1008 Native·39,840 iterations**. 이 1건은 동일 1008 calls 완료나 공정 승패에 포함하지 않는다. 실패나 무조건 16/16 완료로 표시 금지. 기존 [v314 계획 노트](development/notes/2026-11-11_p2-v314-eight-fresh-profiles-after-v313.md)의 PENDING은 역사 시점.
4. **v315 v313 8+v314 첫2=10개 원본:** [오프라인 #42859573357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42859573357) 신규 Native0, v312/v290 **iterations 비율 중앙값 0.568737**, **wall 비율 중앙값 0.987107**, v312 적은 iterations 10/10·짧은 wall 7/10, 선택쌍 명목95 확정0. 두 aggregate (t,I) 점에서 고정 시작비·순수 iteration 계산비 분해 불가능. [노트](development/notes/2026-11-11_p2-v315-original-iteration-wall-evidence.md).
5. **v316 실제 요청별 계측 구현:** [개발노트](development/notes/2026-11-11_p2-v316-optin-per-case-wall-trace-and-confirmed-checkpoints.md) [최종 근접 CI #42867551279](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42867551279) 635 PASS/2 SKIP/0 FAIL; [최신 HEAD 회귀 #42867821279](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42867821279)도 635 PASS/2 SKIP/0 FAIL**. `case_timing_trace=False` 기본, opt-in True에서는 `V316_CASE_WALL_TRACE.jsonl`에 plan/preflight/engine/JSON ingest/journal 별 duration, invocation/원본 session·case·Native SHA·exact iterations. `engine_execute_seconds`는 순수 iteration runtime 아님. 300·600초에는 해당 단일 invocation에서 *이미 완료된* precision 후보만; 재개·캐시·로그 누락은 `UNAVAILABLE_PARTIAL_OR_RESUMED_OR_CACHE_TIMINGS`. 시즌 Build 전처리시간 미포함. **v316 신규 real Native 계측 0**. 단독 v316 실측 효과 미입증.

과거 Warlock 21단계 19,812 격자 중 9,906 실제 관측 나머지 전수는 **사용자가 중단 지시**. 같은 과거 profile에서 나온 Native DPS 캐시를 이번 신규 사용자 실험에 이식 금지; 동일 시즌 정적 캐시만 유효 동일조건 재사용. 실험 연구 몇시간 허용하지만 최종 사용자 알고리즘 목표는 **5~10분**.

## 5. 알고리즘 아이디어·최근 사용자 지시
[IDEA-001~007 정본](development/algorithm_ideas/README.md), [동일 예산 벤치마크](development/algorithm_ideas/BENCHMARK_PROTOCOL.md).
- IDEA-001: 다중 정밀도 승급·**time-reserved precision**; v316 실제 latency 계측 전 35→120→320 실전 도입 불가. v291 35/320 정확 iteration/seal/cancel/replay 구조를 깨지 말 것.
- IDEA-002: v303/v306 다중 영역·반경 중복 → REUSE/ablation.
- IDEA-003: v290 maximin/v312 global reserve 중복 → 필요 시 커버리지 옵션으로 통합.
- IDEA-004: 비용 인지 KG, calibrated uncertainty·실행 오버헤드 미증명 → HOLD.
- IDEA-005: seed-pair 공분산 양수 보장 안 됨 → feasibility evidence 전 HOLD.
- IDEA-006: 국소 quadratic 방향 실측 기반 [오프라인 #42856597090](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42856597090)에서 기존 v312 전역 cubic보다 RMSE 낮지 않음 (global128/400/1200: 227.863/282.815/248.605 vs local303.929/286.451/279.108); 8지역 중 4곳 split 방향 불안정. 독립 국소 fitting HOLD, 기존 cubic 방향을 활용한 가벼운 기하 ablation은 별도 검토.
- IDEA-007: 정책 간 온라인 포트폴리오, v303 지역 예산·v312 후보 타입과 중복. source·journal·cache 재개/정책 분리 전 후순위.
- **사용자 요구:** 응답마다 새로운 아이디어를 연구하되 **수량 채우기식 중복 제안 금지**. 합리적 신규 아이디어라면 왜 발상했는지·이득 발생 조건·장단점·기존 코드/아이디어 중복·통합 기대·CPU/메모리/I/O·SimC 비용·반증시험을 **개별 문서**에 기록하고 README에 연결. 기존 IDEA-001의 새 시간예산 원칙을 이름 바꿔 신규 ID로 중복 등록하지 않는다. 본 인계 목적의 문서 작업은 새 알고리즘 ID 추가 근거 아님.

## 6. 현재 병목, 비용과 다음 작업
**병목:** 초기 비교는 1008 Native 횟수만 동일, 실제 iterations/정밀 확인 기회가 상이해 알고리즘의 공정 우열 미확정. 기존 v315 aggregate는 5/10분 시점별 확인 후보를 소급 복원할 수 없다. v316 trace는 구조 PASS이나 **진짜 Native 요청별 시간·계측 오버헤드 실증 없음**. 관측 고점 95 선택쌍은 전역/다중비교 우위 아님.

- **P0 새 채팅 최초 읽기 전용 STOP:** isolated/main HEAD, v314 [#42846073820] 15완전+1시간상한·artifact `13791573260`, v316 최신 CI #42867821279, 정책/지식 링크/권한/소유권을 재확인하고 결과 보고만. artifact 만료 시 재수집/재실측으로 위장하지 않는다.
- **P1 REUSE/CONNECT, 사용자 ‘진행’ 이후:** 신규 사용자 프로필 1조건만 골라 기존 v316 opt-in 케이스별 실제 Native timing과 300/600초 확인 DPS 추적의 최소 실험. 프리빌드/전체 GUI 시간과 optimizer-invocation wall을 구분. 계측 fsync overhead·CPU·I/O 검토, 원본 Native/캐시 재개/중복 방지. **기존 v314 상한 540초는 600초 결과를 만들 수 없으므로 600초 checkpoint 필요한 새 시험은 상한을 별도로 설계**, 실행시간 초과 경우 정상 부분으로 표시.
- **P2 별도 공정 비교:** 신규 8스펙×2까지의 과거 results만으로 최종 교체 금지; 독립 첫 생성 새 profiles/seed에서 **동일 총 iterations** A/B와 **동일 실제 300/600초 wall** A/B를 분리 실험. 320+ 확인 DPS/SEM·95 미확정·실행시간·CPU/메모리/Native 캐시·품질/동등 분모 집계. v314 유일 시간 제한 조건은 완전 비교가 되도록 동일 계산 예산·확인 reserve 설계, 무조건 재실행하지 않는다.
- **P2 IDEA-001:** 실측 per-request time을 확인한 후 time-reserved precision·단계적 승급 ablation, 기존 v291의 exact iterations identity/cache/seal/snapshot 계약 변경 범위를 최소화. 필요시 IDEA-006 기존 cubic 기하 소규모 ablation, 별도 full engine 금지.
- **중기 제품 연결:** v113→v216/v212→v098/v096/v094→v290/v291→v292/v293 UI/95 결과·근접 대안/취소·재개 일체화, 실제 Windows 사용자 E2E. 26전문화 전체 Native 전수 대신 실제 변경 영향 최소 시험.
- **장기:** 시즌 G/J/F/O 자동 재구축·Policy A 최고품질 등록·시즌 모듈·26 DPS 범용성, 제품 원클릭 완성. DB/효과 엔진/장비 추천 범위 확대 금지.

검증 완료/부분/미실증/결함을 분리하고, `REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP`로 판단. 기존 증거와 동일 시즌 정확 identity 캐시를 최대한 재사용. 불필요한 Native 대량 반복·구조 확장을 피한다. 본 인계로 NEW_NATIVE 0.

## 7. 새 채팅 독립 복원 프롬프트
~~~
SIMC SECONDARY OPTIMIZER를 읽기 전용으로 독립 복원하라.
GitHub 저장소: degong2-code/simc-secondary-optimizer-runner
격리 브랜치: probe/chat-cache-v035-20261024
이번 인계 전 HEAD isolated c1ef62363edba4be2900e49e11f5a417a0ae0b24 / main 07133e0aaf738d6e4816a6486057b1cd49c018de (현재는 재조회 필수).
단일 최신 인계: docs/CHAT_CONTINUITY_HANDOFF_20261111_P2_V316_V314_RESULTS.md
읽기 순서: 인계 → docs/development/START_HERE.md → docs/PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md → docs/development/INDEX.md → FILE_MAP.md → EVIDENCE_INDEX.md → DECISIONS.md → PROTOCOL.md → CURRENT 최신 필요한 범위 → v1.4.3 승인 시즌 G/J/F/O 정책 → v313/v314/v315/v316 실측 노트와 IDEA-001~007.
제품은 26개 DPS, 목표 ilvl334/수동 최종 T=G+J+F+O를 기준으로 절대 CHMV rating을 SimC DPS 최대화로 찾는다. 기존 v290 기본 유지, 시즌 원본은 해당 시즌에서 재검증; 현재 착용 장비 전수 재분배/장비 조합 추천·전체 시즌 DB 금지. SimC는 APL/proc/effect/DPS, 95%는 선택편향·전역 최적과 구분.
실제 영수증: v313 #42843524976 8/8; v314 #42846073820 GitHub SUCCESS라도 15/16 완전 + assassination_rogue__wide 540초 TIME_CAPPED_PARTIAL (집계 artifact 13791573260). v315 10건 iterations/wall 비용 #42859573357. v316 opt-in per-case trace 코드·635 PASS/2 SKIP #42867821279, 실제 계측 Native 0. 1008회 동일 호출은 iterations 동등이 아니며 35→120→320 추가는 현재 v291 캐시/seal 계약 조정 전 구현하지 않는다. 21단계 남은 9906 전수 중단. IDEA-006 독립 국소 이차회귀 미승격.
첫 응답에서는 격리/main HEAD, 최신 GitHub Actions·원본, 완전/부분/미실증, 실측·오프라인 구별, 최근 변경, 제품 주요 진입점, 캐시 재사용, 26 DPS 정책, 현재 병목, 단기/장기 로드맵, 주 제품 채팅 소유권과 승인 경계를 **읽기 전용 복원 보고**하고 **즉시 STOP**한다.
사용자가 별도로 '진행'을 승인하기 전까지 코드·문서 수정, 새 테스트, 외부/Native 수집, Actions 실행, 커밋·병합, main/immutable v003/Project UI/Work OS 공식 승격을 시작하지 마라.
~~~
