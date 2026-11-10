# 제품·기술 결정 지도 — 현재와 철회된 역사 구분

> 현재 사용자 직접 결정 > [승인 v1.4.3](../SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) > 실제 코드·Native/Actions > 과거 노트. 이 표는 승인 정책의 대체 원본이 아니다.

| 결정 | 현재 적용 | 개발 이유·관련 자료 |
|---|---|---|
| 제품 범위 | 26 DPS, 목표 ilvl/수동 최종 T에서 CHMV **절대 rating** SimC DPS 최대화 | [설계 승인](../SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md); 장비 조합 추천/현재 장비 재배분은 범위 밖 |
| 공식 회계 | G/J/F/O 매 시즌 소스; B=G+J+F, T=B+O; 수동 T 우선·L/E/O 이중 가산 금지 | 기존 다른 시즌 79×2·J/F 숫자 복사 금지 |
| 보석 | 일반 치·가·특·유 각1, 특수보석 **선택** | 과거 `특수1+일반N 필수`·독립 효과 인증은 역사/철회. [일반4 소스](notes/2026-11-10_p1-ordinary-only-default-engine-bridge.md) |
| SimC 책임 | proc·APL·효과·DPS는 SimC가 실행; 독립 메커니즘 인증 Gate 금지 | [승인 v1.4.3](../SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) |
| 환경 검증 | 이미 현 70783 무이력 Build READY/프로필 PASS, 같은 조건 불필요한 재검증 금지 | [실 Native3](notes/2026-11-10_p1-four-ordinary-real-zero-history-ready.md). 다른 시즌·4보석 실 DPS는 미검증이지 곧바로 결함이 아님 |
| P2 알고리즘 | v290/v291은 **교체 가능한 현재 구현**. 신규 세션 최종 T 개별 상한 기본 60% 이하·사용자 지정; legacy <50% 세션 보존. 승인된 다음 비교 설계: 각 자유 B 축의 적응형 백분율 기준점(초기 11개, SimC 처리량에 따라 가변)→가장 큰 격자 합계 shell→비례 확대→상한/하한 bounded 재배분→정수 총량 보정·중복 제거. 여러 유망/미탐색 영역을 함께 정밀화. 구현·DPS 우위는 미입증. 특정 최종 rating 고정은 향후 확장 후보, 미구현 | [적응형 격자·비례 정규화 설계](notes/2026-11-10_p2-percentage-grid-proportional-normalization.md), [상한 정책](notes/2026-11-10_p2-user-configurable-final-stat-cap-and-grid-study.md), [경계 적응 변경](notes/2026-11-10_p2-fractional-bounded-neighbor-proposals.md), [비고정 신뢰성 원칙](notes/2026-11-09_p2-opt-reliability-first-open-search-policy.md), [Native10 감사](notes/2026-11-09_p2-real-native-ten-case-region-audit.md) |
| 정책 A | 정확 ID·품질·사용 조건·SimC 입력·CHMV 소유권 입증 시 자동 등록, 부족한 선택지만 보류 | [승인 v1.4.3](../SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) |
| 개발 지식 구조 | 현재 INDEX는 간단하게, 파일·영수증·결정은 각각 한 지도, 이전 배너는 역사 원문 | [기존 INDEX 전체](HISTORICAL_INDEX_20261110_PRE_KNOWLEDGE_LAYER.md); 중복/삭제 없이 검색성 개선 |
