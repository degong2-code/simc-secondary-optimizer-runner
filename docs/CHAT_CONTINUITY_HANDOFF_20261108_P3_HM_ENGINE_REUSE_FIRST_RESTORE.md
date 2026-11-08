# SIMC SECONDARY OPTIMIZER — P3-HM 새 채팅 단일 인계 (2026-11-08)

**성격:** 격리 GitHub 개발 상태를 읽기 전용으로 복원하기 위한 인계. 승인 설계 변경, main 병합, ChatGPT Project UI/Work OS 공식 적용, v003 immutable 변경 또는 제품 완성 증거가 아니다. P3-GX와 그 이전 인계의 "최신" 문구는 역사 자료.

## 1. 인계 기준과 읽기 순서

- GitHub: degong2-code/simc-secondary-optimizer-runner; 격리 branch: probe/chat-cache-v035-20261024.
- **작성 직전 실제 격리 HEAD:** 4998fb7ccf78ca5339737bf1916b798c2324d491. **main HEAD:** 07133e0aaf738d6e4816a6486057b1cd49c018de. **마지막 기능 코드 커밋:** bf613847ec885db66b7a8fec35019b0ce4a9541b (P3-HL). 이후 테스트-only c8737ce57c6766eb814b9ecb134a59ebcc284418 → a070c892a3d2164a8997f13d586383dfb13a1ce4, 문서-only 4998fb7c. 본 인계 커밋 이후 HEAD는 달라지므로 새 채팅이 격리/main HEAD를 다시 **각각 독립 조회**하고 기능·테스트·문서 SHA를 분리.
- 읽기 순서: **이 P3-HM → docs/development/PROTOCOL.md 상단 → docs/development/INDEX.md E3/E2/E1·A3/A1/A2·B3/B2·C4/C3/C2/C1·D1/D2/D3·F1/F2·G1/G2 관련 행 → docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md 상단 → docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md 상단 → P3-HL/HK/HJ/HI 노트·실제 해당 코드/SHA/Actions·Native**. 역사 전체 재감사 금지, 과거 P3-GX는 필요한 경우에만.
- 권위: 최신 사용자 직접 결정 > 비충돌 승인 [v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)·2026-11-02 정책 > 실제 코드/원본 SHA/Actions/Native > CURRENT·INDEX·인계. 첨부 v1.4.1 문서의 DPS 27개·구 보석 기본6개 고정은 역사. 현재 **26개 DPS만** 지원(증강 기원사·탱커·힐러 제외). 문서 작성이 Project UI에 등록 완료되었다는 뜻이 아님.

## 2. 최종 제품/승인 설계

**목표는 지금 시즌 하나의 PASS가 아니라 다음 시즌에도 동일한 입력 계약과 source·봉인·캐시·SimC 경로로 재사용하는 하나의 환경 자동 구축 + 적응형 SimC DPS 최적화 엔진.** 사용자 목표 ilvl 기본 334 또는 직접 지정한 **최종 T** 기준 치명·가속·특화·유연 **최적 절대 rating**과 DPS, SEM, **95%** 우위 판정, 관측 1위와 확정 여부의 구분, 충분히 다른 근접 대안, 비율·캐시·취소·재개 제공. 전역 최적해 증명은 미확정이면 그대로 표시.

사용자는 직업/전문화/종족/특성, 목표 ilvl/수동 최종 T, 장신구2, 선택 특수장비, 장식0~2, 보석·소모품·기름·전투조건 선택. 대표 일반 장비/무기·티어4/주능력치/SimC 프로필은 내부 자동 생성. 업로드 프로필은 선택적 캐릭터/특성 추출이지 현재 장비 재분배가 아님. 장비 조합·획득 경로·전체 시즌 DB·자체 APL/효과 엔진은 제품 범위 밖.

**B=G+J+F; T=B+O; c_final=c_base+o.** 수동 최종 T가 자동 예산보다 우선, O 고정 비재분배, L은 G 안의 하한, E·L·O 이중 가산 금지. 장신구 정적 G는 자유 G 밖, 장신구 gear 미관측은 0 확정/선택 차단 아님. 제작 50:50 초기 스탯은 L이 아님. 최종 스탯은 SimC `gear_*` 입력으로 중복 없는 최종 rating 반영; 아이템/보석/장식/proc/APL/DPS 효과 해석은 SimC 책임.

