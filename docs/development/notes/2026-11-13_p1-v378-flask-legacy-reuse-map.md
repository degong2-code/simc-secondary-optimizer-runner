# v378 — 기존 F.FLASK·티어 연구로 곧장 이동하는 검색 지도 보수

- **Capability:** `DEV.CONTINUITY`, `F.FLASK`, `TIER.SEASON`, `PRODUCT.E2E`.
- **Keywords:** v378, previous research first, knowledge map, INDEX, flask, static gear zero, F floor, per-user variant, 5 tier.
- **Prior evidence:** 2026-11-13 현재 개발 노트 287개, `START_HERE` 단일 인계 v365, `CURRENT_PRODUCT_DEVELOPMENT_STATE` 장문, INDEX F.FLASK의 이전 v3-EZ 한정 참조. 이미 있던 P3-GL은 SimC `gear_*=0`과 최고품질 측정 선택; P3-GN은 대표 F 1종 자동 선택; P3-GP는 70783 ItemID241324의 가속165 Native2/영수증; v350은 개인별 F 선택/설치 변형; v065/v124는 F 하한. v101/v098/v187은 5티어 원본 중 유동4pc 구성.
- **Decision:** `REUSE/CONNECT`. 새 F 탐색 알고리즘·Native·원본 수집/인증 Gate를 연구하기 전에 기존 코드·정확 영수증을 먼저 확인. 대표 영약은 기존 기본값으로 빠른 경로를 제공하지만, v134는 미지원 원본을 crit reference로 대체할 수 있고 v139는 시즌 공통 F 사용 — **전문화별 최적/필수 스탯 인증은 아님**. 향후 F 변경은 별도 선택 프로필과 cache identity·필요시 원래 v290 적응형 SimC 경로로 비교; 자동 4종 전수 Native 기본화 금지.
- **Changes:** 기존 `INDEX.md`의 항목별 과거 증거 진입표 및 `F.FLASK` capability 직접 링크 보강; `FILE_MAP.md`에 v127/v134/v139 원본 기본 F→v065 하한→v098 개인 선택 연결 표시; `START_HERE.md`에서 최신 단일 인계 v365와 그 이후 코드 증분 구분. 과거 자료 삭제·원문 재분석/복제 없음. 지금 변경은 **탐색 개선만**, 런타임 F 정책 변경 아님.
- **Verification:** 격리 GitHub 실제 HEAD의 관련 소스와 P3-GL/GN/GP/v350/v187 역사 기록을 정적 열람하여 링크·범위 확인. 신규 코드 unittest/Actions/실 Native/게임 API/DB2 0; 과거 P3-GP F165 실 Native는 **재사용 역사 증거**이지 신규 실증 아님.
- **Remaining:** 단일 시나리오 기본 영약과 선택형 여러 F 시나리오의 DPS·통계/시간 트레이드오프는 실제 동등 조건에서 미비교. 현재 70783 새 환경 전체 G/J/F/O/READY는 계속 별도 PENDING. INDEX의 날짜별 축적은 향후 별도 축약 필요; 새 노트를 매번 INDEX 상단에 쌓지 않고 capability별 정본 링크만 갱신.
- **Efficiency:** 과거 P3-GP Native2·기존 캐시 재사용, 신규 원본/SimC 요청 0. 문서 탐색 3개 파일만 국소 수정, main·불변자료·Project UI·공식 승격/주 개발 소유권 불변.
