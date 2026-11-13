# 78개 요소 완료 계약: 정책이 실제 진행을 통제하는 최소 강제 절차 (v401)

> 2026-11-13 사용자 직접 승인: **반복 지적 없이**, 어떤 ChatGPT 채팅에서 개발하더라도 범용성·현재 시즌 원본·사용자 제품 통합을 **누락·혼동·성급히 PASS 선언하지 못하도록** 구조화 데이터/자동 회귀/단일 완료 판정 절차를 유지한다. 78개 Native 재실행, 전 품목 인증, 새 제품 엔진, 미래 미출시 시즌의 실측 선행 Gate를 만들지 않는다.

## 단일 상태 정본과 읽기용 파일

1. **상태·수락 조건의 기계 판독 정본:** [`78_ELEMENT_COMPLETION_CONTRACTS.json`](78_ELEMENT_COMPLETION_CONTRACTS.json). A1~H6 정확히 78개, ID·요소명·BASE/USER/RUN/OPTION·원래 수락 조건 + 4개 독립 판정 축, 해당 항목에만 귀속되는 근거 ID, 원본 테스트 SHA/Actions/노트 경로를 갖는다.
2. **사람이 보는 상태표:** [`78_ELEMENT_STATUS_GENERATED.md`](78_ELEMENT_STATUS_GENERATED.md). JSON에서 결정론적으로 생성. `python integration_probes/v401_completion_contract_gate.py --write`로 갱신하며 **직접 수정 금지**.
3. **78개 상세 감사·과거 맥락:** [기존 78개 항목 추적표](ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md)는 **인수 조건 및 작업 메모의 역사·세부 문서**로 유지한다. 다만 상태값을 독자적으로 승격할 권한은 없다. CI가 78개 모두 JSON 상태와 표 마지막 칸의 `ENGINE_*/READY_SCOPED/PENDING_SCOPE`가 정확히 대응하는지 검사한다. 기존 보고문에 남은 구 시점 진척은 **자동 생성 표가 우선**한다.

## 4개 독립 축 (완료 수준을 한 열로 혼합하지 않는다)

| 축 | PASS의 뜻 / 필수 증거 | 다른 축 대체 여부 |
|---|---|---|
| `generic` | 해당 기능이 **현재 실제 시즌 ZERO-SOURCE 원본**과 **시즌/ID/이름/빌드 등을 바꾼 출처 구동 회귀**에서 동작. 실제 엔진이 지원하는 API/소스/관계 범위만 승인. `CURRENT_SOURCE_REAL + GENERALIZATION_REGRESSION` 필요 | 현재 원본 SHA만 확인했다는 사실로 PASS 금지. 미출시 미래 시즌 실측은 PASS의 선행조건이 아님 |
| `current_source` | 현재 동일 빌드·원본 영역의 실 API/DB2/SimC Native(해당 시) **원본 및 SHA**·정확한 실제 소비·요청 범위. `CURRENT_SOURCE_REAL` 필요 | `generic`이나 제품 E2E 자동 PASS 아님 |
| `product_integration` | 해당 기능이 **실 사용자 입력 → 내부 시즌/예산/프로필 → SimC/제품 결과**의 실제 소비 경계와 정상 실패 처리를 확인. `PRODUCT_INTEGRATION_REAL` 필요 | 원본 GET 성공·오프라인 unit PASS로 승격 금지. 제품 전체 E2E는 별도 |
| `historical` | 특정 과거 빌드·프로필·옵션의 실제 영수증. `HISTORICAL_SCOPED` | 어떤 현재/범용/제품 검증도 대체하지 못함 |

