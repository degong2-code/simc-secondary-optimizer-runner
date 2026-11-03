# 2026-11-03 · P3-BX · 새 시즌 소켓 허용성 SimC Native 대비 실험

- **Capability:** `J.GEM`, `GEAR.SEASON`, `PRODUCT.E2E`
- **Keywords:** socket, 기본/추가 소켓, gem_id, ITEM_BONUS_SOCKET, show_bonus_ids, 인게임 유효성
- **Prior evidence:** 최신 사용자 질문은 시즌 6~7소켓 고정이 아니라 **새 시즌의 어떤 부위/특수 아이템이 몇 소켓 가능한지 환경 엔진이 처음부터 발견할 수 있는가**. SimC의 `item_data.hpp` 기본 `socket_color[]`, `sc_item_data.cpp`의 `ITEM_BONUS_SOCKET` type6 및 `show_bonus_ids=1`, `item.cpp::decode_gems`의 gem_id 처리, `enchants.cpp::initialize_gem`은 실제 원본 확인. 기존 v139의 6 일반+1 특수 보석은 역사 시즌 전용.
- **Decision:** `EXTEND` — SimC의 장비 소켓 원본과 **아무 소켓 없는 가슴에 gem_id만 넣는 경우**를 구분한다. 원래 가슴(no gem) → 가슴 gem 입력만 → 같은 가슴에 SimC 원본에서 조회한 1소켓 bonus_id + gem → 다른 비소켓 어깨에 해당 bonus_id + gem을 최대 4회 Native로 비교. 보너스 자체가 SimC에서 적용되는 것과 *해당 장비에 인게임으로 보너스를 붙일 수 있는 것*은 별개.
- **Changes:** `integration_probes/v270_socket_parser_native_contrast.py` + 단발성 `.github/workflows/v270_socket_parser_native_contrast.yml`을 사용. 기존 v192 동일 버전/SHA Linux SimC binary, 기존 MID2 Frost Mage 실제 fixture, 1iteration×4회, SimC `show_bonus_ids=1`로 실제 소켓 보너스 ID 선정. 별도 이펙트 구현·영구 Gate·시즌 전체 장비 DB 없음.
- **Verification:** Native 결과 `PENDING`; 코드와 원본만 확인한 상태. 과거 v198/v210 Native 증거는 관련 범위에서만 재사용.
- **Remaining:** 실험 후 결론·run ID·실제 4개 case status 및 ID/SHA 반영. 실제 인게임 소켓 추가 아이템의 허용 부위와 아이템 bonus 적용 조건이 SimC만으로 판별되는지 분리. 엔진에는 출처 데이터 내 가능한 기본/보너스 숫자만 자동 추출하고 무조건 gem_id 성공으로 게임 적법성 주장 금지.
- **Efficiency:** 기존 바이너리·fixture·cache 재사용, Native 최대 4회, 신규 소스 빌드·Wago HTTP·전문화/아이템 전수0, 짧은 SHA receipt 보존.
