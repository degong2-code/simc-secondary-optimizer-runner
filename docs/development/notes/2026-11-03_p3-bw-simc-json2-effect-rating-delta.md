# 2026-11-03 · P3-BW · SimC JSON2 실제 정적 CHMV 차이 재사용

- **Capability:** `F.FLASK`, `O.OIL`, `J.GEM`, `BUDGET.GJFO`, `PRODUCT.E2E`
- **Keywords:** SimC, JSON2, buffed_stats, snapshot_stats, flask, oil, temporary_enchant, food, J/F/O/E, native delta, 정적 rating
- **Prior evidence:** [P3-BV](2026-11-03_p3-bv-gem-enchant-source-once.md) v266의 DB2 effect-point는 실제 SimC rating과 구별; [P3-BG](../../P3_BG_20261103_PREPROFILE_GJFO_ACCOUNTING_BRIDGE.md) v222 단일 회계; 기존 v091은 특정 **이전 시즌**의 16/16 oil 고정값이므로 신규 시즌 수치로 재사용 불가. SimC `engine/report/json/report_json.cpp`에서 `sim.players[].collected_data.buffed_stats.stats.{crit,haste,mastery,versatility}_rating` 직출력, `engine/player/consumable.cpp` DBC 기반 flask/food, `snapshot_stats` precombat 순서 확인.
- **Decision:** `CONNECT` — 별도 효과 계산·DB2 숫자 해석 엔진 대신 기존 SimC가 이미 처리한 원본 JSON2 2개(기본 disabled/단일 최고 품질 옵션 활성)를 동일 binary/profile/전투조건으로 비교해 정적 CHMV **관측 델타**만 남긴다. 플라스크·음식·기름의 확정된 옵션/적용 조건별로만 측정; 보석·영구 마부는 실제 장비 슬롯/ID 편집 규칙이 확정되기 전 일괄 측정 금지. snapshot 수치만으로 발동/유지효과나 실제 J/F/O 회계 소유권을 증명하지 않고 기존 v222에 연계한다.
- **Changes:** 경량 JSON2 실제 rating-delta 어댑터와 선택형 로컬 두 프로필 시험 경로, source/binary/옵션 identity·결과 비교 회귀, 기존 환경 Build와 결과 연결 경로 점검. 계정 토큰/Native 전수 수집/새 효과 Gate 없음.
- **Verification:** 현재까지 새 SimC Native 0·외부 게임 HTTP0. 가능한 focused 표준라이브러리 테스트는 **실제 실행 결과**로 별도 기록 예정; GitHub CI PASS는 검증 전까지 `NOT_VERIFIED`. 과거 원본/P3-BV 코드는 `REUSED_HISTORY`.
- **Remaining:** 실제 동일 바이너리/빌드의 flask·oil·food 옵션별 짧은 Native 결과 수집 및 회계 결합, Gem 슬롯 변경/최고 품질 선택과 실제 J, 기존 시즌 고정유값 미복사, v216 환경/Policy A·26DPS E2E. 런타임 부재 시 실제 수치를 추측하지 않는다.
- **Efficiency:** 각 옵션 baseline/control 비교 소량 실행(옵션별 필요할 때만)·동일 baseline 재사용/코드 경량화; 기존 v234/v046 G와 v222 B/T 재사용, 외부 데이터 전체 재다운로드/26x79 Native 루프 없음. 캐시 identity 정확히 고정, 추가 시간·I/O는 실측 후 기록.