**보석 최신 사용자 결정:** 사용자 선언 N소켓은 N개 실제 `gem_id`를 모두 채움. 최소 N=5: **여러 검증 특수보석 중 사용자가 한 종류를 선택해 정확히 1개** + 일반 4종 치명/가속/특화/유연 각 1개. 남는 N-5는 고정 순환. 보석 구성 DPS 최적화/획득 아이템·주문·효과 별도 인증 Gate 금지. J는 **두 가지 양수 2차스탯의 명목 rating을 가진 실제 일반보석의 합계**; 특수보석·단일스탯 보석 제외. 현재 70783 대표 최고품질 일반보석 **각 +16/+7=23**, N=5면 J92, N=7이면 J138; 새로운 시즌 값으로 하드코딩 금지. 보석 개별 Native 측정은 J Gate가 아니며 P3-HE 단일 보석 델타 코드도 기본 제품 경로에서 STOP.

**실제 완료 판정:** 동일 시즌/빌드 `v216` 대표 장비·무기·티어4/G/J/F/O source owner → 기존 `v222` 공식 B/T → `v220/v196` 검증 최고품질 선택지 실제 발행 → `v212/v217` **environment_ready=true·installed=true** 실 영수증 → 사용자 `v098/v096/v094` 실제 DPS 최적화 1건. 오프라인 합성·STAGED·후보 J만으로 READY라고 쓰지 않는다.

## 3. Evidence vs Integration — 이미 확보한 것과 미완료

