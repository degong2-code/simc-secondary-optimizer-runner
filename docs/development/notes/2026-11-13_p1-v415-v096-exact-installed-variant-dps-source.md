# v415 — P1 v096 DPS 실행 직전 정확 v212 설치 SHA 전달

- **Capability:** `PRODUCT.E2E`
- **Keywords:** P1, v096, v212, v216, DPS, installed SHA, same-oil variant, JFO, snapshot, cache, no Native
- **Prior evidence:** [v414 user/session SHA and special L fix](2026-11-13_p1-v414-fresh-special-l-catalog-and-session-sha-bridge.md); [v413 exact SHA finder](2026-11-13_p1-v413-verified-install-variant-limit-removal.md)
- **Decision:** `CONNECT` 사용자 v096 최종 후보 계획에 이미 존재하는 설치 manifest SHA를 원래 v216 verified finder에 전달. 새로운 인증 단계 추가 안 함
- **Changes:** `_admitted_fresh_season_source`의 기존 `find_verified_installed_season_environment` 호출에 `expected_installed_manifest_sha256=doc["manifest_sha256"]` 추가. 같은 기름을 사용하지만 F/보석이 다른 설치본 선택/거부를 방지. 이미 있는 v217·v212 원본/예산 검증 유지. 기존 v096 테스트는 실제 전달 인수를 단언하도록 갱신
- **Verification:** [v415 집중 #43391249207](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43391249207) **7 PASS / 0 FAIL**; [v098 Target User Scenario #43391249073](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43391249073) **382 PASS / 0 FAIL**; [v113 Web API Linux/Windows #43391249405](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43391249405) 각 **331 PASS / 1 SKIP / 0 FAIL**; [78-element contract #43391249190](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43391249190) SUCCESS. 실제 새 SimC Native0. 원본 역사 v342/v344 및 기존 사용자 실제 E2E는 재실행 아님
- **Remaining:** 이전 시즌 G/J/F/O 수치 재사용/영구 엔진 변경 없음. 신규 실제 사용자 특수 L 포함 SimC DPS 완주 확인은 별도 실증 필요
- **Efficiency:** 이미 알고 있는 설치 SHA로 v216의 단일 설치 파일 조회. 중복 스캔과 다른 F/보석 구성으로의 잘못된 재시도 방지; Native/HTTP/DB2 호출 추가0

기존 사용자 정책대로 실행 환경의 SHA/버전은 캐시 식별에 쓰고, SimC 빌드와 게임 빌드 동등성·컴파일 계보 증명 Gate는 도입하지 않는다.
