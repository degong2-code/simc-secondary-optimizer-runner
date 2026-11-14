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

## 이미 실행된 다른 DPS 기본 사용자 — 신규 재측정 STOP (2026-11-14 재확인)

- **냉기 마법사**: [2026-11-10 real #42785318578](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42785318578) SUCCESS. ilvl334·일반보석4·특수0·O0, **수동 T3300**, 실제 v216/v212→v098 사용자 프로필→FastAPI/v291 Native2·캐시 재실행 신규0, DPS165226.98/SEM706.33, 95% 우위 미확정. [원본 근거](development/notes/2026-11-10_p2-fresh-four-ordinary-cross-profile.md).
- **풍운 수도사**: [2026-11-11 real #42941245130](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42941245130) SUCCESS. 70783·ilvl334·일반보석4·특수0·O0, **자동 T3107**, 실제 원본 GJFO→새 프로필→SimC. v290 DPS183394.77/SEM259.63. 기존 64+64회는 역사 알고리즘 연구 비용이지 새 기본 제품 실행의 필수 반복량 아님. [원본 영수증](development/research_receipts/p2_v319_windwalker_auto_T_real_v290_v318_compact.json).
- **조화 드루이드**: [2026-11-11 real #42949922419](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42949922419) SUCCESS. 같은 빌드·ilvl334, 일반보석4·특수0·O0, **자동 T3107**, 신규 사용자 프로필·실제 Native. v290 DPS176065.99/SEM271.35. 기존 64+64·추가 N32는 과거 정책 연구이며 신규 필수 Gate 아님. [원본 영수증](development/research_receipts/p2_v324_balance_auto_T_variable_n_32_compact.json).
- 세 실증은 개별 user-like FastAPI/원본/SimC 범위이며 개인 Windows 브라우저 클릭·전체26·미래 시즌·strict ZERO-SOURCE→USER-E2E 제품 전체 PASS는 아니다. v343/v439의 생존 사냥꾼과 다른 전문화임이 실증되어 있으므로 **'다른 DPS 1건' 명목의 새로운 전체 DB2/Native 실행은 STOP**. 오래된 다른 시즌 수치를 미래 시즌에 전용해서도 안 된다.

## 다음 개발 채팅이 해야 할 첫 판단

1. 위 실증 3건을 먼저 확인하고, 이미 입증된 기본 4보석/O0/자동·수동 T/USER→SimC 연결의 재인증을 위한 신규 Native 계획은 **STOP**하라. 실제 UI/API 사용자 경로가 실패하는 **새로운 구체적 장애물**을 찾아 기존 원본·캐시를 사용해 최소 수정하라. 선택지 근거가 없으면 그 선택지만 보류한다.
2. 그 결함의 원본·수치·예산 정확성을 해치지 않는 **최소 CONNECT/FIX**와 변경 범위 집중 회귀를 제안·시행하라. 임의의 B10 연구, 78 ID 숫자 채우기, 외부 자료 전수 다운로드를 자동으로 재개하지 마라.
3. 결과 보고는 사용자 가치·실제 진행도·실행증거와 PENDING 분리·비용/기존 캐시 재사용을 먼저 제시. 다음 채팅에 동일한 [상시 정책](development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md) 링크를 반드시 인계하라.

**새 사용자 직접 결정 > 이 운영 해석 > 비충돌 승인 설계 > GitHub 실제 코드/영수증 > 과거 인계**. 단, 이 문서는 승인 설계/기계 정본의 값이나 실제 개발 상태를 변경하는 근거가 아니다.
