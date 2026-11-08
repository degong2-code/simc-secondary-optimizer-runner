# P3-HY · 원본 시즌 환경 설치 후 v291 실제 Native 3회/재개/캐시 검증 (2026-11-08)

- **Capability:** `OPTIMIZER.POLICY`, `PRODUCT.E2E`
- **Keywords:** v291, real SimC, Native, resume, cached replay, three cases, zero-history 334, source lock, ready
- **Prior evidence:** v291 P3-HX [focused #42481220760](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42481220760) 451 PASS/2 SKIP, 0 Native; v290 후보 엔진 [#42480039601](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42480039601) 441 PASS/2 SKIP, 0 Native; 기존 고양/옴니움/티어 실 [#42475536108](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42475536108) 6 DPS Native.
- **Decision:** `CONNECT` — 새 알고리즘/실행기를 실제 동일 빌드·동일 고양 대표 프로필 환경에서 한번 검증. 기존 v216/v212 G/J/F/O 설치·소모품/옴니움/시즌 실 원본 재사용, v098 profile/manifest를 **실행 없이** 준비, v096.source가 재인증한 context에 새 v291만 Native 수행.
- **Changes:** P3-FZ 기존 one-shot workflow의 오직 새 request JSON+marker `[p3-hy-longrun-three-native-once]`에 명시적 opt-in. 2 신규 SimC Native→동일 세션 1회 추가→cache-only 신규0회 실 replay; SHA 원본 입력/JSON2/receipt/세션 seal/JSONL ZIP로 7일 보존. `v094` 원래 6호출은 이 모드에서 미실행, 다른 모든 기존 request 경로 유지. 일반 웹 UI, 26스펙, 2000 Native 전수 실행은 없음.
- **Verification:** 실제 CI/Native **NOT_RUN** at authoring time. 집중 오프라인 검증과 one-shot 실제 Actions 영수증은 따로 확보한다.
- **Remaining:** 모든 신규 Native 입력/JSON2 SHA·레이드·티어·food·O·종료 상태가 실제 일치하는지 확인. v291 초반 3회가 최적해라는 주장 금지. 6회 제한 테스트의 장기 실행 확대는 추가 runtime 변경 및 제품 UI/예산 계약을 통해 제공.
- **Efficiency:** 신규 v291 Native 3회, 원래 v216 환경용 G1+F2 Native3, cached replay0; SimC binary 재컴파일0. 새 독립 효과 인증/메커니즘 없음. 기존 시즌 정적 원본/API 범위 초과 재수집 방지.
