# 2026-11-05 · P3-ES · 기술 자산 라이브러리와 인계 경량화

- **Capability:** `DEV.CONTINUITY`
- **Keywords:** P3-ES, capability library, INDEX, function map, reuse, handoff, 역사 기록, 검색 비용
- **Prior evidence:** [PROTOCOL](../PROTOCOL.md), [기존 INDEX 원문](../HISTORICAL_INDEX_20261105_PRE_LIBRARY.md), [P3-EN](../../CHAT_CONTINUITY_HANDOFF_20261105_P3_EN_ENGINE_FIRST.md), [P3-ER](2026-11-05_p3-er-existing-simc-intrinsic-socket-source-connection.md). 기존 ledger는 16개 Capability 키와 6열 표, 키별 실제 note 링크를 요구. 기존 INDEX에 P3/CI가 누적되어 함수·증거 재사용을 빠르게 찾기 어려웠음.
- **Decision:** `REUSE` — 기존 기록·증거/코드와 16개 키는 보존, `INDEX.md`를 기능 중심 A~G 라이브러리로 재구성. 시간순 장문 INDEX는 같은 폴더의 역사 스냅샷으로 보존. 새 수집·Native·효과 엔진·옛 기록 전수 재감사는 하지 않음.
- **Changes:** `docs/development/INDEX.md`에 기능별 사용 함수·검증 범위·제품 연결 상태·재작업 금지를 작성하고 하단 16키 호환 표 유지. `PROTOCOL.md`의 선조회·인계 규약, `CURRENT` 및 실행 노트/단일 새 채팅 인계 포인터 갱신. **DOCS_ONLY**, 제품·cache·세션 코드/원본 불변.
- **Verification:** 신규 문서 HEAD **NOT_VERIFIED** (커밋 후 Actions 확인). 이전 코드 [focused #41986004769](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41986004769) **253 PASS/0 FAIL·DEV_LEDGER_PASS**, [v212 #41985639098](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41985639098) 양 OS **447 PASS/4 SKIP**는 이전 P3-ER 코드 시점 증거. 이번 실 Native·게임 HTTP·신규 READY 실행 **0회**.
- **Remaining:** 원래 `v216` 새 시즌 공식 G/J/F/O→`v222` B/T→`v220/v196` 정책 A 실제 발행→`v212` 설치 READY/T1 미완료. `source-only`·`prepared`와 제품 배포를 구분. 다음 작업은 라이브러리 E3→E2→E1부터 CONNECT, 정말 부족한 소스만 EXTEND.
- **Efficiency:** 향후 작업에서 관련 A~G 영역 1개와 교차 영역 1~2개만 조회. P3 역추적·동일 실험 반복 비용 방지, 상세 과거 원문 보존. 실제 비용/속도 개선율 미측정. main/immutable/v016/Project UI/Work OS/개발 주도권 변경 없음.
