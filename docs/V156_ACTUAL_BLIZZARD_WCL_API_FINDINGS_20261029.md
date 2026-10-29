# v155/v156 실제 인증 API 시험 — 시즌 식별과 보스 드롭 ID

**2026-10-29 1회 한정 자료 수집 검증.** 재조회가 필요한 새로운 개발
게이트는 아니며, 범용 제품 엔진의 선행 Native 전수 시험도 아니다.

## 1. 인증 실제 응답으로 확인된 콘텐츠 (v155)

GitHub Actions [#40826278881](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40826278881)
에서 Blizzard KR OAuth 인증 후 Game Data 4회 조회가 HTTP 200 반환:
- `mythic-keystone/season/index`: `current_season.id = 18`
- `mythic-keystone/dungeon/index`: `dungeons` 87개;
  **현재 시즌 8개라고 이 응답만으로 단정하지 않음**
- `mythic-keystone/period/index`: `current_period`, `periods` 447개
- `journal-instance/index`: `instances` 214개

WCL OAuth 인증 후 WorldData GraphQL 2회:
- `Midnight` expansion ID **7**
- 비고정(frozen=false) `Mythic+ Season 2` zone **55**, 던전 8:
  Altar of Fangs; Den of Nalorakk; Kings' Rest; Murder Row;
  Ruby Life Pools; Temple of Sethraliss; The Blinding Vale; Voidscar Arena
- 비고정 `The Venomous Abyss` zone **53**, 전투 10개
- 해당 조회의 WCL `encounters.journalID`는 **모두 0**.
  API 스키마상 존재하는 필드지만 이 환경에서 자동 ID 연결에 사용 불가.
  Blizzard Journal에서 실제 인스턴스/보스 ID를 별도로 조회해야 한다.
- `frozen=false`만으로 임의 zone의 시즌 적격성을 인증하지 않는다.

## 2. Blizzard 저널 실물 매핑 (v156)

WCL raid 이름 `The Venomous Abyss`를 Blizzard
`journal-instance/index`에서 정확히 발견:
**Journal instance 1320**, 보스 8명:
- Nek'zali the Soulcoiler: 2888
- Entombed Sentinels: 2874
- The Lost Explorers: 2894
- Vashnik the Malignant: 2882
- Sszorak: 2871
- The Twin Fangs: 2887
- The Coiled Altar: 2883
- Ula'tek: 2895

WCL 같은 zone 전투 10개와 Blizzard 해당 단일 instance 보스 8개는
서로 다르다. WCL에 표시된 `Kith'ix`와 `Nymrissa Wavecaller`를
1320의 보스로 임의 삽입하지 않는다. **이번 API에서 보이지 않는다는
사실만으로 해당 시즌 드롭이 아니라는 뜻은 아니다.**
초기 v156은 Kith'ix 이름 불일치를 안전하게 차단했고,
실제 후보 이름을 수신한 뒤 사용자에게 확인된 보스만 조회했다.

최종 성공 [Actions #40827019159](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40827019159):
`journal-encounter/2888`가 실물 `items` 목록을 제공.
**16개 고유 ID**, 기존 v047 394 + partial10과 **13개 겹침**,
기존에 없던 ID는 **279115 / 280305 / 281227**.
기존 spell-bearing 후보 **270162**가 이 보스 드롭에서 확인됨.
이것은 효과의 SimC 실행·발동 여부 확인이 아니라 item ID 출처 확인.
JSON 영수증 SHA256:
`2ff1a0c94a76d872f636e22fa4c272aad7a206bf7dac3d81a750c078d18fbd59`.
정확한 ID들은 `integration_probes/catalog/v156_one_boss_observed_ids_20261029.json`
경량 데이터와 Actions artifact에 보존한다.

## 3. 범용 아키텍처에 대한 실제 결론

**Blizzard 시즌 ID + WCL 현재 시즌 콘텐츠 구역 → Blizzard
Journal instance/encounter 이름-대-ID 매핑 → 보스별 드롭 ID →
기존 경량 목록/SimC item data**가 동작한다는 표본 실증 확보.

남은 실제 범위는 WCL 시즌2 던전 8개 각각 Blizzard Journal 매핑,
레이드의 분리된 추가 전투 인스턴스, 그리고 구렁/던전 일반 드롭
같은 공식 REST 누락 보완이다. 1개 성공을 전체 시즌 성공으로 확대 금지.
차후 full enumeration은 선별된 콘텐츠 범위·호출량과
누락/신뢰도 규칙부터 확정해 사용자 지시에 맞게 진행한다.

**기존 제품 v094/v046/v151/예산/캐시/26개 DPS 변경 없음.**
이번 시험 신규 SimC Native **0회**.
