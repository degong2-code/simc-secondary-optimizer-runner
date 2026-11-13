# v405 — A7 실제 KR ZERO-SOURCE 자동 원본→아이템 후보 검증 성공 (범용/원본 PASS; 제품 E2E 대기)

> **최신 A7 범위 판정:** `generic=PASS`, `current_source=PASS`, `product_integration=PENDING`. **현재 실제 Blizzard/WCL/Wago 원본에서 장비 후보·사용자 선택지를 사람/AI 아이템 ID 지정 없이 자동 구성하고, 각 ID의 동일 빌드/시즌 출처를 `v163→v165→v166→v167` 소비 경계에서 봉인**했다. WSE 값은 진단 전용이다. **실 사용자 입력→SimC profile→DPS/SEM/95% 결과는 이번 시험이 아니며** 최종 시즌 전체 아이템/효과 인증도 아니다.

## 1. 코드와 일반 제품 경로 — 별도 AI 검증기/새 gear 엔진 아님

- **`runner/v405_a7_selected_source_contract.py::assess`**는 기존 `v216` Build가 생산한 **인증된 v163 전체 후보 + v167 최종 후보**를 읽기 전용으로 사용. 현재 빌드·DB2 ExpansionID·DisplaySeasonID가 같은지, 실제 각 후보(내부 일반 장비 후보 포함)에 원본 `item_id`와 정확한 원본 `acquisition_sources`가 남았는지, 적어도 하나의 활성 raid/M+ 저널 소속 또는 검증 중인 같은 확장팩 제작 출처가 있는지 확인. 사용자 공개 `trinket/special_effect_gear_candidate/selectable_stat_craft`도 최종 후보의 정확한 부분집합인지 검증. **원본에 없는 item ID, 다른 DisplaySeasonID, 변경된 source evidence·중복 ID·빌드 교차는 FAIL**. WSE 양수/0/None/비정상 문자열은 동등하게 처리하고 원본 진단에 보존.
- **`runner/v216_environment_build_coordinator.py::_fresh_ordinary_gear_source_stage`**에 별도 **`v217.execute_stage`** `fresh-a7-auto-public-choice-provenance`을 연결. 입력은 해당 v163/candidate 원문 SHA + v254 영수증 + 코드 fingerprint; 출력은 작은 `source/v405_a7_auto_public_choice_provenance.json`. 최초 source-only 검증은 `EXECUTED_AND_SEALED`, 동일 원본 재사용은 `REUSED_VERIFIED`/HTTP 0. 선택지 목록/소스 수치 모두 프로그램이 자동 계산; 보조 단계 오류는 A7 후보 인수만 `PENDING`으로 보고하고 기본 GJFO를 위한 다른 source 선행 단계를 새로운 WSE Gate로 차단하지 않음.
- **`integration_probes/v405_a7_real_source_diagnostic_once.py`**는 기존 `v289` KR Retail build 발견→`v242` 인증 Blizzard/WCL→`v161` 선택한 10개 Wago DB2→`v216._join_authenticated_season_source`(`v163`)→`v216._fresh_ordinary_gear_source_stage`(`v165/v166/v167/v405`)을 **기존 생산 함수 그대로** 실행. 입력은 정상 API 자격 증명과 현재 게임 빌드 자동 발견뿐. GPT 질의·수동 ID/확장팩명/시즌명·오래된 예산·대표 장비 DB·Native 작업 없음. 파이프라인 자체가 정상 user-session E2E라고 하지 않는다.
- 사용자에게 공개하는 것은 **최적화할 장신구/특수장비/제작장비 후보**이며 일반 장비 전체 수동 선택이 아니다. 제작 ID는 향후 정확 옵션·SimC 검증 후 정책 A에 따라 자동 등록, `PROVISIONAL_SIMC_BATCH_REVIEW`라는 원래 후보 상태를 실제 인증 완료로 과장하지 않는다. 내부 일반 장비는 제품의 자동 대표 프로필 소스이다.

## 2. 실제 인증 영수증 — 재현 가능한 기계 판독 값

