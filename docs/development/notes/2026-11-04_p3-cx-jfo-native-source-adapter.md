# 2026-11-04 · P3-CX · 기존 J/F/O 정적 관측의 단일 v216 Build 연결

- **Capability:** `J.GEM`, `F.FLASK`, `O.OIL`, `BUDGET.GJFO`, `PRODUCT.E2E`
- **Keywords:** P3-CX, J, F, O, v271, v281, v278, v216, zero-history, sealed ItemID, native source-only, no admission, quality, fixed hand
- **Prior evidence:** [PROTOCOL](../PROTOCOL.md)→[INDEX](../INDEX.md)→[P3-CA](2026-11-03_p3-ca-physical-gems-j-normal-build.md) 물리 소켓 ID J 계산, [P3-CQ](2026-11-04_p3-cq-item-id-native-binding.md) v281 정확 ID→v278, [P3-CO](2026-11-04_p3-co-actual-flask-oil-native.md)/[P3-CP](2026-11-04_p3-cp-quality-phoenix-oil-native.md) 제한된 실 Native; [P3-CW](2026-11-04_p3-cw-v277-g-to-preprofile.md) 동일 Build G→v222. 역사 1pt·J 보석 원본/SimC 차이는 미해결이며 조사·재실측은 새 사용자 논의 전 보류.
- **Decision:** `CONNECT` — 원래 v216에 들어온 `v271` 물리 보석 ID·rating의 **미승인 산술**과 `v281` exact ItemID·품질·손→`v278` Native의 **미승인 정적 변화량**을 한 Build source-only 출력에 연결; 새 인증 Gate/효과 알고리즘·실 Native/HTTP 없음.
- **Changes:** zero-history internal `gem_layout_receipt`/`gem_rating_by_id`를 원본 preflight·v271에 전달하고 collector에는 전달하지 않음. 기존 v222 budget J와 다르면 차단, J만 있으면 숫자 후보만 반환. F/O는 기존 v281 sealed exact item/SimC identity·v278 Native receipt SHA를 이용해 **아이템별** 후보와 누락 근거를 기록; flask 여러 품질과 양손 oil을 합치거나 최고품질 선정하지 않음. 정적 0/비정적 pending은 O=0 처리하지 않음. UI·정식 F/O/B/T·세션 변경 없음.
- **Verification:** 이번 코드 변경의 offline focused/Actions는 **NOT_VERIFIED**(GitHub CI 영수증 확인 후 갱신). 신규 synthetic source-only 7개(보석 ID/J·J 불일치, 영약 F, 기름 O, 비정적 pending, token drift, legacy token-only 격리) 및 역사 [P3-CW 182 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41747763755) 재사용. 신규 Native0·게임 HTTP0.
- **Remaining:** 실제 해당 시즌 G/J/F/O 공식 원본 인증 및 제품 예산 소유권, 보석 소켓 합법성·J +1 차이, 영약 품질 동일효과/동일조건, 기름 물리 손·무기 ilvl 및 정적/조건부 구분은 미해결. 사실 검증을 위한 새 조사·실측은 사용자와 먼저 상의. 검증 후 `v222→Policy A→v098→v094` E2E 연결.
- **Efficiency:** 원래 v216 preflight/v271/v281/v278 반환 JSON 소형 증거를 일회 소비, 별도 Native·HTTP·소스 스캔·B/T 계산기·캐시 재구축 없음. main/immutable v003/원본 v016/Project UI/Work OS 불변.
