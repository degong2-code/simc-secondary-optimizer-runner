# SIMC SECONDARY OPTIMIZER — v550 최신 제품 우선·보석 J·AI 없는 범용 시즌 구축 인계

**기준일:** 2026-11-17 KST  
**저장소:** `degong2-code/simc-secondary-optimizer-runner`  
**격리 개발 브랜치:** `probe/chat-cache-v035-20261024`  
**인계 당시 HEAD:** `8540e0dd5d8d540592bdbbfaa681d75625ea096a` (**작성 당시 스냅샷. 새 채팅은 반드시 최신 HEAD·CURRENT·Actions를 독립 확인**)  
**첫 새 채팅 응답:** GitHub 등 **읽기 전용 복원 → 7항목 보고 → STOP**. 별도 사용자 `진행` 이전에는 문서·코드·테스트·Actions·Native·DB2·커밋 금지.

> **단 하나의 목표:** World of Warcraft **26개 DPS 전문화**의 미래 목표 아이템레벨 또는 사용자가 직접 지정한 최종 CHMV 총량에서, **기존 적응형 SimC DPS**를 이용해 최적인 것으로 *관측한 치명·가속·특화·유연 절대 rating* 및 DPS·SEM·95% 우위 확정 여부·실질적으로 다른 근접 대안을 찾는 **실사용 제품**을 완성한다. **새 시즌·확장팩에서도 제품 런타임 AI/LLM 호출·판단 0회**로 필요한 시즌 원본을 스스로 발견·구축한다. 현재 시즌 데이터를 수작업으로 지속 등록하는 프로젝트가 아니다.

## 1. 반드시 읽을 최신 정본과 우선권

**권한 순서:** 최신 사용자 직접 결정 > 최신 승인 v1.4.3 및 비충돌 v1.4 정책 > 최신 GitHub 코드·CURRENT·Actions·실제 Native/시즌 원본 SHA > 과거 인계·역사 자료.

1. 이 문서와 **실제 브랜치 HEAD**, `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 최상단.
2. **보석 사용자 확정:** `docs/USER_APPROVED_GEM_J_POLICY_20261117.md` **최신 개정본**(기존 문서의 과거 "미결정" 문구는 하단 "해결됨" 및 v550을 우선). 이어서 `docs/development/notes/2026-11-17_p1-v550-gem-id-sources-and-approved-selection.md`.
3. `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md` · `docs/development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md`.
4. `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md` 및 `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`(78요소 정본).
5. `docs/development/INDEX.md`, `FILE_MAP.md`, `EVIDENCE_INDEX.md`에서 **필요한 실제 소비 파일·영수증만** 확인.
6. `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md`. 오래된 v1.4.1/이전 문서의 **27 DPS·증강 기원사 포함**은 최신 사용자 지시와 충돌하며 적용 금지.
7. 기존 `docs/CHAT_CONTINUITY_HANDOFF_20261117_V543_AI_FREE_SEASON_ENGINE_PRODUCT_FIRST_READONLY_RESTORE.md`는 기본 프로젝트 설명의 역사적 바탕; 해당 HEAD·계산 수치·다음 작업을 최신으로 가정하지 않는다. 업로드 `LAST_Q&A(7).txt`는 2026-11-17 직접 승인 보석 선택 정책 및 v550 기록 회복을 위한 자료이지 GitHub 내 저장 파일이라고 가정하지 않는다.

## 2. 최종 제품과 정상 사용자 흐름 — 절대 범위 변경 금지

- 대상: **26 DPS**, 증강 기원사·탱커·힐러 제외. 목표는 **DPS 최대화 절대 CHMV rating**, 비율은 보조 표시. DPS/SEM/오차·**95% 통계 판정만**, 관측 1위와 95% 우위 확정을 구분하고 전역 최적 입증을 주장하지 않는다.
- 사용자: 직업·전문화·종족·특성·목표 ilvl(시즌별 자동 기본값 또는 수동값) 또는 **기름 포함 수동 최종 T**, 장신구 2개·선택 특수장비·장식 최대2·선택 보석/영구마부/기름/영약·음식·전투조건을 선택한다. 업로드 SimC 프로필은 캐릭터 정보용 **선택 기능**이고 현재 착용 전체 장비/현재 CHMV를 목표 예산으로 복사하지 않는다.
- 프로그램 내부: **동일 단일 Environment Build 엔진**이 현재 시즌/빌드·대표 일반 장비·무기(분노 전사는 양손 2개 G 트랙)·티어4pc·주능력치·SimC 기본 APL, 시즌 G/J/F/O와 옵션 L/E/O, 정확한 실행 프로필을 구성한다.
- 예산: `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. O는 별도 기름 고정치/중복 가산 없음. **수동 최종 T가 항상 우선**, E는 수동 T에서 추가 가산이 아닌 고정 하한; 특수장비 L은 G에 이미 포함, 장신구 고정 스탯은 자유 G 밖, 제작장비 초기 50:50은 L로 잠그지 않음.
- 실행: `v113 시즌/사용자 입력 → v216/v217 시즌 원본·예산 → v222 B/T → v212 설치 → v098/v096 대표 프로필 → v094/기존 적응형 SimC → DPS/SEM/95%·근접 대안·세션/캐시/취소/재개`.
- **SimC의 영역:** 아이템/보석/장식·장신구 효과, proc, APL, DPS. 앱에서 이를 복제·독립 인증하지 않는다. 프로그램은 선택 ID/옵션/고정 예산·중복 방지·JSON2 정적 rating·95% 및 캐시를 검증한다.
- **금지:** 현재 장비 CHMV 재분배, 장비 조합/획득 경로 추천, 전체 시즌 일반 장비 DB, 새 최적화 엔진, 개별 주문/APL/proc 재구현, 전 전문화/전 ilvl 무조건 Native 반복, 비선택 특수효과/추가 소켓 때문에 검증된 기본 제품 차단, 제품 런타임 AI 호출.

