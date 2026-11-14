> **v441 최신 사용자 결정 — 78요소 검증 엄격도·실사용 필수성 재평가:** [78개 개별 수락 조건 감사](78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md)를 정본 JSON의 `acceptance`/추적표에 반영했다. **총 78개 검토, 54개 조건 범위 축소/명료화, 24개 유지**, PASS 상태는 종전 7/78·축별 18/18/7/12에서 **단 한 건도 자동 승격하지 않았다**. 공통 사용자 E2E·Actions·Native는 사용 범위가 일치할 때 여러 요소에 공동 귀속한다. 시즌 독립 RUN의 `current_source`는 실제 불필요한 경우에만 해당 축의 **정책 증거·구체 사유가 있는 NOT_APPLICABLE**을 허용한다(무조건 RUN N/A가 아님). 필수 G/J/F/O·L/E/O·JSON2 정합은 유지. [v441 개발 노트](notes/2026-11-14_p1-v441-78-acceptance-necessity-relaxation.md).

> **v409 사용자 결정 — A8 간소화:** 게임 빌드와 SimC 내부 빌드 번호의 일치나 SimC 소스→실행 바이너리 컴파일 계보 인증은 필수 Gate가 아니다. 실제 SimC 버전·SHA는 DPS 캐시를 분리하는 메타데이터로 기록한다. 기존 `V106_USER_RESULT.json`/`V291_RESULT.json` 결과를 저장·표시하며 조회 시 SimC 재실행을 요구하지 않는다. 시즌 G/J/F/O 원본 수치·선택 조건·오류 처리는 유지한다. 78축의 미완료 상태는 과장하지 않되 별도 A8 인증을 제품 P1 통합의 선행 Gate로 삼지 않는다. [변경 노트](notes/2026-11-13_p1-v409-a8-simc-metadata-and-result-snapshot-policy.md).

> **v405 최신 진행 규칙:** [A7 실제 원본 ZERO-SOURCE + 변경 시즌/빌드 regression](notes/2026-11-13_p1-v405-a7-automated-current-source-selection-verified.md)으로 `generic/current_source=PASS`일 때만 `next_review=A8`을 허용하도록 [v401 validator](../../integration_probes/v401_completion_contract_gate.py)와 부정 테스트를 개정. **A7 product_integration=PENDING**은 사라지지 않고 78개 요소 COMPLETE/전체 E2E를 차단한다. A8 검토는 미완료 downstream user→SimC 통합의 승인이나 완료가 아님. [정책 CI #43376626773](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43376626773) **16 PASS**.

# 78개 요소 완료 계약: 정책이 실제 진행을 통제하는 최소 강제 절차 (v401)

> 2026-11-13 사용자 직접 승인: **반복 지적 없이**, 어떤 ChatGPT 채팅에서 개발하더라도 범용성·현재 시즌 원본·사용자 제품 통합을 **누락·혼동·성급히 PASS 선언하지 못하도록** 구조화 데이터/자동 회귀/단일 완료 판정 절차를 유지한다. 78개 Native 재실행, 전 품목 인증, 새 제품 엔진, 미래 미출시 시즌의 실측 선행 Gate를 만들지 않는다.

## 단일 상태 정본과 읽기용 파일

1. **상태·수락 조건의 기계 판독 정본:** [`78_ELEMENT_COMPLETION_CONTRACTS.json`](78_ELEMENT_COMPLETION_CONTRACTS.json). A1~H6 정확히 78개, ID·요소명·BASE/USER/RUN/OPTION·원래 수락 조건 + 4개 독립 판정 축, 해당 항목에만 귀속되는 근거 ID, 원본 테스트 SHA/Actions/노트 경로를 갖는다.
2. **사람이 보는 상태표:** [`78_ELEMENT_STATUS_GENERATED.md`](78_ELEMENT_STATUS_GENERATED.md). JSON에서 결정론적으로 생성. `python integration_probes/v401_completion_contract_gate.py --write`로 갱신하며 **직접 수정 금지**.
3. **78개 상세 감사·과거 맥락:** [기존 78개 항목 추적표](ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md)는 **인수 조건 및 작업 메모의 역사·세부 문서**로 유지한다. 다만 상태값을 독자적으로 승격할 권한은 없다. CI가 78개 모두 JSON 상태와 표 마지막 칸의 `ENGINE_*/READY_SCOPED/PENDING_SCOPE`가 정확히 대응하는지 검사한다. 기존 보고문에 남은 구 시점 진척은 **자동 생성 표가 우선**한다.

## 4개 독립 축 (완료 수준을 한 열로 혼합하지 않는다)

| 축 | PASS의 뜻 / 필수 증거 | 다른 축 대체 여부 |
|---|---|---|
| `generic` | 시즌 원본 수집·자동 구축 기능은 현재 실제 ZERO-SOURCE + 출처/시즌 변경 회귀. 시즌 독립 RUN 산술·통계·캐시는 결정론적 입력·오류 회귀 및 기존 실제 사용자/Native 경계 증거를 재사용. 기능별 새 시즌/Native 전수 재실행 금지 | 현재 원본이 실제로 필요하면 해당 축 별도 확인. 필요하지 않은 RUN만 증빙된 N/A 허용 |
| `current_source` | 실제 소비하는 현재 시즌 원본·ID·G/J/F/O·SHA를 해당 범위에서 확인. 시즌 독립 RUN은 기존의 실제 관측/동일 소비 경계 증거를 공유하고, 진정 불필요할 때에만 설명·정책 근거를 붙여 N/A | 현재 원본의 정합성이 필요한 항목을 포괄 N/A로 대체 금지 |
| `product_integration` | 사용자 입력→예산/프로필→SimC→결과의 해당 요소 소비와 실패 경계. **같은 실제 E2E 영수증이 여러 ID를 직접 검증하면 공동 사용**. 선택하지 않은 옵션은 그 옵션만 보류 | 단순 코드 존재/합성 PASS만으로 실 제품 증거 대신하지 않음 |
| `historical` | 특정 과거 빌드·프로필·옵션의 실제 영수증. 완료 계산의 필수 축 아님 | 과거 성공을 다른 시즌·변형의 실제 성공으로 확대 금지 |

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
