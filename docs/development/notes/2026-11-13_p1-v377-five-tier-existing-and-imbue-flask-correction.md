# v377 — 5티어 유동 장착 기존 기능 복원·기름/주술사/영약 F 회계 재확인

- **Capability:** `TIER.FIVE.SLOTS`, `ENVIRONMENT.SEASON`, `O.OIL`, `F.FLASK`, `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Latest user decision (2026-11-13):**
  1. 현재 지원되는 **같은 기름의 최고 품질 CHMV**는 치명·가속에 각각 **동일 rating q**가 한 손 적용 단위다. 이 제품의 수치 확보에 필요하지 않은 아이템별·스탯별 중복 Native와 독립 검증 Gate는 금지. 수치는 신규 시즌에서 그대로 복사하지 않고 해당 빌드의 신뢰된 SimC/DB2 원본이 공급한 최고 품질 값을 사용.
  2. 물리 무기 손/무기 유형·임시 마부 중복의 기본 규칙은 공통 제품 규칙이며 **시즌마다 새로 발견/재인증하는 대상이 아님**. 다만 새 아이템 고유 레벨/적용 제한의 변경과 실제 선택 손은 처리.
  3. **고양/정기 주술사의 불꽃혓바닥 무기·질풍의 무기** 등 SimC APL의 무기 강화와 일반 기름은 동일 손에서 배타적이다. 단일/쌍수/손별 적용·선택 스킬·특성·시뮬레이터 원본으로 결정하며 기름 O를 중복 계상하거나 존재하지 않는 적용을 가정하지 않는다. 죽음의 기사 `v294` 룬벼리기는 별도 **영구** 무기 마부로 구분한다.
  4. **티어 5개 원본 → 사용자 특수장비/장식에 따라 4개 유동 장착은 기존에 구현되어 있었다.** v376의 '유동 조합 미구현' 단정은 철회. 새 시즌의 원본 선택 파이프라인과의 연결은 따로 구분해 점검.
  5. **영약 F**는 선택된 스탯의 최종 rating 하한으로 작용한다. 따라서 `c_final_s=0`은 `F_s>0`일 때 물리적으로 불가능하나, **자유 장비 분배 `x_s=0`은 허용**하고 후보 탐색이 이 경계를 빠뜨리면 안 된다. 다른 F 종류 선택은 다른 고정 조건/시뮬레이션 정체성이다.
- **Verified GitHub implementation:** `v101_common_representative_equipment.py`의 `reconcile_current_season_five_tier()`는 정확한 5개 tier_map을 받아 사용자의 일반 special/crafted 겹침 후 4개를 유지하며 촉매 부위를 취급한다. `apply_user_equipment(... flexible_current_tier=True)`를 `v098_target_user_scenario_bootstrap.py`에서 `current_season_product`일 때 이미 호출한다. `tests/test_v187_current_season_tier_overlay.py`에는 26개 전문화의 머리 장식→가슴 티어 대체, 촉매 다섯째, 한계를 초과한 겹침 차단, 실제 v098 연계 회귀가 있다. **지금 새로 실행한 PASS는 없음**.
- **Important difference:** `v232_simc_only_ordinary_representative.py`는 최초 일반 대표 G의 장비 선택에 `chooser.FOUR`를 사용한다. 이는 `v101/v098`의 유동 4/5 기능 부재 증거가 아니다. 다만 `v098`의 `season_profile_inputs` 모드는 현재 `not user["special_items"] and not user["embellishments"]`를 요구하므로, **신규 설치 시즌 개인 특수/장식 조합으로의 연계는 아직 제한**. 이때 새 유동 조합 함수를 중복 작성하지 말고 기존 v101 경로에 신 시즌의 검증된 tier/gear source를 전달하고 대상 원본/예산 프로필 정체성을 재검증한다.
- **F floor evidence:** `v065_v015_scheduler_adapter.budget_with_fixed_components`는 `max(...,F_s-O_s,0)`를 적용하고 `v091_weapon_oil_external_adapter.propose`는 최종 목표와 실제 SimC gear_* override + flask vector를 비교한다. 이는 F를 후처리에서 추가하지 않고 fixed 하한을 보존한다는 뜻이다. `v197_verified_effect_budget.py`도 `minimum_final_per_stat=J+F+O+L+E`를 계산한다. 신규 시즌 F 수치는 과거 165를 복사하지 않는다.
- **Shaman status:** `v098`는 DK `runeforge_by_hand`를 처리하지만, `windfury_weapon/flametongue_weapon` 충돌 선택/손별 오일 무효화 규칙은 현재 코드·v363 개발 노트에서 미완료로 확인. 먼저 선택된 SimC 프로필의 APL과 제품 옵션 관계를 연결해야 하며, 현재 기름 ON을 주술사 해당 손에 무조건 유효하다고 가정하면 안 된다. **이번 커밋은 정책·감사 정정이며 새 코드 연결/Native 검증은 하지 않음.**
- **Current game background, not executable proof:** 외부 SimC 공개 MID2 Enhancement 프로필은 `temporary_enchant=disabled`, `actions.precombat=windfury_weapon`, `flametongue_weapon`. 외부 웹 확인은 제품의 자동 API/DB2/SimC 봉인 원본 증거로 사용하지 않음.
- **Remaining:** 기존 v187 테스트를 무효화하지 않고 신규 시즌 v216→v098 통합에서 special/embellishments 제한을 정식 물리 프로필 소스로 풀기, Shaman 손별 임시 강화/일반 기름 배타성 및 옵션 반영, 최적화 free=0 경계가 세대별 캐시/탐색에서 누락되지 않는지 실제 후보 테스트. 동일 시즌 캐시/Native 재사용, 불필요한 완전 재검증 금지. G/J/F/O READY, 실제 Windows E2E 계속 PENDING.
- **Verification:** 이번 문서 교정은 실제 GitHub 소스와 역사 테스트의 **정적 열람** 증거. 신규 소스 테스트·Actions·Native·API 수집 **0회**. `main`, 정적 캐시, Project UI, 공식 권한 불변.
