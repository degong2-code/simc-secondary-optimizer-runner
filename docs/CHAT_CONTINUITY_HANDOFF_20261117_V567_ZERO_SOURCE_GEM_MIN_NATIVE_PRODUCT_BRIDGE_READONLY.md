# SIMC SECONDARY OPTIMIZER — v567 제로베이스 실제 성공 이후 범용 제품 완성 인계

**기준일:** 2026-11-17 KST. **프로젝트:** `degong2-code/simc-secondary-optimizer-runner`.
**격리 개발 브랜치:** `probe/chat-cache-v035-20261024`.
**인계 자료 작성 직전 HEAD:** `ba50c624013e3c5f24c9ba4e3682c8c7752ccd89` (문서 작업 후 HEAD는 변경됨. 새 채팅은 반드시 최신 HEAD를 재조회).
**실제 코드 시험 기준 SHA:** `2b6135a2c9c810ed62fa6e01bfb162ca38bfbaa6`.
**새 채팅 최초 응답:** 읽기 전용 독립 복원, 아래 7항목 보고, **STOP**. 별도 사용자 `진행` 전에는 소스·문서 수정, GitHub Actions·Native·HTTP/DB2 실행, 공식 상태 승격을 하지 않는다.

> **제품의 유일한 목표:** 새로운 WoW 시즌·확장팩에서도 **제품 런타임 AI/LLM 호출·판단 0회**, 기존 데이터 수집 및 SimC 기반으로 G/J/F/O·목표 대표 프로필을 자동 구축하고, 사용자가 입력한 목표 아이템레벨(현재 기본 334; 시즌별 재산정) 또는 직접 지정한 최종 T에 대해 **26개 DPS 전문화의 치명·가속·특화·유연 최적 관측 절대 rating**을 실제 SimC DPS로 찾아주는 일반 사용자 제품. 장비 조합 추천·현재 장비 재분배·전체 시즌 장비 DB·별도 AI·효과/APL 재구현이 아니다.

## 1. 최신 정본 조회 순서 및 우선권

최신 **사용자 직접 결정 > 승인 설계 문서의 비충돌 정책 > 최신 격리 GitHub 코드·CURRENT·실제 Actions/Native SHA > 이전 인계·과거 영수증**.
1. **실제 최신 HEAD**와 `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 최상단 v567(이전 v550/v554은 역사·원인 기록).
2. **본 문서**와 `docs/USER_APPROVED_GEM_J_POLICY_20261117.md` **마지막 F절(2026-11-17 품질 2축·최소 측정)**. 이전 절의 과거 미완료 표현을 최신 F와 실제 v567로 덮어 읽는다.
3. `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `docs/development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md`.
4. `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md`, `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json` (공식 78개 수락의 원장).
5. `docs/development/INDEX.md`, `FILE_MAP.md`, `EVIDENCE_INDEX.md`에서 **다음 작업의 실제 소비 파일만** 좁혀 읽는다.
6. `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md`. 과거 v1.4.1의 **27 DPS·증강 기원사 포함**은 폐기: 최신 대상은 **26 DPS**, 증강 기원사·탱커·힐러 제외.
7. 구 인계 `docs/CHAT_CONTINUITY_HANDOFF_20261117_V550_GEM_J_PRODUCT_FIRST_READONLY_RESTORE.md`, `docs/development/notes/2026-11-17_p1-v554-zero-source-first-real-blocker-gem-J.md`는 원인·개발 역사로만 참조. 해당 PENDING을 현재 장애라고 주장하지 않는다.

## 2. 반드시 보존할 제품·회계 계약

