# v038 — 선택 특수효과 장비 CHMV 고정 하한: 증거 인수·후보 제약

**상태 (2026-10-24):** v038 제한적 구현 및 증거-우선 검증. **실제 시즌 특수효과 장비의 정적 CHMV 추출 완료·범용 제품 적용 PASS가 아님.**

## 설계 기준과 구분

- 공식 설계: `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.0.md` §4.4·4.5·5.5·5.6, §13.3. 주 목적은 장비 추천이 아니라 **최종 CHMV rating 절댓값** 최적화.
- 참고용 2026-10-23 `CHMV_FIXED_FLOOR_AND_INJECTION_ADDENDUM`의 `L + x + o` 수식은 분석에 유용하지만 **v1.1 Candidate를 공식 승인으로 승격하지 않는다**.
- `L`: **선택한 장신구 외 특수효과 장비의 재분배 불가 정적 CHMV**. 이미 장비 예산 `G` 안에 포함됨. `o`: 현재 대표 시나리오 고정 무기 기름 `(16,16,0,0)`으로 총량 안에 포함. `E`: 장신구·마법부여 등 별도 외부 고정 스탯으로 자유 예산 `T`에 **더하지 않음**.
- 따라서 수동 총량 `T`를 유지하고 `c_i ≥ max(수동최소_i, L_i + o_i)`, `Σc=T`로 탐색한다. 가용 재분배량 `U=T−ΣL−Σo`. `L`·`o`를 **총량에 추가하면 중복 가산**이다.
- `v037`의 50% 스탯별 상한은 시험용 제약. 하한이나 총량과 충돌하면 차단.

## 발견 사항: 기존 v037 장비 JSON2로는 특별 고정값 확정 불가

`v031r3_dwarf_arcane_fixed_gear` 대표 프로필의 `wrists=239648` 및 `back=239656`은 장식이 달린 제작 부위이고 `crafted_stats=49/36`을 지정한다. 이 부위의 네이티브 장비 스탯이 보이더라도 **그 값을 고정 특수효과 장비 L로 잠그지 않는다.** 장신구는 일반 CHMV 자유풀에서 분리한다. 일반 장비·보석·영약·장식 제작스탯 분포도 고정하지 않는다.

증거에 없는 특수장비 목록을 자동으로 생성하지 않으며, **실제 선택 아이템 ID/슬롯/아이템레벨 및 특수효과 분류는 외부의 명시적 검토가 필요**하다. 신뢰할 수 있는 원본 확인이 없으면 `VERIFIED_SELECTION_REQUIRED` 또는 `MISSING_INDEPENDENT_BARE_ITEM_JSON2`로 차단한다.

## v038 구현

- `runner/v038_fixed_gear_floor.py`: JSON2 `report_version=2.0.0`, SimC 고정 리비전, 선택 item ID·slot·ilevel, 보강 요소 제거된 bare item encoded 속성, 원본 JSON2 SHA256 및 CHMV 정적 벡터 검사. `gem_id`, `enchant`, `crafted_stats`, 기계적으로 중복/불명확한 아이템 증거는 거부. 실패는 명시적인 `BLOCKED` 영수증.
- `collect_verified_floor`: 검토자가 명시한 특수장비 목록과 **별도 수집된 베어아이템 JSON2**를 결합. 단, 자기 서술 필드만으로 사용자가 실제 그 장비를 선택했다거나 효과가 SimC에서 제대로 구현됐음을 증명하지는 않는다. 영수증의 `actual_user_selection_independently_verified_by_tool` 및 `nonstat_item_effects_verified`는 `false`.
- `enforce_constraints`: 수동 하한, 선택 특수장비 하한 및 기름 하한을 분리하여 계산. 총량 증감 및 외부 장신구 스탯 유입 금지.
- `check_candidate` / `pinned_native_result`: 후보 생성 전·실제 Native JSON2 이후 각각 동일한 CHMV 총량과 하한 충족 여부 확인.
- `runner/v038_native_floor_probe.py`: **가상 특수장비 하한 `(150,0,100,0)` TEST_ONLY**을 사용하여 v037+원본 v032의 Native 인젝션이 하한을 지키는지 실제 시험하는 단일 SimC 호출 어댑터. `synthetic_special_item_fixture_only:true`; 실존 아이템 자동추출 PASS 아님.

