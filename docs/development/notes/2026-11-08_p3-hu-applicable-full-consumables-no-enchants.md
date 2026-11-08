# P3-HU · 고양 주술사 전체 적용 가능한 소모품, 영구마부·선택 특수장비 제외 (2026-11-08)

- **Capability:** `PRODUCT.E2E`, `CHARACTER.PROFILE`, `O.OIL`
- **Keywords:** P3-HU, enhancement, food, potion, augmentation, omnium, oil, shaman weapon imbue, DPS
- **Prior evidence:** [P3-HT Native #42470887863](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42470887863): 고양 334, 티어 2/4pc·민첩2542·raid1 확인, 음식/물약/증강/옴니움은 OFF. Pin SimC `c20e2ad52e4c33711f74272309a5748125175fe8` 공식 MID2 고양 source 및 기존 v108에는 음식 `harandar_celebration`, 물약 `potion_of_recklessness_2`, 증강 `void_touched`, 옴니움 `136822:1/136823:1/136817:1/136821:1/136814:1`가 있다. 12.1.5 고양 가이드는 무기 오일과 Windfury/Flametongue를 동시 사용하지 말 것을 권고.
- **Decision:** `CONNECT` — 기존 v098의 `season_controls`를 한정 제로베이스 실험으로 전달. 기존 영약241324, 보석5, 실제 tier/raid, 두 장신구 보존. 영구마부/선택 특수장비 OFF. 고양은 전문화 고유 무기 강화 유지 위해 oil OFF/O0. 다른 전문화의 일반 oil 지원 변경 없음.
- **Changes:** 기존 P3-FZ one-shot 요청 JSON 단독 트리거 추가, 기존 v108의 source 인식 토큰/Omnium preset만 입력. 기존 v216→v212→v098→v096→v094 DPS, P3-HT native 감사 JSON2 재사용; 신규 효과 엔진·가짜 시즌 품질 Gate 없음.
- **Verification:** CODE_PENDING: offline / 신규 실 Native 아직 NOT_RUN. P3-HT 실 2/4pc/레이드 증거는 역사 재사용이며 본 소모품 활성 입증이 아님.
- **Remaining:** exact isolated one-shot 실행, SimC Native에 실제 적용된 음식·물약·증강·옴니움, G/J/F/O, primary, 티어, 95%/SEM을 관측. 최고품질 Policy A UI 선택지 전면 발행은 별도.
- **Efficiency:** 기존 바이너리/수집기/적응형 엔진 사용; 새 SimC build0, 효과 재현0, 고양 oil/native0, 실제 실행 3+6 Native 한정, 기타 전문화 추가 시험 없음.
