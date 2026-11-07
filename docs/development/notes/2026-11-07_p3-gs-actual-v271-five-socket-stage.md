# 2026-11-07 · P3-GS · 기본 3소켓과 목표 5소켓 배치 대조 교정

- **Capability:** `SOURCE.SEAL`, `ENVIRONMENT.WEB`
- **Keywords:** P3-GS, J, v232, v271, 3 sockets, 5 sockets, nominal J, future target, source-only
- **Prior evidence:** [P3-GQ real #42332836316](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42332836316) G native source 2850, selected F +165, J original intrinsic socket 5 미달. [P3-GR focused #42333487323](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42333487323) 357 PASS/2 SKIP은 미래 후보 계획 산술만 검증했고 실제 `v271.arrange`→`v216` 배치 경로를 검증하지 않음.
- **Decision:** `CONNECT` 미래 목표 5소켓 배치의 개수는 배치 후보 `proposed`와 비교해야 하고, 원래 `v232` intrinsic 개수는 downstream `_fresh_selected_J_intrinsic_socket_source`에서 별도로 보존·대조해야 함. 사용자 승인 없는 소켓 추가 item/use 인증 또는 J/READY 승격은 하지 않는다.
- **Changes:** `v216._fresh_default_intrinsic_gem_layout_from_source`의 마지막 count check에서 `sum(counts)`를 `sum(proposed)`로 교정. 구전 소켓을 v232 원본에 덮어쓰지 않고 `v271`에는 가상 슬롯이 존재함을 표시, 기존 J source owner가 extra 슬롯을 보고 `J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING`으로 분리. 신규 focused test는 **seal된 synthetic v232 candidate→3 intrinsic+2 extra→one special+4 ordinary physical gems→J 추가 소켓 미승인**을 한 번에 실행하며 원래 legacy 3 socket·거짓 위치·카운트 조작도 확인.
- **Verification:** 집중 오프라인 CI/ledger 실제 결과로 판정; 신규 실 Native·게임 HTTP 0. 과거 3 Native audit 영수증 유지.
- **Remaining:** 시즌 socket item 및 use 조건 원본(기존 v280 item spell source)을 J의 extra slot 범위에 연결하고 검증해야 J와 v212 설치 가능. 선택한 일반보석 4종의 nominal J도 현재 아직 공식 아님.
- **Efficiency:** 수정은 값 비교 2곳과 scoped 회귀 하나. Native/G/F 재측정0, source 재수집0, 효과 시뮬레이터0. 격리 외 branch/main/immutable/Project UI/Work OS/기존 주 제품 소유권 불변.
