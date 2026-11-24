# SIMC SECONDARY OPTIMIZER — P1 v690.9 첫 사용자 제로베이스 / 필수 J·F 결손 독립 복원 인계

**작성일:** 2026-11-24 KST  
**저장소:** degong2-code/simc-secondary-optimizer-runner  
**격리 개발 브랜치:** probe/chat-cache-v035-20261024  
**인계 당시 HEAD:** cf8e89817508002dd490c3d1412350f0fcc957aa (정적 기준; 새 채팅에서 최신 HEAD 확인)

> 이 문서는 새 채팅의 **첫 응답 READ-ONLY** 기준이다. 개발 재시작·검증 자료 전면 재감사·새 Native 선행 실행 요청이 아니다. 7개 항목 복원 보고 후 **STOP**한다. 사용자가 별도로 `진행`이라고 지시하기 전에는 코드·문서·Actions·Native·공식 상태를 변경하지 않는다.

## 1. 프로젝트 정체성 — 변경 금지

World of Warcraft **26개 DPS 전문화만** 지원한다(증강 기원사·탱커·힐러 제외). 목표는 현재 착용 장비를 재분배하는 것이 아니라, **미래 목표 ilvl(기본 334) 또는 사용자의 수동 최종 CHMV T**에서 SimulationCraft DPS를 최대화하는 **치명·가속·특화·유연의 절대 rating**을 찾는 Windows 제품이다. 비율은 보조 정보이며, DPS·SEM·**95%만** 사용하는 통계 판정·관측 1순위·실질적으로 다른 근접 대안·캐시·중단/재개·저장/재열람을 제공한다. 전역 최적해와 단순 관측 1순위를 혼동하지 않는다.

사용자에게 전체 장비/내부 원본 SimC 프로필/후보 벡터/SHA를 요구하지 않는다. 사용자 입력은 캐릭터(직업·전문화·종족·특성), 목표 ilvl 또는 수동 최종 T, 장신구 2개, 선택 특수장비/장식 0~2, 보석·영약·음식·물약·무기 기름·전투조건 등이다. 프로그램이 대표 일반 장비·무기·티어 4세트와 시즌 원본 예산을 구성한다. 프로필 업로드는 캐릭터·특성 추출 선택 편의 기능이며 현재 장비 총량이 최적화 기준이 아니다.

예산 회계: `G` 대표 장비, `J` 검증된 기본 보석, `F` 최고 품질 영약, `O` 무기 기름 고정치, `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. 수동 최종 T가 자동 총량보다 우선하며, `B=T-O`로 변환한다. L은 G 내부의 정확한 특수장비 하한, E는 승인 회계에 따라 한 번만 반영, O는 자유 재분배·중복 가산 금지. 장신구 정적 stats는 자유 G 밖, gear record 미관측을 0이라고 단정하지 않는다. 새 시즌 G/J/F/O 모두 시즌 원본에서 자동 산출하며 과거 시즌 숫자를 새 시즌 수치로 복사하지 않는다.

Wago DB2는 물리 item ID·품질·사용 조건의 원본, SimC는 입력·APL·proc·효과·DPS의 권위다. 자체 APL/효과 메커니즘/아이템 발동 인증 엔진을 만들지 않는다. 현재 장비 재분배·장비 조합/파밍 추천·시즌 전체 일반 장비 DB·전 품목 Native Gate·새 최적화 엔진·AI 런타임·불필요한 SEM 미세 최적화는 범위 밖이다.

## 2. 처음 읽을 정본 및 최신 사실 우선권

1. `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 맨 위 최신 항목과 실제 HEAD·Actions·Native 영수증
2. `docs/development/notes/2026-11-24_p1_v690_real_first_user_single_zip_zero_history_acceptance.md`
3. `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`
4. `docs/development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md`
5. `docs/development/POLICY_ONE_BUILD_SOURCE_TRUST_GAMER_FIRST_20261123.md`
6. 필요시 `docs/development/notes/2026-11-24_p1_v689_real_installed_food_adaptive_native_dps_once.md`, `2026-11-24_p1_v688_actual_onebuild_optional_user_ui_profile_once.md`와 해당 원본 코드를 좁게 확인
7. 첫 장애에만 `integration_probes/p1_v690_one_zip_first_user_zero_history_once.py`, `runner/v216_environment_build_coordinator.py`, `runner/v113_local_web_api.py`, 해당 J/F/원본 설치 모듈과 영수증을 조사

