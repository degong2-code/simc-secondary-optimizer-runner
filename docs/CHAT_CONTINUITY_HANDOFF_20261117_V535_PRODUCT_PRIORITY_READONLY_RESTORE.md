# SIMC SECONDARY OPTIMIZER — v535 제품 완성 우선 최신 독립 인계
**기록일:** 2026-11-17 (KST) · **인계 목적:** 다음 일반 채팅에서 최신 GitHub/Actions/Native를 *읽기 전용*으로 독립 복원한 뒤, 사용자가 별도로 `진행`할 때에만 남은 첫 필수 사용자 제품 연결을 최소 비용으로 완성한다.

> **이 문서를 읽어야 하는 이유:** 2026-11-16의 기존 M2 중심 인계는 중요한 역사·원본 증거로 유지하되 **최신 개발 위치를 반영하지 못한다.** 그 이후 v524 실제 M1→M2 Windows 설치, v525~v527 실 장비 조합, v528 소켓·마부 원본, v530~v534 영구 마부 자동/수동 T 실제 SimC, v535 제한적 사용자 UI 오프라인 연결이 생겼다. **M2를 처음부터 재구현/재실증하지 않는다.**
>
> **조회 시점 스냅샷:** 저장소 `degong2-code/simc-secondary-optimizer-runner`, 격리 브랜치 `probe/chat-cache-v035-20261024`, 인계 작성 **시작 전 HEAD `45ddc5fbf085a6b4ced9beaa0ec285de1c69a6b1`** (`docs(v535)`). 문서 커밋 자체가 HEAD를 바꾼다. 이것을 영구 최신 HEAD로 반복하지 말 것. **새 채팅은 반드시 브랜치의 현재 HEAD, 최신 커밋·Actions를 다시 읽는다.**

## 1. 새 채팅에서 먼저 읽을 정본 (순서)

1. **이 문서:** `docs/CHAT_CONTINUITY_HANDOFF_20261117_V535_PRODUCT_PRIORITY_READONLY_RESTORE.md`
2. `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` — **맨 앞 v535 최신**, 그 자체가 2026-11-17 UI 연결 요약이며 구버전 M2 우선순위로 되돌아가지 말 것
3. `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md` — 맨 앞 v534/v531~v533 실 Native 결과와 M0~M7
4. `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json` — **78개 계약의 공식 상태**(임의 PASS·COMPLETE 금지)
5. `docs/development/INDEX.md`, `FILE_MAP.md`, `EVIDENCE_INDEX.md`
6. `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md`
7. `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md`
8. 역사 증거가 실제로 필요할 때만 `docs/CHAT_CONTINUITY_HANDOFF_20261116_M2_SOURCE_SHA_PRODUCT_COMPLETION_READONLY_RESTORE.md` 및 개별 compact/Actions로 확장

**업로드된 `LAST_Q&A(5).txt` (2026-11-17)는 마지막 대화가 `8025 + 수동 T` 구현 직전 세 차단점(v531.user_scope / v098 자동 B 동일성 / v096 동시 입력)을 찾았음을 보여준다.** 그러나 그 **이후 GitHub v534 실 Native PASS, v535 UI 오프라인 PASS**가 발생했다. 업로드 파일의 마지막 PENDING을 최신 상태로 오인하지 말 것. 과거 자료 속 **27 DPS/증강 기원사 포함, 7소켓/J138 고정, 미래 시즌 334 고정**은 최신 승인 정책과 충돌한다. **26 DPS(증강 기원사·탱커·힐러 제외)** 및 **시즌마다 실측 G/J/F/O**가 우선한다.

## 2. 제품 목적 — 변경 금지

