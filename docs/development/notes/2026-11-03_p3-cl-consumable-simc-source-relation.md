# 2026-11-03 · P3-CL · F/O 원본 관계에서 SimC 소스 ID까지 연결

- **Capability:** `F.FLASK`, `O.OIL`, `SOURCE.SEAL`, `PRODUCT.E2E`
- **Keywords:** F/O, flask, oil, SpellEffect, EffectMiscValue, enchant ID, v281, v230, quality, SimC, zero-history, source join
- **Prior evidence:** PROTOCOL→INDEX→P3-CK [126 focused PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41650487058). v254 ItemXItemEffect→v280 on-use SpellID, 봉인된 v275 generated temporary enchant, 기존 v256/v230 정확 SimC item_data, v217 stage, v191/211/213 compiler, v269/278 Native 델타. 실제 pinned SimC consumable.cpp는 DBC Item ID/name/crafting quality로 flask를 찾으며 generated temporary_enchant.inc는 enchant ID/quality/spell/token을 기록.
- **Decision:** `CONNECT` — 기존 SimC 아이템 파서/임시 마부 원본과 동일 빌드 Wago SpellEffect(Effect 54 + enchant misc ID)의 교차 참조만 증분 연결한다. 신규 효과 해석기, 전체 아이템 DB, 신규 Native 전수, 별도 사용자 Build 금지.
- **Changes:** v281 추가: 기존 v280·v275·v256를 재사용하고 Wago SpellEffect만 v217에 최대 1회 봉인. Flask는 정확한 SimC DBC ItemID/class/subclass/quality 후보, 일반 item-enhancement는 실제 SpellEffect enchant ID ↔ SimC temporary enchant ID로만 일치시킨다. v230 crafting_quality 필드 보존, v216 normal Build 자동 호출, v274 기존 컴파일러에 sealed successor 전달. Source candidate는 정확하더라도 임의 사용 token·oil 정체·무기/손 허용·품질 최고·F/O 정적 rating의 확증 아님.
- **Verification:** 신규 focused CI는 코드 커밋 후 확인 예정(NOT_RUN/NOT_VERIFIED). 이전 P3-CK 126 PASS, P3-BX Native4/4는 REUSED_HISTORY. 이번 변경 전용 실제 게임 HTTP0·실 SimC Native0(합성 fixture 대상).
- **Remaining:** 실제 같은 빌드 SpellEffect 컬럼/아이템 조인 결과 확인, SimC Flask 옵션·oil 적용 손·품질 우위/원본 효과 강도 및 Native F/O 검증, v222 B/T→Policy A→사용자 26 DPS adaptive E2E. 보석 +16/+7 vs Native +16/+8 별도 미해결. 사용 확정 전 READY=false.
- **Efficiency:** 기존 stage SHA/원본·캐시 보존, 추가 DB2 1개 최초 수집 후 v217 재호출 HTTP0·Native0. 26MB SimC item_data는 신규 source stage에서만 v230 1회 파싱하고 cache hit은 작은 receipt만 확인. 기존 정적/DPS 캐시·원본/Project UI/main 불변.
