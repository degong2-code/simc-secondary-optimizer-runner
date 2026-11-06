# SIMC SECONDARY OPTIMIZER · P3-GI 단일 새 채팅 인계 정본 (2026-11-06)

**신분:** GitHub 격리 개발의 새 채팅 읽기 전용 복원 정본. 승인 설계, Project Sources/Instructions, 공식 Work OS, immutable 원본과 main 승격이 아니다. 구 P3-FK 및 더 이른 인계는 역사 자료다.

## 1. HEAD 및 조회 순서

- GitHub: degong2-code/simc-secondary-optimizer-runner / probe/chat-cache-v035-20261024.
- 이 인계 작성 전 최신 **제품 코드** SHA: d9f05ecd009981ef603ccdfe8bcf0e4042a2f0b4 (P3-GH). main HEAD: 07133e0aaf738d6e4816a6486057b1cd49c018de. **본 인계 문서 커밋 후 격리 HEAD는 바뀌므로 새 채팅에서 두 브랜치 HEAD를 각각 독립 조회할 것.** 문서 커밋과 제품 코드를 구별한다.
- 읽는 순서: **P3-GI → docs/development/PROTOCOL.md → docs/development/INDEX.md의 E3/E2/E1, D1/D2, B3, C1~C4, G1/G2 → docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md 최상단 → docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md → P3-GH/GG/GF/FP/FQ/FX/FY/FR 관련 note → 필요 코드/봉인 원본 SHA/Actions/Native 영수증.** 이전 모든 개발 기록 무조건 재조회 금지.
- 우선권: **최신 사용자 직접 승인 > 비충돌 설계 v1.4.3 > 실제 코드·원본·Actions/Native > INDEX/CURRENT/인계.** 이전 27 DPS 포함 표현은 역사이고 **현재 26 DPS, 증강 기원사·탱커·힐러 제외**.

## 2. 최종 제품 목적·필수 완료 기준

- 목표 ilvl 기본 334 또는 사용자가 입력하는 **최종 CHMV T**로 미래 파밍 목표가 될 치명/가속/특화/유연의 **SimC DPS 최대 절대 rating**을 찾는다. 전체 착용 장비 재분배나 장비 조합/파밍 경로 추천, 전체 시즌 장비 DB가 아니다. 사용자는 캐릭터/특성·장신구2·선택 특수장비·장식 최대2·보석/소모품/전투조건을 입력한다. 일반 장비/무기/티어4/주능력치는 엔진 내부 대표 프로필. 선택 SimC 업로드의 현재 장비/총량을 복사하지 않는다.
- Environment Build **실제 T1 완료**는 웹 v216의 현재/신규 시즌 대표 장비·G/J/F/O 자동 검증 → v222의 **B=G+J+F, T=B+O, c_final=c_base+o**(사용자 최종 T 우선, 고정 L/E/O 중복 차단, 장신구 자유 G 밖) → v220/v196 정책 A 검증 최고품질 선택지 발행 → v212/v217 **실제 봉인 설치 및 environment_ready=true 와 environment_installed=true** 모두 확인. source-only, 합성 PASS, Native 호출 수 자체는 READY가 아니다.
- **최신 보석 직접 정책:** 이전에 지정된 특수보석 **정확히 1개** 실제 장착; 일반보석 치명·가속·특화·유연 **각 1개** 기본. J에 포함되는 일반보석은 **서로 다른 두 가지 양수 2차스탯**이 붙은 보석만, **두 rating 모두** 합산. 단일 스탯 보석은 특수 효과 활성화를 위한 장착은 가능하지만 J에는 포함하지 않는다. 실제 기본 소켓/증명된 추가 소켓만 사용하고, 특수보석 정체·효과 독립 조사/효과 Native Gate 금지. SimC가 효과/APL/proc/DPS 계산.
- 검증된 동일 시즌 장비·마부·보석·영약·기름·G/J/F/O 정적 DB는 주간 SimC/게임 빌드·밸런스 패치만으로 폐기하지 않는다. 실제 아이템/콘텐츠 변경은 영향 범위 갱신; 시즌/확장팩 변경은 새 환경. 새 SimC는 바이너리/프로필/후보/iterations별 **DPS 캐시** 분리.
- 환경 READY 후 **기존 v139/v098/v096/v094 적응형 SimC**로 사용자별 DPS·SEM·95% 확정/관측 1위 구분, 스탯 비율·실질적으로 다른 근접 대안, 진행·취소·캐시·재개. 새 최적화 엔진/전문화 APL/효과 구현 금지.
- **제로베이스 T1**: 새 작업공간에서 구시즌 소스·캐시·기존 영수증/값을 정답으로 넣지 않고 외부 데이터/SimC로 현재 시즌을 신규 구축하는 엔진 시험. 정상 시즌 재사용과 이 특별한 T1 증명은 분리.