- 상태는 `PENDING` / `PASS` / `NOT_APPLICABLE`뿐. N/A는 **40자 이상 구체적 사유 + 해당 기능의 정책 검토 원본 근거**를 요구한다. 모든 USER/OPTION 항목을 무조건 시즌 전수 인증 Gate로 만드는 것은 금지. 그렇지만 실제로 일반화가 필요한 기능을 무증거 N/A로 처리해서도 안 된다.
- 단일 JSON의 `policy.next_review`가 다음 판정 항목을 소유한다. A4·A5·A6의 `generic`이 미검토이면 A7을 다음 완료 항목으로 표기하거나 A7 `PASS`를 선언할 수 없다. A4~A6의 각 소스 자체에서 이미 관측된 일반화 증거를 평가하고 부족한 경우 **그 항목의 최소 변화 테스트만** 보완한다.
- **요소 COMPLETE = generic + current_source + product_integration 세 축이 각 기능의 실제 적용 범위에서 PASS(또는 원본 정책으로 입증된 N/A)**. 역사 PASS는 완료 산식에 포함하지 않는다. **제품 전체 COMPLETE = 78개의 유효한 요소 COMPLETE + 별도 엄격 ZERO-SOURCE→USER-E2E 실제 실행 영수증**. 신규 `full_product_e2e=PASS`는 모든 항목 완료 및 E2E 증거 없이는 차단.
- 한 근거를 다른 요소에 붙여 완료시키지 못하도록 **근거 키의 `supports` ID와 기록된 테스트 SHA·GitHub Actions 실행 링크·노트**를 함께 검증한다. 원본의 진위를 자동으로 검증했다는 뜻은 아니므로 PASS 승격 시 실제 Actions/Native 영수증을 **별도 읽기**로 확인해야 한다.

## 실제 개발자가 따라야 할 매 항목 절차

1. 현재 사용 범위·시즌·선택 기능·대표 프로필의 **수락 조건** 확인 → 기존 캐시·GitHub Actions·Native evidence 재사용.
2. 해당 항목의 `generic/current_source/product_integration`을 **모두 점검**. 근거가 없으면 `PENDING`, 적용 불필요면 구체적 정책 N/A. 하나만 PASS인데 전체 READY로 표현하지 않는다.
3. 반드시 **기능 ID에 정확히 귀속된 원본 SHA·실 실행 링크·변형 회귀**를 JSON 근거에 연결하고, 기존 상세 추적표·generated 표와 일치시키며 테스트.
4. 아래 명령이 통과해야만 판정 커밋을 유효하다고 보고 다음 ID 진행. FAIL인데 문서에서 완료 선언하거나 테스트를 회피해서는 안 된다.
5. 불필요한 Wago 대용량 재다운로드·전 전문화 Native·새 gate 프레임워크를 만들지 말고 코드 변경이 실제 무효화한 것만 시험. A7 이후 같은 원칙.

```bash
python integration_probes/v401_completion_contract_gate.py --write
python integration_probes/v401_completion_contract_gate.py --check
python -m unittest discover -s tests -p test_v401_completion_contract_gate.py -v
```

[GitHub Actions](../../.github/workflows/p1_v401_completion_contract_policy_gate.yml)은 격리 개발 브랜치의 **매 push**에 대해 검증·부정 테스트를 실행하고 해당 커밋에 결과를 게시한다. **CI 실패가 GitHub push/사용자 주도권을 물리적으로 차단하는 것은 아니다.** 별도 사용자 승인 없이 main 보호 정책/병합 권한을 변경하거나 정식 출시 권한을 부여하지 않는다. 이 검증은 **증거 주장 간의 정합성 검사**이지 실제 API/SimC 시험을 대신하지 않는다.

## 소유권·인계

- 현재 실제 개발 정본: `probe/chat-cache-v035-20261024`. `main` 병합·v003 immutable·Project Sources/Instructions UI 적용·공식 Work OS/승격은 별도 사용자 승인 사항이다.
- 새 채팅은 **이 정책 → JSON → 생성 상태표 → 상세 추적표 → 변경 노트 → 테스트/실제 영수증** 순으로 읽는다. 이전 인계의 과거 카운트보다 최신 기계 판독 PASS 축을 우선한다.
- 같은 시즌 정적 캐시와 실 원본 영수증은 유효조건 내 재사용하고, SimC revision 변경만으로 전부 폐기하지 않는다. 제품 목적은 **26 DPS의 미래 절대 CHMV 최적 rating**이며, 일반 장비 전체 사용자 선택/전 시즌 아이템 DB/장비 조합 추천으로 확대하지 않는다.
