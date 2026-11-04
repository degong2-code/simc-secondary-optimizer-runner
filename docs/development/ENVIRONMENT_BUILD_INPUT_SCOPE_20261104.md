# 환경 구축 엔진 — 사용자 입력·내부 설정·시즌 근거 책임표 (2026-11-04)

> **지위:** 사용자 요청에 따라 앞서 승인된 설계·실제 코드·영수증을 재대조한 **개발 재사용 기준**. 새로운 제품 정책을 발명하거나, 과거 v1.4.3 원문·Project UI·main·immutable v003·원본 v016을 수정/승격하지 않는다. 최신 사용자 직접 결정 > v1.4.3 및 비충돌 v1.4 계열 > GitHub 코드/실물 영수증 > 이 해석표. [PROTOCOL](PROTOCOL.md)과 [INDEX](INDEX.md) 이후, 관련 구현 전 본 문서를 조회한다.

## 1. 고정 목표 / 기본 구축 경계

- 오직 26 DPS. 미래 목표 ilvl 기본 334 또는 사용자 최종 T 수동 입력. 장비 재분배/장비 추천/전체 장비 DB·별도 SimC-only 엔진이 아님. 한 개의 **정상 `v216.build_environment`→v222→v098→v096→기존 v094** 엔진을 연결한다. SimC는 장비 효과·proc·APL·DPS를 처리, 우리는 선택된 시즌 원본/정적 CHMV 회계·입력·캐시/95% 판정만 처리한다.
- **필수 환경 예산:** 시즌 대표 장비·티어·무기와 **G/J/F/O의 정확한 시즌·빌드·근거 및 예산 소유권**. `B=G+J+F`, `T=B+O`, 수동 T가 최우선, `B=T-O`. G 내 정확 L/정적 E 하한, 선택 기름 O 손별 한 번, 장신구 고정은 자유 G 밖. 과거 J138/F165/기름 16+16/79×2는 동일 시즌·동일 조건의 역사 근거일 뿐 다른 시즌 기본값이 아니다.
- **선택적 제품 입력:** 음식/물약/증강 룬, 선택 특수 보석·특수 장비/장식/영구 마부, 선택 기름 종류·Omnium 모듈/확장팩 옵션은 검증·선택 시 적용하지만 **미발견 선택 옵션 하나만으로 이미 검증된 기본 환경을 차단하지 않는다**. 보석 J/영약 F/대표 G/제공할 기름 O의 필수 범위는 별도 충족. 부정확한 사용자 옵션은 조용히 무시하거나 구 시즌값으로 대체하지 않는다.
- **자동 등록 정책 A:** 정확 ID·출처·동일 빌드·효과/품질 동등성·적용 조건·정확 SimC 입력·CHMV 소유권이 해당 범위에서 검증되면 별도 수동 승인 없이 자동 선택지 발행. 동일 효과·사용 범위·조건과 높은 품질 비열등이 모두 확인된 중복 품질만 숨긴다. 후보 수집 또는 SimC 핸들러 존재만으로 자동 발행 금지. 일반 임시 마부는 **제외**, 기름은 별도 지원. 새 독립 인증 Gate/효과 엔진 불필요.
- **검증 지위 구별:** `SOURCE_ONLY`/Native 정적 rating **관측**/정확 조건 범위에 따른 **사용자 등록 승인**/실행 가능한 **환경 READY**/실제 26 DPS Native E2E는 각각 다르다. 기존 PASS는 정확 범위에서만 재사용, 작은 입력 누락을 전체 환경 증거 부재로 오인하지 않는다.

## 2. 열두 항목 — 정책·필요성·기존 코드·다음 결정

