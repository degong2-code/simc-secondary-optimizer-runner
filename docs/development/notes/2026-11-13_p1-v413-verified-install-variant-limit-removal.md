# v413 — P1 검증 설치 variant 64개 제한 제거 및 정확 SHA 직접 조회

- **Capability:** `ENVIRONMENT.WEB`
- **Keywords:** P1, G/J/F/O, v212 verified install, v216, v113, F flask, O oil, gems, user variant, exact SHA, cache, 64 cutoff
- **Prior evidence:** [v412 v212 487×2·v113 327×2 오프라인 성공](2026-11-13_p1-v411-fresh-season-gear-test-source-fields-alignment.md); 원래 v216 설치 재사용·v113 선택 설치 profile
- **Decision:** `CONNECT` 검증 완료된 같은 시즌 설치에서 사용자 선택 F/O/보석이 정확히 해당 v212 원본과 연결되도록 기존 finder 및 복원 경로의 비의도적 64개 순회 제한을 제거한다. SimC 빌드 관계 인증, 별도 엔진·새 Gate 없음
- **Changes:** `v216.find_verified_installed_season_environment`는 설치 manifest SHA가 주어지면 해당 `v212_installed_<prefix>.json` 파일 한 개만 직접 검증한다. 일반 oil/hand 조회는 전체 설치 파일을 살펴 기존 v217·v212 정합/모호성 판정을 유지한다. `v113.load_fresh_profile_for_user`의 선택 flask/gem 탐색도 같은 이유로 `[:64]`를 제거했다. 운영 G/J/F/O 수치·프로필 규칙·캐시/결과 포맷 불변
- **Verification:** [v212 Linux/Windows #43389387582](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43389387582) **플랫폼별 488건 실행, 484 PASS·4 SKIP·0 FAIL**; [v113 Linux/Windows #43389387717](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43389387717) **플랫폼별 329건 실행, 328 PASS·1 SKIP·0 FAIL**. 65개 다른 설치본 뒤 정상 선택 O 또는 F가 존재하는 회귀 PASS; 정확 SHA는 `install + catalog + staged` 기존 3파일만 읽는 오프라인 회귀 PASS. 신규 Native 0
- **Remaining:** 이 결과는 **이미 검증·설치한 시즌**의 사용자별 선택 복구이다. 실제 새 시즌 G/J/F/O 최초 계산 및 선택 옵션 전체·26 DPS 제품 실 E2E 완료 근거가 아니다. 다음은 원래 v216/v212 인수 후 user-specific v098/v096/v291 실행·결과 스냅샷의 제품 경로 실증
- **Efficiency:** 정확 SHA에서는 디렉터리 전수 검사 없이 파일 1개에 원래 source/stage 2개 검증(추가 Native/HTTP/DB2 0). 일반 선택 탐색은 전체 수가 늘어도 1회 조회; 새 캐시·파일·데이터 재수집 없음

**권한:** `probe/chat-cache-v035-20261024` 격리 브랜치만. main, v003 immutable, Project UI, 공식 Work OS 및 기존 주 제품 채팅 소유권 무변경.
