# SIMC SECONDARY OPTIMIZER — v629 제품 우선·AI 없는 런타임·최소비용 인계

**2026-11-19 KST · GitHub 실제 코드·CURRENT·Actions/Native 영수증 기반 독립 복원용.** 이 문서는 기존 v621 인계와 v628까지의 당시 NEXT를 대체한다. 인계 당시 HEAD **`915a89105c944331f3515051f1f04eed84a33139`**는 스냅샷일 뿐이며 새 채팅에서 최신 HEAD를 다시 조회한다.

> **새 채팅 첫 응답은 READ-ONLY 독립 복원과 아래 7항목 보고만 수행하고 STOP.** 별도 사용자 `진행` 지시 전 GitHub 코드/문서·Actions·Native·HTTP/DB2·캐시·공식 상태를 변경하거나 실행하지 않는다.
>
> **본 작업은 완성된 엔진 재설계가 아니다.** 이미 성공한 ZERO-SOURCE 환경 구축·E0 마부 자동 등록·적응형 SimC·웹 결과·취소·재개를 보존하면서, AI 개입 없이 실행되는 일반 Windows 사용자 제품의 남은 실제 연결만 최소 비용으로 완성한다.

## 1. 우선 정본·복원 순서

- 저장소 `degong2-code/simc-secondary-optimizer-runner`, 사용자 허용 격리 브랜치 `probe/chat-cache-v035-20261024`. 인계 당시 HEAD `915a89105c944331f3515051f1f04eed84a33139`. **먼저 실제 최신 HEAD·커밋·Actions 성공/실패/취소/SKIP를 다시 확인한다.**
- 1순위: **본 파일 → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` → `docs/development/notes/2026-11-19_p2-v629_reuse_original_v213_ring_weapon_scope_to_unblock_11_E0.md`**.
- 이어서 `docs/development/notes/2026-11-19_p2-v628_product_runtime_AI_and_redundant_v212_read_audit.md`, `docs/development/notes/2026-11-19_p2-v627_actual_70961_two_signed_E0_armor_chrome_cancel_resume.md`, `docs/development/notes/2026-11-19_p2-v626_independent_concurrent_permanent_enchants_per_slot_offline.md`, `docs/development/notes/2026-11-19_p1-v624_real_70961_signed_enchant_web64_final_result_reopen.md`, 원본 `v618-v619` 기록.
- 정책: `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `docs/development/POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md`, `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md` **상단 최신 사용자 결정**, `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`.
- 코드·영수증: 시즌 원본 `v216/v217/v191/v211/v213/v583` → 등록 `v196/v220/v212/v222` → 웹 `webui/app.js/v113` → 입력 `v106/v098/v096` → 적응형 SimC `v094/v290/v291/v293`; 실제 Chrome v624/v627 원본과 관련 Actions artifact. 이전 v621 인계는 역사 비교 자료이지 최신 NEXT가 아니다.

## 2. 프로젝트 목적 — 가장 높은 개발 우선권

**26개 DPS 전문화에서 미래 목표 아이템레벨(기본 334) 또는 사용자가 정한 최종 CHMV T에 대해, 실제 SimulationCraft DPS가 최대가 되는 치명·가속·특화·유연의 최적 절대 rating을 구한다.** 증강 기원사·탱커·힐러 제외. 과거 v1.4.1의 27 DPS/증강 포함 문구보다 최신 사용자 직접 결정을 우선한다.

- **사용자 화면:** 직업·전문화·종족·특성, 목표 ilvl 또는 최종 T, 장신구 2개, 선택 특수장비, 장식 최대 2개, 검증된 최고 품질 마부·보석·영약·기름·기타 소모품·전투조건 등. 전체 현재 착용 장비/현재 CHMV 총량 입력은 기본 흐름이 아니다. 업로드 SimC 프로필은 캐릭터·특성 정보 가져오기 선택 기능.
- **프로그램 내부:** 시즌 자동 발견·원본 G/J/F/O 검증 → 목표 ilvl의 표준 대표 일반 장비/무기/주능력치/티어4pc/SimC 프로필 → 고정 L/E/O 회계·분배 → 기존 적응형 SimC Native/JSON2·캐시/취소·재개 → 절대 rating·비율·DPS·SEM·95%·관측 1순위·실질적으로 다른 근접 대안·저장/재열람.
- **장비 조합 추천/파밍 경로/시즌 전체 장비 DB/현재 장비의 스탯 재분배/독립 APL·효과 인증 엔진은 범위 밖.**
- **배포된 프로그램 런타임 AI/API/LLM/에이전트 의존성은 0**이어야 한다. GPT는 개발에만 사용 가능하며 사용자의 Windows 실행 중 AI 서비스 연결을 요구하지 않는다. v628에서 점검한 기본 `v113/v106/v098/v096/v094/v291/v293/webui` 및 의존성에는 외부 생성형 AI 호출 경로가 발견되지 않았다. `v312 model_guided_multiregion=False`는 기본 비활성 수학적 response-surface 실험이지 생성형 AI API가 아니다. 전 레포/의존성까지 전수 인증했다고 과장하지 않는다.
- **SimC 책임:** 장비·마부·장신구·장식·보석·기름의 효과/proc/APL/DPS. **우리 책임:** 정확 ID·소스·게임 빌드·ilvl·물리 슬롯/손·옵션, 예산/고정치·원본 서명, SimC 프로필/JSON2 rating 정합, 후보·SEM·95% 비교·캐시/세션. 마부 효과 연쇄/발동 독립 인증 Gate 금지.

