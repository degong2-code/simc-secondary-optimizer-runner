# SIMC SECONDARY OPTIMIZER — 단일 최신 인계 정본
## 2026-11-10 · 냉기 마법사 실제 제품 E2E / v305 실측 후 비국소 탐색 개선

> **지위:** 격리 브랜치 개발 지식 인계. 공식 Project UI/Work OS/main 승격 아님. 이 문서 작성 **직전** 확인한 작업 격리 HEAD는 `7d9dbd9f015341923c8adf7aefccb021f8ad42d9`(2026-11-10 08:51 UTC), main HEAD는 `07133e0aaf738d6e4816a6486057b1cd49c018de`. 인계 문서 커밋 이후 최종 HEAD가 바뀌므로 **읽을 때마다 GitHub에서 두 브랜치 HEAD를 각각 다시 조회**한다.
>
> **전임 단일 인계:** [P3-HAX 2026-11-10](CHAT_CONTINUITY_HANDOFF_20261110_P3_HAX_ADAPTIVE_MULTI_REGION_NEXT.md)는 v302/498 Native 시점의 역사 정본으로 보존한다. **현재 개발 판정은 이 인계 및 새 HEAD·CURRENT·Actions가 우선**한다.

## 1. 제품 목표, 승인 정책, 개발 권한

