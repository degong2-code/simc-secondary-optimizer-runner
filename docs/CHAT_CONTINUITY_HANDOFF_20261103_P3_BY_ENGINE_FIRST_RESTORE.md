# SIMC SECONDARY OPTIMIZER · P3-BY · 2026-11-03 최신 새 채팅 인계 정본

**사용법:** 새 채팅에서는 이 **한 문서부터 시작**한다. 아래 링크를 정확히 읽고 GitHub의 **실제 HEAD/Actions/Native를 독립 대조**한다. **첫 응답은 복원 보고만 하며 사용자가 '진행'하기 전 코드 수정·새 Native·Actions 재실행·수집·추가 연구를 시작하지 않는다.** 인계 작성 시점의 branch base HEAD는 `77e0f0dfaaa659b302f6fc04c72274a358e6be94`; 인계 커밋 뒤 SHA는 변경되므로 **반드시 다시 HEAD를 조회**한다.

## 1. 권위·장기 제품 목표

- 최신 사용자 직접 결정 > 승인 [v1.4.3 시즌 G/J/F/O](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 및 비충돌 v1.4계열 > 실제 GitHub HEAD/코드/CURRENT/Actions/Native > 옛 인계·이력. 별도 첨부 v1.4.1의 **27 DPS/증강 포함** 문구는 역사 자료이며 **최신 26 DPS/증강·탱커·힐러 제외**가 우선. GitHub 문서 작성은 Project UI 적용/공식 Work OS 승격의 증거가 아니다.
- **제품은 시즌별 환경 구축 + 기존 적응형 SimC DPS 최적화 '엔진'**이다. 현재 장비 재분배/장비 획득·조합 추천/시즌 전체 아이템 DB/효과 엔진이 아니다. 기본 목표 ilvl334 또는 사용자 수동 **최종 T**에서 CHMV **최적 절대 rating**, 95% DPS·SEM, 관측 1순위/확정 여부, 실질적으로 다른 근접 대안·비율을 제공한다. SimC가 proc·특수효과·APL·DPS를 계산한다.
- 사용자에게 전체 장비 선택을 요구하지 않는다. 직업/전문화·종족·특성·목표 레벨/수동 T·장신구2·선택 특수장비/장식 최대2·소켓/보석·소모품/기름·전투조건을 입력받고 내부 대표 일반 장비·무기·4티어·주스탯/SimC 프로필을 만든다. 특수 확장팩 콘텐츠는 별도 ON/OFF 모듈.
- 기본 회계: `G = 목표 ilvl 대표 일반장비/무기의 정적 CHMV`, `J = 실제 일반 복합보석 정적 CHMV`, `F = 최고 품질 영약 고정 CHMV`, `O = 선택 무기 기름 고정 벡터`; `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. 수동 최종 T 최우선. 선택 특수장비 L은 G 안에 한 번 포함하고 하한 보호, E 정적 마부 중복 가산 금지, 장신구 정적 스탯은 자유 G 밖. O는 `gear_*`에 **한 번만** 반영. G는 **장비 전체 합계**를 ilvl별 nearest10 half-up 표준화, J/F/O 개별 정밀값은 별도로 유지.
- 일반 장비 G는 **현재 시즌 아이템 소속을 필수 인증 Gate로 하지 않는다**. 슬롯·ilvl·재질·주능력치/무기 형태·특수효과 없음·Native 정적 합계가 중요하며 시즌 아이템 우선은 대표 SimC 안전 선호. 정확한 티어/특수장비의 실제 ID·효과는 별개.

## 2. 복원 순서 — 읽기만 수행

1. `degong2-code/simc-secondary-optimizer-runner` 실제 branch `probe/chat-cache-v035-20261024` 및 `main` HEAD를 독립 조회. 사용자 승인 권한과 보호 범위 확인. **다른 채팅으로 개발 주도권 자동 이전 금지**.
2. [개발 성과 선조회 PROTOCOL](development/PROTOCOL.md) → [기능별 INDEX](development/INDEX.md)에서 해당 키워드/Capability 검색 → [P3-BY 이번 작업 노트](development/notes/2026-11-03_p3-by-continuity-handoff-gem-sockets.md) → [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) → [개발자 실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md). 기존 [P3-BQ 인계](CHAT_CONTINUITY_HANDOFF_20261103_P3_BQ_EVIDENCE_FIRST_LEDGER.md)는 역사적 재사용 규칙 참고, 최신 상태로 오해 금지.
3. 필요한 범위의 원본만 탐색: [P3-AQ](P3_AQ_20261102_TIER_TOKEN_BASE_ILVL_SOURCE_PROOF.md), [P3-AR](P3_AR_20261102_RAID_BONUS_TREE_TIER_SEASON_CORROBORATION.md), [P3-AT](P3_AT_20261102_NORMAL_SIMC_SOURCE_INTEGRATION.md), [P3-BR](development/notes/2026-11-03_p3-br-tier-evidence-reuse.md), [P3-BT](development/notes/2026-11-03_p3-bt-normal-build-standard-budget-link.md), [P3-BU](development/notes/2026-11-03_p3-bu-generic-g-physical-not-season-gate.md), [P3-BW](development/notes/2026-11-03_p3-bw-simc-json2-effect-rating-delta.md), [P3-BX](development/notes/2026-11-03_p3-bx-simc-socket-native-contrast.md). 기존 증거가 있는 부분에 새 인증·재수집을 자동 추가하지 않는다.
4. 코드 필요한 함수만 조회: `v216` 단일 Environment Build / `v222,v262` G/B/T / `v232-234` 대표 물리 일반장비·Native G / `v261` 13×5 티어 재사용 / `v098,v101,v108,v135,v139` 실제 gem·4색/고정 소켓 구식 경로 / `v091-093` O 일회 회계 / `v198-201,v269` 기존 SimC stat delta / `v270` Native 소켓 반례 / `v094-097,v015-016` 기존 adaptive/원본 상태. 전체 재감사 금지.
5. 관련 **실제 Actions/Native 영수증**과 코드 연결 범위 독립 확인 → 첫 응답에는 **현재 HEAD·인계/메인 분리·완료/미완료/병목·단기 및 장기 로드맵·기존 증거 재사용 판정**만 보고 후 중단. 사용자 '진행' 전 개발/실행/새 연구 없음.

## 3. 재사용할 확립 근거와 범위 (새로 증명하지 말 것)

| 기능 | 원본·기존 증거 | 이미 가능한 것 | 미완료/증거 한계 |
|---|---|---|---|
| 티어 시즌 식별 | [P3-AQ/AR/AT](P3_AT_20261102_NORMAL_SIMC_SOURCE_INTEGRATION.md); 같은 빌드 S1 197×65, S2 219×65, 활성 레이드 101/118, 13직업×5 ID/2·4세트 SimC 일치 | v250/251 및 v261→v216 정상 Build로 source 재사용 | 이것만으로 실제 26 DPS profile·numeric G/READY 통합 완료 아님 |
| 일반 대표 G | [P3-BU](development/notes/2026-11-03_p3-bu-generic-g-physical-not-season-gate.md); v232→233→234→216 | 현재 시즌 소속 미확인도 **물리 조건 충족 시** Numeric G source 활용 가능; 합계 nearest10 | 목표 ilvl별 실 G/선택 특수효과 E/L의 실제 수치 공급 일부 미완료 |
| 예산·기름 | `v091,v092,v093,v222,v262`, [P3-BT](development/notes/2026-11-03_p3-bt-normal-build-standard-budget-link.md) | `B=G+J+F`, `T=B+O`; 정확 O 손별 처리, `gear_*` 한 번 주입, 수동 T 및 L/E | **기름 회계 재구현 불필요**; 신규 시즌 정적 oil 벡터/옵션 원본 공급 필요 |
| 보석 4색 효과 | `v098,v101.ensure_representative_gem_colors,v135,v108,v139` 및 해당 테스트 | 특수보석 `240983` 주능력치 +32, `240967` 주능력치 +23과 보석 색상(가넷/자수정/라피스/페리도트)별 치명타 피해 +0.15%, 최대 +0.6%; **기존 v101 4색 실제 ID 구성** | v101은 일반보석 정확히 6개, v139은 특수보석 **머리**에 고정, v108은 J=138 고정; 가변 소켓/특수 장비 슬롯과 **최종 실사용 연결 미완료** |
| 실제 소켓 허용 | [P3-BX 실험 #41601140696](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696), v270 | SimC 원본 `socket_color[]` 기본 소켓, 실제 variant `ITEM_BONUS_SOCKET` 추가 소켓 식별. 1소켓 보너스 13750 관측 | **Native 4/4에서 무소켓 가슴 + gem_id=240906도 +16 Crit/+8 Haste**. SimC가 효과를 적용한다고 게임 내 유효 소켓이라는 증거 아님 |
| 보석 원본 +16/+7 | 사용자 첨부 최근 검토는 보석 `240906` 원본 +16 Crit/+7 Haste(합계23) 보고; v108 J=6×23=138 역사 회계 | 현재 목표는 단일스탯 보석 제외, 최고 품질 **복합보석만**·특수보석 하나 실제 장착 | Native Frost Mage snapshot +16/+8(+1) 원인 **미확정**. 이것을 24/보석으로 임의 승격하거나 특성/반올림 원인 확정 금지. 필요한 해당 보석 원본 효과만 최소 대조 |
| SimC 스탯 실측 | 기존 `v198~201` Ring E 실 Native delta +30, `v269`·`v216` 소비품 두 JSON2 입력 | 실제 SimC 계산 결과를 옵션별 source-only 후보로 읽음 | 최고 품질 F/J/O의 실제 새 시즌 수치·조건과 정책 A 등록/회계 최종 연결 미완료 |
| CI·연속성 | [Actions #41601682781](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601682781) | 오프라인 focused **38 PASS/0 FAIL**, ledger PASS at pre-handoff HEAD; 공통 workflow 자동화 | 26 DPS 제품 E2E/새 시즌 값/Native 효과 전수 증명 아님. 인계 문서 커밋의 CI는 별도 확인 |

**사용자 최신 보석 의사결정:** *제로베이스 시즌 환경*에서 소켓 수를 미리 6/7로 고정하지 않는다. SimC 기본 아이템/정확한 bonus 소켓 정보와 시즌 소켓 추가 수단(역사적으로 머리·허리·손목 각 +1 기본)을 참고하여 **사용자가 슬롯별 소켓 수/최종 개수를 자유 입력·수정**할 수 있게 한다. 특수보석은 정확히 **하나 반드시 SimC 실장착**(주능력치/치명타 피해는 GJFO CHMV로 재귀속하지 않음). `240967`을 최고 색상 효과로 쓰는 경우 **서로 다른 4종 일반 복합보석 각각을 실제 SimC에 장착**한다. 일반 최고 품질 복합보석은 소켓수에 따라 `J = Σ(실제 CHMV 일반보석)`을 계산한다. 보석의 물리 ID/색상은 실제 효과용이고 `gear_*` CHMV 목표는 자유 최적화; 고정 J 예산과 물리 구현 가능성은 구분한다. 총 소켓 5 미만 등 색상 요건에 못 미치면 임의로 4색 최대 효과를 주장하지 않는다.

## 4. 미완료·병목과 우선순위

- **연결 미완료:** `v216` 시즌 원본→대표 G + 유효 티어/보석/J/영약 F/기름 O→`v222` B/T→검증된 최고 품질 옵션 **정책 A 자동 발행**→최종 사용자 프로필/기존 적응형 SimC(95%, 캐시/취소/재개) **하나의 정상 제품 경로** 미완성. v016 원본 제품의 실제 바이트·영수증과 직접 통합도 미입증; GitHub 격리 시험 PASS를 원본 통합 완료라고 표기 금지.
- **실제 부족한 증거:** 신규 시즌의 J/F/O 품질별 정확 rating·적용 조건과 대표 ilvl별 G 유효 수치, 소켓 추가 수단의 **허용 부위**(SimC gem_id 강제 성공만으로는 확인 불가), 240906 원본 +16/+7 대 `buffed_stats` +16/+8 원인(정확 +1). 이미 알고 있는 4색 효과·기름 산술·13×5 티어는 증거 부족으로 재분류 금지.
- **효율적 단기 로드맵:** (1) **재사용 누락 제거**: v101 4색 실제 장착+특수보석 하나·기존 v091~093 O 회계 소스 연결 → 사용자 지정 슬롯별 소켓 수, 실제 SimC gem ID 및 n-1 일반보석, 역사 J=138 가정만 제거. (2) 실제 원본/최소 SimC 관측으로 필요한 최고 품질 J/F/O·ilvl G를 적응형 회계에 제공, +1 차이 좁게 확인. (3) 기존 v216→v222→v212/정책 A→사용자 프로필/기존 적응형 SimC의 **한 정상 Build** 연결, 필요한 부분만 focused 테스트 및 실제 최소 Native. (4) 실제 사용자 1개 시나리오 E2E 성공, 이후 26 DPS 사용 범위를 점진 확대.
- **장기 로드맵:** 26 DPS에서 재사용 가능한 시즌 변경/제로기존자료 Environment Build, B/T 자동 갱신·최고 품질 옵션, 95% 통계·의미 있는 근접 대안, 캐시/취소/재개·경량 UI/원클릭. 새 최적화 엔진, 모든 시즌 장비 DB, 불필요한 전수 Native/독립 proc 인증 Gate 금지.
- **반복 병목 예방:** (a) 옛 P3 기록의 시점별 `PENDING`을 원본 증거 없음으로 오해하지 말 것, (b) 원본 값과 SimC 캐릭터 snapshot 델타를 동일 rating으로 단정 금지, (c) History receipt PASS, 이번 신규 CI PASS, synthetic/local PASS, Native 4회, 제품 E2E/READY를 정확히 분리, (d) GitHub push가 많으면 코드·테스트·문서 **한 논리 묶음/한 CI 결과** 우선.

## 5. 인계·권한·다음 채팅 정지 조건

- **실제 반영:** 이 인계 파일, 최신 노트, PROTOCOL/INDEX, CURRENT, 개발자 실행 노트는 격리 브랜치에 작성/업데이트. URL 하나로 복원. 기존 승인 v1.4.3 본문·v003 immutable·main·원본 v016/실제품·Project Sources/Instructions UI·Work OS M0/Shared State는 **미수정/미승격**. GitHub에 썼다고 Project UI 등록 성공을 주장하지 않는다.
- **인계 준비만 수행:** 이 작업 자체는 소켓/보석/회계 구현·새 SimC Native·게임 원본 HTTP 수집을 시작하지 않는다. 인계 작성 후 HEAD/오프라인 CI 상태를 보고한다. 새 채팅은 HEAD/자료/영수증 독립 검증·복원 보고 후 **사용자 '진행' 전에는 읽기 외 아무 작업도 수행하지 않는다**.
