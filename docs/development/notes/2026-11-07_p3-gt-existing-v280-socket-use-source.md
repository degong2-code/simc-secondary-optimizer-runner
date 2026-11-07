# 2026-11-07 · P3-GT · 기존 v280 소켓 아이템 원본 재사용

- **Capability:** `SOURCE.SEAL`, `ENVIRONMENT.WEB`
- **Keywords:** P3-GT, J bonus sockets, v280, v190, same-build ItemEffect, on-use SpellID, future five sockets, no extra collection
- **Prior evidence:** [P3-GQ 실 T1 #42332836316](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42332836316): G=2850, 선택 영약 F=165, J 5개 기본 소켓 미달, 원본 Native 3회. [P3-GS focused #42335310176](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42335310176) stage 비교 수정 이후 360 PASS/2 SKIP; J 새 Native0. 현재 `collect_wago_new_season_source`는 `v280` ItemXItemEffect+ItemEffect 동일 빌드 joined stage를 이미 수집/봉인함.
- **Decision:** `CONNECT` 추가 소켓의 후보 아이템·on-use SpellID를 추적할 때 별도 신규 DB·HTTP나 효과 분석을 만들지 않고 기존 `v280` *sealed source*를 재사용한다. 이름에 Jewelbinder가 있다고 시즌·사용 가능한 부위를 **확인한 것으로 취급하지 않는다**. 실제 시즌 2 공용 웹 자료의 Miasmic Jewelbinder `275707`/Spell `1297709`는 source candidate identification context이지 엔진의 hardcoded current-season ID/최종 효과 인증이 아니다. 같은 expansion에 이전 시즌 보석구멍 추가 아이템도 있을 수 있어 여러 후보를 무단 단일 선택하지 않는다.
- **Changes:** `v216._existing_v280_season_socket_item_source`가 원래 v280 source stage/동일 빌드/파일 경로·SHA identity의 **이미 봉인된** item-use 관계 중 이름/실 on-use SpellID에 적합한 Jewelbinder 후보만 진단에 투영한다. 후보마다 물리 ItemID, 영문명, 관측 use SpellID, 원본 SHA 기록. 기존 미래 목표 5소켓 계획에서만 호출, original v232 count/기존 J added-slot PENDING 판정은 변경하지 않는다. T1 compact receipt에 새로운 후보 진단을 포함한다.
- **Verification:** 새 focused offline 검증 후 영수증 기재. 실 시즌 외부 source fetch/Native 재실행 0.
- **Remaining:** 확인된 현재 시즌 Jewelbinder item↔on-use Spell source와 실제 시즌 2 적용 슬롯/사용 조건을 연결해 J 추가 소켓을 승인하는 것이 아직 필요. 기존 v280 소스 범위에 아이템이 없으면 `NO_MATCH_IN_EXISTING_V280_CONSUMABLE_SCOPE`으로 보류하고 같은 시즌 Wago Item/ItemSparse 기존 snapshot 범위를 우선 재사용한다. 원본 J 고정치 및 최종 B/T·READY 미완료.
- **Efficiency:** 기존 Wago snapshot/v254 ItemXItemEffect/v280 ItemEffect 단계와 임시 저장 캐시 재활용, 신규 HTTP0, 신규 Native0, 신규 아이템 효과 엔진0, 별도 시즌 전체 DB 구축0. main/v003/Project UI/Work OS/기존 주 제품 채팅 권한 변경 없음.
