# v402 — A4·A5·A6 범용성 재판정: 기존 실 원본 + 다른 시즌/빌드 관계의 기존 회귀 재사용

> **판정 범위:** A4/A5/A6은 *새 시즌/빌드의 원본을 별도 수동 ID·캐시·GPT 판정 없이 기존 API/DB2 스키마로 수집·검증·봉인하는 기능*의 범용성이다. **해당 시즌의 모든 gear/J/F/O/WorldStateExpression/실 SimC·제품 사용자 E2E의 범용성은 이 세 항목에서 인증하지 않는다.** 미래 미출시 시즌의 실제 원본을 기다리는 미필요 Gate도 두지 않는다.

## 1. 왜 A4~A6이 뒤로 밀렸는가, 어떻게 차단했는가

A1~A3는 `ENGINE_AUTODISCOVERY_PASS`라고 판정했으나, A4~A6은 실제 원본 SHA·봉인·카탈로그 소유권에 집중해 `READY_SCOPED`까지만 기록하고 **동일 정책의 범용성 판정을 생략**했다. A7 다음으로 넘어간 뒤 사용자가 지적했으며, 이는 테스트 불충분을 먼저 입증한 것이 아니라 **독립 검증 축·다음 단계 검사 부재**라는 운영 구조의 결함이었다.

[v401 정책](../POLICY_78_ELEMENT_COMPLETION_GATE_V401.md)과 [단일 JSON 완료 계약](../78_ELEMENT_COMPLETION_CONTRACTS.json)에서 78요소의 `generic/current_source/product_integration/historical`을 분리하고, [자동 검사](../../../integration_probes/v401_completion_contract_gate.py)가 PASS에 **해당 ID 근거·실 커밋·실 Actions URL·노트·범주별 증거**를 요구하도록 추가. A4~A6의 범용성 증거가 아직 없으면 `next_review=A4/A5/A6`, A7 READY 선언 불가. 기존 수작업 상세 원장 마지막 칸과 [생성용 사용자 상태표](../78_ELEMENT_STATUS_GENERATED.md)의 일치도 CI 확인. 검증은 GitHub **코드·주장 정합**이지 외부 네트워크 사실을 다시 증명하는 Native가 아님.

## 2. 기존 원본·변형 회귀를 정확히 다시 대조한 결과