## 3. 최우선 개발 순서와 '실제 첫 장애' 규칙

**P0 — 새 시즌·확장팩 범용 Environment Build 자동 구축:** 사용자 수동 ID/파일 입력을 전제로 하지 않고 Wago DB2·필요한 Blizzard/WCL·SimC의 **같은 빌드** 원본에서 **G까지 포함한 G/J/F/O**, 대표 장비·무기·티어4pc를 자동 결정한다. 일반 25개 G/분노 전사 양손2개 G 별도. 처음 확인할 것은 최신 코드상 사용자 정상 Build의 **첫 미확정 필수 원본/소비 지점 하나**다. 과거 70783·334·G2850/J92/F165/O0·유래 79×2 참조를 새 시즌 승인값으로 복사하지 않는다.
**P1 — 기존 예산·선택지·프로필 소비 연결:** 유효한 원본의 B/T, 수동 T·L/E/O, Policy A 최고 품질 선택지를 **기존 v216→v222→v212→v098/v096**에 연결. 검증된 기본 환경이 선택 항목 미확정 때문에 막히지 않게 구분한다.
**P2 — 실제 사용자 1건의 기존 적응형 SimC:** 정상 설치 후 입력→DPS·SEM·95%·실질적 근접 대안→캐시·취소·재개까지 **이미 있는 엔진 재사용**으로 확인.
**P3 — Windows 설치·웹 화면/오류/저장·결과 전달:** 기존 v535 UI/마부/선택지 기반 정상 브라우저 E2E를 확인하되 P0를 무시하거나 새로운 제품 통합 엔진을 만들지 않음.
**최종 M7:** 이전 시즌 원본·정답·캐시·seed를 사용하지 않는 **ZERO-SOURCE → USER-E2E**, **실제 사용자에게 쓰이는 바로 그 단일 Environment Build 엔진**에서 수행. 정상 신규 Wago/SimC 등 외부 수집은 허용. 이 시험 이전 최종 COMPLETE 주장 금지.

**매 작업:** `STOP → REUSE → CONNECT/FIX → 필요한 최소 EXTEND → 최후 NEW`. 사용자 화면/실사용 소비 위치, 첫 오류, 기존 코드·SHA·Native·캐시 재사용, 불필요한 기능/검증, HTTP/DB2/Native·CPU/RAM/I/O 비용, **중단 기준**을 먼저 구분. `policy.next_review=B10`은 계약 감사 위치이지 개발 강제 순서가 아니다. 사용자 표현 **“우리 프로그램에 필요한 기능만 잘 작동하면 PASS.”** 를 정확성 포기나 임의 READY 승격으로 해석하지 않는다.

