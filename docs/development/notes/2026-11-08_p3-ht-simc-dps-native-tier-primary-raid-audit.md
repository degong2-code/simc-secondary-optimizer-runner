# P3-HT · 실제 DPS 후보의 tier·primary·raid 로그 보존 진단 (2026-11-08)

- **Capability:** `PRODUCT.E2E`, `CHARACTER.PROFILE`, `TIER.SEASON`
- **Keywords:** P3-HT, tier4, 2pc, 4pc, Agility, primary, raid buffs, v094, native JSON2, audit, DPS
- **Prior evidence:** P3-HR 징벌 [#42466284163](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42466284163) 및 P3-HS 고양 [#42469206828](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42469206828)은 환경+적응형 DPS PASS이나 기존 artifact에는 환경 G/F의 3개 원본 JSON만 보존되어 **실 DPS 후보의 buffed primary/tier-proc/raid 효과는 확인할 수 없음**. G 실 원본은 고양 4개 tier ItemID·민첩 장비합1531·buffed2256·optimal_raid1/전투의 외침 등을 관측. 현 P3-HS one-shot에는 음식·물약·증강/옴니움은 기본 OFF.
- **Decision:** `REUSE` — 원래 v094의 이미 실행된 6개 Native input SHA/JSON2 SHA·원래 프로필에서 관측값을 추출하고 1개 실제 최고 DPS JSON2만 압축 보존. SimC 티어 발동 로직을 재구현/인증하지 않고 실제 적용 여부만 사용자 진단. 신규 재시험에서도 전체 Native 한정 3+6이며 **이 감사 자체의 추가 Native 0**.
- **Changes:** P3-HS 기존 one-shot 실행에 선택형 `P3_T1_DPS_NATIVE_AUDIT_ONCE` 연결. `p3_ht_observe_existing_dps_native.py`는 원래 v094 input/result SHA를 대조하고 가장 높은 관측 mean의 한 case 원본 SimC 입력·JSON2/공통 프로필/후보표와 6개 타이핑 요약을 소형 artifact에 보존. 새 효과 엔진/신규 통계 Gate 없음.
- **Verification:** 오프라인 집중 시험 및 실제 P3-HS 추출 **NOT_RUN** (실행 전 기록). 기존 2026-11-08 G/F 원본의 실제 Native와 두 전문화 DPS PASS는 재사용한 역사 증거이며 이번 DPS JSON2 프로필 검증 증거로 대체할 수 없음.
- **Remaining:** One-shot 기존 요청 JSON 단독 갱신 후 실 Native 후보 JSON2에서 2/4pc 관련 실제 `fire_nova`/`short_circuit`/buff, 민첩 및 무기 상태, `optimal_raid` 및 상시 버프, 음식·물약·증강 등을 확인. 4pc 미작동이면 SimC 공식 `set_bonus` 소스와 프로필 활성 조건 대조 후 최소 범위 교정. DPS 수치의 외부 표준과 일대일 동등조건 비교 전 '낮다'는 사실로 단정 금지.
- **Efficiency:** 이미 있는 6개 Native 원본의 선별 SHA 검증/압축만 추가, 무조건 새로운 효과 검증 Gate·전체 26개 전문화 재시험 금지. 원본 감사 ZIP은 임시 7일, 제품 DPS 캐시로 승격하지 않음.
