# SIMC SECONDARY OPTIMIZER — CURRENT DEVELOPMENT STATE (지속 갱신)

> **2026-10-25 최신 개발 갱신 v063 (P3 Native):** 공식 v1.2 `T=G+J+F`를 사용한 334 Arcane Mage 단일 프로필의 2후보 **실제 SimC 주입 및 DPS 수집 PASS** — [Actions 40165729165](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40165729165), 전체 회귀 **304 PASS / 2 SKIP**, Native 신규 실행 2회. 기존 v059 Native 2후보의 정적 수치 차이로 net gear→JSON2 offset `(0,+165,0,0)`를 같은 프로필에서만 보정했고, 공식 총량 **G2849+J138+F165=T3152**, 무기 기름 `(16,16,0,0)`은 **T 외부**다. 후보 A 600/1108/1115/329 (DPS 192374.47±SEM951.01), 후보 B 750/958/1115/329 (DPS 192109.86±SEM1300.02) 모두 최종 rating 정확히 일치, 통계적 우열 미확정. **9개 gem/enchant 포함 gear 레코드의 정적 수치 출처 완전 분해는 미입증**; 이를 모든 전문화 예산 중복 가산 제거 완료로 승격하지 않는다. 원본 v015~v016 제품 통합도 미완료. [상세 실측·미완료사항](./V063_OFFICIAL_GJF_NATIVE_NUMERIC_RECONCILIATION.md). 다음 작업은 **범용 프로필별 숫자 주입 오프셋 및 실제 제품 적응형 엔진 연결**. 개발은 이 채팅에서 계속.



> **2026-10-25 최신 개발 갱신 v062:** 사용자는 Project Source v1.2 및 Project Instructions 적용을 완료했다고 보고했다(프로젝트 UI 직접 대조는 별개). **개발은 이 채팅에서 계속한다.** 격리 제품 시험은 [v061 입력 계약 PASS 40162193520](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40162193520) **277 PASS / 2 SKIP**(초기 FAIL 40162112120 보존), [v062 정적 예산 컴파일 PASS 40162455726](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40162455726) **291 PASS / 2 SKIP**. 기존 v059 Native JSON2 증분 재사용으로 334 Mage exact 정적 G=2849, Native cache 1759→1760 (0 신규 SimC 호출·기존 값 교정 0). 공식 v1.2 기본 T=G+J+F=3152 산술 예시이며 v059 기름 포함 실험 T=3184와 구분. **P3 최종 numeric rating 주입 정합/원본 v015–v016 통합은 아직 미완료**. 상세: [V062_SCENARIO_AND_G_L_BUDGET_ACCEPTANCE.md](./V062_SCENARIO_AND_G_L_BUDGET_ACCEPTANCE.md).



**문서 목적:** 같은 채팅에서 구현을 이어가면서, 필요한 경우 어느 일반 채팅에서도 동일한 제품 기준·증거·실제 차단 사항을 복원할 수 있도록 보존한다. **새 채팅 전환을 요청하지 않는다.**

**적용 범위:** 개발 격리 브랜치의 현재 작업 기록. 공식 Project Instructions/Project Sources나 Work OS CURRENT의 자동 승격은 아니다.

## 0. 읽는 순서·상태 신분

