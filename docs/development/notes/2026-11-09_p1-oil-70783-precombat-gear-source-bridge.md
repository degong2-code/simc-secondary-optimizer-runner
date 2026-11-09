# P1 · 70783 Phoenix Oil 정적 O 16/16 실 SimC 및 원본 Build 연결 (2026-11-09)

- **Capability:** `O.OIL` / `PRODUCT.E2E` / `BUDGET.GJFO` / `SOURCE.SEAL`. 개발 격리 브랜치만. 사용자가 정정한 냉법의 과거 `치명+16/가속+17` buffed 관측은 공식 O 예산 증거에서 계속 제외한다.
- **Keywords:** oil, O, precombat total gear, SimC 70783, 16/16, v297, v296, v216, sealed Native, source verification, weapon hand, v222, cache.
- **Prior evidence:** [Actions #42582755601](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42582755601) **SUCCESS**. 기존 70783 바이너리 SHA256 `6b83e4d5d2216faf91511fb00ae712cdf4cc0224b0c83107e8c9c7358c24bfc6`, SimC 소스 revision `c20e2ad52e4c33711f74272309a5748125175fe8` 재사용; 신규 컴파일0, **실 Native 2회**. 같은 징벌 성기사 대표 물리 장비, temporary_enchant OFF 및 `main_hand:thalassian_phoenix_oil_2` ON. 원본 `player_t::init_initial_stats`의 `total gear stats`은 OFF 치명1217/가속820 → ON 치명1233/가속836, 특화533/유연358 및 다른 장비 스탯 불변. **기름 정적 O = 치명16 + 가속16, 총32** (해당 빌드·대표 조건·주무기 1개). `buffed_stats` 미사용, 과거 16/17 재사용0. [기존 실패 #42578562372]은 stdout에 item_t 요약이 없는 문제였고, 본 실측은 SimC 자체 전투 전 장비 수치 출력으로 해결했다.
- **Changes:** `runner/v297_sealed_simc_oil_gear_delta.py` 신규: 실제 `v233` 물리 대표 프로필/선택 손·SimC revision/바이너리 SHA를 바탕으로 기존 `v278.run_case`의 **content-addressed Native attempt/검증 캐시**를 재사용. `debug=1`의 SimC `total gear stats` OFF/ON을 동일 gear/액터 조건에서 비교; CHMV가 아닌 장비 변화, 소수·음수, 누락·중복을 차단. 동일 조건 반복 Native0. 특성 효과 계산·마부 스케일링을 재구현하지 않음.
- **Decision:** `CONNECT` — `v296.project_source_oils`에 선택 물리 ID/손/스케일 원본·새 v297 측정의 빌드/리비전/마부ID/토큰/바이너리·실 Native 영수증 정합 연결을 추가. **스케일드 원본에 해당하는 정확한 선택 항목만** `SIMC_PRECOMBAT_GEAR_NUMBER_SOURCE_ONLY` 정적 숫자 후보로 변환, 다른 스탯 효과·무관한 ID는 차단. `v216`의 선택된 실 물리 기름 + opt-in Native + 실제 로컬 바이너리가 있을 때만 v297 실행 후 기존 `v286` 무기 마스크→`v222` **미승격 예산 미리보기**→`v098` 소스 입력으로 연결. 자동 선택/미선택 기름 O0에서 불필요한 Native 실행 없음. `v278` 영약 F 및 수동 최종 T 회계 보존.
- **Verification:** [focused #42583968034](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42583968034) **513 tests / 511 PASS / 2 SKIP / 0 FAIL**, DEV_LEDGER_PASS. synthetic v297 parser·캐시 재사용(new Native0)·v296 scaled source 영수증 ID/스탯 종류 방어·v216 무기 마스크 후보 연결 검사. [선행 전체 연계 CI #42583722027](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42583722027) focused 511 PASS/2 SKIP, v113 API / v212 manifest / v181 Windows / v182 UI도 동일 코드 SHA에서 PASS; 테스트 단계 새 Native0. **#42582755601의 실제 Native는 기존 단발 워크플로 경로이고 v297 런타임 메서드에 대한 별도 실 Native E2E 증거는 아직 아님.**
- **Remaining:** `v216` 기본 공식 시즌 설치는 여전히 O0. v281 실제 물리 아이템 ID·일치하는 손과 무기 마스크·품질 구분, `v212` **O>0 공식 검증 설치**, `v113` 사용자 선택 및 `v098/v096` 실행 최종 프로필과 DPS, 95% 최적화 결과까지 **실 종단 검증 없음**. 현재 확인된 O16/16을 다른 기름·다른 빌드·아이템레벨의 자동 상수로 확장하지 않는다. 선택 미승인 항목은 보류하고 **선택 불필요한 기름까지 전수 Native 시험하지 않는다.**
- **Efficiency:** 기존 v275 소스·v281 물리 ID 조인·v278 영수증·v286 마스크·v222 예산·v217 캐시 사용, 과거 냉법 16/17 재검증 Gate 없음. main·v003·Project UI·Work OS·주 제품 개발 채팅 소유권 변경 없음.

## P1 범용 엔진 연결 보강 · 2026-11-09

**Capability:** `O.OIL`, `BUDGET.GJFO`, `SOURCE.SEAL`, `PRODUCT.E2E`. 이번 변경은 70783 특정 기름의 재시험이 아니라 매 시즌·물리 아이템·손 선택에 재사용되는 엔진 경로다.

**Decision / Changes:** `v113` 시즌 Build는 `selected_oil_item_ids_by_hand`를 물리 ID로만 받으며 API/HTTP에서 O 수치나 검증 영수증을 받지 않는다. `v216`은 `v281` 봉인 아이템→SimC 마부·품질 ID, `v286` 같은 시즌 대표 무기/손/장착 마스크, `v296` DBC 정적 수치 또는 스케일될 때 기존 `v297`의 실제 SimC 전투 전 장비 수치와 `v278` 변경 없는 실행 캐시를 사용한다. 적용 대표 무기 ID·목표 ilvl·정적 rating·SimC revision/게임 빌드·원본 SHA가 일치하는 선택만 내부 `O` 소유자 후보가 된다. 이를 기존 `v222`의 `B=G+J+F, T=B+O`와 `v212` 검증 설치 계약에 연결한다. 기존 O0 설치/영약 F와 수동 최종 T 우선, `B=T-O` 회계 유지. 무의미한 표본 Native 전수 반복, 효과 재구현, 별도 인증 Gate, 현재 장비 수집 없음.

**Verification:** 공통 focused [#42586492832](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42586492832) **522 tests = 520 PASS / 2 SKIP / 0 FAIL**, DEV_LEDGER_PASS / 신규 Native0, 원본 재수집0. 기존 v113 API·v212 manifest·Windows 패키지·UI 관련 CI [코드 변경 테스트군 #42586023675 / #42586023823 / #42586023629 / #42586023699](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42586023675) SUCCESS. 이전 실제 SimC 16/16 #42582755601 증거는 정확히 그 조건의 관측 영수증이며 **이번 generic 연결의 실제 O>0 설치/최적화 PASS라고 주장하지 않는다**.

**Remaining / Efficiency:** 오프라인 소스 결합·예산 계산 경로는 연결되었지만, **실제 원본 증거가 모두 충족된 시즌의 `v216→v212` 양의 O 설치와 `v113→v098/v096→SimC DPS` 실행**, 시즌별 검증된 최고 품질 기름의 사용자용 목록/선택 UX, 사용자가 새 환경으로 진행하는 경로는 미완료/미실증으로 구분한다. 관련 후속은 새로운 16/16 확인보다 일반 사용자 흐름 P1 완결을 우선. main/Project UI/immutable 변경 없음.

### 동일 시즌 O 선택별 설치·복원 캐시 정체성 교정

- `v216.find_verified_installed_season_environment`는 같은 게임 빌드/목표 ilvl이라도 **선택된 손별 물리 기름 ID가 다르면 다른 설치본**으로 취급한다. 선택 인자를 생략한 일반 사용자 기본 호출은 명시적 O=0 전용이다. O>0이 최근 설치됐어도 기본 O=0 요청에 재사용되지 않는다.
- `v113`는 검증된 v212 `official_O_physical_source.selected_oil_item_ids_by_hand`에 따라 설치 완료 영수증을 확인하고, 소스 프로필 복원도 같은 선택 정체성을 사용한다. 기존 세션 재개는 v212 매니페스트의 확정 SHA와 게임 빌드/ilvl을 사용하며 재실행하지 않는다.
- 변경은 **공통 엔진의 캐시 정체성** 교정이지 특정 기름 신규 실험이 아니다. [공통 focused](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42587691331) SUCCESS, 신규 Native0. [웹 API Linux/Windows](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42587691337) 최종 결과는 해당 Actions 영수증을 기준으로 한다. 기존 합성 세션 의존성 테스트는 v212의 독립 실 문서 검사 범위를 중복하는 가짜 문서 때문에 실패했으므로, 그 mock의 문서 인증만 기존 테스트 내부에서 대체하여 세션 매니페스트 비교와 실제 코드 경계는 유지했다.
- **아직 미완료:** 새 시즌의 기름 종류별 자동 품질 비교/사용자 선택 목록, O>0 설치 및 실제 사용자 DPS 종단 영수증. 실 검증 범위 미확대를 준수한다.
