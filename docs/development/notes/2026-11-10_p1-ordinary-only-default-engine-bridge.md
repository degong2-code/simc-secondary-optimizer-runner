# P1 · 기본 일반보석 4종 공통 시즌 엔진 연결 (2026-11-10)
- **Capability:** `BUDGET.GJFO`, `ENVIRONMENT.WEB`, `PRODUCT.E2E`.
- **Keywords:** 26 DPS, four ordinary gems, optional special, same-build source, v271, v216, v098, SimC, first Build.
- **Prior evidence:** 기존 v271→v216→v222→v098 소켓/J 계약은 특수보석 ID 1개를 필수로 요구하여 일반보석 4개만 적용하라는 최근 사용자 결정을 기본 Build에서 실행할 수 없었음. 기존 v221/v266/v230/v232 원본, 원래 v212/웹 Native 영수증은 재사용.
- **Decision:** `CONNECT` — 별도 보석·효과 엔진 없이 기존 v271의 `source_mode`에서 `special_gem_id=None`과 일반보석 4종 배치를 지원하며, v216 J 원본 소유자 및 v098 사용자 프로필로 연결. 기존 사용자가 특수보석을 명시한 경로는 원형 호환.
- **Changes:** v271의 일반 4종 배열·소켓·J 대사, v216 exact source/quality/socket J 연결 및 기본 소켓 4개, v098 동적 프로필 소켓 배치, v113/web 기본 4개 및 특수 선택 시 5개 이상, 변경 범위 회귀 테스트. 수동 G/F/O/Policy A 인증은 그대로 유지.
- **Verification:** GitHub CI의 새 HEAD 집중·웹 Linux/Windows·UI 영수증 확인 전 신규 PASS로 주장하지 않음. 정적 원본 단계 계약/합성 Web 테스트는 실제 신규 시즌 원본 수집·SimC Native READY와 구분.
- **Remaining:** 이전에 관측되지 않은 새 시즌의 G/J/F/O 최초 설치·최고품질 item catalog 전주기·26 DPS 장기 Native/실 Windows GUI 사용은 미실증. J의 실제 증명은 여전히 원본 v221/v230/v232·v212 설치 소유. 소켓 선언 자체를 실제 게임 소켓 증거로 속이지 않음.
- **Efficiency:** 기존 봉인 v217/v221/v266/v230/v232 및 Native G/F·DPS 캐시 재사용. 신규 SimC Native 0회, 새로운 시즌 DB/효과 인증 Gate/파서/탐색엔진 없음. 선택되지 않은 특수보석 ID 수집·분류를 실행하지 않아 원본·I/O 및 사용자 입력 부담 감소.
