# 2026-11-06 · P3-GL · F 최고품질 우선 및 gear_* 0

- **Capability:** `F.FLASK`, `ENVIRONMENT.WEB`, `SOURCE.SEAL`
- **Keywords:** P3-GL, F, flask, highest quality, gear_haste_rating=0, v216, v269, Native worklist, source-only
- **Prior evidence:** [실 T1 #42170351404](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42170351404) Native 8회 보고, F 추가 배치 PENDING, 환경 NOT_READY. 고정 SimC `c20e2ad52e4c33711f74272309a5748125175fe8` `engine/player/player.cpp:1752-1771`은 `gear.get_stat(stat)<0`일 때 장비 기본값, `>=0`이면 정확히 지정 `gear_*` 값(0 포함)을 적용함. 원래 `v269.prepare`는 명시적 `flask=disabled` vs 지정 영약을 비교하고 `snapshot_stats`에서 관측함.
- **Decision:** `CONNECT` 같은 효과 계열 내 소스 최고 품질 영약만 우선 측정하되, 소스 이름으로 효과 동일성/사용조건을 인증하지 않는다. 서로 다른 영약 효과, 모호한 token, 최고품질 동순위는 별도로 보존. SimC 효과 처리, v281 정확한 ItemID, v278 원본 paired Native, v091/v222 F·gear 회계의 소유권을 유지한다.
- **Changes:** `runner/v216_environment_build_coordinator.py:_prioritize_highest_source_quality_F` 및 자동 F 연결. 소스 token stem과 `_<quality>` suffix로 F Native 후보의 낮은 품질만 후순위 제외. `v269._player`에서 실제 CHMV JSON2 필드가 있는 전부 0 기준을 유효로 허용; 필드 자체 미존재면 차단. `tests/test_v269_simc_chmv_effect_snapshot.py` 회귀 수정, `tests/test_p3_gl_highest_quality_flask_measurement.py` 추가, 오프라인 focused 연결.
- **Verification:** 소스 변경 최초 commit `5e8adb9f93680318eabb0c331bc25d76e45864b2` focused #42182882274는 **DEV_LEDGER NOTE_REQUIRED_FIELD로 실패**, 코드 테스트까지 진행되지 않았음. 이 노트 필드 교정 이후 focused 재실행의 결과가 실제 확인되기 전에는 PASS로 표기하지 않음. 신규 SimC Native/게임 소스 HTTP/T1 0.
- **Remaining:** 기존 T1에서 실제 F 최고 품질 수치·J 보석 특수 ID·O/G/예산 소유권 및 정책 A/실 설치 READY 미완료. 새 F 후보 선택은 source-only Native 순위일 뿐 실 최고 품질 효과/동일성 증거가 아니다. `main`·불변 v003·Project UI·Work OS 및 기존 제품 채팅 소유권 불변.
- **Efficiency:** 영약 효과 4종×각 2품질=8개인 예시에서 Native 측정 후보 8→4(최대 16→8회, 공용 baseline 캐시는 더 적음). 소스 탐색/실효과 계산기 신규 구현 0. 오프라인 테스트는 원본 캐시/선택 경로를 변경하지 않음.
