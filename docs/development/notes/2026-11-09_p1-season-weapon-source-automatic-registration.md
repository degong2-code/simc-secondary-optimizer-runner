# P1 · 시즌 소스 기반 무기 강화 등록(룬벼리기·기름)

- **Capability:** `CHARACTER.PROFILE`, `O.OIL`, `PRODUCT.E2E`, `SOURCE.SEAL`.
- **Keywords:** runeforge, Death Knight, oil, season engine, pinned SimC, v216, v212, v295, UI, cache.
- **Prior evidence:** P3-HAT 최신 인계 및 P1-DK/P1-O 기존 격리 코드. v281/v278/v285/v286 원본 기름 관계/정적 관측은 소스별 적용 범위 한정. SimC Death Knight 모듈의 `runeforges_e`에 정확한 `RUNEFORGE_ID_*` 열거형 존재; 과거 v132 예시 프로필은 장비/시즌 자동등록 증거가 아님.
- **Decision:** `CONNECT` — 향후 시즌 룬 목록은 하드코딩된 웹 ID가 아니라 현재 SimC revision의 Git blob SHA로 봉인한 클래스 모듈에서 생성. 기름은 설치된 정확한 O/손/물리 ID만 표시하며 검증되지 않은 소스 후보를 사용자 선택으로 승격하지 않음.
- **Changes:** 기존 v275 Git tree/RAW 조회·v217 stage 재사용하는 선택형 v295 룬 소스 수집; v216→v212 설치 옵션 봉인; v113 원본 확인된 읽기 전용 옵션 API; v098 설치 목록으로 실제 룬 ID 검증; v106 입력 형태 검증·v294 런타임 범위 분리; 웹 정적 룬 ID 제거·시즌 설치 목록 동적 사용. O0 경로와 기존 세션 SHA 유지.
- **Verification:** 신규 Native/DPS 0, 기존 검증된 저장소 Native 영수증은 역사 재사용. 신규 v295 합성 소스/동일 빌드·변조 차단, v294 미래 ID, 웹 및 기존 focused 검사 CI 추가. 이 기록은 실 현재 시즌 v295 원본 수집 PASS나 실제 DK/O>0 DPS PASS를 의미하지 않음.
- **Remaining:** 실제 70783 소스 수집·설치된 DK 목록/선택 Native 1건 확인. 냉기/부정 기본 룬 자동 선정은 별도 원본 선택 기준 필요. 기름은 v212의 `official_O_physical_source`에 이미 검증된 설치 손만 표시하며 **사용자별 임의 O+부분 손 변경과 시즌 전체 기름 목록 자동 발행은 미완료**. 등록 미확정 항목은 기존 O0 정상 환경을 차단하지 않음. Windows 실제 클릭 미검증.
- **Efficiency:** 기존 v275/v217 봉인/캐시 재사용, 같은 단계·리비전 반복 HTTP 제거; 원본 1종만 선택 수집, SimC 효과 기구/품질 인증 Gate 추가 없음. 기존 G/J/F/O·수동 T/캐시 identity 보존, main/v003/Project UI/Work OS·주 제품 개발 소유권 불변.