## 4. 최신 사용자 직접 확정 GEM J 정책 — v550까지 적용

**보석 분류 및 기본 4종:**

- **Primary Stat(주스탯) 상승 포함 보석 → 특수 보석.** Secondary Stat 상승만 제공하는 보석 → 일반 보석. 일반보석 중 Secondary **1종만** 오르면 단일스탯 보석으로 **사용하지 않음**; 정확히 **2종** 오르면 다중스탯 일반보석으로 **최고품질 선택**.
- 다중스탯 두 값 중 **더 큰 쪽을 '대표스탯'**으로 삼아 C(치명)/H(가속)/M(특화)/V(유연) 4종을 정의. 예: C20+H10은 C 보석. C20+M10·C20+V10도 **C 대표 후보**. '대표 4종'은 '효과 조합이 전부 딱 4개'라는 의미가 **절대 아님**.
- **동일 대표 C/H/M/V의 후보가 여럿일 때 직접 승인한 결정론적 기본 선택:** `crafting_quality 최고 → (두 Secondary 절대 rating 합) 최대 → 정확한 ItemID 최소`. 다른 partner stat은 다른 조합으로 인정하며 독립 보석 조합 DPS 검색을 만들지 않는다. 두 상승값 동률인 모호한 보석은 대표 유형을 임의 만들어 내지 말고 출처에 실제 존재하면 필요 시 사용자 정책 확인.
- **C/H/M/V 일반 다중스탯 각각 최소 1개씩** 기본 장착. 이유는 특정 특수 보석의 '서로 다른 보석 종류' 관련 효과를 누리기 위한 것이며 실제 효과·크리티컬 피해 증가는 **SimC 계산 영역**. 다른 특수 보석 선택 시에도 기본 4종 구성 유지.
- **4개가 수량 상한이 아님.** 사용자가 더 많은 물리 소켓을 선택하면 기존 `C→H→M→V` **순환 반복**으로 일반 보석을 더 배치하고 **실 장착된 모든 일반보석의 두 secondary rating을 반복 횟수대로 J에 합산**. 예: 특수1+일반6=7 물리 소켓일 때 단순 예시 J=6×23=138(**이 23/138은 특정 역사 시즌 또는 계산 사례만**, 미래 시즌 승인값 아님). 특수 보석은 **별도 1소켓**을 차지하고 일반 J에 불포함. 이미 유효한 소켓이 있는 장비는 종류와 관계 없이 일반보석 장착 가능; 소켓을 생성/선택하는 별도 게임 조건은 기존 소켓 경로 소유. 불필요한 보석별 장비종류 허가 Gate 금지.
- SimC 프로필에서 물리 보석 효과를 적용하고, 기존 `gear_*` 절대 rating 주입에서는 보석 정적 CHMV가 **중복되지 않도록** 예산/JSON2 정합을 보존.
- 이 보석 정책은 [`docs/USER_APPROVED_GEM_J_POLICY_20261117.md`](USER_APPROVED_GEM_J_POLICY_20261117.md) 및 [v550 기록](development/notes/2026-11-17_p1-v550-gem-id-sources-and-approved-selection.md)을 가장 먼저 참고. **이미 확정한 선택 우선순위를 반복 질문하지 말 것.**

## 5. 이미 구현/검증한 J와 실제 남은 결손

**기존 재사용/STOP:**

