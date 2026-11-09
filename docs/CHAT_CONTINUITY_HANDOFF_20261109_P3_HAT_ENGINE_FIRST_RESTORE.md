# SIMC SECONDARY OPTIMIZER — P3-HAT 단일 최신 새 채팅 인계 (2026-11-09 KST)

**지위:** 최신 GitHub 격리 HEAD·실 Actions/Native·승인 정책을 독립 대조한 새 채팅 복원 정본. 이전 P3-HAL 및 P3-HAI 상세 A~G, 기능별 원본·과거 영수증은 보존·재사용한다. 아래에는 변경된 최신 판정과 다음 접합점만 기술한다. 이 파일은 공식 Project UI/Work OS 승격 또는 main 반영 증거가 아니다.

## 1. 실제 기준 HEAD와 읽기 순서

- GitHub: degong2-code/simc-secondary-optimizer-runner; 격리 probe/chat-cache-v035-20261024.
- **인계 직전 독립 조회 HEAD:** 격리 85e31cf1e6792c9d66837dcae7ffc2d2166d3a62; main 07133e0aaf738d6e4816a6486057b1cd49c018de. 이 문서 커밋으로 격리 HEAD는 변하므로 **새 채팅은 두 ref를 각각 독립 재조회**. 마지막 UI 실행 code HEAD 0dbfdae0e4fc56074bc15f432e79ca5d1a9b4faf부터 인계 직전 HEAD까지 GitHub compare상 3 commits/4 documentation files only.
- **복원 순서:** ① 격리/main 실제 HEAD·diff → ② **본 P3-HAT** → ③ [P3-HAI A~G 기존 상세](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md)의 P3-HAT 보충 및 역사 표 → ④ [PROTOCOL](development/PROTOCOL.md) 상단, [INDEX](development/INDEX.md) A~G, [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 상단 → ⑤ [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md), [실행 개발자 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md)·최신 사용자 직접 결정 → ⑥ [P3-HAR](development/notes/2026-11-09_p3-har-user-manual-t-real-native-probe.md), [P3-HAS](development/notes/2026-11-09_p3-has-current-season-oil-zero-ui-default.md), [P3-HAO](development/notes/2026-11-09_p3-hao-p1-value-first-verification-economy.md), [P2-OPT](development/notes/2026-11-09_p2-opt-reliability-first-open-search-policy.md), 관련 코드·Actions/Native 원본만.
- **정책 우선권:** 최신 사용자 직접 결정 > 승인 설계 > 실제 코드·CURRENT·Actions·Native > 과거 인계. 이전 업로드 v1.4.1의 27 DPS/증강 포함은 최신 설계와 충돌하는 역사 오기. 최신 **26 DPS, 증강 기원사·탱커·힐러 제외**. v1.4.3 안의 11월 2일 개발 진행 설명도 당시 스냅샷이며 최신 코드 상태는 아니다. 옛 HAI/HAL의 HTTP422·웹 Native0는 **해당 날짜의 과거 장애**다.

## 2. 엔진 최종 목표와 변경 금지 계약

목표는 개별 도구를 만드는 일이 아니라 **26 DPS에서 재사용 가능한 시즌 환경 원본→대표 프로필→SimC DPS 기반 CHMV 절대 rating 탐색→95% 한정 결과·의미 있는 근접 대안→캐시·취소/재개·웹 UI의 하나의 엔진 완성**. 사용자는 기본 목표 ilvl334 또는 기름 포함 수동 최종 CHMV T와 직업·전문화·종족·특성·장신구2·특수장비·장식 최대2·검증 소모품/기름·전투조건을 고른다. 일반 장비/무기/티어4/주능력치는 내부 대표 장비로 구성. 현재 장비 총량 재분배·장비 파밍/조합 추천·전수 시즌 장비 DB는 제품 밖이다.

**B=G+J+F, T=B+O, c_final=c_base+o**. 수동 최종 T가 자동 총량보다 우선하며 B=T−O. 기름 O는 무기에만 고정 1회 반영; 선택 특수장비 L과 정적 영구마부 E는 예산 내 고정 하한·중복금지; 장신구 정적 스탯은 자유 G 밖. 제작 초기 50:50을 L로 잠그지 않는다. 모든 최종 개별 rating은 T/2보다 엄격히 작아야 한다. 승인된 기본 일반보석 4종+특수보석 1개, 최고품질 동등효과 선택지·검증 자동등록 정책 A 유지. 효과/proc/APL/DPS 계산은 SimC에 위임, 자체 효과 인증 Gate/메커니즘 재구현 금지. 통계 표시는 **95%만**, 관측 1순위·통계 우위 미확정·전역최적 미증명을 구분한다.

## 3. 기능 A~G 최신 실증 범위 (P3-HAI 역사 표에 대한 상위 보충)

| 기능 | 이미 구현·검증/재사용할 것 | 아직 불확실·미완료 |
|---|---|---|
| **A 환경 G/J/F/O·B/T** | 기존 v161/v191/v211/v213→v216/v222/v212/v217 엔진. [실 #42460255527](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42460255527) 및 HAR: KR 12.1.5.70783 Ret334, **G2850 J92 F165 O0 B=T3107**, 설치 READY, 환경 Native3 | 모든 미래 시즌 최초 원본 자동 수급/선택지 발행의 전주기 실증 |
| **B 대표 장비/26 DPS** | [#40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357) 26/26 기본 물리 SimC 수용, 일부 다전문화·ilvl Native | 26/26 웹 적응형 장기 DPS 탐색 성공 아님 |
| **C 보석·소모품·O/L/E** | 현재 J92/F165/O0 한정; P3-HAP 음식/물약/증강 토큰 전달 오프라인, [P3-HAS](development/notes/2026-11-09_p3-has-current-season-oil-zero-ui-default.md) 신규 웹 기름 OFF·기존 세션 선택 복원·미검증 O 명시 차단 | **O>0 정확 ID/손·무기/정적 O→v096/v098 프로필/예산**, 선택 특수장비 L·정적 E·일부 시즌 모듈 실 사용자 연결 |
| **D 웹·수동 T·DPS** | [실 #42552942329](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42552942329) **SUCCESS**: 원본 T3107/O0 유지, 사용자 **B=T3500**, Ret334 치834·가998·특834·유834, **171497.55 DPS, SEM641.55**, **DPS Native2**, 실제 FastAPI prepare/run/resume/cache-only/result PASS. 다른 신규 바이너리 SHA 캐시로 분리 | 2회 DPS가 최적 후보 탐색 품질·전역최적의 증명은 아님; 다른 옵션/전문화/실 사용자 Windows PC E2E 미증명 |
| **E 탐색 정책/실행** | v290/v291, [실 #42501052586](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42501052586) **8×35 scout+2×320 confirm, Native10**, 한정 95% 확인쌍 | 2000회는 상한, 전역 수렴/다봉형 공간 누락/선택편향 보정/탐색 품질 우월성 미증명 |
| **F 재개·캐시** | v291/v292 cross-job [#42504040076](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42504040076) 이전 DPS10건 재인증·신규 DPS0; v113 복원 P3-HAN 오프라인 | 다른 바이너리/프로필/무조건 다른 시즌에 DPS 캐시 이식 가능 아님 |
| **G 웹 UI** | FastAPI 일부 실 Native, [web #42560987527](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42560987527) **Linux·Windows 각247 PASS**, [focused #42560987504](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42560987504) **491개 실행=489 PASS+2 SKIP**, [UI #42560987522](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42560987522) 양 OS PASS. UI 신규 Native0 | GitHub Linux FastAPI+subprocess 성공 ≠ 사람의 Windows PC에서 실제 브라우저 클릭·배포 실증 |

**엄격한 증거 분리:** HAR 웹 DPS Native2와 환경 G/F Native3은 별도. HAR 실제 binary SHA = 6b83e4d5d2216faf91511fb00ae712cdf4cc0224b0c83107e8c9c7358c24bfc6; HAR Actions head a1cb60aba91173fa79e26fed9cf5e3c8cf80e41f. UI 검증 head 0dbfdae0e4fc56074bc15f432e79ca5d1a9b4faf. 95% 결과 형식 검증 ≠ 다중선택 편향 보정/전역 최적 보증. UI 오프라인 로그의 예제 DPS는 실 신규 Native 증거가 아니다.

## 4. 병목, 더 효율적인 대안, 단·장기 로드맵

**단기 P1 다음:** 새 환경 엔진이 아닌 **기름 O>0 실제 사용자 선택 접합**. [v281](../runner/v281_consumable_simc_relation.py)·[v278](../runner/v278_sealed_simc_consumable_native_pair.py)·[v286](../runner/v286_representative_oil_source_binding.py) 및 관련 시즌 원본/영수증부터 선조회. 이들은 일부 source-only 후보·물리 적용 범위/Native 측정 부품이며 그 자체로 사용자 항목 자동발행·O>0 실행 완료가 아니다. 정확 아이템ID/SimC 입력/실제 적용 손·무기/정적 O/빌드/회계 소유권을 기존 v216/v222/v212→v098/v096 사용자 실행 경로에 연결. 특히 **v096 fresh 설치 경로는 현재 O0만 명시 수용**. 유효한 항목이 미확정이면 O>0만 보류하고 O0 기본 사용자 경로는 유지. 숫자 추정·효과 인증 Gate·시즌 전체 재조사는 금지. 이후 특수장비 L/영구마부 E/선택 옵션과 실제 Windows 제품 클릭 경로를 증거 부족 범위만 보완.

**중기 P2:** 결과의 **발견 충분성·신뢰성·누락 위험**이 1순위. [P2-OPT 승인 운영 노트](development/notes/2026-11-09_p2-opt-reliability-first-open-search-policy.md)대로 v290/v291·v094/HAE 실증과 캐시를 재사용하여 전역 탐색 다양성/이격 봉우리/실질 대안/확인·95% 선택편향/중단 적절성을 평가. CPU-second당 유용 후보, 호출 횟수, SEM은 보조 자원·정밀도 지표, 품질 확정 근거가 아니다. 스탯 변화 10·L1 50/100/200·전역→국소 등은 *예시*이지 고정 알고리즘·종료 기준 아님. 더 나은 데이터 기반 전략으로 적극 교체할 수 있다. 사용자 로컬 CPU마다 시간 다름. 무조건 26 전문화/2,000 Native 반복 금지.

**장기:** 동일 엔진을 26 DPS·미래 시즌으로 확장, 시즌별 검증된 G/J/F/O·대표 장비·정책 A 선택지만 증분 교체. 캐시·취소/재개·95%를 재사용하고, 원본 v016 계보는 바이트·영수증 확인 전 직접 병합 완료라 주장 금지.

**효율:** REUSE→CONNECT가 먼저; 소스·예산·같은 시즌 캐시를 버리지 않는다. 예전 바이너리 바이트 SHA 재현, 만료 ZIP 복원, 같은 G/F Native 반복, 별도 새 최적화 엔진은 P1 완료를 막는 Gate 아님. 반면 원본 신뢰도·예산 정합·실제 바이너리 SHA별 DPS 캐시 분리는 유지. 선택 oil source가 아직 미확정이면 다른 P1 사용자 옵션 연결로 효율적으로 이동한다.

## 5. 증거·지침·권한 관리

- [실 P3-HAR](development/notes/2026-11-09_p3-har-user-manual-t-real-native-probe.md), [O0 P3-HAS](development/notes/2026-11-09_p3-has-current-season-oil-zero-ui-default.md), [P3-HAO 개발 효율 정책](development/notes/2026-11-09_p3-hao-p1-value-first-verification-economy.md), [P2-OPT 신뢰성 정책](development/notes/2026-11-09_p2-opt-reliability-first-open-search-policy.md), [P3-HAT 영수증 대사](development/notes/2026-11-09_p3-hat-handoff-evidence-reconciliation.md).
- 매 작업 전 INDEX 기능 A~G/원본/코드/작업노트/Actions·Native/캐시를 선조회해 **REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP**. 독립 작업 묶음 처리, **동일 완료 검증·기존 영수증 재사용**, 무효화된 부분만 focused/offline→정말 필요한 최소 Native. 구현/오프라인 PASS/실 Native PASS/역사 재사용/미검증/차단/문서 정책만을 구분.
- **신규 Project UI 등록·v1.4.3 정책 승인 본문·main/v003 immutable·원본 v016·Work OS M0/Shared State·MAIN/WORK 소유권을 이 인계로 변경하지 않음**. 과거 P3-HAL/HAI의 작성 당시 PENDING/FAILED는 보존하고 최신 상태로 승격하지 않음.

## 6. 새 채팅 시작 프롬프트 — 그대로 복사

~~~text
SIMC SECONDARY OPTIMIZER 프로젝트를 **읽기 전용으로 독립 복원**하라.

GitHub: degong2-code/simc-secondary-optimizer-runner
격리 브랜치: probe/chat-cache-v035-20261024
**최신 단일 인계:** docs/CHAT_CONTINUITY_HANDOFF_20261109_P3_HAT_ENGINE_FIRST_RESTORE.md

가장 먼저 격리 브랜치와 main의 실제 HEAD를 각각 독립 조회하고, 인계 직전 격리 85e31cf1e6792c9d66837dcae7ffc2d2166d3a62 / main 07133e0aaf738d6e4816a6486057b1cd49c018de와 비교해 그 사이 커밋·diff·Actions를 확인하라.

P3-HAT → PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md의 최신 보충/A~G → development/PROTOCOL.md → development/INDEX.md → CURRENT_PRODUCT_DEVELOPMENT_STATE.md → 승인 v1.4.3/개발자 실행 노트/최신 사용자 직접 결정 → P3-HAR/P3-HAS/P3-HAO/P2-OPT 및 관련 소스·코드·실 Actions/Native만 확인하라. 예전 P3-HAL·HAJ의 웹 HTTP422/Native0은 역사 기록이다.

최종 제품 목적은 개별 기능 축적이 아니라 **26 DPS의 미래 목표 ilvl(기본334) 또는 사용자 최종 CHMV T 기준, SimC DPS를 최대화하는 치명/가속/특화/유연 절대 rating과 DPS/SEM·95%·의미 있는 대안·캐시·취소/재개를 제공하는 다음 시즌에도 재사용 가능한 한 엔진 완성**이다. 각 작업 전 기능 A~G INDEX·기존 원본/코드/개발노트/Actions·Native 영수증·SHA 캐시를 선조회하여 REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP를 고르고, 독립 작업은 묶어 처리하라. 동일 완료 검증 및 확보된 증거를 재사용해 불필요한 개발·대량 Native·원본 재측정·전수 전문화 반복을 방지하라.

실 확인: KR build70783/Ret334 공식 G2850 J92 F165 O0 B=T3107 설치 READY, 사용자 T3500으로 웹→실 SimC DPS Native2 SUCCESS(#42552942329), 834/998/834/834·DPS171497.55·SEM641.55. 새 폼 무기 기름 OFF와 이전 세션 복원, Linux/Windows 각247 회귀 PASS. 미완료: **O>0 정확 아이템/손/무기/O→v096/v098 실행 연결, L/E·다른 선택 옵션·26/26 웹 장기 DPS·실 Windows PC 버튼, 미래 시즌 최초 전주기 실증, 최적화 품질/전역최적 보장**. 다음 작업은 v281/v278/v286 등 기존 실증을 재사용해 O>0 적용 가능 범위를 엄밀히 가리는 것. 미검증 O를 0으로 간주하거나 O0 기본 경로를 차단하지 말 것.

SimC가 APL/proc/장비 효과/DPS를 계산하며 별도 효과 인증 Gate를 만들지 않는다. B=G+J+F, T=B+O, 수동 T 우선, O 한 번만 가산, L/E 하한, 각 rating<T/2 및 결과 95% 정책 유지. 역사 SimC 바이너리 동일 SHA 재현/ZIP 복구는 P1 Gate 아님; 새 실행 SHA별 DPS 캐시 분리, 같은 시즌 정적 자료 보존. **P2 우선순위는 탐색 결과 신뢰성과 누락 위험**, CPU-second/호출수/SEM 단독 품질 판정 금지. L1/10·50·100·200 rating/현재 v290 단계는 고정 구현 명령이 아니며 더 나은 방법이 나오면 교체 가능하다.

**첫 응답에서만** 실제 HEAD·최신 정책·실 증거의 적용 범위·완료/미완료·병목/효율 대안·장단기 로드맵을 독립 대조해 보고하고 즉시 STOP. 내가 별도로 **'진행'**이라고 하기 전까지 **코드/문서 수정, 테스트, 수집, Actions/Native 실행, 커밋/병합, Project UI/Work OS/공식 승격을 시작하지 마라**. main·원본 불변·기존 개발 주채팅 소유권을 보존하라.
~~~