- **미래 파밍 목표의 절대 rating:** 사용자가 현재 모든 장비를 입력·재분배하지 않는다. 26개 DPS 전문화에서 목표 ilvl(해당 시즌 자동 추론 또는 수동 입력) 또는 **사용자가 직접 지정한 최종 CHMV 총량 `T`**을 기준으로 치명/가속/특화/유연의 최적 *절대 rating*을 SimC DPS로 탐색한다.
- 사용자: 직업·전문화·종족·특성, 목표 ilvl/T, 장신구2, 선택 특수·제작장비·장식 최대2, 검증된 보석/영약/기름/영구 마부/소모품/전투 조건. 기본 일반 장비·무기·4티어·주능력치·APL 실행용 프로필은 내부 구성. 선택 업로드 SimC 프로필에서 캐릭터·특성 정보를 가져올 수 있어도 현재 장비 총계를 기본 목표로 채택 금지.
- 결과: 관측 최고 절대 rating, 비율, DPS, SEM/오차, **95% 판정**, 관측 1순위와 통계적으로 우세 확정의 구분, 의미 있게 다른 근접 대안(없을 수도 있음). **전역 최적해 입증 아님.**
- 회계: `G` 대표 비장신구, `J` 검증된 보석, `F` 검증된 영약, `O` 무기 기름 고정치, `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. 사용자 **수동 최종 T 최우선**: `B=T-O` 및 고정 E/L 하한 검증. 특수장비 `L`은 G 안의 하한으로 재가산 금지, 정적 마부 `E`는 해당 회계 소유자로 한 번만, O도 한 번만. 장신구 정적 스탯은 자유 G 밖, 누락된 gear record는 0이라고 추론 금지. 제작장비 초도 50:50 배분을 L로 잠그지 않음.
- 게임 아이템 효과/proc/APL/DPS/SEM은 **SimulationCraft가 전담**. 프로그램은 정확한 ID·ilvl·옵션·프로필, 정적 G/J/F/O/L/E, 소유권/중복 금지, Native JSON2 정합, 적응형 후보·95% 통계·캐시·취소/재개·출력을 담당한다. **제품 런타임 AI 호출/판단은 0**을 유지한다.
- 제외: 장비 조합·획득 경로 추천, 전 시즌 일반 장비 DB, 새 최적화 엔진, 자체 APL/proc/효과 모델, 효과 인증 Gate, 26 DPS 무조건적 Native 전수, 전수 시즌 아이템 연구.

## 3. 최신 검증된 사실 — 구현/실행/승인 상태 구분

| 실제 범위 | 근거 | 현재 판정 |
|---|---|---|
| **M1 현재 시즌 ilvl 자동 탐색** | v523 인증 Blizzard·WCL·Wago/DB2 동일 빌드 원본 및 CurrencyTypes SHA | `12.1.5.70783`의 기본 ilvl **334 실증**. 미래 시즌 값으로 복사 금지 |
| **M2 G/J/F/O→B/T→v212 원본 설치** | v524 이후 실제 Windows 사용 경로 및 v528/v530~v534 설치 재실행 | 현 실 사례 **G2850/J92/F165/O0, B=T3107** 실제 설치. `v113→v216/v217→v191/v211/v213→v277 G/v266·v271 J/v281·v278 F/O→v222→v212→v098/v096` 재사용 |
| **장비 복합 실 Native** | [v527 compact](development/research_receipts/p1_v527_70783_real_user_option_matrix_compact.json), Actions #43888153268/#43891405224 | 서로 다른 장신구 3쌍, 특수 목걸이/제작·장식2·티어4pc 조합의 **해당 시나리오 실제 Native 성공**. 모든 마부·소켓과 한꺼번에 조합한 결과로 확대 금지 |
| **마부 v528 정적 E** | [v528 compact](development/research_receipts/p1_v528_70783_real_socket_enchant_native_compact.json), Actions #43897717703 | 정확 같은 대표 생존334 반지에서 `7967` E0, `8025` 가속+30, `7965` 특화+26. 실제 SimC 전후 JSON2·SHA |
| **마부 자동 목표 사용자 적응형 SimC** | [v530](development/research_receipts/p1_v530_70783_one_real_E0_enchanted_user_six_dps_compact.json), [v532](development/research_receipts/p1_v532_70783_real_positive_E30_enchant_user_compact.json), [v533](development/research_receipts/p1_v533_70783_real_positive_E26_mastery_user_compact.json) | `7967` B=T3107, `8025` B=T3137, `7965` B=T3133: **각 실제 사용자 Native6/SEM/95%/cache-only6 HIT·신규 Native0 PASS**. 모두 한 정확한 캐릭터·장비·빌드 scope |
| **양수 E + 수동 T 실 SimC** | [v534 compact](development/research_receipts/p1_v534_70783_manual_T3200_8025_E30_user_native_compact.json), [Actions #43974259684](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43974259684) | `8025` E+30, **수동 최종 T3200→B3200**, E는 B 안의 가속 고정 하한, 자동 T3137로 덮지 않음. Native6/95%/SEM/cache-only6/JSON2 18 SHA **PASS**. `7965+manual T` 별도 Native 불필요: 기존 회계 오프라인 + v533 실 자동 Native 재사용 |
| **v535 검증된 UI 선택** | 최근 코드/ [CURRENT](../CURRENT_PRODUCT_DEVELOPMENT_STATE.md), [v182 Ubuntu/Windows offline #43981574831](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43981574831), [v113 offline #43981574864](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43981574864) | `/api/v1/season-option-catalog`의 **`verified_exact_user_enchant_runtime`**와 `webui/app.js`의 반지1 7967/8025/7965 선택이 **정확한 70783 설치 SHA·생존/human334·장신구270175/270173·특수/장식/기름 없음**에서만 오프라인 PASS. 일반 `enchant_candidates`는 `runtime_selectable=false` 유지, 미검증 상황 UI fail-closed |
| **v535 브라우저 사용자 E2E** | 현 CURRENT가 미실행으로 구분 | **PENDING**: 실제 설치가 있는 브라우저에서 catalog→UI 선택→plan→start→result 연결 새로 검증하지 않음 |
| **추가 5·6소켓** | [v528 source/J 원본](development/research_receipts/p1_v528_70783_real_socket_enchant_native_compact.json) | `J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING`. J115/138은 *미승인 산술 후보*. 게임 내 최종 장착 허용/부여 근거 전까지 `J_approved=false`, 5/6소켓 프로필 설치·DPS 금지 |

**재현 조건 주의:** 위 70783 Native는 대체로 `hunter/survival`, `human`, ilvl334, `finger1=268266`, `trinkets=270175/270173`, 기름·특수장비·장식 미선택, 봉인된 v212와 SimC `de11f57...` exe SHA `1fc927...`의 **한 경계**에 대한 증거. v525의 복합 특수 장비와 v534의 마부/수동 T는 서로 다른 시나리오다. **합성 PASS ≠ 실제 Native ≠ 브라우저 PASS ≠ 26 DPS 제품 완료**.

**최근 Actions 확인 스냅샷:** 최종 78 계약 [#43981798628](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43981798628) SUCCESS(HEAD `45ddc5fb...`). 직전 `a0ba619e...`의 v182 UI [#43981574831](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43981574831) Ubuntu/Windows SUCCESS, v113 [#43981574864](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43981574864) Ubuntu/Windows SUCCESS, [focused #43981574892](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43981574892) SUCCESS, v180 [#43981574827](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43981574827) offline SUCCESS·`native-six-cases SKIPPED`. 과거 v535 중간 FAIL·CANCELLED는 이후 PASS로 해소한 범위와 미해소 범위를 분리한다. **이번 인계 자체 신규 Native·HTTP·DB2·Actions 실행 없음**.

## 4. 현실적 제품 완성 로드맵 M0~M7

| 단계 | 현재 해석 | 다음 실행 원칙 |
|---|---|---|
| **M0 정본/자산** | GitHub INDEX/FILE_MAP/EVIDENCE_INDEX/시즌 캐시·영수증 존재 | **REUSE/STOP**: 역사 전면 재감사·자료 재수집 금지 |
| **M1 시즌 목표** | 70783 실 시즌 기본 목표 334 **실증** | 새 시즌일 때만 동일 조인으로 추론; 334 자동 고정 금지 |
| **M2 환경 설치** | 70783 동일 실제 원본 **G/J/F/O→v212→대표 프로필 Native 실증** | 이미 통과한 BASE 재구현·새 Gate 금지. 실제 시즌/아이템 ID/빌드 변경 시 필요한 owner만 증분 보완 |
| **M3 실행·통계·캐시** | v094 적응형 Native/95%/SEM/관측 1순위·cache-only 실제 다수 PASS; 취소/재개 구현 자산도 기존 있음 | **REUSE**. 신규 스케줄러·SEM 극소 정밀화/전수 Native 금지. 출시 경로에서 실제 취소·재개 소비 누락만 점검 |
| **M4 옵션 선택/자동 등록** | v525/v527 복합 장비, v528-v534 마부 정적·자동·수동 T 성공; v535 정확 범위 UI 오프라인 연결 | **단일 정확 장비/시즌/품질/적용 조건의 정당한 승격만.** 미선택 소켓5/6 등 미검증 옵션을 BASE 차단 이유로 삼지 말 것 |
| **M5 26 DPS 경계** | 여러 전문화 과거 Native·현재 장비 구조 유형 증거 존재; 26 전체 제품 통합 수락 아님 | 실제 제품의 신규 무기·티어·물리 구조 유형만 대표 최소 검증. 전 전문×전 레벨 Native 매트릭스 금지 |
| **M6 Windows 제품 수락** | UI·웹 API·Windows 패키지·TestClient/loopback 기본 자산 존재; v535 GUI 선택은 오프라인만 PASS | **지금 제품 최우선:** 사용자 브라우저/Windows 설치 v212 환경에서 옵션→plan→start→결과 한 사용자 실제 E2E; 첫 실행·에러 표시·캐시/취소·재개/결과 폴더 확인 |
| **M7 최종 완성 판정** | `full_product_e2e=PENDING` | 마지막에 실제 새 시즌 **ZERO-SOURCE→USER-E2E** 및 78 계약 수락 근거 확인. 이미 유효한 공통 Native/기존 통계·캐시 증거는 재사용 |

**78 요소 공식 위치:** `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json` 78개 중 현 `generic PASS 27/current_source PASS 27/product_integration PASS 15/historical PASS 13`; 공식 집계 **15/78 COMPLETE**, `full_product_e2e=PENDING`. `next_review=B10`은 *원장 검토 위치*이지 다음 제품 작업의 우선순위가 아니다. 이 숫자를 전체 제품 구현률로 해석하거나 단일 PASS 때문에 승격하지 않는다.

## 5. 다음에 가장 먼저 할 일 **하나**

**v535 정확 마부 사용자 UI의 실제 설치 환경 브라우저 E2E를 최소 비용으로 수락한다.**

- **사용자 경험상 위치:** 실제 Windows 패키지/로컬 UI 첫 실행에서 현재 시즌 v212 설치/원본 SHA 검증 → `/api/v1/season-option-catalog` → 반지1의 정확 검증된 마부 중 하나 선택 → `/plan` 예산·SHA/세션 키 → `/start` 기존 SimC 적응형 실행 → 결과·SEM/95%·rating·캐시 및 오류 표시.
- **최초 실제 차단 확인:** 최신 HEAD에서 `v113` 카탈로그 생산자 → v535 UI 이벤트/선택 상태 → v106·v531·v098·v096 소비자 → 기존 v094/캐시를 읽는다. 이미 오프라인 PASS인 부분은 중복 구현하지 않는다.
- **최소 테스트:** 70783에서 이미 실 Native와 예산이 증명된 8025 한 구성 또는 동등한 7967 한 구성을 사용. 동일 identity의 기존 세션·캐시가 재사용 가능하면 Native0, 불가능하고 실제 GUI→worker 증거가 필요할 때에만 정확 한 세션의 **최소 신규 Native**. 26전문화 전수/새 DB2/마부 효과 역구현 금지. UI가 사용자 입력 범위를 벗어날 때 선택 해제·HTTP 422·기본 BASE 실행 유지도 검증.
- **완료 판정:** 실제 설치가 존재하는 사용자 UI에서 정확 선택→`/plan`→`/start`→`/result`의 **한 실행 영수증·SHA·실제 Native/캐시 소유자**가 연결되면 *그 범위만* PASS. 단순 backend Native PASS나 v535 offline UI PASS를 브라우저 E2E PASS로 바꾸지 말 것.
- **차단 시:** 정상 4보석 BASE 또는 다른 미선택 옵션을 차단하는 신규 Gate 금지; 검증되지 않은 5/6소켓은 보류. 첫 실제 연결 결손만 수정하고 STOP.

그 다음에만 정확한 실패 사례를 기준으로 Windows 설치/첫 실행 품질, 옵션 일반화·26개 DPS 신규 구조, 최종 M7 수락을 순차 처리한다. **수동 T+E는 v534로 이미 실증돼 있으므로 다시 처음부터 하지 않는다.**

## 6. 모든 후속 개발에서의 절대 유의사항

1. **중복 금지 절차:** `INDEX → FILE_MAP → EVIDENCE_INDEX → 실제 생산자/호출자/소비자 → CURRENT·Actions·Native·캐시 identity`. 먼저 `STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW`.
2. **작업 전에 사용자에게 간결히 보고:** (a) 정확 사용자 입력/화면 소비 위치, (b) 현재 무엇이 막혔는지, (c) 기존 코드·원본·캐시 재사용 가능 범위, (d) 만들지 않을 것, (e) Native·HTTP·DB2·CPU/RAM/I/O 비용과 STOP 조건. 보고는 새로운 승인 Gate가 아님.
3. **정적 캐시:** 같은 시즌 아이템 정적 ID/variant 캐시는 단지 SimC revision 변경으로 폐기하지 않는다. 사용자가 요청한 명시 교정만. **DPS 캐시**는 binary/profile/source/selected item/enchant/E/O/B/T/iterations/전투 identity별로 엄격 분리.
4. **회계:** `B=G+J+F`, `T=B+O`는 무마부 기본 표기. **검증된 추가 E는 사용자별 G/B에 한 번 포함하거나 수동 T 안의 floor로 보호**하며 G/J/F/O 기존 봉인 설치값을 무단 덮어쓰지 않는다. `7967 E0`, `8025 E+30`, `7965 E+26` 실측은 정확 v528 조건에서만. 마부 이름·SimC 핸들러만으로 범용 등록하지 않는다.
5. **동시 옵션:** v527 특수+제작+장식2+티어4+장신구/3장신구 조합, v534 마부+수동 T는 **별도 사례**. 모든 옵션 동시 부착 PASS로 일반화하지 않는다. 3장식, 동일 슬롯 중복, 소켓 5·6의 검증 안 된 J는 차단.
6. **AI 0회 런타임:** AI가 후보 결과·스탯·효과·DPS를 직접 판단/계산하지 않는다. 개발자의 연결·테스트 작성 역할과 제품 런타임을 분리, 모든 결과 SimC 원문·결정론적 회계·정확 SHA만 사용.
7. **상태 보고:** 실제 구현/오프라인 PASS/역사 Native 재사용/이번 신규 Native/개인 GUI E2E/공식 수락을 항상 별개로 기록. 통계적 우위와 단순 관측 DPS 차이를 혼동 금지.
8. **권한:** 이 격리 브랜치에서 후속 `진행` 지시가 있을 때 최소 개발은 허용되나, `main` 병합·v003 immutable·원본 v016 통합 완료 주장·Project Sources/Instructions 실제 적용·Work OS M0/Shared State·공식 승격·다른 채팅/MAIN/WORK의 운영 주도권 이전은 사용자 별도 허가 없이는 금지. 새 채팅 인계 자체는 제품 승격 아님.

## 7. 새 채팅 첫 응답 계약 — 읽기 전용 후 STOP

처음에는 실제 GitHub를 열고 HEAD·최근 커밋과 Actions를 **독립 확인**, 위 정본 파일·컴팩트·원장과 업로드 `LAST_Q&A(5).txt`의 시간적 차이를 복원한다. 새 채팅 첫 응답은 다음 **7가지**만 정확히 보고한다.

1. 실제 격리 브랜치·최신 HEAD·최근 Actions PASS/FAIL/CANCELLED/SKIPPED 구분
2. 실제 사용자 제품에서 이미 사용 가능한 기능 vs UI/일반화/출시에서 여전히 막힌 경계
3. 실 Native 및 원본 SHA·실 시즌 DB2·오프라인 PASS 각각의 근거 수준
4. M0~M7 실제 위치, 78요소 공식 상태, `full_product_e2e`
5. 필수 미완료·선택형 보류·확인된 실제 결함의 구별
6. 비용 대비 가장 중요한 다음 작업 **하나**와 재사용·비용/STOP
7. 미확인 증거·권한 한계 및 금지되는 승격

**첫 응답에서는 코드·문서 수정, 테스트/Actions/Native/HTTP/DB2 실행, 커밋·병합을 일절 하지 않는다.** 7항목 보고 후 명시적으로 **STOP**. 사용자가 **별도로 `진행`**한 때에만 최신 HEAD와 첫 실제 차단점을 다시 읽어 격리 브랜치에서 최소 개발을 시작한다.

---
**인계 증거 경계:** 본 문서 작성만으로 신규 Native·UI 브라우저 E2E·원본 v016 직접 통합·제품 전체 완료가 성립하지 않는다. 공식 COMPLETE는 실제 78 계약과 수락 증거만이 결정한다.
