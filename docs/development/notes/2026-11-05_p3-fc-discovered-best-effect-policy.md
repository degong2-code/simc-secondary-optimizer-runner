# 2026-11-05 · P3-FC · 동일 효과군의 발견된 최고 수치와 최소 입력 적합성

- **Capability:** `J.GEM`, `F.FLASK`, `ENVIRONMENT.WEB`
- **Keywords:** P3-FC, discovered strongest, observed quality, nominal J, SimC F, four v220 proofs, slot, next-season
- **Prior evidence:** [INDEX C2/D1/E2](../INDEX.md), [P3-FB](2026-11-05_p3-fb-jf-observed-quality-source-handoff.md), [P3-FA](2026-11-05_p3-fa-selected-jf-source-owner-numeric-bridge.md). 최신 사용자 직접 결정은 전체 시즌 품질 전수/독립 사용조건 인증이 과도하며, **서로 같은 효과로 식별된 발견 후보의 최대 수치**로 최고품질 선택이 충분하다는 것.
- **Decision:** `CONNECT` — 기존 그룹·Native 관측기/캐시·v220 증거/SimC input을 재사용. 발견된 후보 중 수치가 가장 큰 항목을 선호하며, 전체 품질 완전성·효과 자체 재현·사용조건 인증 Gate 추가는 `STOP`.
- **Changes:** `v216`의 동일 enchant/color/expansion/class source family에서 명목 CHMV 벡터의 stat-kind/비열등성을 비교하고 가장 강한 관측 수치(동률이면 등급)를 선택한다. 품질별 `minimum_ilevel`을 그룹 일치의 선결조건에서 제거한다. F는 동일 SimC stem과 고정 스탯 종류의 기존 v278 관측을 수치 우선 비교. 기존 품질 플래그 `all_market...` 등은 진단이지 Gate가 아니다. `v196`의 별도 `highest_available_quality_verified`·`same_effect_and_use_conditions_verified` 필수 필드를 제거하고, 원래 v220 4-family 영수증, 정확한 원본 품질 rank/SHA 및 실제 적용 slot만 유지한다.
- **Verification:** 기존 v287의 같은효과/다른스탯·손상 rank·원본 검증 회귀에 최대 수치가 craft rank와 다르고 `minimum_ilevel`이 다른 사례 추가. 기존 v240 v196→v212 준비 테스트에서 불필요 플래그 없이도 PASS, 적용 슬롯·SHA·rank 잘못되면 보류. 신규 Actions 확인 전 `NOT_VERIFIED`. 기존 [P3-FB focused #42021462988](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42021462988) 262 PASS는 이전 코드 범위. 신규 Native·게임 HTTP 0.
- **Remaining:** 동일 효과군/정적 rating 비교가 불가능한 실제 후보는 별도로 보류; 특수 효과는 SimC에 맡김. 실제 최고 관측 선택은 품질 정책 완료지만 별도 원본/입력/CHMV 예산·Policy A 네 증거군이 없으면 READY가 아님. 새 시즌 인증 source-owner 제공자·정상 T1·26 DPS E2E 미완료. 저품질 영약+151/Phoenix Oil+16/+17 의심 수치는 공식 증거로 승격 금지.
- **Efficiency:** 기존 v230/v266/v271/v281/v278 관측 데이터에 대한 O(품질 후보 수) 비교만 변경; Native0/게임 HTTP0/새 parsers·효과 엔진·시장 DB·전수 품질 조회0, 정적 캐시 보존. main/v003/v016/Project UI/Work OS/주 개발 채팅 권한 불변.
