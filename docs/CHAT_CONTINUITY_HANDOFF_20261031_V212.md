# SIMC SECONDARY OPTIMIZER — 2026-10-31 v212 정본 인계

**문서 목적:** 삭제된 직전 채팅의 첨부 `LAST-CHAT(3).txt`를 시작 자료로 삼되, 그 안의 보고를 실제 격리 브랜치·최신 CURRENT·Developer Notes·코드·Actions 로그와 대조하여 다음 일반 채팅이 프로젝트를 재시작하지 않고 정확히 이어가게 한다.

**인계 상태:** 문서/상태 보강 완료. 2026-10-31 DPS 26개/증강 제외 범위 교정도 문서 전용으로 반영했다. 제품 코드 변경·Native 실행·새 Actions 실행·main 병합·배포·Project UI/Work OS 승격은 수행하지 않았다. 다음 채팅의 첫 응답은 복원·검증 보고만 하고 사용자의 **`진행`** 전까지 중단해야 한다.

## 0. 실제 저장소 스냅샷과 증거의 기준

- Repository: `degong2-code/simc-secondary-optimizer-runner`
- Branch: `probe/chat-cache-v035-20261024`
- 공개 상태: **Public** (이번 인계에서 visibility 변경 없음)
- 인계 문서 갱신 직전 branch HEAD: `4e50962c70d3a50017d9d8f79df41e7e0daadab1`. 이 문서를 추가하면 HEAD는 문서 커밋으로 이동하므로, 새 채팅은 반드시 실제 HEAD를 다시 조회한다.
- 확인 당시 `main` HEAD: `07133e0aaf738d6e4816a6486057b1cd49c018de`. 이 인계는 main에 쓰지 않았다.
- P3-A 최종 검증 Actions: [#41160002104](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41160002104), 실행 commit `475768bf91531e76e3ad06eda624b3979d8e9145`, SUCCESS. Ubuntu 24.04와 Windows 2022 job 각각 **9/9 tests PASS**, 모듈 compile PASS, `V212_ENVIRONMENT_MANIFEST_NATIVE0_PASS`.
- #41160002104 실행 이후 당시 HEAD `59eb71b09c414648b114e0b5ec10401cf2d8832e`까지는 3개 문서만 변경되었다. 그 뒤 이번 인계 준비도 CURRENT, Developer Notes, P3 설계, Windows guide의 문서 변경만 했다. 실행 commit과 현재 branch HEAD 사이 compare에서 변경 파일은 문서 4개뿐이며 v212 코드·테스트·workflow는 변경되지 않았다.
- #41160002104에는 업로드 artifact가 없다. job logs를 직접 확인했으며 양 OS 모두 `Ran 9 tests ... OK` 및 Native0 marker가 남아 있다.
- 최신 branch Actions는 [Windows source beta #41161740839](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41161740839): Windows Server 2022 Python 3.12/3.14 각각 101 tests PASS, ZIP 2 tests PASS, extracted launcher check, localhost HTTP security 및 징벌334/분노321/냉법344 3개 plan PASS, 기존 cache-only 6/6 HIT, 신규 Native0. Artifact [#13027326887](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41161740839/artifacts/13027326887), ZIP SHA256 `08c56925e0520e17d78392ef2740e00b09f67b6005acc6a9021b462da2ca66d0`, expiry `2026-11-07T02:50:50Z`. This is source beta packaging/HTTP plan evidence, not user-PC GUI, actual SimC Native, or Environment Build UI acceptance.
- **주의:** 위 9×2 테스트는 synthetic JSON fixtures와 dummy binary를 사용한 계약 테스트다. 실제 운영 v191/v211/v196/v098 산출물을 연결한 종단 간 제품 실행이 아니다.

## 1. 새 채팅의 필수 읽는 순서

새 채팅은 다음 순서를 지킨다. 처음부터 모든 과거 문서를 전수 재감사하지 않는다.

1. GitHub에서 repository visibility, 지정 branch, 실제 최신 HEAD, 최신 branch Actions, main HEAD를 읽기 전용으로 확인한다. public/private 상태를 변경하지 않는다.
2. 이 문서 전체를 읽는다.
3. `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 최상단 P3-A/v212, P3 장기 목표, v211/v210 최신 상태를 읽는다. 아래쪽의 오래된 버전 이력은 현재 상태로 재해석하지 않는다.
4. `docs/DEVELOPER_NOTES_v1.4.2_LATEST_USER_POLICY_ADDENDUM_20261030.md` §1, §7, §8 및 `docs/DPS26_SCOPE_CORRECTION_20261031.md`를 읽는다. **v1.4.2와 2026-10-31 직접 정정이 현재 승인 범위**다. 최초 업로드 v1.4.1 사본의 27 DPS/증강 포함은 오기이며, 교정된 v1.4.1 교체본은 26 DPS/증강 제외다.
5. `docs/P3_ENVIRONMENT_BUILDER_TARGET_ARCHITECTURE_20261031.md` 전체를 읽는다. 특히 §7 roadmap과 §8 v212 실제 구현/제한을 함께 본다.
6. `WINDOWS_BETA_START_HERE.md`의 상단 P3-A/v211/v210 안내와 사용자 시작 절차를 읽는다. 이 guide 및 현재 ZIP은 원클릭 Environment Build가 배포되었다는 뜻이 아니다.
7. P3-A를 확인할 때만 다음을 읽고 실제 Actions #41160002104 로그와 대조한다.
   - `runner/v212_environment_manifest.py`
   - `tests/test_v212_environment_manifest.py`
   - `.github/workflows/v212_environment_manifest_offline.yml`
8. P3-B를 설계할 때는 다음 기존 계약을 필요한 범위만 읽는다.
   - `runner/v191_unified_season_data_update.py`, `.github/workflows/v191_unified_season_data_update.yml`
   - `data/current_season_simc_enchant_candidates.json`
   - `runner/v211_enchant_source_effect_classification.py`, `data/current_season_enchant_effect_classification.json`, `.github/workflows/v211_enchant_source_effect_classification.yml`
   - `runner/v196_current_season_user_catalog.py`, `runner/v197_enchant_effect_families.py`, `.github/workflows/v211_enchant_catalog_integration_offline.yml`
   - 해당 테스트 파일들
9. P3-C 이후에만 v098/v208/v046/v062/v093/v094/v095의 접합부를 확인한다. 기존 P1 Windows 실측 영수증은 이 문서 §4 범위로 재사용한다.

이 문서는 2026-10-31 v203 정본 `docs/CHAT_CONTINUITY_HANDOFF_20261031_V203.md`를 대체하는 최신 P3-A/v212 handoff다. v203 문서는 역사적인 v203 마부·Windows 증거를 확인할 때만 보조 참조한다.

## 2. 승인된 제품 목적과 변경 불가 경계

### 2.1 현재 유효한 전문화 범위

**DPS 26개 전문화만 지원한다. 증강 기원사, 탱커, 힐러는 제외한다.**

- 최초 업로드 v1.4.1 사본 및 과거 handoff에 남은 27 DPS/증강 포함은 범위 오기다. 2026-10-31 v1.4.1 교정본과 v1.4.2 §8은 26 DPS/증강 제외를 명시한다.
- **26개 범위의 코드·실증 대조:** `runner/v143_specialization_contracts.py`는 26개 specialization contract를 보유한다. `integration_probes/v176_all_26_source_first_physical_native.py`는 `len(ALL)==26`과 `ALL == sessions.SUPPORTED`를 강제하고, `tests/test_v176_all_26_source_first_physical_native.py`는 `evoker/augmentation` 부재를 확인한다. 기존 [#40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357) 로그는 `FINISHED_ALL_26_PHYSICAL_PASS` 및 26 PASS, 신규 Native 25회+기존 성기사 영수증 1회 재사용을 확인한다. 물리 smoke 범위이며 26개 전부의 적응형 최적화 E2E 증거는 아니다. 이번 교정에서 이를 재실행하지 않는다.
- 지원 전문화의 목적함수는 SimC DPS 최대화다.
- 기본 목표 ilvl은 334이며, 목표 ilvl 또는 사용자가 직접 입력한 기름 포함 최종 CHMV 총량 T를 기준으로 미래 파밍 목표가 될 치명·가속·특화·유연의 **최적 절대 rating**을 찾는다.
- 현재 착용 장비를 재분배하는 도구가 아니며, 전체 장비 조합 추천·아이템 획득 경로 추천·전 시즌 loot DB 탐색기로 범위를 넓히지 않는다.

### 2.2 사용자 입력과 내부 환경

일반 사용자는 직업·전문화·종족·특성, 목표 ilvl 또는 수동 최종 T, 장신구 2개, 선택 특수효과 장비, 장식 최대 2개, 보석·소모품·기름·전투조건을 고른다. 일반 방어구·무기·티어 4세트·대표 프로필·기본 예산은 내부에서 구성한다. 선택 업로드 SimC 프로필은 캐릭터/특성 추출용 편의 기능이며, 업로드한 현재 장비와 현재 CHMV를 목표 예산으로 복사하지 않는다.

### 2.3 CHMV 회계

- `T=G+J+F+O`, `B=G+J+F`, `T=B+O`, `c_final=c_base+o`.
- 무기 기름 O는 실제 적용 가능한 무기에만 고정 벡터로 한 번 반영한다.
- 선택 특수장비의 정확한 정적 L은 G/B 안에 이미 포함되므로 스탯별 하한으로 보호하고 다시 더하지 않는다.
- 보석 J, 영구 마부 E, 특수장비 bare L을 서로 혼동하지 않는다. 마부를 선택했다는 사실만으로 B/T가 변하지 않는다. 자동 ilvl 기준에서 정확히 확인된 영구 정적 CHMV E만 기존 v204 규칙에 따라 반영한다. 비CHMV 7967은 B/T 불변이며 수동 최종 T는 선택 효과 때문에 다시 증가시키지 않는다.
- 장신구 정적 JSON2 레코드 미출력은 0이라는 뜻이 아니다.
- SimC가 장비효과·proc·APL·buff·DPS를 계산한다. 우리 코드는 원본/ID/옵션/부위/프로필/예산/정적 JSON2 정합/후보·통계·캐시·취소·재개·오케스트레이션을 담당한다. 독립 효과 엔진이나 별도 optimizer를 만들지 않는다.
- 통계 표시는 95%만 사용한다. 관측 DPS 1위, 95% 통계적 우위, 전역 최적해 증명은 서로 구분한다.

### 2.4 엔진 중심의 최종 제품 목표

최종 제품은 다음을 결합한 **원클릭 Environment Builder**다.

1. 시즌 장비 수집 DB
2. SimC 원본 및 DB2/item source 기반 자동 발견·분류·부위 적용성·효과 출처·정적 스탯 분석과 자가검증 엔진
3. 검증된 카탈로그 및 versioned Environment Manifest
4. 기존 v098 대표 프로필/예산 및 v208 선택 L, v046/v062 캐시
5. 기존 v093/v094/v095 적응형 SimC 최적화 엔진

개별 마부 38종 UI가 최종 목적이 아니다. 새 시즌·아이템·마부·보석·장식·특수장비를 사용자가 일일이 알려주거나 매번 하드코딩하지 않아도, 엔진이 승인된 원본에서 후보를 발견하고 정확 ID·slot mask·옵션·효과·출처 SHA·검증 범위를 정리해야 한다. Build는 명시적 요청형 증분 동기화이며 상시 polling이 아니다. 변경되지 않은 source identity/hash 및 Native/DPS 캐시는 재사용하고, 실제 변경된 의존성만 무효화한다. Plan은 Native0, 명시적 Start에서 선택한 미관측 정적 L/E만 필요한 최소 Native로 확인한다. UNKNOWN은 0이나 선택 가능으로 추정하지 않는다.

## 3. 현재 구현 상태 — 완료와 미완료를 구분

### 3.1 기존 구성요소의 역할

| 구성요소 | 현재 역할 | 실제 상태 |
|---|---|---|
| v161–v190 | API-first/zero-seed 시즌 원본·장비·티어·소모품·효과 후보 수집 | 여러 기존 collector와 증거 보유. 새 collector 중복 생성 금지 |
| v191 | source-pinned 시즌 후보 aggregator | 후보 JSON 생성. Native0·자동 UI 승격 없음. v211/v196 직접 handoff는 아직 없음 |
| v211 | 고정 SimC revision 기반 영구 마부 38종 원본 분류 | 38행 소스 분류 완료. 일반화된 Native E나 38종 사용자 허용 아님 |
| v196/v197 | 기존 UI option catalog와 효과군/승인 경계 | 38종 읽기 전용 카탈로그, 현재 선택 가능 7967 한 범위. 고정 source candidate JSON을 읽음 |
| v098 | 사용자 입력 → 내부 대표 프로필/예산 | 일부 source-backed archetype과 source-independent 경로. `all_specs_ready=false`; 26개 전체 공급 아님 |
| v208 | 선택한 특수장비 bare L을 필요한 경우 Start 시 Native 최대 1회 조회, cache snapshot | 특정 Windows 실제 사용 조건에서 검증됨. v212에 독립 receipt input으로 연결된 상태는 아님 |
| v046/v062 | 정적 아이템 Native cache와 G/B/L/J/O 예산 브리지 | 기존 캐시와 계산 규칙 재사용 |
| v093/v094/v095 | 적응형 SimC 후보 평가, DPS/SEM/95%, 의미 있는 대안, 캐시·취소·재개 | 기존 optimizer. 새 엔진으로 대체 금지 |
| v212 | 기존 산출물의 내부 Environment Manifest assembler | 첫 계약 구현 PASS. 실제 생산 파이프라인이나 사용자 Build 기능은 아님 |

### 3.2 P3-A v212 구현 및 실제 Actions 증거

코드:
- `runner/v212_environment_manifest.py` — Git blob SHA `cd56a43b5dfeea5558377140169e564814c98d64`
- `tests/test_v212_environment_manifest.py` — Git blob SHA `bee76d5f9dbe0b2920827fe646ffd568a1699545`
- `.github/workflows/v212_environment_manifest_offline.yml` — Git blob SHA `8e9d7b8c7f16a6b047e8316e51bc828ca7b117cf`

v212는 이미 생성된 v191 season-candidate JSON, v211 enchant-classification JSON, v196 approved UI-catalog JSON, v098 preparation result와 target folder를 입력받는 결정적 manifest assembler다. collector, network API, SimC binary, optimizer를 호출하지 않는다. 다음을 검사한다.

- v191/v211/v196/v098 schema
- v191/v211/v196 사이 동일 game build와 정확한 40-hex SimC revision
- 현재 시즌 마부 38행 및 UI selectable count 1
- source candidate/classifier의 Native0 및 no-auto-promotion
- v098 READY plan, target archetype/ilvl/B/T, generated manifest와 profile/scenario/fillers/manifest 4개 파일
- SimC binary SHA, optional static-cache SHA, target file SHA
- source/build/revision/approval/path mismatch fail-closed
- 로컬 절대경로/전체 사용자 프로필을 결과에 복사하지 않는 relocation-stable digest

실제 [Actions #41160002104](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41160002104)는 Ubuntu 24.04 및 Windows 2022 각각 9/9 PASS, compile PASS, Native0 marker PASS다. relocation stability 테스트도 포함한다. 이 테스트는 temporary directory에 synthetic v191/v211/v196/v098 JSON과 dummy binary를 만들어 실행했다. **실제 production artifacts를 넣은 E2E가 아니며, 26 DPS profile coverage나 Windows 사용자 UI 인증도 아니다.** run에는 artifact가 없다.

### 3.3 v212에서 발견된 계약 경계/하드닝 항목

다음은 9×2 테스트 실패가 아니라 코드 검토로 확인한 후속 과제다. 완료로 표시하지 않는다.

1. `bootstrap_sha` 인자가 `compile_manifest`에 전달되지만 현재 사용되지 않는다. 출력은 v098의 정규화된 일부 identity와 생성 파일 SHA를 포함한다. raw bootstrap-result SHA를 포함하지 않는 설계라면 relocation invariance를 보존하는 정규화 계약을 명시하고, 아니라면 수정한다.
2. v212는 UI selectable count가 1인지 검사하지만 **그 유일한 ID가 정확히 7967인지 자체 검증하지 않는다.** v196 별도 테스트는 7967을 확인하지만 manifest 경계도 exact ID를 확인하도록 보강해야 한다.
3. 마부 candidate 38행 및 selectable 1은 현 시즌 고정 상수다. 현재 시즌 검증 계약으로는 유효하지만 season-agnostic engine이라고 부르지 않는다.
4. v208 선택 bare-L receipt는 v212의 별도 input이 아니다. 현재 v098 target manifest의 optional static-cache SHA만 참조한다. 선택 L receipt의 정확한 identity/scope 연결은 P3-C에서 통합해야 한다.
5. digest가 변경 입력을 구별하는 것은 구현됐지만 production dependency graph, changed-only invalidation/orchestration은 구현되지 않았다. 현재 `unresolved_dependencies`는 고정 목록이며 dynamic missing-join report가 아니다.
6. P3-A의 실제 source-to-catalog 연쇄 실행 및 real artifact E2E는 미완료다.

### 3.4 P2 v211 마부 분류 — 정확한 증거 범위

- SimC revision: `710c2408bfd3ae4df71b8cd55cdf01f63fd6c926`
- Game build: `12.1.5.70575`
- 38 rows: token/rank/item class/inventory mask/subclass mask, DBC static components, spell source, SimC custom handler source classification.
- 분류 카운트: static CHMV rating 8, static non-CHMV only/mixed 19, spell effects 15, Native E measured 2. 카테고리는 서로 중첩될 수 있다.
- 정적 CHMV 8종: 반지 특화 7965/7969, 치명 7995/7997, 가속 8021/8025, 유연 8023/8027.
- 실제 Native E는 7967=0 한 Windows 징벌334 조건, 8025=가속+30 한 Linux 냉법334/finger1/item158366 조건이다. 8025는 개발 전용이고 일반 UI에서 잠금.
- 현재 사용자 선택은 7967 한 범위만 유지. 나머지 37종은 잠금이며 8025는 개발 전용, 나머지 36종도 잠금.
- 따라서 정적 CHMV 8종 중 8025 외 **7종은 정확 Native E 미측정**이다. 38종 소스 분류는 모든 전문화·모든 부위/손 위치·효과량·Native 수치 인증이 아니다.
- 부위 정보는 원본 mask 기반이다. v196은 머리/어깨/가슴/발/반지의 mask를 slot group으로 매핑한다. 무기 10종은 inventory mask가 0이며 subclass mask만 있으므로 **정확한 main-hand/off-hand 적용성은 아직 인증되지 않았다.** 따라서 38종 모두가 모든 물리 부위에서 완전히 slot-certified라고 표현하지 않는다.
- 현재 v211 생성 코드와 runtime manifest의 limitations 문구는 여전히 “other six static CHMV ring enchants”라고 적혀 있다. 실제 미측정은 7종이다. 수치/선택 경계에는 영향 없는 설명 오류이며 후속 v211 산출물 갱신 때 7로 교정한다.

최근 관련 offline evidence:
- v211 source compile [#41155772497](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41155772497): Ubuntu/Windows 각각 6 tests, 38-row source pin/manifest match, Native0.
- v211→기존 catalog 통합 [#41155959636](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41155959636): 각 OS 56 tests, Native0, selectable 7967 한 개 유지.
- UI regression [#41155959593](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41155959593): PASS.
- Windows source beta [#41155959570](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41155959570): Python 3.12/3.14 SUCCESS.
- v211 문서 반영 후 이전 beta 재패키징 [#41157484148](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41157484148): Python 3.12/3.14 SUCCESS, artifact #13025173397. 이번 handoff 문서 갱신 후 재패키징은 하지 않았다.

## 4. 기존 Native/Windows 증거 — 재사용하되 범위를 넘기지 말 것

| 증거 | 실제 범위 | 금지되는 과장 |
|---|---|---|
| v203 Linux 8025 | 냉법334 전체 프로필, finger1/item158366, SimC 710c240, Native 6/6 PASS 및 동일 세션 cache 6/6 HIT, E=haste+30 | Windows/다른 전문화·장비·특성 검증 아님 |
| v207 Windows 7967 | 징벌334, 7967, Native 6회와 cache 6/6 HIT, E=0, B3150/T3182, 95% 결과 | 모든 마부/전문화의 E0 증명 아님 |
| v205 Windows 기본 경로 | 징벌334, 영구 마부 미선택, Native6, cache6/6, B3150/O32/T3182, DPS/SEM 결과 | 마부 선택 또는 전체 26 spec 인증 아님 |
| v210 Windows 특수장비 경로 | 정기 주술사331, 특수 목걸이268250, gem 240900/240900 유지, bare L Native1, DPS Native6, cache6/6, L=(crit93, haste305, mastery0, vers0), B3110/O32/T3142 | 모든 특수장비·마부 조합·26 spec·Windows PC 직접 GUI 클릭 인증 아님 |

이전 Native 및 SHA cache evidence는 해당 exact identity가 유지되는 범위에서 재사용한다. 이번 인계 때문에 v203/v205/v207/v210 Native를 다시 실행하지 않았다. 다른 profile/binary/item/options/fight identity로 넓혀 재사용하지 않는다.

## 5. P3-B의 실제 접합 결손과 가장 효율적인 다음 작업

**다음 핵심은 P3-B: v191 → v211 → v196의 versioned source/catalog handoff다.** 단, P3-A 코드 리뷰의 작은 계약 보강을 이 작업에 묶어 처리한다.

현재 실제 코드 경로:

1. v191 `runner/v191_unified_season_data_update.py`는 `out/v191_unified_source_first_catalog.json`을 만든다. 이 안에 `enchants.current_season_midnight.highest_rank_candidates`와 source/build/revision/provenance가 있다. source 후보는 Native0, automatic UI promotion=false다.
2. 현재 v211 workflow는 이 최신 v191 output artifact를 직접 받지 않는다. 대신 고정 파일 `data/current_season_simc_enchant_candidates.json`(schema `v196_source_first_enchant_candidates_v1`, source artifact ID `12961140046`, 38 rows, fixed build/revision)을 읽어 pinned SimC DBC/spelltext/handler를 분류한다.
3. v196도 같은 고정 `data/current_season_simc_enchant_candidates.json`을 읽고, source artifact ID와 related source counts를 고정값으로 검증한 뒤 v211 runtime classification manifest를 결합한다.
4. 따라서 현재 v191 season aggregator → v211 classifier → v196 catalog는 실제 production artifact 하나로 자동 연결된 파이프라인이 아니다. v212도 이미 생성된 JSON들을 인자로 받아 manifest를 만드는 내부 CLI일 뿐 자동으로 이 단계를 실행하지 않는다.

권장 구현 순서:

- P3-A manifest hardening: v212가 정확 selectable ID 7967을 검사하고, v098 identity/SHA 계약을 명시하며, 현 시즌 고정 수치와 season-generic schema를 구분한다. v208 selected-L receipt는 P3-C로 분리해 억지로 P3-A에 포함하지 않는다.
- P3-B source adapter/artifact contract: v191 `highest_rank_candidates`에서 v211/v196 공통 입력 schema를 생성한다. 정확 token/ID/rank/item class/inventory mask/subclass mask/build/revision/source artifact ID·SHA를 유지하고, 미확인 필드는 추정하지 않는다.
- v211은 이미 `--candidates` 입력을 받으므로 새 후보 artifact를 그대로 사용하도록 연결한다. SimC source pin은 기존 revision으로 유지하며 DBC/handler 분류 로직을 재구현하지 않는다.
- v196은 고정 경로/source artifact ID/related counts에 묶인 읽기 방식을 versioned artifact 입력으로 바꾼다. 기존 approval gate와 7967 단일 selectable을 보존한다. 8025 및 나머지 36종은 자동 승격하지 않는다.
- 부위별 카탈로그는 exact inventory/subclass mask 및 item join으로 구성한다. 무기 mask 0은 손 위치 허용으로 추정하지 않는다. 동일 효과/동일 부위/비교 가능한 rank만 묶고, 치명/가속/특화/유연 등 다른 효과를 합치지 않는다.
- v212는 그 동일 source artifact hashes와 resulting v196 catalog identity를 manifest에 묶는다. source dependency changed-only invalidation은 별도 단계로 분명하게 구현한다.
- v211 stale “six” 문구를 “seven”으로 교정하고 runtime manifest를 갱신한다. 해당 설명 수정은 Native를 요구하지 않는다.

효율 정책:
- 기존 v191/v211/v196 collector, classifier, catalog, source snapshots와 Actions receipts를 재사용한다.
- P3-B는 우선 offline/source artifact contract tests로 검증한다. 변경이 Native input identity를 실제로 바꾸지 않으면 Native를 실행하지 않는다.
- 38×26, 26×모든 장비, 전체 시즌 Native matrix를 돌리지 않는다.
- 매 변경마다 Native 중복 실행, cache identity, memory, I/O, runtime, 구조 단순화를 검토한다.
- 기존 v093/v094/v095 optimizer와 v046/v062 cache/budget, v098 profile builder, v208 selected-L path를 복제하지 않는다.

## 6. 단기·장기 로드맵

| 단계 | 목표 | 현재 상태 |
|---|---|---|
| P3-A | versioned manifest/readiness contract, Native0 preview | v212 첫 구현 및 9×2 synthetic contract PASS. production E2E와 위 hardening은 미완료 |
| P3-B | v191→v211→v196 source/catalog artifact handoff, 정확 부위별 catalog | **다음 권장 작업** |
| P3-C | 승인 선택 → v098 profile/예산 → v208 selected L → 기존 optimizer, 26 DPS profile suppliers | 미완료 |
| P3-D | Windows 원클릭 Build/Start, progress, cancel/resume, incremental update/cache/evidence report | 미완료 |

장기적으로 사용자가 프로그램을 열고 한 번의 Build로 최신 시즌 자료와 검증된 실행 환경을 준비한 뒤 Start로 기존 SimC 최적화를 실행하게 한다. 사용자에게 source artifact, filler/seed vector, 전체 장비 DB, 내부 manifest를 직접 준비시키지 않는다.

## 7. 이번 인계에서 실제 갱신한 파일과 미갱신 항목

이번 handoff 준비에서 격리 브랜치에 문서만 갱신했다.

- `docs/P3_ENVIRONMENT_BUILDER_TARGET_ARCHITECTURE_20261031.md`: P3-A를 v212 첫 구현으로 정정, synthetic-only 증거 및 코드 리뷰 결손, P3-B next 반영.
- `docs/DEVELOPER_NOTES_v1.4.2_LATEST_USER_POLICY_ADDENDUM_20261030.md`: P3-A 구현 범위, v191→v211→v196 실제 handoff gap, v212 hardening, v211 “six/seven” 설명 오류 반영.
- `WINDOWS_BETA_START_HERE.md`: P3-A 오프라인 결과를 각 OS 8/8에서 9/9로 교정하고 synthetic-only 범위 명시.
- `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md`: P3-A 증거의 synthetic-only 범위 및 본 handoff 정본 링크 추가.
- 이 파일 `docs/CHAT_CONTINUITY_HANDOFF_20261031_V212.md`: 새 채팅 복원 정본 및 시작 프롬프트.

**갱신하지 않은 것 / 미승격:**
- v212/v191/v211/v196/v098/v208 실행 코드와 tests/workflows: 변경 없음.
- v211 script/runtime manifest의 “other six” 문구: 이번에는 코드/data 수정 및 CI를 하지 않았으며 P3-B 작업 때 7로 교정할 항목으로 기록.
- Windows beta ZIP: Windows guide 9/9 범위 교정으로 workflow가 자동 실행되어 [#41161740839](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41161740839)에서 새 artifact #13027326887이 생성됐다. SHA256은 `08c56925e0520e17d78392ef2740e00b09f67b6005acc6a9021b462da2ca66d0`; 2026-11-07T02:50:50Z까지 보관된다. 이 ZIP은 최신 Windows guide와 소스 베타를 포함하지만 Environment Build 버튼/API/원클릭 통합을 제공하지 않는다. 이 handoff doc 자체가 ZIP에 포함됐다고 주장하지 않는다.
- GitHub `main`, immutable v003, 원본 v016, repository visibility: 변경 없음. Repository는 확인 당시 Public.
- ChatGPT Project Sources/Instructions UI 및 공식 Work OS/M0/Shared State: 실제 적용/승격하지 않았다.
- 실제 production artifacts를 넣은 v212 E2E, v191→v211→v196 자동 연결, v208 receipt manifest 통합, 26 DPS 전체 profile supplier, Windows Environment Build 버튼/one-click UX: 미완료.
- 새 Native/새 Actions: 이번 handoff를 위해 추가 실행하지 않았다. #41160002104 및 이전 valid evidence를 재사용했다.

## 8. 새 채팅 시작 프롬프트 — 첫 응답 후 반드시 대기

아래 내용을 새 일반 채팅 첫 메시지로 사용한다.

---

너는 **SIMC SECONDARY OPTIMIZER** 기존 주 제품 개발 채팅의 후속 담당자다.

**첫 응답은 상태 복원·검증 보고까지만 수행하고, 내가 “진행”이라고 하기 전에는 구현·파일 수정·Actions 실행·Native 실행·배포를 시작하지 마라.**

GitHub 저장소 `degong2-code/simc-secondary-optimizer-runner`의 격리 브랜치 `probe/chat-cache-v035-20261024`에서 먼저 실제 최신 HEAD, repository visibility, main HEAD 및 최신 Actions를 읽기 전용으로 확인하라. 다음 순서로 읽어라.

1. `docs/CHAT_CONTINUITY_HANDOFF_20261031_V212.md` 전체
2. `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 최상단
3. `docs/DEVELOPER_NOTES_v1.4.2_LATEST_USER_POLICY_ADDENDUM_20261030.md` §1 및 §7
4. `docs/P3_ENVIRONMENT_BUILDER_TARGET_ARCHITECTURE_20261031.md` 전체
5. `WINDOWS_BETA_START_HERE.md` 상단과 현재 사용자 실행 절차
6. 필요한 경우에만 v212 code/test/workflow, v191/v211/v196/v197의 실제 source handoff 계약과 Actions logs

최신 사용자 승인 제품 범위는 **증강 기원사·탱커·힐러를 제외한 DPS 26개 전문화**다. 최초 업로드된 v1.4.1 사본과 과거 문서의 27 DPS/증강 포함은 범위 오기이며, 교정된 v1.4.1 교체본은 26개로 일치한다.

최종 제품은 목표 ilvl 또는 수동 최종 T를 기준으로 미래 파밍 목표가 될 CHMV 최적 절대 rating을 기존 SimC DPS 엔진으로 찾는다. 예상 DPS·SEM·95% 판정·실질적으로 다른 대안·캐시·취소·재개를 제공한다. 최종 장기 목표는 **장비 수집 DB + SimC 원본 기반 자동 발견/분류/자가검증 엔진 + 기존 profile/budget/optimizer를 결합한 원클릭 Environment Builder**다. 개별 마부 목록/장비 DB가 목적이 아니며, 장비 조합 추천이나 별도 효과/proc 계산 엔진으로 확대하지 않는다.

v212 P3-A는 synthetic fixture 기반 Ubuntu/Windows 각 9/9 PASS의 내부 manifest assembler다. 실제 v191/v211/v196/v098 production artifact E2E나 사용자 Build UI가 아니다. `bootstrap_sha` 미사용, exact selectable ID 7967 미검사, 현 시즌 38/1 상수, v208 receipt 별도 미연결 등 handoff에 기록된 hardening gap을 완료로 표시하지 마라.

가장 효율적인 다음 작업은 P3-A manifest contract hardening을 P3-B source/catalog handoff와 묶어 **실제 v191 artifact → v211 classification → v196 approved catalog**의 versioned provenance/SHA/slot-mask 연결을 만드는 것이다. 현재 v211/v196이 고정 파일 `data/current_season_simc_enchant_candidates.json`을 읽는 gap을 해소하되 기존 수집기/분류기/catalog/optimizer를 재사용한다. 7967 외 사용자 선택을 자동 승격하지 않는다. v211의 “other six” 설명은 실제 미측정 7종으로 교정해야 한다.

장기 목표를 지속 점검하고 독립 작업은 묶어 처리하며 동일 기준으로 완료된 검증은 재사용하라. 실제 변경으로 무효화된 부분만 최소 재검증하라. 매 변경마다 Native 중복 실행·캐시·메모리·I/O·실행시간·구조 단순화를 검토하라. 26×N Native 전수 반복이나 과거 프로젝트 재시작/전면 재감사는 금지한다.

`main`, v003 immutable, 원본 v016, Project Sources/Instructions 실제 적용, 공식 Work OS 승격, repository visibility 변경은 별도 사용자 권한 없이 실행하지 마라. GitHub branch 문서 변경을 Project UI 적용으로 주장하지 마라.

**첫 응답에서는 실제 HEAD/visibility/Actions, 승인 정책, 구현 완료와 신규 PASS/FAIL, 역사 증거 재사용, 미완료·미승격, P3-B의 실제 다음 작업을 간결하게 보고하라. 그 후 반드시 중단하고 내 “진행”을 기다려라.**

---

**END — V212 continuity handoff.** 새 채팅은 실제 최신 HEAD를 재조회하고 이 문서의 복원 순서를 따른다.
