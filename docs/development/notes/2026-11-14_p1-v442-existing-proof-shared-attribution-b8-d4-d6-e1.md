# v442 — 기존 v439 실제 Native + v187/v432 회귀 공동 귀속 (B8·D4·D6·E1)

- **Capability:** `TIER.SEASON`, `GEAR.SEASON`, `BUDGET.GJFO`, `PRODUCT.E2E`
- **Keywords:** v442, B8, D4, D6, E1, 78-element, scoped acceptance, shared evidence, 70783, crafted, tier4pc, GJFO, no new Native
- **Prior evidence:** [v441 감사](../78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md), [v432 회귀](2026-11-13_p1-v432-b8-selected-static-budget-preflight-offline.md), [v439 실제 Native](2026-11-14_p1-v439-b8-one-real-selected-70783-four-tier-native-e2e.md), [v440 기존 통계](2026-11-14_p1-v440-b8-existing-real-json2-95-material-replay.md)
- **Decision:** `REUSE` → `CONNECT`. v441에서 승인된 실사용 수락 조건만 적용한다. B8만 재검사하거나 새 Gate/최적화 엔진을 만들지 않는다. 모든 78개 수락 문구는 v441 그대로이며 실증 범위 밖을 자동 승격하지 않는다.
- **Changes:** 공식 78 JSON의 B8/D4/D6/E1 3축 근거와 자동 상태표·상세 추적표·CURRENT/START_HERE를 일관되게 갱신하고 v401 역사 B8 하드코딩 테스트를 증거 기반 반례로 변경. 
- **Generic regression:** [v187·v432 기존 통합 오프라인 Actions #43440892382](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43440892382), tested SHA `8d2a107b682a6fc3beb894fcdc6a16eed11a8883`. 한 티어부위 제작 점유→5번째 티어 복원, 두 티어 부위 점유→불가능 사전 차단, 소스 빌드/아이템 변경·슬롯 오류 차단, 정확 변경 정적 변형만 조회, 제작 초기 분배와 고유 특수 L 구분, 수동 T/양수 O 산술 및 불가능 하한 회귀. v187의 변경 빌드 사례는 **합성 회귀**이지 그 빌드의 실 원본 증거가 아니다.
- **Verification:** v401 `--check` 기존 변경에서 통과했고, 테스트 교정 커밋 `d184ff294ca6c7584e5400b822274740200fb583`의 [정책 CI #43540463560](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43540463560)는 **35 PASS/0 FAIL**; 전체 오프라인 작업은 기존 ledger 실패. 실제 v439 원본 #43466966207 및 v440 재사용 #43534722801 그대로 유지.
- **Current/source + product:** [v439 Windows 실제 70783 #43466966207](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43466966207), tested SHA `bad415de407671898b26001869478bcdb1ab047e`; 원본 artifact `14059197320`, ZIP SHA256 `ac5f41298515d22121e635e57531e599164acdd97f3b00193becc7bae5311d76`, 실제 JSON2 6건 내부 증거 ZIP SHA256 `fcffd42b5f818a0e4fac296cd715afec628ebef35426823f9b737dd50ccceb52`. 기존 환경 Native3+변경 슬롯4+DPS6=13회, 재생 캐시 6회(추가 Native0). 선택 제작 머리 ID244579, ilvl334, `crafted_stats=32/36`, `embellishment=arcanoweave_lining`, 가슴·어깨·손·다리 동일 시즌 4pc, 정적 head 100+100, 제작 초기 50:50을 L로 잠그지 않음(L0). 설치 소스/프로필 및 실제 웹 API plan/start/result/cache-only 경로를 확인한 사례.
- **Budget:** 같은 시즌 대표 G 2850에서 변경 슬롯 exact delta -1을 반영한 **근사 투영 G2849** + 검증 J92 + F165 = B3106; O0이므로 T3106. 이것을 전체 부위 exact Native G라고 칭하지 않는다.

| 요소 | generic 검증 범위 | current_source 검증 범위 | product_integration 검증 범위 | 판정 |
|---|---|---|---|---|
| **B8** 티어 4pc | 정상 복원·2부위 불가능·원본 mismatch 차단 | 실제 70783 장비·티어 소스/4pc | 한 사용자 제작 머리 선택→가슴 티어 복원→실 SimC DPS | 3축 PASS |
| **D4** 제작장비 | 정확한 variant 총량, 제작 50:50 미고정, 특수 L 구분 | 실 제작 머리244579·ilvl334·옵션·정적200 | 선택 제작+장식 프로필·DPS·L0 | 3축 PASS |
| **D6** 부위 충돌 | 2개 티어 점유 불가능 및 선택 충돌/드리프트 | 70783 현재 4pc 실제 슬롯 | 한 정상 제작+장식/티어 충돌 해결 | 3축 PASS |
| **E1** 기본 B | G 변경부위 산술·J/F 귀속·수동 T 반례 | 현 G 근사·J92/F165 원본 | 최종 사용자 프로필 B3106·T3106·DPS | 3축 PASS |

- **Remaining:** 미승격/제약 — E2는 실제 O>0 중복 방지 증거를 더 비교해야 하고, E7은 bounds·정수 불가능 후보, E9는 gear/static과 buffed 분리, F7은 미선택 장신구·기름·특수 입력, G4/G5는 rev-only 정적 캐시/다른 실행 정체성 변화, H1/H3/H4/H6는 v439/v440 통계·사용자 소비의 증거를 각 수락 조건에 별도로 재귀속할 필요가 있다. v440은 JSON2 기존 6건 재사용·두 확인 후보 DPS 차 1091.06>95% 경계827.40·근접 대안 관측0이며 새 Native0이다. 임의로 PASS하지 않는다.

- **Efficiency:** 이번 변경 코드 Native/API/DB2 0, 4요소 공통 원본 재사용, 추가 CI는 문서/테스트 변경의 자동 push 검증만; main·원본 v016·Project UI 무변경.

**Result:** 공식 `generic 22/current_source 22/product_integration 11/historical 12`, `COMPLETE 11/78` (기존7 + B8/D4/D6/E1), `next_review=B9`, `full_product_e2e=PENDING`. 오프라인 v401 상태 검사/Actions 결과는 해당 커밋의 CI 영수증으로 따로 판정한다. **이번 변경 신규 Native/API/DB2 0, 제품 실행 코드 0, 원본 v016/main/Project UI/공식 승격 변경 0.**

**v442 CI 교정:** 최초 v442 변경 커밋 `395a83ef344354744069a09e15788c71491ffe14`에서 v401 `--check`는 22/22/11/12·B9 정합 통과했으나 34건 테스트 중 4건은 과거 B8=PENDING/B8 다음 검토 숫자를 하드코딩하여 실패했다. 기능 수락 조건을 약화하지 않고 해당 테스트를 현재 증거의 3축·서로 다른 증거 종류·역사 증거 오용 차단·B9 순서 검사로 대체한다. 별도 전체 Reusable Offline CI의 DEV_LEDGER_FAIL 198건은 이 상태 검사와 별도 기존 문제이며, 본 변경으로 통과했다고 주장하지 않는다.
