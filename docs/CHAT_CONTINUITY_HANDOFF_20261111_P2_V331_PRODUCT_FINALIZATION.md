# SIMC SECONDARY OPTIMIZER — P2 v331 종료·제품 완성 전환 단일 인계 정본
**기준일 2026-11-11 KST.** 개발 격리 브랜치의 최신 단일 인계. 설계 정책 원문 개정/제품 기본 변경/공식 승격 아님.

## 1. 저장소와 소유권
- Repo `degong2-code/simc-secondary-optimizer-runner`, 격리 `probe/chat-cache-v035-20261024`.
- 인계 작성 직전 실제 HEAD `7697d10b611ada1624a04e1f52ab7c88989238a1`; main `07133e0aaf738d6e4816a6486057b1cd49c018de`, 당시 diverged ahead3557/behind7. 인계 문서 커밋 이후 HEAD는 바뀐다. 새 채팅에서 실제 두 HEAD를 다시 확인한다.
- 주 제품 개발 채팅의 소유권을 보존한다. 사용자의 이번 요청은 새 채팅에 개발 연속성을 넘기는 명시적 요청이며, 기존 주 제품 개발 범위를 계승하는 것이지 MAIN/WORK 공식 주도권 이동이 아니다. 새 채팅 첫 보고는 읽기 전용, 별도 '진행' 전 모든 수정/실행/수집/Actions/커밋 금지.
- main, immutable v003, 원본 v016 파일, Project Sources/Instructions 실제 변경, Work OS M0/Shared State/공식 승격은 별도 승인. 원본 v016은 사용자 보고 기준, 원본 바이트 직접 통합은 독립 확인하지 않았다.
- 우선권: 최신 사용자 직접 결정 > [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) + 비충돌 v1.4 계열 > 실제 코드/Native/Actions > 역사 인계. 역사 자료의 27 DPS/증강 포함 표현은 폐기; **26 DPS만**. Project UI 실제 등록을 GitHub 문서로 추정 금지.

## 2. 제품 목표·회계·범위
목표 ilvl 기본334 또는 수동 최종 T에서 미래 파밍 목표 CHMV 절대 rating을 SimC DPS로 최적화. 결과는 관측 1순위·비율·DPS·SEM·95% 판정·실질적으로 다른 근접 대안; 전역 최적 증명 아님. 현재 장비 전수 입력·재분배, 장비 추천/조합/획득 경로, 시즌 전체 DB, 증강/탱커/힐러는 제외.
- 사용자: 직업/전문화/종족/특성, ilvl/수동 T, 장신구2, 선택 특수장비, 장식 최대2, 소모품/기름/마부/전투조건. 대표 일반 장비·주능력치·무기·티어4·SimC 프로필 내부 생성. 업로드는 캐릭터 정보 추출 편의, 현재 장비 복사 아님.
- B=G+J+F, T=B+O, c_final=c_base+o. 수동 최종 T 최우선, B=T-O. G/J/F/O는 매 시즌 동일 시즌 원본으로 다시 구축; 과거 시즌 수치 복사 금지. exact Native G 보조 경로, 전수 Gate 금지.
- L은 G/B에 이미 들어 있는 정확한 고정 특수장비 하한. E는 승인 회계로 한 번, O 고정 벡터 한 번; 장신구 고정 스탯 자유 G 밖, 미관측 gear≠0, 제작50:50 잠금 금지. 보석·영약 F/J의 초기 CHMV 종류는 자유 배분 가능; SimC gear_* 덮어쓰기/정적 결과 대사로 보정. **영약 종류를 임의로 고정 하한으로 삼지 않는다.**
- 기본 일반보석 치/가/특/유 각1, 특수보석 선택. 현재 70783 새 기본 사용자 예산 G2850/J92/F165/O0/T3107은 실제 사례 값이지 새 시즌 상수 아님. 일반 임시마부 제외, 영구 마부와 무기 기름 지원; 확장팩 특수 콘텐츠는 선택 모듈, 비활성 시 profile/budget에 흔적 없음. 정책 A: 정확한 ID/출처/조건/입력/회계 검증 후 자동등록, 최고 품질은 동일 효과·조건·범위 검증 시만 중복 제거.
- SimC 책임: 효과/proc/APL/DPS. 우리 책임: 입력/회계/정적 JSON2 rating/탐색/통계/세션. 별도 효과 인증 Gate·AI 런타임 의존성 금지.

