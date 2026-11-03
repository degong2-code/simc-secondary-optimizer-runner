# SIMC SECONDARY OPTIMIZER · P3-BQ · 새 채팅 인계 정본 (2026-11-03)

**최신 인계 우선순위:** 사용자 직접 승인한 **과거 개발 성과 선조회·중복 검증/재개발 방지** 교정 규약을 이 문서에서 새 채팅의 첫 읽기 순서로 고정한다. 기존 [P3-BO 역사 인계](CHAT_CONTINUITY_HANDOFF_20261103_P3_BO_ENGINE_GJFO_NEXT.md)의 P3-BO 당시 상태/CI 내용은 보존하되, 그 문서의 `미인증/미완료` 문구만으로 새 조사를 자동 시작하지 않는다.

## 첫 응답 (복원만 수행, 사용자 '진행' 전 작업 금지)

1. 실제 GitHub `degong2-code/simc-secondary-optimizer-runner` 브랜치 `probe/chat-cache-v035-20261024` **현재 HEAD와 main을 조회**하고, [PROTOCOL](development/PROTOCOL.md)과 [INDEX](development/INDEX.md)를 먼저 읽어 적용한다.
2. 현재 진행하거나 제안된 기능 키(`TIER.SEASON`, `G.NUMERIC`, `J.GEM` 등)를 한·영 키워드로 INDEX에서 조회하여 원본 출처/관련 코드·실제 Actions/Native 영수증을 좁혀 확인한다. [P3-BQ 교정 노트](development/notes/2026-11-03_p3-bq-continuity-correction.md)를 확인한다.
3. 그 다음 [P3-BO 역사 인계](CHAT_CONTINUITY_HANDOFF_20261103_P3_BO_ENGINE_GJFO_NEXT.md), [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md), [승인 설계 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md), [개발자 실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md)를 필요한 범위에서 확인한다. 코드 구현·원본 증거·제품 READY·오프라인 CI·실 Native를 엄격히 구분해 **복원 보고 후 중단**한다.
4. 새 작업을 사용자가 지시하면 선조회 → `REUSE/CONNECT/EXTEND/NEW/STOP` 결정 → 해당 재사용 증거·실제 누락 사항·효율을 기록한 **작업당 노트 1개 및 INDEX 수정** → 기존 엔진 최소 패치 → focused CI/필요 최소 원본·Native → 노트 결과 기록을 따른다. `false/PENDING` 단어 자체는 원본 조사 실패를 의미하지 않는다.

## 직전 중복 작업 예방을 위한 핵심 사실 (다음 채팅 재조사 금지)

- **티어 시즌 식별:** [P3-AQ](P3_AQ_20261102_TIER_TOKEN_BASE_ILVL_SOURCE_PROOF.md) 실제 같은빌드 S1 197×65 / S2 219×65 기초 ilvl. [P3-AR](P3_AR_20261102_RAID_BONUS_TREE_TIER_SEASON_CORROBORATION.md) 활성 레이드 전리품 118 중 101개 S2 보너스 그룹 상관. [P3-AT](P3_AT_20261102_NORMAL_SIMC_SOURCE_INTEGRATION.md) exact 13직업×5 물리 ID·2/4세트와 SimC set option 일치. **기초 ilvl만으로 활성 시즌 확정은 불가**지만 위 **복합 증거는 이미 확보**했다.
- **진짜 미완료:** 현재 `v245/v250/v251`의 최종 선정·제품 통합은 `season_membership_verified=false`; 지금 필요한 것은 기존 증거를 **사용할 수 있는 범위와 필요한 최종 선정 조건을 검토하고 정상 Build에 연결**하는 일이지 새 독립 티어 인증기나 65부위 전수 원본 재수집이 아니다. G/J/F/O 실제 rating과 최고 품질·유효 손, v222 B/T의 실제 원본 접합, 정책 A/READY/기존 adaptive DPS E2E는 미완료.
- **현재 직전 P3-BP:** [v217 SHA 중복 제거](P3_BP_20261103_ONCE_ONLY_SOURCE_SEAL_REUSE.md) 격리 브랜치 코드/테스트 반영, **변경 후 CI PASS 영수증 미확인**. 새 실제 SimC Native/외부 게임 DB 호출 0. 이것과 과거 P3-BO 430 tests PASS는 동일한 검증 범위가 아니다.
- **최신 P3-BQ:** 재사용 색인/작업 노트/오프라인 검사기 작성. 실제 코딩과 Github 반영은 별도, 제품 승격/새 CI PASS는 아직 검증 전.

## 불변 경계·장기 목표

지원은 **26 DPS**만. 미래 기본 목표 ilvl334 또는 수동 최종 `T`로 SimC DPS 최대화. 사용자가 전체 장비를 고르지 않고 엔진이 일반 대표 장비/무기/티어를 구성한다. 시즌별 `B=G+J+F`, `T=B+O` 및 L/E/O 한 번 회계, 최고 품질 정책 A, SimC proc/APL/DPS 책임, 95% 통계, 캐시·취소·재개 유지. **새 엔진/전수 시즌 DB/독립 효과 인증 Gate/무조건 전체 Native 반복 금지**.

기존 주 제품 채팅 개발 소유, 격리 브랜치 수정만 허용; **main·immutable v003·원본 v016·Project Sources/Instructions 실제 UI·Work OS 공식 승격은 별도 권한**. GitHub 문서 작성 ≠ Project UI 설치. 역사 Native·CI는 해당 조건에서만 재사용.

**전달 방법:** 이 짧은 문서 URL 하나를 다음 채팅에 제공하고, 순서대로 링크를 읽도록 한다. 새 채팅 첫 응답은 읽기·검증 보고 후 사용자 '진행' 대기.
