# 2026-11-04 · P3-CP · 품질 비교 1개와 실제 고정 O 가능 기름의 제한된 SimC 측정

- **Capability:** `F.FLASK`, `O.OIL`, `BUDGET.GJFO`, `SOURCE.SEAL`, `PRODUCT.E2E`
- **Keywords:** P3-CP, F, O, oil, Phoenix Oil, flask, quality rank1/rank2, SimC native, rating, v269, v278, source-only
- **Prior evidence:** PROTOCOL→INDEX→[P3-CO](2026-11-04_p3-co-actual-flask-oil-native.md) 실 Native #41666305288에서 Shattered Sun rank2 치명+165, Oil of Dawn rank2 정적 CHMV0(조건/발동 가능), original v269/v278 baseline 공유. [P3-CN](2026-11-03_p3-cn-real-source-integration.md): Flask 물리 item241327 rank1/241326 rank2 SimC exact ID, 실제 오일 ID243734=(Class0/Subclass8), pinned temporary enchant ID8052/rank2/effect_spell1237006/thalassian_phoenix_oil. 표본의 실제 Wago/SimC 관계 영수증은 이 동일 빌드만 적용.
- **Decision:** `EXTEND` — 확인된 1개 flask family의 lower rank와 정적 O 가능성이 있는 rank2 Phoenix Oil 1개만 원래 v269/v278로 측정한다. 동일 효능/적용 조건을 Native 한 번으로 인증하지 않으며, 임의 스탯 하드코딩·전수 Native·새 효과 엔진 없음.
- **Changes:** 기존 P3-CO의 고정 source-profile SHA·2옵션·최대3회 Native 실행기를 두 번째 고정 candidate pair에도 재사용하도록 최소 옵션화. 해당 사용자 입력/UI 목록/예산과 독립, 원본 P3-CO 실측과 stage identity는 보존. 새 일회성 Action은 이미 보유한 Linux SimC binary 캐시만 사용, 결과를 원본 v278 receipt에 SHA 봉인하며 F/O/READY에는 미반영.
- **Verification:** 신규 focused 및 실제 Native Actions 실행 전 NOT_RUN. P3-CO Native3회 및 148 PASS는 REUSED_HISTORY; 신규 빌드 HTTP0, 기존 pinned binary만 사용. 새 followup Native 실행 상한3(두 옵션/공유 baseline).
- **Remaining:** 동일 품질군의 효과 구조와 사용 조건(스탯뿐 아니라 proc 포함), 각 무기/손 실제 적용 가능성, 여러 영약·기름 옵션의 품질 우위 및 정적 F/O의 예산 소유권이 실증돼야 정책 A·v222 B/T·26 DPS 사용자 E2E 연결 가능. 차단 품질/기름은 UI에서 보류. F/O 미승격.
- **Efficiency:** 기존 v269/v278 구현·핀 바이너리·v084 profile·real P3-CN 영수증을 재사용, 기존 측정 옵션 2개를 재실행하지 않음. 새 source network0, one run baseline1+active2 최대3 Native, 작은 3일 artifact. 과거 정적/DPS 캐시 및 main·immutable·Project UI·Work OS 불변.