- 사용자: 직업·전문화·종족·특성, 목표 ilvl 또는 **수동 최종 T 최우선**, 장신구 2개, 선택 특수장비/장식(최대2), 보석·검증된 최고 품질 영약·기름·마부 및 전투조건. **일반 장비 전체를 고르지 않음**. 업로드 SimC 프로필은 캐릭터 정보 보조 입력이며 현재 장비 총량/착용 장비를 기본 목표로 쓰지 않음.
- 내부: 해당 시즌 대표 일반 장비·무기·티어4세트·주능력치/무기 성능·기본 APL·표준 SimC 프로필; 시즌별 검증된 G/J/F/O; 적응형 SimC, 취소·재개·SHA 캐시. **SimC가 효과·proc·APL·DPS를 계산**.
- 공식 수식: `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. 기름 O는 무기·손에 따라 **고정/한 번만** 주입, L(선택 특수장비 정적 고정치)은 G 내 포함하고 스탯별 하한, E(영구 마부)는 승인 회계 안에서 중복 없이 처리. 장신구 고정 스탯은 자유 G 밖; 정적 gear 레코드 미관측을 0이라고 처리하지 않는다. 제작장비 초기 50:50은 L로 잠그지 않음.
- 결과: **관측 1순위**와 **95% 우위 확정 여부**를 구분한 치명/가속/특화/유연 절대 rating, 비율, DPS, SEM/오차, 실질적으로 다른 근접 대안. **전역 최적 증명 주장 금지.**
- 캐시: 동일 시즌 정적 아이템 자료는 **SimC revision만으로 폐기 금지**; DPS 캐시는 실제 binary/revision·캐릭터·프로필·선택 장비/보석/기름/마부·전투조건·rating 후보·iterations identity별 구분. 정상 같은 조건의 재실행에 불필요한 Native 금지.
- 신규 시즌에서 과거 `334/G2850/J92/F165/O0`, 70783 보석 ID 및 `16+7`을 **사전 입력·보장값으로 복사 금지**. 같은 시즌 실측 재사용은 별도. 최고 품질 선택지가 정확 ID/조건/SimC 입력/소유권으로 검증되면 승인된 정책 A에 따라 자동 등록, 불명확한 *선택 옵션만* 보류.

## 3. v567에서 실제로 완성한 보석 경로 — 이 기능을 다시 만들지 말 것

기존 생산자·소비자 그대로 연결:
`v221 Wago ItemID/GemProperty` → `v230 SimC item_data 이름·기본 ilvl·품질·제작 단계` → `v211/v275/v296 정확 스탯 종류·스케일링 ID/계수` → `v269/v278 보석 없는 기준 vs 정확 물리 gem_id 하나만 장착한 SimC JSON2 player CHMV 차이` → `v271 소켓별 실제 J 합산` → 기존 `v216 J/F owner` → `v222 B/T` → `v212 설치` → `v113/v098/v096/v094` 사용자 SimC/95%/캐시.

- **품질 2축:** (1) 이름/아이템 계열로 구별되는 **바깥 등급**, (2) 그 계열 내부 제작품질. 최고 품질은 **최상위 계열의 최고 내부 제작품질**. 바깥 단계가 2개인지 3개인지, 내부가 2개인지 3개인지 코드에 고정하지 않는다. **같은 이름 안에서도 itemlevel이 내부 품질에 따라 다를 수 있음**(실제 v566 첫 제로베이스 FAIL 원인, v567 수정).
- **12개 방향성 조합:** CH/CM/CV, HC/HM/HV, MC/MH/MV, VC/VH/VM. 높은 쪽이 대표 C/H/M/V. **'효과군 수 정확히4여야 SimC 측정' 조건 삭제 완료**. 네 **대표스탯**과 네 **효과 조합**을 혼동하지 않는다.
- **SimC 최소 측정:** 보석 효과가 `gear[]` 정적 수치에 보이지 않아도 `player.collected_data.buffed_stats` 전후 차이에 반영됨. 같은 프로필에서 보석 추가 한 개만 달리하고 실제 SimC로 두 양수 Secondary rating을 판독. 같은 빌드·스케일링 ID·두 스탯 계수·효과 조건이 동일할 때만 **대표 Native 한 번 실측한 큰 값/작은 값을 스탯 방향으로 매핑해 재사용**. 측정한 ItemID와 서명으로 추론한 ItemID, 실제 Native 원본 영수증을 구분. 다른/불충분한 서명은 추가 측정 또는 PENDING. **75개 전수/무조건 24개/항상 2번 측정 같은 숫자 고정 금지.**
- **대표 4종:** 바깥 최상위 계열 및 가장 높은 내부 제작품질을 우선한 뒤, 동일 대표스탯 후보 간 두 rating 합계 내림차순, 실제 ItemID 오름차순. 기본 C/H/M/V 각1, 사용자가 추가 일반 소켓을 선택하면 기존 C→H→M→V 순환, **실제 장착된 모든 일반보석** 반복수만큼 J 전량 계산. 주능력치 포함은 특수 보석으로 별도, 일반 J 제외; 단일 Secondary 보석 미사용. 불명확한 동점 스탯은 임의 대표 분류하지 않는다.
- 복수 아이템에 같은 숫자를 재사용하는 것은 원본 **수치 서명 동등성 기반 재사용**이지 개별 ItemID 전부 Native 실행했다는 뜻이 아니다. 게임 효과 재구현이나 별도 품질 인증 Gate 금지.

## 4. 실제 최신 영수증: 성공과 미완료 범위를 분리

**현재 코드 검증 기준:** `2b6135a2c9c810ed62fa6e01bfb162ca38bfbaa6`. 작성 직전 브랜치 HEAD `ba50c624013e3c5f24c9ba4e3682c8c7752ccd89`는 v567 기록 문서까지 반영. 이 HEAD에서 최신 [v401 계약 Actions #44047349540](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44047349540)은 **CANCELLED(FAIL 아님)**. 직전 동일 계약 [#44046442633](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44046442633)은 **SUCCESS**.

**실 Win64 ZERO-SOURCE→USER SimC:** [Actions #44046442654](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44046442654), status `PASS_REAL_ZERO_SOURCE_TO_USER_DPS_SEM_95_CACHE`. 정상 Wago/SimC 외부 원본은 수집, 역사 packaged 시즌 JSON **12개 격리**, 과거 답/캐시/세션 미주입. 게임 12.1.5.70783, 목표 ilvl334, 시즌 기본 목표 자동 발견. 원본 **12 방향 조합**, 최상위 이름 계열 후보 **24개**, 서로 다른 실제 수치 서명 **2개**, 물리 보석 Native **3회(공유 기준1·대표 240889/240890 각각1)**. 최종 C/H/M/V ID **240906/240890/240898/240914**·각 **16+7**. `G=2850, J=92, F=165, O=0, B=T=3107`. 환경 전체 Native **6회**(보석3 포함), 사용자 DPS Native **6회**, `v212` 설치 SHA `6151f1f84a4dc9df0e70cb7d3f019c687e114857f714a8408e3194bee6f9e4d1`, v113 HTTP API `plan→start→result→cache-only` PASS, 사용자 worker exit0·DPS/SEM/95% 확인·동일 결과 **캐시6 hit/새 Native0**. **여기까지는 완성된 실제 범위**.

- [v212 Windows·Ubuntu #44045370625](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44045370625): 각 **499 PASS/4 SKIP/0 FAIL**. [최신 focused #44046442544](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44046442544): **678 PASS/2 SKIP/0 FAIL**. [78 계약 #44046442633](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44046442633) SUCCESS. 모두 이 범위의 CI 증거; 전 기능/전문/시즌 실 Native PASS가 아님.
- 최초 v566 현장 FAIL: 이름이 같아도 내부 품질별 itemlevel 278/295가 달랐는데 코드가 이것을 위조된 불일치로 취급. **v567에서 tier의 ilvl 범위를 인정하고 재실행 성공**; 실패 원본은 역사로 보존하고 최신 성공을 우선.
- 역사 v524 본 시즌 G/J/F/O 설치, v534 **수동 최종 T3200 + 영구 E 가속30 실제 DPS175397.79 SEM299.40/95%**는 별도 **재사용 가능한 그 조건의 Native**. v567 제로소스 자동 J 숫자의 사전 입력은 아님.
- **명시적 미검증:** 미래의 실제 다른 게임 빌드, 26 DPS 전 전문화의 전체 시즌/장비 선택, 특수보석·추가 소켓 전 범위, 전체 영구 마부·특수 장비 선택 조합, 최종 Windows GUI 설치/업데이트/진짜 최초 사용자 시작 UX. **공식** `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`은 **15/78 COMPLETE**, `full_product_e2e=PENDING` 그대로. **실제 한 범위의 E2E PASS와 공식 전체 E2E PENDING은 모순 아님**.

## 5. 이 인계 후 실제 개발 우선순위

**최우선 다음 작업 하나: M1/M2 실제 Build의 성공 결과가 사용자의 일반 제품 진입점에서 자동으로 준비되어 v113 세션에 전달되는지 검증·최소 연결.** v567 실험에서는 본래 v113 `plan/start/result/cache-only`를 사용했지만, 검증된 환경을 하네스가 `app.state.jobs.remember_verified_fresh_environment(env)`로 미리 등록했다. 따라서 **일반 UI의 최초 실행에서 season discovery→기존 v216 Build·v212 install→세션이 자동 연결되는 소비 경계**는 아직 독립 PASS라고 과장하지 않는다. 기존 `v113` API·`v181/v182` Windows UI/패키지·`v216/v212` 공급자를 우선 확인하고, *부족한 그 연결만* 최소 수정. 새 Build/측정/J 엔진을 만들지 않는다. 확인된 정상 기본 환경까지 선택형 특수 옵션이 막지 않게 한다.

이후 (필수 순서 고정 아님):
- 시즌/목표 ilvl이 달라도 같은 엔진이 동적 원본으로 G/J/F/O를 재산출하는지 실제 필요 범위만 확인. 다른 미래 시즌의 현재 존재하지 않는 데이터를 가정한 전수 Native는 금지.
- M3 사용자 입력·선택 UI/세션·저장/복구·취소/재개·DPS/SEM/95%·근접 대안 소비를 실제 Windows 사용자 관점에서 완성. 사용자 수동 T 최우선, L/E/O 단회 계상 보존.
- M4 검증된 최고 품질 선택지 Policy A 자동 등록, 선택 옵션의 정확 ID·조건/소유권, 특수보석/장식/영구 마부/기름의 필요한 변형만 최소 검증. 미선택 옵션은 기본 정상 실행 차단 금지.
- M5 26 DPS 원본 SimC 기본 프로필/대표 무기/티어, 기존 여러 Native·캐시 재사용, 변화가 실제 무효화한 소비 경계만 추가 검증. M6 UI/설치/캐시/복구를 마무리하고 M7 최종 공식 수락 조건을 증거로 판정.
- **M0~M7과 78 공식 계약은 보존**하되 `next_review=B10` 등의 번호를 이유로 사용자 제품 개발을 중단하거나 무관한 전수 검증을 하지 않는다.

**모든 작업의 의사결정:** 먼저 실제 사용자 UI/세션의 어느 단계에서 이 코드가 소비되는지, 결함/체감 효과, 이미 있는 코드·Native·SHA·캐시, 추가 HTTP/DB2·CPU·RAM·I/O·Native 비용, **최소 수정과 STOP 조건**을 짧게 사용자에게 설명. `STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW`. 그 뒤 격리 브랜치에서 실제로 막힌 첫 경계를 수정하고 focused offline 회귀→필요할 때만 **한 번** 최소 real Native. 기본 결과가 맞으면 STOP; SEM 미세화/전 전문화 반복/새 Gate로 제품을 지연하지 않는다.

## 6. 변경 권한과 검증상의 경계

- 기존 주 제품 개발 채팅의 개발 소유권을 존중하며, 이 인계가 자동으로 MAIN/WORK로 권한 이전을 뜻하지 않는다.
- 사용자의 별도 권한 없이 `main` 병합, `v003 immutable` 수정, 원본 `v016_SCENARIO_CONTRACT` 직접 통합 완료 주장, Project Sources/Instructions UI 적용 주장, 공식 Work OS M0/Shared State 승격, 78 COMPLETE 항목 승격 금지.
- GitHub CURRENT/인계 문서·테스트 PASS는 **개별 범위 증거**이며 사용자 Windows 제품 출시 완료·실제 타 시즌 보장을 의미하지 않는다.
- 같은 시즌 이미 얻은 실제 Native·정적 캐시·캡처/영수증을 재활용. 발견 안 된 숫자/옵션은 PENDING으로 표현, **미관측을 0/역사값으로 대체하지 않는다**. 사용자 요청 없이 과거 감사나 프로젝트 재시작 금지.

## 7. 새 채팅 첫 응답: 읽기 전용 7항목 후 STOP

최신 GitHub HEAD·CURRENT·Actions·유효한 실제 Native/수집·시즌 영수증과 이 문서를 **직접 독립 조회**하고 아래만 보고한다:
1. 최신 브랜치·HEAD와 실제 PASS/FAIL/CANCELLED/SKIP, 어떤 SHA에서 수행됐는지.
2. 현재 일반 사용자가 실제 실행 가능한 구간과 **정확히 누가 최초 Environment Build를 호출/전달하는지**의 미검증 구간.
3. v567 zero-source→user real Native와 과거 v524/v534, 오프라인 회귀의 구분.
4. M0~M7 위치, 공식 78요소 상태(15/78), `full_product_e2e=PENDING`의 정확한 범위.
5. 필수 미완료 vs 선택형 PENDING vs 이미 고친 v566 named-tier ilvl 결함.
6. **다음 작업 딱 하나**, 기존 생산자/소비자·캐시·Native 비용 및 STOP 기준.
7. 불확실한 증거와 main/v003/v016/Project UI/Work OS/주 개발 채팅 권한 경계.

**이 최초 답변 뒤에는 STOP. 사용자 별도 `진행`이 있을 때만 최신 HEAD에서 개발을 재개한다.**
