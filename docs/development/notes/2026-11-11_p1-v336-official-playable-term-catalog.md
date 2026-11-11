# v336 — 직업·전문화·종족 공식 한국어 용어 Environment Build 자동 구축
- **Capability:** `ENVIRONMENT.WEB`, `CHARACTER.PROFILE`, `DEV.CONTINUITY`.
- **Keywords:** v336, playable class, specialization, race, Blizzard static-kr, English Korean ID join, source-first.
- **Prior evidence:** [v335 아이템명 자동 구축](2026-11-11_p1-v335-environment-ko-auto-localization.md), [공식 API spec index·소속 직업 구조](https://us.forums.blizzard.com/en/blizzard/t/playable-specialization-api-brewmaster-returns-404/50406), [v333 실 Chrome](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42983424219).
- **Decision:** `CONNECT` — 아이템명과 별도로 직업13/지원 DPS26/기존 SimC 종족25를 공식 Blizzard static-kr en_US/ko_KR index 양쪽의 정확한 ID로 조인. 전문화 중복명(예: 냉기)은 개별 spec detail의 `playable_class.id`가 일치할 때만 승인; 동일 영어 종족명이 여러 ID라면 KO도 동일할 때만. 새 직업/전문화/종족 지원 범위 확대하지 않음.
- **Changes:** v336 source-first 자동 수집 모듈 6개 index + 해당 전문화 detail 최대100건(실제 타겟26)·요청당 동시4 제한, 응답 digest/roster SHA/설치 빌드별 원자 캐시, 변조·빌드·범위 불일치 안전 처리. v216 VERIFIED READY 및 v113 이전 설치 재사용 경로에 연결. 조회는 웹/서버에서 읽기 전용; 프런트의 검색 옵션명/종족 제안만 교체하고 SimC 토큰은 원형 유지. 불확정은 기존 이름으로 표시. `dracthyr_visage`처럼 API 별도 ID가 없는 SimC 별칭을 별도 공식 종족으로 인증하지 않음.
- **Verification:** 신규 v336 모의 공식 응답 기반 소스 전용 테스트 7개, 기존 웹 API/HTML 및 Windows ZIP CI 추가. HEAD 결과 확인 전 PASS 아님; 실제 공식 API one-time source 증거는 별도 워크플로 검증. v335 실 Native 새 호출0.
- **Remaining:** Blizzard 현재 static-kr 인덱스는 버전에 고정한 네임스페이스가 아니므로 여기서 얻은 공식명은 요청 `game_build`에 귀속하는 캐시 스코프이지 그 게임 빌드 API 콘텐츠 전체 인증은 아님. 향후 새 시즌 실제 원본 수집 결과 대사 및 종족별 SimC 적용 가능성 검증은 원래 엔진 소유. 미지원 증강/탱크/힐러는 여전히 제외.
- **Efficiency:** 같은 지원 로스터·시즌 구축 빌드 캐시 재사용 시 외부 요청0, 새로운 환경에서 최초 6 index + 해당 전문화 소속 확인 detail만. Native0, 기존 G/J/F/O·SimC DPS identity 변경0.
