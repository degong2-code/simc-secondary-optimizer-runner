# SIMC SECONDARY OPTIMIZER — P3-DF 단일 새 채팅 인계
2026-11-04 · 문서·증거 정본 · 이번 인계는 코드 개발/시험/공식 승격이 아니다.

## 1. GitHub 복원과 최신 권위
- 저장소: degong2-code/simc-secondary-optimizer-runner; 격리 브랜치 probe/chat-cache-v035-20261024.
- **인계 문서 작성 전 독립 확인**: 격리 HEAD 8454adcc11e8ec420834686e26095fed82f37f48; main HEAD 07133e0aaf738d6e4816a6486057b1cd49c018de. **본 문서의 커밋으로 HEAD가 이동하므로 새 채팅은 양쪽을 독립 재조회해야 한다.**
- 최신 사용자 직접 결정 > [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) + 비충돌 과거 승인 정책 > 실제 코드/원본/Actions·Native > 과거 인계. 구 v1.4.1의 27 DPS·증강 포함 기록은 역사 자료일 뿐: **26개 DPS, 증강 기원사·탱커·힐러 제외**.
- 사용자 보고 원본 최신은 v016_SCENARIO_CONTRACT: 원본 bytes/영수증 독립 확인 전 직접 병합 완료 아님. main, immutable v003, Project Sources/Instructions UI, Work OS M0/Shared State, MAIN/WORK 권한은 별도 승인/실제 증거가 있어야 변경 가능하다.
- 이 문서가 최신 단일 인계. [기존 P3-CV 인계](CHAT_CONTINUITY_HANDOFF_20261104_P3_CV_ENGINE_RESTORE.md)는 과거 P3-CU 시점 스냅샷.

## 2. 최종 목표: 개별 기능이 아닌 재사용 가능한 단일 엔진
26 DPS에서 미래 파밍 목표 **치명/가속/특화/유연 절대 rating**을 SimC DPS 최대화로 찾는다. 목표 아이템레벨 기본 334 또는 사용자가 지정한 **기름 포함 최종 T**. 현재 착용 장비 재분배·장비 조합 추천·획득 경로·시즌 전체 장비 DB가 아니다. 사용자는 캐릭터/특성, 목표, 장신구2, 선택 특수장비·장식 최대2, 보석/영약/무기 기름/전투조건을 입력. 일반 장비·무기·티어4·주능력치와 SimC 프로필은 내부 생성한다.

**새 시즌 전체 G/J/F/O**를 원본 기반 자동 구축한 뒤 B=G+J+F, T=B+O, 최종 스탯=c_base+o를 자동 재계산한다. 수동 최종 T 우선(B=T-O), O는 적용 가능한 무기 손별 고정·gear에 한 번만, 정확 L은 G 내부 하한, E는 승인 회계에 따라 한 번, 장신구 고정치는 자유 G 밖. 제작 초기 50:50 잠금 금지. 구 시즌 79x2/J138/F165/O16+16을 새 시즌 검증값으로 복사 금지. 품질/효과/사용 조건·ItemID·SimC 입력·예산 소유권이 검증된 최고 품질 선택지만 Policy A 자동 등록; 일반 임시 마부 제외, **무기 기름은 별도 지원**, 확장팩 특수 시스템은 별도 on/off 모듈.

출력은 절대 rating와 비율, DPS·SEM, **95%만**의 판정/관측 최고·우위 미확정, 의미 있는 근접 대안, 진행·로그·캐시·취소·재개. 전역 최적해 보증 금지. SimC가 효과/proc/APL/DPS를 책임진다; 효과 재구현·새 최적화 엔진·독립 효과 인증 Gate 금지. 같은 시즌 정적 아이템 캐시는 SimC revision만으로 폐기하지 않고 DPS 캐시는 실제 바이너리/환경/프로필/아이템/전투/iterations별 분리.

