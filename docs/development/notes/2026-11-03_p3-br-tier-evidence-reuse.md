# 2026-11-03 · P3-BR · 기존 시즌 티어 증거를 정상 Build 대표 선정에 연결

- **Capability:** `TIER.SEASON`, `PRODUCT.E2E`, `DEV.CONTINUITY`
- **Keywords:** tier, 티어, current season, ilvl, 13x5, v245, v250, v251, v216, SimC, 증거 재사용
- **Prior evidence:** [P3-AQ](../../P3_AQ_20261102_TIER_TOKEN_BASE_ILVL_SOURCE_PROOF.md) base ilvl 197/219×65; [P3-AR](../../P3_AR_20261102_RAID_BONUS_TREE_TIER_SEASON_CORROBORATION.md) 활성 레이드 101/118 S2 보너스 관계; [P3-AT](../../P3_AT_20261102_NORMAL_SIMC_SOURCE_INTEGRATION.md) 정확한 SimC 13직업×5/2+4; [P3-BQ](2026-11-03_p3-bq-continuity-correction.md) 선조회 규약.
- **Decision:** `CONNECT` — 새 티어 인증기·아이템 전수 조사 대신 기존 v250/v251 **동일 빌드 레이드-티어 상관 + SimC 정확 ID**를 v216 일반 Build의 *티어 선정 출처*로 재사용한다. 단 기초 ilvl만으로 시즌을 단정하지 않으며 실제 G/J/F/O/READY는 별도 미완료.
- **Changes:** v251 source-only 티어 선정 요약 API 및 v216 정상 Build 연결, focused 두 모듈 테스트와 INDEX/CURRENT 갱신. 새로운 외부 source/Native/효과 Gate는 만들지 않는다.
- **Verification:** 이전 소스/Actions 영수증은 `REUSED_HISTORY`; 신규 코드 실행 CI `NOT_VERIFIED`(추가 확인 시 교정). 실제 신규 Native/외부 게임 HTTP 0회.
- **Remaining:** 연관 근거를 '현재 시즌 전체 아이템의 파밍 인증'으로 과장하지 않는다. 대표 일반 장비 일부의 조건·실 G, 최고 품질 J/F/유효 O, B/T→Policy A→READY/적응형 DPS E2E는 미완료.
- **Efficiency:** 새 Wago/Blizzard/WCL/SimC 조회·Native 호출 없음; 작은 기존 v217 봉인 JSON에서 시즌 티어 ID를 재사용, 캐시 원본은 변경하지 않음. 전체 시간·메모리/I/O 절감은 미측정.
