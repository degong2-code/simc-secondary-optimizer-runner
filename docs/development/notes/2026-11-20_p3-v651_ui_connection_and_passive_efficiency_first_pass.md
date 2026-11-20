# P3 v651 — 사용자 UI/API 연결 감사 및 저비용 성능 개선 1차 (2026-11-20)

**사용자 결정:** 실제 PC의 `V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH` 원본 진단 영수증은 추후 제공. 그 전까지 UI 디자인·동작 연결·중복 작업·실행 효율을 검사하되, 기존 SimC/GJFO/서명 세션·Native64와 안전 경계는 보호한다.

## 1. 실제 확인한 자료와 범위

- 조사 시작 격리 HEAD: `fa2babcc47a6d72535c6881555ebe8ac986d5edc` (v648 원인 분리 실험 원복 이후 코드 보존 상태).
- 사용자 제공 전 ZIP 그대로: v647 Actions `#44677378569` / artifact `#14603195195`, 내부 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip` SHA256 `debb25affa7e0539f2197a267deb5286d566b57510cec1d3412e838b28edfdd2`; 283 제품 파일 + manifest. **이것은 변경 전 소스 참조본**이며 새 ZIP을 만든 것이 아니다.
- 실제 `runner/webui/index.html`·`styles.css`·`app.js` 및 `runner/v113_local_web_api.py`, `v293_local_longrun_session.py` 함수 읽기: `read_status()`는 `V291_PROGRESS.json`과 작업자 파일을 읽고, 브라우저는 이전에 idle/paused에서도 1400ms 간격의 동일 status GET을 반복할 수 있었다.
- 정적 UI 연결 검사: `index.html` ID **200개**, 중복 ID **0**, JS 직접 `$(id)` 참조 중 미존재 ID **0**, `label for` 대상 누락 **0**, 정적 `/api/v1` 호출 경로 **23종**과 서버 라우트 매칭 누락 **0**. 동적 session 경로는 서버 path parameter 패턴 대조.
- 임시 로컬 서버의 `/`, `/assets/app.js`, `/assets/styles.css`: GET200/정상 MIME, Python 3.13 Linux FastAPI TestClient (사용자 Windows CI 또는 Native가 아님).
- Headless Chromium **실 localhost 탐색은 실행 환경 정책에서 `ERR_BLOCKED_BY_ADMINISTRATOR`**로 접근 거부. 브라우저 네트워크/사용자 PC 기능 불량이라고 주장하지 않는다. 대신 승인 v647 HTML/CSS를 `page.set_content`으로 공급한 **정적 레이아웃**에 한해 320/390/768/1024/1440px × 3 views **15/15 가로 overflow 없음**을 관측. 실제 JS/API 동작·전문 사용자 시각 인수 대체 아님.

## 2. 구현된 두 가지 최소 개선 — JavaScript UI 전용

### A. Passive session status GET 빈도 절감 (v649)

- `runner/webui/app.js`의 기존 `renderProgress`·`beginPolling`에만 `state.nextPassivePollAt`을 추가했다.
- **서버 active=True: 기존 1400ms 간격 유지**. Active Native·진행률 반응성 불변.
- 서버 active=False + 저장 worker `RUNNING/QUEUED`: 5000ms. 곧 시작하는 작업/서버 재시작의 진행 전환을 확인한다.
- 서버 active=False + 그 외 pause/cancel/blocked/complete/idle: 15000ms. 사용자가 명시적으로 resume/restore/새 세션을 열 때 `pollOnce`는 타이머와 무관하게 즉시 실행하고, 새로운 session ID는 idle throttle을 초기화한다. 기존 네트워크 실패 `nextPollAt` backoff를 유지한다.
- I/O 비용: 중단된 탭 하나 기준 약 60초마다 42~43회 GET → 약 4회 GET 수준의 **이론적 요청 빈도 감소** (실제 측정된 사용자 부하·Native 실행시간 가속 수치는 아님). 다른 탭/외부 작업 재개는 유휴 화면에서 최대 약 15초 뒤 반영될 수 있는 교환관계가 있다. 해당 탭의 명시적 동작은 즉시 조회한다.
- `v293`/서버 status 파일·계산·캐시/세션 코드, polling 중 실행할 Native 횟수는 변경하지 않았다.

### B. 설치 장비 후보 정렬 재사용 (v650)

- `eligibleEquipment(group)`는 이전에 카드 선택·검색 `input` 마다 설치 카탈로그의 전수 후보를 복사·검증·정렬했다.
- `WeakMap`을 현재 `state.seasonGear` 카탈로그 객체로, `Map`을 장신구/특수효과 그룹으로 키잉하여 **같은 설치 목록의 정렬 결과만 재사용**한다. 같은 카탈로그 객체의 `choices[group]` 배열 reference가 바뀌어도 즉시 다시 정렬한다.
- 새 시즌 카탈로그 객체는 새로운 목록을 사용하며 이전 시즌 선택/READY로 재승격되지 않는다. 비활성 객체는 `WeakMap`에서 GC 가능. 기존 검색 필터링·정렬 순서·80개 카드 최대 노출·선택 `item_id`·버튼 DOM 연결은 불변.
- 큰 카드 DOM 전면 재작성, 비검증 item 허용, 신규 이미지/DB, JS 프레임워크 추가는 하지 않았다. 장비 데이터의 원래 내림차순/선택 로직과 최종 서버 검증이 권위자다.

## 3. 검증 — PASS와 미실행 명확 구분

- 실제 production `app.js`에서 해당 함수를 잘라 Node에서 실행한 **독립 오프라인 테스트 2개 PASS**: 중단 15초/active 1.4초/queued 5초/새 세션 즉시 조회/오류 backoff 존중; 장비 후보 유효 ID·정렬/동일 목록 재사용/choices 변경/새 시즌/해제 검증.
- `node --check` PASS (신규 로컬 편집 소스), 임시 localhost TestClient GET200 (3 paths). v647 정적 CSS 15조합 넘침 검사 PASS.
- 두 테스트를 **기존 v647 UI 회귀 파일 `tests/test_p3_v647_visual_hierarchy_offline.py`에 추가**했다. 테스트 harness의 `$()` 함수 인자를 보존하도록 진단 중 한 번 수정했으며 마지막 GitHub 원본에는 `String.fromCharCode(36)`로 기록. 기존 테스트 삭제·skip·완화 없음.
- 아직 이 새로운 커밋으로 **Windows 3.12/3.14 공식 v181 CI, 패키징 ZIP, 사용자 Chrome, 신규 Native/SimC 실제 실행을 수행·확인하지 않았다**. v647 #44677378569의 289 PASS/283파일 ZIP SHA와 v639의 실제 Native64·95%·재열람은 **변경 전 역사 범위**로만 재사용한다. 동일한 Windows PASS/ZIP 바이트가 현재 커밋에 발생했다고 주장하지 않는다.
- **새 SimC Native, G/J/F/O 원본 HTTP/DB2, Blizzard/WCL 인증 요청, 새 optimizer·효과 Gate, 캐시 강제삭제 모두 0.**

## 4. 사용자 제품 연결, 중단 및 권한

- 사용자가 결과 화면을 열어놓고 중단한 세션의 로컬 status GET을 줄이고, 설치 장비 검색·선택 시 정렬을 재사용하는 **기존 UI 경로**에만 연결됐다. UI HTML/CSS의 v647 승인된 선·하이라이트·서체는 변경하지 않았다.
- 기존 시즌/SimC 설치·원본 `v229` 코드, v217 stage fingerprint, 26 DPS 정책·L/E/O 회계·DPS/SEM/95%·취소/재개·중복 실행 차단은 변경하지 않았다.
- 배포 전 최소 확인: 현재 변경 커밋에서 테스트가 포함된 실제 Windows ZIP focused regression 및 추출·localhost UI (신규 Native 없이). 사용자 PC의 V229 영수증이 없어도 이 변경의 최소 QA는 독립 수행 가능하다. 브라우저 실제 시각 인수는 별도.
- **STOP:** UI 정적 구조·서버 경로 매칭에서 실제 실패 0, v647 디자인 추가 재작성 근거 부족. 변경 효과를 입증하지 못한 다른 구조 리팩터링·분기별 Native 전체 반복은 하지 않는다.
- 공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`. GitHub 격리 branch만 변경; main, v003 immutable, Project UI/Work OS/Shared State, 주 제품 개발 채팅 소유권 그대로.

**추가 효율 후보(미개발):** 장비 카드 DOM은 검색 입력 시 양쪽 80개 후보까지 재구성한다. 실제 성능 병목이 측정되기 전에는 이벤트 위임/가상화 등 대규모 UI 리팩터링을 도입하지 않는다.
