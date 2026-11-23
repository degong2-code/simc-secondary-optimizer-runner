# SIMC SECONDARY OPTIMIZER — P1 v680 제로베이스 1회 환경 구축·게이머 중심 UX·결과 우선 독립 복원 인계

2026-11-23 KST. 사용자 요청으로 새 채팅 독립 복원을 준비하는 문서. **본 문서만으로 소스/코드·PC 실측·공식 권한을 승격하지 않는다.**

## 0. 새 채팅의 첫 동작과 정본

- Repo: `degong2-code/simc-secondary-optimizer-runner`
- 격리 브랜치: `probe/chat-cache-v035-20261024`
- **본 인계 작성 전 확인 HEAD: `39e78b2ce1258b40c2f9ed41e8441cac344b0aa4` (정적 스냅샷). 반드시 새 채팅에서 다시 조회.**
- 우선 읽을 것:
  1. **이 인계**, `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` **첫 최신 항목**
  2. `docs/development/POLICY_ONE_BUILD_SOURCE_TRUST_GAMER_FIRST_20261123.md` — 최신 사용자 직접 결정
  3. `docs/development/notes/2026-11-23_p1_v680_one_build_source_owned_consumable_wiring.md` — 지금 실 구현 및 미완료
  4. 실제 `runner/v216_environment_build_coordinator.py`, `runner/v280_consumable_item_use_spell_source.py`, `runner/v212_environment_manifest.py`, `runner/v218_v098_profile_stage_adapter.py`, `runner/v113_local_web_api.py`, `runner/webui/app.js`, `tests/test_v680_one_build_optional_consumables.py`
  5. `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `docs/development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md`
  6. 필요 시에만 이전 v677 인계·v676/677/678/679 기록, v639 Windows ZIP 결과, v567/v611/영구마부 원본, Actions/Native 영수증.
- 최상위 해석: **최신 사용자 직접 결정 > 승인 설계 > GitHub 실제 HEAD·CURRENT·코드 > Actions/Native 해당 범위의 실증 > 이전 인계**. GitHub CURRENT는 긴 누적 역사이므로 맨 위의 최신 항목과 해당 코드부터 확인한다.
- 새 채팅 **첫 응답은 READ-ONLY 독립 복원 후 아래 정확한 7항목만 보고하고 STOP**. 새 코딩, 파일/문서 변경, 새 Actions·Native·HTTP/DB2, 공식 상태 승격은 사용자가 `진행`하기 전 금지. 첫 답변을 위해 PC 캡처를 요구하지 않는다.

## 1. 최상위 제품 목적 — 현재 장비 최적화가 아니라 미래 목표 rating

World of Warcraft **DPS 26개 전문화만** 지원(증강 기원사·탱커·힐러 제외). 사용자가 목표 ilvl(기본 334) 또는 수동 최종 CHMV 총량 T를 지정하면, 치명·가속·특화·유연의 **미래 파밍 목표가 될 최적 절대 rating**을 SimulationCraft의 **DPS 최대화**로 찾는 Windows 제품. 목표 rating 절댓값과 비율, 예상 DPS, SEM, **95%만** 사용하는 통계적 우위 여부, 관측 1순위와 실제로 다른 근접 대안, 캐시·취소·재개·저장·재열람을 제공한다. 관측 1순위/95% 확정/전역 최적 증명을 혼동하지 않는다.

일반 사용자 입력: 직업·전문화·종족·특성, 목표 ilvl 또는 수동 최종 T, 장신구 2개, 선택 특수장비, 장식 최대 2개, 보석·영약·음식·물약·기름·영구 마부·전투 조건. 현재 착용 장비 전수/현재 총량/내부 SimC filler·SHA는 필수 입력이 아니다. 선택 SimC 프로필 업로드는 주로 캐릭터·특성 불러오기. 내부 대표 일반 장비·무기 성능·주능력치·시즌 티어4pc·기존 SimC APL을 조합한다.

회계 `G`(대표 일반 비장신구 예산), `J`(기본 보석), `F`(영약), `O`(무기 기름 고정), `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. **사용자 수동 최종 T 우선** → `B=T-O`. 특수장비 고정 L은 G 안에 포함된 하한(재가산 금지), 영구마부 E는 승인 회계에 따라 정확히 한 번, O는 비자유분배이며 JSON2나 결과에 중복 가산하지 않는다. 장신구 정적 스탯은 자유 G 밖이고 gear record 미관측은 0이 아니다. 제작장비 초기 50:50은 고정 L이 아니다. **새 시즌에서는 G/J/F/O 모두 새 시즌 원본·빌드 기반으로 자동 결정**, 과거 79×2/70961 수치를 새 시즌 확정값으로 복사하지 않는다.

