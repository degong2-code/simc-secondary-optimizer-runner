# 2026-11-05 · P3-EC · 특수 보석 정확히 1개 필수: P3-EB 오류 교정

- **Capability:** `J.GEM`, `SOCKET.LAYOUT`, `PRODUCT.E2E`, `DEV.CONTINUITY`
- **Keywords:** P3-EC, special gem, 특수 보석, exactly one, required, mandatory, 정책 정정, P3-EB 회귀, v271, v139, v098, v216, v222
- **Prior evidence:** 최신 사용자 직접 결정 **“특수 보석 하나는 무조건 필수 사항”**이 최상위 기준. [PROTOCOL](../PROTOCOL.md)→[INDEX](../INDEX.md)→[P3-BZ](2026-11-03_p3-bz-variable-socket-physical-gems-connect.md) 원래 v271은 특수 보석 정확히 1개 + 일반 보석 N개, [P3-DK](2026-11-04_p3-dk-v271-variable-socket-v098-bridge.md) 원래 v139/v098 가변 소켓 source-only 연결, [P3-EA](2026-11-05_p3-ea-v266-raw-gem-rating-normal-build-bridge.md) v221/v266 raw J 연결. [P3-EB](2026-11-05_p3-eb-optional-special-gem-core-j.md)는 특수 보석의 **종류 선택 가능**을 **생략 가능**으로 잘못 판단한 역사 실패 기록. `v061`의 nullable generic field는 새 제품에서 필수 장착 정책을 완화하는 근거가 아님.
- **Decision:** `REUSE` — P3-EB만 도입한 `special_gem_id=None,special_slot=None` 허용 **철회**. 현재 기본 사용자 시즌 목표에서는 **특수 보석이 정확히 하나** 있어야 함. 종류·ID/효과·장착 소켓은 동일 시즌 검증에 따라 선택 가능하되, 생략하는 선택지는 지원하지 않음. 기존 v271 필수 1개 계약/역사 240983·240967 4색 로직 재사용; 미래 시즌 특수 보석 후보 전체를 역사 ID 두 개로 제한하는 정책은 아님.
- **Changes:** 제품 3파일 `v271/v139/v098`과 기존 `v287` 회귀를 P3-EA 검증된 원본 bytes로 복귀. P3-EB의 다이아 없음 프로필 경로 제거. 기존 `v271` 다이아 정확히 1개·일반 보석 개수/추가 다이아 차단을 확인하는 별도 회귀 1개만 추가. P3-EA raw J 연결, G/F/O Native opt-in, 취소/재개/캐시/기존 사용자 프로필 및 메인 소유권 변화 없음.
- **Verification:** 새 회귀 및 원래 v271/v139/v098/v216 집중 계약, v113 웹, Windows와 DEV_LEDGER 검사. 코드/Actions 후 영수증 갱신 전 `NOT_VERIFIED`. P3-EB focused 최종 242 PASS는 **오류 설계 구현의 당시 테스트 통과**이지 정정된 필수 정책 준수 증거가 아님. Native/외부 게임 HTTP 추가 0.
- **Remaining:** 새 시즌 특수 보석 **정확한 아이템 ID·품질·효과/소켓 부위** 및 일반 보석 최고 품질/J·소켓 게임 내 적법성·정확한 G/F/O, 검증된 v222 공식 B/T→v220/196 Policy A 선택지→v212 READY 설치/T1 미완료. 이 정정은 특수 보석을 역사 ID로 고정하지 않으며 자동 시즌 옵션 발견은 별도 남은 구현.
- **Efficiency:** P3-EB 부정확 분기만 되돌려 기존 보석/프로필 엔진을 직접 재사용. 신규 원본 수집·Native·효과 구현·캐시 폐기·세션 수정 없음. 격리 브랜치 한정, main/v003/v016/Project Sources UI/Work OS/주 제품 개발 소유권 불변.
