# 2026-11-05 · P3-EZ · 일반 보석 명목 J와 기존 SimC F 수치 재사용

- **Capability:** J.GEM, F.FLASK, BUDGET.GJFO, ENVIRONMENT.WEB
- **Keywords:** P3-EZ, J, ordinary gem, special gem, F, SimC numeric, v216, v269, v278, v281
- **Prior evidence:** [INDEX C1/C4/D1/E3](../INDEX.md), [P3-EP](2026-11-05_p3-ep-special-gem-raw-static-j-ownership.md), [P3-EY](2026-11-05_p3-ey-j-intrinsic-socket-source-join.md). 사용자 최신 직접 결정: 최고품질 일반 다중스탯 보석의 명목 rating 합만 J에 포함. 특수 1개는 실제 프로필의 효과만 SimC 담당. F는 기존 SimC 관측 수치만 사용하며 별도 효과 기전 인증 불필요. [기존 Native F 실험](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666305288)은 과거 해당 프로필 한정이며 숫자는 사용자 재검토 대상으로 남김.
- **Decision:** CONNECT — 기존 v271 일반 보석 합계와 v281/v269/v278 F 정적 델타 원본/캐시를 normal v216 Build에 연결. 새로운 효과 인증 Gate와 측정기, 수치 하드코딩은 STOP.
- **Changes:** v216 특수 보석 raw 양수 때문에 일반 J 합계를 막던 오류 조건 삭제, 명목 J scope 추가; 원래 raw 진단/특수1 프로필 유지. 기존 F selected SimC numeric vector 합·정확 품질·입력 토큰·원본 item 후보 SHA·Native receipt를 source-only 예산 연결로 제공. 잘못된 합 차단. v222 B/T·수동 T·캐시/취소·재개·실제 DPS 유지.
- **Verification:** 합성 focused 테스트 2개와 기존 기대값 교정; 신규 CI는 실제 Actions 결과 우선(작성 시 NOT_VERIFIED). 과거 [P3-EY focused #42006498728](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42006498728) 258 PASS/0 FAIL은 이전 코드 범위. 신규 Native/HTTP 0.
- **Remaining:** 최고품질 일반 보석 개별 명목 rating/실제 소켓·선택 ID source, F 최고품질 실제 ItemID와 해당 프로필/게임 빌드 SimC numeric source-owner 인증, Policy A 4-family, 새시즌 READY/T1. 특수 raw CHMV는 실제 최종 static rating 검산에 SimC가 관여하지만 J 예산을 추가하지 않음. 과거 영약 151 및 Phoenix Oil 16/17 관측은 의심/재조사 후순위로 공식 수치에 사용하지 않음.
- **Efficiency:** v266/v268/v271·v281/v269/v278·v222/v217 그대로 재사용, 신규 측정기/HTTP/Native/대형 DB/CSV 반복0. 입력 소규모 딕셔너리 1회. main/원본/Project UI/Work OS/주 개발권한 불변.
