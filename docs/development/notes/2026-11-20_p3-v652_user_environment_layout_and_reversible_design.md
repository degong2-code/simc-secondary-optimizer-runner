# P3 v652 — 사용자 지정 환경 입력 통일·4열 마부 배치·디자인 버전 롤백 (2026-11-20)

## 사용자 요청 / 진척 범위

사용자 참조 캡처 기반으로 **실제 제품 UI**를 수정했다. 별도 디자인 편집기 범위를 확대하지 않았다.

- 1행: 대상 수 / 전투시간(초) / 보석 소켓 수 / **무기 기름: 사용·미사용 드롭다운**.
- 2행: 음식 / **영약**(고급에서 검증 설치 영약 선택기를 이동) / 물약 / **증강 룬**(기존 하단 필드를 이동).
- 마법부여: ① **무기(주무기) / 보조무기 / 반지1 / 반지2** ② 가슴 / 다리(각각 2칸) ③ 머리 / 어깨 / 등 / 발 ④ 허리 / 손 / 손목 / 목. 사용자가 '무기·주무기'라고 명명한 2개 위치는 실제 원본의 *main hand + off hand* 슬롯 2개로 해석했다. **주무기와 보조무기를 중복·동일 슬롯으로 선언하지 않는다**. 기존 숨김 `season_enchant_other` 호환 필드 보존.
- **선택 환경 검증·준비** 버튼과 기존 사용자 상태 문구를 옅은 음영·좌측 강조선으로 둘러 표시.
- 사용자 캡처의 모바일 가독성을 고려하여 공통 label 18px + 입력 36px, 데스크톱 4열, 폭 880px 이하 2열. Omnium Folio는 기존처럼 full-width 및 별도 선택형 시즌 모듈, 공대 버프 체크박스 유지.

## 코드 연결·데이터 안전

- `runner/webui/index.html`: 기존 각 id 보존, 새 `optimizer-oil-use-mode` select 한 개만 추가. 숨김된 `optimizer-oil-enabled`은 기존 SimC 유효성/기름 O=0·검증 설치 경로를 위한 내부 호환 필드로 계속 남음. `season-verified-flask`와 `augmentation`은 새 선택지가 아니라 원본 DOM을 그대로 이동. 영약 선택 상태가 이전처럼 `renderInstalledFlaskChoices`/`chooseInstalledFlask`에서 업데이트되는 경로 보존. `season-verified-flask-status`와 `env-flask-summary`는 숨김 ID 유지하여 JS 참조와 세션 복원 일치.
- `runner/webui/app.js`: 새 기름 select 선택 시 내부 원본 checkbox만 설정한 후 **기존** `applyOilUseToggle()` 호출. 서버 검증 없는 O 선택·이전 SHA 자동 승인 없음. `syncOilUseToggle()`가 기존 의도에서 select 값을 재설정하며, busy/active 시 비활성화. 기존 `resultBoundInputIds`에 추가해 세션 결과/예산 변경 감지 유지.
- `runner/webui/styles.css`: v647 이전 CSS를 삭제·대체하지 않고 v652 후행 scope 스타일만 추가. 외부 JS/CSS 프레임워크 신규 도입 없음. v649 passive poll/v650 equipment cache 개선 유지.
- 해당 revision의 **시각적 롤백 기준은 이전 v651 HEAD `071cc1f48c8159ec75469c00049c2f753b8c8542`**. `docs/development/UI_DESIGN_VERSION_REGISTRY.md`에 원본 UI 세 파일의 blob ID 및 복구 명령 기록. `main`, 공식 Project UI 권한·주 개발 채팅 소유권 변경 없음.

## 검증 분리

- 현재 GitHub 제품 HTML의 **201개 ID** 모두 유일, 모든 HTML `label for` 실제 id 존재. 기존 제품 200개 + 새 유저용 기름 select 1개. 두 행의 순서, 마법부여 총 14개 표시 순서, 호환 숨김 필드, CSS mobile 2열, 기존 oil bool 동기화 코드를 현재 repo 원본에서 정적 검증 **13/13 조건 PASS**.
- 신규 `tests/test_p3_v652_environment_grid_design_offline.py`: 5개 오프라인 regression test를 추가. **새 CI/Windows에서 이 5개를 실행했다는 주장은 아직 하지 않는다**.
- 별도 **시각 검토용** 단일 HTML(`SIMC_SECONDARY_UI_v652_Review.html`)은 v647 원본 UI 기반에 v652 배치/스타일을 재현한 오프라인 미리보기이며 실제 프로그램/공식 package와 혼동하지 않는다. Chromium `page.set_content` static preview: 360,390,430,768,1024,1365px 화면에서 **overflow 0**; 880px 이하 2열, 1024px 이상 4열, 플라스크/기름 control 36px. 실제 제품 JS/서버/SimC 연결 검증, Windows 브라우저 최종 인수 대체 아님.
- 새 실제 Windows 3.12/3.14 full UI/package CI·새 배포 ZIP·사용자 PC Native **미실행**. v647 Windows Actions 289 PASS, v639 Native64는 **이전 코드 증거**로 계속 보존. P3 v648 **사용자 PC V229 최초 장애는 여전히 원본 영수증 없이 미확정**.

## 회복 계획

v652 UI가 승인되지 않으면 `git restore --source=071cc1f48c8159ec75469c00049c2f753b8c8542 -- runner/webui/index.html runner/webui/styles.css runner/webui/app.js`를 사용하여 **UI 세 파일만** v651 기준으로 복원하고 코드 차이 확인 후 별도 커밋한다. 기존 세션 폴더, v003 immutable, GitHub main은 변경하지 않는다. 승인된 부분만 이후 공식 Windows 테스트/패키징에 반영한다.

공식 범위 불변: 26 DPS, 미래 T/ilvl 절대 CHMV, G/J/F/O와 L/E/O 정확 회계, SimC DPS·SEM·95%·캐시·취소/재개. `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`.
