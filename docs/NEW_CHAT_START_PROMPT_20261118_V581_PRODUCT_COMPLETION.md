# SIMC SECONDARY OPTIMIZER — 2026-11-18 최신 독립 복원 (v581 이후, 제품 완성·영구 마부 전 선택지 우선)

SIMC SECONDARY OPTIMIZER를 **최신 GitHub 실제 HEAD·CURRENT·코드·Actions·Native/설치 SHA 영수증**으로 READ-ONLY 독립 복원하라. 새 프로젝트를 만들거나 새 최적화 엔진을 연구하는 작업이 아니다.

**GitHub:** `degong2-code/simc-secondary-optimizer-runner` / 격리 브랜치 `probe/chat-cache-v035-20261024`. 작성 당시 정책 HEAD `9bc8fd8952dd416c6277ee37ced9632651fa8f93`는 역사 스냅샷이다. **현재 HEAD를 다시 조회**하라.

**가장 먼저 읽을 정본:**
`docs/CHAT_CONTINUITY_HANDOFF_20261118_V581_PRODUCT_COMPLETION_PERMANENT_ENCHANT_FIRST.md`
그다음 `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 최상단, `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md` 최상단, `docs/development/POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md`, `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `docs/development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md`, `docs/USER_APPROVED_GEM_J_POLICY_20261117.md` F절, `docs/V211_ENCHANT_EFFECT_SOURCE_CLASSIFICATION_AND_EVIDENCE_20261031.md`, `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`, 필요 코드/Actions 순서로 확인한다.

**제품 목적:** 게임의 새 시즌에도 AI 호출 없이 원본으로 대표 일반 장비·무기·티어4pc와 G/J/F/O·B/T를 구축하고, 목표 ilvl(기본334) 또는 사용자가 직접 지정한 **기름 포함 최종 T**를 기준으로 **26개 DPS 전문화(증강/탱커/힐러 제외)**의 치명·가속·특화·유연 **최적 관측 절대 rating**을 실제 SimC DPS로 탐색한다. 결과는 rating·비율·DPS·SEM·95% 우위 판단·관측 1순위·실질적으로 다른 근접 대안·캐시/취소·재개. 장비 추천·현재 장비 재분배·시즌 전체 DB·새 APL/효과/최적화 엔진·런타임 AI는 범위 밖이다. `B=G+J+F`, `T=B+O`, 수동 `B=T−O` 우선, 고정 L/E/O 중복 금지.

**최신 사용자 승인 변경 — 이 순서가 최상위다.**
1. 현재 시즌 **실제 ZERO-SOURCE 제로베이스 구축/사용자 실행 v567·v570을 범용 시즌 자동 구축 엔진 기능의 PASS로 인정**한다. 아직 미출시 미래 시즌의 별도 실측을 요구해 PASS를 번복하지 않는다. 새 시즌 출시는 검증된 엔진의 정상 데이터 갱신·유지보수 대상이다.
2. **본 제품의 가장 중요한 남은 기능은 영구 마부의 지원 대상 모든 선택지 자동 구축·최고 품질 선별·정확 부위/조건/SimC 토큰·고정 E 정합·사용자 선택/프로필 등록을 완성하는 것.** 지금은 과거 소스 후보38개와 생존 사냥꾼 반지1 3개 실증만 있다. 전체 Environment Build SUCCESS는 이 영역이 완성되기 전에는 선언 금지. 그러나 미선택 마부가 미검증이라는 이유로 정상 BASE G/J/F/O 사용자는 차단하지 않는다. 일반 임시 마부 제외, 무기 기름은 지원.
3. **옴니움 장서·다른 확장팩 특수 시스템은 본 제품 전체 핵심 기능 완료 후 별도 선택형 모듈로 업데이트·ON/OFF 시험한다.** 핵심 완료 선행 Gate가 아니다.
4. **기존 최적화 v290(전역 분산·다중 스케일 지역 탐색·SEM 참고)→v291(SimC JSON2/SHA/캐시/취소·재개)→v293(신규 scout56/confirm320, 95% 판정·근접 대안)**를 보존한다. v303~v312 새 정책 실험이나 64회 반복 Native를 제품 필수로 되살리지 않는다.

**실제 증거:** v567 ZERO-SOURCE→SimC [#44046442654](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44046442654), v570 실제 Chrome 원클릭→DPS64 [#44074372451](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44074372451), v534 양수 마부 E+수동 T [#43974259684](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43974259684), v580 양수 기름 O 실제 Chrome·수동 T [#44106357901](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44106357901), v581 해당 O와 수동 T의 실 DPS2·재개·cache-only [#44110104367](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44110104367). v581 관측 846/995/830/829, DPS169750.54 SEM680.33, **95% 우위 미확정·전역 최적 미확정**. 공식 원장 **15/78 COMPLETE**, `full_product_e2e=PENDING` — 구현률 아님.

**다음 개발 원칙:** `STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW`. 영구마부의 실제 선택지 전체 발견→정확 ID/최고품질·조건→고정 E/프로필→사용자 등록 중 **처음 끊긴 소비 지점 하나**를 찾는다. 작업 전 UI/사용자 효과·기존 구현 재사용·Native/HTTP/DB2/CPU/메모리/I/O 비용·명확한 STOP을 설명. 38×26 Native 전수 금지, SimC 효과·APL 독립 인증 금지, 과거 성공 시험 재실행 금지.

**첫 응답은 7항목만 보고하고 STOP:** (1) 최신 HEAD/Actions PASS·FAIL·CANCELLED·SKIP (2) 사용자 가능 범위 (3) ZERO-SOURCE 엔진 기능 PASS와 전 선택지 등록의 경계 (4) v290+ 실증·Native/95% 경계 (5) 필수 영구마부 vs 선택 보류·Omnium 후속 (6) 비용 대비 다음 **한 작업**, 재사용·STOP (7) 공식 78 상태, 미확인 영수증, GitHub/Project UI/Work OS/주채팅 권한.

**첫 응답에서 코드·문서 수정, Actions·Native·HTTP/DB2 새 실행 금지.** 7항목 보고 후 STOP, 사용자의 별도 **“진행”** 이후 최신 HEAD 재확인하고 최소 범위 개발. 사용자 별도 승인 없이 `main` 병합, `v003 immutable` 변경, 원본 `v016` 직접 통합 완료 주장, Project Sources/Instructions UI 적용 완료 주장, Work OS M0/Shared State 승격, 공식 78요소 COMPLETE 변경, 기존 주 제품 개발 채팅 소유권 이전 금지.
