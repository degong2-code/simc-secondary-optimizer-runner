# SIMC SECONDARY OPTIMIZER · 개발 지식 시작점

> **최신 v398 (이전 A4 PENDING 문구보다 우선):** [A4 현재 Blizzard 인증 원본 4 index 출처·제품 소비 소유권 완료](notes/2026-11-13_p1-v398-a4-blizzard-source-owner-base-scoped-ready.md). [실 Python Actions #43364420119](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43364420119) **101 PASS/1 SKIP**, 한국어 선택 표시명 없음에도 아이템 정확 ID 유지. **현재 A4 `READY_SCOPED — CURRENT_KR_70783_BLIZZARD_INDEX_BASE_ONLY`**이며 A7 item/WSE·수치 인증·전체 E2E 아님. **현황: A1~A3 ENGINE 3 / A4 현재 범위 READY 1 / 역사 READY 3 / PENDING 71. 다음 A5 WCL.**

> **v397 A4 현재 선행 경계:** [실 Blizzard 네 API 원문 HTTP byte SHA/크기 증명](notes/2026-11-13_p1-v397-a4-blizzard-original-http-body-provenance-progress.md) — [Actions #43359408019](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43359408019). A4는 이 4개 인덱스 원본 확보까지 실 PASS지만 **선택한 필수 item/contents 출처 정합이 미확정이므로 PENDING_SCOPE**. 다음 A4 원본 소비 필드별 추적, Wago 10개/Native 중복 수집 금지.

> **최신 v396 (이전 A1/A2 PENDING 서술보다 우선):** [A1 실 제로베이스 범용 자동 식별 PASS](notes/2026-11-13_p1-v394-a1-current-zero-source-engine-pass.md) → [A2 공식 Retail KR 버전/동일 원본 전파 PASS](notes/2026-11-13_p1-v395-a2-current-retail-build-source-and-propagation-pass.md) → [A3 실제 활성 raid/M+ 유일 조인 PASS](notes/2026-11-13_p1-v396-a3-active-raid-mplus-current-source-scope-pass.md). 세 항목은 해당 ENGINE 기능 범위만; A7 시즌 아이템 소속/원본 WSE와 GJFO·최종 E2E 미완료. **78개 원장: 3 ENGINE PASS + 3 역사 READY_SCOPED + 72 PENDING. 다음 A4.**

> **v394 A1 순차 완료 / 다음 A2:** [현재 KR 70783 실제 ZERO-SOURCE 원본 유일 자동 시즌 조인·ENGINE PASS](notes/2026-11-13_p1-v394-a1-current-zero-source-engine-pass.md). WCL all-expansion에서 frozen 과거 2개 비양수 ID만 제외, 현재 활성 WCL 2 zone+공식 Blizzard season 18+Wago 10 DB2(62,280,767바이트)에서 expansion11/DisplaySeason37/tier505, raid10/던전8 정확 발견. **A7 개별 아이템 WSE/전체 시즌 READY는 아님.** 상태 집계는 원장 최신 확인. 다음 채팅은 과거 A1 PENDING 안내 대신 **A2 현재 게임 빌드**부터 진행.

> **A1/G10 최신 v388 실제 회귀:** [첫 FAIL/원인/복구/두 번의 PASS·앱 TXT 영수증](notes/2026-11-13_p1-v388-a1-and-app-filelist-real-offline-ci.md) — GitHub Ubuntu Python 3.12 **74 PASS/1 SKIP/0 FAIL**, 실제 272개 배포 후보 파일명을 같은 패키저의 TXT로 추출·SHA 확인. CI 전용 가상 v213 fixture는 ZERO-SOURCE 정답이 아님. **A1은 여전히 PENDING_SCOPE**, 정상 인증 원본 자동 발견·현재 시즌 DB2 JOIN 시험 필요.

> **현재 A1 코드 증분 v387:** [전체 확장팩 WCL 원본/동일 출처 DB2 JOIN, MIDNIGHT 하드코딩 제거](notes/2026-11-13_p1-v387-a1-all-expansion-source-discovery.md). **수정 코드·테스트 추가**, 원본 함수 10 스모크 PASS, 전체 Python CI/실 API ZERO-SOURCE **미실행**, A1 PENDING. 다음 채팅에서 v386 인계 문서의 v385 코드 스냅샷보다 **v387 최신 실제 HEAD/테스트**를 우선 재조회.

> **최종 앱 파일 구성 원칙:** [배포 파일 자동 TXT 목록 + 78개 기능 추적 지침](APP_PACKAGE_FILE_REGISTRY_20261113.md). 소스 파일을 별도 완성 폴더에 복사하거나 수동으로 파일 목록을 중복 유지하지 않는다. 현재 베타 패키저의 단일 `select()`에서 TXT를 생성하고 ZIP `V181_PACKAGE_MANIFEST.json`의 실제 바이트/SHA를 사용한다. 78개 기능은 파일 개수와 1:1이 아니며 파일 수정 시 연결 테스트·영수증 범위 대조.

> **2026-11-13 최상위 최신 사용자 결정 / 새 채팅 정본:** [v386 독립 인계](../CHAT_CONTINUITY_HANDOFF_20261113_P1_V386_ZERO_SOURCE_GENERALIZATION.md) → [현재 제로베이스 PASS = 범용 미래 시즌 대응 엔진 기능 PASS 정책](POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md) → [운영 헌장](OPERATING_CHARTER_FUTURE_SEASONS_AND_EVIDENCE_20261113.md) → [78개 원장](ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md). **현재 시즌·확장팩을 ID/정답/GJFO 캐시 미주입·AI 개입 없이 승인 원본/API 키로 자동 발견·검증하는 실제 ZERO-SOURCE 성공**이면 미래 시즌 대응 **ENGINE 기능 완료를 인정**하며, 미래 미출시 데이터 실측 부족을 미완료 사유로 쓰지 않는다. A1부터 78개 순차 개발, 현재 상태 역사 READY_SCOPED 3/78, A1은 진행 중. 이 텍스트 자체는 PASS/Project UI 반영 증거가 아니다.

> **상시 우선 확인 · 최신 사용자 결정 (2026-11-13):** [범용 개발·정합성·검증 운영 헌장](OPERATING_CHARTER_FUTURE_SEASONS_AND_EVIDENCE_20261113.md)을 **모든 개발 사이클 착수 전 먼저 읽는다**. 아직 존재하지 않는 미래 시즌의 실제 READY를 현재 증명하려 하지 않고, 현재 실제 원본의 ZERO-INSTALL / 엄격 ZERO-SOURCE / 합성 ZERO-CONTRACT를 구별한다. BASE/USER/RUN 증거 범위와 재사용 우선 원칙을 따른다. 이 헌장은 제품 승인 v1.4.3이나 78개 실제 상태 원장을 대체하지 않는다.

> **2026-11-13 최신 새 일반 채팅 인계 (v382, 기존 일반 인계보다 우선):** [단일 인계 — 78개 요소별 준비 완료 운영](../CHAT_CONTINUITY_HANDOFF_20261113_P1_V382_78_ELEMENT_READINESS.md) → [A~G 72개 + H 6개 **78개 준비 추적표**](ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md). 사용자 최신 명시 요청에 따라 새 채팅이 최초 **읽기 전용 복원 후 STOP**, 별도 '진행'이 있을 때부터 요소별 P1–P2 재사용/연결/최소 검증을 이어간다. **78개의 신규 인증 Gate·Native 전수를 만들지 않음.** 기존 287개 역사 개발 노트/파일 지도/Native 영수증을 재사용하며 새 결함을 추측하지 않는다.


> **인계 기준과 이후 증분 구별:** 아래 v365 문서는 v382 **이전의 역사 단일 인계**이고 최신 코드 HEAD라는 뜻이 아니다. 2026-11-13 v377 이후 검증/수정 증분은 [기능별 INDEX](INDEX.md)의 재사용 앵커와 [FILE_MAP](FILE_MAP.md)·[EVIDENCE_INDEX](EVIDENCE_INDEX.md)에서 실제 HEAD로 확인한다. 특히 영약 F/gear_* 0/개인별 영약 변경과 5티어 유동 기능은 **기존 구현·Native를 먼저 재사용**한다.

> **이전 역사 단일 인계 (2026-11-12, P1 v365까지):** [2026-11-12 P1 v365 UI 동결·시즌 원본 조인 미완료 최신 단일 인계](../CHAT_CONTINUITY_HANDOFF_20261112_P1_V365_UI_FREEZE_SOURCE_JOIN_NEXT.md). v350 이전 인계는 역사가 되며 v350의 실증·v364 UI 동결·v365 원본 조건 4 PASS·실제 시즌 JOIN PENDING을 별도 구분한다.

> **2026-11-11 역사 인계:** [v338 제품 완성·공식 한국어·제로베이스 최신 단일 인계](../CHAT_CONTINUITY_HANDOFF_20261111_P1_V338_PRODUCT_FINALIZATION.md). 기존 v331 인계는 제품 N 연구 완료 당시의 역사 스냅샷이고, 최신 제품 상태(v332~v338)는 신규 인계를 우선한다.

[v365 **시즌 WorldStateExpressionID 손상값을 0으로 오분류하던 오류 수정, 조건 원본 검증 4/4 PASS**](notes/2026-11-12_p1-v365-db2-conditional-season-parse.md) — 원래 v163·v216 조인 유지, 새 시즌 JOIN/READY는 계속 보류, 신규 Native0.

[v364 **UI 줄간격·행열·중복 선 최종 보수, 7/7 PASS; P1 시즌 G/J/F/O 증거 갭 복귀**](notes/2026-11-12_p1-v364-ui-spacing-freeze-and-source-gap-resumption.md) — 입력 ID183/183·원래 SimC/세션 그대로, 신규 Native0. 현 시즌 JOIN과 J/F/O 최고품질·실행 실증은 PENDING.

[v363 **기름 기본 사용·쌍수 원본 검증·물약 직접 선택·장비 5열·환경/결과 선형 UI, 7/7 SUCCESS**](notes/2026-11-12_p1-v363-oil-default-input-end-to-end-audit.md) — [오프라인 HTML 미리보기](https://github.com/degong2-code/simc-secondary-optimizer-runner/blob/probe/chat-cache-v035-20261024/previews/v363_oil_default_potion_five_column_flat_preview.html). 기존 G/J/F/O·183 입력 ID 유지, 현 시즌 JOIN·물약 비기본 항목 승인은 여전히 별도 확인.

[v362 **박스 없는 선형 컴팩트 UI·장신구 선택/해제 수정·무기 기름 검증 토글, 7/7 Windows/API/UI 성공**](notes/2026-11-12_p1-v362-flat-compact-gear-flow.md) — [브라우저 미리보기](https://github.com/degong2-code/simc-secondary-optimizer-runner/blob/probe/chat-cache-v035-20261024/previews/v362_borderless_compact_preview.html), 기존 G/J/F/O·세션/캐시 유지, 증강룬·PI·주술사/반지2 확장은 검증 대기.

[v360 **차콜·골드 복원·02 환경 입력 압축·부위별 마법부여 드롭다운, Windows/API/UI/Focused 7/7 SUCCESS**](notes/2026-11-12_p1-v360-compact-environment-charcoal-enchants.md) — [단일 HTML 미리보기](https://github.com/degong2-code/simc-secondary-optimizer-runner/blob/probe/chat-cache-v035-20261024/previews/v360_compact_environment_charcoal_preview.html), 기존 사용자별 ID/기름/수동 T 보존, 이미지/신규 Native0.

[v359 **투명 고대비 다크 테마·환경 입력 정리·고정 장비 본문 직접 선택, UI/API/Windows 회귀 7/7 SUCCESS**](notes/2026-11-12_p1-v359-glass-compact-inline-equipment.md) — [새 단일 HTML 미리보기](https://github.com/degong2-code/simc-secondary-optimizer-runner/blob/probe/chat-cache-v035-20261024/previews/v359_high_contrast_inline_gear_preview.html), 정확한 ItemID/SELECT·예산·세션 유지, 아이콘 외부 수집 0, 시즌 JOIN/새 개인 변형 READY 미검증.

[v358 **2열 컴팩트 입력 화면(1 캐릭터 | 2 환경 / 하단 3 고정장비), 기존 Windows/API/UI 회귀 7/7 SUCCESS**](notes/2026-11-12_p1-v358-compact-two-up-layout.md) — [실제 CSS 기반 단일 HTML 미리보기](https://github.com/degong2-code/simc-secondary-optimizer-runner/blob/probe/chat-cache-v035-20261024/previews/v358_compact_two_up_offline_preview.html), 이미지 수집은 UI 검토 후. 신규 Native0, 시즌 JOIN PENDING 유지.

[v357 **사용자 입력 중심 다크 UI·장비 카드·실행/결과 화면 분리, Windows ZIP/API/UI 회귀 7/7 SUCCESS**](notes/2026-11-12_p1-v357-task-first-dark-card-ui.md) — [단일 HTML 오프라인 배치 미리보기](https://github.com/degong2-code/simc-secondary-optimizer-runner/blob/probe/chat-cache-v035-20261024/previews/v357_task_first_dark_offline_preview.html), 기존 입력·SimC/세션 보존, 이미지 수집 보류, 신규 Native0. 시즌 JOIN 및 신규 개인 변형 READY는 미검증.

[v352 **WoW Dark Tactical Dashboard 외관·모바일·가독성 보수, Windows ZIP/API/UI 회귀 SUCCESS**](notes/2026-11-12_p1-v352-dark-tactical-ui.md) — CSS·탐색만 변경, HTML 기존 ID142개 유지, 새 Native0. 시즌 JOIN PENDING·신규 사용자 변형 READY는 별도.

[v351 **최적화 ilvl 오적용 교정·검증 영약/기름 단일 조회·시즌/개인 UI 정리, Windows ZIP/API/UI 회귀 PASS**](notes/2026-11-12_p1-v351-user-variant-level-ui-clarity.md) — 제품 엔진·기존 세션 유지, 신규 Native0. 시즌 JOIN PENDING·새 개인 변형 READY 미실증.

[v350 **시즌 공통 구축과 개인별 소켓·특수보석·영약·기름 선택 분리, 검증 설치 변형 없으면 422 차단 PASS**](notes/2026-11-12_p1-v350-common-season-user-variant-split.md) — Windows 3.12/3.14 실제 추출 ZIP 272개 소스 SHA, UI/API/ledger CI PASS; 새 시즌 70783 가입/원본 확정과 개별 변화 Native는 여전히 미실증.

[v349 **실사용 시즌 환경 UI: 진행 중임·경과시간·시즌 JOIN 보류 원인·소켓 총수·수동 ItemID 고급 설정 분리 PASS**](notes/2026-11-12_p1-v349-user-season-progress-sockets-sourceitem-ux.md) — Windows ZIP 자체 원클릭 BAT 보존, 272개 소스 SHA 검증, Native0; 실제 단계별 진행 퍼센트 및 개인 사용자 키 READY는 미검증.

[v348 **Windows 본인 Blizzard/WCL 키를 로컬 Credential Manager에 등록하고 기존 v216 시즌 Build에 전달·삭제·비밀키 비노출 PASS**](notes/2026-11-12_p1-v348-user-owned-credentials.md) — 실제 Windows CMD/HTTP·WinCred 왕복, Native0. 실제 발급키를 이용한 70783 READY 현장 시험은 미실증.

[v347 **비밀키 없는 현재 KR70783 시즌 Build는 Wago·SimC 수집 후 시즌·레이드 범위 미확정으로 PENDING**](notes/2026-11-12_p1-v347-credentialless-gjfo-current-once.md) — 환경/DPs Native0, 실제 사용자 무키 READY 미구현, 추정 예산·역사70575 fallback 금지.

[v346 **기본64·continuous 최적화의 검증 v212 설치 의무, Windows·Linux PASS**](notes/2026-11-12_p1-v346-current-default-season-install-boundary.md) — 기존 Native64 실증 v344 원본 재사용, 무효 시즌 시작 차단.

[v345 **배포 ZIP 그대로 압축 해제·CMD 실행·Chrome 저장 계획 세션 복원 Windows PASS**](notes/2026-11-12_p1-v345-windows-zip-cmd-chrome-zero-native.md) — source ZIP 270개 SHA 검증, Native0, 역사적 포함 v213 카탈로그는 빌드 70575이며 현재 70783 환경 READY는 사용자 시즌 Build 별도 필수. 실제 Native64 증거는 v344 참조.

[v344 **실제 Windows Chrome→현재 70783 시즌 자동 GJFO3→N56 64회·취소·HTTP 서버 재시작·재개·결과 재열기 PASS**](notes/2026-11-12_p1-v344-real-windows-browser-native64-once.md) — GitHub Actions Windows-2022 생존 사냥꾼 한 사용자 조건, 실제 SimC DPS64·SEM·95% 기록. 개인 PC 설치·미래 시즌 일반화·전역 최적해는 미입증.

[v343 현 Retail70783 Windows GJFO3 + 생존 사냥꾼 기본N56/12 실제 Native PASS](notes/2026-11-11_p1-v343-current-70783-windows-source-native-once.md) — 단일 전문화 실제 Windows FastAPI→SimC; 개인 PC Chrome 64회는 미검증.

[v342 Windows·Linux Chrome 64회 클릭(합성) 및 공식 Windows 70783 바이너리 소스 SHA PASS](notes/2026-11-11_p1-v342-browser64-windows-source-preflight.md) — 신규 DPS Native0; 70783 Windows 환경·SimC DPS 통합 아직 미검증.

[v341 실제 Windows N56/12 원본 SHA·취소·재개·캐시 PASS](notes/2026-11-11_p1-v341-windows-n56-native-once.md) — 과거 고정 SimC 바이너리 한 전문화; 현재 70783·사용자 브라우저 64회 전주기 실증은 아님.

[v338 통제 필수 시즌 원본 실패→정상 봉인·재사용, G/J/F/O 누락 차단 — Linux/Windows PASS](notes/2026-11-11_p1-v338-negative-season-source-recovery.md). 새 시즌 전체 원본 READY 실증은 아님.

[v337 **무이력 설치→한국어 원본 자동 구축→무중복 재사용** 실 Native PASS #43000049793](notes/2026-11-11_p1-v337-real-coldstart-environment-ko-reuse.md) — 현재 70783 한 조건 한정, 미래 시즌 원본 인증 아님.

> 2026-11-11 최신 P2 인계 연결을 반영한 격리 브랜치 검색 진입점. 파일·Actions·Native 현재 여부는 매 작업 실제 HEAD와 비교. **본 문서는 새 제품 코드/Native PASS를 의미하지 않는다.**

| 질문 | 문서 |
|---|---|
| 지금 무엇을 구현했고 남았나 | [제품 최신 A~G 정본](../PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md), [2026-11-11 최신 P1 v338 제품 완성·현지화·제로베이스 인계](../CHAT_CONTINUITY_HANDOFF_20261111_P1_V338_PRODUCT_FINALIZATION.md), [P2 v331 연구 종료 역사 인계](../CHAT_CONTINUITY_HANDOFF_20261111_P2_V331_PRODUCT_FINALIZATION.md) ([2026-11-10 P2 v305 역사 인계](../CHAT_CONTINUITY_HANDOFF_20261110_P2_FRESH_FROST_V305_NEXT.md)) |
| 어떤 코드·테스트를 먼저 봐야 하나 | [INDEX](INDEX.md) → [FILE_MAP](FILE_MAP.md) |
| 특정 파일이 어디 있나 | [전체 FILE_INVENTORY](FILE_INVENTORY.md) → [핵심 FILE_MAP](FILE_MAP.md) |
| 실제 CI·Native PASS 범위 | [EVIDENCE_INDEX](EVIDENCE_INDEX.md) → GitHub 원본 영수증 |
| 영구 보관된 시즌 Build 최소 영수증 | [70783 Ret334 검증 범위](environment_receipts/README.md) — 전체 환경 DB 복원은 별개 |
| v318 오차·다른 CHMV 후보 확인 정책 | [v319 신규 풍운 수도사 실 Native A/B](notes/2026-11-11_p2-v319-new-windwalker-real-v290-v318-ab.md), [영구 compact 원본 대사](research_receipts/p2_v319_windwalker_auto_T_real_v290_v318_compact.json) — 최고 CHMV 동일·95 우위 없음 |
| 최신 실 Native 성공/비용·원본 범위 | [v319 실제 Actions SUCCESS #42941245130](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42941245130), [증거 지도](EVIDENCE_INDEX.md) |
| v321 신규 Shadow Priest 128+3 Native 실측 | [영구 compact·원본 SHA](research_receipts/p2_v321_shadow_auto_T_35_120_320_compact.json), [Action 실패·별도 120 복구 기록](notes/2026-11-11_p2-v321-new-shadow-priest-120-native.md) — 제품 120 단계 미통합 |
| v331 마지막 N32/35/48/56/64 실 v290 비교 | [343 Native 검증 compact](research_receipts/p2_v331_unholy_fixed_N_343_native_compact.json), [Actions SUCCESS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42969029964) — N56 공학적 권고, 신규 v293 기본56 적용; [제품 변경·검증 상태](notes/2026-11-11_p2-product-v290-default-n56.md) |
| v330 IDEA-003 신규 야성 드루이드 실제 124 Native | [검증 compact](research_receipts/p2_v330_feral_idea003_124_native_compact.json), [Actions SUCCESS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42965880663) — 19회 동일 관측 재사용, 발견력 우위 없음 HOLD |
| v329 IDEA-002 신규 고통 흑마법사 267 Native | [원본 SHA·독립 홀드아웃·제약](research_receipts/p2_v329_affliction_idea002_267_native_compact.json), [Actions PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42962010689) — 우위 미입증, radius-only 판정 보류 |
| v327 Havoc 신규 프로필·N32~96×3시드 | [299회 실제 Native·N별 후회도](research_receipts/p2_v327_havoc_auto_T_299_native_compact.json), [원본 재활용 연구 SUCCESS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42957270859) — N32/48 모두 유망, 기본 미변경 |
| v325/v326 신규 황폐 기원사 251 Native·N 선별 성공률 | [원본 SHA·N24~192 비교](research_receipts/p2_v326_devastation_auto_T_heldout_251_compact.json), [Actions SUCCESS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42953218111) — N48 유망, 제품 미승격 |
| v324 조화 드루이드 새 프로필+N20~640 실측 | [163 Native 성공·N별 데이터](research_receipts/p2_v324_balance_auto_T_variable_n_32_compact.json), [v323 동일 CHMV 오류 교정·판정](notes/2026-11-11_p2-v324-new-balance-continuous-n.md) — 변수 N 자동 통합 전 |
| v322/v323 CHMV 최초 도달·연속 N 선택 | [도달시간·가변 N 연구](notes/2026-11-11_p2-v323-arrival-continuous-n.md) — 동일 CHMV 소요시간 우선, Native 적용 전 |
| v320 SEM 기반 35/120/320 연구 진단 | [IDEA-001 단계 선택 진단](notes/2026-11-11_p2-v320-sem-tier-advisory.md) — 120 단계 실행 아직 미통합 |
| 실제 35/120/320 비용 계측 | [18회 Native 실측 노트](notes/2026-11-11_p2-18-real-request-cost.md) |
| 왜 그렇게 만들고 무엇을 철회했나 | [DECISIONS](DECISIONS.md) → 근거 노트 |
| 개발·인계 규칙 | [PROTOCOL](PROTOCOL.md) |
| 과거 경과와 이전 인계 | [원래 INDEX 기록](HISTORICAL_INDEX_20261110_PRE_KNOWLEDGE_LAYER.md), [원래 PROTOCOL 기록](HISTORICAL_PROTOCOL_20261110_PRE_KNOWLEDGE_LAYER.md), [개발 노트](notes/), [누적 CURRENT](../CURRENT_PRODUCT_DEVELOPMENT_STATE.md) |

> **v317 새 시험 경계:** [격리 코드](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/ff8b1da8a5781664a1fa5d616d23533cc9f0d7d6)·[Native 워크플로](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/workflows/p2_v317_single_profile_timing_native_once.yml) 등록됨, **실제 run ID/Native 영수증 확인 전 PENDING**. 10분 하드 탈락 폐기, 품질/비용 우선. [IDEA-001 고도화](algorithm_ideas/IDEA-001-multifidelity-successive-halving.md), [IDEA-008 선택편향 홀드아웃 제안](algorithm_ideas/IDEA-008-postselection-independent-holdout-confirmation.md) 모두 실증 개선 미확정.

## 2026-11-11 최종 P2 판정

[최신 단일 인계](../CHAT_CONTINUITY_HANDOFF_20261111_P2_V331_PRODUCT_FINALIZATION.md)를 우선한다. [v333 Chrome 실클릭](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42983424219)과 [v334 기본 v290/N56 Native12 실증](notes/2026-11-11_p1-v334-primary-n56-native-once.md) 완료(2026-11-11); [한국어 웹·77개 공식명](notes/2026-11-11_product-korean-simple-ui.md) 보존; [v335 한국어 공식 아이템명 Environment Build 통합](notes/2026-11-11_p1-v335-environment-ko-auto-localization.md) 및 [v336 공식 직업·전문화·종족 64/64 원본+실 Chrome](notes/2026-11-11_p1-v336-official-playable-term-catalog.md), [코어 회귀 PASS #42988281237](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42988281237); v331 완료, 신규 v293 기본 N56 적용. [최신 제품 통합 노트](notes/2026-11-11_p2-product-v290-default-n56.md); 실제 CI/Native 검증 상태는 해당 영수증 기준. 아래 v316/v314 설명은 **역사 기록**이며 후속 v329/v330/v331 실제 timing trace를 부정하지 않는다. 기존 환경/대표프로필/선택 기능 재개발 금지.

## 2026-11-11 역사 P2 실측 및 계측 경계

- [단일 인계](../CHAT_CONTINUITY_HANDOFF_20261111_P2_V316_V314_RESULTS.md)가 v313 8/8, **v314 15/16 완전 + 암살 도적 wide 540s 부분**, v315 10개 조건 비용, v316 opt-in 계측 635 PASS/2 SKIP·실 Native 계측0의 최신 기록이다. 아래 2026-11-10 ‘현 시점’ 항목은 **그 당시 역사 기록**이며 최신 실험 상태를 대신하지 않는다.

## 2026-11-10 역사 시점의 중요한 판정

- **P2 최신 v312 5~10분 적응형 알고리즘 실제 A/B:** [Actions #42838011084](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42838011084) 신규 동일 Destruction Warlock/ilvl334/수동T3400/일반보석4·O0/SimC SHA·프로필 동일, **각 1008 DPS Native**, 원본 캐시전용 재확인 Native0, v312 연구 모델 **285.557초/확인320 최고181384.94±SEM238.71** vs **기본 v290 270.490초/최고182000.24±SEM253.46**, 차이615.31 < 선택쌍 명목95 반폭682.40. v290는 **121개 정밀확인/69765 총 iterations**, v312 **16개/39840 총 iterations**: 같은 calls이지만 **확인 예산과 총 iterations가 다르므로 v312 탐색 자체 열등을 확정하지 않는다**. 신규 v312 기본 승격 금지, 제품 기본 v290/ main·불변 자료/Project UI 불변. [회귀 #42836800413](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42836800413) 620 PASS/2 SKIP, [원본 9906/48 holdout #42837263874](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42837263874) 신규 Native0·모델예측 RMSE228≠실제 탐색 우위. [정확 영수증·상한](EVIDENCE_INDEX.md), [상세 노트](notes/2026-11-10_p2-v312-surrogate-5to10min-adaptive.md).
- **21단계 고밀도 잔여 전수는 최신 사용자 지시로 중단:** 과거 [11단계 전수 2784](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42814969237), [25% 4953](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42822653731), [50% 9906](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42826070351) 실측 완료. **21단계 19812 중 나머지 9906**은 실행하지 않는다. v312는 11/21 격자를 후보 목록으로만 재사용하고 SimC는 선택된 후보에만 실행한다.
- **P2 v307 고밀도 다단계 탐색 실 Native 완료:** [Actions #42809784899](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42809784899), [노트](notes/2026-11-10_p2-v307-dense-nested-global-coverage-optin.md). 파괴 흑마법사 신규 제품 사용자/manual T3400/4일반·특수0/O0, same profile SHA from v306; GJFO Native3+DPS Native520/129.077초, cache-only 신규0. **격자6 436/436 전수**, 격자11은 477/2784만 관측. 확인320 최고 181419.76±SEM230.27, 차점181324.32±237.36, 95% 차이 미확정. v290 44-call normalized 후보와는 동등 예산 비교 아님. 새 코드 opt-in/v290 기본 불변; 향후 더 촘촘한11단계 원본 캐시 보존·재개 설계가 먼저. [offline CI #42809143791](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42809143791) 605 PASS/2 SKIP/0 FAIL.
- 목표는 **26 DPS** 대상으로 목표 ilvl 기본334 또는 수동 최종 T에서 치명·가속·특화·유연의 **절대 rating**을 SimC DPS로 최적화하는 하나의 시즌 공통 엔진. 사용자 현재 장비 재분배/장비 조합 추천/시즌 전체 DB 아님.
- 현재 실 70783 Ret334 빈 작업공간: **일반보석 치·가·특·유 각1, 특수 없음, O0**, G2850/J92/F165/B=T3107, 기존 v216/v212 Native3→READY/검증 사용자 프로필 PASS. **미래 시즌·이 4보석 구성의 실제 DPS·Windows 개인 클릭**은 미실증.
- v290/v291에는 Native10/정확 cross-job 캐시 검증이 있다. 최신 사용자 승인 P2 설계는 [적응형 백분율 기준점·비례 정규화](notes/2026-11-10_p2-percentage-grid-proportional-normalization.md): 초기 11개 기준점은 고정이 아니며 실제 SimC 처리량으로 조정. [v298 선택형 후보 생성](notes/2026-11-10_p2-percentage-grid-opt-in-engine.md) 및 [v299 다중영역·속도22 시험](notes/2026-11-10_p2-multiregion-throughput22-opt-in.md)으로 상한/하한 비례 재배분·정수 총량·중복 제거·다중 영역/대각선 방향·v291 opt-in은 코드화했으나 **기본 탐색 교체·웹 사용자 노출은 없음**. 새 [실 SimC100·중첩11/21·v290 비교](notes/2026-11-10_p2-real-simc-nested-11-21-48case-comparison.md)에서 m11/m21 최종 integer 후보 포함 PASS, 실제 신규 Native100/62.84초, **기존 v290이 높은 확인 DPS 발견**, 추가 26전문화/E2E 입증 아님. [실 **21개 초기→8영역×6개 국소 격자→GP 연구**](notes/2026-11-10_p2-real-simc-global21-local6-gp-comparison.md): 공통 초반160 Native, 지역160/확인8, 실제 21+6 조합에서 기존 최고보다 더 높은 DPS 후보 발견. GP 지역후보 선정은 추가 연구로 일부 개선 관측하지만 1000-iteration 선택쌍95% 확정 아님. v302 독립 실험 코드만 추가/기본 v290 미승격. 다음 중점은 **지역별 관측 개선·SEM·순위 안정성에 따른 반경/Native 예산 적응 조절**, 저성과 지역 예산 재배분과 탐색 reserve 유지다. fixed local6·GP-UCB·MADS-like·Sobol을 동일 iterations+wall-clock으로 비교한다. 전역 최적/가족단위95% 증명 아님.
- **P2 v303 적응형 배분 초안:** [개발 노트](notes/2026-11-10_p2-adaptive-region-resource-policy.md). 10개 scratch 테스트 PASS 및 [실제 격리 CI #42766503663](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42766503663) 566 tests=564 PASS/2 SKIP, ledger PASS. v290 기본 유지. 후속 [v304→v291 별도 opt-in 연결](notes/2026-11-10_p2-v304-v291-adaptive-durable-bridge.md)은 [focused #42769319450](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42769319450) **573=571 PASS/2 SKIP** 합성 Native·checkpoint 회귀 통과; 실제 DPS 우위·웹 연결 아님, 신규 Native 0. 공통 global160 + post-global160 + 8×320 비교 계약(13,760 iterations/방법)을 만들고 적응형은 post-global 예산 중 136 지역 + 24 global reserve로 나눈다.
- **P2 v306 다른 전문화 최초 공정 비용 Native 실증:** [실 #42804842969](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42804842969) 새 파괴 흑마법사 인간 T3400·보석 일반4·특수0/O0 사용자 프로필을 기존 v113→v216/v212→v098/FastAPI에서 생성, 예산 원본3107 대비 수동 최종3400 우선. **Native 환경3 + DPS67 / 동일실험 정확 재사용1**, 초기20 공통·후속20·확인4/방법, **각 2680 requested iterations**. v290 정규화 후보형 **180823.52 ±247.84 SEM** vs v306 **180461.33 ±226.38 SEM** (320회), 관측 격차362.19 < 명목95 반폭657.90, **우위 미확정**. v306 12/24%B 실제 시도 확인, 기본 v290 유지, 95% 다중선택/전역최적·원형 v290 정밀일정·26스펙 증명 아님. [개발 근거](notes/2026-11-10_p2-v306-destruction-new-user-native-planned.md); [사전 CI #42804522961](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42804522961) **602=600 PASS/2 SKIP**, Native0.
- **P2 새 사용자 프로필 제품 Native 실증 완료:** [실 #42785318578](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42785318578) 냉기법사 인간 ilvl334/수동T3300/일반보석4·특수0/O0, 원본 G2850/J92/F165 Native3+새 사용자 DPS Native2, 관측 DPS **165226.98±706.33 SEM**, 95% 우위 미확정·전역최적 미증명, 0 새 Native cache-only. [근거·교차 전문화 오류 교정](notes/2026-11-10_p2-fresh-four-ordinary-cross-profile.md). 이전 Ret 일반 Build의 단일 스펙 G를 새 사용자 장비로 복사하지 않고 동일 시즌 봉인된 소스로 **선택 스펙 1개**의 대표 gear 후보를 다시 구성한다. 다음 독립 실험에선 다른 전문화·설정을 선택하며, 같은 실험 정책별 비교 시 한 프로필을 고정. [focused #42785116724](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42785116724) 594 PASS/2 SKIP. v290 기본/웹 실제 사용자 PC/26전문화 실증 범위는 불변.
- **P2 v305 결합형 실제 검증 완료:** [실제 SimC 결과·진단](notes/2026-11-10_p2-v305-real-hybrid-4520-result.md) — [#42776992650](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42776992650) 신규 Native21/과거 compact48 재사용, 4520 iterations, v305 187345.89±170.56 vs normalized-v290 189913.69±170.73. **v305 기본 승격 보류**, 95% 다중 후보 우위 미검증. 첫 6.5%B 지역 반경×1.5는 v290 우수점의 12%B(373 rating) 2스탯 이동을 포함하지 못함. 다음 개선은 새 v306 identity의 비국소 escape/지역 성과 우선 예산을 오프라인 재현한 뒤 최소 Native 검토.
- **P2 v305 결합형 opt-in 구현/검증 진행:** [설계·근거](notes/2026-11-10_p2-v305-hybrid-global21-local6-v290.md). 전역21-축/지역6-축 격자·v290 두 스탯 이동·v304 지역 예산/반경·전역 reserve 결합; v291 독립 세션 seal/cancel/resume 코드 연결. 실제 비교는 이전 127 Native 및 초기32 공통 표본·100 Native 압축 증거 재사용, 새 Native 최대40. 실제 결과는 위 별도 #42776992650와 증거 노트 참조. v290 기본/웹 미변경.
- **P2 real SimC 동일iterations 확인:** [실제 #42772775449 결과](notes/2026-11-10_p2-real-v304-32x32-native-result.md) — 3방법 모두 각4,520 iterations; 127 NEW_NATIVE/역사100 compact 3/동일실험 캐시13, 전체49.648초. **v290-normalized 1000iter189913.69±170.73 > v304 187946.03±175.29 > fixed187783.17±172.59** (이 한 역사 프로필). 원본 v290 일정과 다른 scout 강제 정규화이고 95% 다중선택 교정/26전문화/현재4보석 미입증. **v290 기본 유지, v303/v304 미승격.** [실험 계획](notes/2026-11-10_p2-real-v304-equal-budget-pilot.md)
- `B=G+J+F`, `T=B+O`, 수동 T 우선, 기름 O와 L/E 고정 회계 중복 금지. SimC가 effect/proc/APL/DPS 책임. 신규 효과 인증 Gate 불필요.

## 검색 4단계

1. 최신 기능 판정 → INDEX의 A~G → FILE_MAP 코드/테스트 → EVIDENCE_INDEX 해당 영수증.
2. 왜 만들어졌는지는 DECISIONS의 결정 링크를 통해 이전 노트로 이동. 역사 문서의 `PENDING`을 현재 상태로 쓰지 않는다.
3. 먼저 `REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP`을 결정한다. **실패 재현과 증거 미확보를 분리**하고 기존 Native/원본/캐시의 유효 범위만 재사용한다.
4. 변경한 기능의 상태·파일 지도·증거 지도만 갱신하고, 원본 역사와 단일 인계는 삭제·중복 재작성하지 않는다.

격리 `probe/chat-cache-v035-20261024`의 변경과 `main`, immutable v003, 원본 v016, Project UI/Work OS, 공식 승격은 별도 권한이다. 주 제품 개발 채팅의 소유권도 유지한다.
