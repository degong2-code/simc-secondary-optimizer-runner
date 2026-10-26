# Project Instructions — 추가 반영 제안 (MAIN 공식 적용 대기)

> **HISTORICAL / SUPERSEDED — DO NOT TREAT AS CURRENT USER POLICY.** The following is a dated working document preserved for evidence. Its old v1.0/v1.2 precedence, O-outside-T or efficacy-gate statements are superseded by user's approved v1.3 `T=G+J+F+O`/95%-only design and 2026-10-26 target-level farming-goal clarification. The user's v1.4 Source replacement and Instructions are **prepared for manual UI application**, not asserted applied. Current product meaning and next P1: [CURRENT_PRODUCT_PURPOSE_AND_USER_ENTRY_20261026.md](./CURRENT_PRODUCT_PURPOSE_AND_USER_ENTRY_20261026.md). Moving development state: [CURRENT_PRODUCT_DEVELOPMENT_STATE.md](./CURRENT_PRODUCT_DEVELOPMENT_STATE.md).

> **상태: PROPOSED / NOT APPLIED.** 아래는 기존 SSfindout Project Instructions의 SIMC SECONDARY OPTIMIZER 항목 끝에 보충하기 위한 **정확한 문구**다. 이 GitHub 문서가 존재한다는 사실은 ChatGPT Project Instructions/Sources의 설정 변경을 뜻하지 않는다. 공식 변경은 기존 MAIN 사용자 승인·검증·기록 절차에서만 수행한다. 기존 지침/Developer Notes v1.0를 삭제하거나 아래 내용으로 대체하지 않는다.

## 삽입할 텍스트

### SIMC SECONDARY OPTIMIZER — 지속 개발 정책 보충

- 공식 제품 설계 기준은 Project Sources의 `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.0.md`이다. 후속 사용자 명시 결정은 문서의 기존 조항과 충돌 여부를 보고·구분하여 기록한다. `v1.1_CANDIDATE`는 사용자 승인 없이 전부 승격하지 않는다.
- **SimC가 직접 처리하는 아이템·장신구·장식·보석 효과, APL 및 DPS 메커니즘을 재구현하거나 선행 효과 인증 Gate를 도입하지 않는다.** 정확한 아이템 ID/레벨/옵션과 전투 조건을 전달하고 SimC 실행 결과를 그대로 이용한다. 제품 책임 범위는 입력·정적 CHMV 예산/고정 하한·자유분배·중복 가산 방지·결과 rating 정합성·DPS 통계 비교에 한정한다. SimC 실행 자체가 실패하면 오류를 기록하되 자체 발동 효과 분석으로 확장하지 않는다.
- 고정 2차 스탯을 제공하는 장신구도 **CHMV 최적화 G 예산 밖**이며 SimC 프로필에 포함한다. JSON2 정적 장비 레코드가 없어도 선택을 막지 않고, 누락 수치를 검증된 0으로 오인하지 않는다. 예: `Mindpiercer's Sigil` (250224).
- 제작장비는 천/가죽/사슬/판금 방어구와 무기 등 사용자가 **장식 2개를 고정 선택·장착**할 수 있는 대표 프로필 수단이다. 2차 스탯의 초기 50:50 배분은 고정 최소 하한이 아니며 전체 정적 CHMV 예산을 최적화한다. 모든 제작 레시피를 수집해야 기능을 시작할 수 있는 것은 아니며 정확한 수동 ID 입력도 허용한다. 장비 조합 추천이나 장비 DB 전체 수집을 새 목표로 추가하지 않는다.
- **정적 장비 캐시**는 시즌+item_id+ilevel+slot+옵션을 기준으로, SimC 버전만 바뀌었다고 자동 폐기하지 않는다. 같은 시즌 기존 장비 수치 수정은 사용자 요청에 따른 명시 교정으로 관리하고 새 아이템/레벨/옵션은 증분 추가한다. 반면 **DPS 결과 캐시**는 SimC 바이너리/데이터, 캐릭터·특성/APL, 장비·소모품, 전투 조건, CHMV 후보·반복 횟수에 종속되므로 버전·조건별 격리한다.
- 공식 v1.0의 CHMV 예산식 `T=G+J+F`를 사용자 새 승인 없이 바꾸지 않는다. 기존 `v059`의 기름 +32를 포함한 T=3184는 **한정 실험 조건**이지 범용 제품 정책 확정 증거가 아니다.
- 제품 개발 최신 사용자 보고는 `v016_SCENARIO_CONTRACT`. v015~v016의 실제 원본 파일/실행 영수증 검증 없이 GitHub 시험 브랜치 `v059`를 원본 제품 통합 완료로 표시하지 않는다. GitHub 시험 브랜치는 독립 개발/실험 도구다.
- 개발 중 상태는 `degong2-code/simc-secondary-optimizer-runner`의 `probe/chat-cache-v035-20261024` 브랜치 `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md`와 별도 증거에서 최신 HEAD/Actions를 확인한다. **현재 진행 중인 일반채팅에서 개발을 계속한다.** 지속 문서의 '향후 다른 채팅에서도 복원 가능'은 당장 채팅을 바꾸라는 지시가 아니다.
- Work OS 공식 M0는 운영환경 Gate이고 일반 제품 개발/시험의 금지 사유가 아니다. MAIN/WORK 권한 분리, Developer Notes v1.0 및 기존 v003 immutable 보호, CURRENT/Shared State/Project Instructions/Project Sources 변경·승격의 MAIN 승인 절차를 유지한다. WEQUIP 런타임 authority·지속 의존성을 도입하지 않는다.
- 코드 변경마다 중복 계산 제거, 캐시 재사용, SimC 실행 횟수 상한, 경량화, 통계 신뢰도, 재개 가능성과 회귀검사 증거를 함께 검토한다.

## 적용 절차/판정

1. MAIN이 기존 지침과 중복·충돌을 먼저 검토한다.
2. **정책 변경이 아니라 현재 사용자 승인 결정의 반영인지** 확인한다. 기름 O 정책 등 미승인 부분은 후보로 둔다.
3. 공식 Project Instructions/Project Sources에 문구를 실제 반영하고 적용 전/후 및 승인 영수증을 남긴다.
4. 그때만 상태를 `APPLIED_MAIN_CONFIRMED`로 표시한다.

**현재 판정:** `DRAFT_STAGED_BRANCH_ONLY`. 공식 반영 영수증 없음. 이 사실이 현재 채팅에서의 격리 개발 진행을 차단하지 않는다.
