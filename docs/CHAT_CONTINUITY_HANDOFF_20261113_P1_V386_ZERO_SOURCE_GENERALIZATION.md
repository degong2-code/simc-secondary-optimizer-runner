# SIMC SECONDARY OPTIMIZER — v386 최신 단일 인계 (2026-11-13)

> **v386 작성 후 A1 코드 증분 (v387):** [WCL 전체 확장팩 원본 기반 탐색·같은 확장팩 raid/M+·DB2 조인 연결](development/notes/2026-11-13_p1-v387-a1-all-expansion-source-discovery.md). `v155.select_midnight_expansion` 제거, `v155 → v242 → v163 → v216` 후보 원본 경로 갱신·새/보강 오프라인 회귀 작성, **선택 순수 함수 10 스모크 PASS**. 아직 전체 Python/Actions/정상 API 키 실제 ZERO-SOURCE 미실행이므로 **A1 PENDING_SCOPE**. 아래의 'v155 Midnight 하드코딩 남음'과 '다음 제거' 문구는 이 증분 **이전 이력**이므로 우선 읽지 말고 최신 실제 GitHub HEAD/이 노트를 따른다. 다음 작업은 **새 회귀 실제 실행 및 권한 있는 현 시즌 실 원본/조인 증거 확보**다.

> **v387 후속 사용자 결정 — 최종 앱 파일 구성/인계:** [배포 파일 후보 자동 TXT·파일별 담당 기능/78요소 추적](development/APP_PACKAGE_FILE_REGISTRY_20261113.md). 완성 소스 복제 폴더를 만들지 말고 `v181_windows_beta_packager.select()`의 기존 ZIP 선정 로직을 그대로 TXT(`--list-files`)로 출력. ZIP `V181_PACKAGE_MANIFEST.json`은 실제 파일명·SHA, `FILE_MAP/FILE_INVENTORY`는 기능·테스트 지도, **78개 원장**은 READY 상태 정본이다. 78개 요소↔Python 파일은 **다대다** 관계이며 한 파일 고친 뒤 연결 회귀 확인. 현재 ZIP은 베타 후보이지 독립 EXE/최종 승인 패키지가 아니다. 이번 `v181` packager+test 증분은 **코드와 새 회귀 테스트 추가만**, 최신 전체 Actions/Windows/Native PASS는 미확인. A1 개발 우선순위 유지.

## 0. 이 문서를 새 채팅에서 가장 먼저 읽기

**최신 사용자 직접 결정 및 작업 지시:**
- **현재 실제 시즌에서 ZERO-SOURCE 제로베이스 자동 발견이 성공하면 '미래 시즌 대응 범용 엔진 기능'은 PASS.** 아직 공개되지 않은 미래 데이터의 사전 인증이나 미래 시즌 실 실행을 기다리지 않는다. 정상 API 키·출처 접근은 기본 전제이고, 현재 시즌/확장팩 ID·수치/DB/완성 프로필을 선주입하거나 GPT가 검색·판정하면 안 된다. 최신/활성/시즌/확장팩/시간·빌드·콘텐츠 관계 등 실제 출처 구조를 이용한 **비하드코딩 결정 로직**을 검증한다. 세부 정본은 [최신 검증 정책](development/POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md).
- **78개 항목 A1~H6을 각각 추적·처리**, 하지만 78번 Native나 78개 독립 인증 Gate는 아니다. 현재 범위/역사 범위/ENGINE 범용 PASS/SEASON READY/USER-E2E 최종 PASS는 별도 칸. 78개 적용 범위 완료 **이후** 정답 없이 현재 실제 시즌 엄격 ZERO-SOURCE→USER-E2E 최종 시험 필수. 시험 실패 시 과거 성공 영수증 대조로 첫 결함 stage를 찾는다.
- 다음 채팅에 **인계를 요청했다고 즉시 코드를 변경하지 않는다.** 새 채팅 첫 응답은 아래 문서·실 GitHub HEAD/증거를 읽고 현재 상태·다음 ID를 복원한 다음 STOP; 사용자 후속 `진행`에서만 격리 브랜치 제품 개발·테스트·커밋. 기존 주 제품 개발 채팅을 다른 채팅으로 이전하거나 main 병합/공식 승격하는 권한이 아니다.
- 우선순위: **최신 사용자 직접 결정 > 충돌 없는 승인 v1.4.3/v1.4 정책 > 실제 GitHub 격리 HEAD·Actions/Native 원본 > v385 이하 역사 노트.** 정책을 GitHub에 기록했다고 Project UI/Project Sources/Instructions 실제 적용으로 주장하지 않는다.

