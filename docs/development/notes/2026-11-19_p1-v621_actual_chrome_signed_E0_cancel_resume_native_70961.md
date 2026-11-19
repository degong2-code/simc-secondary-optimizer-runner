# P1 v621 — 실제 Windows Chrome 서명 E0 영구마부 클릭 → Start → Cancel → HTTP 재시작 → 동일 세션 Resume (PASS)

2026-11-19 · 격리 브랜치 `probe/chat-cache-v035-20261024` · 게임 빌드 `12.1.5.70961` · SimC 소스 `9933ffb946fb55b1fa66657b848f519ac19006e1`.

## 실제 실행 증거 및 구분

- **최종 실환경 PASS:** [GitHub Actions #44445250976](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44445250976), Windows-2022, 실제 Headless Chrome/Selenium과 실제 로컬 v113 HTTP 서버, 본 제품 원래 v113→v216→v217→v212→v106→v098→v096→v293/v094 사용. 원본 artifact **14492594292**, `V621_REAL_CHROME_ENCHANT_CANCEL_RESUME.json` (직접 다운로드·JSON 확인) `status=PASS_REAL_CHROME_SIGNED_E0_START_CANCEL_RESTART_RESUME`. 브라우저 API/SimC 입력을 fake하거나 임의 설치 manifest를 주입하지 않음.
- 검증된 **동일 70961 소스 빌드** Windows CLI 캐시만 읽음, `simc.exe` SHA256 **4f4472ac8687d029cd7d6041741f44aa98750ea1b3e953dfa7002dee1f38879f** + 소스 commit/빌드 SHA 바인딩 확인. 이번 실행 신규 컴파일 **0회**.
- 실제 Chrome 화면에서 일반 사용자가 **징벌 성기사/334**, 무기 기름 미사용, 장신구 **270175 + 270173**을 선택하고 시즌 Build 실행: `G2850/J92/F165/O0/B=T3107`, **시즌 환경 Native6회**, ready=true, installed=true. 실 v212 자동 등록 **19건**, 현재 실행 설치 manifest SHA **202e4067736a98189ce693e6747adda36f5664b33b7b731bf719601ee753d5b9**. 빌드가 달라지면 즉시 차단, 과거 70783 증거를 70961에 복사하지 않음.
- `runner/webui/app.js`의 v620 부위별 드롭다운 **`env-enchant-chest`**가 실제 서명 E0 `chest:7957/7985/7987/8013` 4건을 노출. Selenium **실제 Select 동작**으로 `chest:7957` 선택, `season_enchant_other=chest:7957` 미러링, 반지1/2 값은 비어 있고, 요청 `controls.enchant_choices={"chest":7957}` 정확 적용. 서버로 가는 요청의 installed SHA, 게임 빌드, ilvl334, 공식 T 자동, 실물 장신구 ID, O=0 조건 확인. 원래 `v106→v098/v096` 서버 장비 ID·부위·정적 E0·중복 보호를 변경하지 않음.
- Chrome 기본 `start-btn` 클릭으로 **원래 64 native_budget 세션을 생성**(64건을 전부 계산하지 않음). 화면의 `cancel-btn` 클릭으로 작업 중단, 워커 `PAUSED_USER_CANCEL`, 초기 **Native 2회** 완료 후 부분 체크포인트 보존.
- **서버 HTTP 인스턴스를 실제 종료·재생성**하고 Chrome 페이지 새로고침. 같은 세션 ID(개인정보 제외 SHA256 **50e406b033dfc3860795719f027687699d77fc9d90dba0a4a1d79dc0381c63b3**)를 복원, **원래 `v212` 설치 SHA 및 E0 가슴 마부 7957 UI 선택이 다시 확인**됐고 `resume-btn` 활성화. `state.verifiedInstalledBuildFromThisPage`는 새 HTTP 페이지에서 null일 수 있으나, 저장 세션의 설치 manifest SHA 및 실제 서명 E0 목록은 재검증 완료; 이를 새 임의 사용자 Build 승인으로 오인하지 않음.
- 실제 `resume-btn` 클릭, 동일 세션의 **Native 누적 2→3→4회 증가**, 재개 후 후보 체크포인트 누적 `completed_jobs=4` 기록. 안전을 위해 두 번째 `cancel-btn`으로 다시 `PAUSED_USER_CANCEL` 상태에서 종료. **사용자 DPS Native 신규 총 4회**; 이전 평가 리셋/재시작 현상 없음. 기존 v619의 단일 사용자 실제 **DPS·SEM·95% Native6회**는 별도 이전 증거로만 재사용하며 이번 v621이 64건 완성·새 최적화 95% 결론 또는 전역 최적임을 주장하지 않음.
- 이 실행은 GitHub Actions Windows 브라우저 실환경이지 사용자의 개인 컴퓨터 설치/실제 사용자 전 전문화 검증을 의미하지 않음. 기록한 artifact에는 비밀번호, 원본 프로필, 경로, 개인 세션 ID를 포함하지 않음.

## 첫 실제 실패와 수정

- [첫 실제 Chrome #44444615522](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44444615522)는 **실제 v212 19건 설치, 화면에서 chest 7957 클릭, 서명 SHA 맞는 HTTP 요청 구성까지 성공**한 뒤 검사 스크립트의 **`KeyError`** 때문에 Native 시작 전 중단. 원본 실패 영수증 artifact **14492008452**. 제품 내부 승인/Native 실패로 분류하지 않는다.
- 원인은 새 테스트 `integration_probes/p1_v621_real_70961_browser_enchant_cancel_resume_once.py`가 JS `ilvl` 반환을 Python에서 `ilevel`로 잘못 읽고, 자동 T 선택의 생략 가능한 `final_T`도 필수라고 가정한 스크립트-only 오류. 동일 빌드/부위/E0/출처 검증을 유지하면서 실제 키를 사용하고 `req.get("final_T") is None`을 확인하는 최소 수정 **`1e31c41cd7680cd9cc802a2424b1bf0f8b932e2e`** 후 **최종 #44445250976 SUCCESS**.
- 코드와 워크플로는 `integration_probes/p1_v621_real_70961_browser_enchant_cancel_resume_once.py`, `.github/workflows/p1_v621_real_70961_chrome_enchant_cancel_resume_once.yml`. 신규 UI·탐색 엔진·효과 메커니즘·통계 Gate·서버 권한 승격 없음.

## 실제 개발 범위와 다음 과제

이 검증으로 **이번 시즌 검증된 E0 한 부위 선택의 실제 웹 UI 조작/시작/취소/재개** 경로가 PASS. 수동 최종 T, E>0 또는 다부위·무기손 미인증 마부, 26 DPS 전부 동일 실 Native 검증, 개인 Windows 설치 및 전체 사용자 전투 설정 UI, 전체 제품 release는 아직 다른 범위다. 제품 정식 `15/78 COMPLETE`, `full_product_e2e=PENDING` 유지. 동일 시즌 원본/바이너리/캐시는 이전 승인 scope에서 재사용하고 차이가 실제로 생긴 부분에만 최소 Native 실시.

**권한:** 모든 수정은 지정 격리 브랜치에만, `main` 병합·`v003` immutable·원본 `v016`·Project Sources/UI 적용·공식 Work OS M0/Shared State·기존 주 개발 채팅 소유권 불변.
