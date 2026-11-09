# P1 · 하나의 최초 시즌 Build에 기존 G/F 연결 (2026-11-10)
- **Capability:** `BUDGET.GJFO`, `ENVIRONMENT.WEB`, `PRODUCT.E2E`.
- **Keywords:** cold-start, first Build, existing v216, source owner, G native, F native, bounded, reuse, GUI.
- **Prior evidence:** [P3-HAV 원본](../../CHAT_CONTINUITY_HANDOFF_20261109_P3_HAV_ENGINE_FIRST_RESTORE.md), 기존 v216 `auto_native_G_requested`/`auto_native_F_requested`/`auto_select_observed_F_no_oil`와 v222/v212 봉인 설치 경로, [직전 source 연결](2026-11-10_p1-cold-start-four-stat-source-default.md), 과거 실 70783 O0/O>0 영수증 재사용.
- **Decision:** `CONNECT` — 처음부터 별도 엔진을 만들지 않고 사용자 Build가 기존 v216 원본과 측정·등록 경로를 사용. 기존 동일 빌드·ilvl의 검증 설치는 우선 0 Native로 재사용.
- **Changes:** v113 API 자동 최초 기본 Build 선택 및 캐시 미스 때에만 로컬 SimC로 bounded G·F 실행 요청; webui 기본 선택·고급 설정 우선권·Native 비용 확인; v113/v114 기초 회귀 및 CURRENT/INDEX 연결.
- **Verification:** 이번 변경의 새로운 CI 및 실 Native/새 시즌 원본 수집은 Actions 결과 확인 전 `NOT_RUN`. 과거 522 PASS/2 SKIP는 이전 HEAD, 실 70783 정적 G/F 및 O>0 웹 DPS는 별도 범위 증거.
- **Remaining:** 특수보석 ID 없는 일반 J 배치·인증과 완전 신규 시즌 G/J/F/O 최초 설치는 미완료. 정책 A 선택지·26 DPS 사용자 장기 웹 Native·실 Windows 개인 PC 클릭과 전역 최적성은 별개. 미인증 상태에서 READY 선언 금지.
- **Efficiency:** 이미 봉인한 시즌 설치는 원본·Native 신규 0; 신규 시즌만 기존 G 최대 1회와 대표 F 품질 후보 Native paired 최대 2회, v217/v278 캐시 사용. 개발용 추가 품질/효과 Gate·별도 optimizer 불필요. 기존 DPS 캐시·중단/재개 SHA 정체성 변경 없음.