## 1. GitHub 정본/읽을 순서

저장소 **`degong2-code/simc-secondary-optimizer-runner`**, 격리 개발 브랜치 **`probe/chat-cache-v035-20261024`**. **이 인계에 적힌 SHA는 생성 당시의 역사값일 수 있으므로 실제 최신 HEAD와 Actions는 반드시 재조회**. main, v003 immutable, 사용자 제공 원본, Project UI, Work OS M0·Shared State·공식 승격은 별도 권한.

1. **이 인계** → [최신 일반화 정책](development/POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md) → [운영 헌장 §11·§12](development/OPERATING_CHARTER_FUTURE_SEASONS_AND_EVIDENCE_20261113.md).
2. [78개 유일 원장](development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md) → [START_HERE](development/START_HERE.md) → [PROTOCOL](development/PROTOCOL.md) → [INDEX](development/INDEX.md)·[FILE_MAP](development/FILE_MAP.md)·[EVIDENCE_INDEX](development/EVIDENCE_INDEX.md)·[DECISIONS](development/DECISIONS.md).
3. 필요할 때만 [승인 설계 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)와 해당 ID의 소스/시험/원본 영수증. [v382 역사 인계](CHAT_CONTINUITY_HANDOFF_20261113_P1_V382_78_ELEMENT_READINESS.md)는 성과/과거 정책 복원용이며 이 문서보다 선행하지 않는다.

## 2. 제품 범위/불변

- 증강 제외 **26 DPS** 전문화. 현재 장비 재분배/장비 파밍 추천/전 시즌 아이템 DB가 아니라 **목표 ilvl(기본334) 또는 수동 최종 CHMV T에서 치명·가속·특화·유연의 최적 절대 rating**을 SimC DPS 최대로 찾는다.
- 일반 사용자는 캐릭터·특성·종족·장신구2·선택 특수장비·장식2까지·기름/보석/영약/마부·전투조건만 입력. 내부에서 대표 일반장비·무기 성능·주능력·티어5 ID 중 유동 4pc·SimC 프로필을 구성; 선택 업로드 프로필의 현재 장비는 최적화 총량으로 복사하지 않음.
- 새 시즌은 **G/J/F/O 전부 원본으로 자동 산출**. `G` 일반 장비/무기, `J` 기본 최고품질 보석, `F` 검증 최고품질 영약, `O` 손별 기름 고정. `B=G+J+F; T=B+O; c_final=c_base+o`. 수동 T 우선, L은 G 포함·하한 보호/재가산 금지, E/O 한번만 계산, 장신구 정적 능력치는 자유 G 밖. 미관측 값 0 금지. 제작 장비 초기 50:50은 L 아님.
- 품질은 효과·조건·범위 동등성과 열등하지 않은 최고 등급만 일반 UI 표시. 일반 임시 마부 전체 제외; 영구 E와 별도 기름 지원. 확장팩 전용 특수 효과/모듈은 선택형. Policy A는 실제 필수 증거 확인 후 자동 등록, 미선택 항목 미관측은 BASE READY 차단하지 않음.
- SimC가 proc/APL/장비효과/DPS를 담당. 앱은 수집·예산·옵션·JSON2 정적 rating·DPS/SEM/95% 통계·관측 1순위/근접 대안·캐시·취소/재개를 담당. 독자 효과 엔진·불필요한 전수 Native·기존 최적화 알고리즘 새로 구축 금지.

## 3. 최신 78개 운영/검증 원칙

