# v154 — API만으로 시작하는 보스 드롭 아이템 ID 수집

현재 `runner/v154_blizzard_season_loot_index.py`는 과거 WEQUIP,
v047/v057, 이전 시즌 아이템 목록 **어느 것도 읽지 않는다**.
오직 시즌 콘텐츠 탐색에서 발견한 공식 encounter ID 목록과
Blizzard `journal-encounter/{id}` 응답만 수집 입력이다.

## 입력

`--encounters`: 아래와 같은 **API에서 발견한** encounter ID,
instance ID 및 콘텐츠 출처 형태의 JSON. 예시 숫자는 가상 ID다.

```json
{"encounters":[
  {"encounter_id":987,"instance_id":432,"kind":"raid"}
]}
```

`--live`: GitHub Secrets/환경변수의 Blizzard Client ID+Secret을 통해
OAuth token을 얻고, 공식 Journal을 최대 48개만 조회한다.
`--journal-dir`: 별도로 받은 `encounter_<id>.json`을 오프라인 파싱하되
그 입력의 진짜 API 출처를 독립 검증했다고 주장하지 않는다.

```powershell
py -3 runner/v154_blizzard_season_loot_index.py --encounters season-encounters.json --journal-dir journal --out season-loot-ids.json
```

## 출력·한계

`unique_item_ids`와 각 아이템의 `source_encounter_ids/source_kinds`,
보스별 `loot_state`, `encounters_missing_loot_field`를 제공한다.
실제 `items`가 빈 배열인 것과 필드가 없어 `UNKNOWN`인 경우를
구별한다. 기존 DB 일치율과 비교 결과는 **전혀 출력하지 않는다**.

현재는 encounter manifest를 구성하는 콘텐츠 자동 탐색/매핑이 완전
연결되지 않았으며, 이 문서의 예시 ID로 실제 API를 조회해서는 안 된다.
수집된 ID를 `v158` 새 인덱스에 전달할 수 있다. 특정 보스의 실제
조회 증거는 `v156` 역사 JSON을 보존하되 입력 우선권으로 사용하지
않는다. 전체 시즌 완전성 보증·정적 L·SimC proc/DPS 계산 없음.
