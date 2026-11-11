# P1 — 기본 실행 N56/320 연속 Native 제품 종단 단일 시험
- **Capability:** `PRODUCT.E2E`, `OPTIMIZER.POLICY`, `DEV.CONTINUITY`.
- **Keywords:** v334, survival hunter, fresh profile, primary start, v293, Native N56, CI.
- **Prior evidence:** [v333 Chrome 한국어 입력 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42983424219), [v331 N56 연구](2026-11-11_p2-v331-unholy-fixed-scout-n-final-study.md), [기존 실제 Native HTTP probe](../../../integration_probes/p3_haj_real_local_web_native_e2e.py).
- **Decision:** `CONNECT` — 전체 Native 재감사 없이 새 생존 사냥꾼 334/자동 T/4보석 1개 사용자 입력, 기존 시즌 빌드·정확 바이너리 재사용. 실제 기본 /longrun/start continuous=True, v290 N56, 내부 검증 상한 DPS12.
- **Changes:** 기존 p2/p3_haj 실 제품 시험 경로에 opt-in primary를 추가. 원래 prepare/resume 시험 기본 동작 유지. source/Build/프로필/CHMV/12회/95%/원본 JSON2 영수증 확인.
- **Verification:** [v334 실제 Native 1회 Actions](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/workflows/p1_v334_primary_n56_native_once.yml) 신규 실행 결과 확인 전 미확정. v333 Chrome은 0 Native이므로 이 검증을 대신하지 않음.
- **Remaining:** Actions 결과 대사, 성공 시 최신 상태 기록; 실제 사용자 Windows 브라우저에서 SimC 경로/중단·재개/결과 확인 별도 미실증.
- **Efficiency:** 동일 시즌 원본 바이너리 아티팩트 재사용(기한 내), G/J/F/O 환경 Native 최대3, DPS Native 최대12. v331 343 호출 전수 반복 및 새 알고리즘 연구 없음.
