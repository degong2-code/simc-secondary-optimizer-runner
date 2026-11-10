# 2026-11-11 P2 v317 — 신규 사용자 프로필에서 v316 실 Native 계측 최소 실증

- **Capability:** `OPTIMIZER.POLICY`, `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** v317, v316, Arms Warrior, new profile, 12 Native cap, case trace, 35/320 exact, 10min soft target, source SHA.
- **Prior evidence:** [v316 합성 계측 #42867821279](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42867821279) 635 PASS/2 SKIP, Native0; [v314 15/16](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42846073820), 1 partial.
- **Decision:** `REUSE/CONNECT` original v113/v216/v212→v098/v291, v316 `case_timing_trace=True`; 한 번에 Arms/ilvl334/manual T3250/일반보석4/특수0/O0, 원본 새 프로필. 10분 초과 알고리즘 폐기 금지; 1800초는 이 **12-call one-shot 안전 상한**이지 품질 평가 하드 탈락선이 아님.
- **Changes:** 한정 standalone one-shot 실행기·3개 guard offline 테스트·push-only Actions workflow. 12 Native 이하의 per-case timing, 35/320, 300/600 체크포인트, exact SHA, 같은 세션 cache-only 신규0, 원본 Native ZIP 최대7일 보존. v290/v291 정책·캐시·journal·사용자 UI 불변.
- **Verification:** 코드/계약은 Github 분기에 격리. 실행 영수증 확인 전 `PENDING_REAL_NATIVE`; 이번 설명 자체는 신규 Native PASS가 아님. 별도 Actions 실행/성공/실패는 정확 run id로 이후 보고한다.
- **Remaining:** 실제 Build/바이너리·신규 사용자 소스/캐시 일치 → v316 real trace 데이터 확인; 그다음 동일 iterations A/B와 동일 시간 A/B 분리; IDEA-001 확인 예산 정책은 지금 미실행.
- **Efficiency:** 기존 바이너리 SHA와 시즌 원본 조립 경로 재사용; 불필요한 전 26스펙/1008-call 재시험 없음. 실행별 실제 원본 열람·캐시 재생 검증; 실 SimC 실패·빌드 drift는 원문 차단.
