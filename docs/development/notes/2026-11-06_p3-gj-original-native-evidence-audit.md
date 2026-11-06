# 2026-11-06 · P3-GJ · 실 T1 Native 원본 유실 방지 및 1회 실행 통제

- **Capability:** `SOURCE.SEAL`, `ENVIRONMENT.WEB`, `F.FLASK`
- **Keywords:** P3-GJ, T1, Native8, v277, v278, ephemeral workspace, SHA, audit ZIP, no repeated T1
- **Prior evidence:** [실 T1 #42170351404](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42170351404) 70783 SEALED/COMPILED, Native 8회 보고, F next batch PENDING, READY/installed false. [Artifact 13480598417](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42170351404/artifacts/13480598417)는 요약 JSON 한 파일뿐. 원래 `v278.run_case`/ `v277.collect`의 SHA 검증된 Native 폴더는 T1 `TemporaryDirectory` 종료로 삭제됨.
- **Decision:** `CONNECT` 기존 Native 증거를 *다음 실행 시 감사 가능하도록* 제한적 보존. 구시즌 수치나 실측 캐시를 제로베이스 T1 입력으로 주입하지 않는다. 이 ZIP은 절대경로가 들어 있는 원래 v278 input 때문에 **직접 이식 가능한 cache가 아님**. 제품 READY·효과 인증·추가 Native 엔진이 아니다.
- **Changes:** `integration_probes/p3_fr_zero_base_t1_acceptance.py` 종료 전 이미 존재하는 v277/v278 input/JSON2/log/receipt만 SHA·크기·파일 수 상한으로 묶어 inventory와 보존. 원래 업무·실패 상태를 변경하지 않음. P3-FZ T1 workflow는 `workflow_dispatch` 전용으로 바꾸어 변경 push만으로 다시 실 Native 8회가 실행되지 않게 하고, 추후 명시적 T1 시 요약+감사 ZIP을 7일 저장. `offline_focused_continuity`에는 기존 계약 회귀 4건 추가.
- **Verification:** 이번 수정은 새 실 T1/Native/HTTP 결과를 만들지 않는다. 새 focused CI 영수증 확인 전 `NOT_VERIFIED`. 과거 focused #42170351351 323 PASS/2 SKIP 및 실제 T1 실패는 변경 전 범위 증거로 보존.
- **Remaining:** 기존 8회 개별 수치는 앞선 Artifact에서 복구 불가. 새 측정 전 별도 영속 cache/영수증 선조회. 감사 ZIP 자동 import는 구현하지 않았으므로 재개 가능한 영속 v217 stage로 전환할 때 원래 v277/v278 identity와 입력 absolute-path/원본 SHA를 독립 확인해야 한다. 기본 F 후보·J 보석·O 무기·G/B/T source-owner 및 실 READY 미완료.
- **Efficiency:** export는 기존 파일만 1회 읽고 최대 16 case·64MB로 제한; 신규 Native/HTTP 0, 기존 cache/in-place stage 변경 0. 무조건 full T1 재실행 차단. 단일 엔진의 다음 시즌 실증을 재수집 없이 진단 가능하게 만드는 최소 보존 연결.