## 검증 단계와 게이트

1. v038 독립 계약/보안/경계 오프라인 회귀검사 실행. 특별 아이템 미선정·증거 미보유 상황이 `BLOCKED`인지 확인.
2. 기존 v033+v037 테스트 보존 및 v035 Linux 바이너리 SHA `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e` 동일 캐시 **HIT인 경우에만**, 120 iterations **1회** 시험. 캐시 MISS면 재컴파일하지 않고 거부.
3. Native 후보 JSON2에서 CHMV 합계 3284, 고정 하한 `(166,16,100,0)`, 기름, 기본 치명타 룬 및 원본 v032 정합성 검사. 후보 1개 계산으로 전역 최적성을 주장하지 않음.
4. **추후 실제 선택 특수장비가 주어지면:** Native bare item fixture를 독립 생성·적용 범위 확인 → SHA 기록 → 선택 목록·실제 아이템 효과 검증 → 신규 고정 하한 산출 → 기존 구성 전체 스탯/비정적 효과 및 4세트 보존을 Native JSON2로 대조. 그전에는 실사용 `L` 미검증.

## 변경 경계

- 원본 v032 모듈 17개, v036 브리지 원본, v037 어댑터, `main`의 v033 워크플로, Project Sources/Instructions/CURRENT/Shared State, 공식 Work OS M0, 불변 v003 **변경 금지**.
- `probe/chat-cache-v035-20261024` 시험 브랜치에 v038 **추가 파일만** 기록. 기존 캐시를 재사용하는 구체적인 시험 브랜치 범위 외에는 캐시 HIT를 보장하지 않는다.
- 민감정보·개인경로·비인가 원본 전체 ZIP을 GitHub에 업로드하지 않는다. 임시 전달 파일은 작업 뒤 삭제한다.

---

## 2026-10-24 Native 결과: 가상 하한 시험만 PASS

- [GitHub Actions #40104213001](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40104213001): SUCCESS; Runner 로그 약 8.7초; v035 캐시 HIT, C++ 재컴파일 없음.
- 기존 16 + v037 29 + v038 37 = **오프라인 82/82 PASS**. v038 계약 테스트에는 선택 아이템 누락, 누락된 독립 bare-item JSON2, 아이템 ID·레벨 불일치, crafted_stats·gem_id, 장신구 제외, 후보 하한 침범이 포함됨.
- 가상 L=(150,0,100,0)과 기름 o=(16,16,0,0), 수동 T=3284 ⇒ 최소=(166,16,100,0), 자유분배 U=3002. **실제 특수효과 장비의 L로 승격 불가**.
- 고정 하한을 적용한 단일 Native 후보 CHMV=(619,1176,1150,339), **JSON2 스탯별 정확히 일치**, 120 iterations 요청/실제 DPS 샘플 119, DPS 198771.0013, 95% 근사 ±1782.516. 치명타 옴니움 룬 버프 확인.
- Artifact ID 12563816884, ZIP 파일 크기 82475 bytes, SHA256 4dd48b6e35e9bd3ab3ff9842d47a16dae63ede5993e8ef4a1f226c1d2d6e08c2, 8개 entry 전부 ZIP CRC PASS.
- 기존 v037 Native JSON2 실측에서 back=239656은 crafted_stats로 거부, wrists=239648은 gem_id로 거부, trinket1/2는 최적화 하한 원천에서 제외하도록 실제 코드를 실행해 확인.
- [독립 검증 영수증](V038_FIXED_FLOOR_NATIVE_ACCEPTANCE_20261024.json)은 synthetic=true·real_item_attested=false·actual_special_effects_proven=false를 보존.
- **남은 게이트:** 사용자 선택 실존 특수효과 장비의 식별·효과 지원 증거 및 보강하지 않은 순수 네이티브 아이템 스탯 JSON2 확보 후 동일 계약에 투입. 현재 해당 데이터가 없어 실사용 자동 고정 하한 산정은 미완료.
