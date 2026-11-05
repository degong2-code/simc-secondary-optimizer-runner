# 2026-11-05 · P3-FI · 특수보석 1개 필수 정책 재확인

- **Capability:** `J.GEM`, `SOCKET.LAYOUT`
- **Keywords:** P3-FI, special gem mandatory, exactly one, nominal J, v271, v139, v098
- **Prior evidence:** [P3-EC](2026-11-05_p3-ec-exactly-one-special-gem-policy-correction.md)에서 특수보석 1개 필수 계약을 복구했고, [P3-EZ](2026-11-05_p3-ez-jf-numeric-policy.md)에서 J는 일반보석 N개 명목 rating 합계로 분리했다. P3-FH의 '일반보석만 장착하는 기본 경로'는 잘못된 제안이다.
- **Decision:** `REUSE` 기존 특수 1개 + 일반 N개 장착 계약. `STOP` 특수보석 없는 기본 장착 경로.
- **Changes:** 기존 코드 동작 변경 없이 현재 INDEX와 상태 문서의 오판을 후속 교정한다. 기본 환경의 '특수 선택 장비 없음'과 '필수 특수보석 없음'을 혼동하지 않는다.
- **Verification:** 기존 P3-EC focused 240 PASS 및 P3-FH 268 PASS는 역사 영수증이며 이 정책 자체의 새 Native 결과가 아니다. 이 문서 작성은 새 Native/HTTP 호출 없이 수행한다.
- **Remaining:** 새 시즌의 정확한 특수보석 ItemID 1개와 최고 관측 일반보석 N개의 소켓 배치를 원본에서 자동 결정하여 기존 v271→v139/v098에 연결. 실 신규 시즌 READY/T1 미실증.
- **Efficiency:** 새 효과 엔진·소켓 엔진·J 실효 측정 Gate 없이 v221/v266/v230/v232와 v271을 재사용. 격리 브랜치만 수정, main·Project UI·공식 승격은 불변.
