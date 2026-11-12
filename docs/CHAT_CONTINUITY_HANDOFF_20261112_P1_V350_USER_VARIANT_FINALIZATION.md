# SIMC SECONDARY OPTIMIZER — 2026-11-12 P1 v350 사용자 환경 분리·Windows 실사용 최신 단일 인계 정본

**역할:** 새 채팅의 첫 읽기 정본. [2026-11-11 v338 인계](CHAT_CONTINUITY_HANDOFF_20261111_P1_V338_PRODUCT_FINALIZATION.md)는 역사 기준으로 보존하고, 본 문서는 최신 사용자 결정 및 v339~v350 제품 완성 작업만 증분 정리한다. 원본 증거의 대체물·새 Native PASS·공식 승격 승인서가 아니다.

## 1. GitHub 실제 확인과 개발 권한
- 저장소: `degong2-code/simc-secondary-optimizer-runner`. 격리 작업 브랜치: `probe/chat-cache-v035-20261024`. **본 문서 작성 직전 실제 HEAD `3e93fcc9d1a0a323e24fb1ccf4c3c86e79417503`**, 기준 `main` HEAD `07133e0aaf738d6e4816a6486057b1cd49c018de` (2026-11-12 KST 확인). **본 문서를 커밋하면 격리 브랜치 HEAD가 변경되므로 새 채팅에서 반드시 다시 읽을 것.** `main`을 수정하지 않는다.
- 최신 사용자 직접 결정 > [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)와 충돌 없는 v1.4 계열 > 실제 GitHub 코드/Actions/Native 영수증 > 기존 v338·그 이전 이력. **26 DPS 전문화만**: 증강 기원사·탱커·힐러 제외. 역사 v1.4.1의 27 DPS 문구는 현재 정책이 아니다. GitHub 문서 작성과 ChatGPT Project Sources 실제 등록은 다르다.
- 개발은 격리 브랜치에서 연속성 유지; 기존 주 제품 개발 소유권을 MAIN/WORK나 이번 새 채팅이 임의 인수하지 않는다. **별도 승인 없이 `main` 병합, immutable v003, 원본 v016, Project Sources/Instructions 실제 수정, Work OS M0/Shared State·공식 승격 금지.** 사용자 요청의 이번 작업은 인계 문서 갱신일 뿐 제품 기능 개발 지시가 아니다.

## 2. 최종 제품 계약
- 기본 ilvl334 또는 **사용자 수동 최종 T**를 기준으로 미래 파밍 목표가 될 **치명/가속/특화/유연 절대 rating** 중 SimC DPS 관측 우세를 탐색한다. 26 DPS, 캐릭터/특성·장신구2·선택 특수장비·장식 최대2·보석·영약·기름·전투조건을 선택. 현재 장비 CHMV 재분배/장비 추천/시즌 전체 장비 DB는 제외.
- **`B=G+J+F`, `T=B+O`, `c_final=c_base+o`**. 새 시즌의 일반 장비 G·기본 보석 J·영약 F·선택 기름 O 전부 원본 기반 검증. 수동 최종 T 우선; L/E/O 중복·기름 고정치 재분배 금지. 장신구 고정은 자유 G 밖, 제작 초기 50:50은 L 아님. 검증된 최고 품질 선택지만 사용자 노출; 정확한 품질·효과·적용 범위가 미확정이면 해당 항목 보류.
- SimC가 효과/proc/APL/DPS 담당, 앱은 ID/ilvl/옵션·정적 예산/하한/JSON2 rating·95% 통계·캐시·취소/재개·출력 담당. 최고 관측 DPS 후보와 95% 유의 우위/전역 최적 증명 분리. 기존 **v290 적응형·v293 신규 N56/최종 확인 N320** 재사용; N 없는 역사 세션은 legacy35.
- 환경 Build는 사용자 요청 시 실행. 새 시즌 최초 구축과 사용자 선택 변경은 검증/예산 재산출이 필요하나 **동일 시즌·동일 조건의 유효 원본과 Native/결과 캐시는 재사용**한다. 사용자 키/API를 서버에 상시 맡기는 구조는 채택하지 않는다.

