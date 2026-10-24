# v041 — 촉매 변환 장비의 기존 머리 보석 및 특수효과 증거 검증

**상태:** 사전 시험. 2026-10-25. 제품 정책 승격·Work OS 공식 M0 실행과 무관.

## 기준

- 승인된 Developer Notes v1.0 유지: CHMV T=G+J+F, 선택 특수장비의 고정 CHMV 잠금, 티어 4세트, 중복 적용 차단. v1.1/v1.2 미승격 후보의 예산 공식 변경을 자동 수용하지 않는다.
- v040 기존 결과는 `271564` 티어 머리 + `redirected_base_stats=271874` 에서 **특화 +201, 4세트**와 `bonus_id=13846` 추가 후 발동 `venomcursed_mastery`를 보였으나 `gem_id=240967`을 누락했다. 따라서 기존 장비의 전체 보석/효과 보존 실증은 부족했다.
- 고정 SimC C++의 `unique_gear_midnight.cpp`는 Venomcursed 두 효과를 `effectN(1)`과 `effectN(2)`의 양·음수 스탯 증감으로 구현한다. 다만 실측 scaling과 실제 게임과의 parity는 여전히 미입증.
- [WoWHead의 334레벨 원본 271874](https://www.wowhead.com/ptr/item=271874/venomkeepers-horrific-cowl?bonus=6652:13696:13662:13334:13846:12854)에는 `bonus_id=13846`과 발동 효과 표기가 함께 있어 **원본 아이템의 보너스 후보**로 검토 가능하지만, 변환된 **334레벨 티어 장비에 적용된 게임 실측 bonus 리스트는 미확보**.

## v041 고정 시험

- 기존 대표 비전 마법사·334레벨 장비 구성에서 머리 **한 부위만** 교체. 기존 일반 장갑 `268243` 및 어깨·가슴·다리 티어 유지.
- 머리: 티어 ID `271564`, 원본 ID `271874`, `ilevel=334`, `bonus_id=13846`, `redirected_base_stats=271874`, **기존 `gem_id=240967`을 보존**. 원본 코드/시스템 정책은 수정하지 않음.
- 기본 치명타 룬 유지. 60 iterations SimC **1회**만 허용, 기존 v035 Cache HIT와 바이너리 SHA256 검증 실패 시 컴파일 없이 STOP.
- Native JSON2에서 ① 실제 티어 ID/원본 ID/334/보너스 ID, ② 머리 `gem_id=240967` 인코딩, ③ 고정 특화 201, ④ `cumulative_power`, ⑤ `rune_of_critical_power`, ⑥ `venomcursed_mastery` 발동을 모두 확인하는 경우에만 제한 PASS.

## 차단 및 미검증

- 보석 ID의 JSON2 보존만으로 소켓 수와 장착 가능성 또는 보석의 모든 메커니즘이 실게임에 부합한다고 주장하지 않는다.
- `13846`의 게임 측 촉매 변환 결과 본인증, 완전 발동 스탯량(예상 334: 특화+363 기타 -60), 정상 아이템레벨별 scaling, 장비 기반 G/T 재산정, 장식 및 보석 예산 유효성은 별도 게이트.
- `201`은 기존 장비 내 재분배 불가 고정 특화이며 예산에 **더해서 증가시키는 보너스가 아님**. 기존 총량 3184나 수동 3284를 자동으로 새 장비의 실제 총량으로 승격하지 않는다.
- 본 시험에서 DPS 우열·전역 최적화·실제 사용자 아이템 선택을 주장하지 않는다.

---

## 실제 GitHub Native 2026-10-25 결과

- [GitHub Actions #40112424280](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40112424280): SUCCESS; **132 tests 중 130 PASS·2 SKIP**, 캐시 HIT, SHA256 pin 검증, Node24 cache/restore@v5, **Native 1/1**. 전체 Runner 작업 약 8초.
- JSON2 확인: `head=271564`, `redirected_base_stats=271874`, `ilevel=334`, `bonus_id=13846`, **`gem_id=240967`**, 고정 특화 **+201**, 티어 `cumulative_power`, 치명타 룬 `rune_of_critical_power` 유지. 기존 일반 장갑 `268243` 유지.
- `venomcursed_mastery` 발동 시작 평균 **7.3729**, 보고된 uptime **40.5667%**, 샘플 **59회**. 이는 로그 관측이지 효과 스탯량 scaling 정확도 실증이나 DPS 우위 입증이 아니다.
- 독립 검증: GitHub Artifact ID `12566764251` 전체 **7 files CRC PASS**, ZIP SHA256 `bfd4043596ae722ad96fb94007cdd2388a97530f8c0c602f59e59140429b9598`, 입력 SHA256 `8519a926322103a6e263e3bd250ecc213d05ca359d9b56519a0146403c4aecfb`, JSON2 SHA256 `44802458c6606549664d8699b6f35766b76d9fed1af0d7498db0a9b0e1d30a1f`.
- [독립 기계판독 영수증](V041_INDEPENDENT_ACCEPTANCE.json)에서 실게임 보너스 ID 귀속, 보석 메커니즘 전체, 실제 G/T 예산, 발동 스탯 증감량, DPS 비교는 전부 **미검증**으로 남김.
