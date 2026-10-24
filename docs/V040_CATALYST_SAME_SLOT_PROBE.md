# v040 — 한밤 시즌 2 촉매 변환 아이템의 스탯·효과·티어 귀속 Native 검증

## 검증 질문

`Venomkeeper's Horrific Cowl` (원본 `271874`, 334) → 마법사 티어 머리(`271564`)로 촉매 변환한 후, **원본 특화 +201 + 티어 4세트 + 특수효과**가 하나의 머리 장비에서 유지되는가?

- 공식 고정 SimC 커밋 `7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd`의 `engine/item/item.cpp`에서 `redirected_base_stats`를 파싱하고 `parsed_item_data_t::init`에서 리다이렉트된 아이템의 스탯 배열을 복사하는 소스 구현이 확인됨.
- 같은 커밋의 `profiles/MID2/MID2_Mage_Arcane.simc`는 `head=...id=271564,bonus_id=13335/13668/13846/13848,ilevel=344,...,redirected_base_stats=271874`를 공식적으로 사용. 단, **344 아이템 레벨·보너스 목록은 334로 무검증 복사하지 않음**.
- v039는 원본 머리 271874의 bare 특화 201, tier gloves 교체로 4세트, 특수효과 버프 관측 PASS. **원래 머리 티어 1부위와 원본 특수효과가 동시에 적용되는 촉매 표현은 아직 Native 미검증**.

## v040 개발 계약

1. `minimal_334`: `head=crown_of_the_primal_leywarden,id=271564,ilevel=334,source=local,redirected_base_stats=271874`.
2. `bonus_13846_334`: 위 334 입력에 `bonus_id=13846` 한 가지만 추가. 이것은 공식 SimC 프로필에서 출처를 확인한 **진단용 옵션**이며 실제 게임의 334 촉매 보너스 ID가 검증됐다는 뜻이 아님.
3. 두 경우 기존의 일반 장갑 `268243`을 유지하고 어깨·가슴·다리 티어를 유지해 총 4세트. 기본 치명타 룬, 단일 대상 300초 60 iterations를 적용.
4. JSON2에서 **head=271564** + `redirected_base_stats=271874` + 원본 특화 201, `cumulative_power`, `rune_of_critical_power`, `venomcursed_mastery` 버프를 각각 확인한다.
5. 특수효과 발동 수치와 감소되는 타 스탯의 크기는 이 짧은 버프 존재 검증만으로 확정하지 않는다.
6. 옵션이 인식돼도 실제 게임에서의 정확한 변환 bonus ID, 아이템레벨, 보석홈 유지, 일반 장비·효과 스케일링은 별도 검증해야 한다. DPS는 비교하지 않음.
7. v032 원본·main 제품 코드·Work OS M0·Developer Notes 변경이나 승격 금지. 기존 v035 동일 브랜치의 SHA 검증된 Linux SimC 캐시 HIT일 때만 **Native 최대 2회**, 캐시 MISS 시 재빌드 없이 차단.

## 사후 검증

Native run ID, 원본 input/JSON2 SHA256, 장비 ID·총량, stat floor, 4pc·특수 버프·고정 리비전, 오류·잔여 게이트를 Artifact 영수증에 남긴다. 결론의 단계는 `PASS`, `PARTIAL` 또는 `BLOCKED`로 구분한다. 테스트 브랜치 외 공식 Work OS 상태를 자동 변경하지 않는다.