| 항목 | 승인 방침 및 기본 환경에 필요한지 | 기존 함수/근거 (REUSE) | 남은 실작업 및 금지 방향 |
|---|---|---|---|
| **① 캐릭터 레벨** | **일반 사용자 입력 아님, 신규 시즌 수집 Gate 아님.** 최신 P3-BN: SimC 컴파일된 기본 최대 레벨 사용, 보통 프로필 `level=` 생략. P3-BM의 v163 레벨 추론은 이전 정책. | `v233/v234` 기본 level 미기입; [P3-BN](../P3_BN_20261103_SIMC_DEFAULT_LEVEL_OPTIONAL_CHARACTER_AND_ENGINE_OWNED_ITEMS.md) | **CONNECT:** P3-DI `v098._season_settings_from_v216`/ `v139.compose`의 source-only `character_level` 필수 및 강제 `level=` 교정. 구 시즌 명시 level/기존 프로필 바이트 보존. 새 레벨 생산기 **STOP**. |
| **② 종족·특성** | 사용자 선택, 미입력 시 이미 승인된 대표값. 임의 종족의 직업 적합성 검사. 실 유저 SimC import는 캐릭터·특성만, 현 장비/스탯 금지. | `v106.user_scenario`, v146 대표 특성, [P3-BN](../P3_BN_20261103_SIMC_DEFAULT_LEVEL_OPTIONAL_CHARACTER_AND_ENGINE_OWNED_ITEMS.md) | **REUSE:** 새 시즌 폼/샘플 전체 SimC 프로필/레벨 입력 필드 신규 구현 **STOP**. |
| **③ 음식** | 사용자가 선택하는 **선택적 SimC 효과**, 기본 G/J/F/O 자동 구축의 필수 입력 아님. 미선택은 실제 효과 없는 명시 `disabled` 등 유효한 OFF 경로 가능. 음식이 정적 CHMV에 미치는 특수 영향이 관측되면 회계 혼동 없이 별도 검토. | `v108.SUPPORTED/validate_choice/apply`, `v113` UI/API, `v189/v190` 동일빌드 후보, [P3-BO](../P3_BO_20261103_PINNED_SIMC_V189_WAGO_V190_CONSUMABLE_STAGE.md) | **REUSE/CONNECT:** 검증된 시즌 ID·SimC 토큰·품질/조건의 옵션만 발행. 후보 192개 전수 승인·미검증 기본 음식 강제·독립 효과 모사 **STOP**. |
| **④ 물약** | 음식과 동일한 **선택 입력**. 정적 J/F/O 필수 수치의 생산자가 아님. | `v108/v113` 기존 선택지, `v189/v190` 61 후보 원본 경로 | **REUSE/CONNECT:** 선택된 검증 옵션만 프로필/세션 정체성에 반영. 새 시즌 모든 물약 데이터베이스 완성 **STOP**. |
| **⑤ 증강 룬 (augmentation)** | Omnium과 다른 SimC `augmentation=` 입력. 기본 시즌 G/J/F/O 환경의 의무 선택·신규 수집 Gate 아님. | `v108.SUPPORTED`, `v108_user_consumable_dialog`, `v113` | **REUSE:** 지정된 시즌 옵션/명시 OFF를 처리. 기본값을 구 시즌 토큰으로 자동 복사 금지. 독립 증강 효과 엔진 **STOP**. |
| **⑥ 일반 보석 J** | **기본 환경 필수**: 실제 물리 보석/스탯 J, 검증된 고품질·적용 조건, 수동 T·G/J/F/O 회계 연결. 사용자가 모든 보석·전체 장비를 수집하게 하지 않음. | `v221` 물리 후보, `v266/v268` 정적 원본, `v271.reconcile_observed_J`, `v216→v222`, [P3-CA](notes/2026-11-03_p3-ca-physical-gems-j-normal-build.md) | **CONNECT/필요시에만 EXTEND:** 기존 physical IDs/J를 `v098` 실제 소켓 배치로 전달; ID/품질/게임 적용/실측 범위를 구분. 기존 J138 하드코딩·새 Gem 산술 엔진 **STOP**. |
| **⑦ 소켓 수·배치** | 시즌에 따라 가변. SimC가 `gem_id`를 받아도 실제 인게임 소켓 가능성을 증명하지 않음. | `v271.arrange`, `v139.compose(socket_plan=...)`, `v101` 4색, [P3-BZ](notes/2026-11-03_p3-bz-variable-socket-physical-gems-connect.md), [P3-BX 실 Native](notes/2026-11-03_p3-bx-simc-socket-native-contrast.md) | **CONNECT:** 이미 구현된 `socket_plan`을 정상 `v098` supplier에 전달. P3-DI의 6일반/머리특수 고정 PENDING은 그 경로를 아직 사용하지 못하는 **통합 한계**. 진짜 시즌 소켓 허용성/보너스 ID는 필요한 범위만 EXTEND; 신규 소켓 엔진/Native 전수 **STOP**. |
| **⑧ 특수 보석/다이아** | **선택적** 옵션. 역사 240983·240967은 당시 주능력/특수효과·4색 규칙으로 관측, 다른 시즌에 복사하지 않음. 정적 CHMV J와 부가효과 소유권 구분. | `v101`, `v108.DIAMONDS`, `v135`, `v271` 역사 ID 한정, [v115](../V115_P1_WEB3_SPECIAL_GEMS_UI_20261027.md) | **REUSE/조건부 EXTEND:** 새 시즌 실제 ID/효과·소켓 조건에 맞는 옵션만 노출. 선택 모듈 증거 부족을 기본 J 전부 불가로 확대하지 않음. |
| **⑨ 영약 F** | **기본 환경 필수**: 최고 품질·정적 CHMV 종류/수치·정확 token; 실제 비정적 효과는 SimC 소유. 사용자 선택에 따라 적용 스탯 달라질 수 있음. | `v278` 정적 관측, `v281` ID→token, `v216` 선택 물리 F, `v222` 회계, `v108/v139/v098` 직렬화. [P3-CO](notes/2026-11-04_p3-co-actual-flask-oil-native.md), [P3-CP](notes/2026-11-04_p3-cp-quality-phoenix-oil-native.md) 정확 동일 시즌 한정 실측 | **CONNECT:** 기존 F vector를 프로필/예산에 사용. P3-DI 현재 `v139` 단일 스탯 F 전제는 *현재 인증 범위의 제한*, 새 다중 스탯 영약 생기면 기존 vector 계약만 최소 확장. 추정 수치·F165 복사 **STOP**. |
| **⑩ 무기 기름 O** | 선택 기름의 고정 O와 손·무기 조건은 공식 `T=B+O`에 필수. **미사용 O=0** 가능, 소스 미관측은 0으로 판정 금지. 일반 임시 마부 금지. | `v285/v286` 물리 무기 마스크, `v281/v278` 실제 후보, `v091` 손별 O, `v222` 고정 회계, [P3-CT](notes/2026-11-04_p3-ct-representative-oil-product-bridge.md), [P3-CY](notes/2026-11-04_p3-cy-flask-observed-quality-oil-mask.md) | **REUSE/CONNECT:** 정확 기름·선택 손/필수 무기 ilvl 조건 확인·`gear_*` 일회 적용. O16/16 역사값, 방패에 기름, 별도 임시 마부 일반 카탈로그, 중복가산 **STOP**. |
| **⑪ Omnium·시즌 특수 시스템** | 핵심 환경 DB 밖 **선택형 모듈**. OFF 시 프로필/예산 효과 완전 제거, ON 시 정확 SimC 토큰·버전·상태를 세션/DPS 캐시 identity에 반영. `augmentation`과 혼동 금지. | `v108` 기존 Omnium preset, `v182` 사용자 4열 선택, P3-DI `v139` None일 때 omnium 라인 생략, [v1.4.3 §4](../SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) | **CONNECT/필요시 EXTEND:** 옵션 모듈 등록·ON/OFF→프로필/캐시 소유권 경로; 현 코드의 OFF 줄 삭제만으로 전체 모듈 격리/버전 identity 완성 주장 금지. GPT 영구 호출·기본 GJFO Build 차단 **STOP**. |
| **⑫ 최고 품질·Policy A 자동 선택지** | 검증된 범위 자동 등록, 후보·낮은 품질의 동일 효과 중복은 UI 노출 금지. 미확정 선택 항목만 보류. | `v220.decide` 정책 A 순수 판정, `v196.public_options` 시즌 후보 UI, `v108/v113` 기존 선택지. [v1.4.3 §3/§5](../SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) | **CONNECT:** 기존 source/Native/예산/실사용 경로 영수증 → v220 → v196·UI **원자적 발행**. v220의 자격 판정이 UI 설치를 스스로 수행하지는 않음. 새 품질/효과 독립 인증 Gate·매 아이템 수동 승인 **STOP**. |

