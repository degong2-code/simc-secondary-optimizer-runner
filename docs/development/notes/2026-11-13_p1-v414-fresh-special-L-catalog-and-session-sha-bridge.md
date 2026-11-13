# v414 — P1 시즌별 특수장비 L·사용자 세션 설치 SHA 원본 연결

- **Capability:** `PRODUCT.E2E`
- **Keywords:** P1, GJFO, v212 installed, v113, v208, special L, static rating, exact SHA, profile, session, result snapshot
- **Prior evidence:** [v413 설치 variant 64개 제한 제거](2026-11-13_p1-v413-verified-install-variant-limit-removal.md); 기존 v113/v208 current-season startup. 이전에는 특수장비 L 준비 시 `source_catalog_path()`의 역사 패키지 v213를 사용하고 fresh 세션의 v208 후 legacy `_seal_environment_manifest` 재진입
- **Decision:** `CONNECT` 선택한 검증 v212 설치본의 기존 v213 카탈로그를 원래 v208 L hydration으로 전달하고, source-bound 사용자 프로필의 원래 설치 identity를 유지. 새 Gate·스탯 재구현 없음
- **Changes:** `LocalJobs._catalog_for_selected_special_L`가 기존 `load_fresh_profile_for_user`로 선택된 아이템레벨/기름 손·ID/보석·영약에 맞는 검증 설치 원본 카탈로그만 선택. 명시된 설치 빌드를 찾지 못하면 packaged fallback을 막고 L Native 이전 차단. v208 수령 후 fresh session은 이미 v098/v096에서 검증한 v212 environment summary를 보존하고 패키지 v216를 다시 조립하지 않음. 시작/재개 `_verify_environment_dependencies`에 이미 봉인된 설치 SHA를 전달하여 같은 O의 다른 F·보석 변형과 혼용되지 않게 함
- **Verification:** 새 focused v414와 기존 v113/v212 Linux·Windows CI에서 PASS/FAIL 확인. 새 Native 0, HTTP DB2 0; v208 Native 수행 함수 자체 변경 없음
- **Remaining:** 실제 사용자 특수장비 포함 신규 시즌 전체 DPS E2E Native, 26전문화 전수 완료 등은 별도 증거가 필요하며 이를 본 수정의 PASS로 주장하지 않는다. P1 사용자 입력→대표 프로필→기존 적응형 SimC→스냅샷 제품 실행 계속
- **Efficiency:** 기존 v113 복원·v208 단일 Native/캐시 재사용. 명시 빌드의 파일 조회는 원래 v212 finder로 해결하며 불필요한 새로운 source collector·컴파일·Native 반복이 없다. 이전 패키지 manifest 재계산 제거

**권한:** 격리 브랜치 한정, main·불변 원본·Project UI·공식 승격 무변경.
