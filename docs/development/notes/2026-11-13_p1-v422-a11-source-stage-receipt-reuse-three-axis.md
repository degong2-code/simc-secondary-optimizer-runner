# v422 — A11 원본 영수증·봉인·재개: 기존 실증과 범용 테스트 재사용

- **Capability:** `SOURCE.SEAL`, `ENVIRONMENT.WEB`, `PRODUCT.E2E`.
- **Keywords:** A11, v217, v212, v216, SHA, receipt, input fingerprint, original source, reuse, interrupted resume, Windows, JSON2.
- **Prior evidence:** [v383 역사 원본 ZIP·설치 SHA](2026-11-13_p1-v383-a10-a11-g2-archived-native-receipt-reuse.md), [v417 실 Windows](2026-11-13_p1-v417-bounded-post-bridge-product-e2e-once.md), [v419 A8 결과 저장](2026-11-13_p1-v419-a8-runtime-sha-cache-snapshot-evidence.md), [v421 A10 컴파일](2026-11-13_p1-v421-a10-source-compiler-reuse-three-axis-evidence.md).
- **Decision:** `REUSE` — 수락 범위 A11의 source/build/SHA/봉인·재개/실제 소비 영수증 연결 완료. 각 stage 구현을 다시 만들거나 원본·Native를 재수집하지 않는다.
- **Changes:** 78 JSON의 A11 세 필수 축 PASS 및 다음 B1, 자동 생성 상태표/상세 추적표/회귀 테스트/상태 인덱스만 갱신; 제품 코드 변경 없음.
- **Verification:** [v113 Linux/Windows #43391249405](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43391249405) 각331 PASS/1 SKIP, [v409 v275 소스 #43386905854](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43386905854) 60 PASS, [v344 실 Windows #43114134208](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208), [v417 실 제품 #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756).
- **Remaining:** B1 26 DPS 계약부터 순차 검토. 새 시즌/선택적 변형의 실제 원본·환경/스탯·전체 USER-E2E는 별도, A1~A7 제품 통합 PENDING.
- **Efficiency:** 신규 Native0, HTTP/DB2/SimC 소스 수집0, 캐시/스냅샷 재생성0, 기존 코드와 4개 성공 Actions 영수증 재사용.

## 1. 코드·범용 회귀

기존 `runner/v217_stage_execution_engine.py`의 `_seal/_read_receipt`는 stage receipt payload SHA-256을 검사한다. `_input_sha/_check_identity`는 stage ID/version/입력 fingerprint·출력 경로 계약을 봉인하고, `_snapshot/_verify_outputs`는 실제 출력 바이트 SHA-256과 크기를 검증한다. `execute_stage`는 `EXECUTED_AND_SEALED`, `REUSED_VERIFIED`, 중단 후 `RECOVERED_VERIFIED`를 구분하며 손상/다른 입력은 재사용하지 않는다. `runner/v212_environment_manifest.py::compile_fresh_source_environment`는 `v191/v211/v213` 각 stage의 `receipt_sha256`, source catalog manifest, 빌드·SimC revision, preflight SHA를 연결하며 설치 READY와 단순 source-only를 구분한다.

**GENERALIZATION_REGRESSION:** [#43391249405](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43391249405), tested `5732defbeba44db51427e7c1172724365ccca298`, Linux/Windows 각각 331 PASS/1 SKIP. 기존 `tests/test_v217_stage_execution_engine.py`에 최초 봉인→동일 요청 무실행 재사용, 출력 변조/입력 fingerprint 변경 차단, 완성된 중단 출력 복구/부분 출력 한정 재실행, 경로 충돌·변조 방지가 포함된다. [#43386905854](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43386905854), tested `94150580bbc4745c25c559db2f185d20de009e6d`, v275 pinned Git blob/원본 누락·변조·변경 소스 회귀도 재사용한다. 변형 검사는 합성 입력이며 미출시 시즌 실제 증거는 아니다.

## 2. 현재 원본·제품 통합

**CURRENT_SOURCE_REAL / PRODUCT_INTEGRATION_REAL:** [v417 #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756), tested `89d4810baf5e05f1c5c6f355f39a5f35ca9ec4e7`. 실제 KR Retail 12.1.5.70783 / pinned SimC source `de11f57df75dda668bae6ac7043a43b98831fa96`에서 소스→v191/v211/v213 컴파일→v212 검증 설치→사용자 Survival Hunter ilvl334/일반4/O0→환경 Native3/DPS Native12→기존 결과 스냅샷 조회까지 성공했다. 설치된 v212 source receipt 소비는 코드상 세 stage SHA·빌드/revision 검증을 요구한다. 관측된 G2850/J92/F165/O0/B=T3107, DPS178334.8563/SEM298.6111/CHMV373·1078·1491·165은 이 한 요청의 범위이다.

**역사 원본 직접 재확인:** [v383](2026-11-13_p1-v383-a10-a11-g2-archived-native-receipt-reuse.md)이 [v344 실 Chrome #43114134208](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208) artifact 내부 ZIP SHA와 `EXECUTED_AND_SEALED`, 실제 v212 설치 manifest SHA `278d3c52d4c9c272d8d2c89d7b02cff4abe05db1639bde80b58b14d99f4f4294` 및 취소·서버 재시작·재개를 확인했다. 별개 [v343](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43049564271)의 설치 manifest SHA는 `5d655836c6f69382a1ca81d72346fa5d71dc78eb2ae029843b49dea532693a02`로 **다른 요청**이다. [v337 #43000049793](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43000049793)은 동일 root Native/API0 재사용의 역사 증거다. 각 stage 개별 원본 ZIP 바이트를 이번 작업에서 새로 전수 열거나 26개 전문화 전체 재시험한 것은 아니다.

## 3. 판정 및 제한

- **A11 generic/current_source/product_integration PASS**, 기존 historical PASS 유지, 요소 COMPLETE. 실제 현재 원본·기능 회귀·실 사용자 제품 소비를 각 축에 별도 기록한다.
- A11에서 증명된 것은 관측 요청/실행 범위 내 **원본 영수증의 봉인과 소비·복구 경로**다. 모든 시즌·사용자 선택의 실제 READY, A1~A7 제품 통합, 별도 최종 `ZERO-SOURCE→USER-E2E` 완료가 아니다.
- 기존 범용 오프라인 developer-ledger의 198개 역사 노트 오류는 선행 CI에서 이미 존재하고 A11 새 기능 결손이 아니다. 수집기·캐시·컴파일러·SimC 인증 Gate 새 개발 금지.