| 구분 | 신규 실측 |
|---|---|
| [A7 실제 KR ZERO-SOURCE GitHub Actions #43375839959](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43375839959) | Tested HEAD `349986e8c816523240816abe51b8497c6882921a`, Ubuntu Python3.12, 성공. 시크릿은 Actions env, 아티팩트 미저장. 최종 프로그램 실행 진단 `A7_REAL_ZERO_SEED_SOURCE_PUBLIC_CHOICES_RECONCILED`. |
| [제한 영수증 artifact #14014072785](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43375839959/artifacts/14014072785) | 실제 ZIP digest `sha256:a5ec1c34a07dcc14c851227acb0883139275b73c11a66bb7fdc9af844efd2d62`; artifact의 `a7_v405_real_source_receipt.json` 실제 파싱 확인. 원본 10 DB2 CSV·개별 아이템 ID/이름·토큰을 공개 영수증에 담지 않음. |
| 실제 KR Retail | `12.1.5.70783`, 공식 BPSV 원본 SHA `a30d4de410d5ff65a682940077e7b1dc200a6a1deed095dd02676c57a5104440`. Blizzard/WCL 인증 8 요청(토큰 2 포함); WCL Raid zone 53 / M+ zone55, 동일 빌드 DB2 ExpansionID11, DisplaySeasonID37, raid10 boss / M+8 dungeons. **시즌/확장팩/아이템 ID 사전 입력 0**. |
| 원본 DB2 | 현재 10 CSV / 62,280,767 bytes **이번 진짜 A7 경로에서 1회 확보**. 과거 v393 CSV 원본은 compact artifact에 포함되지 않아 이 A7 end-to-end source 소비를 위해 1회 재획득한 것. 반복 감사/26 spec Native는 없음. 이번 source `receipt.json` SHA `754cf428cc48edfead5f5ad4d0946ec968f6b82f34e216b798539a41d80ef9b4`, 테이블별 원문 SHA는 artifact에서 확인 가능. |
| 자동 현재 출처 대조 | v163 raw source item **434**, `v163` `unknown` 조인 문제 **0**, 현 시즌 v405 대조된 source-selected 후보 **209**, user list **134** (`trinket=18`, `special_effect_gear_candidate=10`, `selectable_stat_craft=106`). 사용자 목록 134건은 source/season 입증 **후보**이지 장신구 발동/효과/모든 옵션 인증이 아님. |
| 원문/봉인 SHA | v163 `ec8987193c1114e7b24c746efe7ad74ba7525f1370181cfb980ee5d7a27a2236`, v254 `6c135396a7f46765a70f1fa557aaaa53fe19d413fb39d12cd6fc89f7f86fc605`, v405 `ba671af3cdf30d3990bbefdbf13baf3c17880ac29baed6d756dbe6c67ccbe678`. User item ID sort-list digest `e8cddf3a6c17d58f67f4cc9d3715a21193abba8231b30dc1f28404c8351ed5fc`; 전체 현재 후보 digest `a29850211b2076b0cf0f98637ec8fc850a2c1c68e4803673d771f09373b3bf3e`. |
| 반복 실행/경계 | `same_source_reused_without_extra_http=true`, **v254/v405 재사용=REUSED_VERIFIED**, `v254` 신규 필수 ItemXItemEffect HTTP 1회, 추가 자동 A7 HTTP 0, **Native 0**, user profile 생성0, GJFO 설치/최종 DPS 결과0. WSE membership gate `false`, diagnostic-only `true`. |

## 3. 회귀 실증과 범용성 판정

- [오프라인 Actions #43375459029](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43375459029) tested `2a2fbc06444a47b160d9ff4f9a43f08b7619248c`: **144 시도 / 141 PASS / 3 선택적 원본 mount SKIP / 0 FAIL**. WSE 0/양수/누락/불형식 시 결과 불변, 미래 가상 Retail 13.0.0.88888/다른 DisplaySeason·레이드·M+·장신구·제작 source, forged current-source ID/원본 변조 차단, `v165→v166→v167` 정확 선택지, **`v216` 정상 Build 자동 `v254→v405` 봉인/재사용 0 재수집**, 기존 A1~A6/GJFO 관련 focused suite 계속 통과.
- 기존 A1~A6 실 원본 및 일반화 증거 + 이번 actual zero-seed A7 자동 전체 후보 경로 + 변경 시즌·빌드·ID 변형 회귀가 A7 **`generic=PASS/current_source=PASS`**를 지지. 미래 시즌 미출시를 기다릴 이유가 없고, WSE 전수·영구 GPT 수동 분류 Gate가 없다.
- **`product_integration=PENDING`**: 사용자 개별 입력, 검증된 목표 ilvl G/J/F/O 자동 완성, 해당 아이템 정확 SimC 효과·옵션/프로필 설치, DPS/SEM·95% 판단까지 이어지는 E2E 영수증은 아직 없으므로 A7 source PASS로 승격하지 않는다. 이 축은 뒤따르는 A8/A9/환경 구축·P1 사용자 연결 개발과 합쳐서 검증한다. 나머지 미선택 아이템/WSE 때문에 기본 환경을 막지 않는다.

## 4. 78개 상태 및 다음 작업

상태 정본 [`78_ELEMENT_COMPLETION_CONTRACTS.json`](../78_ELEMENT_COMPLETION_CONTRACTS.json) A7 generic/current_source를 **각 1개 실제 scope PASS**로 변경, product_integration은 PENDING 유지. 역사 PASS는 A10/A11/G2 기존만 인정. 상태 생성표와 기존 78-row 상세 tracker가 자동 일치 검사 통과해야 한다. **다음 근거 검토 A8 SimC revision·동일 소스/바이너리 정체성**, 그다음 A9 SimC 원본 입력. 제품 E2E 미통과로 A8 코드 진행을 무조건 막는 새 Gate는 만들지 않되 A7 제품 통합 PENDING을 숨기지 않고 최종 DoD에서 확인한다.

권한: 격리 브랜치만, main/v003 immutable/Project UI/Work OS 승격 및 기존 주 제품 개발 채팅 주도권 무변경.