## 3. 최신 완료·미완료 구분 (Evidence ≠ Integration)
| 구간 | 코드·증거 REUSE | 범위 제한/다음 gap |
|---|---|---|
| [P3-DA](development/notes/2026-11-04_p3-da-v222-direct-numeric-gjfo.md) / P3-CZ | v216 기존 G(v277)·J(v271)·물리 F/O(v278/281)·무기 마스크(v286) → 기존 v222 source-only B/T 산술, 수동 T/고정 O 검증. focused 204/200 PASS | 원본 전체 새 시즌 READY·Policy A 아님. 누락/비정적 관측=0 아님 |
| [P3-DB](development/notes/2026-11-04_p3-db-season-profile-serializer.md) / [P3-DC](development/notes/2026-11-04_p3-dc-adaptive-seed-typed-budget.md) | v108/v091/v098 새 시즌 영약·기름 ID/SimC token·J/F/O 직렬화, v061/v062/v065 기존 B/스탯별 F·O 하한/초기 후보 2개. focused 212/213 PASS | 미승인 숫자 미리보기 자체는 실행용 인증이 아님 |
| [P3-DD](development/notes/2026-11-04_p3-dd-admitted-season-v096-native-entry.md) | **같은 시즌 v216/v223 승인 영수증이 있을 때** v098 자동 manifest → v096/v091/v093 → 원래 v094 adaptive 엔진의 실행 함수 위임·캐시 identity/파일 불변. [focused 219 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41764255684) | 기존 설치 시즌 근거 범위; **새 시즌 전체 인증/실 Native DPS E2E 아님** |
| **[P3-DE](development/notes/2026-11-04_p3-de-new-season-source-swap.md)** | v169의 gear/tier/budget/settings **동적 시즌 교체**, v139 구 시즌 Diamond/Omnium 제약을 source-only에서 분리, v098 기존 26 DPS 대표 프로필 공급에 같은 Build/ilvl 숫자 미리보기 적용. **최종 코드 SHA 58d1cc8fb81f9b25f61931c472e71d3f0d5ba1b9**, [focused 222 PASS/0 FAIL·DEV_LEDGER_PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41767573431) | **교체된 gear/tier raw SHA를 v216/v223 원본 영수증에 귀속하지 못함**. 같은 build 표지만으로 새 시즌 Native manifest 생성 금지, **preview만 허용**. 기존 P3-DD와 혼동 금지 |
| 기존 원본/실 Native | [물리 Flask·SimC ID](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41661212083), [F/O Native A](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666305288) / [B](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666925906): 총 Native6, [gem Native4/4](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696), [원본 무기 mask Wago](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41732744145) | 동일 시즌·같은 빌드/프로필/손·아이템에서 관측한 범위만. 새 시즌 전체 최고 품질/소켓/무기 최소 ilvl/26 DPS 자동 인증 아님 |

**독립 Actions 대조**: P3-DE tested SHA 58d1cc8의 focused 로그에서 Ran 222 tests / OK / DEV_LEDGER_PASS 확인. v098, v172, v177, v180 **offline**, v187, API, UI(Ubuntu/Windows), Windows(3.12/3.14) 모두 SUCCESS; v180의 Native job **SKIPPED**. 테스트된 SHA → 인계 전 8454adc HEAD 사이는 CURRENT·개발자 노트·INDEX·P3-DE 노트 **4개 문서만** 변경. 이 인계 중 **신규 CI·Native·게임 HTTP 호출 0**. 기존 보석 원본 +16/+7와 특정 Native +16/+8의 1점 차이는 사용자 지시대로 심층 연구 후순위; buffed rating을 정적 G/B/O로 역산하지 않는다.

## 4. 병목을 분리한 작업 로드맵
**즉시 단기 (CONNECT 우선)**:
1. 기존 v216/v217/v274 원본·raw SHA와 P3-DE gear/tier/budget/settings bundle을 **실제 동일 소스/빌드·목표 ilvl 기반으로 자동 구성·연결**. v223 기존 검사·봉인 영수증 재사용. 더 많은 Gate를 만들지 말고 **현재 왜 source-only인지** 실제 파일/함수/영수증으로 특정한다.
2. **Evidence EXTEND는 정말 부족한 항목만**: 실제 대표 장비·티어/시즌 G 또는 같은 시즌 참조, v271 가변 소켓·물리 보석 J·최고품질/영약 F, 기름 무기 손/최소 ilvl O, L/E 소유권. 사용자와 먼저 논의 후 게임 사실 연구·Native 허용 범위 정한다. 선택적 미확정 항목은 그 항목만 보류.
3. 승인된 기본 환경과 선택지만 Policy A에 자동 등록 → v222 B/T·v098 대표 프로필·이미 존재하는 P3-DD manifest→v096→v094 단일 사용 경로 **CONNECT**.
4. 완결된 대표 시나리오 1건부터 실제 Native SimC JSON2 정적 rating+DPS·SEM·95%·실질 대안·캐시/취소·재개 확인; 기존 실측/다전문화 Actions·캐시 재사용 후 필요한 경우에만 점진 확장.

**장기**: 위 **같은 Environment Build 엔진**을 과거 소스/캐시 없는 새 설치 통제 환경에서 실제 정상 Wago/Blizzard/SimC 등 수집을 허용하여 새 시즌 G/J/F/O→B/T→선택지→26 DPS 공통 대표 프로필→적응형 최적화까지 시험. 별도 SimC-only 엔진·전수 26×ilvl Native·효과 재구현·시즌 전체 장비 DB는 불필요. 원본 v016 독립 확보 및 실제 Windows 사용자 경로/배포는 필요한 지점에서 증분 연결.

**개발 작업 기준**: 항상 INDEX capability/한영 키워드→연관 note·실제 코드/원본/Actions/Native 선조회. 증거 부족과 제품 미연결을 따로 판정하고 REUSE/CONNECT/EXTEND/NEW/STOP 기록. 독립 작업 묶기, 통과한 동일 기준의 검증 재사용, 중복 HTTP/Native·캐시 무효화·메모리/I/O·전체 시간 점검. 미세 1점 현상/SimC 효과 자체 연구 반복 금지.