SimC가 APL·장신구/장식/소모품 효과·proc·DPS를 계산한다. 우리 코드는 빌드/아이템 ID·ilvl·선택·대표 프로필·예산 정합·SimC 입력·CHMV 후보·95% 판정·캐시/실행 관리만 담당. **범위 밖**: 현재 장비 재분배, 장비 추천·파밍 경로, 전 시즌 일반 장비 DB, 새로운 APL/효과·proc 구현/인증 엔진, 새로운 최적화 알고리즘, 생성형 AI 영구 런타임 의존성, 불필요한 원격 빌드 플랫폼.

## 2. 가장 최근 사용자 결정 — v677 시대 우선순위는 폐기

**2026-11-23 직접 지시: PC에서 테스트할 수 없으므로 개인 PC 실측은 나중으로 미룸.** 이전 v677 인계의 "당장 PC에서 자동 T 클릭"은 **더 이상 다음 1순위 아님**. PC가 다시 가능하다는 사용자 지시가 있을 때만 그 정확한 PC 사례를 재개. 이것은 일반 제품 코딩/오프라인 시험 중단 이유가 아니다.

**환경 구축 엔진 문제는 개별 아이템 증상만 수리하지 않는다.** 다음 확장팩/시즌의 **제로베이스 1회 환경 구축**에서 G/J/F/O, 대표 장비·티어 및 검증된 사용자 선택지가 자동으로 준비되고 **같은 설치 환경 기록에서 UI와 실제 SimC 프로필이 함께 소비되는 것**이 완료 판정이다. 환경 구축이 여러 내부 단계를 실행하더라도 **사용자는 한 번 준비**한다. 선택형 결손은 해당 선택지만 보류, 기본 환경까지 차단하지 않는다.

**Wago DB2의 정확한 게임 아이템/품질·장비 정적 원본과 SimC의 입력/효과/APL/DPS를 신뢰한다.** Wago/SimC 원본 획득 이후 똑같은 근거를 별개 Native/효과 인증 Gate로 되풀이하지 않는다. 유지할 최소 정합은 대상 시즌/빌드·ItemID·슬롯/사용 조건·SimC 지원 입력의 실제 연결, 품질 그룹의 동일 효과·동일 조건 및 상위 품질 비열등성, G/J/F/O/L/E 중복 방지, 실제 실행 프로필·캐시 identity. 이름에서 SimC 입력 토큰을 **추측**하거나 품질 번호만으로 동일 효과/비열등을 **가정**하지 않는다. 오류는 SimC 원문으로 보존. 실 데이터가 부족하면 **원래 수집/연결 엔진의 시즌 범용 규칙**을 수정하며 계절별 하드코딩 금지.

**게이머 중심 UI**: G/J/F/O, B8, v212, SHA, Native, receipt, source-only, `SimC disabled`, 정책 A 같은 내부 용어는 기본 화면에서 치우고 필요 시 펼침 '고급 진단'으로 이동. 일반 화면은 **문제가 무엇인가 → 실제 DPS 계산에 어떤 영향이 있는가 → 사용자가 쉽게 할 수 있는 조치가 무엇인가**를 자연스러운 한국어 게임 용어로 설명. 자동 복구 가능한 문제는 프로그램에서 처리. 수동 해결 가능한 문제만 사용자에게 맡김(실제 존재하는 아이템 번호 입력, SimC 업데이트, 네트워크 재시도 등). 없는 버튼을 만들지 않음. 이미 겪은 경계 설명의 과도한 패널/기술 코드·설치본 SHA 비교를 일반 사용자에게 노출하지 않는다.

## 3. 최신 실제 구현 v680 — 구조 연결은 완료, 시즌 전체 자동 등록은 미확인

**문제의 근본:** v216이 Wago/SimC 음식·물약 원본을 수집하면서 v212 설치 환경 원장과 v113 선택지·v218 프로필 입력은 독립 `source_default → disabled`만 사용. v679은 실제 미사용을 설명했을 뿐 원인 해결이 아니었음.

