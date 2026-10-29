# v161 — Wago DB2 제로베이스 실제 CSV 시험 (2026-10-29)

**본 시험의 목표는 과거 WEQUIP/다른 프로젝트 아이템 목록이 0개인 새 시즌에서
원본 DB2를 직접 취득하고 실제 WCL 시즌 정보와 결합해 아이템 ID를
발견할 수 있는지를 확인하는 것.** 기존 404/51/79개 데이터는
후보 선정·수집 입력·누락 평가에 사용하지 않았다.

## 인증된 소스와 빌드

- WCL 현재 시즌 콘텐츠: [v155 실제 인증 조회 #40826278881](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40826278881),
  2026-10-29 당일 WCL Midnight expansion의 `Mythic+ Season 2`
  8던전 및 `The Venomous Abyss` 10 encounters.
- wago.tools 실제 자료: [v160 CSV 헤더 검사 #40836140708](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40836140708):
  9/9 필수 테이블 CSV/필드 정상.
  [v161 원본 CSV #40836955761](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40836955761):
  **Retail `12.1.5.70575` + enUS**, 10개 테이블 전체 200/다운로드 PASS.
  총 원본 CSV 약 62MB. GitHub Actions 2일 보존 ZIP 내 원본/각 SHA.
  신규 Native SimC **0회**.
- 다운로드 테이블:
  `JournalTierXInstance`, `JournalInstance`, `JournalEncounter`,
  `JournalEncounterItem`, `MythicPlusSeasonTrackedMap`,
  `MapChallengeMode`, `Map`, `CraftingData`, `ItemSparse`, `Item`.

## 처음부터 실제 결합한 결과

| 그룹 | 발견 범위 | DB2 원본 Item ID 참조 | Item/ItemSparse 장착 후보 (임시) |
|---|---|---:|---:|
| 레이드+소굴 | WCL 10보스 모두 DB2 고유 encounter와 1:1 연결 | 144 | 105 |
| 쐐기 | WCL 현 시즌 8던전 모두 DB2 JournalInstance와 1:1 연결 | 247 | 223 |
| 제작 | 확장팩 11의 CraftingData 결과 + stat placeholder 24/25 + quality>=3 + 장비 class | 106 | 104개에는 알려진 내장장식 제한 코드(512/697) 없음 |
| 구렁 | Zah'ran 서버 측 상인 판매풀 연결 미확인 | **UNKNOWN** | **UNKNOWN** |

상세 보스 ID:
Nek'zali=2888, Entombed Sentinels=2874, Vashnik=2882,
Lost Explorers=2894, Sszorak=2871, Twin Fangs=2887,
Coiled Altar=2883, Ula'tek=2895,
**Nymrissa Wavecaller=2849(별도 Tidebound Grotto instance 1317)**,
**Kith'ix=2896(별도 Unbinding of Kith'ix instance 1324)**.

DB2 `MythicPlusSeasonTrackedMap.DisplaySeasonID=37`의
8개 던전 목록은 위 현재 WCL 시즌 2의 8개 명칭과 **정확히 일치**.
Blizzard REST의 `mythic-keystone current_season.id=18`과 DB2
`DisplaySeasonID=37`은 **서로 다른 namespace의 ID**이며 혼용하면 안 됨.

**통계 해석의 한계:**
- 레이드의 144는 JournalEncounterItem의 모든 명시 item IDs;
  105는 장착 가능 class/InventoryType으로 한정한 일차 후보.
- 쐐기 247에는 구 시즌/개편 전 던전의 참조가 일부 포함.
  일부 `WorldStateExpressionID=52104/52105` 등이 존재하므로
  실제 현 시즌 보상만 남기려면 해당 조건을 처리해야 한다.
  223도 **시즌 필터 적용 전 후보**다.
- 제작 106은 자유 2차스탯 placeholder 24/25 기반 **후보**.
  알려진 `ItemLimitCategory` 512,697 표시가 없는 104개를
  SimC 최종 검증 없이 무조건 일반 제작장비로 확정하지 않는다.
- **구렁 0개가 아니라 UNKNOWN**:
  client ItemSparse가 모든 아이템의 ID를 포함할 수는 있어도,
  Zah'ran의 서버 측 판매 장비 **소속 관계/전체 목록**은
  위 DB2 테이블이 증명하지 않는다. 사용자가 알려준
  'Zah'ran 풀=구렁 전체 풀'을 소스 선택 원칙으로 활용할 수 있다.
  그 경우 **현재 시즌 상인 목록을 독립 출처**(PTR/공식 게임 관측/
  Wowhead 공개 판매 테이블)에서 받으면 DB2로 Item ID/이름/부위
  검증 후 하나의 구렁 pool로 합칠 수 있다. 과거 프로젝트의
  기존 79개 ID를 새 엔진의 입력 seed로 자동 채택하지 않는다.

## 현재 통합 상태

- **구현 완료:** v160 API 접근 검사, v161 10 CSV의 버전 고정 및 SHA를
  포함하는 다운로드/임시 Actions artifact 경로.
- **현재 대화의 분석 환경에서 수행:** DB2 실제 행을 결합하여
  WCL 10보스·8던전·제작 106 후보 수량 확인.
  **이 분석용 join 로직은 아직 제품 GitHub 실행 엔진에 통합하지
  않았으며**, CURRENT가 제품 통합 완료를 주장하지 않는다.
- **다음 최소 작업:** 검증한 join을 재사용 가능하고 경량인
  source-first collector로 승격하고 쐐기 WorldState 필터를 정밀화,
  Zah'ran의 현재 시즌 판매 목록 데이터 원천을 연결.
  이후 SimC로 item ID+부위+effect/제작 옵션을 일괄 분류.
- main/v003/Project Sources/UI/원본 P1 최적화/SimC 정적 캐시 변경 없음.