## 5. 새 채팅 읽기 순서 / 권한
1. **실제 GitHub 격리 branch/main HEAD 각자 독립 재조회**.
2. **본 P3-DF 단일 인계** → [PROTOCOL](development/PROTOCOL.md) → [INDEX](development/INDEX.md) relevant capability → [P3-DE](development/notes/2026-11-04_p3-de-new-season-source-swap.md) → [P3-DD](development/notes/2026-11-04_p3-dd-admitted-season-v096-native-entry.md), 필요 시 P3-DA/CV.
3. [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) + [개발자 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md) + [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md).
4. 관련 코드 v216/v217/v222/v223/v169/v139/v098/v096/v094/v271/v278/v281/v286와 실제 원본·Actions·Native 영수증을 **해당 SHA/범위에 한해** 재확인한다.
5. **첫 응답은 복원 결과·두 HEAD·핵심 실제 증거·완료/미완료(증거 부족 vs 연결 미완료)·병목·효율 대안·장단기 로드맵·권한 경계를 보고한 뒤 STOP. 사용자 “진행” 전 수정/커밋/수집/Actions/CI/Native/테스트/공식 승격 금지.** 문서 커밋은 Project UI/Main/Work OS 승격이 아니다.

## 6. 새 채팅용 복사 시작 프롬프트
~~~text
SIMC SECONDARY OPTIMIZER를 읽기 전용으로 복원해.

GitHub 저장소 degong2-code/simc-secondary-optimizer-runner, branch probe/chat-cache-v035-20261024. 실제 격리 브랜치와 main의 HEAD를 각각 독립 조회하고, docs/CHAT_CONTINUITY_HANDOFF_20261104_P3_DF_ENGINE_RESTORE.md → docs/development/PROTOCOL.md → docs/development/INDEX.md → P3-DE/P3-DD 최신 노트 → CURRENT → 개발자 실행 노트 → 승인 v1.4.3 → 관련 실제 코드/원본/Actions/Native 영수증을 읽어. 이전 P3-CV 인계는 역사 자료.

최종 목표는 **개별 기능의 반복 개발이 아닌, 26 DPS(증강·탱커·힐러 제외)를 위한 재사용 가능한 단일 엔진 완성**이다. 동일한 정상 시즌 G/J/F/O 전체 자동 구축 → B=G+J+F, T=B+O(수동 최종 T 우선·L/E/O 중복 방지) → 검증된 최고품질 옵션 자동 등록 → 사용자 선택에서 대표 장비·무기·티어4·SimC 프로필 내부 생성 → 기존 v094 adaptive DPS/SEM·95%·근접 대안·캐시·취소/재개까지 연결한다. 장비 추천·전수 시즌 장비 DB·SimC 효과/APL 재구현·새 최적화 엔진 금지.

P3-DD는 기존 같은 시즌 승인 영수증의 v098 자동 manifest→v096→v094 위임(219 PASS), P3-DE는 교체형 4문서 시즌 소스→v169/v139/v098 26 DPS 프로필 미리보기(222 PASS)다. P3-DE는 신규 시즌 bundle의 raw gear/tier SHA를 v216/v223 원본 영수증에 연결하지 못해 Native manifest 차단 중이므로, 신규 시즌 READY·Policy A·26 DPS Native E2E로 승격하지 마라. 기존 gem Native4, F/O Native6, Wago 무기 마스크·캐시를 조건/빌드별로 재사용하고 buffed rating을 정적 예산으로 역산하지 마라. 사용자 요청상 1 rating 심층 연구는 후순위.

매 작업 전에 INDEX/연관 기록/실제 원본·코드·영수증을 선조회하고 Evidence와 Integration을 분리, REUSE/CONNECT/EXTEND/NEW/STOP으로 최소 변경을 결정해. 독립 과제 묶기, 이미 완료한 동일 기준 검증 재사용, 중복 Native·HTTP·Actions·메모리/I/O·캐시·실행 시간 자가점검. 코드 문제는 자체 해결하고, 게임 데이터 사실 확인·새 자료 수집·Native 연구가 필요할 때는 먼저 나와 논의해.

**새 채팅 첫 응답은 독립 복원 보고만 하라**: GitHub 실제 두 HEAD, 최신 근거, 제품 목적, 완료·미완료/병목(증거 부족과 연결 미완료를 분리), 더 효율적인 대안, 단·장기 로드맵, 권한/미승격을 먼저 보고하고 멈춰. 내 명시적인 **“진행” 전에는 개발·코드/문서 수정·GitHub 커밋·신규 수집·Actions/Native/테스트 실행·공식 승격을 절대 시작하지 마라.**
~~~
