# SIMC SECONDARY OPTIMIZER — 제품 우선·최소 충분 검증 상시 인계

> **2026-11-14 최신 사용자 직접 결정의 인계 진입점.** 정책 정본은 [제품 우선·최소 충분 검증](development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md)이다. 이 인계는 과거 v445 인계의 날짜별 상태와 독립이며, 실제 개발 HEAD/78요소 증거를 덮어쓰지 않는다.
>
> **새 채팅 필수 동작:** 이 정책 → [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) → [START_HERE](development/START_HERE.md) → [78개 기계 정본](development/78_ELEMENT_COMPLETION_CONTRACTS.json) → GitHub 브랜치 HEAD/Actions/Native 영수증 순으로 확인한다. 사용자가 읽기 전용 복원을 요청했다면 확인 후 **STOP**; 명시적 `진행` 전에 코드·문서·시험 실행 금지.

## 제품 목표와 절대 보존 범위

- **26개 DPS만 지원**, 목표 ilvl 기본334 또는 사용자 지정 최종 CHMV T를 기준으로 **치명·가속·특화·유연 최적 절대 rating**을 기존 SimC DPS로 찾는다. 비율/DPS·SEM/95% 판정·관측 1순위·실질적 근접 대안 제공. 전역 최적 증명 금지.
- 사용자는 전문화/종족/특성·목표 ilvl/T·장신구2·선택 특수/제작 장비·장식 최대2·보석/영약/기름/소모품·전투조건만 입력. 일반 장비·무기·티어4pc·주능력치·원본 SimC 프로필은 내부 대표 구성. 현재 착용 장비 재분배·전체 DB·아이템 조합 추천은 범위 밖.
- 새 시즌 **G/J/F/O 자동 구축**, `B=G+J+F; T=B+O; c_final=c_base+o`; 수동 T 우선, 정확 L/E/O 소유권/중복 방지, 옵션별 정확한 정적 rating 검증. SimC가 아이템 효과·proc·APL·DPS 소유. 별도 효과 해석/발동 인증기 불필요.
- 그대로 유지: 기존 v216/v217/v212 환경 원본, v098/v096/v094 USER→적응형 SimC, 95% 판정, 캐시·취소·재개, 동일 시즌 정적 캐시 재사용. 새로운 알고리즘/전수 Native/영구 WEQUIP 의존성 금지.

## 이번 사용자 결정으로 바로잡은 개발 우선순위

**78개 요소는 진척·증거의 정확한 기록이지, 모든 항목을 하나씩 심층 연구해야 하는 개발 순서가 아니다.** `next_review=B10`은 다음 **판정** 위치이며, 선택 기능인 추가 소켓의 내부 효과를 모두 추적한 뒤에야 일반 제품을 만들 수 있다는 뜻이 아니다. 네 증거 축과 COMPLETE/최종 실제 ZERO-SOURCE→USER-E2E 수락 조건은 그대로 유지한다.

매 새 개발 작업은 먼저 **(1) 사용자 결과 경로의 실제 차단 (2) 실제 소비 필드 (3) 기존 코드·영수증 재사용 (4) 비선택 옵션 보류로 BASE 실행 가능 여부 (5) Native/HTTP/DB2·유지비 (6) STOP 기준**을 확인한다. 비선택 미검증 옵션은 그 옵션만 감추거나 차단한다. 이미 검증된 기본 환경이나 다른 사용자 선택까지 막지 않는다. `STOP/REUSE/CONNECT/FIX` 우선, 새 수집기·효과 모델·Gate는 예외다.

## 사실과 한계 (이 문서 작성 시점)

- 저장소 `degong2-code/simc-secondary-optimizer-runner`, **격리 브랜치** `probe/chat-cache-v035-20261024`; 실제 HEAD는 인계 시 반드시 새로 조회. `main`·v003·원본 v016·Project UI·공식 승격은 변경 권한 없음. 현재 주 제품 개발 채팅이 구현을 계속 소유.
- 최신 [78요소 정본](development/78_ELEMENT_COMPLETION_CONTRACTS.json): **15/78 COMPLETE** (generic 27/current_source 27/product 15/historical 13 PASS), B10 generic/current_source/product PENDING, historical PASS, 전체 strict E2E PENDING. 숫자는 작성 시점 기록이며 실제 최신 JSON 우선.
- v445~v451 B10의 보석/물리 ItemID 일관성 방어는 보존. [v452 실제 70783 ItemID→use SpellID](development/notes/2026-11-14_p1-v452-b10-real-70783-on-use-item-source.md), [v454/v455 SpellEffect 원본·봉인된 v281 진단](development/notes/2026-11-14_p1-v454-v455-b10-real-spell-and-sealed-v281-j-source.md)은 **연구 자료**로 남긴다. 실사용 소켓 적용 권한/J 신규 승인은 미증명. **더 이상의 B10 주문 체인/전 품목 검증은 일단 중단**하고 일반 제품의 첫 실제 차단을 우선 확인한다.
- 최근 v098 집중 회귀 **489 PASS/0 FAIL** ([Actions #43570938990](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43570938990)); v401 최신 검사 PASS는 당시 해당 HEAD의 범위에 한정. Reusable Offline 공통 ledger의 역사 오류 198건은 모든 제품 코드 실패가 아니다. 이번 정책·인계 문서 기록 자체로 새로운 Native/DB2/API·사용자 E2E 증거가 생기지 않는다.

## 다음 개발 채팅이 해야 할 첫 판단

1. 현재 USER 웹/시즌 Build/대표 프로필/SimC 결과의 실제 실행 경로를 열고 **검증된 기본 조건을 막는 가장 작은 현실 결함**을 찾아라. 기능이 동작하면 새 수집 대신 기존 증거·캐시를 우선 재사용하라.
2. 그 결함의 원본·수치·예산 정확성을 해치지 않는 **최소 CONNECT/FIX**와 변경 범위 집중 회귀를 제안·시행하라. 임의의 B10 연구, 78 ID 숫자 채우기, 외부 자료 전수 다운로드를 자동으로 재개하지 마라.
3. 결과 보고는 사용자 가치·실제 진행도·실행증거와 PENDING 분리·비용/기존 캐시 재사용을 먼저 제시. 다음 채팅에 동일한 [상시 정책](development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md) 링크를 반드시 인계하라.

**새 사용자 직접 결정 > 이 운영 해석 > 비충돌 승인 설계 > GitHub 실제 코드/영수증 > 과거 인계**. 단, 이 문서는 승인 설계/기계 정본의 값이나 실제 개발 상태를 변경하는 근거가 아니다.
