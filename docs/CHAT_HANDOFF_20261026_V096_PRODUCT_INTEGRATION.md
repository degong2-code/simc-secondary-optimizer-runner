# SIMC SECONDARY OPTIMIZER — 새 프로젝트 채팅 인계 / v096 PRODUCT INTEGRATION

**작성일:** 2026-10-26 KST
**분류:** 개발 지속성 인계 및 정확한 Boot 기준. 이것은 Project Instructions나 공식 Work OS를 자동 변경하는 문서가 아니다.
**프로젝트:** SSfindout / SIMC SECONDARY OPTIMIZER
**실제 코드 authoritative repository:** https://github.com/degong2-code/simc-secondary-optimizer-runner
**계속 개발할 격리 브랜치:** \`probe/chat-cache-v035-20261024\`
**인계 직전 확인한 커밋:** \`283ef05615e3b644844cdb7cebf324415478b51e\`
**보호할 main 커밋:** \`07133e0aaf738d6e4816a6486057b1cd49c018de\`
**최신 상태:** [docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md](./CURRENT_PRODUCT_DEVELOPMENT_STATE.md)
**직전 완료 v096 보고서:** [docs/V096_PRODUCT_BASELINE_DRIFT_ROOT_CAUSE_AND_UNIFIED_ENTRY_ACCEPTANCE.md](./V096_PRODUCT_BASELINE_DRIFT_ROOT_CAUSE_AND_UNIFIED_ENTRY_ACCEPTANCE.md)
**v096 CI:** [Actions #40271512368](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40271512368) **SUCCESS; 545 tests = 543 PASS / 2 SKIP / 0 FAIL; zero SimC calls**, artifact ID \`12628432935\`, GH artifact digest \`b9dd47bca288f07c32840e9d6ac734f0712cae893986c71c95bcee168917f41f\`.

## 0. 새 채팅 시작시 반드시 구분할 사실

1. **공식 승인 정책**: 사용자가 2026-10-26에 직접 **\`T=G+J+F+O\`** 및 해당 Project Sources / Work OS 정책 변경을 승인했다. \`B=G+J+F\`는 기존 기본 분배 예산, \`O\`는 실제 기름 바른 무기 한 개당 **치명 +16 / 가속 +16**, **절대 재배분 금지**. \`c_final=c_base+o\`. 기본 334 공통 **B3150/T3182(1기름)/T3214(2기름)**, Fury dual 2H **B3350/T3414(2기름)**. **95% 판단만 유지**; 사용자가 97% 표시 불필요하다고 확정해 v095에서 제거했다.
2. **설계 정본**: \`SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.3_APPROVED_OIL_INCLUSIVE_PROJECT_SOURCE_REPLACEMENT.md\`가 사용자 승인된 정책 **내용**의 기준이다. 역사 v1.2의 \`T=G+J+F\` 기름 제외 설명보다 우선. 하지만 **ChatGPT Project Sources 실제 업로드/Instructions의 v1.2→v1.3 문구 갱신은 확인되지 않음**. Source v1.3은 정적 설계 문서이며 자체 개발 상태 표에 v059/v092 시점의 오래된 줄이 있다. **개발 최신은 GitHub CURRENT 및 Actions/원본 Native 영수증**을 우선 확인하라. 지침 충돌 시 사용자 확정 2026-10-26 정책을 보존하고 충돌을 명시한다.
3. **제품 원본 기준**: 사용자 보고한 **v016_SCENARIO_CONTRACT**; 원본 v015/v016의 실제 바이트/영수증을 독립적으로 받아 완전 통합했음을 뜻하지 않는다. 격리 v096 PASS = 원본 제품 full merge PASS 아님.
4. **공식 Work OS**: \`M0_STAT_INJECTION_FEASIBILITY\`는 운영 Gate다. 새 제품 개발을 금지하거나 과거 코드를 폐기하는 Gate가 아니다. 공식 외부 Windows Shared State/CURRENT/Project UI 적용 완료 영수증은 현재 **없다**. 승인과 실제 Apply 완료는 분리한다. v003 immutable, main, 보호 원본, official Gate status 조작 금지. 이 승인된 산식 건의 반복 MAIN 사전승인 요구는 없다.
5. **최근 최우선순위 수정**: 사용자가 지적함. 이미 많은 전문화에서 Native 실증했는데 매번 '범용성 첫 검증' 또는 특정 Fury의 SEM 세부 조정만 다음 과제로 삼은 건 잘못된 로드맵. **이제 최우선은 기검증 코드를 실제 제품 입력→실행→결과의 하나의 경로로 통합**. 불필요한 전 전문화 재시험/정밀 iterations/전용 proc Gate를 만들지 말라.
6. **역할 분리**: SimC가 장비·장신구·장식·보석 효과, APL, proc, DPS 전체 계산. 프로그램은 정확한 ID/ilvl/options와 combat 입력, 정적 B/L/O, 중복 스탯 삽입 방지, JSON2 정합, 후보 탐색, DPS/SEM, 캐시/재개 담당. 신규 장비 추천/파밍/시즌 장비 DB 범위 확대 금지.

## 1. 기검증 전문화 / 이미 있는 진짜 Native 증거

- **잠행 도적**: v069-v075; v071 v015-derived 1 scout 실제 Native + SHA cache. 구형 부분 FAIL이 있으면 PASS로 덮지 말고 올바른 receipt 범위만 재사용.
- **정기 주술사** (사슬/지능/한손+방패): v078/v078B, v085 SHA re-audit; 실제 두 증인+3 공식 후보(scouter 포함) Native.
- **야수 사냥꾼** (사슬/민첩/원거리, offhand 없음): v079 원본 talent-inflated buffed-stat 역산 결함은 v080-v081 **정적 c와 buffed_stat 분리로 교정**. v086 랜덤 2차스탯 아이템 2개를 fixed-secondary 대표 머리/발로 교체·실제 G Native. 역사 FAIL/affine evidence를 새로운 PASS로 오인하지 말 것.
- **분노 전사** (판금/양손쌍수): v082/092~095 실제 Native. 공식 O 포함 정적 rating과 B→T Native 적응형·다른 대안 실제 5건·SHA cache.
- **징벌 성기사** (판금/단일 양손): v083 actual 4 Native & adaptive scout.
- **냉기 마법사** (천/한손+비무기 보조): v084 actual 4 Native & adaptive scout. v096 동일 단일 manifest 사전 검증; **v096 자체 Native 새 실행 0**.
- 역사 검증은 동일 조건의 범위에 한정. **전 전문화·탱커·힐러 모두 이미 PASS라고 확대 주장 금지**. 단지 이미 실증한 구조를 처음부터 재시험하지 말 것.

## 2. 진행 상태와 실제 증거 계보

- **v091**: 전술 기름 0/1/2를 SimC에 명시 전달. 기존 \`gear_*\`가 오일 rating을 덮어쓴 사실을 실제 Native로 확인.
- **v092**: 사용자 승인 공식 \`T=B+O\`; gear override에 고정 O를 **정확히 한 번**, 자유 B 및 특수 장비 잠금 L 보존. 기름 0/1/2 Native 3350/3382/3414 실제 rating. [CI #40260947724](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40260947724) 522PASS/2SKIP.
- **v093**: v065 v015-derived 선택은 B, Native는 T=B+O, 검증 후 탐색용 B 투영. 2 initial + 1 scout + 2 independent confirmations actual 5 Native; identical 5 SHA cache hits; [CI #40262903998](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40262903998) 527PASS/2SKIP.
- **v094**: prepared-context 공통 durable CLI, cache-only, cancellation **새 Native 호출 전**, bounded call limit, session sealing/progress; actual 2 seed + 2 confirmation Native, cache 4 hits. [CI #40266550555](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40266550555) 532PASS/2SKIP.
- **v095**: 사용자가 95%만 유지, 97% 비교 전면 제거. 기존 v065 neighbors로 CHMV B 10% 이동한 실제 대안: 334 Fury **T3414, 335 rating 이동, 관측 최고대비 DPS 0.862% 하락**, 95% 근사에서 열세로 구분. Actual 5 Native + SHA replay 5 cache hits; [CI #40268656884](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40268656884) 538PASS/2SKIP. **제품 전역 최적해 검증 아님**.
- **v096 최신**: [runner/v096_unified_product_entry.py](../runner/v096_unified_product_entry.py) 는 **하나의 사용자 JSON manifest** (실제 SimC profile, typed scenario, filler, optional same-season static cache, layout/oil, F, B seeds, SimC revision/binary, Native cap, result dir)를 기존 v091/093/094로 전달. \`--plan-only\`은 Native0, \`--cache-only\`은 SHA verified cache만, 기본 실행은 기존 common Native runner 위임. source-locked 334 Fury 2H/oil2 B3350→T3414 및 Frost 1H/frill/oil1 B3150→T3182를 같은 entry preflight로 검증. **[CI #40271512368](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40271512368) 543PASS/2SKIP**, new Native 0. **새 CLI 실사용 전체 제품 완료 아님**.
- 정적 아이템 캐시 \`v046\`는 동일 시즌 SimC revision만 바뀌어도 폐기하지 않는다. DPS 케이스 캐시는 revision/bin/source/inputs/stats/oil/iteration/combat identity로 분리. SimC 오류는 그 자체로 보고, 효과 기전 독립 구현 금지.

## 3. 다음 정확한 개발 작업 (v097 가칭; 번호 자체 중요하지 않음)

**P1 / 이어서 구현:** 새 v096 단일 manifest entry의 **남은 실제 제품 입력 경로 연결**.
- v096은 현재 **옵트인 ilvl 레퍼런스 B** 경로에 제한. 실제 Native에서 얻은 exact G 기반 \`B=G+J+F\` 경로, 사용자 수동 **기름 포함 최종 T**를 레거시 v061 B로 명시 변환하는 v092 adapter 경로를 v096에 연결할 때 사용자 옵션이 서로 섞이거나 이중 O 가산되지 않게 한다. 단위/계약 테스트를 먼저, 진짜 새 결함 부분만 최소 Native.
- 이미 테스트한 전문화/무기/APl/효과를 다시 처음부터 Native로 돌리지 말라. 기존 v061/v062/v065/v091-v096을 재사용하되 1개 공통 input→execution→results 인터페이스로 묶어라. 단계별 리소스/시간·중복 SimC 호출/메모리·I/O/코드 수를 매 변경 검토.
- 기존 v015/v016 **원본 바이트와 실제 영수증을 확인**해야 원본 제품 완전 통합이라고 판정. 확보되지 않으면 격리 통합을 제품 원본 merge로 표기 금지. 사용자 일상 Windows/PyCharm 실행 경로(일괄 설정·진행·취소·결과 폴더) 개선은 원본 통합 계획에 맞춰 진행.
- Semantics: **관측 DPS 최고를 1순위로 표시**, 95%에서 차이 불확실하면 근접 후보를 보존. 적응형 high-iteration refinement는 전체 UI 및 핵심 기능 통합 뒤로 미룸.
- 실제 Project Sources v1.3·Instructions·Work OS는 사용자가 이 변경을 승인했다. 다만 **정확한 실제 target 원본/권한 확인 없이 적용 완료 주장 불가**. 접근되면 승인 범위만 갱신·영수증 보존, 그렇지 않으면 파일/명확한 UI 적용 지시 제공.

## 4. 새 채팅 Boot 안전 절차

1. 이 인계 문서만 읽고 PASS라고 주장하지 말고, 실시간 GitHub 격리 브랜치 HEAD, \`docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md\`, v096 코드/테스트/CI 영수증, 중요 원본 Native evidence를 **직접 열고 교차확인**.
2. 프로젝트 v1.3 전체 교체본을 읽고, Project Instructions의 구형 v1.2 참조가 있으면 사용자 승인된 v1.3과 충돌로 보고한다. GitHub의 공식 원본/실측 사실을 구분한다.
3. 새 채팅에서 ZIP local filesystem은 이어지지 않을 수 있다. 동일 바이너리 SHA \`64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e\`, SimC rev \`7bc10711b5\`를 검증하기 전 '현재 환경 그대로'로 주장 금지. ZIP 속 portable sources/evidence를 사용하고 캐시 identity를 확인한다. 원본 v015/v016가 필요하면 별도로 사용자 제공 또는 확인 가능한 source fetch.
4. 기존 공식 파일·v003·GitHub main·원본 제품을 건드리지 않고 **기존 주 제품 개발 채팅 소유권**으로 격리 브랜치에서 이어서 개발. 새 대화 생성 자체는 새 MAIN/WORK 자동 승격이 아님.
5. CI PASS와 real Native PASS 및 offline synthetic fixture 차이를 구분하고, 실제 파일/원본 바이트 없는 부분을 미검증으로 표시.
6. 첫 응답에서 **Boot 점검 + 현재 제품 전체 진행 위치 + 가장 가치 있는 다음 통합 작업 1개**를 짧고 정확히 정리한 후 이어서 수행. 반복적인 상세 질의 없이 이미 결정된 정책 준수.

## 5. 출처 및 기준점

- 사용자 승인 v1.3 파일명: \`SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.3_APPROVED_OIL_INCLUSIVE_PROJECT_SOURCE_REPLACEMENT.md\` (로컬 승인 정책 문서이며 UI 적용 미확인).
- [v096 실제 개발 보고](./V096_PRODUCT_BASELINE_DRIFT_ROOT_CAUSE_AND_UNIFIED_ENTRY_ACCEPTANCE.md)
- [전체 현황](./CURRENT_PRODUCT_DEVELOPMENT_STATE.md)
- [v095 Native 영수증](../integration_probes/data/v095_material_95_five_real_native_receipt.json)
- [v094 Native 영수증](../integration_probes/data/v094_durable_inclusive_four_real_native_receipt.json)
- [v093 Native 영수증](../integration_probes/data/v093_inclusive_B_to_final_T_five_real_native_receipt.json)
- [v092 Native 영수증](../integration_probes/data/v092_approved_T_GJF_plus_O_native_compact_receipt.json)
- [v096 Actions run](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40271512368)

**인계 생성 사실 ≠ 새로운 제품 실행/Native PASS. 사용자 최종 목표는 모든 전문화 DPS 최적의 CHMV 절대 rating·SEM·의미 있는 대안이지 장비 DB/기름 효과 인증이 아니다.**