- `v271`: 일반 4종 기본 배치, 전체 물리 소켓 수·특수1 소켓 차감, C/H/M/V 순환으로 4개 초과 장착, 각 실제 일반보석 rating 총합 J 계산이 이미 구현. **소켓·J 합산기를 재작성하지 말 것.**
- `v221`: 동일 빌드 Wago `Item.ClassID=3` + `ItemSparse.Gem_properties`와 SimC `gem_data.inc` GemProperty 조인으로 **물리 보석 ItemID를 이미 자동 발견**한다. 70783 역사 원본에서 **75개 후보** 확인; 75=최종 기본 4종이 아님. `ItemSparse.ExpansionID`로 확장팩 소속 판단. **새 ItemID 검색기 제작보다 이 경로 정상 소비를 먼저 확인**.
- `v230`: 봉인 SimC `item_data.inc`의 ItemID·품질·crafting_quality 파싱. **SimC 단독 ID 열거도 가능**(기존 `candidate_filter`, `item_class`·`gem_properties` 원본 필드)하지만 현재 v230 출력에 `gem_properties` 미투영 및 생성 데이터에 `ExpansionID` 없음. **SimC `gem_data.inc`만으로 실제 ItemID는 나오지 않음**. Wago 소속 경계와 결합이 우선이며 SimC-only 시즌 자동확정 주장 금지.
- `v275/v296`: 봉인 SimC `spell_item_enchantment.inc` 정적 2차스탯 포인트를 exact EnchantID로 읽고 같은 빌드·revision/SHA로 보관; 수치가 불명확하면 `v269/v278`의 봉인·캐시 Native 한 보석 증분 비교를 제한적으로 재사용.
- **v550 `b1a948b6`**: `v216._fresh_pinned_dbc_ordinary_gem_j_source`에서 **같은 대표스탯의 다른 partner도 후보**로 인정하고 최고 제작품질→두 rating 합계→최소 ItemID 선택 구현. 사용자 확정 보석 정책 일부 적용 및 합성 오프라인 회귀 성공.
- **하지만 v548 `v216._fresh_four_stat_simc_observed_j_preview` Native fallback에는 아직 `len(effect_families)==4` 제한이 남아 최신 '대표 C/H/M/V 네 유형'과 불일치.** 실제 fallback을 써야 할 때 해당 국소 조건부터 교정; 모든 75개 보석을 Native 전수 측정하지 말 것.
- `v216._fresh_source_owner_selected_J_F_numeric` 공식 J owner가 최근 DBC/static·Native 후보를 바로 공식 J로 승격하는 완성 경로는 아직 확인되지 않음. 최소 필요한 소스/품질/스탯이 확인될 때 **기존 owner에만 연결**, 새 독립 "품질 인증/소켓 합법성" Gate 제작 금지.
- **Primary+Secondary 보석 특수 자동 역할 분류** 및 새 시즌 4종 물리 ID 선택→대표 프로필→공식 J/B/T→v212 설치/사용자 DPS의 완전한 ZERO-SOURCE 정상 실행은 아직 미검증·PENDING.
- **실제 게임의 선택 추가 소켓**(예: 5·6 일반 보석) 법적 출처가 미관측이라면 그 **선택지만 보류**. 이미 구현된 수량별 J 합산이나 기본 4종 BASE 실행에 새 Gate를 요구하지 않는다.

**다음 실제 개발 작업 하나:** 최신 HEAD normal Build `v113 → v216/v221/v230/v275/v296`에서 **이미 수집한 같은 시즌 ItemID 후보를 Primary/Secondary 분류하고, 정확히 두 개의 Secondary 상승값으로 C/H/M/V 대표 유형 및 사용자 승인 최고품질·총합·최소ID 규칙을 적용해 `v271/v216 original J owner`에 연결하는 첫 미연결 호출 지점**을 찾는다. 기존 소스가 부족한 정확한 항목만 보완하고 STOP한다. Wago `v221`을 우선; SimC-only는 season/ExpansionID 경계를 신뢰성 있게 해결할 수 있을 때 대안. v548 Native fallback 조건 수정이 정말 필요한지 **원본 정적 경로 결과를 먼저 보고** 판단한다. 공식 J가 정확하고 BASE 설치가 가능하면 더 많은 보석/옵션을 연구하지 말고 적응형 SimC 사용자 E2E로 전진.

## 6. 최신 증거 — 실제 Native와 오프라인/공식 수락 구분

