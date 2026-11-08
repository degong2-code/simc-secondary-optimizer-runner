# P3-HS · 다른 전문화 zero-base G/J/F/O → 기존 DPS 엔진 1회 검증 (2026-11-08)

- **Capability:** `PRODUCT.E2E`, `CHARACTER.PROFILE`, `ENVIRONMENT.WEB`, `G.NUMERIC`
- **Keywords:** P3-HS, zero-base, enhancement shaman, dual_one_hand, Native G, GJFO, exact build, DPS E2E
- **Prior evidence:** [P3-HR 한 조건 실 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42466284163)은 징벌 성기사 334·70783·Native 3+6회 한정. v216/v212/v217 설치·v098/v096/v094 적응형 루트 재사용, 새 전문화 실 G는 별도 확인 필요.
- **Decision:** `CONNECT` — 공통 zero-history T1 시험 입력만 다른 DPS class/spec/race로 연결, 고양 주술사(`shaman/enhancement`, dwarf, dual_one_hand)에서 새 원본 구축→설치→사용자 DPS 1회 실행. 전문화별 효과 엔진·새 스탯 알고리즘 없음.
- **Changes:** 기존 T1 probe의 징벌 고정 입력을 v143 전문화 계약으로 일반화(기본 징벌 유지), 원래 v216/v098/v096/v094 경로·바이너리 그대로 사용. P3-FZ workflow에 다른 전문화 요청 marker·exact request allowlist 추가, 커밋 파일 단독 검사 유지. 기본/새 전문화·지원 밖 경계 오프라인 회귀 추가.
- **Verification:** 코드/워크플로 초안 단계. OFFLINE CI PENDING. 실제 고양 주술사 Native/READY/DPS **NOT_RUN**, 결과·예산 **미확정**. 기존 P3-HR 한 전문화 실 PASS는 이번 성공 증거가 아님.
- **Remaining:** 오프라인 CI 후 다른 전문화 요청 JSON 단독 커밋으로 1회 실제 Native G1/F2/O0, 사용자 DPS 최대6 실행. 신규 대표 프로필/예산/READY/SEM/95%·1순위 영수증을 확인. 실패는 최초 기존 owner만 원인 분석; 전수 Native 금지.
- **Efficiency:** 새 source collector/SimC 컴파일/최적화 엔진 0, 정확 binary SHA 재사용. 빈 임시 작업공간으로 새 전문화 G Native(이전 사용자 프로필/캐시 미주입), 26×N 무차별 실행·새 효과 인증 없음.