| 영역 | 재사용 증거·코드 (범위 한정) | 아직 미완료 |
|---|---|---|
| A 원본/봉인 | `v161/v229/v191/v211/v213/v217` 시즌 DB2·SimC SHA/원본/재개 경로. 70783 실제 source-only [#42443197606](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42443197606) SUCCESS/native0. | 다음 시즌 source 생산 자동 완성 아님, 다른 패치 빌드의 콘텐츠 동일성 기반 증분 재봉인 미구현. |
| B 대표 장비/G | `v230/v232/v277/v222`. [실 G/F T1 #42332836316](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42332836316) workflow **FAILURE/NOT_READY**지만 원래 정확한 대표 프로필 G=2850 Native1, F=가속165 Native2 (합 3). | 원래 아이템/프로필과 현재 선택 대표 item identity가 다르면 G2850 자동 재사용 금지. 실 새 READY 없음. |
| C 보석/J | P3-GZ 원래 70783 pinned SimC 로컬 **Native4 exit0**, 실제 특수1+일반4에서 JSON2 `buffed_stats` CHMV **+92** (한 대표 사례). P3-HC source #42443197606의 특수 240967 same-build, gem 링크75, v266 raw 인정0/미해결75. P3-HI/HJ/HK: 기존 `v271` 명목 J → 빌드별 `data/season_ordinary_gem_nominal/12.1.5.70783.json` → `v113/v216` → `v221/v230/v232/v222` J source-owner **오프라인 PASS**. | 실 정상 빌드에서 J 공식 설치·최고품질 선택지 발행 미확정. 다음 시즌 J JSON 자동 발견/생성은 아직 없음. v266 EffectPointsMin 0/75는 J=0이 아님, 새 Native 필수 Gate 아님. |
| D 소모품/O/E | `v281/v278/v269/v285/v286` 기존 F/O/E 및 명시 미사용 O=0. [F-only #42196731158](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42196731158) 물리 영약 241324 F+165 Native2; T1에서도 조건부 F+165. | 다른 시즌/아이템에 F165를 무단 복사 금지. 선택 기름 손/O 증거 조건부, 일반 임시마부·효과 Gate 확대 금지. |
| E 예산/선택/설치 | `v222` B/T, `v220/v196` 정책 A, `v212/v217` 공식 설치 코드는 기존에 존재. P3-HK 기존 J 숫자 owner·품질 불일치·소켓 보류 합성 계약 PASS. P3-HL exact-game-build 설치 캐시 선택과 과거 READY 오인 차단 offline PASS. | **실 70783 공식 G/J/F/O/B/T·published verified choices·environment_ready/installed 모두 미실증**. Source Evidence와 제품 Integration 구분. |
| F 26 DPS | `v139/v143/v098/v096/v094` 대표 사용자 입력/기존 적응형 SimC·캐시·취소·재개·SEM/95%·근접 대안 코드/과거 일부 Native 증거 존재. | **실 READY→한 사용자 DPS E2E 미완료**, 26개 신규 Native 전수 실행은 선행조건 아님. 원본 v015/v016 직접 통합 확인 없이 완료로 표시 금지. |

## 4. 최근 커밋/검증의 정확한 범위

- **P3-HI** 기능 `e1509f5e...`: 4종 per-ID 명목 합계 + 기존 `v216/v271` 연결. **P3-HJ** 기능 `25b99521...`: 70783 ItemID·+16/+7 시즌 원본 파일을 `v113` 정상 Build에서 자동 공급(미등록/다른 빌드 PENDING; 미래 시즌 자동 원본 수집기 완성 아님).
- **P3-HK** 기능 `3d578236...`: 명목 J를 기존 v216 원본 숫자 owner·v230 품질·v232 소켓과 v222 컴포넌트로 연결. [focused #42449427160](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42449427160) **402 tests = 400 PASS/2 SKIP, DEV_LEDGER_PASS**, Native0.
- **P3-HL** 기능 `bf613847...`: 설치 READY 재사용을 **정확한 게임 빌드 + ilvl**로 제한; 빌드 미입력 시 공식 KR Retail version 조회 1회, 입력 빌드면 조회0, 기존 구빌드 정적 캐시 삭제 없음. **패치 빌드가 다르다는 이유만으로 새 시즌이라고 단정하지 않음**. 다른 빌드로 재봉인해 증분 설치하는 기능은 미완료. 이후 테스트-only `c8737ce5`·`a070c892` / 문서-only `4998fb7c` 분리.
- [P3-HL focused #42452438181](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42452438181) **402 tests = 400 PASS/2 SKIP, DEV_LEDGER_PASS**. [v212 #42452438131](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42452438131) Windows/Ubuntu **각 481 tests = 477 PASS/4 SKIP**. [v113 #42452438167](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42452438167) Windows/Ubuntu 각각 **227 PASS**, [v181 #42452438153](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42452438153), [v182 #42452438154](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42452438154) SUCCESS. 문서 HEAD [#42452596302](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42452596302) **400 PASS/2 SKIP·ledger PASS**. 전부 **오프라인**, 실제 신규 Native0·게임 DB 재수집0.
- 기존 G/F T1 #42332836316은 **실 workflow FAILURE/NOT_READY**. 옛 SimC Native ZIP은 정확 원본 프로필·바이너리/경로에 한정한 감사 증거이지 신규 환경의 이식 가능한 실행 캐시가 아님. 새 T1/실 READY 성공이라고 과장하지 않는다.

## 5. 단기 병목·효율 대안·장기 로드맵

**초단기 CONNECT 우선 (실 1건 완주):**
1. INDEX E3/E2/E1·B3/C4/D1/D2/A3에서 원래 봉인 SHA·정확한 현재 대표 장비/프로필·F/G 영수증을 선조회해 **원본 부족 vs 이미 있는 증거의 제품 연결 미완료**를 구분. 기존 정확 증거가 있으면 재수집/Native 반복 금지.
2. 동일 70783 실제 `v216`의 G/J/F/O source-owner → `v222` B/T → `v220/v196` verified choices → `v212/v217` **실 READY/installed** 연결. 명시 O=0은 별도 기름 효과 검증 불필요. G2850은 원본 동일 조건에서만 활용. J raw0/75 재분석, 보석별 Native/효과 인증 Gate 중단.
3. **검증 특수보석 여러 종류의 사용자 선택 옵션**을 `v196/v113`과 실제 대표 프로필에 연결(한 번에 1개, 효과는 SimC). 일반보석 4종·N개 선언 소켓 자동 배치는 기존 v271 재사용.
4. 기존 `v098/v096/v094`로 실제 사용자 DPS 1건, 절대 rating·SEM·95%·관측1위·실질적 근접 대안·캐시/취소·재개를 확인.

**장기:** 26 DPS 실사용으로 확대; 새 시즌 G/J/F/O **자동 수집·source-owner·품질 선택지·설치**에 같은 함수와 데이터 교체 방식 사용. 빌드만 변경됐고 콘텐츠가 같다는 실제 증거가 있을 때 정적 원본을 영향 범위만 증분 재봉인. 기존 통계/적응형 엔진 보존. 전체 시즌 장비 DB·전 전문화/ilvl Native·새 효과 엔진·불필요한 Gate 신규 개발 STOP.

**매 작업 필수:** 기존 INDEX·코드·영수증·캐시 먼저 검색; `REUSE / CONNECT / EXTEND / NEW / STOP` 판정; Evidence와 Integration 분리; 독립 작업은 묶어 처리하고 이전 동일 조건 CI·Native·캐시 사용; 중복 HTTP/Native/Actions·메모리·I/O·실행시간·코드 복잡도 평가. 늘 질문: **"이 변경이 단지 이번 시즌 PASS가 아니라 다음 시즌에도 작동하는 하나의 엔진을 완성하는가?"**

## 6. 반영·미반영·권한

이 인계 준비에서 **격리 GitHub 문서만** 갱신한다. 최신 승인 설계 v1.4.3, main, v003 immutable, Project Sources/Instructions UI 실제 적용, Work OS M0·Shared State, 공식 승격, 이전 주 제품 채팅 소유권은 변경하지 않는다. 원본 v016_SCENARIO_CONTRACT 완전 직접 병합·실 v212 READY·26 DPS 제품 완료는 주장하지 않는다. 새 채팅은 사용자 요청에 따른 인계 읽기만 수행; 추가 개발 권한은 사용자 명시 `진행` 이후.

## 7. 새 채팅 시작 프롬프트

```text
SIMC SECONDARY OPTIMIZER 프로젝트를 읽기 전용으로 독립 복원해.

GitHub: degong2-code/simc-secondary-optimizer-runner
격리 브랜치: probe/chat-cache-v035-20261024
단일 인계: docs/CHAT_CONTINUITY_HANDOFF_20261108_P3_HM_ENGINE_REUSE_FIRST_RESTORE.md

먼저 격리와 main의 실제 HEAD를 각각 독립 조회하고 마지막 제품 기능코드/테스트-only/문서-only 커밋을 구분해. 인계 전 기준 격리 4998fb7ccf78ca5339737bf1916b798c2324d491, main 07133e0aaf738d6e4816a6486057b1cd49c018de, 기능 bf613847ec885db66b7a8fec35019b0ce4a9541b, 테스트 a070c892a3d2164a8997f13d586383dfb13a1ce4; 인계 문서 커밋 후 최신 HEAD는 반드시 다시 확인.

읽는 순서: P3-HM → docs/development/PROTOCOL.md 최신 상단 → docs/development/INDEX.md E3/E2/E1·A3/A1/A2·B3/B2·C4/C3/C2/C1·D1/D2/D3·F1/F2·G1/G2 → docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md 상단 → docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md 상단 → P3-HL/HK/HJ/HI 및 해당 코드·원본 SHA·Actions/Native만. 전체 과거 기록 재감사 금지.

최종 목표는 이번 시즌 단일 기능 PASS가 아니라 다음 시즌에도 재사용 가능한 하나의 환경 G/J/F/O 자동 구축·적응형 SimC DPS 최적화 엔진이야. 26 DPS만, 증강·탱커·힐러 제외. 기본 ilvl334 또는 사용자 수동 최종 T에서 CHMV 절대 rating, DPS/SEM/95%·관측1위·실질적으로 다른 근접 대안·캐시/취소/재개를 제공해. 현재 장비 재분배/장비 추천 아님. 완료는 v216 대표 장비·무기·티어4 및 G/J/F/O 원본 → v222 공식 B/T → v220/v196 검증 선택지 발행 → v212/v217 실 installed/READY → 기존 v098/v096/v094 실 SimC DPS E2E.

보석은 사용자가 여러 특수보석 중 정확히 1개 직접 선택, 일반 치명/가속/특화/유연 각1개 기본, N소켓 전부 실제 gem_id 채움·남는 소켓 고정 순환. J는 일반 두스탯 보석의 명목 합계(현 70783 개당23, N=5 J92)이며 별도 보석 Native 실측은 J Gate가 아니야. 효과/APL/proc/DPS는 SimC. gear_* 최종 CHMV·O/L/E 중복 없음. 다른 시즌 23/F165/G2850 무단 복사 금지.

실 #42332836316은 FAILURE/NOT_READY지만 원래 G2850 Native1/F165 Native2. F-only #42196731158, P3-GZ 실제 보석5 +92 로컬 Native4, source-only #42443197606 보석 링크75/raw0/Native0은 서로 다른 제한된 증거야. P3-HK J 기존 owner 연결은 오프라인 PASS, P3-HL latest #42452438181 400 PASS/2 SKIP, v212 #42452438131 각477 PASS/4 SKIP, v113 #42452438167 각227 PASS, docs #42452596302 400 PASS/2 SKIP. 전체 실 READY/사용자 DPS 미완료. 과거 Native ZIP은 신규 이식 캐시 아님.

매 작업 전 INDEX 기술자산·실 코드·봉인 원본 SHA·Actions/Native·캐시를 먼저 검색해. REUSE/CONNECT/EXTEND/NEW/STOP으로 판단하고 원본 부족과 제품 연결 미완료, Evidence와 Integration을 구분해. 독립 작업은 묶어 진행하고 동일조건 PASS·Native·캐시 재사용, 불필요한 HTTP/Native/CI·메모리/I/O/시간/복잡도를 항상 검토해. 완료된 모든 A~F 기능에도 "다음 시즌에 똑같이 작동하는 하나의 엔진 완성에 기여하는가?"를 최우선으로 적용해.

첫 응답에는 격리/main 실제 HEAD와 마지막 기능/테스트/문서 SHA, 핵심 증거의 정확 적용 범위, Evidence/Integration 완료·미완료, 병목/효율 대안, 간결한 단·장기 로드맵 및 미반영·권한 제한만 보고해. 읽기 전용 독립 복원 보고 후 즉시 STOP. 내가 명시적으로 "진행"이라고 하기 전에는 코드/문서 수정, GitHub commit/push, 신규 수집, CI/Actions/Native/테스트, Project UI/Work OS/공식 승격을 절대 시작하지 마. main/immutable/Project UI/Work OS/기존 주 제품 채팅 소유권 유지.
```