## 3. 최근 사용자 결정과 v350 반영 상태 — 가장 중요
- 사용자가 Windows 개인 PC 베타에서 직접 확인한 문제: 환경 수집 중 진행 표시 부재, 소켓 총수/특수 포함 여부 혼란, 환경 단계에서 특수보석·영약·기름 ItemID 입력 요구, 시즌 빌드 `12.1.5.70783`의 `SOURCE_SEASON_JOIN_PENDING` 및 연쇄 미완료27항목.
- **최신 승인 설계:** 시즌 환경 구축은 **공통 원본·아이템 종류/품질/적용 조건·대표 장비·G/J/F/O 근거를 자동 검증**하고, 개인의 전체 소켓 수(특수 포함)·특수보석·영약·기름 사용/물리 ID는 **최적화 단계**에서 선택한다. 일반 사용자에게 ItemID 조사를 요구하지 않는 것이 최종 목표. 제로베이스는 구시즌 값을 복사하지 않는 것이지, 새로 검증한 같은 시즌 Wago/SimC 원본을 매번 다시 내려받는다는 뜻이 아니다. 이름은 “시즌 환경 자동 확인·구축(검증된 동일 시즌 원본 재사용)” 방향.
- **실제 v350 구현:** [개발 노트](development/notes/2026-11-12_p1-v350-common-season-user-variant-split.md). 시즌 공통 버튼은 내부 대표 일반보석4/특수0/기름0 기준을 사용; `runner/webui/index.html`에서 개인 소켓·특수보석·검증 설치 영약·기름을 최적화 양식으로 이동; `runner/webui/app.js`에서 공통 Build와 개별 구성 검증·준비 분리. `runner/v113_local_web_api.py`는 사용자 선택을 세션 계약으로 가져와 **소켓·특수 ID·영약 F·손별 기름 O와 같은 빌드/ilvl의 v212 설치 manifest SHA·v113 snapshot** 일치를 요구한다. 없거나 모호하면 422/Native0, 이전 4보석 G/J/F/O를 임의 재사용하지 않는다. 수동 최종 T 우선 정책 그대로.
- **구현 범위에 대한 제한:** 이는 “정확한 검증 설치 변형 선택·차단·예산/SimC 경로 연결”의 구현 및 테스트이지, 사용자가 8소켓/특수/영약/기름으로 **실제 새 v212 변형 READY를 생성하고 DPS Native까지 성공한 양성 영수증**이 아니다. 현재 검증된 선택 이름·품질 자동 등록 전체도 미완. 수동 ID는 고급 재현에만 남아 있으며 사용자 UX에서 완전히 사라진 것은 아니다. 실제 source/Build가 활성 시즌을 확정하지 못하면 기본 환경과 개인 변형 모두 PENDING.
- **v349 구현:** [진행·보석 UI 노트](development/notes/2026-11-12_p1-v349-user-season-progress-sockets-sourceitem-ux.md). 요청 중 애니메이션+경과 초 및 최종 원본 상태 요약; 서버 단계별 실시간 퍼센트는 미구현. “미해결 27건”은 독립 결함 27개도 실행 %도 아니며 상위 시즌 JOIN이 미확정인 결과의 연쇄. 소켓 수는 특수보석을 포함한 전체 수, 기본4/특수 선택시 총5 이상.