## 3. 실제 구현과 검증 — 재개발 금지
[제품 A~G 정본](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md), [FILE_MAP](development/FILE_MAP.md) 참조. 아래는 최신 보충이며 A~G의 역사 서술보다 우선.
| 영역 | 구현 | 실증·남은 경계 |
|---|---|---|
| 환경 구축 | v216/v217/v212/v222/v196/v220 핵심 구현, source→예산→설치/READY | 70783 zero-history 4보석 새 Build Native3 [#42664089225](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42664089225); 여러 새 전문화 자동 T 및 실제 DPS 아래 참조. 다른 시즌 최초 실제 종단 미실증, 기능 미구현/결함으로 판정 금지. |
| 대표 프로필 | v098/v139/v101 기본 26 DPS 구현 | [26/26 기본 SimC 수용 #40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357); 모든 전문화 모든 선택 조합 장시간 UI 미실증. |
| 선택/회계 | 장신구·특수장비·장식 및 gem/flask/oil/enchant 입력과 기존 품질/정책A 구현 | 일부 L/E·선택 조합/새 시즌 실제 연결 미실증; 실제 막히는 경로만 CONNECT/FIX. 양의 O 웹 종단 [#42598051977](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42598051977). |
| 탐색 | v290 기본, v291 durable, v316 timing | 다수 Native 실증; v318/v328/v330 opt-in 연구, 기본 교체 미승격. v331 완료, 기본 N35 유지. |
| 실행·UI | v113 → v098/v139 → v096/v094/v093 → v290/v291 → v292/v293, 캐시·취소·재개·출력 구현 | 실제 cross-job cache Native0 [#42504040076](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42504040076), 로컬 웹/Windows 포장 [#42623497934](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42623497934); 사용자 개인 PC 설치~결과 전주기 미실증. |
| N 설정 제품 준비 | v293 sealed per-session N, allowed 35/48/56/64, DEFAULT=LEGACY=35, v093.prepare rebind 검증 | [v331 seal tests](../tests/test_p2_v331_product_scout_n_seal_offline.py), [common #42969547544](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42969547544), [web #42969405779](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42969405779) SUCCESS. 새 기본 미선택/미적용, 32 연구 전용. 변경 후 실제 새 제품 N 경로 최소 시험 필요. |

## 4. 직전 인계 이후 연구 — 원본 참조와 판단
이전 [v316/v314 인계](CHAT_CONTINUITY_HANDOFF_20261111_P2_V316_V314_RESULTS.md)는 역사. v313 8/8, v314 15/16 FULL+암살 wide540s 부분, v315 10원본 offline Native0, v316 계측 offline 635 PASS/2 SKIP은 당시 증거. 이후 실제 timing trace는 v329/v330/v331에서 검증됨. v317 개별 run을 이번 인계에서 독립 식별하지 못함; 후속 실측을 무효화하거나 그 캠페인 재실행할 이유 없음.
| 연구 | 실제 원본/결과 | 판단 |
|---|---|---|
| v319 풍운 | [131 Native compact](development/research_receipts/p2_v319_windwalker_auto_T_real_v290_v318_compact.json) / [#42941245130](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42941245130) | v290/v318 동일 최고 CHMV, 우위 미입증 |
| v320/321 암흑 | [134 Native compact](development/research_receipts/p2_v321_shadow_auto_T_35_120_320_compact.json) / [#42945184377](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42945184377) | 원본128 성공 후 120 metadata 검증 실패; 로컬 새120 3회만 실행. 120 연구용, 제품 중간 단계 아님. |
| 비용 실측 | [18회 35/120/320](development/notes/2026-11-11_p2-18-real-request-cost.md) | 320/35 실제 process wall 5.5~6.0배, iterations 비율9.14 아님; 120 추가 승급 비용 고려. 역사 프로필 단순 비용 측정으로 새 알고리즘 비교 아님. |
| v322~324 조화 | [163 Native](development/research_receipts/p2_v324_balance_auto_T_variable_n_32_compact.json) / [#42949922419](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42949922419) | 동일 CHMV의 독립 N DPS 차이로 N 추천한 v323-v1 무효, v2 교정; 동일 CHMV는 noise/SEM·도달비용 비교. |
| v325/326 황폐 | [251 Native](development/research_receipts/p2_v326_devastation_auto_T_heldout_251_compact.json) / [#42953218111](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42953218111) | N24 1/2, N48/96/192 2/2 near-band, 12 후보에 한정. |
| v327 파멸 | [299 Native](development/research_receipts/p2_v327_havoc_auto_T_299_native_compact.json) / [복구 #42957270859](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42957270859) | 원본128 재사용, 새168만 실행. N32/48/64/96 모두3/3 near; regret .214/.033/.123/.033%; 3시드·첫 후보 이미 near·후향 셔플은 확증 아님. 원본 final_T는 벡터, scalar와 비교하지 않음. |
| v329 IDEA-002 고통 | [267 Native](development/research_receipts/p2_v329_affliction_idea002_267_native_compact.json) / [#42962010689](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42962010689) | v306/v328-v1 각64/4520; 독립 원래 1순위 183075.70/183113.50, 95 미분리. 시드 교란·pairwise→grid 혼합. v328-v2 pairwise 보존 수정 offline PASS [#42963110872](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42963110872), 새 Native0. HOLD. |
| v330 IDEA-003 야성 | [124 Native](development/research_receipts/p2_v330_feral_idea003_124_native_compact.json) / [#42965880663](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42965880663) | 새 source 공통19 관측 재사용, 20번째 reserve 분기, 각 논리64/4520, 실제64+45. 12/12셀, 35번째 near, 동일 best-of-six 379/1398/1103/227 198326.54. 우위 미입증, HOLD. |
| v331 부정 | [343 Native compact](development/research_receipts/p2_v331_unholy_fixed_N_343_native_compact.json) / [#42969029964](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42969029964) | 마지막 N 비교 완료; 상세 아래. |

## 5. v331 완료 — 다음 작업의 정확한 시작점
- 코드 `integration_probes/p2_v331_unholy_fixed_N_real_once.py`, [연구 노트](development/notes/2026-11-11_p2-v331-unholy-fixed-scout-n-final-study.md), 워크플로 `.github/workflows/p2_v331_unholy_fixed_n_native.yml`. 실행 HEAD 844457983731556663bf6fc2fa8f69560508431d, SUCCESS. Artifact 13833315993, 2026-11-18T06:05:22Z 만료; Git tracked compact 보존. 원본 전체 ZIP 영구 Git 보관은 아님.
- 새 부정 죽기 인간 ilvl334/자동 T3107/일반4/O0. 환경3+5×64 v290 Native+20 독립640=343. 실제 340 DPS 원본의 input·JSON2 SHA, seed, revision, samples, DPS/SEM, journal/trace 및 common-prefix metric 검증. 340 독립 DPS seed. 환경3은 실행 receipt 기반.
- 초기 8개 CHMV 동일, 각 독립 시드. N은 **CHMV 한 개당 iterations**, 시작 후보 수/총 calls와 다름. 확인 N320 유지. 64 calls 동일이나 scout/confirm 수와 iterations 다름. 공통 실측 trace 51.298s, iterations4352의 prefix를 따로 비교.
| N | scout/confirm | 총 iter | 전체 wall(s) | 처음 near(s) | 선정 CHMV | 독립 DPS | regret % | 공통 wall/iter 발견 regret % |
|---:|---|---:|---:|---:|---|---:|---:|---|
|32|56/8|4352|51.49|40.97|1398/332/1212/165|155275.38|0.0703|0.0703/0.0703|
|35|56/8|4520|52.89|44.15|1398/372/1172/165|155314.41|0.0452|0.0452/0.0452|
|48|56/8|5248|60.01|46.30|1398/332/1212/165|155275.38|0.0703|0.0703/0.2597|
|56|57/7|5432|62.31|36.71|1398/333/1211/165|155384.65|0|0/0.2597|
|64|57/7|5888|66.36|43.01|1398/332/1212/165|155275.38|0.0703|0.2597/0.2597|
- 10 shortlist 독립 N640×2 best-of-10, near 5/10. N32/48/64 정확히 동일 최종 CHMV. N56은 1 rating 이동 차이; 평균 차이 약109 DPS, SEM~126씩, 명목95 미분리. N56이 공통 wall에서 가장 좋은 shortlist 후보를 발견했으나 공통 iter에서는 N35가 더 좋았고 전체 wall도 N35보다 길다. 한 전문화/한 trajectory per N, 전역 최적/일반적 N 우월/가족단위95 증명 아님. **N56을 공학적 기본 후보로 권고**(사용자 안전망 선호와 비용·누락 고려), 사용자 확정 또는 적용을 주장하지 않음.
- **재개 우선:** 첫 읽기 전용 복원에서 이 완료 receipt와 HEAD 확인. 이후 '진행' 승인 시 `v293_local_longrun_session.py`의 DEFAULT_SCOUT_ITERATIONS 및 실제 사용자 제품 경로의 기본 N 설정 일관성 확인 → v290 유지·N56/320 채택 검토/적용 → legacy missing-field N35 재해석 금지, 기존 N35 cache/session 보존, 새 N56 exact identity → 변경분 focused offline/필요 최소 새 사용자 Native E2E. v331 전체 재실행 금지. 아직 default35. v293은 새 세션 35/48/56/64 선택 가능하도록 이미 구현, 재개 config가 우선, N32는 연구 전용; v331 연구 실행 HEAD는 v293 후속 변경 전.
- 120 중간 단계 추가, 가변 N per candidate, v318/328/330 기본 승격은 하지 않는다. 해당 선택은 별도 개선 증거가 있을 때만 재검토.

## 6. 최신 사용자 결정 및 개발 방향
- 좋은 CHMV **발견·누락 방지**가 1순위; 발견 시간·계산 효율 2순위; 최종 SEM/95 통계는 결과 설명·확인용. 동일 CHMV의 관측 DPS 차이는 noise, 알고리즘은 도달 효율로 비교. N 증가에 따른 SEM 기대 감소가 작은 독립 표본의 regret 단조 감소를 보장하지 않는다.
- 5~10분 사용자 목표는 hard cutoff 아님. 품질·효율 중요. 연구 장시간 허용과 제품 기본 목표 혼동 금지.
- 모든 신규 실제 알고리즘 실험은 새 전문화 프로필을 P1 실제 경로에서 생성. 자동 T 원칙, 임의 수동 +343 금지. 동일 캠페인 arm은 한 신규 source SHA 공유. 현재 캠페인의 정확한 공통 관측 재사용 허용(원본 SHA/seed/identity 검증); 이전 캠페인 완성 프로필/DPS를 복사하지 않음. 같은 시즌 정적 아이템 cache는 SimC revision만으로 폐기 금지. DPS cache는 N 포함 정확 identity, 결과/원본 재사용과 새 실행 구분.
- **최신 사용자 결정:** 마지막 N 연구 후, 더 좋은 실질적 아이디어가 없는 이상 알고리즘 연구를 종료하고 제품 완성. 과거 '채팅당 아이디어' 의무를 제품 마무리까지 끌고 가지 않음. 기존 아이디어 registry [IDEA-001~008](development/algorithm_ideas/README.md) 보존·중복 없이 통합 고도화; 강한 근거 없는 숫자 늘리기/모형/전수 Native 금지. IDEA-001의 fixed N만 제품에 반영 검토; IDEA-008 독립 홀드아웃은 연구 실증, 공식 제품 통합 미완. IDEA-002/003 HOLD, IDEA-006 국소 2차 음성 offline, 004/005/007 후순위.
- 이미 구현한 환경 엔진/대표 프로필/옵션/캐시/UI를 다시 개발 과제로 등록하지 않는다. 새로운 시즌 원본 검증 미완료≠기능 미구현. 실제 재현 결함만 수리. REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP.

## 7. 로드맵 및 검증 범위
1. **바로 다음:** v331 결과 반영한 공학적 N 선택 및 제품 통합, 새 세션 default 일치/legacy cache&resume·UI/result 회귀. 기존 최적화 v290 유지.
2. 기존 제품 사용자 흐름의 실제 미연결·결함만 점검: P1 Build→선택/프로필→longrun→결과/대안/95%/취소·재개. 필요한 최소 신규 프로필 실증만. 모든 기능 재개발·26개 전수 Native 금지.
3. UI/UX 최종 정리, 기존 Windows packaging 실행, 사용자의 실제 PC 설치→실행→재개→결과 시험 및 발견 결함만 수정.
4. 제품 버전/배포 상태 확정 후, 필요 시 다음 시즌 실제 정상 Build 검증 및 옵션 모듈 업데이트. 미래 시즌 실증/모든 조합/전역 최적 보증/원본 v016 직접 통합/공식 main 승격은 별도 범위.
- 인계 작업 자체는 신규 Native0. 기존 v331 결과만 검증. 코드/정책/기본값/main/Project UI 변경 없음. 문서 push에 따른 기존 공통 offline CI만 허용, 별도 실행/고비용 재검증 없음. 인계 당시 이전 common [#42969547544](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42969547544) 성공; 새 인계 commit CI는 실제 상태 조회 필요.

## 8. 새 채팅 읽기 순서·STOP
이 단일 정본 → [START_HERE](development/START_HERE.md) → [A~G](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md) → [INDEX](development/INDEX.md) → [FILE_MAP](development/FILE_MAP.md) → [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md) → [DECISIONS](development/DECISIONS.md) → [PROTOCOL](development/PROTOCOL.md) → CURRENT 필요한 부분만 → 승인 v1.4.3 및 v331 노트/compact, 아이디어 registry. 과거 CURRENT/원본 전체 전수 감사 금지. 실제 HEAD/Actions/코드 독립 대조, 구현·실증·미확인 구분하여 읽기 전용 보고 후 STOP. 별도 '진행' 전 아무 변경/실행/커밋 금지.
