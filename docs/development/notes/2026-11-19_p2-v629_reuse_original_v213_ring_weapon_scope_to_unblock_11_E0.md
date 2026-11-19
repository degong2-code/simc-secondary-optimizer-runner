# P2 v629 — 봉인 v213 반지·무기 슬롯 정보의 기존 v196 등록 소비 누락 수정

2026-11-19 KST · 격리 브랜치 `probe/chat-cache-v035-20261024`. 직전 v628의 기본 사용자 SimC 실행 경로·AI 비개입·캐시/취소·재개·95% 엔진은 그대로. 사용자가 요구한 **모든 지원 마부 부위별 동시 선택**을 위해 실제 시즌 마부가 *입력 목록에 올라오기 직전*의 최소 소비 경계만 수정.

## 1. 사용자 가치와 실제 결함

- 사용자 경로: **새 시즌 G/J/F/O 자동 구축 → 기존 원본 v191/v211/v213/v583 및 v220 Policy A → v196/v212 등록 → 일반 UI 선택 → v106/v098의 실제 최종 장비 ID/무기 손/마부 → 기존 v096/SimC 검색**. 이번 코드는 **v196→v220의 소스 전달**만 수정한다. 전체 장비·아이템 DB, 신규 효과 엔진/최적화 모델은 추가하지 않는다.
- 원본 [v618 실제 70961 설치 #44438148520](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44438148520) artifact [#14489588587](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44438148520/artifacts/14489588587), ZIP SHA256 `c13f0c58dbb62d0bc689587458b8a6ff171046f76e5db4fb6e81b70182c6a88a`, 원본 `V618_REAL_INSTALLED_V212.json` SHA256 `434789420855bc979f601e9449361d3e00d10d6bb385e9dac5190ab67641877b`를 **직접 다운로드해 원문 필드 확인**. 실제 빌드 `12.1.5.70961`, SimC source `9933ffb946fb55b1fa66657b848f519ac19006e1`, 기존 19개 최고품질 E0는 등록.
- 원본 옵션별 결손: **11개** `EXACT_PHYSICAL_SLOT_OR_HAND_RELATION_NOT_VERIFIED` *만* 남음: `7967,7979,7981,7983,8007,8009,8011,8037,8039,8041,8689`. 별도 **8개** `EVIDENCE_MISSING:chmv_budget`도 함께 남음: `7965,7969,7995,7997,8021,8023,8025,8027`. 원본 quality pending `[]`. `11+8=19`이며 모두 미등록 상태인 사실을 보존. 이 8개를 임의로 `E=0`이라고 표시하거나 이전 70783의 정적 E 수치를 70961 검증값으로 재사용하지 않음.
- **최초 코드 원인:** `v216._v217_policy_A_source_relation_receipts`는 원래 봉인 `source_catalog["catalog"]["enchants"]["items"]`를 사용하여 `v220.candidate_from_source_enchant`의 정확한 반지 가족 `finger1/finger2`/무기 클래스 마스크·손 미확정 범위를 인지하며 receipt identity를 생성. 반면 **`v196.prepare_verified_fresh_choices`는 슬롯 상태·slot_group을 제거한 `source_catalog["v196_enchant_source"]["rows"]`를 같은 v220 함수에 전달**해서 반지·무기를 `SOURCE_SLOT_UNRESOLVED`로 오판. 기존 네 증거가 있더라도 source receipt와 identity가 불일치하여 자동 등록이 막힘. **SimC 입력, Native 정적 회계, 품질 원본의 새 Gate 문제가 아니라 소비 필드 누락.**

## 2. 최소 수정 및 안전 경계

- 코드 `233039a6694443e73e858fb6fcc6d8dfdea323b3`: **v196 한 지점**에서 기존 `source_bridge.verify_catalog(source_catalog)`가 검증한 봉인된 `catalog.enchants.items`를 `original_source_rows_by_id`로 전달. 원래 `v196_enchant_source.rows`와 **정확 ID 전체 집합·개수·token·quality_rank·item_class·inventory_type_mask·item_subclass_mask** 모두 상호 일치하도록 차단. 유효한 원본 슬롯 상태는 `SOURCE_MASK_RESOLVED` 또는 `WEAPON_SUBCLASS_PENDING_EXACT_HAND_APPLICABILITY`만 허용.
- 기존 `v220`은 **반지 양쪽에 같은 가족 적용 가능 / 무기 subclass는 가족까지만 인지**하도록 이미 구현되어 있으므로 변경하지 않음. 이후 **실제 사용자 최종 ItemID/무기 hand/subclass/mask**는 원래 `v098/v216`에서 별도 검사하며, 무기 가족 등록만으로 주·보조 손이 자동 적합하다고 주장하지 않음. 같은 슬롯에는 마부 하나만 선택. 어떤 원본 필드든 불일치하면 fail-closed.
- 기존 `v220.chmv_budget` 증거가 없는 **8개 정적 E 미확정**은 계속 등록 보류. SimC에 의한 효과/proc/APL/DPS 처리와 `B=G+J+F`, `T=B+O`, E/L/O 1회 회계, 수동 T 최우선, 95% 통계·캐시/재개는 전혀 변경하지 않음.
- 테스트는 기존 `tests/test_v220_catalog_auto_admission.py`와 `tests/test_v607_sealed_crafting_enchant_quality.py`의 **합성 v213/source projection fixture**를 실제 소스 구조와 맞춤. 새 `test_v629_sealed_v213_ring_and_weapon_slot_state_reaches_installer`는 raw v196에는 슬롯 상태가 없는 상황에서도 원본 v213를 전달하면 반지·무기 합성 E0가 기존 v220/v196 준비에 올라가고, 마스크 변조/예산 증거 부재 시 각각 차단하는 것을 검증. 과거 `tests/test_v240_v211_v213_fresh_catalog_handoff.py`의 **항상 부위 미해결 가정**을 새로운 원본 경계에 맞춰 수정(`c0dd16e869aa74c958f122bd9b28854d3c81505e`). 이 테스트들의 가짜 ID·E 벡터·receipt는 **실 사용자 옵션 승인 증거가 아님**.

## 3. 새 CI 영수증·비용과 제한

- [최종 focused #44466725249](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44466725249): **685 PASS, 2 SKIP**, 신규 회귀 포함.
- [최종 v212 Win+Ubuntu #44466725307](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44466725307): **양 플랫폼 각 529 PASS, 4 SKIP**.
- [정적 78 계약 #44466725214](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44466725214): SUCCESS; [v410 #44466725206](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44466725206) SUCCESS.
- 첫 코드 HEAD [v583 #44466613428](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44466613428) FAIL은 옛 **“반지는 항상 물리 범위 미확정”** 기대값 때문이며 테스트만 교정한 최종 v212/focused PASS와 구분한다. 별도 과거 [v213 source-to-catalog #44466613548](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44466613548) FAIL은 2026-11 시점 만료된 **2026년 이전** source artifact `v192-updated-simc-catalog-41017578894` 복원 불가; source 미확보 장애지 이번 코드/Native 실패로 오판하지 않음.
- **이번 신규 Native 0 / 신규 Wago HTTP·DB2 0 / SimC 재컴파일 0 / 기존 정적·DPS 캐시 무효화 0 / 새 solver·효과 인증 Gate·AI 런타임 0.** 다수 경로 기반 오프라인 CI fan-out 발생(기존 설계이며 신규 워크플로 제작하지 않음).
- **정확한 수락 경계:** 이미 봉인된 실제 70961 결과에서 11개가 *부위 상태 하나만* 부족했다는 것은 실측. 코드가 그 손실 경계를 복구한 것은 오프라인 검증. 그러나 **수정한 v196으로 동일 70961 시즌 전체 설치를 새로 실행한 원본 Native/receipt 없음**. 따라서 `published_verified_option_count`가 19→30으로 증가했다고 **주장 금지**. 무기/반지의 구체적인 현재 대표 아이템·hand 조합도 조건별 확인 필요.
- 다음은 현재 빌드의 같은 원본 stage workspace가 재사용 가능할 때만 **source-only v196/v212 등록수 및 새 E0 ID/hand 조건 1회 검증**, 필요한 새 자료만 최소 수집. 원본 stage가 없으면 차단 원인을 기록하고 **환경 Native6·DPS64 또는 26전문화 무조건 반복 금지**. 양수 E 8개는 정확한 현 시즌 정적 수치/원본 G 소유권 없이 E0로 승격하거나 합산 엔진을 먼저 작성하지 않는다.

## 4. 공식 원장·권한

`15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` 불변. 기존 주 제품 개발 채팅·격리 브랜치 허용, main 병합·v003 immutable·원본 v016 직접 통합·Project Sources UI·Work OS M0/Shared State 공식 승격 금지.

## 5. 후속 P2-1 기존 70961 stage 재사용 확인 — 원본 부재로 STOP (2026-11-19)

- 조사 당시 GitHub 브랜치 HEAD `efe19459ddf8c40a720e52907caecd6f8cd6b1b2`. `v196` 코드의 봉인 원본 `catalog.enchants.items` 전달 및 `v220` 원래 Policy A 재사용을 읽기 전용 확인. 이번 후속 단계에서 **신규 실제 등록 PASS는 발생하지 않았음**.
- 기존 실제 70961 [v618 run #44438148520](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44438148520)의 Actions artifact **2개** 확인: `#14490621359`는 `V611_REAL_70961_ENCHANT_ADMISSION_ONE_BUILD.json` 요약만, `#14489588587`은 `V618_REAL_INSTALLED_V212.json` 설치본만 포함. `v191/v211/v213` **원본 stage의 파일 바이트 또는 재사용 가능한 workspace는 업로드되지 않음**. 설치 JSON에 stage receipt SHA(예: `v213_stage=20d10c39b5547c5d175fbc52af64dd507219293ece6e10898768323cb9ab3674`)가 있어도 원래 봉인 파일을 복원·재인증하는 근거가 아님.
- 실제 실행 코드 `integration_probes/p1_v610_real_installed_enchant_one_build.py`가 `tempfile.TemporaryDirectory(prefix="v610-enchant-",dir=output_folder)`로 원본 `v217` stage를 일시 생성하고 run 종료 시 삭제함을 확인. 당시 workflow `.github/workflows/p1_v611_current_live_70961_enchant_build_once.yml`의 `upload-artifact` 대상도 위 두 JSON만. 브랜치 `data/` 최상위 목록에서도 70961 봉인 stage 원본 미발견. 이는 **확인한 Actions/저장소 범위의 부재**이며 외부 Windows 로컬 등 미접근 workspace 전체의 부재를 증명하지는 않음.
- 따라서 **첫 장애 = `CURRENT_70961_SEALED_V213_STAGE_NOT_REUSABLE_FROM_CHECKED_ARTIFACTS`**. 19개 실제 등록·보류 11+8·v629 오프라인 PASS는 유지; **19→30 실제 등록 수 확인 PENDING**. 설치본·요약 receipt만으로 원본 슬롯 가족 증거를 합성하거나 8개의 미확정 E를 0으로 만들지 않음.
- **STOP 및 비용:** 신규 Native 0, 신규 시즌 HTTP/DB2 0, DPS64 0, SimC 컴파일 0, 정적/DPS 캐시 폐기 0, 제품 코드 변경 0. 추후 같은 빌드의 **정확히 인증된 봉인 stage 바이트**를 확보하면 기존 `v196→v220→v212` source-only 검증 한 번으로 재개. 기존 stage가 계속 없다면 source-only 최소 재구축의 원본/비용을 별도로 검토하되 환경 Native6·DPS64·26전문화 전수 재실행을 자동 시작하지 않음. 공식 원장 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` 변경 없음.

## 6. v630 최신 사용자 결정 반영 — 과거 stage 복원 대신 실제 동일 빌드 새 원본 구축 및 v629 등록 PASS (2026-11-19)

**과거 stage를 고집하지 않는다.** 사용자 직접 결정에 따라 v629 뒤 첫 장애를 과거 임시 stage 부재로 고정했던 §5의 STOP은 최신 NEXT에서 해제. 기존 `v611→v610→v113.LocalJobs→v216/v217→v196/v220→v212` 원래 제품 실행 경로를 **현재 빌드의 새 출처·소스 stage**로 한 번 다시 실행하여, 동일 실행에서만 봉인·Policy A·실제 마부 등록을 검증했다. 이전 70961 봉인 stage 파일이나 70783 자료를 재사용하지 않았다. `v567`의 별도 완전 ZERO-SOURCE 엔진 PASS는 보존하며, **이번은 정확히 70961 소스/SimC 버전을 고정해 실제 동일 빌드의 빈 시즌 stage를 재생성한 시험**으로 범위를 구분한다.

- 수정 범위: 기존 `.github/workflows/p1_v611_current_live_70961_enchant_build_once.yml`의 명시적 **1회 opt-in 트리거·artifact 명칭만** (commit [af4e961a](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/af4e961a563a155cff15cc13d40dd7e8522c2e61)). 신규 환경/마부/예산/SimC 엔진 없음. 과거 시즌 입력 파일은 기존 workflow가 격리하고, `v610`은 일시 빈 run root에서 같은 빌드 출처를 다시 수집.
- [Windows Actions #44470852160](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44470852160) **SUCCESS**. 실제 원본 [compact artifact #14504292686](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44470852160/artifacts/14504292686), [설치 artifact #14504332493](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44470852160/artifacts/14504332493)를 다운로드해 ZIP 내 원본 JSON 직접 확인.
- 원본 `V611_REAL_70961_ENCHANT_ADMISSION_ONE_BUILD.json`: SHA256 `0c79423cbcb186af38855da1a1722fa0ef376b7339837b0933a2ba987f067a31`, `status=PASS_REAL_SEASON_V212_ENCHANTS_AUTO_REGISTERED`, `environment_ready=true`, `environment_installed=true`, `source_missing=[]`, `source_cached_old_season_used=false`, `actual_enchant_registration_count=30`; `live_game_build=12.1.5.70961` 및 SimC SHA `4f4472ac8687d029cd7d6041741f44aa98750ea1b3e953dfa7002dee1f38879f` 일치.
- 원본 `V618_REAL_INSTALLED_V212.json` (이름은 기존 재사용 코드의 레거시 출력명): SHA256 `9af7451b68e1682f790d0e688990e12bdf54d48bfe82dcba0bb33879e0d0c980`, 신규 설치 `manifest_sha256=4987ec724bf284a485cd675d55e83d5eb8ead6e0baeaa23022ad929ab9d3e5b8`, `source_catalog_manifest_sha256=494f672a35e4eba6026495bbd0a26b6b58363dad3087be59109959b25ffb03d1`. **`published_verified_option_count=30`**.
- **이전 19개 + 정확히 11개 신규 승인:** `7967, 7979, 7981, 7983, 8007, 8009, 8011, 8037, 8039, 8041, 8689`. 30개 전부 최고 품질 rank 2, 정적 `verified_fixed_E={crit:0,haste:0,mastery:0,versatility:0}`. `7967`은 `finger1/finger2` 반지 가족, 나머지 10개는 `WEAPON_SUBCLASS_NOT_YET_USER_SLOT_CERTIFIED` 무기 가족. 따라서 **등록은 실제 PASS**이나 무기마다 실제 대표 ItemID·주/보조 손·서브클래스 적합은 제품 `v098/v216`이 최종 선택 시 검사해야 하며 전부 손별 READY/E2E라고 확대하지 않는다.
- **나머지 8개** `7965,7969,7995,7997,8021,8023,8025,8027`: 실제 `optional_other_proof_pending_by_id`에 각각 `EVIDENCE_MISSING:chmv_budget` **한 가지**만 잔존. `E=0` 추정/과거 70783 고정수치 재사용 없이 해당 선택지만 보류. `optional_quality_pending_item_ids=[]`.
- 실제 검증 환경 `G=2850,J=92,F=165,O=0,B=T=3107`, ilvl334. **새 환경 Native6, 신규 사용자 DPS Native0, SimC 바이너리 캐시 HIT/재컴파일0, 과거 정적·DPS 캐시 폐기0, 새로운 탐색기·AI 런타임 0**. 실제 Native DPS/브라우저 30개 전부 인수 시험은 수행하지 않음. 기존 v624 한 부위 웹64 PASS, v627 두 부위 Native4 취소·재개 PASS는 독립 역사 증거로 유지.
- **P2-1 수락:** v629 최초 slot-family 전달 수정이 실제 새 시즌 stage에서 **19→30 등록 PASS로 확인됨**. 다음은 무기 손별 사용자 선택에 실제 첫 장애가 있으면 해당 정확한 하나의 ItemID만 기존 `v098/v216`로 검증하고, 그 전에 대량 Native를 실행하지 않음. 양수 정적 E 8개의 같은 빌드 소유권 증거를 사용 범위에 맞게 채우는 P2를 계속 추진하되, 검증된 BASE/E0는 차단하지 않는다.
- 공식 원장 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`; main/v003/v016/Project UI/Work OS 및 주 개발 소유권 불변.