## 3. 단일 엔진 구현 가능성 — 함수 존재 기준의 구조 검토 (증명/실측 Gate 아님)

| 정상 Build 단계 | 실제 코드 존재 여부 | 개발 판정 |
|---|---|---|
| 사용자 요청 → 동일 `v216.build_environment` 및 빈 시즌 원본 수집 | **있음**: `v113 /api/v1/environment/build`, `v216.collect_wago_new_season_source`, `v217` 입력 SHA/재사용 | **REUSE**. 별도 엔진 작성 불필요. |
| 시즌 gear/tier/대표무기·정적 G | **있음**: `v167/v168`, `v191/v211/v213`, `v241/v274`, `v233/v234/v277` | **REUSE+CONNECT**. source-only와 시즌 공식 증거를 구분. |
| 소켓/보석 J, 영약 F, 기름 O 및 B/T | **있음**: `v271`, `v221/v266`, `v278/v281`, `v285/v286`, `v222`; `v216` 실제 관측 미승격 출력 | **REUSE+CONNECT**, 품질·게임 적용성 부족분만 보완. |
| 대표 프로필·선택 소모품·가변 소켓 | **있음**: `v139.compose(socket_plan=...)`, `v108`, `v169`, `v098`. P3-DH/DI `v216→v098` source-only opt-in 있음 | **CONNECT**. 현재 P3-DI의 일반 입력 강제와 고정 소켓이 제품 기본 경로를 불필요하게 제한. |
| 승인 선택지/환경 설치 | **부분 구현**: `v220.decide` 판정, `v196.public_options` 표시, `v212` 환경 매니페스트 | **CONNECT**. 자격 판정≠검증된 값의 자동 발행/설치; *실제 신규 시즌* 완료 아님. |
| 실제 DPS 적응형 실행·캐시·취소/재개 | **있음**: 승인된 같은 시즌에서 `v098→v096→v091/v093→v094`, [P3-DD](notes/2026-11-04_p3-dd-admitted-season-v096-native-entry.md) | **REUSE**. 신규 시즌 READY/26 DPS E2E는 별도 미완료. |

