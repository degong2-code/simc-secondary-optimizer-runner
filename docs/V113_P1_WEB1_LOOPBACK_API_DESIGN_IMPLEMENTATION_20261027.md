# v113 P1-WEB-1 — 로컬 웹 API 연결, 기존 Windows SimC 보존

**적용일:** 2026-10-27 KST. **상태:** 격리 GitHub 브랜치 구현 및 Linux/Windows 오프라인 API 회귀시험 PASS. **아직 실제 브라우저 HTML 앱, 로컬 PC 서버 사용자 실기, 웹뷰 설치형 앱은 완료되지 않음.**

## 사용자 확정 제품 방향

개인용 로컬 웹앱 우선. HTML/CSS/JavaScript 웹 UI → `127.0.0.1` Python HTTP API → 기존 v106 세션 컨트롤러 / v098→v096→v094 Native 어댑터 → 로컬 `simc.exe`. 이후 같은 웹 UI를 pywebview 등 설치형 앱으로 감쌀 수 있고, 필요한 경우 클라우드 실행기를 별도로 연결할 수 있도록 **UI와 계산 프로세스의 입출력 계약을 분리**한다. 지금은 별도 클라우드·DB·React·서버 작업 큐·장비 DB·새 최적화 엔진을 만들지 않는다.

최종 대상은 **딜러 27개(증강 기원사 포함), 탱커·힐러 제외**. 사용자 입력을 내부 대표장비·티어 4개와 목표 ilvl(기본 334)/최종 CHMV T로 전환하는 기존 소스 기반 경로 6개만 실제로 연결됨. 장비 추천과 파밍 경로 없음. 공식 `T=B+O`, `B=G+J+F`; 기름 O 한번만, 정확 L 하한, 트링켓 고정 스탯 자유 G 밖, 95% 비교만 표기. SimC 원본 효과/APL/DPS 계산 변경 없음.

## 구현 파일

