# P2 아이디어별 영속 등록 + 공정 통합 비교 계약 (2026-11-11)

- **Capability:** `OPTIMIZER.POLICY`, `DEV.CONTINUITY`.
- **Keywords:** ideas, registry, per-idea document, future simultaneous comparison, separate evidence, Multi-Fidelity Successive Halving, Multi-start Trust Region, Adaptive Stratified Exploration, 95 only, eight spec, sixteen cases.
- **Prior evidence:** [기본 v290·opt-in v312 비교](2026-11-10_p2-v312-surrogate-5to10min-adaptive.md), [v313 4×2 실험](2026-11-11_p2-v313-four-spec-eight-distribution-fair-comparison.md), [후속 v314 8×2 신규 프로필 예약](2026-11-11_p2-v314-eight-fresh-profiles-after-v313.md); v290과 v312는 같은 1008 Native라도 각각 SimC iterations가 달라 동등한 계산량을 입증하지 않는다.
- **Decision:** `EXTEND`: 사용자 요청으로 **모든 아이디어를 독립 파일**에 기록하고, 공통 색인·공정 벤치마크 계약으로 한꺼번에 비교할 수 있도록 한다. 아이디어를 구현·검증·승격했다고 주장하지 않으며 기존 일정과 v290 기본은 유지한다.
- **Changes:** [IDEA-001](../algorithm_ideas/IDEA-001-multifidelity-successive-halving.md) 반복 정밀도 단계별 승급, [IDEA-002](../algorithm_ideas/IDEA-002-multistart-trust-region.md) 다중 시작점/신뢰영역, [IDEA-003](../algorithm_ideas/IDEA-003-adaptive-stratified-exploration.md) 새 제안인 공간별 적응형 층화 탐색을 별도 문서로 등록했다. [아이디어 목록](../algorithm_ideas/README.md)에서 기존 v290/v303-v306/v312와 아이디어 상태를 구별하고, [통합 비교 계약](../algorithm_ideas/BENCHMARK_PROTOCOL.md)은 신규 8전문화×2분포/기존 프로필 미사용/Native iterations 및 wall-clock/95 비교를 정의한다.
- **Verification:** `DOC_ONLY`: 각 아이디어의 Native/모델 구현/동등 예산 성능 시험은 이번 변경에서 수행하지 않는다. 문서 정합성은 후속 focused Actions 원본 영수증을 확인해 판단한다.
- **Remaining:** 각 아이디어 opt-in 구현 후 독립 오프라인·실제 SimC 검증과 8전문화×2분포 공정 비교; 기존 v313 종료 뒤 등록된 v314 순서를 지킨다. 모든 비교 결과는 동일한 근거 필드와 실패/보류 표시로 등록한다.
- **Efficiency:** 추가 Native 0, Actions 실험 트리거·캐시 identity·사용자 UI·main 불변. 동일 프로필/승인된 시즌 정적 자료 재활용, 검증 전에 새 엔진 고비용 전수 탐색 금지.
