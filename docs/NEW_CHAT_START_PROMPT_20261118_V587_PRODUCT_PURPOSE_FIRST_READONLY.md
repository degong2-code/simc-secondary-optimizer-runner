# SIMC SECONDARY OPTIMIZER — 최신 제품 완성 독립 복원·인계 (v587 이후)

SIMC SECONDARY OPTIMIZER 프로젝트를 **GitHub 최신 HEAD·CURRENT·실제 코드·Actions·원본 Native 영수증을 기준으로 읽기 전용으로 독립 복원**하라. 이 작업은 **기존 개발을 다시 시작하거나 과거 Native를 재검증하는 업무가 아니다**. 현재 일반 제품을 끝까지 완성하기 위해 이미 통과한 엔진을 보존하고, **실제 사용자에게 남은 최소 연결**을 정확히 찾아내는 인계다.

## 먼저 읽을 GitHub 정본

- 저장소: `degong2-code/simc-secondary-optimizer-runner`
- 격리 브랜치: `probe/chat-cache-v035-20261024`
- 인계 작성 전 스냅샷 HEAD: `a7fd8035688961c3b03492e126c33d9fd2c9c53c`; **이 SHA는 최신 HEAD가 아니다. 실제 브랜치를 재조회하라.**
- **첫 문서:** `docs/CHAT_CONTINUITY_HANDOFF_20261118_V587_PRODUCT_PURPOSE_REUSE_PERMANENT_ENCHANT_NEXT.md`
- 다음: `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md`, `docs/development/notes/2026-11-18_p1-v587-exact-selected-enchant-scope-and-dk-source-guard.md`, `docs/development/notes/2026-11-18_p1-v586-simc-only-dk-runeforge-and-unnecessary-work-boundary.md`, `docs/development/notes/2026-11-18_p1-v585-enchant-quality-and-ranged-source-comparison.md`.
- 정책: `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md` **최상단 최신 결정**, `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `docs/development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md`, `docs/development/POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md`, `docs/USER_APPROVED_GEM_J_POLICY_20261117.md` F절, v1.4.3 시즌 G/J/F/O 승인 설계, `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json` 및 GENERATED/INDEX/FILE_MAP/EVIDENCE_INDEX.
- 우선권: **최신 사용자 직접 결정 > 최신 승인 정책 > 실제 현 코드·CURRENT·Actions/Native > 과거 인계**. 고정 SHA·역사 인계의 다음 작업이 현재 HEAD를 대체하지 못한다.

## 제품 목적 — 한 문장도 흐리지 말 것

**새 WoW 시즌·확장팩에서도 AI 없이 시즌 원본·대표 환경을 자동 구축하고, 사용자의 목표 아이템레벨(기본334) 또는 최종 CHMV 총량 T에서 실제 SimC DPS가 가장 높은 치명·가속·특화·유연의 미래 파밍 목표 *절대 rating*을 찾는 범용 Windows 사용자 프로그램.**

- **26개 DPS 전문화만**, 증강 기원사·탱커·힐러 제외.
- 사용자는 전문화·종족·특성·목표 ilvl/수동 T, 장신구 2, 선택 장비/장식 최대 2, 보석·영약·음식·물약·기름·영구 마부·전투조건을 설정. 현재 착용 장비 전체 선택/현재 스탯 총계 재분배 금지. 내부 대표 일반 장비·무기·티어4·SimC 프로필 사용.
- **`B=G+J+F`, `T=B+O`, 수동 최종 `T` 우선/`B=T−O`**, `c_final=c_base+o`. 고정 L/E/O, 손·장비 부위, 장신구 G 외부, 정적 rating 중복 방지. 출력 rating/비율/DPS/SEM/95% 확정 여부/관측 1순위와 실질적 근접 대안/캐시·취소·재개.
- SimC가 아이템 효과·발동·APL·DPS 계산. **제품 런타임 AI 0, 효과 재구현·독립 효력 인증 Gate 0**. 장비 추천/전체 장비 DB/신규 탐색기 개발 금지.

## 이미 통과한 기능 — 연구를 재개하지 말 것

- **실 ZERO-SOURCE v567 / Windows Chrome v570**: 원본 G/J/F/O→v212 설치→기존 v113 사용 DPS·95%·캐시 및 기본 사용자 64 DPS 성공. 범용 시즌 구축 **엔진 기능 PASS 인정**; 미래 미출시 시즌을 기다리는 재시험 금지. 새 시즌이 나오면 정상 데이터 갱신.
- **기존 v290/v291/v293**: 전역 분산·다중 스케일 탐색·실제 SimC DPS/SEM, Native JSON2, SHA 캐시·취소/재개, 기본 scout56/confirm320. 새 엔진/SEM 연구·26 DPS 전수 Native 금지.
- **E/O·수동 T**: v530~v534 정확 반지1 세 마부와 고정 E Native 사례, v578~v581 실제 기름 O32·T3500/B3468·DPS 2후보·재개·cache-only 통과. **v581 95% 우위 미확정**, 전역 최적 증명 아님.
- **마부 원본/분류 v582~v585**: Wago↔SimC 후보 38/38과 정확 쌍 76/76, 나머지33→전투 장비16/전문기술12/미확정5, 전투 장비 최상위 원본 등급 후보8, 그중 5/8 원본 계수 비감소. 이 수치는 **현재 70783 관측값**이며 동일 효과·실제 수치/최고 품질 사용자 등록 확정이 아니다. 동일 출처 캐시 재사용.
- **DK 룬벼리기 v294/v295/v586/v587**: **SimC DK 클래스 원본 전용 영구 무기효과**, 7종(현재 고정 소스); 이미 주·보조무기 선택·enchant_id·UI/세션 경로 존재. 새 시즌은 설치 v212 동적 SimC 룬 목록을 요구하는 보호 포함. **Wago/시즌 아이템/제작품질/고정 E Native 인증 불필요**. 신규 DK 실제 Native E2E 완료라고 과장하지 않음.
- **가장 최근 v587**: 기존 `v220.selected_equipment_source_mask_match`가 정확 선택 장비의 SimC class/InventoryType/subclass mask를 비교. [Actions #44233373988](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44233373988) **104 집중 offline PASS / 0 FAIL / Native0**. **하지만 아직 이 helper는 실제 동일 빌드의 `v230` 장비 메타데이터와 `v216/v196` 일반 사용자 선택 consumer에 연결되지 않았음.** 가짜 테스트 item metadata가 실제 사용자 옵션 승인은 아니다.

**공식 증거 경계:** `15/78 COMPLETE`, `full_product_e2e=PENDING`, 15/78은 구현률이 아님. 최근 Actions의 SUCCESS, 역사 CANCELLED/SKIP/FAIL과 실제 Native PASS를 구분.

## 지금 가장 중요한 단일 개발 작업

**일반 영구 마부의 소스·분류 결과를 실제 사용자 선택으로 승격하는 첫 단절을 최소 수정**하라. 첫 확인은 **기존 v216/v196의 선택지 producer가 실제 같은 빌드 봉인 `v230` 대표 장비 1개의 정확 metadata와 현재 `v220.selected_equipment_source_mask_match`를 호출하는지**다. 아직 연결되지 않았다면 기존 producer→consumer에 최소 연결. 그 뒤 필요한 경우에만 기존 `v220`의 source_relation/simc_input/product_input/chmv_budget, `v196→v212→v113` 공개, 정적 CHMV E 회계, SimC 프로필/세션·캐시 경계를 순서대로 수리. **마스크 일치 = 품질·E·Policy A 승인 아님**. 미검증 선택만 PENDING, 검증된 BASE G/J/F/O는 비차단.

영구 마부 전체 자동 구축은 최종 필수 기능이지만, **개별 항목의 효과·주문 구동 메커니즘 재현, 동등하지 않은 계수만으로 최고 품질 주장, 마부×26 DPS 전수 Native**, 새로운 인증 엔진·Wago 전수 재수집은 금지. 같은 효과/사용 조건의 최고 품질만 표시하고, CHMV 정적 E만 기존 측정/소유권으로 한 번 처리. 한국어 공식 이름이 없으면 원본으로 확인된 효과 설명. **Omnium Folio 같은 확장팩 특수모듈은 핵심 완성 이후 별도 작업.**

매 작업 전 **STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW**: (1) 사용자가 어느 지점에서 무엇을 못하는가 (2) 실제 차단 producer/consumer (3) 기존 기능/Native/캐시 재사용 (4) 추가 HTTP/DB2/Native·CPU/RAM/I/O와 회귀 비용 (5) 좁은 성공/STOP 조건을 밝힌다. 새 코드가 기존 현재 버전의 캐시·동일 빌드 소스를 재수집하지 않도록 한다.

## 첫 응답은 READ-ONLY 7항목 후 STOP

1. 실제 최신 HEAD 및 최근 Actions의 PASS/FAIL/CANCELLED/SKIP.
2. 목적과 실제 일반 사용자에게 가능한 구간.
3. v567/570 ZERO-SOURCE PASS와 영구 마부 전체 UI/선택 등록 미완료 경계.
4. v290+ 탐색·실제 Native/오프라인 테스트·관측 1순위 vs 95%/전역 최적.
5. 필수 미완료/선택형 PENDING/DK SimC-only/Omnium 후속 구분.
6. 비용 대비 다음 **작업 하나**, 기존 코드 재사용·STOP 및 추가 Native 필요성.
7. 미확인 증거/공식 15/78·full E2E PENDING/권한 경계.

**첫 응답 중 GitHub 코드·문서 수정, Actions/Native/HTTP/DB2 실행 금지.** 일곱 항목 보고하고 **STOP**. 사용자 별도 **`진행`** 이후 실제 최신 HEAD·사용자 첫 장애를 다시 확인하고 격리 브랜치 최소 개발. 별도 승인 없이 main 병합·v003 immutable 변경·원본 v016 직접 통합 완료 주장·Project Sources/Instructions UI 적용 주장·Work OS M0/Shared State 승격·78 요소 COMPLETE 임의 변경·기존 주 제품 개발 채팅 소유권 이전 금지.
