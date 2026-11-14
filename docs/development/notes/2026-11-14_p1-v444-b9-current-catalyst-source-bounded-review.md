# v444 — B9 선택 촉매 원본 연결 및 정적 L 미확정 경계

- **Capability:** `TIER.SEASON`, `GEAR.SEASON`, `PRODUCT.E2E`, `DEV.CONTINUITY`
- **Keywords:** v444, B9, catalyst, tier, redirected_base_stats, original item ID, current season, profile, exact L
- **Prior evidence:** v040/v041/v042 과거 진단 Native 2+1+1, v187 현재 시즌 오프라인 회귀 #43550242720, v182 Linux/Windows 회귀 #43550242725.
- **Decision:** `REUSE` → `CONNECT` → `PARTIAL_ACCEPT`: 범용·동일 시즌 소스 검증만 PASS; Native 정확 정적 L이 없는 선택 촉매 제품 통합은 PENDING.
- **Changes:** v101 촉매 원본 동부위/계열/마스크/주능력치 검증과 v187 26 DPS·위조/충돌 회귀 및 v208 테스트 픽스처 교정.
- **Verification:** v187 #43550242720 SUCCESS(109+36+7), v182 #43550242725 Linux/Windows SUCCESS(102+145+3 per OS), v401 후속 문서 상태 검사 별도 수행.
- **Remaining:** 실 70783 사용자 선택 촉매 Native JSON2·정확 static L·G/B/T·DPS 전과정 관측 미완료, v098 제품 경로는 L 부재 시 fail-closed. B9 product PENDING.
- **Efficiency:** 신규 Native/API/DB2=0; 기존 기능/캐시/Native 증거만 범위 내 재사용, 무관한 효과 인증·전 전문화 Native 반복·main 변경 없음.

- 적용 기능: B9 촉매 변환. USER 선택형이며 미선택 목록의 전수 실측은 기본 환경 Gate가 아니다.
- 수정: `runner/v101_common_representative_equipment.py`에서 `redirected_base_stats` 원본을 동일 시즌 승인 카탈로그의 실제 항목으로 조회하고 올바른 물리 부위, 방어구 계열, 클래스 마스크, 주능력치, 중복 슬롯을 검증. 실패하면 Native 시작 전 차단.
- 회귀: `tests/test_v187_current_season_tier_overlay.py`의 26 DPS별 소스/티어 경로, 미등록 원본·잘못된 부위/계열, 중복 슬롯, v098 실제 사용자 입력→source-only SimC 프로필 생성, 정확 L 캐시 누락 시 제품 실행 차단. v208의 chest 테스트 픽스처 원본 ID도 잘못된 어깨에서 실제 동일 시즌 가슴으로 수정.
- 동일 시즌 원본 범위: `data/current_season_product_gear_db.json` 및 `data/current_season_tier_itemsets.json`의 12.1.5.70575 원본 조합; 현재 70783 제품의 선택 촉매 Native 실증으로 오인하지 않는다.
- CI: [v187 #43550242720](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43550242720) SUCCESS, 109+36+7 tests, [v182 #43550242725](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43550242725) Linux/Windows SUCCESS, 102+145+3 tests/OS. [v401 #43550242722](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43550242722) 이전 JSON의 일관성 검증 PASS; 본 문서 반영 후 별도 최신 CI로 판정.
- 재사용 역사 실측: [v040 #40108486179](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40108486179) 2회, [v041 #40112424280](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40112424280) 1회, [v042 #40120755711](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40120755711) 1회. 모두 334 촉매 진단; 실제 게임 334 bonus 인증, 사용자 선택 제품 T/G 및 전체 DPS 최적화는 증명하지 않음. 기존 영수증은 제품 출처 승격에 사용하지 않음.
- 상태: B9 generic PASS, current_source PASS(위 동일 시즌 범위), product_integration PENDING, historical PENDING. 실제 Native static L 원본 검증 및 최종 v096/DPS 연결 미완성. `SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT` 차단을 유지.
- 효율: 새 Native 0, 외부 API 0, DB2 0, 독립 proc 인증 Gate 0. 기존 SimC 책임 및 프로젝트 권한 유지; main/v003/Project UI/원본 v016 미변경. 다음 순차 검토 B10.
