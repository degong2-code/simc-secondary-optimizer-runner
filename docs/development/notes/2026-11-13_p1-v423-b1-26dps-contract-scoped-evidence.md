# v423 — B1 26 DPS 계약: 범용·현재 원본 범위 PASS, 제품 통합 보류

- **Capability:** `CHARACTER.PROFILE`, `ENVIRONMENT.WEB`.
- **Keywords:** B1, 26 DPS, v143, v169, v098, v106, v113, weapon forms, primary stat, augmentation exclusion, v176, current 70783.
- **Prior evidence:** [v422 A11](2026-11-13_p1-v422-a11-source-stage-receipt-reuse-three-axis.md), [v417 실제 제품](2026-11-13_p1-v417-bounded-post-bridge-product-e2e-once.md), [v383 기존 Windows 증거](2026-11-13_p1-v383-a10-a11-g2-archived-native-receipt-reuse.md).
- **Decision:** `REUSE` — B1은 **generic/current_source PASS, historical PASS, product_integration PENDING**. 26개 계약 존재와 현재 한 전문화의 제품 소비는 26개 전부의 최신 제품 통합·무기 정확성을 증명하지 않는다.
- **Changes:** 78개 계약 JSON·자동 생성표·상세 추적표·회귀 테스트·문서 인덱스에 B1의 범위별 증거와 다음 B2만 기록. 기존 제품/SimC/무기 선택 코드 무변경.
- **Verification:** [v113 양 OS #43391249405](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43391249405), [v417 실제 Windows #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756), [v176 과거 26 물리 #40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357).
- **Remaining:** B1 26개 현재 빌드 대표 장비·무기 선택의 실제 제품 수용 범위는 별도; B2 목표 ilvl 순차 검토, B3/B4/B5 일반 장비·무기 ID/성능 세부 검증 독립. 최종 ZERO-SOURCE→USER-E2E PENDING.
- **Efficiency:** 현재 코드·영수증 재사용, 신규 Native0, HTTP/DB2 수집0, 과거 26 전문화 Native 재실행0, 프로필/캐시 교체0.

## 1. B1 고정 계약과 범용성

`runner/v143_specialization_contracts.py`는 26개 `class/spec` 계약과 주능력치/방어구 계열/7가지 무기 형태, 티어 슬롯·직업/종족 조건을 표현한다. 증강 기원사, 탱커 및 힐러 전문화는 등록하지 않는다. `v169.shape_weapons/select_class_spec`는 전문화의 형태별 주/보조 손, 아이템 주능력치·클래스 마스크·원거리/양손/쌍수·Fury 양손 쌍수 조건을 원본 후보와 결합한다. 잘못된 주능력치·잘못된 tier/gear build·누락 후보를 차단하고 `all_items_physical_simc_accepted=False`를 유지한다.

**GENERALIZATION_REGRESSION:** [#43391249405](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43391249405), tested `5732defbeba44db51427e7c1172724365ccca298`, Linux/Windows 각각 331 PASS/1 SKIP. 포함된 `tests/test_v106_user_session_controller.py`는 26 기본 사용자 입력/전문화 계약을 장비 전체 선택 없이 검사하고, `tests/test_v113_local_web_api_offline.py`는 health/bootstrap/defaults 26개와 구 24개 완전 SimC fixture 없이도 26개 계획 생성·Native0을 검사한다. `tests/test_v169_source_first_representative_stage.py` 원래 장비/무기 26개 소스 기반 프로필/4pc와 44개 손 슬롯의 주능력치·종류·클래스 마스크·다른 빌드 거부, `tests/test_v187_current_season_tier_overlay.py` 26개 재배치 검사를 **코드에서 확인**했다. 이 마지막 두 테스트를 이번에 새로 실행한 것은 아니다.

## 2. 현재 원본과 역사 Native를 구분

**CURRENT_SOURCE_REAL:** [v417 #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756), tested `89d4810baf5e05f1c5c6f355f39a5f35ca9ec4e7`, KR Retail `12.1.5.70783`, pinned SimC revision `de11f57df75dda668bae6ac7043a43b98831fa96`. 현 빌드에서 원본 기어209·티어65 카탈로그→검증 대표 프로필/설치→Survival Hunter 1개 실제 DPS Native12까지 B1 선택·대표 장비 경로의 **현재 소비 범위 한정** 입증. 26개 모든 전문화의 현 빌드 아이템 적법성이나 DPS 성공은 입증하지 않는다.

**HISTORICAL_SCOPED:** [v176 #40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357), tested `5bba261f01da150a3b7cc881ff1cf7969d7c780c`. 26개 기본 물리 SimC 수용: **신규 Native25+동일 범위 이전 영수증1 재사용**, 프로필 당 35 iterations, **최적화·SEM·95% 판정 없이**. 이후 v169 테스트가 탐지한 과거 잘못된 주능력치 무기 문제는 SimC 프로필 수용=정확한 게임 장비 선택이 아님을 보여준다. 과거 v176 증거를 최신 70783의 26개 장비 완전 정확성으로 승격하지 않는다.

## 3. 제품 통합 PENDING 및 후속

`v098._profile_supplier_registry`는 `v143` 26개/기존24+독립2/`v106.SUPPORTED`/`v113` 기본 UI 및 시즌 공급자 집합을 확인하고 차이를 거부한다. `v113` 실제 로컬 API는 26종 선택지를 노출한다. 하지만 최신 실 제품 v417은 그중 **한 전문화**와 기본 조건만 검증했고, v176은 다른 역사 조건의 물리 수용뿐이다. 따라서 B1 **제품 통합은 PENDING**: 26개 사용자별 실제 설치·무기·대표 프로필→DPS/SEM/95%의 완료를 주장하지 않는다. 다음 B2는 B1 범용/현재 원본 검토를 재활용해 진행하되, B1 제품 축은 별도 후속 추적한다.
