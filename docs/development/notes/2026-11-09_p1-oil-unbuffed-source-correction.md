# P1 · 기름 O 원본 정적 rating 교정 (2026-11-09)

## 사용자 결정과 원인
- 과거 냉기 마법사 buffed JSON2 관측 `치명+16/가속+17`은 냉법 특성에 의한 오염 가능성이 지적된 자료이며 **기름의 공식 정적 O로 재사용 금지**.
- 이전 관측 영수증은 역사로만 보존. 과거 자료 일치 여부를 별도 필수 Gate로 만들지 않음.
- 원본 시즌 SimC DBC의 직접 정적 값만 해당 범위에서 사용. SimC 소스의 scaling이 필요한 수치는 임의 16/16으로 추정하지 않음.

## 실제 코드·검증
- `runner/v296_pinned_oil_static_rating_source.py`: 이미 봉인된 `v275` `spell_item_enchantment.inc`를 읽고 `v211` 원본 파서를 재사용. 특성/버프가 섞인 v278 JSON2 관측과 독립된 후보 `static_CHMV_vector`를 산출; 스케일링·혼합 효과는 보류. `v281` 물리 아이템과는 ID·손·출처 일치 조건에서만 연결하며 등록은 별도 미완료.
- `tests/test_v296_pinned_oil_static_rating_source.py`에서 정적 16/16 예시와 오염된 16/17 관측을 구별. **이 합성 16/16은 70783 실 원본의 최종 확정 O가 아님.**
- `894d76950577`에서 변경된 scaled-ID 처리와 시험 fixture가 불일치해 focused FAIL(512 중 1 FAIL/1 ERROR). 후속 `bb8de1b3caf2`에서 실제 스케일링 필드에 맞게 테스트만 교정. [focused #42579722294](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42579722294) **510 PASS / 2 SKIP / 0 FAIL, DEV_LEDGER_PASS**, 신규 Native0.
- 실제 [70783 unbuffed 원본 #42577642495](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42577642495) PASS. [별도 SimC 정적 보고 #42578223479](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42578223479) PASS. 이 두 범위 증거가 전체 O>0 시즌 자동 설치·사용자 선택·DPS PASS를 의미하지 않음.

## 남은 P1
현재 `v296`의 결과는 **미승격 후보**. 원본 스케일링에 대한 SimC 자체 계산값, 정확한 물리 ID·적용 손/무기·최고 품질·CHMV 예산 소유권을 확인한 선택지만 기존 `v216→v222→v212→v113→v098/v096` 경로로 등록해야 함. 필수 O 미확정 항목은 보류하고 O=0 정상 환경을 차단하지 않음. 기존 사용자 수동 T·캐시/취소/재개 보존, 추가 Native 전수 반복 금지.

격리 브랜치만 변경. main, v003 immutable, Project UI, Work OS, 주 제품 개발 채팅 소유권 불변.