- **목적:** 26개 **딜러 DPS 전문화**(증강 기원사·탱커·힐러 제외)에 대해 목표 ilvl(기본 334) 또는 사용자가 수동 지정한 **최종 CHMV 총량 T**에서 SimC DPS를 최대화하는 치명/가속/특화/유연 **절대 rating** 탐색. 결과에는 관측 DPS, SEM, 95% 판정 상태, 관측 1위, 충분히 다른 근접 대안 및 비율을 표시한다. 현재 착용 장비 전체 재분배/장비 조합 추천/시즌 전체 DB/직접 proc·APL 효과 모델링은 **범위 밖**.
- **최신 승인 설계:** [v1.4.3 시즌 G/J/F/O 전체 자동 구축 정책](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)와 최신 사용자 직접 결정이 우선. 과거 업로드된 v1.4.1의 **27개·증강 기원사 포함** 문구는 역사 자료로만 해석한다. 식은 `G` 비장신구 대표 일반 장비/무기, `J` 검증 보석, `F` 최고 품질 영약, `O` 선택 무기 기름의 **비자유분배 고정 스탯**, `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. **사용자 수동 T 우선**, L/E/O 재가산·기름 중복 금지. 다른 시즌에 70783의 G/J/F/O 수치 복사 금지.
- 검증 후 최고 품질 선택지 정책 A 자동 등록; 영구마부 포함, 일반 임시마부 제외하되 기름 지원; 특수 시즌 시스템은 선택 모듈. SimC가 gear effects/procs/APL/DPS 담당, 제품은 입력·정적 rating·JSON2·후보·캐시·취소/재개·95%만 담당한다.
- **사용자 입력:** 직업/전문화/종족/특성, 목표 ilvl 또는 수동 T, 장신구2, 선택 특수장비·장식 최대2, 보석·영약·음식·기름·전투조건. 일반 대표 장비/티어4pc/무기/SimC 프로필은 내부 생성. 업로드 SimC 프로필은 선택적 캐릭터 정보 소스이지 현재 장비 총량 기준이 아님. 기본 일반보석은 **치명·가속·특화·유연 각 1개, 특수보석 선택형**.
- **2026-11-10 최신 사용자 시험 정책:** 과거 Enhancement/Ret/Frost의 **한 프로필을 매번 반복하지 않고**, 독립된 다음 실험은 가능한 한 **다른 전문화·종족·T/전투 조건**으로 일반 제품 v113→v216/v212→v098/v291 경로에서 실제 새 프로필을 구성해 누락 결함을 조기 발견한다. 단 **같은 실험 안의 알고리즘 간 공정한 비교는 반드시 동일한 새 프로필/바이너리/시즌/전투/iterations/초기 후보를 공유**한다. 사용자가 이 접근을 승인했다. 과거 exact Native 증거는 재현/캐시/회귀에 계속 활용.
- **권한:** 주 제품 개발 채팅의 소유권을 유지. 이 격리 브랜치에서만 허용된 개발·인계 수행. 별도 승인 없이 GitHub `main`, immutable `v003`, 사용자 원본 `v016`, Project Sources/Instructions 실제 UI, Work OS M0/Shared State, 공식 승격·병합 변경 금지. Work OS M0는 일반 제품 구현 중단 Gate가 아님. GitHub 문서 커밋으로 Project UI 등록 완료를 주장하지 않는다.

## 2. 코드·개발 지식의 검색 경로

먼저 [개발 시작점](development/START_HERE.md) → [기능 지도 INDEX](development/INDEX.md) → [핵심 FILE_MAP](development/FILE_MAP.md) → [증거 지도 EVIDENCE_INDEX](development/EVIDENCE_INDEX.md) → [결정/철회 DECISIONS](development/DECISIONS.md) → [기록 프로토콜](development/PROTOCOL.md)을 확인한다. 현재 A~G 개요는 [Canonical Status](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md)이나 **11/09 역사 스냅샷 설명도 있으므로 아래 최신 보충과 실제 Actions가 우선**한다. 누적 일자별 상태는 [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) **상단**만 활용하고 옛 단락의 `PENDING`을 지금 상태로 오해하지 않는다.

**주 실제 호출 경로:** `runner/v113_local_web_api.py` 사용자 FastAPI → `v216_environment_build_coordinator.py`/v217 봉인과 시즌 G/J/F/O → `v212_environment_manifest.py` 설치 → `v106_user_session_controller.py`/ `v098_target_user_scenario_bootstrap.py`의 선택 전문화 프로필 → `v096_unified_product_entry.py` / `v291_durable_multiscale_native_runner.py` → `v292_portable_native_case_cache.py` / `v293_local_longrun_session.py`; 기본 후보 `v290_multiscale_adaptive_policy.py`. v303/304/305는 실험형 opt-in.

**해당 부분만 읽을 테스트:** `tests/test_v098_source_only_one_spec_user_bridge.py`, `tests/test_v098_cross_spec_installed_G_source.py`, `tests/test_p2_fresh_user_profile_case_offline.py`, `tests/test_v305_hybrid_durable_offline.py`, `tests/test_p2_v305_hybrid_offline.py`. 실제 새 사용자 시나리오 진입: `integration_probes/p2_new_profile_product_e2e_once.py`. v305 실 측정: `integration_probes/p2_real_hybrid_v305_once.py`. 전체 파일은 [FILE_INVENTORY](development/FILE_INVENTORY.md)에서만 찾는다.

## 3. A~G 현재 진행도 (코드·오프라인·실 Native·Web 범위 구분)

| 영역 | 구현 및 실증 | 남은 부분/확정하지 말 것 |
|---|---|---|
| **A 시즌 소스/봉인** | v161/v191/v229/v217, 70783 동일빌드 원본 SHA·GJFO source 재사용, 실제 새 빈 작업공간 Build SUCCESS | **새로운 별도 시즌**의 무이력 첫 G/J/F/O Build까지 포괄 인증 아님 |
| **B 대표 장비/티어/G** | v167/v169/v230/v232/v251/v216. Ret334 `G=2850` 실제 Native; 선택 스펙 1개의 70783 자료만 재생성해 Frost 신규 프로필 성공 | Ret physical G 레코드를 **Frost의 exact Native G로 주장 금지**; 타 전문화/새 시즌 정밀 G 독립 증거 필요 시만 실측 |
| **C 4일반보석/J** | 기본 일반 치·가·특·유 각1, special0. Frost 새 제품 Native JSON2 입력 성공; 70783 `J=92` | 모든 보석·소켓 선택/품질·미래 시즌 전수 인증 아님 |
| **D 영약/기름/선택장비** | 70783 기본 `F=165`, `O=0` Build; 이전 O>0 별도 실 사용자 Native 증거 보유 | 특수 L/E/기름·모든 사용조건의 범용 E2E 미실증. 효과 자체 인증 Gate 금지 |
| **E GJFO/수동 T/설치** | 70783 일반4 빈 workspace `G2850+J92+F165+O0 = B=T자동3107`, v212 READY/설치 Native3. Frost 사용자 **수동 최종 T3300** 우선 및 정적 rating 총합 검증 | 자동 환경 `3107`과 사용자가 수동 지정한 `3300`은 **다른 값**이며 덮어쓰기 오류가 아님. 타 시즌 최초 Build 전주기·옵션 전수는 미실증 |
| **F 사용자 프로필·Native DPS·탐색** | `v098→FastAPI v113→v291` **서로 다른 전문화 Frost의 신 프로필 실제 2개 DPS 후보**·캐시 전용 재개 SUCCESS. v290 기본, v305 결합형 opt-in 실제 SimC 연구 완료 | **95% 우위/전역 최적해 미증명**, v305 효율 우위 없음, 26개 사용자 E2E·Windows 실제 브라우저/GUI 클릭 미실증 |
| **G 검증/운영/기록** | 최신 격리 focused #42785901877 **596 tests=594 PASS/2 SKIP/0 FAIL**, DEV_LEDGER_PASS, source·session·cache/journal 재개 구현 | TestClient/Actions Native와 최종 사용자 Windows 클릭 구분; 공식 제품 통합/Work OS 승격 아님 |

**상태어:** 위 A~G는 `CODE_IMPLEMENTED`, `OFFLINE_PASS`, 일부 `REAL_NATIVE_PASS`, 일부 **FastAPI TestClient 실제 subprocess E2E PASS**를 각각 갖는다. 완성 제품 또는 사람의 브라우저 클릭 `USER_WEB_E2E_PASS`는 아직 주장하지 않는다. 현재 최신 코드에서 **해결되지 않은 재현 제품 결함을 이 인계가 확인한 것은 없음**; 다음 다른 프로필에서 새로운 결함이 발견되면 재현·원본 영수증을 따로 보고한다.

## 4. 최근 작업: 신규 Frost 제품 프로필 실제 성공과 교정

- **새로 구성한 프로필:** 인간 냉기 마법사, ilvl334, 수동 **최종 T3300**, 일반보석4, 특수보석0, 기름0, 이전 Enhancement/Ret gear·input.simc/DPS 불복사. 새 사용자 profile SHA256 `4733ca451b2f2f9e2cdf1c0322086240a7fbf816a6eae4c131d71f864e811a16`.
- **성공 영수증:** [GitHub Actions #42785318578](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42785318578) **SUCCESS**, [Native input/JSON2/session artifact #13749021394](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42785318578/artifacts/13749021394) 단기 보존(2026-11-17 UTC까지, 만료 시 기록된 SHA/노트 재사용). 동일 실행에 **환경 구축 실제 Native 3회 + 새 DPS Native 2회**, 캐시 전용 재조회 신규 0. 최고 관측 rating (치명784, 가속784, 특화784, 유연948), 합계 T3300; **관측 DPS 165226.9796952423 / SEM706.3251438025171**. 2후보·한 프로필 실험이고 95% 우위 미확정. 사용자 Windows 브라우저 클릭은 하지 않음.
- **첫 실제 차단** [#42779527679](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42779527679): 같은 빌드 Ret 단일 대표 G 물리 후보를 다른 전문화에 강제 대입하려 해 `FRESH_V232_SELECTED_G_BUILD_SPEC_OR_ILEVEL_DRIFT`(HTTP422), DPS Native0. **원래 fail-closed 검증을 제거하지 않는다**.
- **두 번째 실제 차단** [#42781686192](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42781686192): `v169.build_all`이 다른 25개 전문화까지 전체 장비를 요구해 한정 소스에서 막힘(HTTP409 `LOCAL_SESSION_PRECHECK_BLOCKED`), DPS Native0. 해결: 이미 봉인한 같은 시즌 v167 일반장비/v251 티어/v229 item data를 써서 `v216._one_spec_ordinary_simc_stage`로 **사용자가 요청한 단 하나의 전문화** 후보만 0 추가 Native/0 추가 수집으로 생성하고 build/revision/spec/ilvl/SHA 확인. `v098`이 새 스펙의 대표 gear만 사용하게 연결. 일반 G 참조는 회계용으로만 재사용. 새 [회귀 테스트](../tests/test_v098_source_only_one_spec_user_bridge.py).
- 최신 코드/영수증의 이전 오류는 **수정 후 실제 Frost Native SUCCESS로 종료**됐다. 최초 두 실패를 현재 미해결 결함으로 승격하지 않는다. 해당 과정의 실시간 환경변수가 offline preflight에 상속된 문제도 별도로 교정했다.
- **최신 오프라인:** [Actions #42785901877](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42785901877) HEAD `7d9dbd9f015341923c8adf7aefccb021f8ad42d9`, 596 tests=**594 PASS/2 SKIP/0 FAIL**, `DEV_LEDGER_PASS OFFLINE_NO_NATIVE_NO_NETWORK`. 코드 성공과 제품 전체 완성은 다르다.
- 상세 [개발노트](development/notes/2026-11-10_p2-fresh-four-ordinary-cross-profile.md), [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md).

## 5. P2 탐색 실험: 구현, 실제 우열, 미실증

- v290/v291은 여전히 **기본 정책**이며 캐시/취소/재개/독립 샘플 처리 유지. v298/299/301/302의 백분율/다지역 격자·v303 지역별 개선/SEM/반경·예산 배분·v304→v291 opt-in 및 v305 **전역21 축 격자 + 분리 최대8개 지역 + 지역6격자와 v290 양방향 이웃 이동 교대 + 적응형 배분/전역 reserve**는 격리 코드 구현이다. 사용자 웹 기본 옵션으로 승격하지 않는다.
- **실제 [#42772775449](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42772775449):** 한 역사적 70783 Enhancement **특수보석** 프로필, 전역32 공통·방법당4520 requested iterations: 신규 Native **127**, 기존 compact3 + 같은 실행13 재사용. 최고 1000 iterations DPS: `v290 normalized-scout 189913.69±170.73`, `v304 adaptive 187946.03±175.29`, `fixed local6 187783.17±172.59`. `normalized-v290`는 scout cadence를 강제 통일한 **변형**이며 원래 v290 스케줄의 무조건적 우세 증거가 아니다.
- **실제 [#42776992650](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42776992650):** v305 동일 기존 initial32·방법당4520 iterations, 신규 Native **21**, 과거 exact compact **48** 관측 재사용, 1000 iterations 선택 확인 **187345.89±170.56 DPS**. 해당 한 프로필에서 v304/fixed/normalized-v290보다 낮았다. 각 실험을 따로 실행했으므로 **동일 실제 벽시계 비교가 아님**. 과거 498 Native 연구는 별도 [연구노트](development/notes/2026-11-10_p2-real-simc-global21-local6-gp-comparison.md): 원본 raw ZIP 전체는 현재 GitHub에 없어 498회를 다시 실행하거나 전체 raw cache 확보됐다고 주장 금지.
- **확인된 한계/개선 가설:** v305의 초기 regional radius 약6.5%B × 1.5로 약303 rating 이내 중심 거리만 이동 가능, 역사 v290 우수 후보는 예시상 **두 스탯 사이에 12%B 약373 rating 이동** 필요. v305는 초기 local6 12회 + v290 pairwise15회 + global reserve5회로 **최대8개 지역에 탐색 분산**. 이 제약이 관측된 낮은 결과에 기여했을 **가능성**이 있지만 실증된 유일한 원인은 아님. 새로운 정책은 `v306`이라는 **별도 identity/세션 봉인**으로 먼저 offline 비교(12%/24% B 비국소 escape·성과기반 allocation·다중 지역 최소 탐색 보호), 실측 가치가 있으면 최소 Native. 현재 인계에서 **v306 구현/Native PASS는 확인되지 않았음**.
- **통계적 정직성:** 여러 후보 중 선택한 DPS와 명목 쌍95%는 family-wise 95% 확정이 아니다. 전역 최적·26개 전문화 공통 우위도 증명되지 않았다. GP-UCB/MADS/Sobol도 동등 iterations/벽시계 완전 비교 미완료.

## 6. 캐시·증거 재사용과 효율

- 동일 시즌 **정적 아이템 캐시**를 SimC revision만으로 폐기 금지; 정정은 사용자 명시 요청. **DPS 캐시**는 실제 binary/profile/gear/options/O/combat/vector/iterations/seed 정체성별 분리. `v291` raw JSON2/원본 SHA 영수증과 과거 **compact** 연구 요약 캐시를 동일 인증 등급으로 오인하지 않는다.
- 최신 Frost 새 시나리오 자체는 별도 프로필 SHA로 과거 Enhancement/Ret DPS를 재사용 불가. 다음 독립 시나리오에서는 **서로 다른 새 사용자 설정**을 만들되 시즌 소스/단위 캐시를 그대로 재사용할 수 있는 조건이면 다시 수집·Native3를 무조건 반복하지 않는다. 매번 빈 캐시 통제 시험을 재진행하는 것도 금지.
- 498건 전수 Native 재실행, 더 정밀한 SEM 무조건 반복, 효과 인증 Gate, 불필요한 전수 전문화/ilvl 조사는 하지 않는다. 실험은 같은 iteration·시간 cap, 동일 새 프로필, 별도 새로운 Native/역사 재사용/캐시/실제 wall을 명확히 계상한다.
- 과거 Native/Actions의 7일 Artifact는 만료될 수 있으므로 영수증의 시나리오/프로필/원본 해시와 문서 SHA를 우선 재활용하고, raw 확보 실패를 재현 결함이라고 부르지 않는다.

## 7. 병목, 다음 작업 시작점 및 로드맵

**현재 병목은 새로운 시즌 엔진의 재구현이 아니라** (a) 새 사용자 전문화/설정에서 실 경로의 재사용 가능한 오류 발견, (b) v305의 초기 지역 반경 제한과 분산된 Native scout 예산 때문에 **전역 고점을 놓치는 탐색 신뢰성**이다.

**우선 REUSE → EXTEND (검증 전 새 Native 최소화):**

1. `development/notes/2026-11-10_p2-v305-real-hybrid-4520-result.md`와 compact Actions #42776992650/#42772775449에서 원본 실측·후보 분포·region radius/중복 탐색을 확인. 재생 가능한 범위 내에서 **v305의 12%/24%B 큰 이웃 이동과 보수적 지역 예산 재배분을 offline replay로 비교**; v290 기존 움직임, v302 격자, v303/304 보조 그대로 재사용.
2. 새로운 정책으로 실질 개선이 예상되면 **신규 v306 opt-in identity**로 구현하고 v291 세션 SHA/메서드·pending/journal·resume·예산 conservation을 집중 테스트. **기존 v290 기본/v305 source SHA를 덮어쓰지 않는다.**
3. 다음 **독립 제품 실험은 이전 Enhancement/Ret/Frost와 다른 26 DPS 전문화 및 사용자 설정**을 `integration_probes/p2_new_profile_product_e2e_once.py`의 기존 실사용 경로로 구성. build/source/ilvl/종족/옵션/스탯 제약이 안전하면 그 내부에서 **v290 vs v306 (필요시 fixed/305) 모두 동일 새 프로필**로 최소 실제 SimC 비교. 새 사용자 경로가 실패하면 A~G 원본 입력/대표장비/JSON2를 먼저 고치되 정책 우위를 억지로 판정하지 않는다.
4. 관측 1위와 다른 rating의 근접 대안, 95% 판정, 추적 가능한 총 iterations 및 진짜 wall-time을 결과에 분리해 기록. 빠른 탐색 품질이 확보된 뒤에만 사용자 기본 정책 교체를 검토.

**단기:** offline 현 v305 실측 재분석 → v306 설계/검증 → 새 독립 전문화의 단일 제품 E2E + 동등 자원 실 SimC 비교.
**중기:** 통계적 선택편향과 multi-region/근접 대안 품질 개선, 취소·resume/case 캐시, 여러 **서로 다른** 전문화·ilvl·고정 장비/기름·T에서 소표본 검증, Windows 실제 사용자 브라우저/GUI E2E.
**장기:** 소스가 바뀐 **진짜 새 시즌**의 G/J/F/O→B/T→선택지 최고품질/정책 A→프로필→SimC→DPS/95%/캐시를 같은 엔진으로 재사용. 26 DPS 제품 완결, 전체 장비 추천/효과 모델링 없음.

## 8. 재개 절차, 확인 범위, STOP

1. 격리와 main HEAD를 **각각 새로** 조회; 이 문서 내 작성 전 HEAD는 정확 기준 스냅샷일 뿐 최신 HEAD 고정 아님.
2. 이 인계 → [START_HERE](development/START_HERE.md) → [INDEX](development/INDEX.md) A~G → [FILE_MAP](development/FILE_MAP.md) → [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md) → [DECISIONS](development/DECISIONS.md) → [PROTOCOL](development/PROTOCOL.md) → [CURRENT 상단](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) → [v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 순서로 필요한 범위만 확인. 최신 Frost 실패→성공 노트와 v305 실측 노트만 추가 조회.
3. 새 채팅 첫 응답은 **읽기 전용 독립 복원 결과 보고**만 한다. 최종 목표, 실제 HEAD, A~G의 구현/오프라인/실 Native/TestClient E2E/미실증, 최근 수정·실패 교정, 병목, 다음 일, 단·장기 로드맵만 보고 **STOP**.
4. 사용자가 별도 **'진행'**이라고 승인하기 전 코드/문서 편집, 테스트, Actions, 실제 Native SimC, 외부 수집, 고비용 실행, 커밋·병합, 공식 승격 절대 하지 않는다. 주 제품 개발 채팅 소유권을 넘겨받지 않는다.

## 9. 새 채팅 시작 프롬프트

~~~text
# SIMC SECONDARY OPTIMIZER — 독립 복원 (최신 v305 실 SimC / 신규 Frost 제품 E2E 인계)

프로젝트를 읽기 전용으로 독립 복원하라.

저장소: degong2-code/simc-secondary-optimizer-runner
격리 브랜치: probe/chat-cache-v035-20261024
이 인계 문서 작성 직전 격리 HEAD: 7d9dbd9f015341923c8adf7aefccb021f8ad42d9
main 기준 HEAD: 07133e0aaf738d6e4816a6486057b1cd49c018de
최신 단일 인계 정본: docs/CHAT_CONTINUITY_HANDOFF_20261110_P2_FRESH_FROST_V305_NEXT.md

첫 작업:
1. 격리/main HEAD를 각각 독립 조회하고 실제 최신 HEAD·최근 코드 변경·Actions와 인계 내용을 대조한다. 과거 HEAD를 최신이라고 가정하지 않는다.
2. 인계 정본 → docs/development/START_HERE.md → INDEX/FILE_MAP/EVIDENCE_INDEX/DECISIONS/PROTOCOL → docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md 상단 → v1.4.3 승인 정책 → 두 최신 실측 개발 노트 순서로 필요한 부분만 조사한다.
3. 목표: 26 DPS(증강 기원사/탱커/힐러 제외), 목표 ilvl 또는 수동 최종 T를 기준으로 SimC 최대 DPS의 절대 CHMV rating. 시즌 G/J/F/O 모두 매 시즌 자동 검증, B=G+J+F/T=B+O, 수동 T 우선; SimC 효과 책임 유지. 기본은 일반보석 치·가·특·유 각1/특수 선택형.
4. 11/10 최근 실제 #42785318578은 Human Frost Mage ilvl334/수동 T3300/일반4/특수0/O0로 환경 Native3, DPS Native2 및 FastAPI TestClient/재개/캐시 PASS, 관측 DPS165226.98±SEM706.33, rating784/784/784/948. 최초 cross-spec G 레코드 불일치와 all26 gear fallback 실패는 요청 전문화 **하나만** source-backed 후보 생성하도록 수정 후 실증 PASS. 이걸 26개 전문화 또는 Windows 실제 브라우저 완성으로 승격 금지. 최신 focused #42785901877 596=594 PASS/2 SKIP, ledger PASS.
5. v305 global21+지역6격자+v290 이동+적응형 지역 자원 결합은 opt-in 코드 및 #42776992650 실제 Native21/과거 compact48 재사용 PASS이나 단일 역사 Enhancement 특수보석 조건에서 v290 normalized보다 DPS 낮음. 기존 v290 기본 유지, 전역 최적/familywise 95% 입증 없음. v305 초기 지역 6.5%B×1.5 이동 제한과 최대8개 지역 분산을 기존 관측값으로 먼저 offline 재분석; **v306 비국소 12%/24%B escape는 아직 검증/구현 완료로 주장 금지**.
6. 사용자 최신 시험 결정: **독립 새 실험마다 다른 제품 생성 프로필/전문화/설정**으로 실제 사용자 경로 오류를 함께 발견. 다만 **한 공정 알고리즘 비교 안에서는 똑같은 신규 프로필·바이너리·환경·iterations/예산** 사용. 역사 exact Native/동일 시즌 source/caches는 유효한 범위에서 재사용하고 498 Native 반복 금지.
7. A~G 상태, 완료·부분·오프라인 PASS·실 Native PASS·TestClient E2E·미실증·이미 해결한 실패를 구분하고, 실제 병목/다음 작업 및 단기·장기 로드맵을 제시한다. 기존 주 제품 채팅의 개발 소유권, 격리 브랜치, main/v003/v016/Project UI/Work OS 권한을 보존한다.

**첫 응답은 위 자료의 읽기 전용 독립 복원 보고만 하고 즉시 STOP하라.** 사용자가 별도로 '진행'이라고 승인하기 전 코드·문서 변경, 테스트, Native SimC, 외부 수집, GitHub Actions 실행, 고비용 작업, 커밋·병합·공식 승격을 시작하지 말 것.
~~~
