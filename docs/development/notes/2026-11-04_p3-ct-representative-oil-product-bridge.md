# 2026-11-04 · P3-CT · 내부 대표무기→무기 기름 물리 적용 후보의 기존 제품 경로 연결

- **Capability:** `O.OIL`, `BUDGET.GJFO`, `SOURCE.SEAL`, `PRODUCT.E2E`
- **Keywords:** P3-CT, representative weapon, weapon mask, InventoryType, subclass, source-only, existing Build, v167, v232, v274, v285, oil, talent, Winter's Blessing
- **Prior evidence:** [PROTOCOL](../PROTOCOL.md)→[INDEX](../INDEX.md)→[P3-CS](2026-11-04_p3-cs-spell-weapon-source-normal-build.md): 실 Wago #41732744145 동일 빌드 주문/무기 마스크 및 기존 v216→v274/v191 source 연결, focused 166 PASS. [P3-CQ](2026-11-04_p3-cq-item-id-native-binding.md) 기존 v281 exact item ID→v278 SimC Native, [v080](../../V080_STATIC_CHMV_TALENT_SEPARATION_NATIVE_ACCEPTANCE.md) 톱니날 촉 +4% JSON2 사냥꾼 Native 700→728/600→624와 정적 c·buffed 분리. P3-CO/CP 같은 핀 냉법의 +1 rating은 특성·반올림 가능성을 고려해 사용자 직접 결정으로 심층 재감사 보류.
- **Decision:** `CONNECT` — 사용자 지시대로 영약 1품질 치명 1포인트·냉법 가속 반올림 원인 규명은 후순위. 특성별 역산이나 `gear_*` 보정 규칙을 추가하지 않고, 기존 v232가 선택한 대표 무기와 v167 게임 원본 장비 type/subclass를 v285 실제 기름 주문의 마스크에 *한 번* 결합한다.
- **Changes:** 새로운 standalone 수집·검증 엔진이 아닌 읽기 전용 내부 조인 v286: 기존 v217 봉인된 소형 v285/v167/v232 후보의 SHA/receipt/build 검사, 선택 main/off-hand 물리 item ID→class/subclass/inventory type→Wago 원본 mask 조건 일치 여부를 기존 v274 `compile_collected` 결과에 동봉. 숫돌·일반 임시 마부 제외, 소스 없는 무기는 PENDING. 물리 매칭은 **사용자 선택 승인·기름 최소 ilvl 조건·F/O rating 인증·v222 예산·READY**가 아니며 기존 v091/v222 회계는 그대로 보존.
- **Verification:** 신규 focused CI 실행 전 NOT_RUN/NOT_VERIFIED. 이전 #41733818394 166 PASS 및 v212 각440/v113 각207/패키징·UI PASS는 REUSED_HISTORY. 이번 작업 HTTP0/Native0, 이전 실 SimC/F/O Native6회는 재실행하지 않음.
- **Remaining:** 실제 현재 빌드 source/전체 대표 무기 coverage, 필요한 사용 아이템/무기 최소 ilvl·품질 동일효과 등가성·고정 O·선택지 자동 등록, G/J/F/O 모두 증명 후 v222 B/T→v098 적응형 E2E 연결 미완료. 특성으로 늘어난 JSON2 buffed rating을 B/T의 정적 rating과 혼동하거나 역산 금지.
- **Efficiency:** 무기/기름용 시즌 DB 신규 수집 없음, 이미 파싱·봉인된 v167/v232/v285 소형 JSON만 조건부 읽기. 원래 v274→v241 소스 컴파일 경로 재사용, 캐시/DPS/Native identities 변경 없음; 기존 v285 stage 코드·영수증 미변경, main·immutable·Project UI·Work OS 불변.