**v680 코드에서 구현한 연결(신규 시즌 원본 전용):**
- 기존 v280 Wago ItemXItemEffect/ItemEffect의 ItemID→사용 주문을 재사용, 같은 시즌·빌드 SimC v189 핸들러/minimum_game_version과 v230 item data(분류/품질)와 결합.
- v217 캐시 가능한 경량 projection으로 중복 대형 파일 파싱·해시·추가 소스 조회 방지.
- v212 새 환경 매니페스트에 **source-owned optional consumable menu**와 미지원 상태를 함께 저장. **기존 설치 매니페스트를 사후 수정하지 않음.** v113 /season-option-catalog 및 기존 installed-budget 조회, 웹 사용자 선택/세션 복원, v218→v098 실제 SimC 토큰 검증 경로에서 같은 **정확한 설치 SHA** 사용.
- 최고 품질 후보는 소스 효과/조건별로 묶고 동률/토큰 충돌 같은 모호성은 선택형 항목만 제외. **품질 상위 순위가 효과 수치상 비열등하다는 실 시즌 증명까지는 아님.**
- 음식·물약을 선택하지 않은 BASE(`source_default`/disabled)는 **추가 디스크 조회 없이** 기존 실행. 선택형 문제로 BASE 차단 금지.
- 주요 실 코드: `runner/v216_environment_build_coordinator.py`, `runner/v280_consumable_item_use_spell_source.py`, `runner/v212_environment_manifest.py`, `runner/v218_v098_profile_stage_adapter.py`, `runner/v113_local_web_api.py`, `runner/webui/app.js`, `tests/test_v680_one_build_optional_consumables.py`.

**절대 혼동 금지:** 테스트의 Wago/SimC source join은 **합성 소스/오프라인 검증**. 새로운 시즌의 **실제** Wago 효과 ID↔SimC consumable parser/토큰 연결과 실제 자동 등록된 음식·물약 개수/품질 비열등성, 신규 SimC Native 사용, 모든 26 전문화/개인 PC 자동 T+DPS E2E는 **미증명**. 아직 전체 음식·물약 및 증강룬·마부·기름 선택지 자동 완료 아님.

## 4. 검증·배포 영수증 — 최신과 역사 분리