**공식 회계**: `B=G+J+F`, `T=B+O`, 수동 최종 `T` 우선이면 `B=T-O`, `c_final=c_base+o`. L은 G 내 고정 하한, O는 기름의 비자유분배 고정치이며 중복 가산 금지. E는 해당 시즌 정적 예산의 **소유권을 확인한 후 한 번만** 적용; 무조건 G에 더하거나 G에서 빼지 않는다. `E=0`은 효과 없는 마부가 아니라 CHMV 정적 증가량 0인 정상 마부. **미관측 E를 0으로 추정 금지**. 장신구 고정 stat은 자유 G 밖. 95% 관측 최고·95% 선택쌍 우위 확정·전역 최적해 입증은 각각 별개.

## 3. 실제 달성한 기능 — 재개발 및 재실행하지 않는다

- `v567` 실제 ZERO-SOURCE 시즌 환경 자동 구축 PASS. `v570` 실제 Windows Chrome에서 사용자→SimC DPS **64후보→결과** PASS(해당 과거 빌드). `v572` Windows ZIP 중단/재시작/재개 PASS. 기존 `v290/v291/v293` 적응형 SimC·캐시·95%·근접 대안; 새 탐색 엔진 불필요.
- 시즌 `12.1.5.70961`: `v611` 실제 G=2850/J=92/F=165/O=0, `B=T=3107`. `v613` 영구 마부 **38개 최고 품질 원본 계열**, `v617` `product_input` 38/38·정적 E 관련 **30개 증거**, `v618` 정확한 실제 Policy A **19개 E0 자동 등록**. 38/30/19는 다른 판정이며 나머지를 READY로 올리지 않는다.
- `v619` 실제 가슴 마부 `7957`→대표 ItemID→SimC DPS Native6, DPS/SEM/95% 결과 PASS.
- `v624` **실제 70961** Chrome 가슴 E0 선택 → 취소/HTTP 재시작/재개 → Native64/64 완료 → 절대 rating, DPS, SEM, 95%, 대안6 표시 → 저장 목록 및 재시작 후 재열람 **PASS**. [Actions #44454908607](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44454908607). 이 95% 우위는 **미확정**, 전역 최적해 아님. 한 E0 사용자 시나리오의 끝까지 수행 증거이며 전체 제품 인수 아님.
- **최신 사용자 직접 결정:** 모든 **실제 지원 가능한 영구 마부**를 **각 물리 부위당 하나씩 동시 선택**한다. 10개 일반 장비 부위+반지2+주/보조무기 등 슬롯별 독립 선택; 같은 enchant ID도 서로 다른 실제 허용 슬롯(예: 두 반지)에 가능. v625의 2~4 방어구만/반지 동시 금지 정책 폐기. 무기 손별 적용 subclass 및 룬벼리기 충돌 검증은 유지.
- `v626` 위 슬롯별 다중 입력·UI/프로필·E0 차단 오프라인 PASS. `v627` **실제 70961** 머리 **7959**+가슴 **7957** 동시 선택, 각 물리 장비 line의 enchant_id 정확 1회, Chrome Native2→Cancel→HTTP 재시작/동일 세션 Resume→누적 Native4 **PASS**. [Actions #44463091504](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44463091504). **다부위 64후보 최종 결과/95% 시험은 아님.** 최초 synthetic 머리 7951 오선택은 실제 등록 목록에 없어 Native DPS 전 차단; 실제 등록 7959로 정정. 합성 fixture ID를 실 시즌 승인 ID로 오인 금지.
- `v628` 다부위 마부 v212 문서 반복 read를 **N회→세션당 1회**, 슬롯별 원본·물리 마스크·서명 검증 유지. [focused #44464806168](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44464806168) 685 PASS/2 SKIP, 신규 Native0·캐시 폐기0·SimC 재컴파일0. 위 기본 실행 경로 AI 비개입 감사.
- **현재 가장 최근 `v629`:** 기존 v618 실제 70961 보류 19개 원인 **11+8로 분해**. **11 IDs** `7967,7979,7981,7983,8007,8009,8011,8037,8039,8041,8689`는 남은 blocker가 `EXACT_PHYSICAL_SLOT_OR_HAND_RELATION_NOT_VERIFIED` 하나. **8 IDs** `7965,7969,7995,7997,8021,8023,8025,8027`는 `EVIDENCE_MISSING:chmv_budget`도 있음. 정확히 v216 receipt의 봉인 `catalog.enchants.items` 슬롯 가족 정보가 `v196_enchant_source.rows` 변환에서 빠져 v220 Policy A가 반지·무기를 slot unresolved로 오판한 것. **v629 코드가 기존 sealed v213 원본과 v196 projection의 ID/토큰/품질/클래스/마스크 정합을 확인하고 v220에 원본 슬롯 가족을 재전달**. 실 최종 손/ItemID/무기 subclass는 여전히 v098/v216이 판정. [focused #44466725249](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44466725249) **685 PASS/2 SKIP**, [v212 Win+Ubuntu #44466725307](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44466725307) 각 **529 PASS/4 SKIP**, [계약 #44467070743](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44467070743) SUCCESS. **신규 Native/HTTP/DB2/캐시 무효화0**.
- **중요한 경계:** v629 실제 **새 70961 설치 재실행 영수증은 없음**. 새 등록을 **19→30으로 실측 완료했다고 주장 금지**. 11개도 실제 아이템 손·무기 subclass 조건별로 다르게 선택 가능; 정확히 등록·물리 적용된 항목만 UI READY. 위 8개의 미확정 E를 0 또는 과거 `70783` 수치로 대체 금지.

## 4. 다음 필수 우선순위 — 제품 기준 단일 NEXT

**P2 최우선 1개**: 현재 시즌 원본 stage workspace가 이미 재사용 가능하면 **`v629` 수정한 `v196→v220→v212`의 source-only 자동 등록을 해당 70961 같은 소스·빌드로 정확히 1회 검증**, 승인 수/아이템 ID/정적 E·슬롯·원본 SHA/부위·손 보류 이유를 증거로 기록한다. **19→30은 기대 가설이지 PASS 아님.** workspace/정확 출처가 없으면 첫 결손을 기록하고 기존 stage/Actions/아티팩트 재사용 여부를 먼저 확인한다. 이 한 단절을 입증하려고 **환경 Native6·DPS64·26전문화 무조건 재실행 금지**. 승인 11건 실제 등록이 확인되면 기존 14슬롯 UI 및 대표 ItemID/hand 매핑에서 필요 최소 1회 적용 경계만 확인한다.

**다음 P2**: 원본 chmv_budget가 미확정인 8개 **정확한 현 빌드 정적 E·G 소유권·반지/무기 손 증거**를 제품이 실제 소비하는 범위에서만 확인한다. 실제 등록 가능한 E>0가 확인되면 기존 `v212/v222/v531` 소유권/수동 T 경로를 재사용하여 부위별 `E_total[k]=ΣE_slot[k]`를 **한 번** 반영, 정확한 stat floor·G 중복 방지·cache identity·SimC 주입을 연결한다. **일반 E+ 전수 효과 메커니즘 연구나 새로운 예산/탐색 엔진을 선행 개발하지 않는다.** 미확정 항목만 보류하고 검증된 BASE·E0 사용자 실행은 유지.

**P3**: 26 DPS·시즌 구축·최고품질 선택지·모든 실제 지원 부위 동시 선택·대표 SimC·결과·저장/재열람·중단/재개까지 Windows 일반 사용자 제품 전체 수락. 전체 환경 성공과 개별 BASE/선택 옵션 성공 범위를 구별한다. 옴니움 등 확장팩 전용 콘텐츠는 후순위 선택형 모듈이며 일반 임시 마부 제외, **무기 기름 O는 지원**. DK 룬벼리기는 별도 SimC 원본 경로.

## 5. 효율·엔진·AI 규칙 — 새 채팅이 개발 중 지켜야 함

- 모든 코드 작업 시작 전에 **사용자 화면/실제 소비 단계, 첫 막힌 입력, 기존 코드·원본·영수증 재사용, Native·HTTP/DB2·CPU/RAM/I/O·캐시 비용, 미선택 옵션 격리·STOP 이유**를 짧게 밝힌다. `STOP → REUSE → CONNECT/FIX → 필요한 최소 EXTEND → 최후 NEW`.
- 이미 통과한 ZERO-SOURCE/Native/캐시/웹64/취소·재개를 다시 개발하거나 전수 반복하지 않는다. 동일 시즌 **정적 아이템 캐시는 SimC revision 변경만으로 폐기 금지**, DPS 캐시는 정확 binary SHA·프로필/장비/옵션·후보·O·전투조건·iterations identity로 분리.
- SimC 실제 메커니즘·마부 발동, 별도 APL·최적화 solver·SEM 미세정밀화·AI/LLM API·지속 에이전트·시즌 전체 장비 DB·불필요 Gate 추가 금지. 런타임 AI 0 원칙을 지속 검사. `v312` opt-in 모델 근사를 기본 경로로 끌어오지 않는다.
- 원본 scope를 혼동하지 않는다: v613 `source_scope`/`auto_source_scope`, v616 무관 중복 ID, v621 시험용 `ilvl/ilevel` 혼동, v627 합성 7951/실제 7959, v629 실제 sealed v213/손실 v196 projection, 만료된 옛 Actions artifact 복원 실패. **테스트 fixture·과거 70783 Native·이름/품질만으로 현 70961 값을 승인하지 않는다.**
- 실환경 결과는 **신규 PASS/재사용 역사 PASS/offline PASS/미구현/원본 부재/정상 fail-closed** 구분. 통계는 95%만, 전역 최적 확정 주장 금지. CI SUCCESS≠Native PASS≠전체 제품 COMPLETE.

## 6. 권한 및 공식 원장

- 공식 원장 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`. **15/78은 전체 코드 구현률이 아님**. B10은 원장 검토 순서이고 실제 사용자 제품 P2의 강제 선행 Gate가 아님. 공식 요소 변경은 별도 승인·증거 없이 금지.
- GitHub `main` 병합, `v003 immutable` 변경, 원본 `v016` 직접 통합 완료 주장, Project Sources/Instructions UI 실제 적용 완료 주장, Work OS M0·Shared State 공식 승격 금지. 기존 주 제품 개발 채팅의 소유권은 인계 문서 작성이나 새 채팅 독립 복원만으로 자동 이전되지 않음. 개발 허용 범위는 사용자 별도 지시와 격리 브랜치 원칙에 따름.
- 사용자 명시적으로 `진행`을 지시하기 전 **첫 응답은 보고만 하고 STOP**. 새 채팅의 직접 작업 시작 시 그 시점의 최신 HEAD/실제 사용자 첫 단절을 다시 확인.

## 7. 새 채팅 첫 응답 — 7항목만

1. **최신 실제 HEAD/커밋·최근 Actions:** 최신 SUCCESS/FAIL/CANCEL/SKIP 구분, v629 중간 실패(구 기대값, 만료 artifact)와 최종 PASS 구분.
2. **제품 목적/범위:** 26 DPS·미래 CHMV 절대 rating·런타임 AI0·SimC/프로그램 책임 분리.
3. **시즌 환경/마부 등록:** ZERO-SOURCE, 현 70961 G/J/F/O, 38/30/19 구분, v629 11(슬롯 정보) +8(E 증거) 보류·수정 근거와 신규 등록 미측정.
4. **기존 엔진·실 Native:** v624 실제 단일 E0 64완료/결과·95%, v627 실제 2 E0 Native4 취소·재개, v628 I/O 최적화 및 AI 감사. 증거 범위를 혼동하지 않음.
5. **필수 미완료 vs 선택형 보류:** v629 source-only 새 설치 등록 확인, 양수 E 원본 회계·부위별 합산, 최종 Windows 제품 전체 인수; 옴니움 등 선택형 후순위.
6. **비용 대비 다음 1개:** 동일 70961 기존 source stage 재사용 가능한 경우 v629 v196→v220→v212 source-only 재등록 계수/ID/receipt 증명, 불가하면 STOP·첫 장애만 보고. Native64/전체26 반복 금지.
7. **증거·권한 경계:** 미확인 원본, 공식 15/78·full_product_e2e PENDING·B10, main/v003/v016/Project UI/Work OS, 주 제품 개발 소유권 불변.

**보고 후 STOP.** 사용자 별도 `진행` 전 개발 금지.