- A11+B12+C14+D9+E9+F7+G10+H6 = **78개**. **A1부터 순차로 점검**하되 구현·의존성은 묶어 최소 실행 가능. 각 항목에 기존 코드/증거→실 소비 필드/원본 소유자/시즌·빌드·SHA→실제 제품 연결→필요한 국소 수정→재현 가능한 PASS/FAIL→기록/차단 이유→다음 ID.
- 최신 사용자 결정: **미공개 미래 시즌 원본은 검증 불가능한 것이 당연**하며 그것을 기능 미완료 사유로 계속 남기지 않는다. **코드가 현재 실제 시즌을 AI 없이 스스로 찾고 필요한 자료를 정확히 가져오며, 정답 하드코딩 없는 원본 구조 기반 로직임을 보인 ZERO-SOURCE + 다른 시즌/ID/날짜 변형 회귀가 PASS면 `ENGINE_AUTODISCOVERY_PASS`**로 완료. 단, 실제 새 시즌이 나오면 그 시즌의 ITEM/GJFO/선택 환경 증거·호환성은 재검사.
- 독립적인 판정: `ENGINE_AUTODISCOVERY_PASS` ≠ `CURRENT_SEASON_SOURCE_READY_SCOPED` ≠ `CURRENT_SEASON_ZERO_SOURCE_USER_E2E_PASS`. 현재 실제 시즌 자료의 적격성/아이템 효과·수치 계산과 완제품 통합은 별도 단계. 후보/미확정 WSE를 0 또는 임의 시즌 READY로 바꾸지 않음.
- 시험의 API 키·권한·승인 원본 접근은 **정상 준비 조건**. 개발자/AI가 직접 최신 시즌을 보고 값을 넣는 것은 불가. `ZERO-CONTRACT`(합성)·`ZERO-INSTALL`(같은 시즌 번들 재사용)·`ZERO-SOURCE`(원본 새 수집, 기존 정답 미주입)·`USER-E2E` 구별. 최종 ZERO-SOURCE+E2E는 78개 지원 범위 닫은 뒤 필수.
- 항목별 코드 HEAD/시험 HEAD, 원본 요청/응답·SHA·빌드·실 Native/Actions·cache reuse와 증거 범위, 직접 확인한 PASS/FAIL/NOT_OBSERVED를 기록. 실패하면 **마지막 성공 단계→첫 status/missing·G/J/F/O 소유자 미일치→관련 78개 ID→동일 원본 영수증 비교**.
- **자원:** Native 수·SimC iterations·중복 다운로드·CPU/메모리/I/O·실행시간·static/DPS 캐시 재사용 검토. 같은 시즌 static item 캐시는 SimC revision만으로 폐기하지 않음.

## 4. 지금까지 실제 확인된 상태 (v385까지)

- 현재 원장: **3개는 역사 조건 제한 `READY_SCOPED`** — A10/A11/G2, KR 빌드 `12.1.5.70783`/ilvl334/4일반보석/O0/기존 Windows Actions/설치·Native 영수증; 나머지 **75개 `PENDING_SCOPE`**. 역사 3개를 현재 새 HEAD의 범용 완료 3개로 간주하지 않는다. [v383 원본 재조회](development/notes/2026-11-13_p1-v383-a10-a11-g2-archived-native-receipt-reuse.md).
- v343/v344 Windows 70783 기본 G2850 J92 F165 O0 B=T3107·v212 설치, 환경 Native3; v343 DPS Native12/v344 Chrome DPS Native64·취소·재개. **현재 HEAD의 신규 Native PASS 아님**.
- v384 **실제 UI 코드**에 사용자가 원하는 `source_compilation.missing`, G/J/F/O 원본 소유자 상태, 설치 manifest SHA 등을 **허용 목록으로만 축약·수동 복사**하는 진단 기능 추가; V8 분리 테스트 PASS, Windows 실 클릭/전체 pytest는 미확인. [v384 기록](development/notes/2026-11-13_p1-v384-season-evidence-copy-diagnostic.md).
- v385 A1부터 순차 개발 시작: **같은 빌드에 기존 봉인 Wago 영수증이 있을 때 `season_change`·`expansion_change` 명시 요청의 구형 원본 재사용 차단**, 기존 `item_content_change` 코드 보존, 다른 빌드는 기존 v216로. `runner/v113_local_web_api.py`와 `tests/test_v113_local_web_api_offline.py`를 변경·테스트 **추가**했으나 신규 pytest/Windows CI 아직 미실행. [v385 기록](development/notes/2026-11-13_p1-v385-a1-season-identity-refresh-boundary.md). A1 **PENDING_SCOPE**.
- **A1 현재 확장팩 비고정 자동 식별 미완:** `runner/v155_season_api_probe.py`는 WCL expansions에서 이름 `midnight`을 찾아 `midnight_zones`만 조회, `runner/v242_authenticated_season_source_stage.py`의 현재 provider scope도 `MIDNIGHT_ONLY_UNTIL_EXPANSION_PROOF`; `v163_zero_seed_db2_join.py`는 WCL/동일 빌드 DB2 관계를 추출해도 `season_membership_completely_verified=False` 표시. `v289` 공용 KR 빌드 발견은 시즌 자체의 승인 근거가 아님. [v347 비밀키 없음에 따른 정확 PENDING](development/notes/2026-11-12_p1-v347-credentialless-gjfo-current-once.md)은 **정상 키가 갖춰진 범용 엔진 테스트의 실패**라고 주장하면 안 된다.