1. Project Sources의 공식 `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.0.md`를 제품 정책 최상위 문서로 읽는다.
2. `docs/DEVELOPER_NOTES_CURRENT_POLICY_ADDENDUM_20261025.md`에서 그 후 사용자가 명시한 **SimC 책임 분리, 장신구·제작장비, 정적 캐시** 결정을 읽는다. 이 부록의 branch 기록만으로 Project Source 승격을 가정하지 않는다.
3. 이 문서에서 최신 개발/시험 사실 및 정확한 다음 구현 지점을 복원한다.
4. `docs/V059_NATIVE_CANDIDATE_BRIDGE_ACCEPTANCE.md`와 [실제 GitHub Actions #40157655114](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40157655114)를 대조한다. 각 후속 버전은 그 버전의 증거를 추가한다.
5. `Developer_Notes_v1.1_CANDIDATE.md`는 **후보**이고 전체 승격 불가. 개발자 노트 v1.0, v003 immutable, MAIN 운영 계약을 기계적으로 덮어쓰지 않는다.

## 1. 지금 진행 중인 채팅이 개발을 계속 소유함

- 사용자는 2026-10-25 기존 채팅에서 작업을 이어가겠다고 명시했다. **'새 일반 채팅에서 바로 시작하라'는 인계 절차는 현재 작업 요청이 아니다**.
- 새 채팅용 복원 가능성은 지속 상태 문서의 품질 기준일 뿐이다.
- 현재 개발 방식은 GitHub 연결 API/Actions 사용. 로컬 PyCharm 환경 재구축·Work 모드 전환을 요구하지 않는다.
- branch: `degong2-code/simc-secondary-optimizer-runner@probe/chat-cache-v035-20261024`. HEAD는 반드시 재조회; 커밋 해시는 고정 버전 증거로만 취급. GitHub `main`을 시험 branch와 혼동하지 않는다.

## 2. 최신 제품 개발 상태 vs 시험 브랜치

| 구분 | 현 상태 | 근거/제한 |
|---|---|---|
| 사용자 보고 원본 제품 | **v016_SCENARIO_CONTRACT** | 이 repo에서 해당 제품 소스 바이트 및 receipt를 독립 확보·검증하지 못함 |
| 옛 적응형 탐색 파일럿 | v015 구현 보고/오프라인 71/71 PASS | 원본 제품 계보 및 당시 실 Windows 시험 미확보 |
| GitHub 시험 런타임 | v032 byte-preserved 연구 실행 파일 존재, v037 메모리 내 적응형 연결 | 원본 v015/v016과 일치한다고 단정 금지 |
| 정적 아이템 캐시 | v046~v058, 455 item IDs / 1759 Native stat variants snapshot | 시즌 전수 DB, full crafted recipes, 모든 ilvl 검증 완료 아님 |
| 장비 선택 | v055, Mindpiercer 트링켓 JSON2 static miss 허용 | v056 1회 Native PASS, SimC 효과는 SimC가 처리 |
| CHMV 후보 평가 | **v059, 2후보 실제 SimC PASS** | **적응형 전역 최적화 완료 아님**, 단일 334 Mage 실험 |
| MAIN/공식 Project Sources | **변경/승격 미완료** | 별도 기존 MAIN 승인 절차 및 실제 적용 기록 필요 |

## 3. 보존할 실제 v059 Native 증거

- Workflow: `.github/workflows/v059_candidate_two_native.yml`
- Actions [run 40157655114](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40157655114) SUCCESS.
- Git commit: `08c309ef31fb1a9119252b633d1d34cb34e36c4f`, SimC Linux binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`.
- 258 regression tests: 256 passed + 2 skipped.
- Artifact: `simc-v059-two-candidate-DPS-40157655114`, SHA256 `56002f118cb85cbc7e32aa1c0fc3a0149e7bd7ca0e96b1b96b586b3ddf836288`. Artifact retention may expire; portable ZIP from the prior conversation is alternative, its integrity must be independently checked on reuse.
- v059 334 Arcane Mage, one fixed selected trinket `250224`; selected two Arcanoweave embellishments unchanged; v059 **trial only** budget `T=G2849+J138+F165+O32=3184`.
- Target A `600/1140/1115/329`: DPS 192324.1023, SEM 1379.5784. Target B `750/990/1115/329`: DPS 191574.5434, SEM 1285.6370. Both target/observed four rating numbers match. Difference statistically inconclusive; no optimum declaration.
- Base v1.0 policy `T=G+J+F` is still authoritative; v059's oil vector is **bounded test**, not generalized product rule.

## 4. 구현 순서 — 다음 실제 작업

**P0 · 계보 확인 — 우선 작업이지만 격리 개발 중단 사유 아님.** 원본 `v015`/`v016_SCENARIO_CONTRACT` 파일 위치/바이트/영수증 확인. 기존 탐색 기능(후보 생성, 통계 비교, 실행 예산, 중단/재개)을 재활용할 수 있는지 판단. 미확보이면 '원본 제품 통합 증거 없음' 유지하면서 다음 격리 기능 구현 진행.

**P1 · 범용 Scenario Contract** — 고정 Mage/334 값 제거. 직업/전문화/종족/특성, 선택 장비·장신구 2개·장식 2개, 4pc, 목표 ilvl/수동 T, 보석/영약/소모품, 전투 시나리오, 스탯 상하한, SimC 실행 예산을 정형 입력으로 연결. 장비 조합 자동선택, 자체 효과 계산 금지.

**P2 · 대표 장비·정적 예산** — 실제 Native stat cache 기반 G/특수장비 locked floors/제작 자유배분, J/F를 구성. 목표 ilvl에 맞는 주능력치/무기 성능/기본 티어4셋 유지. 장신구는 G 밖. Native cache miss는 선택된 비장신구에 한해 1회 지연 조회, 같은 변형 재사용.

**P3 · 범용 SimC CHMV 주입** — gear_* override와 실제 출처별 외부 가산을 숫자로 정확히 조정. 같은 스탯의 중복 가산/누락을 막고 **요청 목표 vs Native JSON2 정적/적용 rating** 확인. 아이템 proc/효과 검사를 선행 Gate로 추가하지 않는다.

**P4 · 원본 적응형 탐색 접합** — v059 `plan / compose_input / observe_result / compare` 인터페이스와 출처 확인된 기존 탐색 루프 연결. scout→guided→confirmation iterations, 고유 후보 캐시, 오차 범위 내 미확정 처리, 근접 대안 산출.

**P5 · 범용화 실측** — 우선 별도 전문화, 탱커/힐러까지 기존 SimC APL로 DPS 시험, 사용자 설정 전투 환경 반영. '전체 전문화 PASS'는 증거가 쌓일 때만.

**P6 · 실사용 UI/내구성** — 원클릭, 진행도, 취소, 자동 재개, 오류·JSON2·출력해시·실행 폴더 열기, 절대 rating·비율·DPS·SEM·실질적으로 다른 대체 목표 표시.

## 5. 환경/정책 조건의 정확한 판정

- **격리 브랜치 개발 시작**: READY. GitHub 수정·workflow 실행·SimC 재사용·artifact 검색이 현재 채팅에서 실제 작동했다.
- **원본 v015/v016에 최종 합치기**: PENDING_SOURCE_BYTES. 원본 출처·SHA·회귀 계약 없이는 '통합 완료' 선언 불가.
- **공식 Project Instructions/Sources 갱신**: PENDING_MAIN_APPLY. 이 채팅 연결 도구에는 Project Settings/Project Source를 직접 수정하는 API 없음. 사용자가 승인한 결정은 정책 부록에 기록되었지만 공식 설정 적용 여부를 추정하면 안 된다.
- **공식 Work OS M0 환경 Gate**: 제품 실험/개발 허가와 분리, MAIN 소유. 미통과로 정상 제품 시험을 금지하지 않는다.
- **WEQUIP runtime**: 런타임 의존성 도입 금지. 일회성 정적 metadata 입력까지만.
- **Developer Notes v1.0 및 v003 immutable**: 보존.

## 6. 문서 유지 규칙

새 버전을 개발할 때마다 *실제 실행된 Run ID, SHA, PASS/FAIL, 남은 불확실성과 정확한 다음 작업*만 추가한다. 미실행 시험이나 이전 문서의 자기 보고를 독립 검증 완료로 바꾸지 않는다. “인계 준비”를 개발 중단이나 새 채팅 이동 요청으로 해석하지 않는다.
