# v158 — 아이템 자료 0개에서 시작하는 시즌 수집 인덱스

이 모듈은 **기존 데이터베이스 없이 새 시즌 데이터 수집 엔진을 구성**하기
위한 최소한의 저장 계층이다. 이전 WEQUIP/v047/v057 목록 또는 현 시즌
수집 이력에 대한 일치/누락 비교는 **수집 데이터 경로에 없다**.

수집 순서:
- v155 Blizzard/WCL 시즌 콘텐츠 API 응답: 현재 시즌 ID·콘텐츠 구역
- v154 공식 Blizzard Journal 보스별 드롭 ID
- v156 단일 보스 공식 Blizzard Journal 응답
- v157 공식 Profession skill-tier 전체 recipe references와
  명시적으로 얻어진 결과 아이템 ID

출력 `v158_source_first_season_acquisition_index_v1`:
`item_ids`, `items[].acquisition_sources`,
`collection_receipts`, `unresolved_provider_fields`,
`full_season_completeness_confirmed=false`.

제작법이 결과 Item ID를 공개하지 않으면 **UNKNOWN**, 임의 유사한
이름의 아이템을 찾거나 기존 자료에서 채워 넣지 않는다.
구렁의 고정 드롭/상자/금고/상인 보상을 각기 다른 획득 출처로
구분해야 하며, 공식 실제 출처가 미확보면 UNKNOWN이다.

오프라인 독립 시험: 완전히 가상의 새 시즌/새 아이템 ID로
수집 성공, 중복 출처, 명시적 빈 loot와 미제공 loot의 차이,
범위 밖 schema 차단, 구성 파일 저장을 확인한다.
이는 실제 미래 시즌 전체 수집 PASS 증거는 아니다.

실행 예시(실제 취득된 API report 파일을 지정):
```powershell
py -3 runner/v158_source_first_season_catalog.py --report v155-live.json --report v154-live.json --report v157-live.json --out season-acquisition-index.json
```

DB는 **획득 가능성/출처에 관한 경량 ID 인덱스**이지 장비 조합,
획득 추천, SimC 스탯/effect/DPS의 재구현이 아니다. Native 호출 0.
기존 동일 시즌 static item cache는 제품에 보존되며 이 수집
파이프라인이 덮어쓰거나 그 데이터를 수집 입력으로 사용하지 않는다.