- 최신 v680 **제품 코드 HEAD `f48a283dd18e734e16d089eba35948eb30a23f84`**. 이후 인계 전 최신 GitHub HEAD `39e78b2ce1258b40c2f9ed41e8441cac344b0aa4`까지 **문서만** 변경됨(커밋 비교 확인). 새 채팅은 항상 HEAD 재조회.
- [API #45152990800](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45152990800) Windows Python3.14/Ubuntu Python3.12 각 **540 tests OK, 1 SKIP, 0 FAIL**.
- [Windows ZIP #45152990735](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45152990735) Windows3.12/3.14 각 **389 PASS, 0 FAIL**, 패키징5 PASS, 실제 ZIP 추출·CMD·localhost HTTP 3계획·세션 복원 **Native0**. [wrapper artifact #14808020590](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45152990735/artifacts/14808020590) (outer artifact digest `sha256:8892803c6c917b3e88933f1a6ced27a1f88128d5b6793eb466ffb3e5fe3400db`; **내부 제품 ZIP 해시가 아님**).
- [v212 설치 계약 #45152990885](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45152990885), [UI #45152990775](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45152990775), [focused #45152990813](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45152990813) SUCCESS.
- v680 새 개인 PC 시험0·DPS/G/F Native0·외부 Wago/DB2 재수집0. **Actions PASS=관련 코드/환경 연결 계약 검증이지 현재 시즌 실 소모품 등록 또는 실제 DPS E2E PASS 아님.**
- **재사용 역사 성과:** v567 실제 ZERO-SOURCE 시즌 구축, v611 70961/334 정확 조건 예산 G2850/J92/F165/O0/T3107, 영구 마부 38/38(v629~v633), v570 Windows Chrome Native64 실제 결과, v572 ZIP 취소/서버 재시작·재개, v624/v636~638 예산/마부/캐시, **v639** [Windows ZIP Native64 결과](development/notes/2026-11-19_p3-v639_published_zip_70961_final_result_restore.md): 징벌 성기사 ilvl334 관측 CHMV 1098/922/922/165, DPS161718.63, SEM243.11, 95% 우위 미확정, 5개 근접 대안, 저장·재열람 성공. 각 당시 조건 증거로 한정, **무의미한 동일 Native64 반복 금지**.
- 70961 역사 설치 환경, 이전 사용자 수동 SimC 내장 70575, **현재 KR Retail 빌드**를 구분. 최신 KR Retail/기존 SimC 매칭 실측은 미확인.

## 5. 우선순위 — 지금부터 실제 개발할 일

**1순위(PC 없이 가능): v680의 범용 제로베이스 환경 구축 소모품 연결 마무리.**
- 기존 봉인된 **실제 동일 시즌·빌드** Wago/SimC 자료가 있다면 먼저 재사용해 **제로베이스 1회 구축 결과**에 음식/물약 후보가 실제로 나타나고 v212→v113→v218→v098로 전달되는지 *한 사례* 확인. 필요한 실 소스가 없다면 제약을 명시하고 최초 결손 1곳만 최소 비용으로 수집/수정. 새로운 전체 수집·전수 Native부터 하지 않는다.
- 실제 막힐 수 있는 지점: Wago 사용 주문과 SimC 지원 항목 연결(ID), item name에서 만든 token이 실제 SimC parser에 허용되는가, 동일 효과·사용조건·**수치 비열등성**을 이용해 최고 품질만 고르는가. **기존 원본 구조를 이용해 일반 규칙을 완성**하고 품목별 인증 Gate/예외 하드코딩 금지.
- **STOP**: 한 번의 새 시즌 구축으로 검증된 최고품질 선택지와 미지원 사유가 설치 원장에 생기고, 그 **같은 설치본**을 UI/SimC가 소비한다는 근거가 확보되면 그 결손 작업 중단. 새 실세계 등록 결과가 없으면 “완료”라고 보고하지 않음.

**2순위(PC 없이 가능): 전체 UI의 사용자 언어 전환 및 쉬운 복구 안내.**
- 실제 사용 순서: 시즌 준비→캐릭터/목표/장신구/특수장비·소모품 선택→최적화→결과. 각 상태는 '준비 완료 / 일부 선택지 이용 불가 / 계산 불가'로 이해하게 한다.
- 게임 용어/자연어 우선, 기술·내부 예산은 접힌 고급 정보. **문제·DPS 영향·쉬운 다음 행동 하나**, 자동/수동 해결 분리. 실제 기능 없는 버튼·사용자에게 SHA/원본 프로필 전달 요구 금지. v678 진단은 개발 내부 정보로 유지. UI 디자인 v653/v673~v675 보존, 이전에 수정된 아이콘·줄바꿈·장식/소모품 배치 회귀 금지.
- **STOP**: 처음 사용하는 WoW 게이머가 막힌 이유/할 수 있는 행동을 이해하며 기본 계산과 선택형 보류가 분리되면 종료. 고급 진단 패널을 새로 쌓지 않는다.

**3순위(PC 가용성 회복 후): 사용자 실 PC 흐름의 첫 미확인 연결만 확인.**
- v676에서 사용자 PC `검증 환경 1` 선택 성공. v677 자동 T 준비는 개인 PC 미검증. **지금 다시 버튼 누르라고 요청하지 말 것.** 사용자가 PC 가능하다고 밝히면 현재 HEAD와 새 ZIP로 예산·준비 1회 확인, 그 다음 정확 장신구 2개·대표 장비/4티어→기존 적응형 SimC→CHMV/DPS/SEM/95%/대안·저장·재열람 연결. 이미 v639 성공한 Native64를 새 버전마다 반복하지 않는다.

**후속 선택 범위:** 기름 ON의 실제 무기별 O·고정 rating 적용, 선택 특수장비/장식 B8 정적 L/SimC 프로필, 실제 일부 후보 10개 제한/수동 정확 ID 경로, 검증된 음식·물약/영약 선택 및 DPS 적용, 공식 아이콘/Windows 설치·저장 UX. **모두 환경 구축 엔진 원인인지 판단 후 원인이라면 범용 Build로 수정**. O0·선택 특수/장식 OFF는 정상 BASE. 증강룬, 시즌 특수 모듈(옴니움 장서), 원격 SimC 빌더는 *현재 필요한 실제 막힘이 될 때만* 확대. 공식 Nightly·기존 관리본·공개 자체빌드 캐시를 우선 재사용.

## 6. 제거해야 할 비생산적인 작업

- 과거 v669~v675처럼 **서로 다른 F/J 설치본 간 완전 동등성 비교·새 영수증 차이·새 승인 Gate**를 필수 제품 조건으로 계속 개발하지 않는다. 필요한 것은 **사용할 한 설치본**의 시즌/입력 정합성. v676 독립 선택 및 v677 exact SHA 재사용 경로를 보존한다.
- 품목별 SimC 효과를 우리 코드로 재구현·재증명하지 않는다. 원본/효과 수집을 이미 했는데 **다음 등록 Gate를 새로 만들어** UI와의 연결을 늦추지 않는다.
- 현 설치 원본·Native·정적 캐시·DPS 캐시·취소/재개·95% 엔진을 재작성·전면 재감사하지 않는다.
- 시즌 전체 장비 DB, 레시피/파밍 경로/장비 세트 추천, 전 전문화 Native 일괄 반복, SEM 오차 0 추적, 새로운 최적화기, 독립 AI·WEQUIP runtime, 기본 P1 선행 원격 빌더, 정적 아이템 캐시의 단순 SimC revision 무효화 금지.
- 코드를 바꿀 때마다 **STOP→REUSE→CONNECT/FIX→최소 EXTEND→정말 필요할 때만 NEW**. CPU·I/O·메모리·새 Native·HTTP/DB2·Actions 호출·캐시 영향을 고려. 실사용 결과를 바꾸는 첫 결손 외 작업이 계속되면 STOP.

## 7. 공식 상태·권한 및 첫 답변의 정확한 형태

- 공식 원래 상태 `15/78 COMPLETE`는 **제품 구현률 아님**. `full_product_e2e=PENDING`, `next_review=B10`. 공식 Work OS M0 미통과는 일반 개발·기존 사용자 승인 시험 중단 Gate 아님.
- 원본 사용자 보고 제품 기준 `v016_SCENARIO_CONTRACT`와 격리 v680 제품 작업 구분. 원본 바이트·영수증 독립 확인 전 직접 통합 완료 주장 금지.
- 사용자 별도 승인 없이 GitHub **main 병합**, v003 immutable 수정, Project Sources/Instructions 실제 적용 완료 주장, Work OS M0·Shared State·78계약 공식 승격, 주 제품 개발 채팅 권한 이전, 외부 서버/WEQUIP 운영 권한 신설 금지. 기존 격리 브랜치의 개발은 `진행` 뒤 허용. 새 채팅 복원 요청 자체가 기존 주 제품 채팅을 강제로 이전시키는 것은 아님.
- 새 채팅의 첫 답변은 다음 **정확한 7개 항목**으로, 최신 GitHub HEAD·CURRENT·실제 코드/Actions·Native·Windows ZIP 영수증을 읽기 전용 확인한 뒤 기술한다:
  1. 최신 GitHub HEAD·제품 코드·v680 구현·Actions/Windows ZIP의 PASS/FAIL/SKIP·증거 경계.
  2. 제품 최종 목적(26 DPS, 미래 목표 CHMV 절대 rating, SimC DPS·95%·G/J/F/O, 범위 제외).
  3. 재사용할 성공 자산(v567/v611/마부38/v570/v572/v639·적응형 SimC·캐시).
  4. 최신 설계 교훈(제로베이스 1회/소스 신뢰/등록 단절 해결/과잉 인증·설치본 동등성 중단).
  5. v680 구현된 부분과 여전히 미해결인 실 시즌 parser·품질·선택지·UX, PC 시험 보류 상태.
  6. **PC 없이 수행 가능한 단 하나의 다음 최우선 작업**: 기존 실 시즌 소스로 v680 한 번 구축→UI/SimC 전달의 실제 첫 미완료 단절만 최소 수정. 비용/STOP 기준.
  7. 공식 상태 및 main/immutable/Project UI/Work OS/기존 주 개발 소유권 제약.
- **첫 응답은 반드시 READ-ONLY 보고 후 STOP.** 사용자가 `진행`하기 전에는 code/docs/Actions/Native/HTTP/DB2/공식 상태를 수정하지 않는다.

**최종 기준: 최신 시즌 환경을 사용자에게 한 번 준비시키면 최적 rating·DPS를 얻도록 기존 SimC와 시즌 엔진을 정확히 연결한다. 검증·엔진·UI를 위한 개발 자체가 목적이 아니다.**
