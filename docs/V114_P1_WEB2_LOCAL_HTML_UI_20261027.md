# v114 · P1-WEB-2 로컬 HTML 웹앱 UI 구현 및 검증

**2026-10-27 KST · GitHub 격리 브랜치 전용.** P1-WEB-1/v113의 기존 로컬 FastAPI와 검증된 v106→v098→v096→v094 Native SimC 실행기를 보존하면서, 새 프런트엔드만 연결했다. **아직 Windows 설치형 독립 앱, Cloudflare 배포, 브라우저 클릭 실기까지 검증한 것은 아니다.** Native 신규0회.

## 사용자 승인 제품 형태

웹 화면(HTML/CSS/JS)과 로컬 Python HTTP API가 `127.0.0.1`로 통신하고, 실제 SimC 계산·영수증·캐시·취소·재개는 사용자 PC에서 작동한다. 전용 클라우드/계정/DB/새 엔진 없음. 추후 pywebview/Tauri 설치형 UI 또는 클라우드 별도 실행기를 연결할 가능성만 열어둔다. 최신 대상 딜러 **27** 전문화(증강 포함), 탱커·힐러 제외; 현재 검증된 사용자 대표 프로필 6개만 웹 선택지로 공개한다.

## 구현

- `runner/webui/index.html`: 한국어 1페이지 HTML. 캐릭터/전문화·종족·특성·장신구2개·목표 ilvl 기본334/수동 최종 T·전투대상/시간·공대버프·주/보조 기름 O 입력. 선택 특수장비 최대2개, 장식 최대2개는 접어서 필요 시만 입력. 음식·물약·증강 룬·다이아몬드·Omnium 소스 관측 선택지. 원본 정적 영약 F=165 고정.
- `runner/webui/styles.css`: 톤다운된 반응형 스타일, 웹 폰트 다운로드·외부 JS/UI 패키지 없음. 측정 데이터가 없으면 결과를 만들어내지 않음.
- `runner/webui/app.js`: v106 동일 `controls` JSON을 수집해 `v113` API에 전달. (1) Native0회 예산 미리 확인, (2) 사용자가 확인한 경우에만 실제 Native 실행, (3) 진행률 조회(1.4초), (4) 현재 Native 완료 후 취소 요청, (5) 같은 세션 재개, (6) 완료 세션 캐시 6/6 재검증, (7) 기존 세션 ID로 브라우저에서 결과 복구. 세션 ID **20자리만** 로컬 스토리지에 기록, 사용자 특성/개인 경로/결과 원문을 브라우저 스토리지에 복제하지 않음. DOM 결과 생성은 `textContent`/createElement로 하여 사용자 제공 문자열의 HTML 삽입 금지. DPS/SEM/CHMV 절대 rating·비율·선택쌍 95% 방향 지지·실질 관측 대안·전역 최적해 미입증 표기를 사용한다.
- `runner/v113_local_web_api.py`: `/`, `/assets/styles.css`, `/assets/app.js`를 지정된 로컬 디스크 파일에서만 직접 제공하고, 소스 계약 `v108_native_consumable_inputs`에서 `/api/v1/options`를 내준다. 기존 Host/peer/same-origin/CSRF-토큰 검증 그대로 적용. 정적 파일은 공개된 loopback GET 3개만 예외. **외부 origin/Host 거부, 공개 네트워크에 바인딩하지 않음**. 동적 API는 세션 토큰 필요. Content-Security-Policy 기본 전부 차단, 자체 JS/CSS·자체 HTTP 통신만 허용, 캐시 비활성화, iframe 차단, sniff 방지.
- `tests/test_v114_local_web_ui_offline.py`: 실제 HTTP로 HTML/JS/CSS 및 Content-Type/CSP/Host/Origin, 필수 UI 입력 ID/리소스 경로, 소스 관측 옵션 목록·영약 잠금, 정적·옵션 GET의 세션 파일 비변경 등을 테스트. Node `--check`로 JS 문법 검증.

