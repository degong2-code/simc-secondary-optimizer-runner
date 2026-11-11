# v341 — Windows 실 Native N56 단일 사용자 중단·재개 시험

- **Capability:** PRODUCT.E2E / DEV.CONTINUITY.
- **Decision:** REUSE / CONNECT. 기존 v205 Windows Native6와 v334 Linux N56 Native12의 서로 다른 실증 사이 Windows N56 전주기 부분만 1개 전문화·12회 상한 시험한다.
- **Scope:** Windows-2022, 공식 고정 SHA의 과거 710c240 SimC, 징벌 성기사 목표 334. 현 12.1.5.70783 시즌 검증으로 간주하지 않는다.
- **Flow:** v113 /longrun/start → 실제 v293 N56 2회 → 새 HTTP 앱 객체에서 세션 읽기 → /cancel → bounded 취소 → continuous 재개 → 최대 12회 DPS/SEM/95% 결과 → cache-only SHA 재사용 → 세션 다시 열기.
- **Bounds:** 최대 신규 SimC 12회, 일반 장비/알고리즘 재개발 및 전 전문화 Native 없음. 정확한 pinned 아카이브 원본을 재사용하고 7일 동안 JSON2·영수증 보존. 일회성 커밋 태그 및 workflow-only 트리거 적용.
- **Verification:** Actions 검증 전 PASS로 표시하지 않는다. 실패하면 원인을 기록하고 무조건 반복 실행하지 않는다.
- **Unproven:** 사용자 개인 Windows 브라우저 실조작, 64회 전체 기본 실행, 현 70783 Windows Native, 차기 시즌 최초 READY.
