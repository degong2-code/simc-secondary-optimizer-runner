# v417 — P1 최신 v414/v415 변경 후 실제 사용자 SimC 종단 단발 시험

- **Capability:** `PRODUCT.E2E`
- **Keywords:** P1, v414, v415, same-season installed, v113, v096, v293, GJFO, Native, result snapshot, 95%, one-shot
- **Prior evidence:** [v414 특수장비 L 및 설치 session](2026-11-13_p1-v414-fresh-special-l-catalog-and-session-sha-bridge.md), [v415 정확 v212 DPS source](2026-11-13_p1-v415-v096-exact-installed-variant-dps-source.md), 이전 실제 [v344 Windows](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208)와 [v343 Windows](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43046174810)
- **Decision:** `REUSE` 검증된 동일 시즌 Windows 공식 SimC artifact와 기존 `p1_v343_windows_70783_real_native_once.py` 실행 경로. v414/v415 이후 새 제품 코드로 **단 한 번**, 대표 전문화 1개/기본 O0/일반 4보석의 새 시즌 환경부터 저장 결과까지 확인. 새 Gate/알고리즘/전수 반복 금지
- **Changes:** 구 프로브를 수정하지 않고 단발 workflow `p1_v417_post_bridge_actual_e2e_once.yml`만 추가. 결과는 기존 `V343_...` 이름이지만 v417 run SHA/영수증 별도 기록. 사전 `v096/v113` offline 전체 브리지 회귀를 실행. 재실행 조건은 commit message 명시 마커로 제한
- **Verification:** 신규 workflow 실행 결과/로그/영수증을 확인하기 전 실제 E2E **PENDING**. 최대 신규 환경 Native3 + DPS Native12, 별도 v344 64-case 반복 없음. 시험에 사용하는 정확 바이너리 SHA/70783은 단발 시험 fixture 정체성일 뿐 제품의 게임 빌드 일치 인증 Gate가 아님
- **Remaining:** 이 시험 PASS도 특수장비 L 실제 Native 선택, 모든 전문화/시즌/옵션 완료나 전역 최적 증명이 아님. P1 기본 입력→환경→대표 프로필→SimC→95% 스냅샷 완료 근거만 수집하고, 이후 78요소 미완료 항목으로 복귀
- **Efficiency:** 기존 원본 artifact·스크립트·Native 코드·캐시 정책 재사용. 조건부 one-shot, 신규 SimC 다운로드 외 엔진 재빌드0, Native 총15 이내, 스냅샷 중복 저장 엔진0

**권한:** 격리 브랜치만. main/불변 v003/Project UI/공식 승격·주 제품 채팅 역할 불변.