- `runner/v113_local_web_api.py`: FastAPI 단일 로컬 API. 이미 설치된 사용자 세션 저장소(`%USERPROFILE%\\SIMC_Secondary_Optimizer\\runs`)와 기존 `runner/v106_user_session_controller.py` worker를 호출하는 **얇은** 어댑터. `GET/status`, `GET/result`는 기존 디스크 파일로 복원, 브라우저 새로고침으로 프로세스·캐시 제거하지 않음.
- `requirements-web.txt`: `fastapi>=0.115,<1.0`, `uvicorn>=0.30,<1.0`. 테스트는 `requirements-web-test.txt`의 `httpx`를 별도 추가.
- `tests/test_v113_local_web_api_offline.py`: 실제 FastAPI HTTP TestClient를 이용한 8개 신규 함수 테스트(기존 18개 사용자 세션·Windows SHA 테스트와 총 26). 포트·Host / Origin / 로컬 세션 토큰 / CSRF / 요청 Content-Type / traversal, 6개 기본 전문화, 실제 기존 소스 프로필 B/O/T 3150/32/3182 zero Native 준비, 세션 완료 결과 95% 표시, 중복 실행·취소 신호, 캐시 미완성 선차단, 상태 조회 파일 무수정. `subprocess.Popen` mock만; 실제 Native 호출 0.
- `.github/workflows/v113_local_web_api_offline.yml`: [Linux Ubuntu 24.04 / Python 3.12와 Windows 2022 / Python 3.14 CI #40359841345](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40359841345) 각 **26 PASS/0 FAIL**. 외부 서버나 SimC Native 시험 없음.

## HTTP 계약 (v113 · 로컬 사용자만)

| Method | Route | 동작 |
| --- | --- | --- |
| GET | `/api/v1/health` | server/status 및 현재 연결된 6개 DPS 전문화 수 |
| GET | `/api/v1/bootstrap` | 브라우저 동일 출처의 **서버 프로세스 임시 토큰** 및 지원 전문화 목록 |
| GET | `/api/v1/defaults` | v106에서 검증된 6개 전문화의 입력 기본값 |
| POST | `/api/v1/sessions/plan` | 사용자 기본 입력 검증 → 기존 v098 source-locked 프로필/manifest + B/O/T 계산; **SimC 0회** |
| POST | `/api/v1/sessions/start` | 동일 사용자 계획 생성 후 기존 v106 Native worker 시작; 실제 Native는 사용자 명령에서만 |
| POST | `/api/v1/sessions/{id}/resume` | 기존 identity/manifest/binary SHA 검증 후 동일 세션 worker 재시작 |
| POST | `/api/v1/sessions/{id}/cache-only` | **완료된** 6 Native+영수증 선확인, 기존 `--cache-only` worker만 실행; 6/6 캐시 검증 또는 차단 |
| POST | `/api/v1/sessions/{id}/cancel` | OS lock/작업 진행 중인 경우만 CANCEL 신호; **현재 Native 한 건 완료 후 중단** |
| GET | `/api/v1/sessions/{id}/status` | 기존 V094 progress / v106 worker 상태 / 취소 요청 표시 |
| GET | `/api/v1/sessions/{id}/result` | 기존 v106 실제 95%-only 최종 결과; SimC 재실행 없음 |

POST 계획/시작 요청 구조: `{"controls": <v106 user_scenario controls>, "binary": "C:...\\simc.exe", "revision": "7bc1071", "static_cache": null}`. API 리턴은 session ID만 돌려주며 사용자의 바이너리 경로·특성 코드·원본 프로필은 응답에 임의로 덤프하지 않음. 기본값 endpoint는 소스 프로필 기반 (개인 캐릭터 정보 아님).

## 로컬 보안·운영 결정

- 서버는 `127.0.0.1`만 바인딩. 원격 IP 및 Host가 `127.0.0.1[:port]`가 아닌 요청 거부; DNS rebinding 경로 차단.
- API 호출은 동등 origin(`http://127.0.0.1:<port>`)만 허용. `Sec-Fetch-Site: cross-site` 차단. 모든 실제 데이터·실행 endpoint에 임시 `x-simc-local-token` 요구(health/bootstrap 예외); 허가 없는 다른 출처 웹사이트가 로컬 SimC 실행을 유도하지 못하게 함. POST JSON Content-Type 강제.
- 20자리 세션 SHA ID만 허용, 원본 폴더를 기반으로 resolve 후 root 밖 경로 거부. 임의 파일 경로·원격 URL을 세션 ID로 전달할 수 없음.
- 웹 API는 원본 OS 파일잠금과 캐시 identity를 재사용. API 요청 파일은 표준 v106 세션 외 신규 데이터베이스가 없고, GET 상태 조회는 잠금 파일도 새로 생성하지 않음. 요청 중복은 API 프로세스 내부 mutex + OS worker lock으로 방어. **프로세스 밖 최초 동시 시작 race 등 전체 운영성 추가 강화는 이후 WEB-3.**
- 로컬 임시 토큰은 사용자 PC의 악성 프로세스 자체를 완전히 차단하는 인증 수단이 아님. 개발 단계에서는 공개 네트워크 binding·CORS 허용·원격 클라우드 모드를 지원하지 않음.
- **주의:** 기존 v096의 Native 완료 후 로컬 결과 폴더 자동 열기 등 Tk 시절 동작은 아직 별도 수정하지 않음. 추후 WEB-3/배포 단계에서 웹 UX에 맞춰 다룰 예정.

## 실행 (기술 검증용; 아직 HTML 화면 아님)

로컬 기존 작업 사본에서:

```powershell
python -m pip install -r requirements-web.txt
python runner/v113_local_web_api.py --port 8765
```

브라우저에서 `http://127.0.0.1:8765/api/v1/health`는 JSON 응답만 제공한다. 이는 앱 화면이 아니다. 프로세스를 종료하면 로컬 API도 종료되며, 기존 `runs` 캐시/세션은 남는다. 전체 브라우저 화면과 더블클릭 시작은 각각 **P1-WEB-2 / P1-WEB-4** 후속 과제다. 이번 WEB-1 단계에서 사용자에게 기존 Native 6회를 다시 돌려달라고 요청하지 않는다.

## 기존 실제 Windows 증거 재사용 — v111 / v112 구분

- 사용자 Windows 실제 징벌성기사 Native6/6 PASS, B3150/O32/T3182, 관측 DPS **179517.9936773854**, SEM **264.49327569785953**, 95% 비교 선택쌍 방향 지지, 관측 네 후보 / 실질 근접대안0, 전역 최적 입증 아님.
- 사용자가 추가 제공한 `V112_CACHE_REPLAY_RECEIPT.json` 및 `V106_WORKER.log`에는 같은 Windows 세션에서 `PASS_CACHE_ONLY`, **기존 Native 누적6, 캐시 적중6, 추가 Native0**, 기존 결과 동일, 원본 Native JSON2 **6개 SHA**가 선행 `V094_RESULT.json`의 기록과 모두 일치한다. 이는 **Windows 실제 캐시 재생 사용자 영수증으로 확인**. 다만 원본 여섯 JSON2 파일 자체를 별도로 업로드·바이트 검사한 것은 아니므로 독립 실측 해시 검증과 구별. 취소·부분 재개 사용 실기는 미완료로 유지.
- 최초 v112 사용자 실기는 **실제 Windows/3.14.5** 사용자 환경. 이번 v113 검증은 별개 **Windows Actions/3.14 HTTP 오프라인**이며, 새 웹 로컬 서버를 사용자 PC에서 실기 검증한 것으로 간주하지 않음.

## 이후 작업

**P1-WEB-2**: 지금 추가된 같은-origin local API로 브라우저 HTML/CSS/JS UI 제작. 우선 완료된 원본 6/6 캐시 및 기존 v106 결과로 출력 검증, 새 Native 미호출. P1-WEB-3: 새로고침 복구·취소/재개·세션 동시성·오류 원문과 UX 안정화. P1-WEB-4: 더블클릭 실행/포트 선택/브라우저 자동 열기/웹뷰 포장. 향후 클라우드 서비스 전환은 보류.

**Authority:** user-approved design direction only; isolated GitHub branch change, **main merge / v003 immutable / Work OS M0 / Project UI Source·Instructions 적용 없음**. 기존 주 제품 개발 채팅 권한 불변.
