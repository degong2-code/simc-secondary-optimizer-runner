## 2026-11-09 P3-HAF 실제 SimC seed 원본 보존

[P3-HAF](notes/2026-11-09_p3-haf-native-seed-provenance-recovery.md): 실 Native 10회 [#42501052586](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42501052586) 성공, v291 2개 320 확인 JSON2·v065 Native receipt에는 서로 다른 시드가 있는데 v291 journal 전달이 누락됐음. 새 Native 없이 사실 메타데이터만 정확 복원, 옛 null journal은 해당 1필드 외 모든 SHA 재인증 뒤 조건부 재생. 95% 판정은 선택된 실측 쌍의 정규근사 한정, 다중비교 편향·전역 최적 인정 금지. 신규 코드 CI 미실행이면 PASS로 기록하지 말 것.

## 2026-11-09 P3-HAE typed12의 95% 확인 연결

[P3-HAE](notes/2026-11-09_p3-hae-short-budget-precision-contract.md): 이전 실제 8개 scout 이후 short budget 10~16에 한해 v290의 precision을 앞당김. v291 95%는 두 confirmed Native 실측 쌍 비교로만 사용하며 독립 seed·선택 편향 표시, 전역 최적 증명은 아님. 구 버전 결과의 임시 경로/정책 SHA 무검증 재사용 불가. 신규 Actions 결과 확인 전 성공으로 표기하지 말 것.

## 2026-11-09 P3-HAD 첫 >6 실 Native 완료 — 한정 실증

[작업·실 영수증](notes/2026-11-09_p3-had-first-over-six-native-pilot.md): 격리 코드 `a5931d33` [focused #42499184780](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42499184780) 461 PASS/2 SKIP, 요청 `1d480a25`, [real #42499288257](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42499288257) 환경 Native3+고양 DPS Native8(4+4·캐시 재생0 신규), 8 case SHA/엄격한 <50% cap 검증. 기존 2-tier 및 원본 v094 유지. 관측 최고 DPS186630.19±787.11 SEM(35 iterations)이며 전역최적/95% 확정/2000회 수렴이나 별도 프로세스 간 재개·웹 UI 완성 증거가 아니다. 다음은 긴 탐색·정밀화·효율 확인과 제품 사용자 경로 최소 연결. `main`/immutable/Project UI/Work OS/주 개발 소유권 변경 금지.

## 2026-11-09 P3-HAC 최신 단일 인계·독립 복원 전용

**최신 진입점:** [P3-HAC](../CHAT_CONTINUITY_HANDOFF_20261109_P3_HAC_MULTISCALE_ENGINE_RESTORE.md) → 이 PROTOCOL 상단 → INDEX 관련 기능/OPTIMIZER.POLICY/PRODUCT.E2E → CURRENT 최상단 → v1.4.3+개발자 실행 노트 → 해당 코드·Actions/Native 원본. P3-HM 이하 '최신'은 **작성 당시 역사 상태**이며, 당시 'READY/DPS 미완료'는 이후 P3-HN~HU 실제 한정 실증으로 일부 해소됨. 현재 P3-HAB 최종 T 기준 **각 스탯 strict 50% 미만**과 v290/v291 장기 엔진 개발 증거가 우선; **실 >6 native/일반 사용자 장기 웹 UI는 미검증**. A~G 기존 원본·코드·영수증을 선조회하고 REUSE/CONNECT/EXTEND/NEW/STOP 결정, 독립 변경 묶기·동일 범위 회귀 재사용. 새 채팅 **첫 응답 읽기 전용 HEAD·증거·장단기 로드맵 보고 후 중단**, 사용자 `진행` 전 개발/수정/수집/CI·Native·테스트/승격 일체 금지. main/v003 immutable/Project UI/Work OS/주 개발 소유권 불변.

## 2026-11-08 P3-HN 실제 source→v212 READY 성공 및 다음 소유 경계

격리 브랜치 코드 `68daa480`/one-shot `c7fa9789`: 기존 T1에서 빠진 빌드별 `v271` 명목 J 입력을 원래 `v216` Build에 전달. [offline #42460176730](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42460176730) 402 PASS/2 SKIP, [실 T1 #42460255527](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42460255527) `ZERO_BASE_T1_PASS`, 최종 **G2850 J92 F165 O0 B3107 T3107**, `v212/v217` installed/READY TRUE, Native3(G1/F2), compiler missing []. **하나의 70783/334 Ret 기준 사례**만 실증; 기존 실패 #42332836316은 보존. [노트](notes/2026-11-08_p3-hn-real-gjfo-ready-one-case.md). 다음은 신뢰 원본을 새로 만들지 말고 새 v212 설치 타입을 기존 `v098/v096/v094` 실제 DPS 사용자 경로에 연결. 개별 보석 효과 Gate/새 최적화 엔진/무조건 Native 반복 금지. `main`·immutable·Project UI·Work OS·주 개발 소유권 유지.

## 2026-11-08 P3-HM 최신 새 채팅 인계/작업 제한

**단일 복원 정본:** [P3-HM](../CHAT_CONTINUITY_HANDOFF_20261108_P3_HM_ENGINE_REUSE_FIRST_RESTORE.md) → 이 PROTOCOL → INDEX의 E3/E2/E1·A3/A1/A2·B3·C4/C3/C2/C1·D1/D2/D3·F1/F2·G1/G2 → CURRENT/개발자 노트 → P3-HL/HK/HJ/HI 실제 필요한 코드·SHA·영수증만. P3-GX 이하 "최신"은 역사. 새 채팅 **첫 응답 읽기 전용 복원 보고 후 즉시 STOP**, 사용자 `진행` 이전 새 코드/문서/커밋/수집/CI·Native/승격 금지.

**A~F 전 엔진:** 다음 시즌 동일 입력·source만 교체하여 재사용되는 공통 엔진 완성을 최우선. 기존 증거 먼저 찾아 REUSE/CONNECT/EXTEND/NEW/STOP 판단. P3-HK J 명목 source 연결 및 P3-HL 정확 빌드 READY 오인 방지는 **오프라인 코드 PASS**, 실 70783 G/J/F/O/B/T·v212 READY/DPS는 아직 미완료. P3-HE 보석별 Native 실측 Gate는 STOP. 같은 시즌 패치 변경 시 과거 정적 캐시 무조건 폐기하지 않되 다른 게임 빌드 READY를 자동 승계하지 않는다.

## 2026-11-08 사용자 직접 재강조 — 완성 기능 전체에 적용할 엔진 우선 원칙

**이번 시즌 시험만 통과시키기 위한 특례가 아닌, 다음 시즌에도 같은 코드·입력 계약과 원본만 갱신하여 작동하는 엔진 기능**을 목표로 한다. J뿐 아니라 기존 완료 기능(A 원본·봉인, B 대표 장비/G, C 보석, D 소모품/E·모듈, E G/J/F/O·정책 A·설치, F 26 DPS 적응형/캐시·취소·재개) 전체의 후속 변경은 다음 기준을 선적용한다: **기존 함수/원본/CI/Native 증거 재사용 → 미연결 제품 흐름 연결 → 실제 누락한 최소 근거 보완 → 대응이 없을 때만 신규 기능**. 시즌 ItemID/rating/품질·소켓·무기 조건을 코드 상수로 넣지 않으며 특정 시즌의 합성 PASS는 새 시즌 자동 갱신 완료 증거가 아니다.

**정적 자료 수명과 설치 READY 구분:** 같은 시즌의 SimC revision 또는 게임 빌드 변경만으로 정적 자료를 삭제하거나 전량 재수집하지 않는다(P3-FX). 그러나 현재 요청한 빌드와 다른 구 버전의 `v212` READY를 근거 없이 그대로 반환하지 않는다. 빌드가 달라졌다고 새 시즌·아이템 변경을 단정하지 않으며, 향후 정확한 시즌/콘텐츠 동일성 원본을 재사용하여 필요한 부분만 재봉인한다. 실 DPS 결과는 SimC 바이너리·프로필·옵션·후보·iterations·전투조건·환경 identity로 따로 관리. **P3-HL** [작업 및 영수증](notes/2026-11-08_p3-hl-cross-season-environment-cache-identity.md). 이는 새 인증 Gate나 G/J/F/O 전체 재측정 요구가 아니다.

## 2026-11-08 P3-GZ 최신 범위 교정 (P3-GX 복원·P3-GY 코드 이후)

기존 P3-GX 읽기 경로·권한·인계 신분을 유지한다. [P3-GZ](notes/2026-11-08_p3-gz-pinned-simc-gem5-real-native.md)는 기존 정확 SimC Native G 원본 입력과 바이너리를 재사용해 특수1+일반4 `gem_id`가 JSON2 `buffed_stats`에 CHMV +92를 실제 적용한 **로컬 단일 프로필 증거**다(신규 Native4회, CI 실행과 구분). `gear` 레코드만으로 보석 미적용이라 단정하지 말 것. 동일 시즌 최고품질 일반보석 공식 J source-owner/예산·READY는 미완료. 인게임 소켓 획득 아이템·주문/별도 효과 Gate는 STOP, 원래 v222/v220/v196/v212/v217 CONNECT가 다음 우선. 제품 코드 P3-GY 3ceb2566의 CI는 별도 PASS, 이번 문서 영수증은 새 Native CI가 아님. `main`/immutable/Project UI/Work OS/소유권 변경 없음.

## 2026-11-08 최신 단일 인계 P3-GX — 읽기 전용 새 채팅 (P3-GI 후속)

**진입점:** [P3-GX 단일 인계](../CHAT_CONTINUITY_HANDOFF_20261108_P3_GX_ENGINE_FIRST_RESTORE.md) → 이 PROTOCOL → INDEX C3/C4/C1/C2·E3/E2/E1·B3/D1/D2·G1/G2 → CURRENT 최신 상단 → 개발자 실행 노트 → 필요한 코드/원본/실 영수증. 과거 P3-GI 이하 '최신' 표현은 당시 역사. **첫 응답은 격리/main HEAD 독립 조회, Evidence/Integration·병목·장단기 로드맵 읽기 전용 보고 후 즉시 STOP**; 명시적 '진행' 전에 코드/문서 수정, 수집, CI/Actions/Native/테스트, 승격 금지.

**최신 실제 범위:** 제품 코드 `e368944b42803f4894f0ddc40588a338e1c3abe1` (v232 소켓 편향 선택 철회, source-first 대표 장비 복원), 인계 전 격리 HEAD `1861f9d88f21d694652098e9dee89659d44640d8`, main `07133e0aaf738d6e4816a6486057b1cd49c018de`; [focused #42386036556](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42386036556) **391 PASS/2 SKIP, Native0**, [v212 #42385936229](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42385936229) SUCCESS. 실 결합 T1 [#42332836316](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42332836316) **FAILURE/NOT_READY**, 원래 대표 G2850/F165 Native3·J 미확정·공식 B/T/READY 미완료. P3-GW는 **소켓 N개 전부 gem_id, 일반 4종 최소/추가 고정 순환**으로 v216/v271을 수정했으나 실제 SimC/시즌 J 공식값 검증은 아직 안 됨. 기존 특수보석 효과·획득용 소켓 추가 아이템 인증/별도 Gate 금지. user 직접 결정이 역사 intrinsic-only 정책보다 우선. 동일 시즌 정적 재사용·DPS 캐시 분리 유지.

## 2026-11-06 최신 단일 인계 P3-GI — 읽기 전용 새 채팅

**최신 단일 진입점:** [P3-GI 인계](../CHAT_CONTINUITY_HANDOFF_20261106_P3_GI_ENGINE_FIRST_RESTORE.md) 및 [노트](notes/2026-11-06_p3-gi-engine-continuity-handoff.md). 아래 P3-FK와 이전 인계의 '최신' 표기는 작성 당시 역사 상태. 새 채팅은 격리와 main 실제 HEAD를 각각 독립 조회 → P3-GI → PROTOCOL → INDEX E3/E2/E1·D1/D2·B3·C1~C4·G1/G2 → CURRENT → 실행 노트 → 관련 P3-GH/GG/GF/FP/FQ/FX/FY/FR 코드/원본·영수증만 확인한다. **첫 응답은 읽기 전용 복원·장단기 로드맵 보고 후 즉시 STOP**, 사용자 '진행' 전 코드/문서 변경, 신규 HTTP/CI/Native/테스트/승격 금지.

**기준 근거:** 제품 코드 d9f05ecd009981ef603ccdfe8bcf0e4042a2f0b4, main 07133e0aaf738d6e4816a6486057b1cd49c018de. 실 #42170351404: 70783 source SEALED·컴파일 성공, Native 8회 보고, F AUTO_F_NEXT_MEASUREMENT_BATCH_PENDING, 공식 G/J/F/O/B/T 모두 null·READY/installed false. 집중 #42170351351 325 tests/2 SKIP(323 PASS), v212 #42170118202 양 OS 478 tests/4 SKIP(474 PASS)는 직전 코드 SHA. 다음은 v281/v278 F worklist·캐시/원본 Native 보존 여부 선조회 후 최소 연결; 무조건 full T1 반복 금지. 최신 직접 정책: 26 DPS, 다음 시즌 재사용 단일 엔진, 특수 1개+일반 4종(각 일반보석은 서로 다른 2개 2차스탯을 가진 경우만 J 귀속), SimC 효과 신뢰, 같은 시즌 SimC 버전 변경만으로 정적 데이터 폐기 금지. **실 READY/T1은 아직 미완료.**

**2026-11-06 사용자 승인 P3-FX 정적 데이터 수명 교정:** 동일 확장팩·시즌의 게임 빌드 또는 SimC revision·밸런스 변경만으로 검증된 장비·티어·보석·영약·기름·마부·G/J/F/O를 폐기하거나 전체 제로베이스 재구축하지 않는다. 관련 아이템·콘텐츠의 실변경이 확정되면 영향 범위만 증분 갱신; 시즌·확장팩 전환 시 환경 재평가. 신규 원본의 `v229` 게임 빌드 검증은 출처 일치용이지 기구축 시즌 DB 재사용 Gate가 아니다. 새 바이너리의 DPS 캐시만 별도 유지. [P3-FX 근거/검증](notes/2026-11-06_p3-fx-same-season-static-versus-simc-runtime.md). 정적 SHAs 동일은 READY 또는 새 시즌 여부 인증이 아니다.

# 개발 연속성 규약 · 2026-11-03 사용자 직접 교정

**2026-11-06 사용자 직접 교정 [P3-FM](notes/2026-11-06_p3-fm-four-ordinary-stat-default-simc-owned-effects.md):** 기존 특수보석 정체·효과의 별도 식별·재검증을 중단하고 SimC를 신뢰한다. 이미 지정된 특수보석 1개+일반보석 치명타·가속·특화·유연 각 1개의 실제 물리 소켓 배치를 기본 적용한다. 소켓 5개 미만은 PENDING, 이전 시즌 GemID 재사용/새 특수보석 탐색/별도 효과 Native Gate 금지. P3-FL LimitCategory 탐색 코드는 철회, 기록은 역사. 기존 P3-FI의 특수보석 정확히 1개 장착 계약은 유지한다. 최신 사용자 결정이 FJ/FK의 이전 미완료 기능 제안보다 우선한다.

**권위:** 최신 사용자 직접 결정. 이 문서는 GitHub 격리 브랜치의 **개발/인계 운영 규약**이며 승인된 제품 설계 v1.4.3의 원문, main, immutable v003, 원본 v016, Project UI/Work OS를 변경하지 않는다.

**환경 입력 관련 필수 선조회:** 레벨·종족·특성·음식/물약/증강·보석/가변 소켓·영약/기름·Omnium·품질/정책 A 작업 전에 [2026-11-04 환경 구축 입력 12항목 책임표](ENVIRONMENT_BUILD_INPUT_SCOPE_20261104.md)를 읽고, 각 항목의 REUSE/CONNECT/EXTEND/STOP·기본 G/J/F/O와 선택형 기능 경계를 확인한다. 이 문서는 승인 원문 교체가 아닌 기존 정책과 구현을 구분하는 개발 색인이다. 특히 P3-BN SimC 기본 level 및 P3-BZ 기존 가변 socket_plan 구현을 재개발하지 않는다.

## P3-FK 현재 단일 인계·읽기 전용 새 채팅 (2026-11-05)

**현재 인계 정본:** [P3-FK 엔진 연속성](../CHAT_CONTINUITY_HANDOFF_20261105_P3_FK_ENGINE_FIRST_RESTORE.md). 이전 P3-EV/ES/EN/EE/DW/DO는 작성 당시의 역사 정본. 새 채팅은 **격리/main HEAD 각각 독립 조회 → P3-FK → 이 PROTOCOL → INDEX E3/E2/E1·C1~C4 → CURRENT 상단/개발자 실행 노트 → P3-FJ/FI/FH/FG/FD/FE 및 필요한 E* → 해당 실제 코드·봉인 원본·Actions/Native** 순서로 좁혀 본다. **새 채팅 첫 답변은 읽기 전용 복원 보고 후 STOP**, 명시적 '진행' 이전 수정·수집·CI/Native/테스트·승격 전면 금지.

**제품 변경 경계:** P3-FJ는 v232 봉인 기본 소켓과 v271 특수보석 정확 1개+일반 N개 장착 위치를 **역할별 ID 제공 시** 연결했고 focused 270 PASS. **보석 정확 역할/ItemID source-owner 자동 선택과 실 신규 시즌 READY/T1은 아직 미완료**. P3-FD~FG J/F 원본 조건부 v222 설치 및 P3-FH 발견 최대 F opt-in·P3-FE source_relation 재사용은 기존 자산. 새로운 소켓/보석 엔진·기능 게이트 재개발 금지. 목적은 다음 시즌 26 DPS 공통 엔진 하나.

## P3-EV 당시 최신 인계/실행 경계 (2026-11-05)

**단일 인계 정본:** [P3-EV 환경 설치 엔진 인계](../CHAT_CONTINUITY_HANDOFF_20261105_P3_EV_ENGINE_INSTALL_RESTORE.md). 다음 채팅은 격리/main HEAD를 각각 독립 조회 → P3-EV → 이 규약 → [INDEX 기능 라이브러리](INDEX.md)의 **E3→E2→E1**, 필요 시 B3/C4/D1/D2만 → [CURRENT](../CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 최상단 → P3-EU/ET/EV 노트 및 실제 코드·봉인 원본·CI/Native. 기존 P3-ES/EN/EE는 **역사 인계**이며 전체 P3 기록의 순차적 재감사는 금지한다.

**최상위 개발 목표의 흔들림 금지:** 26 DPS 공통의 **다음 시즌에도 재사용 가능한 자동 환경 구축·DPS 최적화 엔진**을 완성한다. 이번 시즌의 숫자를 고정하는 것은 목표가 아니며 현재 시즌을 '신규 시즌'으로 보고 처음부터 정상 Build를 수행하는 **실제 T1 시험**은 엔진을 검증하는 수단이다. 현 P3-EU에서 `v216` 내부 검증 입력 provider → `v222/v196/v212` → `v217` 설치/재개 **합성 경로는 연결 완료**, 그러나 실제 자동 source-owner 공급자·실 제품 T1은 미완료다. 문자열 `VALID_SAME_SEASON_SOURCE`, callable 형태나 합성 READY가 출처 검증을 대체하지 않는다. 증거 부족·원본 미연결·선택 항목 불필요를 먼저 구별하고 불필요한 Gate/수집/Native 재개발을 금지한다.

**새 채팅 첫 동작은 읽기 전용 독립 복원 보고 후 STOP.** 사용자 명시적 `진행` 전에는 코드·문서 수정/커밋, 신규 원본 수집·CI/Actions/Native/테스트 실행, 공식 Project UI·Work OS/원본 승격 금지. 일반 개발도 기존 주 제품 개발 채팅 소유권 원칙을 따른다.

## 최신 운영법 · P3-ES 기술 자산 중심 탐색 (2026-11-05)

**현재 탐색 정본:** [기능별 라이브러리 INDEX](INDEX.md) — A~G 상위/하위 영역의 **재사용 함수·증거 적용 범위·미연결·재개발 금지**부터 확인한다. 16개 기존 Capability 키는 이 파일 하단의 6열 호환 표로 보존하며, 기존 수백 개 작업 번호의 상세 원문은 [2026-11-05 INDEX 스냅샷](HISTORICAL_INDEX_20261105_PRE_LIBRARY.md)과 개별 notes에서만 조회한다. 이 새 지도는 증거 인증이 아닌 검색 최적화다.

**작업 라우팅:** 환경 신규 READY는 `E3→E2→E1`, 필요 시 `B3/C4/D1/D2`만. 보석은 `C1~C4`, 시즌 수집은 `A1~A3`, 사용자 최적화는 `F1/F2`, 인계는 `G2`부터. 현재 코드의 PENDING만으로 **실제 소스 부족**을 추정하지 않고 기존 소스 미전달/선택 항목 미요구/검증 미완료를 구분한다.

**갱신 정책:** 작업 번호를 표에 시간순 누적하지 않는다. 기능 행의 현재 함수·확립된 Evidence/적용 범위·Integration·다음 최소 결손만 갱신하고, 하단 기존 Capability 행에는 **해당 키에 속하는 최신 노트 1개 링크**를 유지한다. 이전 인계·실패·영수증은 삭제하지 않고 역사 스냅샷에 보관한다. 이미 있는 코드·캐시·Native/Actions를 재사용한 뒤 필요한 것만 EXTEND한다.

**새 채팅 단일 진입점:** [P3-ES 자산 라이브러리 인계](../CHAT_CONTINUITY_HANDOFF_20261105_P3_ES_ASSET_LIBRARY.md). 아래 P3-EN/EE/DW/DO의 '현재 정본' 표기는 **작성 당시 역사 기록**이다. 새 채팅은 양 HEAD 독립 조회→P3-ES→PROTOCOL→관련 INDEX 영역→CURRENT 상단→실 코드/원본/CI·Native; 첫 응답 복원 후 사용자 `진행` 전 **STOP**. 현재 제품 T1 READY·공식 G/J/F/O/실제 정책 A 발행은 미완료.

## 매 논리적 작업 묶음마다 필수: 4단계

1. **선조회(작성·추가 검증보다 먼저).** [INDEX.md](INDEX.md)의 해당 **A~G 기능 하위 영역**을 먼저 선택하고, 대응하는 16키 `Capability`와 키워드·구현 함수·Evidence 범위를 좁혀 관련 **기존 원본 영수증과 실제 코드**만 확인한다. 필요하면 GitHub 전체 코드/역사 기록으로 좁혀 검색한다. 검색어가 없으면 새 고정 capability 키를 추가한다. **현재 코드의 `false`, `PENDING`, 미완료 문구만으로 원본 증거 부재를 단정하지 않는다.**
2. **문제 구분·재사용 결정.** `Evidence`(어떤 사실을 어떤 시즌/빌드/옵션까지 확립했는가)와 `Integration`(제품에 연결되었는가)를 **따로** 판정한다. `REUSE`(이미 증명/구현된 부분), `CONNECT`(연결만 미완료), `EXTEND`(실제 부족한 근거만 보완), `NEW`(기존 대응 없음), `STOP`(불필요/범위 외) 중 하나와 근거를 선택한다. 새 인증 Gate·새 Native/HTTP는 실제 누락된 사실과 기존 증거로 해결 불가능한 이유가 특정된 경우에만 검토한다.
3. **한 작업 = 한 짧은 GitHub 노트.** `notes/YYYY-MM-DD_<task-slug>.md`를 작업 전부터 기록해 작업 범위·재사용 근거·결정·변경·시험·남은 과제·효율을 작성하고, 해당 라이브러리 기능 행의 현재 구현/남은 결손과, 하단 16키 표의 해당 `Last note` 링크 **1개**를 갱신한다. 이전 P3 작업을 시간순으로 라이브러리에 계속 추가하지 않는다. 독립 가능한 여러 세부 작업은 하나의 **논리적 묶음**에 포함 가능하다. 파일별·커밋별 문서를 만들지 않는다. 기존 기록의 사실 오류는 후속 기록에서 교정하고 과거 영수증·실패 이력을 삭제하지 않는다. 새 GitHub 커밋 또는 작업 종료 전에 기록을 반영한다.
4. **인계는 P3-ES와 라이브러리 우선.** 새 채팅: 양 HEAD → P3-ES 인계 → 이 규약 → INDEX의 관련 A~G 하위 영역·Capability 행 → 필요할 때만 해당 note → 원본 영수증/코드 순서로 읽는다. `CURRENT`의 `미완료` 요약만으로 개발을 시작하지 않는다. 인계에는 **재사용 가능한 완료 사실·정확한 적용 범위 / 연결 미완료 / 실제 소스 부족 / 다음 최소 작업 / 검증 방식**을 각각 명시한다.

## 짧은 기록의 정형 필드

[노트 양식](TEMPLATE.md)의 8개 필드(`Capability`, `Keywords`, `Prior evidence`, `Decision`, `Changes`, `Verification`, `Remaining`, `Efficiency`)는 **모두 필수**, 본문은 가능한 20줄 내외, 최대 45줄. 기존 문서/Actions/커밋을 링크로 가리키며 내용을 중복 복사하지 않는다. `Verification`에는 **새 실행 PASS/FAIL, 역사 증거 재사용, 이번에 하지 않은 HTTP/Native**를 분리한다. CI 미확인이면 `NOT_RUN/NOT_VERIFIED`라고 쓴다.

**충돌 처리:** 인덱스는 증거 **위치와 요약**이지 원본보다 높은 진실 출처가 아니다. 최신 사용자 결정 > 승인 설계 > 해당 코드/실제 원본·Native·Actions 영수증 > 인덱스·인계 요약. 반례가 발견되면 관련 note에 교정·범위를 기록하고 INDEX 상태를 수정한다.

**경량 안전장치:** `python tools/check_development_ledger.py`로 INDEX/노트 구조·링크·상태를 네트워크/Native 없이 검사한다. `--since <task-base-ref>`는 해당 작업 범위의 코드·테스트 변경에 노트가 포함되었는지 점검한다. 이는 제품 READY/효과 인증 Gate나 반복 CI/Native 시험이 아니다. 작업 기준 커밋을 명시하지 않는 한 임의로 옛 main 전체 diff를 검사하지 않는다.

**성능·설계:** 기존 원본·동일 시즌 SHA/검증 결과·캐시·Native/CI를 재사용하고, 실제로 부족한 범위만 보완한다. 새 코드 변경마다 중복 HTTP/Native, 캐시 무효화, 메모리/I/O, 전체 시간·구조 간결성을 평가한다. 장기 목표는 **26 DPS용 하나의 재사용 가능한 시즌 G/J/F/O Environment Build → B/T → 기존 적응형 SimC**이며 별도 효과 엔진/전수 장비 DB/추가 인증기 개발이 아니다.

## 새 채팅 인계 복원 동작 · P3-DO 최신 (2026-11-04)

새 채팅 단일 진입점은 [P3-DO 인계](../CHAT_CONTINUITY_HANDOFF_20261104_P3_DO_ENGINE_FIRST.md). 기존 [P3-DF](../CHAT_CONTINUITY_HANDOFF_20261104_P3_DF_ENGINE_RESTORE.md)는 역사 인계다. 격리/main HEAD 각각 독립 조회 → PROTOCOL → INDEX → P3-DN/P3-DM 및 관련 노트 → CURRENT/실행 노트/승인 v1.4.3 → 코드·원본·Actions/Native 영수증 순서로 **읽기 전용** 복원. P3-DG 이후 gear/tier raw SHA 연결·P3-DK 가변 소켓 연결을 다시 미구현으로 되돌리지 않는다.

**최신 P3-DN:** [v212 #41790639319](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41790639319) Ubuntu/Windows 각각 444 tests(440 PASS/4 SKIP)/0 FAIL, [focused #41790639275](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41790639275) 226 PASS/DEV_LEDGER_PASS. 기존 봉인 source_relation 1 family만 연결; `simc_input/product_input/chmv_budget`와 실제 선택지 발행·새 시즌 READY·26 DPS Native E2E는 미완료. 인계 작성/등록은 제품 통합·Native PASS가 아니다.

**새 채팅 첫 응답은 HEAD·핵심 증거·완료/미완료·병목·효율·로드맵·권한 복원 보고 후 STOP. '진행' 이전 개발/코드·문서 수정/커밋/수집/CI·Actions·Native/테스트·공식 승격 금지.** GitHub 문서는 Project UI/Work OS 등록이나 main 병합 증거가 아니다.

## 새 채팅 인계 복원 동작 · P3-DW 최신 (2026-11-05)

- 새 채팅의 **단일 정본**: [P3-DW](../CHAT_CONTINUITY_HANDOFF_20261105_P3_DW_ENGINE_FIRST.md). 위 P3-DO는 역사 기록. 최신 격리/main HEAD를 각각 독립 조회한 뒤 PROTOCOL→INDEX→P3-DN/DM·P3-DS/DT/DU/DV→CURRENT→개발자 실행 노트→승인 v1.4.3→실제 코드/Actions·Native 증거 순서로 읽는다.
- **지금의 완료 Gate:** 하나의 웹앱 `v216` Environment Build가 G/J/F/O·B/T·정책 A 검증 선택지·시즌 설치/READY를 만든다. 이미 개발된 사용자별 v098/v096/v094 DPS 최적화 실행은 **후속 메인 기능**이므로 환경 READY 선행 Gate가 아니다. 최종 제품 목표는 26 DPS 공통 하나의 엔진.
- P3-DV 코드/오프라인 PASS는 자동 F 후보 측정 연결까지의 증거이지 최고품질·예산 승인 또는 전체 T1 READY가 아니다. 새 채팅 첫 답변은 **읽기 전용 복원 보고만** 하고 **'진행' 전 일체 수정·CI/Native/게임 HTTP/테스트·승격 금지**.


## 새 채팅 인계 복원 동작 · P3-EE 후속 정본 (2026-11-05)

- **가장 최근 단일 진입점**: [P3-EE](../CHAT_CONTINUITY_HANDOFF_20261105_P3_EE_ENGINE_FIRST.md), [작업 기록](notes/2026-11-05_p3-ee-engine-continuity-handoff.md). 위 P3-DW/DO는 이전 인계 시점 기록이다. 격리/main 실제 HEAD 각각 조회 → P3-EE → 이 규약 → INDEX → 최근 P3-DX/DY/DZ/EA/EC/ED 및 관련 P3-DN/DM/DS/DT/DU/DV → CURRENT → 개발자 실행 노트 → 승인 v1.4.3 + 최신 사용자 직접 정정 → 실제 코드·원본·CI/Native 영수증 순서.
- **제품 핵심:** 다음 시즌에도 쓰이는 **26 DPS 공통 하나의 엔진**. 현재 T1 Gate는 사용자 웹 `v216` 새 시즌 G/J/F/O → `v222` 공식 B/T → 정책 A 최고 품질 선택지 실제 발행 → `v212` 설치·READY. 후속 `v098/v096/v094` DPS 실행을 환경 READY 필수 Gate로 만들지 않는다. **특수 보석은 정확히 1개 필수**, P3-EB의 0개 허용은 P3-EC에서 철회. P3-ED는 동일 빌드 물리 ID 확인 **source-only**, 실제 품질/효과/소켓 인증 아님.
- 첫 응답은 **GitHub 양 HEAD·실제 영수증·Evidence/Integration 완료/미완료·효율·단기/장기 로드맵·권한**을 독립 복원해 보고한 뒤 **STOP**. 사용자 명시적 **'진행' 이전 문서/코드 수정·커밋·원본 수집·Actions/Native/테스트/공식 승격 전면 금지**.


## 새 채팅 인계 복원 동작 · P3-EN 최종 후속 정본 (2026-11-05)

- **현재 단일 진입점:** [P3-EN](../CHAT_CONTINUITY_HANDOFF_20261105_P3_EN_ENGINE_FIRST.md) / [노트](notes/2026-11-05_p3-en-engine-continuity-handoff.md). P3-EE/DW/DO는 각 시점의 역사 인계이며 삭제하지 않는다. 격리/main 실제 HEAD를 각각 조회 → P3-EN → PROTOCOL → INDEX → P3-EF~EM·선행 P3-DX~ED/DN~DV → CURRENT/실행 노트/승인 v1.4.3 → 실제 원본·코드·Actions/Native를 독립 대조한다.
- 최신 작업 P3-EM의 동일 원본 v266 조인 재사용 **250 PASS**, 이전 P3-EL v212 양 OS **444 PASS/4 SKIP는 역사 범위**. 이는 제품 T1/공식 GJFO·Policy A 발행/READY가 아니다. 최종 목표는 **26 DPS 공통 재사용 가능한 단일 엔진**; 특수 gem 정확 1개 필수, v098 DPS는 환경 READY 이후. 작업 전 Evidence/Integration 분리하고 REUSE/CONNECT/EXTEND/NEW/STOP, 원본·검증 선조회, 논리적 묶음/캐시·효율 점검 필수.
- **새 채팅은 첫 응답에서 복원 보고 후 즉시 STOP. 사용자 '진행' 전 개발·문서/코드 수정·커밋·HTTP/Native/CI/Actions/테스트·공식 승격 금지.** 이 문서 갱신 자체는 Project UI/Work OS/main 적용 증거가 아니다.
