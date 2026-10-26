# SIMC SECONDARY OPTIMIZER — 제품 설계 정책 보충 / 지속 개발 기준 (2026-10-25)

> **HISTORICAL / SUPERSEDED — DO NOT TREAT AS CURRENT USER POLICY.** The following is a dated working document preserved for evidence. Its old v1.0/v1.2 precedence, O-outside-T or efficacy-gate statements are superseded by user's approved v1.3 `T=G+J+F+O`/95%-only design and 2026-10-26 target-level farming-goal clarification. The user's v1.4 Source replacement and Instructions are **prepared for manual UI application**, not asserted applied. Current product meaning and next P1: [CURRENT_PRODUCT_PURPOSE_AND_USER_ENTRY_20261026.md](./CURRENT_PRODUCT_PURPOSE_AND_USER_ENTRY_20261026.md). Moving development state: [CURRENT_PRODUCT_DEVELOPMENT_STATE.md](./CURRENT_PRODUCT_DEVELOPMENT_STATE.md).

> **문서 신분:** 사용자 승인 발언에 근거한 정책 보충안을 개발 브랜치에 **기록**한 것. Project Sources의 `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.0.md`를 수정하거나 v1.1 CANDIDATE 전체를 승인·승격한 것이 아니다. 공식 Project Instructions/Sources 적용은 MAIN 승인 계약에 따라 별도 수행·영수증이 필요하다.
>
> **사용 중인 대화는 그대로 진행한다.** 이 문서는 채팅 전환 요청이 아니라, 개발 중 계속 갱신하고 향후 어느 일반 채팅에서도 동일한 기준을 읽기 위한 지속 상태 문서다.

## A. 사용자 확인 사항 — 적용 방향

1. **최종 목적:** 목표 아이템레벨(기본 334) 또는 명시 총량에 따른 치명·가속·특화·유연 **절대 rating**을 SimulationCraft DPS로 최적화하고, 통계적 오차 및 실질적으로 다른 근접 성능 대안을 제공. 장비 추천·파밍·장비 조합 최적화로 확장하지 않는다. 탱커·힐러까지 모든 전문화의 목적함수는 DPS.
2. **SimC의 책임:** 아이템의 발동·사용 효과, 장식 효과, 특수보석 효과, 전문화 APL, 전투 DPS 등 SimC가 이미 담당하는 게임 모델링을 우리 코드가 중복 구현하거나 별도 재현·지원 인증 Gate로 확장하지 않는다. 선택한 `item_id`, `ilevel`, 정확한 옵션과 전투 설정을 SimC에 전달하고 SimC 결과를 이용한다. SimC 자체 실행 오류는 기록·노출하지만 개별 발동 효과를 자체 계산해 교정하지 않는다.
3. **우리 코드의 책임:** 대표 장비 구성, 입력/부위 충돌 검사, 정적 CHMV 총량 `G`/일반보석 `J`/영약 `F`, 고정 스탯 하한과 자유분배량, 후보 생성, 실제 JSON2의 **요청한 정적 rating·최종 rating 정합성** 및 DPS·표준오차 파싱, 탐색·캐시·재개를 관리. 이 수치 정합성 검사는 효과 메커니즘 검증이 아니다.
4. **장신구:** 사용자 선택 **2개**를 고정. 고정 2차 스탯은 최적화 예산 `G` 밖이고 SimC 계산에는 포함. 정적 스탯 JSON2 레코드가 없어도 선택/SimC 실행을 막지 않는다. 누락 레코드를 '0 스탯 검증'으로 승격하지 않는다. 예: Mindpiercer's Sigil(`250224`)은 실 SimC 실행 성공(v056). Permafrost Essence(`250244`)는 기본 후보에서 제외 가능하되 사용자가 ID로 명시 선택하면 통과시킬 수 있다.
5. **제작장비:** 천·가죽·사슬·판금 방어구와 제작 무기/방패/공용 장비를 대표 프로필의 **장식 2개 부착 기반**으로 지원. 제작 시 선택하는 두 2차 스탯의 50:50 초기 배분은 자유분배 최적화에서 고정 하한이 아니며, 부위·레벨별 총량의 Native 정적 스탯을 기준으로 한다. **실제 선택한 장식 두 개는 탐색 동안 변경하지 않는다.** 별도 장비 조합 최적화를 하지 않는다. 현재 51개 소스 확인 ID는 전체 레시피의 완전 목록이 아니며 사용자가 그 밖의 실제 ID를 명시해도 허용한다.
6. **정적 아이템 캐시:** 같은 시즌, item ID, ilvl, 부위, 옵션/bonus 등의 변형 정체성으로 보관. SimC revision만 달라졌다는 이유로 보관된 같은 시즌 정적 스탯을 일괄 폐기하지 않는다. 신규 아이템·새 변형을 증분 추가. 기존 정적 수치 충돌은 **사용자 요청에 따른 명시 교정**이 필요하며 자동 덮어쓰기하지 않는다. 출처/Native 관측값과 수동 교정 이력을 구분.
7. **DPS 결과 캐시:** 정적 캐시와 달리 SimC 바이너리/데이터·APL·캐릭터·장비/효과 선택·소모품·전투 조건·rating 후보·iterations/실행 옵션에 종속. 다른 시나리오 사이 무단 재사용 금지.
8. **무거운 부가기능 금지:** 기존 기능 보존 + 경량·고속화, 일괄 처리/중복 제거, 실행 상한, 실패 시 증거 보존, 중단·재개. 완전한 시즌 장비 DB나 특수효과 내부 해석은 목표가 아니다.

