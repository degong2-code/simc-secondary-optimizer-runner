# v445 — B10 실제 Native 소켓 파서 대비의 역사 증거 귀속

- **Capability:** `SOCKET.LAYOUT`, `J.GEM`, `GEAR.SEASON`, `PRODUCT.E2E`
- **Keywords:** v445, B10, v270, socket, gem_id, 13750, v232 intrinsic, v271 declared full, physical source, 70783
- **Prior evidence:** [P3-BX 실제 v270 Native4 기록](2026-11-03_p3-bx-simc-socket-native-contrast.md), [v270 Actions #41601140696](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696), [P3-GZ 실제 5gem 사례](2026-11-08_p3-gz-pinned-simc-gem5-real-native.md), [v417 현재 사용자 E2E](2026-11-13_p1-v417-bounded-post-bridge-product-e2e-once.md).
- **Decision:** `REUSE`/`PARTIAL` — 물리/선언 소켓의 실제 SimC 파서 대비를 B10 historical 축에만 수락. 다른 필수 3축은 PENDING. 78 완료나 현재 원본 인증으로 승격하지 않는다.
- **Changes:** 코드·Native 실행·새 Gate 없음. v401 78 JSON의 B10 과거 증거, 상태표/추적표/INDEX/검증 회귀만 갱신. next_review B10 유지.
- **Verification:** v270 실제 Actions #41601140696 SUCCESS, 4/4 JSON2 Native/exit0, tested SHA a35d58431f59afb6247648df8d201a0113415f76. SimC 실제 보너스 ID 13750의 가슴/어깨 처리와 bonus 없이 gem_id만 넣은 무소켓 가슴에서 Crit+16/Haste+8 모두 관측. 이 관측은 소켓 허용 여부와 별개임을 확인. 현재 변경 자체는 78 v401 Actions 검사 이후 판정.
- **Remaining:** v216 기존 코드가 v232 봉인 intrinsic count와 v271 가상/선언 socket count를 구분하고 `additional_socket_proof_required_by_slot` 및 `J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING`을 출력한다. 다만 해당 아이템·빌드의 실제 추가 소켓 허용 부위 및 source→v212/J→v098 제품 소비 검증은 없음. SimC Native의 gem 적용 결과로 인게임 장비 소켓 적법성을 주장하지 않는다. B10 generic/current_source/product PENDING.
- **Efficiency:** 신규 Native0/API0/DB2 0. 기존 소스·영수증·캐시 재사용, 필요할 때만 실제 사용자 선택/추가 슬롯 원본을 좁게 검증. 주 제품 권한, main/v003/Project UI/v016 미변경.