## 3. 현재 완료 근거 (Evidence)와 제품 연결 (Integration)

| 범위 | 실제 근거 및 재사용 | 마지막 미완료 |
|---|---|---|
| 수집·시즌 | KR 12.1.5.70783, 정확한 SimC commit c20e2ad52e4c33711f74272309a5748125175fe8, binary SHA256 980ed4640cecc3ed78b34ed0dc0363dbff2ed7d703174e9cc01f09d18570d36b. v161/v217 Wago **EXECUTED_AND_SEALED**, v191/v211/v213 **COMPILED_UNADMITTED**. v163 raid/tier·v165/v166/v167/v232 내부 일반 목걸이·서로 다른 두 반지 후보 보완. | 원본 컴파일 성공이 시즌 최종 인증은 아님. 최신 T1 season_join은 조건 미확정 상태. |
| G | v229/v230/v232/v233/v234/v277/v288 및 봉인 캐시 경로 보유. 마지막 영수증 G 진단은 **G_NATIVE_NUMERIC_REFERENCE_OBSERVED_JFO_PENDING**, 신규 Native 호출 **8회 보고**. | 공식 G=null. 8회의 개별 성공·G 값·유일 측정 후보를 추정하지 말 것. |
| J | v221/v266/v268/v271·P3-FM/FO/FP: 4종 이중 2차스탯 일반보석 source 후보·실 소켓 배치, 이전 지정 특수 1개 물리 장착. | 마지막 T1 user_selected_gem_ids=0, gem_layout=false, J=null; 실제 시즌 최고품질 4종 ID/공식 J·소켓 입력 승인 미완료. |
| F/O | v281 물리 ID↔SimC 토큰, v278 paired Native/caching, v269 precombat snapshot; P3-GH v233 G 전용 원본은 불변, 동일 v217 경로에 F/O 파생 프로필 봉인. 명시적 기름 미사용 O=0의 v222 회계 경로 기존 구현. | 마지막 T1 **AUTO_F_NEXT_MEASUREMENT_BATCH_PENDING**, **AUTO_F_HIGHEST_QUALITY_ITEM_AND_NUMERIC_BUDGET_SOURCE_PENDING**. F=null, O=null; 무작정 8회 cap 확대·효과 재현 금지. 선택 기름은 정확한 무기·손/O 필요. |
| 설치/카탈로그 | v222 공식 회계, v220/v196 4-family 정책 A, v212/v217 설치·봉인·재개, P3-FX/FY 동일 시즌 정적 설치 재사용은 합성 테스트 PASS. | G/J/F/O/B/T **모두 null**, READY=false, installed=false, 실제 검증 선택지 발행·v212 실 신규 시즌 설치 0. 합성 설치 테스트는 이 증거가 아님. |
| 적응형 DPS | v143/v139/v098/v096/v094의 26 DPS 시나리오와 adaptive·95%·캐시/재개 및 웹/Windows 코드·오프라인 시험. | 새로운 시즌 READY 이후 실제 사용자 E2E 미완료. |