**정확성 불변:** SimC/Native 최적화 엔진, 기존 여섯 Native JSON2/영수증, B=G+J+F, T=B+O, 기름 O 단회, 특수 L 하한, 장신구 스탯 예산 밖, 95% 의미 모두 변경하지 않음. 기존 징벌 성기사 실제 Windows `179517.9936773854 DPS/264.49327569785953 SEM, B3150/O32/T3182`, Native6/6 및 추가 Native0·캐시6/6 증거 재사용. **하지만 이 실제 Windows 세션의 원본 여섯 JSON2 파일을 외부에서 다시 SHA 계산한 독립 검증은 여전히 아님.**

## Windows에서 브라우저 페이지 미리보기 (개발용)

**중요:** 지난 v109 의존성 불일치 실패를 피하려면 두세 파일만 낱개 교체하지 말고 **최신 격리 브랜치 전체**를 새 폴더에 내려받아 압축을 푼다. 사용자 `%USERPROFILE%\\SIMC_Secondary_Optimizer\\runs\\abca493c00d6ee2599f1` 폴더·기존 `simc.exe`와 캐시는 전혀 이동/삭제하지 않는다.

PowerShell / CMD를 새 프로젝트 폴더에서 열어:

```powershell
py -3 -m pip install -r requirements-web.txt
py -3 runner/v113_local_web_api.py --port 8765
```

서버 콘솔을 그대로 둔 채 Edge/Chrome에서 **`http://127.0.0.1:8765/`**를 연다. (이 주소는 개인 PC loopback이고 외부 사이트가 아니다.)

최초 검증은 **SimC 실행/재개 버튼 누르지 않고**, 페이지 하단 **기존 세션 ID로 열기**에 `abca493c00d6ee2599f1`을 입력해 `열기` 버튼만 누른다. 그러면 기존 로컬 `V106_USER_RESULT.json`을 Native0회로 읽어 관측 DPS·SEM·비율·95%를 보여준다. 브라우저 새로고침 시 마지막 세션 ID를 복원하는지도 확인할 수 있다. Windows 로컬 화면에서의 실제 클릭 성공은 **아직 사용자 실기 결과가 도착해야 증명된다.**

SimC 새 작업 실행을 직접 요청해야만 Native 호출이 일어난다. 취소는 기존처럼 현재 SimC 한 건 완료 후 처리된다. 기능별 디자인/오류 원문/브라우저 리프레시 후 진행 제어를 더 다듬는 것은 P1-WEB-3, 더블클릭/포트 자동할당/자동 브라우저 열기/설치·웹뷰 패키징은 P1-WEB-4다.

## 품질·검증 증거와 한계

- [P1-WEB-2 Linux/Windows CI #40414515436](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40415052508): **Linux Python3.12 HTTP/UI 30 PASS/0 FAIL, Windows Python3.14 HTTP/UI 30 PASS/0 FAIL**, Node JS syntax PASS, 파일/코드 컴파일과 pilot PASS. 모든 브라우저 관련 테스트는 **HTML 정적/API HTTP 검사**이며 실제 Chrome·Edge 인터랙션 실기는 미실시. 신규 Native0회.
- 심각한 배포 기능을 아직 구현했다고 주장하지 않으며, 현재는 개발자용 Python 의존성 설치와 콘솔 실행이 필요하다. 미래 호환성을 위해 UI→로컬 API→엔진 분리 유지. 클라우드 호스팅/Windows main branch 통합/공식 v003/Work OS M0/Project Sources/UI 적용 **없음**.

**다음:** 사용자 Windows Edge/Chrome에서 기존 ID 복구 확인(추가 Native0회); P1-WEB-3에서 UI·HTTP 동작/실패 경로·동시성/보안/브라우저 리로드를 통합 검증. 그다음 WEB-4에서 사용자 관점 원클릭 실행 및 배포.