## B. v1.0과의 차이·충돌을 숨기지 않음

| 항목 | 공식 v1.0 | 후속 발언/이번 정리 | 처리 |
|---|---|---|---|
| 장비 효과 지원 검증 | 4.3~4.6, 15장에 지원·효과 검증 문구 | **효과별 자체 인증/구현 Gate를 만들지 말고 SimC 신뢰** | 보충 정책으로 기록. 공식 조항 변경은 MAIN 적용 절차 |
| 기본 CHMV 합계 | `T = G + J + F`; J=138, 샘플 F=165 | v059의 `O=32` 포함 T=3184는 **프로필 한정 실험** | 공식 기본식을 바꾸지 않는다. v1.1 기름 정책과 충돌 보고 상태 |
| 제작 스탯 | 표준 대표 장비의 개별 배분 자유 | 제작 통상 50:50 초기 배분은 **고정 floor가 아님** | 사용자의 명시 방향 기록 |
| 장신구 미보고 정적 수치 | 장신구 CHMV는 G 밖, SimC 실행 | 정적 레코드 누락이면 선택 차단 **금지** | 명시 보충 |
| 아이템 캐시 정책 | v1.0은 DPS 후보 캐시만 명시 | 시즌 정적 아이템 캐시와 버전 민감 DPS 캐시 **분리** | 명시 보충 |
| v1.1 CANDIDATE | 공식 승격 전 | 일부 사용자 결정 반영하지만 기름·효과 사전 검증 문구 존재 | **전체 문서 자동 승격 금지** |

`v016_SCENARIO_CONTRACT`는 사용자 보고 기준 최신 원본 제품 개발 상태이지만 **원본 바이트·테스트 영수증을 이 GitHub branch에서 독립 확인하지 못했다.** v059는 그 대체품이나 v016 후속 제품 승격물이 아니다.

## C. 증거로 확인된 현재 개발 상태 (v059)

- 격리 repo: `degong2-code/simc-secondary-optimizer-runner`, branch `probe/chat-cache-v035-20261024`.
- [v059 Native 2후보 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40157655114): 258 tests = 256 pass + 2 skip, 334 비전 마법사 2개 CHMV 후보의 실제 적용 rating 일치·DPS·SEM 수집. **전역 최적해/자동 적응형 제품 완성이 아니라 2후보 평가 연결부 검증**.
- [v056 장신구 실 SimC PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40155908015): 정적 gear JSON2 누락에도 250224 선택·실행 성공.
- [v058 단일 제작장비 Native 지연 조회 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40156636301): 누락한 239652 ilvl 331 `crafted_stats=49/36` 정적 CHMV 198, 단 1회 조회.
- [v057 51개 제작 레시피 목록/회귀 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40156264178): 실제 레시피 링크 기반 메타데이터. 시즌 모든 제작 아이템이 확보됐다는 뜻 아님.
- 수집된 스냅샷: 아이템 목록 455 ID / Native 정적 변형 1,759건(기존 병합 영수증 기준). **이 브랜치 코드나 source만으로 실제 제품 통합을 증명하지 않음**.
- `v059` 파일: `runner/v059_candidate_runner_bridge.py`, `tests/test_v059_candidate_runner_bridge.py`; SimC 효과 구현 코드는 없음.

## D. 원본 제품·운영 권한 분리

- 공식 개발자 기준 `Developer_Notes_v1.0.md`, 보호된 v003 immutable 패키지를 변경하지 않는다.
- 제품 공식 보고 최신 `v016_SCENARIO_CONTRACT`와 시험 브랜치 v059의 **개발 계보를 구분**한다.
- **제품 일반 시험**과 **Work OS M0 운영환경 Gate**는 별개. 공식 Work OS M0가 미실행/미통과라도 기존 제품 코드를 폐기하거나 일반 제품 시험을 금지하지 않는다.
- MAIN은 Project Instructions, Project Sources, CURRENT, Shared State 및 공식 운영상태/승격 결정을 통제. WORK는 증거·환경 관리 지원. 별도 사용자 승인 없이 소유권 변경·MAIN 정책/공유상태 임의 승격·WEQUIP 런타임 종속성을 만들지 않는다.
- 사용자 명시 승인이 있는 주 제품 개발 채팅의 일반 SimC 시험에 별도 MAIN 승인을 반복 요구하지 않는다.

## E. 지속 유지 방식

1. **현재 채팅에서 개발 계속**. 새 채팅 시작은 사용자가 결정할 때만 한다.
2. 개발 버전마다 변경된 구현·실측 PASS/FAIL·원본 SHA/Actions run 및 미해결을 **현행 개발 기록**에 추가한다.
3. 새 채팅에서도 이 기준과 소스/검증 경로를 확인하도록 준비하지만 **채팅 이동을 다음 작업의 전제조건으로 만들지 않는다**.
4. Project Instructions/Sources의 실제 적용을 할 수 없는 환경에서는 '적용 완료'라고 하지 않는다. MAIN 적용 요청과 검증된 공식 반영을 구별한다.

**이 문서는 개발 브랜치의 지속 정책 보충본이며, 사용자 승인한 v1.0 전체를 대체하지 않는다.**
