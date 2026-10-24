# v039 — 실존 특수효과 장비 Native 순수 스탯 검증 (별도 시험)

**실행 대상(시험용, 사용자 착용/선택 인증 아님):** Venomkeeper's Horrific Cowl, item ID `271874`, 머리/천, 목표 아이템레벨 `334`.

**공개 자료:** [Wowhead item ID 271874](https://www.wowhead.com/item=271874/venomkeepers-horrific-cowl?ilvl=334)에서 아이템레벨 334의 특화 201 rating과 특수효과를 확인한다. 이 웹 표시 숫자를 실측으로 간주하지 않고 고정 SimC 소스 `7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd` 바이너리의 **실제 JSON2 장비 데이터**를 독립 확인한다.

## 엄격한 시험 경계

1. 오리지널 v031r3 참고 프로필의 `head` 한 줄과 **옴니움 4번째 룬(가속→기본 치명타)**만 `head=venomkeepers_horrific_cowl,id=271874,ilevel=334,source=local`로 교체한다. 해당 장비에 `bonus_id`, `gem_id`, `enchant`, `crafted_stats`를 넣지 않는다. 다른 장비/특성/룬/소모품 변경 금지.
2. **머리는 원래 티어4셋 구성 중 하나**다. 이 단일 교체 시험은 **티어4셋 보존 검증이 아니다**. DPS를 기존 v038 기준과 비교하거나 최적화 후보로 사용하지 않는다.
3. 60 iterations **최대 1회**, 동일 SHA256의 v035 캐시 바이너리만 사용. 캐시 없음/파일 무결성 실패 시 재컴파일 금지, `BLOCKED`.
4. 출력 JSON2에서 271874/334, head에 보석/마법부여/제작변형 없음, 고유 특화 201 rating, 나머지 고정 CHMV 0, 다른 세 티어 부위 ID 보존, 캐릭터/룬 출처를 검증한다. 이 검증은 **정적 아이템 스탯**에 한정한다.
5. **비정적 발동 효과 구현·프로크량·장비 티어 세트 보존·CHMV 총량 재산정**은 별도 시험이 필요하다. 아이템의 정적 스탯은 이미 목표 장비 예산에 포함되어야 하므로 추가로 더하지 않는다. 지금 당장 `L=(0,0,201,0)`을 실제 제품 하한으로 승격하지 않는다.
6. 실제 사용자가 이 아이템을 선택했다고 기록하지 않는다. 사용자 직접 선택이 필요한 제품 입력 계약은 유지한다.

## 후속 검사

- 옵션이 있는 실제 아이템 표현(`bonus_id` 등)에서 발동 효과가 활성화되는지 SimC JSON2 버프·통계·로그로 검사.
- 원래 티어4셋이 빠지지 않도록 정식 티어 변환 혹은 다른 4번째 티어 부위를 별도로 검증해 구성. 자동 카탈리스트 효과 보존은 **실제 SimC 증거 없이 추정 금지**.
- 실제 부위 치환으로 인해 달라지는 장비 `G` 총량, 장비 주능력치, 정적 CHMV 하한, 보석 장착 수, tier 세트와 효과를 모두 재검산한 후에만 같은 제품 시나리오로 사용.

**제품 범위:** 승인된 Developer Notes v1.0 유지. 장비 추천, 장비 탐색 DB, 공식 Work OS M0, main 제품 승격은 이 게이트 범위 밖.

---

## Native verification outcomes

**Test item:** Venomkeeper's Horrific Cowl, item ID `271874`, cloth head, level `334` (development trial, not user's asserted gear selection).

- Native bare head: [Run 40106250971](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40106250971) PASS. Native item stats crit 0/haste 0/**mastery 201**/versatility 0. Crit Omnium rune present, but original head tier was displaced and 4pc `cumulative_power` was absent. This is an intentionally invalid configuration for DPS comparison.
- Native head with effect options and alternative tier gloves `271565`: [Run 40106614938](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40106614938) PASS. Head mastery **201**, mage tier gloves native haste **50** + mastery **101**, original shoulder/chest/legs retained, `cumulative_power` present. Crit rune remained active.
- The actual pinned SimC JSON2 buff `venomcursed_mastery` (spell 1307922) appeared with mean start count **7** and reported uptime **35.9402**. This proves the native effect buff *appeared in combat simulation*, not that the gain/loss rating magnitudes, item-level scaling or full DPS correctness have been independently established.
- The official SimC MID2 item profile's bonus list introduced `avoidance_rating=86` on the head in the equipped effect variant. This tertiary stat is not part of CHMV optimization; compare only the **bare** item +201 static mastery for the fixed CHMV floor.
- Offline test suite **97 run, 2 skipped** and GitHub Actions cache HIT, native binary SHA `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`. Native JSON2 and ZIP CRC independently checked.
- The first Run 40105954234 used the old reference **haste rune**; its scope error was corrected and the accepted bare item proof is Run 40106250971. Historical run preserved, not presented as default-crit valid.
- Accepted machine receipt: [V039_REAL_CANTRIP_NATIVE_ACCEPTANCE.json](V039_REAL_CANTRIP_NATIVE_ACCEPTANCE.json).
- **Remaining:** recompute representative-gear budget `G` and total CHMV after *both* head and gloves replacement; verify the whole Venomcursed dynamic stat gain/loss effect; verify per-slot special item options and consequences for gem/tier/primary budget; retain external user-selected equipment contract.
- These runs do **not** prove a global CHMV optimum, cross-spec readiness, or official Work OS M0.
