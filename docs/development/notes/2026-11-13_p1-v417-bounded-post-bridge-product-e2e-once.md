# v417 — P1 최신 v414/v415 변경 후 실제 사용자 SimC 종단 단발 시험

- **Capability:** `PRODUCT.E2E`
- **Keywords:** P1, v414, v415, same-season installed, v113, v096, v293, GJFO, Native, result snapshot, 95%, one-shot
- **Prior evidence:** [v414 특수장비 L 및 설치 session](2026-11-13_p1-v414-fresh-special-l-catalog-and-session-sha-bridge.md), [v415 정확 v212 DPS source](2026-11-13_p1-v415-v096-exact-installed-variant-dps-source.md), 이전 실제 [v344 Windows](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208)와 [v343 Windows](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43046174810)
- **Decision:** `REUSE` 검증된 동일 시즌 Windows 공식 SimC artifact와 기존 `p1_v343_windows_70783_real_native_once.py` 실행 경로. v414/v415 이후 새 제품 코드로 **단 한 번**, 대표 전문화 1개/기본 O0/일반 4보석의 새 시즌 환경부터 저장 결과까지 확인. 새 Gate/알고리즘/전수 반복 금지
- **Changes:** 구 프로브를 수정하지 않고 단발 workflow `p1_v417_post_bridge_actual_e2e_once.yml`만 추가. 결과는 기존 `V343_...` 이름이지만 v417 run SHA/영수증 별도 기록. 사전 `v096/v113` offline 전체 브리지 회귀를 실행. 재실행 조건은 commit message 명시 마커로 제한
- **Verification:** 첫 [v417 Windows #43393206562](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43393206562)는 SimC 바이너리 다운로드·정확 SHA 전처리 PASS, `tests.test_p3_ho_fresh_v212_user_bridge`의 **Windows 8.3 Temp 경로 표기 차이**로 28개 중 1개 오프라인 테스트만 FAIL, 실제 Native0. 테스트는 `root.resolve()`로 제품 v096과 동일한 경로를 비교하도록 수정. **재시도 실제 E2E PENDING**. 이후 한정 환경 Native 최대3 + DPS Native12. test-specific SHA/70783은 제품 빌드 일치 인증 Gate가 아님
- **Verification continuation:** [두 번째 v417 #43393505225](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43393505225)에서 Windows 사전검사 28 PASS, 실제 시즌 원본 컴파일·설치 단계까지 진행, `HTTP_422_/api/v1/longrun/start_WEB_PRIMARY_VERIFIED_SEASON_INSTALL_REQUIRED`로 DPS 시작 이전 차단. 재사용 중인 구 `p3_haj` 시험 스크립트가 명시적 기본 장기탐색에 설치 시즌 빌드를 안 보냈기 때문. 제품의 v212 verified-only 규칙은 정상, 임의 해제 금지. `primary_continuous` 시험에만 `installed_season_game_build` 및 실제 선택 `user_socket_total` 전달. 마지막 시험에서 성공/실패를 분리해 판정.
- **Remaining:** 이 시험 PASS도 특수장비 L 실제 Native 선택, 모든 전문화/시즌/옵션 완료나 전역 최적 증명이 아님. P1 기본 입력→환경→대표 프로필→SimC→95% 스냅샷 완료 근거만 수집하고, 이후 78요소 미완료 항목으로 복귀
- **Efficiency:** 기존 원본 artifact·스크립트·Native 코드·캐시 정책 재사용. 조건부 one-shot, 신규 SimC 다운로드 외 엔진 재빌드0, Native 총15 이내, 스냅샷 중복 저장 엔진0

**권한:** 격리 브랜치만. main/불변 v003/Project UI/공식 승격·주 제품 채팅 역할 불변.
