# SIMC SECONDARY OPTIMIZER — GitHub 현재 상태 기반 동적 인계 프롬프트

> **상시 인계 문법 (2026-11-15 사용자 직접 결정)**. 이 문서는 과거 v479 또는 현재 채팅의 고정 상태를 옮기는 인계서가 아니다. 새로운 채팅이 **그 시점의 GitHub HEAD, 현재 승인 정책, 실제 코드, 봉인 증거와 테스트**를 독립적으로 읽고 우선순위를 재판정하는 절차다. [제품 소비·과잉검증 감사 정본](development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md)을 반드시 읽되, 그 문서의 역사 숫자는 절대 현재 진척으로 복사하지 않는다.

## 새 채팅에 붙여 넣을 프롬프트 (SHA·버전·날짜 고정 금지)

```text
# SIMC SECONDARY OPTIMIZER — 현재 GitHub 독립 복원·제품 우선 최소 개발

이 작업은 ROTATION TEXTBOOK이나 WCL 분석이 아니다. SIMC SECONDARY OPTIMIZER의
최신 개발 상태를 GitHub 실제 자료에서 독립 복원하라. 이 프롬프트, 과거
채팅 요약, 이전 인계서에 쓰인 HEAD·PASS·다음 작업을 현재 사실로 복사하지 마라.

저장소: degong2-code/simc-secondary-optimizer-runner
기존 격리 개발 브랜치 출발점: probe/chat-cache-v035-20261024
먼저 브랜치가 아직 실제 개발 브랜치인지 확인하고 최신 HEAD와 커밋·
CURRENT_PRODUCT_DEVELOPMENT_STATE.md·Actions/Native 영수증을 확인하라.
브랜치가 이동/폐기됐다면 실제 최신 개발 분기를 증거로 확인해 설명하고,
임의로 main에 작업하거나 과거 HEAD를 정본으로 삼지 마라.

1. 최신 사용자 직접 결정과 승인된 제품 목적을 최우선 적용하라:
   - docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md
     및 최신 비충돌 보충 정책·Project Sources를 확인
   - docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md
   - docs/development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md
   - docs/development/78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md
   - docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md
   - docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json
   - docs/development/FILE_MAP.md / EVIDENCE_INDEX.md / DECISIONS.md 중 지금 필요한 부분
   - 해당 작업의 실제 코드/테스트, 최근 커밋 diff, 관련 Actions/Native 영수증

2. 최종 제품은 26개 DPS 전문화에서 목표 ilvl 기본 334 또는 사용자 최종
   T의 최적 절대 CHMV rating을 기존 적응형 SimC DPS로 찾는 프로그램이다.
   사용자 입력 → 현재 시즌 대표 장비/무기/티어 4pc·G/J/F/O →
   B=G+J+F, T=B+O, 수동 T 우선·L/E/O 중복 방지 →
   SimC 프로필 → 기존 적응형 탐색/캐시/취소·재개 →
   DPS·SEM·95% 판정·관측 1순위·의미 있는 근접 대안·스탯 비율.
   현재 장비 재분배, 장비 조합 추천, 시즌 전체 아이템 DB,
   SimC 효과/proc/APL 재구현은 범위 밖이다.

3. 먼저 현재 구현 상태를 다음처럼 분리하라:
   (A) 실제 제품 코드에서 작동하는 기능
   (B) 기존 실 Native/E2E PASS의 정확한 범위와 재사용 가능성
   (C) 합성/offline PASS일 뿐인 부분
   (D) 실제로 재현된 사용자 장애·미구현 연결
   (E) 선택형 미확정(비선택 BASE를 차단하면 안 됨)
   (F) 최종 78요소/엄격 ZERO-SOURCE→USER-E2E 수락의 현재 상태.
   GitHub CI SUCCESS를 신규 Native 실행·정식 제품 COMPLETE와 혼동하지 마라.

4. 각 개발/검증 제안 전에 '누가 어떤 사용자 입력으로 실제 무엇을
   못 하는가?'를 정의하라. 관련 필드·구분자의 생성자→실제 런타임 소비자
   →출력/캐시/호환성의 영향을 확인하고 자료가 있다는 이유만으로
   Gate·원본 수집·효과 인증을 만들지 마라. WSE처럼 진단값인 것은
   진단으로 남기고, 실제 ItemID/빌드/예산/결과에 필요한 값만 검사하라.
   v280/v281 전체를 무작정 제거하지 마라: F/O 실제 소비 부분이 있다.

5. STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW.
   기존 v417/v439/v440 및 다른 유효 Native·시즌 영수증·캐시를 재사용하라.
   미선택 추가 소켓·효과·시즌 모듈이 기본 READY/일반 DPS를 막으면
   선택지 단위로 분리하라. v441에서 이미 78/78 필요성 감사
   (54개 완화/24개 유지)를 했으므로 다시 전수 감사하지 마라.
   78 JSON의 next_review는 다음 개발 항목이 아니라 판정 위치다.
   기본 프로필 E2E가 과거 통과했는데 처음부터 증명하는 Native를
   반복하지 마라.

6. 이번 감사에서 아직 미확정인 제거·단순화 후보는 현재 코드로 다시
   판단하라: v216 내 선택 연구·기본 Build 분리, v477 UI 카탈로그
   guard와 v478 서버 SHA의 중복/과잉 차단, 런타임 미사용 source-only
   상태·구분자, 중복 원본 SHA 해싱, 역사 개발 원장 format 검사/198건,
   one-shot workflow와 중복 노트·회귀. 저장 세션·구버전·진단 소비가
   있을 수 있으니 근거 없는 삭제·Gate 해제는 하지 마라.

7. 효율: 작업 전/후 추가 Native·HTTP/DB2·CPU/메모리/I/O·실행시간,
   캐시·중복 실행·기존 세션 호환을 검토하라. 변경한 경계만 최소
   검증하며, 신규 Native가 실제 필요하지 않으면 실행하지 마라.
   신규 코드/오프라인 PASS/재사용한 역사 Native/새 실제 Native/
   제품 수락·미구현은 정확히 구별하라. 불필요한 새 관리 문서나
   두 번째 Gate를 만들지 마라.

8. 권한: 현재 주 제품 개발 채팅의 소유권 유지. 별도 지시 없이
   main 병합, immutable v003·원본 v016 수정, Project UI/Instructions
   실제 적용 주장, Work OS 공식 승격은 하지 마라. GitHub 격리 분기
   작업과 공식 승격을 구분하라.

첫 응답은 반드시 읽기 전용 복원 결과로:
① 현재 HEAD/주요 근거 ② 일반 사용자 실제 가능/막힘
③ 필수 vs 선택 보류 ④ 과거 증거 재사용·STOP할 검증
⑤ 최소 비용의 실제 사용자 가치가 있는 다음 작업 1개
⑥ 기존 자료와 설계 기준 사이의 차이를 보고하라.
이 첫 복원 요청만으로 코드·GitHub 문서·Actions·Native를 수정하지
말고 STOP하라. 별도 '진행'을 받으면 그 시점의 최신 코드와 실제
장애·권한 범위를 다시 확인하고 필요한 최소 작업을 수행하라.
```

## 문서 조회가 불가능할 때

- 연결된 GitHub에서 실제 자료를 읽지 못했다면 **미확인**으로 표시하고, 과거 대화의 숫자·HEAD·구현 상태를 현재 사실로 추정하지 않는다.
- Project UI 등록 여부는 GitHub 파일의 존재만으로 추정하지 않는다. 실제 사용자 제공 파일이나 Project Sources가 있다면 최신 직접 결정과 함께 읽되 과거 바이트와 혼동하지 않는다.
- 새 사용자 요구가 제품 정책과 충돌할 때는 최신 직접 결정을 우선하되, 기존 구현과 데이터의 변경 비용·영향을 설명한다.