**최종 실제 실전 T1:** [#42170351404](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42170351404), Artifact [13480598417](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42170351404/artifacts/13480598417), p3_fr_zero_base_t1_receipt.json. 이전 세션·ItemID 0, 신규 SimC 바이너리 컴파일 0, source_stage EXECUTED_AND_SEALED, source_compilation_missing=[], Native 호출 **8회 보고**, G/J/F/O/B/T 모두 null, ZERO_BASE_T1_NOT_READY, environment_installed=false. **Artifact는 작은 요약 JSON만 보존**하므로 Native 개별 측정 로그/실제 v278 캐시가 이 파일에 있다고 단정 금지. 각 PENDING 항목은 앞단 미완료의 연쇄 결과일 수 있다.

**주요 Actions 범위:** 최신 제품코드 [focused #42170351351](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42170351351) **325 tests=323 PASS/2 SKIP**. 직전 코드 SHA fd54da46a405821ba392016aeebc6267d9723e3b: [v212 #42170118202](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42170118202) Ubuntu·Windows 각각 **478 tests=474 PASS/4 SKIP**; [v113 #42170118227](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42170118227) 각 **223 PASS**, v181/v182 SUCCESS. 이전 [#42169345660](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42169345660) v269 precombat 오류는 P3-GH 코드 변경 전의 역사 실패. neck/finger2/403/timeouts 역시 이후 수정 전 역사 문제이며 현재 첫 장애라고 되돌리지 않는다. 역사 P3-BX/F/O Native 영수증은 해당 SimC·시즌·ItemID/옵션에만 유효.

## 4. 인계 시점 병목과 가장 짧은 로드맵

**P1 — 기존 성과 선조회 / REUSE·CONNECT:** 마지막 실제 F 추가 측정 대기의 원인을 v281 후보 목록→v278 before/after cache→v269 precombat source→v216 8-call 공유 cap/조건별 결과 경로에서 좁혀 본다. 현재 일회성 Actions는 **임시 작업공간**이고 Artifact에는 결론 JSON만 업로드하므로, 저장되지 않은 Native 상세 자료를 재사용 가능이라고 주장하지 않는다. 반복 T1보다 기존 v217 재개/봉인 방식으로 측정 결과를 보존할 수 있는 최소 연결이 더 효율적일 수 있다. 먼저 실제 증거와 캐시 보존 가능성을 확인하고 결정한다.

**P2 — 예산 소유권 연결:** 실제 G 관측·4개 이중 2차 일반보석 J와 1개 특수보석, 검증 F, 명시적 O=0 또는 선택 기름 O를 기존 v222 예산 provider로 조합. v220/v196에서 확인된 선택지만 발행, v212/v217 기존 설치·READY로 연결. J/F/O source-only와 공식 budget을 혼동하지 말 것.

**P3 — 최소 실증:** 변경 지점 focused 회귀 및 진짜 미해결 단계만 시험한 뒤, 원래 일회성 제로베이스 T1을 **필요할 때만 1회** 실행. G/J/F/O/B/T와 실제 installed 영수증으로 PASS/NOT_READY 판정. 전 전문화 Native·무조건 기존 Wago 재수집 금지.

**장기:** READY 후 하나의 정상 사용자 웹앱에서 26 DPS 적응형 SimC를 완성해 최적 CHMV 절대 rating·DPS/SEM/95%·근접 대안·캐시/취소·재개 제공. 다음 시즌에도 동일 엔진으로 최초 구축 또는 증분 갱신.

**필수 작업 규칙:** 기능 INDEX·실 코드·봉인 원본/Native/Actions·캐시를 선조회 → Evidence/Integration, 자료 부재 vs 제품 연결 누락 vs 선택 항목 보류 구분 → **REUSE / CONNECT / EXTEND / NEW / STOP** 선택 → 독립 작업 묶음 실행, 동일 조건 PASS/Native/캐시 재사용 → 추가 HTTP/Native/Actions·메모리·I/O·실행시간/복잡도 점검. 매번 **“이 작업이 다음 시즌에도 동일하게 작동하는 하나의 엔진 완성에 기여하는가?”** 자가검증.

## 5. 인계 반영·권한

이번 P3-GI는 **문서/인계만 갱신**: 본 정본, PROTOCOL 최신 진입점, INDEX G1/G2·관련 E3/D1·DEV.CONTINUITY, CURRENT 상단, 개발자 실행 노트, P3-GI note. 마지막 제품 코드 d9f05ecd와 v217 봉인 원본 그대로. **이 인계 작업에서 코드 변경·Wago 수집·Native/T1 실행 없음.** 후속 문서 CI는 신규 SHA에서 별도 대조.

**미승격:** 실제 G/J/F/O/B/T·정책 A 실 발행·환경 READY/T1·26 DPS 사용자 실 E2E·원본 v016 직접 바이트 통합. main/immutable v003/승인 v1.4.3 원본/Project Sources·Instructions 실제 UI/Work OS M0·Shared State·MAIN/WORK 권한·기존 주 제품 개발 채팅 소유권 변경 금지.

## 6. 새 채팅 시작 프롬프트

    SIMC SECONDARY OPTIMIZER를 읽기 전용으로 독립 복원해.
    GitHub: degong2-code/simc-secondary-optimizer-runner
    격리 브랜치: probe/chat-cache-v035-20261024
    최신 단일 인계: docs/CHAT_CONTINUITY_HANDOFF_20261106_P3_GI_ENGINE_FIRST_RESTORE.md

    먼저 격리와 main 실제 HEAD를 독립 조회하고 마지막 제품 코드 SHA와 문서 커밋을 구분해.
    인계→PROTOCOL→INDEX E3/E2/E1·D1/D2/B3·C1~C4·G1/G2→CURRENT→개발자 실행 노트→
    최근 P3-GH/GG/GF/FP/FQ/FX/FY/FR의 해당 자료→실 코드·봉인 SHA·Actions/Native 순서로 확인해.
    이전 P3-FK·역사 자료를 최신 실행 상태로 오해하거나 전체 과거 검증을 반복하지 마.

    최종 목적은 26 DPS(증강·탱커·힐러 제외)와 다음 시즌에도 통하는 단일
    Environment Build+적응형 SimC DPS 최적화 엔진이다. 기본 ilvl334/수동 최종 T의
    치명·가속·특화·유연 최적 절대 rating, 95% 판정·SEM·관측 최고·실질적으로 다른
    근접 대안과 캐시·취소/재개를 제공한다. 장비 추천·현 장비 재분배·독립 효과/APL 개발은 하지 마.
    환경 Gate는 v216 G/J/F/O→v222 B/T→v220/v196 검증 선택지→v212/v217 실제 READY/T1이다.
    특수보석 기존 ID 1개 물리 장착 + 일반보석 4종(치명·가속·특화·유연) 기본;
    J는 각 일반보석의 서로 다른 2개 양수 2차스탯 rating을 모두 합산,
    단일 스탯은 활성화 장착 가능해도 J 제외. 특수효과는 SimC에 맡겨.
    같은 시즌 SimC/게임 빌드·밸런스 변경만으로 검증 정적 환경을 폐기하지 마.

    인계 전 마지막 실제 제품코드 d9f05ecd009981ef603ccdfe8bcf0e4042a2f0b4,
    main 07133e0aaf738d6e4816a6486057b1cd49c018de(각각 재조회 필수).
    실제 T1 #42170351404 Artifact 13480598417는 Wago SEALED/v191-v211-v213 COMPILED,
    Native 호출 8회 보고, F_NEXT_MEASUREMENT_BATCH_PENDING,
    공식 G/J/F/O/B/T 모두 null, READY/installed false. focused #42170351351
    323 PASS/2 SKIP, v212 #42170118202 양 OS 474 PASS/4 SKIP는 이전 SHA.
    기존 일회성 Artifact는 후보별 Native/cache 원본 전체를 포함하지 않아 반복 측정 전
    v281/v278/v269/v217 worklist·캐시·재개를 먼저 확인해야 해.

    매 작업 전에 INDEX 자산/실 코드/원본·SHA·Actions/Native/캐시 선조회,
    Evidence와 Integration·실제 소스 부족과 미연결 분리, REUSE/CONNECT/EXTEND/NEW/STOP.
    독립 작업은 묶고 같은 조건 PASS/Native/캐시를 재사용하며 중복 HTTP·Native·Actions,
    메모리/I/O, 실행시간, 구조 단순화를 점검해.
    항상 “이 작업이 다음 시즌에도 동일하게 작동하는 하나의 엔진 완성에 기여하는가?” 자가검증.
    제로베이스 T1에 구시즌 정답이나 미검증 자료 주입 금지.

    첫 응답은 실제 양 HEAD, 핵심 영수증의 적용 범위, Evidence/Integration 완료·미완료,
    현재 병목/효율적인 대안, 간결한 단기·장기 로드맵, 미반영·미승격·권한만 보고하고 STOP.
    내가 명시적으로 '진행'이라 하기 전 개발·수정·커밋·신규 수집·CI/Actions/Native/테스트·
    공식 승격을 시작하지 마. main, immutable, Project UI/Work OS와 기존 주 채팅 소유권 유지.