| 신분 | 재사용 가능한 범위 | 오인 금지 |
|---|---|---|
| **현 시즌 Native 실증** | 70783 v524: ilvl334, **G2850/J92/F165/O0, B=T3107**; 기본 실 v212 설치/프로필 성공. v525~v533 특정 장비/장신구·장식·티어·마부·옵션 실 SimC. v534 수동 최종 T3200·영구 마부 E30, DPS**175397.79**·SEM**299.40**·캐시 검증 | 70783·정확 프로필/바이너리/빌드 범위 증거. 신규 시즌이나 26 DPS 전체 PASS 아님 |
| **v546~v550 신규 코드** | 기존 생산자/수치 소비 연결. **v550 code `b1a948b6b149a44b1bbe6b3e56127650cee6576a`**. Windows+Ubuntu [v212 #44024180899](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44024180899) **각 500 tests = 496 PASS/4 SKIP/0 FAIL**, [focused #44024180915](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44024180915) **679 = 677 PASS/2 SKIP/0 FAIL**. v113/Windows ZIP/UI 등 해당 HEAD SUCCESS. | **합성/오프라인 PASS**. 신규 실제 시즌 ID 수집·Native/DB2 실행 0, 공식 J 자동 실측/신규 시즌 정상 설치는 **PENDING** |
| **문서 기록 당시 HEAD** | `8540e0dd5d8d540592bdbbfaa681d75625ea096a`, [78 계약 #44024493797](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44024493797) **SUCCESS**. | README/문서 CI SUCCESS를 새 Native·제품 완성으로 바꾸지 말 것 |
| **공식 78요소** | `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`의 78 요소, generic **27 PASS**, current_source **27 PASS**, product_integration **15 PASS**, historical **13 PASS**. **첫 세 축을 모두 통과한 15/78 COMPLETE**. `next_review=B10`. | historical은 별도 증거 축이며 4개 축 모두 PASS여야만 COMPLETE라는 임의 규칙을 만들지 않음. `full_product_e2e=PENDING`, 전체 완성 아님 |

새 시즌에 과거 `ilvl334`/`G2850`/`J92`/`F165`/`O0`, 79×2 참조표/기름/티어/장비 ItemID를 검증 없이 복사하지 않는다. 동일 시즌 같은 신원 static 캐시는 SimC revision 변경만으로 폐기하지 않는다. DPS 캐시는 실제 바이너리·캐릭터·장비/옵션·O/E/T·후보/전투조건/iterations로 구분. 원본 Native·Actions 재검증 전수 반복은 불필요하다.

## 7. 실무 비용·허용 권한과 새 채팅 첫 응답

- *검증 기준:* **“우리 프로그램에 필요한 기능만 잘 작동하면 PASS.”** 정확한 실제 소비 항목/숫자/조건에 필요한 최소 증거는 유지. 선택하지 않은 미검증 옵션의 독립 인증·스펠 효과 재구현은 만들지 않음.
- *자원:* 기존 v217 수집 캐시, v275/v230 원본/sha, v278 Native pair cache, v524/v534 실증을 **REUSE**. 신규 HTTP·DB2·Native·CPU·I/O·메모리를 줄이고 중복 반복을 측정/보고. 필요 없는 검증은 STOP.
- *고정 권한:* 격리 브랜치 개발은 기존 사용자 별도 `진행` 시 가능하나, 별도 승인 없이 `main` 병합, `v003 immutable` 편집, 원본 `v016_SCENARIO_CONTRACT` 직접 통합 완료 주장, ChatGPT Project UI/Instructions/Source 실제 적용 주장, 공식 Work OS M0/Shared State 승격, 다른 채팅의 제품 개발 소유권 이전 금지.
- *새 채팅 최초 응답은 읽기 전용:* 최신 GitHub HEAD·CURRENT·Actions·실제 Native/시즌 원본 영수증을 **독립 조회**해 아래 정확히 일곱 항목 보고 후 STOP. **초기 코드/문서 수정·새 Actions·Native·HTTP·DB2·커밋 금지.**
  1. 최신 브랜치/HEAD 및 최근 CI **PASS/FAIL/CANCELLED/SKIP** (워크플로우·테스트 의미 혼동 금지).
  2. 실제 사용 가능한 사용자 흐름과 첫 필수 차단.
  3. 70783 기존 실제 Native·원본 증거 vs v550 합성 오프라인 증거의 구분.
  4. M0~M7 단계, 78 공식 상태 및 full USER-E2E.
  5. 필수 미완성/선택형 보류/실재 결함의 구별.
  6. 재사용·STOP 기준 및 **가장 가치 있는 다음 작업 하나**.
  7. 미확인 영수증·GitHub main/immutable/Project UI/Work OS/주 개발 채팅 권한 경계.

**첫 응답 후 STOP.** 사용자의 별도 `진행` 지시가 오면 그 시점 최신 HEAD와 **실제 첫 사용자 장애**를 다시 확인한 후 최소 필요한 격리 코드 작업만 한다. 새 시즌 기본 환경→사용자 SimC 실제 결과로 진행하며 기존 성공한 70783 Native·기본 J 합산·아이템 검색기를 다시 개발하지 않는다.
