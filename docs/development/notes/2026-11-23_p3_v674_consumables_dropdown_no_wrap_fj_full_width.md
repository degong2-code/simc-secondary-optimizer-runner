# P3 v674 — 환경 구성 드롭다운 1행·소모품 2열·F/J 전체폭 분리

2026-11-23 KST · 격리 브랜치 `probe/chat-cache-v035-20261024`

## 개인 PC 보고/기준

사용자가 직접 촬영한 **v673** 최적화 화면 두 장에서 다음 문제를 확인:
- 환경 설정의 `음식`, `영약`, `물약`, `증강 룬` 4개의 각 제어가 지나치게 좁은 4열 그리드를 차지하고, 검색 목록에서 `미사용 (이번 시즌 기본)` 선택지부터 2행으로 강제 줄바꿈.
- 검증된 `F/J 구성` 선택이 `영약` `.env-grid-cell > .field` 안에 중첩돼 긴 원본 구성 라벨이 그리드 내재 최소폭과 충돌하여 한 행을 화면 너머까지 뚫는 가로 오버플로.
- 같은 PC의 70961, ilvl334, 기본 소켓4·기름 OFF에서 두 verified F/J 설치본은 여전히 **개별 선택 보류**. 최신 v673 화면의 세부 원인은 `DIFFERENT_RUNTIME_SNAPSHOT`(v113 실행 프로필 입력 차이)이며 다른 실행 입력 동등성 증명이 되지 않았음. **v674 UI는 이 차단을 해제하지 않음**.
- 사용자 확인으로 v673 장식 제작장비 1·2 가로 2열은 이미 정상. 이번 작업은 해당 변경을 보존.

## 구현 — CSS/DOM 및 라벨만

1. `runner/webui/index.html`: `season-verified-budget-group`을 영약 `.field` 바깥으로 꺼내 `.env-input-grid`의 직접 자식으로 배치. 음식/영약/물약/증강 룬 다음, Omnium Folio 이전에 **독립된 전폭 행**. 동일 `id`·select value/SHA·진단 버튼과 이벤트는 보존.
2. `runner/webui/styles.css`: 앞 4개 전투/보석/기름 필드는 종전 compact 4열, 이어지는 소모품 4개는 2열(각 2/4 그리드), 검증 F/J 그룹은 `grid-column:1/-1`. 선택값/안내는 minmax(0,1fr)·ellipsis·폭 제한, 상세 실패 사유는 독립 행에서 정상 줄바꿈. 좁은 화면에서 기존 2열 반응형 또는 1열로 감축. 전 UI `.choice-result`는 한 줄/말줄임 처리, 검색 드롭다운은 최소한의 실제 읽을 폭과 짝수 열 오른쪽 정렬.
3. `runner/webui/app.js`: 검색 결과 버튼과 현재 선택 입력에 **원문 라벨 title**을 표시하여 생략된 글자를 확인할 수 있도록 함. F/J 네이티브 option 라벨은 간결한 `F/J·소켓·기름·선택 보류` 중심, **서로 다른 실제 물리 ItemID를 구별할 때만** 상세 ID를 옵션 본문에 포함하고 전체 원본 ItemID는 title에 보존. `option.value = installed_manifest_sha256`, 기존 정확 선택 검증, source identity, disable 조건 모두 불변.
4. `tests/test_v669_verified_fj_physical_identity_offline.py`에 표준 HTMLParser 기반 `F/J group` 직접 부모 검증, 4개 소모품 순서/배치 및 CSS 1행/반응형/검색 결과 title 회귀 추가. 기존 F/J 백엔드·SimC/예산/캐시·취소·재개·통계/세션 코드는 수정하지 않음.

## 신규 검증 범위

- 제품 코드 HEAD: `42db253a2dc26a10060b43c4bee18a2d59821169`.
- [Windows ZIP + actual loopback CI #45117136177](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45117136177): Windows Python 3.12/3.14 각 **354 PASS/0 FAIL**, 기존 패키지·CMD·HTTP·캐시 회귀 통과, 새 DPS Native 0.
- [Local API CI #45117136190](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45117136190): Ubuntu Python3.12/Windows Python3.14 각각 **513 tests OK(skip1)/0 FAIL**.
- 재사용 focused 및 v401 계약 정합성 CI 성공. 새 시즌 DB2/HTTP 소스 수집, Native DPS, C++ 컴파일 신규 없음.
- Windows Actions wrapper artifact ID `14792003122` (wrapper 별도); 실제 내부 단일 제품 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip` 크기 **1,536,429 bytes**, SHA256 `d7fe776084053d23bf8ee0e6743533029e783bd2b659adab4560845dc28c985c`, ZIP CRC PASS, 내부 manifest **286/286 size+SHA PASS**; SimC exe 미포함 (기존 관리형 재사용).

## 남은 작업/불변 경계

- **개인 PC v674 실제 스크린샷 확인 미실시**. 브라우저의 옵션 렌더링은 사용자 PC에서 확인; CI 통과는 PC 시각적 완전성 인증이 아님.
- **F/J 선택 보류 여전히 합당**: v113 profile input differences; 기존 v212/v113 원본을 임의 병합하거나 SHA 자동 선택 금지. 최적화/READY/KR Retail game build 일치도 미확정.
- PC 확인: 기존 CMD 종료 → v674 새 폴더 → 기존 관리형 70961·기존 로컬 원본/캐시 유지 → 조회용 build `12.1.5.70961`/ilvl334, 4소켓, 기름 OFF → 소모품 드롭다운 한 줄/전체폭 F/J UI 확인. 시즌 환경 구축·Native·DPS는 불필요.
- 공식 `15/78 COMPLETE` (제품 달성률 아님), `full_product_e2e=PENDING`, `next_review=B10`. main/immutable v003/Project UI/공식 WorkOS·Shared State/주 제품 채팅 소유권 변경 없음.
