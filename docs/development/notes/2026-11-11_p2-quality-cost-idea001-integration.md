# 2026-11-11 P2 — 사용자 우선순위 교정과 IDEA-001 고도화

- **Capability:** `OPTIMIZER.POLICY`, `DEV.CONTINUITY`.
- **Keywords:** v316, 10min soft target, quality first, cost Pareto, IDEA-001, confirm reserve, exact iterations, 95, cached receipt.
- **Prior evidence:** 실제 [v313 8/8](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42843524976), [v314 15/16+1 partial](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42846073820), [v315 10-case original audit](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42859573357), [v316 offline 635 PASS/2 SKIP](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42867821279).
- **Decision:** `REUSE/EXTEND` IDEA-001. 5~10분 사용자 목표 유지하지만 600초 초과는 알고리즘 자동 탈락이 아님. 정확한 확인 DPS·SEM와 총 iterations/wall/CPU/I/O의 트레이드오프를 먼저 비교. 중복 IDEA-008 발급하지 않음.
- **Changes:** `IDEA-001` 상세 가설/반증, 아이디어 README, benchmark 및 DECISIONS의 기준 정리. v290 제품 기본·v291 캐시·SimC 기계적 실행 소유 변경 없음.
- **Verification:** 이번 문서 기획은 구현/테스트/Native PASS가 아님. 기존 v316 opt-in은 offline에서만 검증. 다음 실측 결과는 별도 Actions 영수증으로 판정.
- **Remaining:** 신규 사용자 1조건 최소 Native trace 실증 → 기존 35/320 확인 예약의 선택형 offline ablation → 동일 iterations·동일 wall 분리 비교. 가설이 효율/품질 개선 없이 중복 I/O·탐사 누락만 늘면 HOLD.
- **Efficiency:** 새로운 회귀모델/탐색 실행기/정적 DB 재구축 없음. 같은 시즌 검증 바이너리·정적 증거 재사용, 신규 사용자 DPS 세션과 기존 DPS 캐시 분리. 이번 단계 비용은 작은 문서 수정과 최소 이후 검증으로 제한.
