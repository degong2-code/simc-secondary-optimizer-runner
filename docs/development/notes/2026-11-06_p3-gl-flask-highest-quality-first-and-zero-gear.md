# P3-GL · 2026-11-06 · F 소스 최고 품질 우선 및 유효한 gear_* 0

- **Capability:** F.FLASK, NATIVE.JSON2, ENVIRONMENT.WEB.
- **검증 원본:** pinned SimC `c20e2ad52e4c33711f74272309a5748125175fe8` `engine/player/player.cpp:1752-1771`: `gear.get_stat(stat) < 0`이면 물리 아이템 스탯, 그 외엔 지정 `gear_*` 값이 적용되므로 정확히 0도 가능. `v269.prepare`는 SimC 전문화 기본 영약과 무관하게 명시적으로 `flask=disabled` vs `flask=<selected>`를 비교하고 `flask` precombat 후 `snapshot_stats`로 CHMV 관측. `v091.propose`는 `raw_gear_override + F = target`을 유지하므로 F 중복 가산 방지.
- **변경:** `v216._prioritize_highest_source_quality_F`는 `v281`의 검증된 물리 후보를 SimC token stem + 소스 품질 suffix 기준으로 그룹화하되 최고 소스 품질만 **Native 측정 대상으로 우선** 지정. 서로 다른 영약 효과·모호한 token·최고 품질 동순위는 유지. 효과 동일성이나 전체 품질 우위 인증이 아니라 측정 최적화. 직접 선택한 정확한 ItemID, v278 Native 저장/비교, 정책 A, v222/v212 설치 소유자 변경 없음.
- **교정:** `v269._player`의 모든 스탯 값 0일 때 잘못 차단하던 오류 제거. JSON2 rating 필드 자체가 비었으면 계속 차단. F는 원래 SimC 전·후 수치 델타만 수집하며 효과 파서 신규 작성 없음.
- **효율 근거:** 4종 영약 각각 2품질인 경우 8개 후보→4개 최고 품질 후보로 축소. 후보당 최대 2회 Native이므로 16→8회 측정 상한 절감 예상, 공유 baseline/cache에서는 그 이하. 실전 재측정 증거 아님.
- **판정:** 오프라인 focused 완료 후 통합 영수증에만 PASS 반영. 현재 real T1 #42170351404의 Native8 및 NOT_READY는 역사 증거, 새 코드 실제 Native 0/HTTP 0. J/O/G의 검증된 소스·정책 A·실 READY 아직 필요. main·불변 문서·Project UI·소유권 불변.
