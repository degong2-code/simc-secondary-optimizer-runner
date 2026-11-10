# SIMC SECONDARY OPTIMIZER · 개발 지식 시작점

> 2026-11-10 격리 브랜치 검색 진입점. 파일·Actions·Native 현재 여부는 매 작업 실제 HEAD와 비교. **본 문서는 새 제품 코드/Native PASS를 의미하지 않는다.**

| 질문 | 문서 |
|---|---|
| 지금 무엇을 구현했고 남았나 | [제품 최신 A~G 정본](../PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md), [P3-HAW 인계](../CHAT_CONTINUITY_HANDOFF_20261110_P3_HAW_OPTIMIZER_RESUME_ENGINE_FIRST.md) |
| 어떤 코드·테스트를 먼저 봐야 하나 | [INDEX](INDEX.md) → [FILE_MAP](FILE_MAP.md) |
| 특정 파일이 어디 있나 | [전체 FILE_INVENTORY](FILE_INVENTORY.md) → [핵심 FILE_MAP](FILE_MAP.md) |
| 실제 CI·Native PASS 범위 | [EVIDENCE_INDEX](EVIDENCE_INDEX.md) → GitHub 원본 영수증 |
| 왜 그렇게 만들고 무엇을 철회했나 | [DECISIONS](DECISIONS.md) → 근거 노트 |
| 개발·인계 규칙 | [PROTOCOL](PROTOCOL.md) |
| 과거 경과와 이전 인계 | [원래 INDEX 기록](HISTORICAL_INDEX_20261110_PRE_KNOWLEDGE_LAYER.md), [원래 PROTOCOL 기록](HISTORICAL_PROTOCOL_20261110_PRE_KNOWLEDGE_LAYER.md), [개발 노트](notes/), [누적 CURRENT](../CURRENT_PRODUCT_DEVELOPMENT_STATE.md) |

## 현 시점의 중요한 판정

- 목표는 **26 DPS** 대상으로 목표 ilvl 기본334 또는 수동 최종 T에서 치명·가속·특화·유연의 **절대 rating**을 SimC DPS로 최적화하는 하나의 시즌 공통 엔진. 사용자 현재 장비 재분배/장비 조합 추천/시즌 전체 DB 아님.
- 현재 실 70783 Ret334 빈 작업공간: **일반보석 치·가·특·유 각1, 특수 없음, O0**, G2850/J92/F165/B=T3107, 기존 v216/v212 Native3→READY/검증 사용자 프로필 PASS. **미래 시즌·이 4보석 구성의 실제 DPS·Windows 개인 클릭**은 미실증.
- v290/v291에는 Native10/정확 cross-job 캐시 검증이 있다. 최신 사용자 승인 P2 설계는 [적응형 백분율 기준점·비례 정규화](notes/2026-11-10_p2-percentage-grid-proportional-normalization.md): 초기 11개 기준점은 고정이 아니며 실제 SimC 처리량으로 조정. 상한 보정·정수 총량 보정·다중 영역/미탐색 영역 정밀화를 포함하지만 **아직 설계만 승인, 코드 미구현·새 DPS 증거 없음**. 다음 중점은 P2 탐색 누락·멀리 떨어진 DPS 고점·95% 선택편향·실질적인 대안의 신뢰성, 전역 최적 증명 아님.
- `B=G+J+F`, `T=B+O`, 수동 T 우선, 기름 O와 L/E 고정 회계 중복 금지. SimC가 effect/proc/APL/DPS 책임. 신규 효과 인증 Gate 불필요.

## 검색 4단계

1. 최신 기능 판정 → INDEX의 A~G → FILE_MAP 코드/테스트 → EVIDENCE_INDEX 해당 영수증.
2. 왜 만들어졌는지는 DECISIONS의 결정 링크를 통해 이전 노트로 이동. 역사 문서의 `PENDING`을 현재 상태로 쓰지 않는다.
3. 먼저 `REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP`을 결정한다. **실패 재현과 증거 미확보를 분리**하고 기존 Native/원본/캐시의 유효 범위만 재사용한다.
4. 변경한 기능의 상태·파일 지도·증거 지도만 갱신하고, 원본 역사와 단일 인계는 삭제·중복 재작성하지 않는다.

격리 `probe/chat-cache-v035-20261024`의 변경과 `main`, immutable v003, 원본 v016, Project UI/Work OS, 공식 승격은 별도 권한이다. 주 제품 개발 채팅의 소유권도 유지한다.
