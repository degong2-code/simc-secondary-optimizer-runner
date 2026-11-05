# 2026-11-05 · P3-EI · 기존 봉인 보석 ItemSparse/GemProperty 속성을 시즌 입력에 직접 연결

- **Capability:** `J.GEM`, `SOCKET.LAYOUT`, `ENVIRONMENT.WEB`, `SOURCE.SEAL`
- **Keywords:** P3-EI, v221, v266, v268, v271, v216, v098, gem_property_id, color_mask, minimum_ilevel, special gem, one special
- **Prior evidence:** [PROTOCOL](../PROTOCOL.md) → [INDEX](../INDEX.md) → [P3-ED](2026-11-05_p3-ed-v221-source-gems-mandatory-special-preview.md), [P3-EA](2026-11-05_p3-ea-v266-raw-gem-rating-normal-build-bridge.md), [P3-BX](2026-11-03_p3-bx-simc-socket-native-contrast.md). 기존 v221 봉인 원본은 item ID→GemProperty ID, enchant ID, color_mask, minimum_ilevel, expansion_id를 이미 정확 관계로 관측. v268/v216 이후는 ID 존재만 전달해 v098 시즌 입력에서 이 자료를 잃음.
- **Decision:** `CONNECT` (REUSE 포함) — v268이 이미 수행한 봉인된 v221 JSON/CSV 1회 읽기에서 **선택된 최대64개 ID의 물리 원본 필드만** v216→v098에 원본 속성 형태로 투영. 새로운 보석 목록/API/Native/게임 효과 엔진/인증 Gate는 `STOP`. color_mask·minimum_ilevel은 정확 source 필드이지 **필수 특수1 역할 인증, 최고 품질, 인게임 소켓 합법성**은 아님. SimC Native가 임의 gem_id를 받아도 socket은 입증되지 않는 P3-BX 실 증거 존중.
- **Changes:** `v268.view` source join에서 source-only property rows, unresolved/complete 상태 반환; `v216.preflight`는 같은 봉인 ID/정렬/값의 구조 정합만 검사해 `selected_v221_gem_item_relation_unadmitted`에 포함; `v098._season_settings_from_v216`이 동일 관계의 별도 season input에 전달하고 target ilevel 대비 source min 상태를 **관측**으로 표시. 구 4색/정확 특수1/v271 레이아웃, 이전 SHA, 사용자·DPS 캐시 변경 없음.
- **Verification:** `tests/test_v266_v268_gem_enchant_source_reuse.py`와 `tests/test_v287_zero_history_v222_user_budget_bridge.py` 오프라인 회귀 추가. **신규 실행 NOT_RUN/NOT_VERIFIED**, 역사 P3-ED CI 243 PASS(범위 한정) 및 P3-BX Native 4/4 재사용. 신규 Wago HTTP·SimC Native 0.
- **Remaining:** 정확 특수 유형·최고품질·실 소켓, SimC-effective J, G/F/선택O, 실제 Policy A 발행, v212 Environment READY/T1은 미완료. 이 연결은 기존 원본 정보를 다음 입력의 동일 구조로 보존한 것이며 공식 선택지 등록이 아님.
- **Efficiency:** 신규 CSV/Native/HTTP 요청 0. 기존 v268 1회 source join의 선택 최대64건만 전달하며 v217 SHA/원본·현 cache identity 보존. main/v003/v016/Project UI/Work OS·주제품 개발권한 불변.
