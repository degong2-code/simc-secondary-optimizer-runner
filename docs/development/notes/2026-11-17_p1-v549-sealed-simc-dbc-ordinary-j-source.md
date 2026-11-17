# 2026-11-17 · v549 · 동일 시즌 SimC DBC 일반보석 J 숫자 원본 재사용

## 목표와 기존 자산

- 제품 목표: **목표 ilvl/수동 T에 따른 26 DPS의 CHMV 최적 절대 rating**. J는 실제 선택한 검증된 일반보석에 따른 고정 예산. 보석 효과와 DPS는 SimC 책임.
- 역사적 실제 증거: `12.1.5.70783`의 `v221` 보석 물리 관계 75건, `v266` Wago raw `EffectPointsMin` 정적 0/미관측75건, 그러나 SimC `v269`+v343/v524에서 기본 4보석 **J92**가 해당 빌드 조건에서 확인돼 v212 설치 성공. raw 0은 보석 rating 0이 아님.
- 선행 기능: `v546`은 v221 ID→v230 sealed item quality 메타데이터를 연결(미승인); `v547`은 v269 한 보석 전후 JSON2 델타를 기존 v278 Native receipt/cache로 실행(미승인); `v548`은 정확히 4개 효과군일 때만 제한적으로 Native 실행(미승인). **이전 기록을 신규 시즌 자동 J 최종 해결로 해석하지 말 것.**

## 이번 최소 변경

- 신규 수집기/효과 재구현 없이 **이미 존재하는** `v275` pinned `spell_item_enchantment.inc` 및 `v211.load_fresh_sources/parse_dbc_rows`, `v296.from_v275/extract`를 보석에도 재사용. 기존 v296 파서는 동일 빌드·SimC revision·원본 Git blob/SHA, exact enchant ID, 정적 비스케일 ITEM_ENCHANTMENT_STAT만 처리. 복합/조건/스케일 효과는 숫자 대신 PENDING.
- `v216._fresh_pinned_dbc_ordinary_gem_j_source`는 원래 v221 물리 ID/마부 관계와 v230 제작품질을 재사용한다. 같은 주스탯 선두 + 다른 보조스탯 조합/색상·최소레벨·확장팩·품질·DBC item level 조건을 분리한다. 4개의 명확한 2보조스탯 후보군이 없으면 PENDING; 각 계열에서 이미 관측한 최고 제작품질의 각 CHMV 수치가 다른 관측 등급보다 열등하면 PENDING. **원본 미확정 후보가 별도 존재할 수 있으므로 높은 등급을 전 세계/시즌 최고 품질로 인증하지 않음.**
- 소비: `v216` default auto4 분기는 **동일 시즌 검증 nominal → 기존 v268 관측 raw → 새 pinned SimC DBC static → 기존 제한적 v269/v278 Native fallback** 우선순위. 최종 조건 충족 시 `v271.ordinary_four_stat_default`와 기존 `gem_rating_by_id`, preflight 미승인 산술 입력만 반환. `source_compilation.four_stat_pinned_dbc_j_source_unadmitted`에는 원본 SHA·상태·미확정 수치가 남음.
- **미구현·미승격**: 신규 시즌 실 DBC 수치확인, 75개 중 정확한 4계열 실제 선별, 최고 품질과 동일 효과/사용조건의 완전한 정책 A 증거, 실제 선택 소켓, 원본 J 수치의 공식 v216 J/F owner 인정 및 v222/v212 설치, 26 DPS USER E2E. static DBC + 명목 J 계산 성공만으로 공식 승인하지 않는다. 기본 70783 packaged J92 정상 설치를 강제로 새 경로에 태우지 않음.
- 효율: same-build 기존 `v275` sealed files를 1회 판독(추가 Wago/Native 0), raw exact coverage만 선택해 전체 시즌 아이템 DB/Native 전수 반복 없음, 불확실하면 캐시 유지·PENDING. 기존 `v217` stage 및 v278 per-profile Native cache/실패 재실행 방지는 불변. 기존 static 시즌 캐시를 SimC revision만으로 전면 폐기하는 정책 없음.

## 검증·실패 교정

- 첫 `4b3b3cd6`: 합성 DBC Python 시험의 literal `\\n` 사용으로 원본 v211 파서가 `SIMC_ITEM_ENCHANTMENT_TARGET_COVERAGE_MISMATCH`를 정확하게 보고. 실제 제품 로직 결함을 입증한 것이 아니라 합성 시험 문자열 문제. `c487c3f2`에서 줄바꿈 교정.
- 두 번째 `c487c3f2`: **미관측 낮은 제작 등급**이 있어도 상위 등급 4종 정적 rating 후보는 산술로 관측되고 품질/공식 J는 PENDING이라는 기존 로직에 반하는 시험 기대값 1건을 `6318dad6`에서 정정. 두 최초 Actions의 실패 기록은 역사로 보존하며 성공으로 덮어쓰지 않는다.
- `6318dad6`의 [v212 Ubuntu/Windows #44020245712](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44020245712) 500건 496 PASS·4 SKIP·0 FAIL, 신규 함수/원본 v296 실제 파서 합성 fixture 통과.
- 최종 normal Build 연결 `c8813e69`: [v212 #44020375095](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44020375095) Windows·Ubuntu 500건 496 PASS·4 SKIP·0 FAIL, [reusable #44020375096](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44020375096) 679건 677 PASS·2 SKIP·0 FAIL. [v113 #44020375088](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44020375088), [v182 #44020375273](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44020375273), [v181 #44020375100](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44020375100), [v401 #44020375094](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44020375094) 모두 SUCCESS.
- 검증은 **synthetic offline/no Native/no Wago**. 실제 70783 v524를 재실행하지 않았고 신규 실 시즌 DBC를 이 채팅에서 수집하거나 parser 통합 Native로 확인하지 않았다. 예전 v524 Actions artifact는 작은 source-owner 영수증이며 생성된 전체 `spell_item_enchantment.inc`를 포함하지 않아, 이번 경로에 대해 새 실수치 확인으로 주장할 수 없다.

## 다음 결손

1. 실제 환경 Build의 동일 시즌 seal된 DBC에서 v296가 4개 명확한 2-stat effect family를 내는지 **기존 증거/캐시에서 우선 검사**. 보유 원본이 없으면 부족한 정확 범위만 수집.
2. 4계열이 불확실할 때는 효과/조건/품질 원본을 먼저 좁히고 필요한 한 보석만 기존 v269/v278로 관측; raw/mixed/special 보석 전수 Native 금지.
3. 정확한 보석 ID·효과 동등·최고 품질/소켓 권한이 검증된 *같은 사용 범위*에서만 기존 `v216 J/F owner → v222 B/T → v212`를 소비/자동 등록. 70783 기본 J92 및 과거 캐시/Native 재사용.
4. 공식 78 원장 **15/78 COMPLETE**, `full_product_e2e=PENDING`. Main/immutable/v016/Project UI·공식 승격 권한 변경 불가. 개발 중 GPT는 사용 가능하나 제품 runtime에는 AI/LLM 호출 0.