## 4. 최근 구현·검증의 확정 영수증과 한계
| 버전/범위 | 구현·실행 근거 | 입증하지 않는 것 |
|---|---|---|
| v337/v338 시즌 환경 | [v337 Windows 현재70783 빈 설치 root G2850/J92/F165/O0, B=T3107 Native3](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43000049793); [v338 통제 원본 실패·재시도·누락 차단](development/notes/2026-11-11_p1-v338-negative-season-source-recovery.md) | 미출시 미래 시즌의 모든 외부 원본 신규 READY |
| v344 실제 Windows DPS | [Windows Chrome→70783 G/J/F/O Native3 → 생존 N56·DPS Native64·중단/재개/결과 재열기 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208) | 개인 사용자 PC의 같은 조건, 전 26 DPS 전수 |
| v345 배포 ZIP | [실제 추출 ZIP CMD→Chrome 세션 저장/재열기 Native0](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43118748950); 역사 포함 v213 카탈로그 `70575` | 포함 카탈로그가 현 `70783` 시즌 READY라는 주장 |
| v346~v347 안전장치/무키 | v346 기본 64회/재개 v212 검증 설치 없으면 차단 [API PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43122643207); [v347 무비밀키 Wago/SimC 수집 성공·시즌 JOIN 불확정 PENDING](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43123280869), 환경/DPS Native0 | 공개 DB2만으로 활성 시즌·레이드 확정 |
| v348 사용자 소유 키 | [Windows WinCred 실 저장/조회/삭제·API 비반사/전달 각 306 테스트 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43129484124); [실제 추출 ZIP HTTP PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43130148906) | 실제 유효 사용자키 OAuth·활성 시즌 JOIN·GJFO READY |
| v349 UI·원클릭 | [Windows 배포 ZIP 및 UI/API CI PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43136010863) | 실시간 백엔드 단계 %, 개인 PC v349 직접 클릭 완전 검증 |
| **v350 개인 변형 분리** | [실 Windows ZIP #43141083314](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43141083314), [Web API Windows/Linux #43141083312](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43141083312), [source SHA compact](development/research_receipts/p1_v350_user_variant_windows_compact.json), [노트](development/notes/2026-11-12_p1-v350-common-season-user-variant-split.md). 272 source files/manifest, 미설치 8소켓·특수보석 422 Native0, 기존 4소켓 계획/WinCred 회귀 PASS | **새 8소켓/영약/기름 변형의 GJFO READY 양성 Native**, 사용자 키 기반 현재 시즌 JOIN, DPS/SEM 양성 Native |
| 공통 최신 문서 커밋 | [HEAD `3e93fcc9`에서 재사용 offline focused #43141662533 SUCCESS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43141662533) | 인계 문서 작성이 새 Native나 공식 승격이라는 증거 |

**개인 사용자 실제 관측:** 2026-11-12 사용자 화면은 인증 이후 `AUTHENTICATED_SOURCE_DISCOVERED_SEASON_JOIN_PENDING` / `DB2_WCL_CANDIDATES_JOINED_SEASON_CONDITIONS_PENDING` / Wago `REUSED_VERIFIED` / 최종 `SOURCE_SEASON_JOIN_PENDING`을 보여준다. 이는 인증 원본 **접근 및 후보 결합의 진척**이지 실제 `READY`나 해당 시즌 레이드 소속 최종 검증 성공이 아니다. 일반 DPS 계산은 아직 사용자 PC에서 이 조건으로 완료했다고 기록하지 않는다.

## 5. 파일/제품 호출 지도로 재사용할 것
- 안내·색인: [START_HERE](development/START_HERE.md) → [INDEX](development/INDEX.md) → [FILE_MAP](development/FILE_MAP.md) → [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md), [DECISIONS](development/DECISIONS.md), [PROTOCOL](development/PROTOCOL.md); 장기 A~G는 [PRODUCT_CANONICAL_STATUS](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md) 상단과 역사 본문 구별.
- 환경 A~E: `runner/v161_wago_db2_snapshot.py`, `v242_authenticated_season_source_stage.py`, `v216_environment_build_coordinator.py`, `v217_stage_execution_engine.py`, `v212_environment_manifest.py`, `v222_season_budget_contract.py`, `v271_user_socket_gem_layout.py`; 공식 한국어 `v335`·`v336`.
- 사용자/최적화 F/G: `runner/v348_windows_user_source_credentials.py` (WinCred), `runner/v113_local_web_api.py` (season build/variant lookup/422), `runner/webui/index.html`·`app.js` (최종 사용자), `runner/v098_target_user_scenario_bootstrap.py`, `runner/v139_pure_target_profile_composer.py`, `runner/v096_unified_product_entry.py`, `runner/v094_durable_inclusive_adaptive_runner.py`, `runner/v290_multiscale_adaptive_policy.py`·`v291`·`v293`; Windows `START_HERE_AUTO_SETUP_AND_RUN.bat`, `integration_probes/v181_windows_beta_packager.py`·`v181_windows_beta_live_http.py`. 회귀: `tests/test_v113_local_web_api_offline.py`·`test_v114_local_web_ui_offline.py` 및 연결된 focused Actions.
- 기존 정적 같은 시즌 원본은 **SimC revision만으로 폐기 금지**. DPS 캐시는 실제 SimC binary/revision·캐릭터/프로필·ilvl/특수장비·보석/영약/기름·전투조건·iterations SHA identity로 구분. 원본 프로필·이미 봉인된 세션·기존 Native 사용 범위에서만 재사용. no more N research/전수 Native/수동 API 원본 강제 취합.

## 6. 상태 분류와 현재 병목
- **완료/기존 기능 재사용:** DPS26 선택·표준 대표 장비/티어/프로필·웹·Windows ZIP/원클릭 BAT·본인 키 WinCred·기본 시나리오 v290/N56 및 95% 통계·캐시·취소/재개·v216 시즌 Build·한국어 시즌 이름 단계.
- **연결 완료·오프라인/Windows E2E PASS:** v350 공통 시즌/개인 설정 분리, verified v212 exact variant identity, 예산/SimC 실행을 미검증 조합으로 시작하지 않게 422 차단. 실제 Windows ZIP 3개 기본 계획 및 WinCred 경로 PASS, 추가 Native0.
- **실제 환경 양성 실증:** v337 특정 Ret334·v344 특정 Survival334 Windows 현재70783에서 환경3·DPS64. **v350의 사용자 변경 구성으로 새 Native 양성 실증 없음**.
- **실제 재현된 미완료:** 유효 개인 인증정보로 시즌 원본 접근 후에도 `SOURCE_SEASON_JOIN_PENDING`; 인증 데이터·Wago DB2 후보 결합만으로 최종 활성 레이드 소속 결론에 도달하지 않음. 이는 현재 P1 **가장 중요한 병목**. 가입/품질·장비 근거를 추정하여 READY로 승격하지 않는다.
- **미구현/부분:** 일반 사용자 이름 기반 모든 특수보석·영약·기름 선택지의 완전 자동 등록; 실제 신규 8소켓/선택 F/O variant 검증 설치 양성 경로 E2E; 개인 PC 최종 Native 결과 E2E; 백엔드 실 단계 진척/중단·재개; 미출시 새 시즌 G/J/F/O 최초 READY. 실패한 테스트와 아직 검증하지 않은 영역을 혼동하지 않는다.
- **제품 목표와 불일치·과거 접근 교정:** v349 이전에 소켓·특수보석/영약/기름 원본 ID를 환경 구축 사용자 입력으로 노출했다. v350에서 개인 설정으로 옮기고 고급 ID만 남겼으나 일반 사용자 품목명 자동 선택은 아직 완결 아님. GitHub Actions 중앙 생성 시즌 패키지와 배포 ZIP에 개발자 공용 비밀키 내장 제안은 **개인 로컬 독립성·키 유출 우려로 채택하지 않음**. 사용자는 본인 API Client ID/Secret 등록을 승인; Windows Credential Manager 저장. Python 설치 수동 반복 대신 동의형 원클릭 BAT 사용. 공개 Wago DB2는 무키 수집 가능하지만 시즌 JOIN 증명 그 자체가 아님.

## 7. 단기·장기 로드맵과 재개 조건
1. **P1-A STOP 신규 연구:** v350 구현을 다시 만들지 않는다. 사용자가 원하면 새 Windows 앱으로 개인 Blizzard/WCL 키와 현재 시즌 Build에서 `season_discovery`, `season_join`, Wago/SimC·raid 후보 원본의 **정확한 PENDING 이유**를 재현·추적한다. 개별 필수 검증 조건이 정확한 원본으로 충족되는지 한 지점에서 교정하고, 불필요한 전수 재수집·Native 없이 최소 테스트. 비밀값·토큰을 채팅/로그/영수증에 기록 금지.
2. **P1-B CONNECT 검증된 사용자 구성 양성 경로:** 시즌 JOIN 및 G/J/F/O 기본 READY 뒤, 대표 ilvl334/8소켓(특수 여부 명시)·검증된 최고 품질 F/O 중 한 조건을 기존 v216→v212 동일 시즌 원본으로 구성·봉인. 선택값 변경 → J/F/O 및 B/T(수동 T 우선) → 보석·영약·기름 SimC 프로필 → session SHA/cache identity까지 확인. 기존 설치본을 그대로 복사하지 말고 실제 필요 최소 G/F/O static Native만; 무조건 다전문화 DPS 반복 금지.
3. **P1-C UI 사용성:** 검증 품목명/최고 품질/선택 조건을 최적화 단계 자동 선택 목록으로 연결하고 원본 ItemID 입력은 개발 고급 모드로 한정. 시즌 Build 표제와 동일 빌드 재사용 의미 수정. 외부 원본 단계의 정확한 진행·취소 UX는 새 백엔드 구조를 만들기 전 재사용 가능한 stage receipt 확인. 기본 Windows 실행→최적화→취소·재개→DPS·SEM·95%·대안 결과 재확인.
4. **장기:** 새로운 시즌에서 소스 자동 G/J/F/O 및 공식 한국어/정책 A 완료, 선택형 시즌 콘텐츠 모듈, 26 DPS 실사용 확대와 캐시/속도 유지. 별도 새 알고리즘 연구·전 장비 DB·장비 추천은 하지 않는다.
- **작업 판단:** `REUSE / CONNECT / EXTEND / REPLACE / NEW / STOP` 순서, source/cached receipts와 GitHub latest HEAD first, 바뀐 범위만 검증; CPU/메모리/I/O/외부 API/Native 비용·추가 중복 요청 검토. 일반 사용자 인터랙션은 여전히 주 제품 개발 소유권/권한 준수.

## 8. 새 채팅 독립 복원 규칙
읽기 순서: **본 단일 인계 → [START_HERE](development/START_HERE.md) → [INDEX](development/INDEX.md) → [FILE_MAP](development/FILE_MAP.md) → [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md) → [PRODUCT_CANONICAL_STATUS](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md) 상단 → [DECISIONS](development/DECISIONS.md) → [PROTOCOL](development/PROTOCOL.md) → [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) → [v349](development/notes/2026-11-12_p1-v349-user-season-progress-sockets-sourceitem-ux.md)·[v350](development/notes/2026-11-12_p1-v350-common-season-user-variant-split.md) → 실제 HEAD 및 Actions/compact**. 누적 CURRENT·과거 인계 전수 재감사 금지. 정확한 작업 브랜치·`main` HEAD를 다시 조회하고 코드/증거와 문서 이력의 신분을 구분.
- **새 채팅 첫 응답은 읽기 전용 독립 복원 보고만 수행하고 즉시 STOP**. 실제 HEAD, 제품 구현·증거 범위, 완료/미실증/결함, v350 최근 작업과 사용자 승인, 병목, 로드맵, 권한을 보고한다. **사용자가 별도로 “진행”이라고 지시하기 전 코드·문서 수정, 테스트, 외부 수집, Native/Actions 실행, 커밋·병합·공식 승격을 시작하지 않는다.**

## 9. 새 채팅 시작 텍스트
이 인계 문서의 URL과 다음을 새 채팅에 전달한다: “SIMC SECONDARY OPTIMIZER `degong2-code/simc-secondary-optimizer-runner`의 `probe/chat-cache-v035-20261024`을 최신 실제 HEAD로 읽기 전용 독립 복원하라. 첫 문서는 `docs/CHAT_CONTINUITY_HANDOFF_20261112_P1_V350_USER_VARIANT_FINALIZATION.md`이다. 26 DPS/목표 CHMV 절대 rating, v290/N56/320·legacy35, v216 시즌 G/J/F/O, Windows v348 개인키·v349 진행 UI·v350 사용자 변형 분리를 구분하라. v350 Windows ZIP/422 PASS와 실 8소켓 양성 Native 미실증, 사용자 시즌 JOIN PENDING, 구 70575 카탈로그/현70783, 권한·캐시·Native 재사용을 정확히 보고하고 즉시 STOP. 내가 ‘진행’이라고 승인하기 전 어떤 개발/테스트/외부 실행/커밋도 하지 마라.”