| ID / 수락된 범위 | 현 시즌 실제 ZERO-SOURCE 원본(새 수집 아님) | 범용성 회귀(기존 실제 Actions 재조회) | 판정 |
|---|---|---|---|
| **A4 Blizzard 인증 원본** | [v398](2026-11-13_p1-v398-a4-blizzard-source-owner-base-scoped-ready.md) / [실 인증 #43359408019](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43359408019): KR70783 Blizzard 4 게임 인덱스 각 원문 HTTP SHA/bytes, v242 봉인·원본 역할 구분 | [#43364420119](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43364420119), tested `5d5af73907c3a912e1a7ded46e1e1e5d46696a65`: v155 4 인덱스 고정 요청 구조·v242의 **가상 다른 빌드 13.0.0.88888** stage·인증 원본 동일 SHA 재사용/미관측 차단·v332 아이템명 선택 실패 시 비차단. Blizzard 동적 시즌ID가 바뀌어도 고정 시즌 번호를 코드에 넣지 않는 구조이며 WCL/DB2가 실제 장비 수치를 소유 | **범용 *Blizzard 기본 원본 요청·봉인* PASS**. 4 index가 전체 시즌 item 수치 원본이라는 주장 금지 |
| **A5 WCL GraphQL 원본** | [v399](2026-11-13_p1-v399-a5-wcl-original-graphql-source-ready.md) / [실 인증 #43365490208](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43365490208): WCL expansion index+전체 zone 2 GraphQL POST body/HTTP response SHA, 기존 v163 실 현재 DB2 raid10/M+8 조인 [#43357639329](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329) | [#43365447503](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43365447503), tested `0bc84c7bb14b636cb703244b6495946b6506cb23`: `tests/test_v242_wcl_source_lineage_offline.py`의 **다른 확장팩 ID 49/7, 다른 이름/보스, 공식 Blizzard current keystone ID 840**, 두 GraphQL request/response SHA·v217 같은 빌드 0재조회·fail-close, v163 다른 확장팩 raid 혼합 거부 | **범용 *WCL 두 원본 발견·관계 후보* PASS**. WCL `frozen=false`만으로 아이템 현재 소속 인증 금지 |
| **A6 Wago DB2 원본** | [v400](2026-11-13_p1-v400-a6-db2-ten-table-source-provenance-scoped-ready.md) / [실 10 DB2 테이블 #43357639329](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329): `v161` 실 `12.1.5.70783` 10 CSV/62,280,767B 원본 SHA, v163 같은 빌드 유일 조인 | [#43366468001](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43366468001), tested `d21cbed88975f2cb471cf91d4583c9b073f27428`: `tests/test_v161_db2_source_provenance_offline.py`의 **변경 빌드 13.0.0.88888 / mismatch 13.0.0.99999**, URL/빌드/enUS/10 테이블의 SHA/size/변조·출력 11개 봉인·캐시 0수집·v216 사용 경로 다르게 변형한 빌드 12.2.0.99999에서도 API 이전 고정 시즌값 미요구 | **범용 *빌드 지정 DB2 10개 원본 수집·봉인* PASS**. 새로운 시즌의 실제 CSV 내용·아이템 WSE 인수는 이후 A7/B/C |

**공통:** A1/A2/A3 자체의 현재 활성 확장팩·빌드·시즌 자동 식별은 이미 [v394~v396](2026-11-13_p1-v394-a1-current-zero-source-engine-pass.md)에서 인증했다. A4–A6을 별도로 실험하면서 **미래 시즌명/ID를 미리 입력할 필요가 없다**. 최종 78개 사용자 입력→대표 ilvl/GJFO→SimC까지는 아직 다른 요소들이 미구현/미인수이므로 상품 완료는 선언하지 않는다. 같은 시즌 정적 원본 캐시·Native 역사 영수증은 승인 유효 조건에서 재사용한다.

## 3. v401 강제 검증의 실제 의미·한계

- [최초 v401 Actions #43368686119](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43368686119)에서 **78개 JSON/상세 원장/생성 문서 교차검사 + 13개 부정 회귀 PASS**, 초기에 A4~A6 generic=PENDING으로 보존한 상태의 정상 검증이었다. **정책 파일 추가만으로 범용 PASS를 생성하지 않았다**.
- 본 v402에서 위 정확한 **실 원본+변형 회귀**를 다시 판독해 A4~A6 `generic=PASS`를 근거 ID에 개별 귀속하고, A7 검토 순서로 이동한다. 소스 원본 `current_source=PASS`는 그대로 유지, `product_integration=PENDING`, `historical=PASS`는 여전히 A10/A11/G2에만 적용.
- CI의 `--check`/부정 테스트는 잘못된 수락 범주, **다른 ID 영수증 대체**, 78개 누락, Markdown 상태 drift, 무증거 N/A, 미승인 A7 진입 및 전체 제품 PASS를 FAIL 처리한다. 외부 Actions artifact를 GitHub Actions에서 실제 조회·SHA로 인증하는 도구는 아니므로, PASS 승격의 근거 읽기 책임까지 대체하지는 않는다. **branch protection이 자동 설정된 것은 아니며** CI 실패를 무시하고 push하는 것을 물리적으로 막지는 않는다.
- **비용:** 이 재판정에서 Blizzard/WCL/Wago API 신규 요청 **0**, DB2 62MB 추가 다운로드 **0**, SimC Native **0**. v401의 Python 계약 검사 및 추가 focused CI만 수행. 기존 브랜치 격리/main·immutable·Project UI 권한 보존.

## 4. 후속 A7

A7부터 **각 요소의 범용성→현재 원본→제품 통합 축을 병렬로 점검**한 뒤 합격/미확정 각각의 근거를 정확히 기록한다. 그러나 **A7의 모든 미선택 아이템/WSE를 전역 필수 Gate로 만드는 것은 금지**: 실제 기본 대표 장비·선택한 아이템의 시즌 소속/조건만 검증하고 선택하지 않은 항목은 별도 범위로 보류. 그 후 G/J/F/O B/T 설치와 실제 ZERO-SOURCE→USER-E2E를 연결해 최종 제품을 완성한다.
