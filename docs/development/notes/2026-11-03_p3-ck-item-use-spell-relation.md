# 2026-11-03 · P3-CK · 소비품 ID → 동일 빌드 ItemEffect on-use SpellID 연결

- **Capability:** `F.FLASK`, `O.OIL`, `SOURCE.SEAL`, `PRODUCT.E2E`
- **Keywords:** 영약, 무기 기름, F/O, ItemXItemEffect, ItemEffect, use spell, v280, same-build, provenance
- **Prior evidence:** PROTOCOL → INDEX → P3-CH(110 focused PASS) → P3-CI(122 focused PASS). 기존 v216/v254 ItemXItemEffect 봉인, v279/v190 소모품 Class0/Subclass3·6 물리 ID, v191 SimC temporary effect_spell_id, v269/v278 static delta 측정기 재사용.
- **Decision:** `CONNECT` — v254 원본 relation을 재다운로드하지 않고 누락된 ItemEffect 테이블만 기존 v217 stage로 추가 수집. 별도 시즌 구축 엔진·효과 모델·UI 인증 Gate 없음.
- **Changes:** 새 v280은 ItemID→ItemEffectID→SpellID의 동일 빌드 FK 관계를 확인하고 on-use TriggerType 0만 source 증거로 봉인한다. v216이 같은 정상 Environment Build에서 호출하며 v274는 봉인된 v280 successor가 있으면 기존 v191/v211/v213 컴파일에 전달한다. v279 봉인 원본, 과거 캐시, main 및 불변 자료는 미수정.
- **Verification:** 신규 focused regression 및 기존 연속성 CI 결과 확인 대상. 기존 P3-CI 122 PASS 및 P3-BX Native 4/4는 REUSED_HISTORY에 한정. 이 변경은 실제 게임 HTTP와 SimC Native를 직접 실행하지 않음.
- **Remaining:** 아이템 사용 주문 ↔ SimC Flask/Temporary token/effect exact 매핑과 최고 품질·oil hands/weapon 검증, 실제 정적 F/O·v222 B/T·정책 A→사용자 adaptive E2E. 단순 (0,6) subclass나 on-use SpellID만으로 기름·품질·F/O 예산 승인 금지.
- **Efficiency:** 기존 v254 관계를 재사용, ItemEffect 첫 실행 최대 1 HTTP, v217 SHA cache hit 이후 0 HTTP. Native0, 기존 정적/DPS 캐시 불변, source-only 소형 JSON 및 제한된 CSV. 