## 4. 다음 구현 우선순위 / 과도한 작업 방지

1. **P3-DI 교정 — 입력 범위:** 일반 프로필은 SimC default level; 음식/물약/증강/Omnium은 강제 입력이 아닌 검증된 선택 또는 명시 OFF. 기존 역사 시즌 프로필·기존 사용자의 명시 선택·원본 캐시 바이트는 보존.
2. **가변 소켓 CONNECT:** 이미 있는 `v271`의 선택 배치와 `v139.compose(socket_plan)`을 기존 `v098_inputs` / 정상 v216 Build에 전달. 새 소켓 계산기 만들지 않음. 게임 내 허용성이 실제로 부족한 범위만 보완.
3. **기존 인증·발행 CONNECT:** 필수 G/J/F/O·L/E 회계, 최고 품질 조건, 기존 v220/v196/v212, `v098/v096/v094`를 한 정상 Build 출력으로 잇는다. 음식/물약/특수 모듈 전체가 미완성이어도 확정된 기본 환경은 진행 가능하게.
4. **필요할 때만 실자료·Native:** 앞선 [P3-CP Native](notes/2026-11-04_p3-cp-quality-phoenix-oil-native.md), [P3-BX Native](notes/2026-11-03_p3-bx-simc-socket-native-contrast.md)를 적용 범위별 재사용. 신규 소스 부족을 함수의 PENDING 하나로 단정하지 않는다.

**금지하는 장기 회귀:** 시즌값 하드코딩, 모든 26전문화×아이템레벨 Native 전수, 부가효과 재현, 인증 Gate 증식, 사용자 전체 장비/레벨 입력 추가, 소모품 전체 DB 구축, 기존 증거 전면 재감사. 변경마다 네트워크/Native 중복·캐시 무효화·메모리/I/O/완료시간 검토.

## 5. 추적용 기준 영수증

- 이전 정책과 구현 충돌: [P3-BN 레벨/캐릭터](../P3_BN_20261103_SIMC_DEFAULT_LEVEL_OPTIONAL_CHARACTER_AND_ENGINE_OWNED_ITEMS.md), [P3-BZ 가변 소켓](notes/2026-11-03_p3-bz-variable-socket-physical-gems-connect.md), [P3-CA 물리 J](notes/2026-11-03_p3-ca-physical-gems-j-normal-build.md).
- 실물 범위: [P3-CO F/O Native](notes/2026-11-04_p3-co-actual-flask-oil-native.md), [P3-CP 품질 Native](notes/2026-11-04_p3-cp-quality-phoenix-oil-native.md), [P3-BX 소켓 대비 Native](notes/2026-11-03_p3-bx-simc-socket-native-contrast.md).
- 기존 접합: [P3-DD 같은 시즌 실행 경로](notes/2026-11-04_p3-dd-admitted-season-v096-native-entry.md), [P3-DH 원본 연결](notes/2026-11-04_p3-dh-v216-v098-auto-source-only-bridge.md), [P3-DI 시즌 설정](notes/2026-11-04_p3-di-source-gem-flask-settings.md). 동일 조건 증거만 재사용.