## 5. 다음 A1 작업 (사용자 `진행` 이후에만)

1. **v385에서 작성한 HTTP 오프라인 회귀를 실제 실행**하여 기존 같은 빌드의 봉인 stage 0재사용/422 안전 차단, 새 빌드 기존 v216 연결, 정상 캐시 재사용을 확인. 실패 시 원인·수정 먼저.
2. **v155의 'Midnight' 문자열 하드코딩을 제거하는 기존 v242→v163 소스 관계 기반 자동 발견을 최소 확장**. WCL expansion `id/name`만으로 현재 시즌 확정하지 말고, Blizzard 동적 시즌·DB2 same-build map/raid·콘텐츠/유효 시점의 실제 필드로 후보를 좁혀 선택. API 호출수 상한·비밀키 비노출/타임아웃/불명확 후보 fail close, 미선택 자료 전수 수집 금지. v216/v212 승인 Gate는 그대로.
3. 다른 확장팩 이름·ID/시즌/빌드·복수 후보·필드 누락을 합성한 **시즌 하드코딩 방지 회귀** + 실제 정상 권한 있는 **현재 시즌 ZERO-SOURCE 원본 자동 발견·수집 시험**으로 A1 ENGINE PASS 판정. 미래 출시를 기다리거나 미출시를 미완료 근거로 쓰지 않는다. 실제 현지 원본 접근 제한은 정확한 BLOCKED와 필요한 외부 권한을 분리 보고.
4. A1이 기준을 충족하면 근거·SHA·실 Actions/Native 구분하여 `READY_SCOPED`/ENGINE PASS, 이후 A2~A11→B→C→D→E→F→G→H. 인수 시험은 마지막.

**실제 코드 변경/기록은 오직 격리 브랜치.** 기존 프로덕션 원본·main·Project UI는 건드리지 않는다. '잘 모르면 다른 대화 추측' 대신 이 정본과 실제 GitHub 코드를 읽는다.

## 6. 새 채팅 첫 메시지용 짧은 프롬프트

> **SIMC SECONDARY OPTIMIZER v386 이어 개발.** 격리 저장소 `degong2-code/simc-secondary-optimizer-runner`의 실제 최신 HEAD를 조회하고 `docs/CHAT_CONTINUITY_HANDOFF_20261113_P1_V386_ZERO_SOURCE_GENERALIZATION.md`, `docs/development/POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md`, 운영 헌장 §11·12, 78개 원장과 A1 v385 코드를 읽기 전용 복원하라. **최신 사용자 결정:** AI·정답/캐시 미주입, 정상 API 키·원본 접속을 제공한 현재 시즌 ZERO-SOURCE 시험에서 코드가 확장팩·시즌·필수 자료를 범용적으로 자동 발견·검증하면 **미래 시즌 대응 엔진 기능을 PASS**로 인정. 미래 미공개 자료 실측은 선행 Gate가 아니다. 역사 3/78 READY와 현재 ENGINE PASS/SEASON READY/최종 USER-E2E를 분리한다. A1부터 순차 검증·기록, v155 Midnight 하드코딩 제거·실 원본/회귀를 다음 단계로 잡고 기존 구현·캐시를 재사용하라. main/공식 UI/Work OS 변경 금지. **첫 응답은 복원 결과만 보고 STOP**, 사용자 `진행` 후 실제 개발에 착수.