**최신 사용자 직접 결정 > 최신 승인 설계(26 DPS, 2026-11-02 시즌 G까지 자동 구축 포함) > GitHub 코드/CURRENT/실제 Actions·Native > 과거 인계/역사 문서**. 제공된 과거 v1.4.1 문서의 27개 DPS·증강 지원 등의 문구는 현행 26개 DPS 확정 정책으로 덮어쓴다. 최신 정책 버전의 Project UI 실제 적용 여부는 확인 없이 주장하지 않는다.

## 3. 기존 실제 PASS — 재개발·재측정 STOP

- v567: 동일 시즌 ZERO-SOURCE 환경 자동 구축 역사 실증; 이전 영수증의 대상·시즌·SimC 조건에 한함.
- v611/v629`v633: 실제 70961 G/J/F/O 및 영구 마부 38종. 일반화 증거 아님.
- v570: Windows 실제 Chrome에서 빈 세션→시즌→생존 사냥꾼 Native64 DPS·95% 결과.
- v572/v624/v639 및 관련 v636~638: 중단/복원/재개·장신구·수동/자동 T·캐시·ZIP Native·최적 rating/DPS/SEM/95%·대안·재열람 성공(각 기존 조건 한정).
- v684: 70961 실제 Wago/SimC source-owned food42/potion17 연결 중 시즌 source projection food35/potion1.
- v688 [Actions #45223542078](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45223542078): 실제 같은 실행의 v212 설치 food35/potion1/마부38, 설치 SHA→사용자 API→SimC `food=blooming_feast` 프로필 PASS.
- v689 [Actions #45227006628](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45227006628): 실제 70961 징벌 성기사+Blooming Feast, 기존 Native6/6, CHMV (736,736,735,900), T=3107, 관측 DPS 158317.4831, SEM 247.27365, 95% 우위 방향 미확정, 근접 대안2, 결과 재열람 PASS. 이 사례는 **같은 실행에서의 Native 제품 1시나리오 성공**이며 모든 전문화/다음 시즌/완전 첫 설치 성공 증명이 아니다.
- v690.9 전 단계에서 빈 Windows 사용자 APPDATA·현재 ZIP 286파일·사전 설치 없는 공개 SimC 70961 자동 설치(소스 revision `6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7`)·실제 Chrome·인증정보 저장/삭제·흑마법사/파괴 선택·실제 보이는 무기 기름 **미사용** 선택까지 성공.

## 4. **가장 최신 Windows v690.9의 실제 종료 결과 — 첨부 기록보다 우선**

사용자가 전달한 `LAST-Q&A(7).txt`는 v690.9 전체 Actions를 **실행 중**이라고 기록하지만, 2026-11-24 GitHub를 다시 조회했을 때 아래 실행은 이미 **completed / FAILURE**였다.

- Commit `cf8e89817508002dd490c3d1412350f0fcc957aa`.
- [v690.9 Windows Actions #45237310462](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45237310462) FAIL; 원본 receipt artifact `14849293119` (V690_FIRST_USER_ONE_ZIP_CONTIGUOUS.json, V573...json).
- 같은 HEAD의 78계약 [#45237310371](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45237310371) SUCCESS, reusable focused [#45237310280](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45237310280) SUCCESS.
- 실제 first-blocker: **`HIGHEST_QUALITY_GEM_J_SOURCE_PENDING`**. 함께 `HIGHEST_QUALITY_FLASK_F_SOURCE_PENDING`, 동일 시즌 G/J/F/O B/T 및 v212 설치 PENDING, 추가 소켓/물리 보석 J·영약 F 원본/수치 정합 PENDING 등이 requires로 기록됐다. 실제 내부 stage는 `FRESH_V191_V211_V213_COMPILED_UNADMITTED`.
- 동일 한 실행의 UI 결과: class/spec `warlock/destruction`, oil `off`, 목표 ilvl334, 게임 `12.1.5.70961`. 소모품/예산 원본 설치 **실패**: `environment_ready=false`, `environment_installed=false`, 설치 SHA 없음, `B/T=null`.
- **환경 준비 Native 3회**, 사용자 DPS Native **0회**. 따라서 이 사례에 DPS·SEM·95% 결과 없음. 개인 PC 시험도 아님.
- 이는 제품의 실 제로베이스 환경 구축에서 확인한 **첫 필수 J/F 원본 미충족**이다. v690.6~.8의 Selenium 기름 selector 오류를 여전히 첫 P1 결손으로 다루면 안 된다. 그러나 J/F 결손의 **근본 원인이 반드시 특정 파서·SimC revision에 있다**고 증거 없이 단정하지 말 것.

## 5. 가장 비용이 낮은 다음 작업 단 하나

**P1 첫 사용자 ZERO-HISTORY 시즌 구축의 보석 J 정확한 원본·최고 품질/수치 승인 경계(이후 필수 F) 연결 복구**. 사용자 가치: 새 ZIP 첫 실행 사용자가 시즌 준비 버튼 한 번으로 목표 예산·대표 프로필을 얻고 최적화 시작할 수 있게 한다.

첫 단계는 **읽기 전용 원인 특정**: v690.9 원본 JSON requires 및 `v216` 원본 소유 경로의 J 계산/physical gem/J source stage, 관련 v217/v212 등록 조건을 추적한다. v689의 동일 70961 성공과 v690의 fresh/새 공개 SimC revision 차이를 **source identity·재사용 자산 유무·검증 필드** 단위로 비교해 **정확히 어느 원본 증거가 없는지** 증명한다. F도 필수이므로 J 뒤 최초 F 차단을 같은 경로에서 처리하되, 추측으로 숫자나 이름을 주입하지 않는다.

`진행` 지시 후에는 첫 확인된 실제 제품 단절에만 집중하여 **기존 함수/봉인 소스 REUSE→CONNECT/FIX**. 3종 저비용 선행 UI 테스트가 필요하면 재사용하지만 이미 통과한 오일 UI를 매번 전체 Chrome ZIP으로 증명하지 않는다. **정적/오프라인 관련 검사 먼저**, 실제 원본·Native는 바뀐 첫 실행 경계를 검증할 수 있는 **한 번의 동일 시즌 단일 Build**가 꼭 필요한 때만 실행한다. 기본 필수 J/F가 결여되면 설치를 PASS로 속이지 않고 정확히 보류; 선택형 미해결 품목만 존재하면 필수 기본 환경을 불필요하게 막지 않는다.

다음 수락은 **같은 신규 사용자 세션에서** 현재 ZIP→동의/보안 저장→SimC 자동 확보→26 DPS 중 실제 선택한 전문화/기름→**신규 시즌 G/J/F/O/B/T·v212 설치 SHA**→대표 장비·장신구2→기존 adaptive SimC→실 DPS/SEM·95%·근접 대안/저장·재열람. 이 실행 한 건이 통과해도 **다른 신규 시즌 전수·26개 전문화 전수 PASS**라고 주장하지 않는다. 적절한 범용성 표본 시험은 이후 실제 결손이 드러나는 경우에만 추가한다.

## 6. 최근 검토의 효율성·UX STOP

- **STOP → REUSE → CONNECT/FIX → 필요한 최소 EXTEND → 최후 NEW**. 실제 제품의 첫 필수 결손을 바꾸지 못하는 코드/반복 CI/가짜 추가 PASS는 만들지 않는다.
- 70961 고정 J/F 숫자를 다른 시즌에 복사하거나 과거 v213 ZIP 메타데이터를 실행 시 현재 시즌 예산으로 승인하지 않는다. v690에서 역사 패키징 메타데이터는 ZIP 생성만 허용, 런타임 시작 전에 격리한다. 패키저의 역사 메타데이터 요구는 나중에 실제 배포 장애로 확인될 때 간결하게 제거할 기술 부채다.
- 동일 시즌 정적 item cache는 SimC revision만으로 무효화하지 않는다. DPS cache는 binary SHA/revision·캐릭터·프로필/옵션·환경/후보·O/전투·iterations로 분리. 기존 Native 증거의 조건 외 일반화 금지.
- 개별 음식/장식/장신구 효과를 별도 인증하거나 WoW proc 메커니즘 재구현 금지. 최고 품질만 일반 사용자에게 보이되 **같은 효과·사용 조건·수치 비열등성** 없이 이름·등급으로 추정 금지.
- 일반 화면에는 개발자가 쓰는 `v212/B8/SHA/Native/source-only/receipt`를 표시하지 않는다. 실패는 **문제 → 이번 최적화에 미치는 영향 → 앱이 실제 지원하는 해결 행동**으로 설명, 내부 증거는 고급 진단에 유지.
- 화면을 테스트할 때 숨겨진 미러 체크박스를 누르지 말고 실제 보이는 UI 컨트롤로 실행. v690 오일 case는 저비용 UI 테스트 3건/실 Chrome off 적용 PASS므로 변경 없으면 STOP.
- 사용자 개인 Windows PC v677 실측은 사용자 별도 가능 지시 전까지 보류. CI Windows는 실제 개인 PC·네트워크·OS 권한을 완전히 대표하지 않는다.
- 새 개발마다 외부 원본 HTTP/DB2, Native 후보/총횟수, 캐시 재사용, CPU·I/O·메모리/실행시간, 기존 worker·수락 경로가 실제 소비하는지 확인. 완성된 증거/신규 PASS/재사용한 과거 PASS/미완료를 구분.

## 7. 공식 상태·권한

`15/78 COMPLETE`는 **제품 완료율이 아니라** 관리용 계약 상태. `full_product_e2e=PENDING`, `next_review=B10`: B10은 감사 순서이지 최우선 전체 과제가 아니다. 이 인계를 만들어도 공식 승격 없음.

원본 사용자 보고 제품 기준 `v016_SCENARIO_CONTRACT`를 현재 GitHub 직접 통합했다고 주장하지 말 것. `main`, v003 immutable, 원본 v016, Project Sources/Instructions 실제 UI 반영, Work OS M0/Shared State, 공식 78계약·공식 승격 권한, 기존 주 제품 개발 채팅의 주도권을 사용자 별도 승인 없이 변경하지 않는다. Work OS 미통과를 일반 격리 제품 개발·시험 중단 사유로 삼지 않는다. WEQUIP의 운영 authority/영구 런타임 의존성도 도입하지 않는다.

## 새 채팅 첫 응답: 7가지, 이후 STOP

1. **최신 HEAD/CI/Windows 실제 영수증** — v690.9 (또는 이후 HEAD), 실제 첫 blocker 및 Native 횟수, 과거 v689 PASS와 분리.
2. **최종 제품 목적 및 범위** — 26 DPS, 미래 절대 CHMV, G/J/F/O와 수동 T, SimC·95% 책임, 금지 범위.
3. **재사용해야 할 성공 자산** — 시즌 실구축/마부/옵션 등록/Native64/6·캐시·취소재개·결과 재열람(조건 제한).
4. **일반 사용자의 현재 가능/불가능** — 첫 ZIP·SimC 설치·전문화/기름 선택까지 가능, 새 빈 시즌의 필수 J/F 설치와 최종 DPS까지는 미완.
5. **첫 실제 필수 결손과 증거 한계** — `HIGHEST_QUALITY_GEM_J_SOURCE_PENDING` 및 관련 F, 원본·숫자 무단 복사/추정 금지.
6. **다음 최소 비용 작업 하나** — J/F 원본 stage에서 첫 부족 증거 찾기, 기존 코드·영수증 재사용, 저비용 focused부터, 필요할 때만 단일 Native/Build; STOP 조건.
7. **공식 상태·권한** — 15/78, full_product_e2e, B10, PC 시험 보류, main/immutable/Project UI/Work OS/주 개발 채팅 보호.

**7항목 보고 후 STOP.** 사용자가 다시 `진행`이라고 할 때에만 최신 HEAD를 재확인하고 격리 브랜치에서 첫 제품 결손을 최소 수정. **최종 목표는 연구와 검증 확대가 아니라 '시즌 준비 한 번→절대 rating·DPS·SEM·95%·실질 대안'을 일반 사용자가 받는 것.**
