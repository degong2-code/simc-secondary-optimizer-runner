# SIMC SECONDARY OPTIMIZER — 개발자 노트 v1.4.2 보충본 (2026-10-30)
## 사용자 최신 결정·실제 v182 구현 증거·차기 작업

**지위:** v1.4.1 전체를 무단 대체하지 않는 **최신 사용자 직접 결정의 버전형 보충본**. 승인된 CHMV/SimC 책임 원칙 유지. GitHub 개발 브랜치에 기록한 것이며 **ChatGPT Project Sources/Instructions UI 실제 적용이 아님**. v1.4.1에 남은 27 DPS/증강 포함 문구는 구형 역사 표기다.

### 1. 결정 우선순위 / 제품 목적

**최신 직접 사용자 결정 > 승인 설계 기준(충돌 없는 부분) > 이 격리 브랜치 최신 CURRENT·HEAD 및 실제 Actions/Native 원본 > 기존 역사 인계/실험 문서.**

- **26개 DPS 전문화(증강 기원사 제외)**만 지원. 탱커/힐러도 제외한다. 사용자가 이후 직접 바꾸기 전까지 27개로 복귀하지 않는다.
- 목표 **ilvl 266–344, 기본 334** 또는 **사용자가 입력한 기름 포함 최종 CHMV T**에서 향후 파밍 목표가 될 **치명·가속·특화·유연의 최적 절대 rating**을 실제 SimC DPS로 찾는다. 현재 착용 장비 스탯 재분배기, 아이템 조합·획득 경로 추천기가 아니다.
- 일반 사용자는 직업·전문화·종족·특성, 목표 ilvl 또는 수동 T, 시즌 **장신구 2개**, 선택 **특수효과 장비**, **장식 제작장비 최대 2개(부위·장식 유형·제작 스탯 선택)**, 보석/영약/물약/기름/전투조건만 고른다. **일반 방어구·무기·티어 4세트·대표 프로필과 시즌 예산은 내부 생성**. SimC 프로필 업로드는 캐릭터/특성 읽기 선택 기능이며 장비 스냅샷을 목표로 복사하지 않는다.
- **`T=G+J+F+O`, `B=G+J+F`, `T=B+O`, `c_final=c_base+o`.** 기름 O는 정확한 적용 무기마다 고정·gear_*에 한 번만. 선택 특수장비 정확 정적 L은 B/G 내부에 이미 있으므로 스탯별 하한으로만 보호하고 재가산하지 않는다. 장신구 정적 수치는 자유 G 밖, JSON2 record 미출력은 0 단정 아님. 제작 초기 50:50은 L 잠금이 아니다. 참조 B(시즌 79×2 Native 기반 10 단위 근사) 또는 수동 최종 T가 기본; 선택 exact Native G는 기본 경로 필수 Gate가 아니다.
- **95% 판정만 사용**. 관측 DPS 최고와 확인 후보의 95% 통계적 우위 및 전역 최적해 증명은 서로 다르다. SimC가 장비·proc·APL·DPS를 계산한다. 별도 효과 인증 Gate/독자 계산 모델/신규 최적화 엔진을 만들지 않는다.
- 시즌 DB는 **다른 프로젝트/WEQUIP를 시드로 하지 않는 zero-seed**. Blizzard·WCL API 시즌 식별, 동빌드 wago DB2, Localbots 새 시즌 구렁 및 wago ID 확정. 현재 선택용 511 후보와 65 티어 IDs의 유효 범위만 유지하며 사용자에게 일반장비 후보 조회를 제공하지 않는다. 매 시즌 Wowhead 79 대조 반복/79 하드코딩 금지.

### 2. 최신 사용자 UI 결정 (v182, 2026-10-30)

1. **무기 기름:** 보조무기가 없거나 기름을 바를 수 없는 무기 구성(예: 냉기 마법사)의 보조무기 기름 체크 불허·자동 해제. 무기 형식은 기존 전문화/장비 계약으로 판단하고 기름 O를 중복 계산하지 않는다.
2. **특수효과 장비:** 사용자가 `bonus_id` 또는 `catalyst_origin_id`를 이해/입력하도록 강요하지 않는다. 일반 UI는 시즌 유효 아이템 목록과 이해 가능한 선택지만 보이며 내부 정확 옵션/identity는 유지한다.
3. **장식 제작장비:** 일반 UI에서 제작 `item_id`·`bonus_id` 직접 입력을 없애고 **부위, 장식 유형, 제작 2차 스탯 2종**만 고르게 한다. 내부에서 현재 시즌 정확 제작 아이템 ID/옵션을 구성한다. 이번 구현의 옵션 범위는 증거가 확보된 장식 유형에 제한되며 모든 제작장비·장식 전수 지원 주장 금지. 구형 API의 내부 정확 ID 호환 유지와 일반 UI의 입력 금지는 별개.
4. **옴니움:** 원문 숫자 5열을 드롭다운에 노출하지 않고, DPS에 영향이 있는 **4열 치명/가속/특화/유연 4개** 중 하나를 고른다. 나머지 열은 고정 원본 토큰, SimC 검증된 실제 rune ID 사용. 유연 초기 이름 토큰 오류는 `136820:1`로 수정(v182 후속 Native).

### 3. v182 검증 실물 및 한계

- HEAD/날짜는 매번 조회; 최초 보충 작성 시 HEAD `c32ae1625299e18e3fd37f61d3110105caed5e84`.
- v182 UI [Actions #40986181287](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40986181287): Windows+Ubuntu 두 환경 PASS, 환경별 **신규 4 tests + 기존 51 tests + 배포 2 tests**; Windows 실제 ZIP 추출/CMD/HTTP 계획 복원, **Native 0**. ZIP [artifact #12946803072](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40986181287/artifacts/12946803072), 7일 보존.
- 로컬 Web API [#40986181309](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40986181309) Windows·Ubuntu SUCCESS; 기존 v098 focused [#40986181282](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40986181282) **363 tests PASS**.
- **v182 Native 6개 초기 [#40985573830](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40985573830): 5 PASS, 1 FAIL**. 4열 치명·가속·특화 및 제작 장식 `arcanoweave_lining`·`sunfire_silk_lining`은 SimC 물리 프로필 실제 수용 PASS; 유연 최초 `SIMC_NATIVE_EXIT_80` FAIL. 역사 FAIL 숨기지 않음.
- 정확 유연 source rune ID `136820:1` 교정 후 **유연 1건만 Native** [#40985987787](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40985987787) PASS. 이전 5개를 불필요하게 재측정하지 않음. 따라서 현 수정본의 선택 6종은 **5개 재사용+1개 신규** 물리 수용 증거이나, 각각 전체 적응형 6후보 최적화를 실측한 증거는 아니다.
- v176 26/26 기본 물리 PASS, v180 다른 ilvl 6세션/36 실제 최적화 PASS, v178 실제 취소/재개와 SHA 캐시는 각자 범위에서 재사용한다.
- **사용자 Windows 냉기 마법사 결과:** `V094_RESULT(20261030-005532).json` + `V106_USER_RESULT(10).json`에서 관측 DPS **158,716.232862584**, SEM **225.73157454188464**, `T=3182, B=3150, O=(16 치명,16 가속)`, 최종 rating `916/766/750/750`, 총 6 Native/고유 후보 4, **선택 두 확인 후보 간 95% 방향지지 true**이나 전역 최적해/다른 유망분배 배제 증거 아님. **낮은 DPS의 원인 미확정**. 이 두 사용자 출력만으로 실제 JSON2 티어 세트 효과, 장신구/proc/APL·무기·버프가 정상 적용됐다고 단정하지 않는다. **정확한 원본 JSON2·생성 profile.simc·SimC 로그를 확인**하고 효과·프로필 입력의 정합을 구분하되 독립 효과 Gate를 만들지 않는다. 사용자의 로컬 파일을 GitHub 공개 개발 상태에 복제하지 않는다.

### 4. 제품 완료 상태와 다음 단계

- **완료 범위:** v161/162 zero-seed 기반 수집→v171 511 시즌 후보→v176 26/26 기본 물리→v177 실제 첫 6후보→v178 후보사이 취소/재개→v179 입력 오프라인→v180 266–344 다중 레벨 130 plans + 6 실물 세션/36 Native & 36 cache→v181 Windows 소스 베타→v182 UI 4건 및 선택 6종 물리 수용.
- **남은 범위:** 사용자 Windows 실제 SimC 최종 베타 운영 검증, 저 DPS 원인과 실제 티어/효과/버프/프로필 항목 확인, 선택 제작/특수장비 exact L 및 옵션별 필요 최소 실측, 사용자 친화적 오류 표시, 사용된 시즌 장비 UI/캐시 정합성. v181·v182 소스 ZIP은 EXE 설치 프로그램이 아니다.
- 빠른 대안: **이미 받은 사용자 결과와 기존 원본 실측 우선 대조 → 실제로 미확인한 한 조건만 Native 최소 검증 → 필요한 UI/입력 결함만 수정 → Windows ZIP 재생성+focused 회귀**. 26-spec 물리/전 레벨/native 모든 옵션 전수 반복 금지.
- 모든 코드 변경마다 속도/Native 중복/API·CSV I/O/메모리/캐시 identity를 점검. 완료 구현/새 PASS·FAIL/재사용 역사 증거/미구현 구분. 제품 개발이 Work OS M0에 의해 막히지 않으나 `main`, v003 immutable, 원본 v016, Project Sources/Instructions UI 적용, Work OS 공식 승격은 **별도 사용자 승인**. GitHub CURRENT 수정 ≠ Project UI 적용.

**이 보충본과 최신 인계 문서는 프로젝트 UI 변경을 자동 수행하지 않는다. 사용자 직접 승인된 설계 해석에만 우선하며, v1.4.1 원본의 비충돌 정책은 계속 유효하다.**

## 5. 2026-10-31 v203 마부 회계 및 기존 기능 충돌 방지 — 후속 증거 보충

**현행 사용자 정책을 재확인:** 오직 **DPS 26개 전문화**, 증강 기원사·탱커·힐러 제외. 본문에 인용된 v1.4.1의 27개/증강 포함은 구형 역사 정책이며 이 v1.4.2와 최근 사용자 직접 결정을 덮어쓰지 않는다. 이 단락은 v1.4.1 원문·공식 Project UI를 수정하거나 새 승인 규칙을 발명하는 것이 아니다.

- **E의 위치:** 마부의 Native 관측 고정 rating `E`는 이미 목표 총량 안에 있는 `G`의 **비자유분배 스탯별 하한**이다. `T=G+J+F+O`, `B=G+J+F`는 불변. 기름 `O`, 특수장비 `L`, 보석 `J`, 영약 `F`와 별도 소유권을 지킨다. `E`를 총량이나 `gear_*` 숫자에 추가하면 이중 계산된다. 선택 특수장비/장식의 동일 슬롯 `L`·`E` 중복 잠금은 원자적으로 거부한다. 기존 후보 탐색·SimC APL/proc/DPS/95%·캐시/취소/재개 코드를 재발명하지 않는다.
- **정확한 증거/적용 범위:** [v199 #41075851509](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41075851509) Native2, [v200 #41076597270](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41076597270) 기존 JSON2 SHA 정정·Native0: `finger1 item158366/enchant8025` 가속 **1004→1034(+30)**. [v201 #41078102843](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41078102843) Native2: 동일 `gear_*` override 시 가속 **735→735(추가0)**. [v203 전체 적응형 #41083301873](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41083301873) Linux exact SimC rev `710c2408bf`/SHA·냉법334 대표 전체 프로필 SHA `8305a811137db6f557f8076dfa44a4a1a359111d60bb7452225e1573bf72a401`에서 **Native6 PASS, 캐시 재실행 6/6 HIT, 신규0, B3150/T3182, 고유후보4, 95% 비교**. 이 SHA 조건 외의 특성·종족·장신구·장비·전투·Windows SimC에는 E30 자동 재사용 금지.
- **v203 교정 네 경계:** 동일 반지 특수 `L`/제작장식 충돌 차단, Native v200/v201 원본 SHA와 artifact ID 고정·이상 시 원자적 거부, 전체 프로필 SHA 적용 범위 잠금, E 증거 누락/손상 시에도 기존 38종 마부 read-only 목록과 음식·물약 기능 보존. 사용자 Web/v106의 마부 선택은 **미승격**. Native 6+6 캐시 성공은 모든 선택 조합과 Windows 실측을 증명하지 않는다. 실제 마부 세션 **중간 강제 종료/부분 재개**, Windows exact binary, 다른 37종 마부는 별도 미완료.
- **검증:** [v203 Ubuntu/Windows 감사 #41084413183](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41084413183) 각 OS 21 단위 + 2 패키징 PASS; 이후 최신 HEAD `b2d727c7…`의 [Windows 소스 ZIP #41085651541](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41085651541), [UI #41085651522](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41085651522), [Web API #41085651503](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41085651503) PASS. 해당 HEAD의 v180 등 Native jobs는 **SKIPPED**이며 이전 실측을 재사용한 것; 신규 Native 실행으로 계산하지 않는다.
- **제품 효율:** 기존 시즌/정적 item 캐시를 SimC revision만으로 버리지 않는다. DPS 캐시는 바이너리·프로필/마부/옵션·전투조건·iterations identity로 구별한다. 독립 작업은 묶어 검증, 변경으로 무효화한 조건만 최소 Native 시험. 제품 코드/원본 v015/v016 직접 병합/공식 main·v003·Work OS·Project Sources/Instructions UI 승격은 별도 권한.

**증거 확장 상세:** [v203 감사와 정책 부록](V203_ENCHANT_8025_CROSS_FEATURE_AUDIT_AND_POLICY_ADDENDUM.md). **최신 상태는 항상 GitHub 브랜치 HEAD와 CURRENT 상단 우선**. 이번 GitHub 개발자 보충 갱신으로 ChatGPT Project Source에 실제 등록됐다고 판단하지 않는다.

## 6. 2026-10-31 사용자 직접 교정 — 선택한 정적 마부만 자동 참조 B/T 증가

**이 절은 §5의 'E는 항상 기존 G 내부이고 자동 B/T에 가산하지 않는다'는 결론을 정확히 한 부분만 교정한다.** 사용자가 실제 정적 2차스탯 마부를 고른 경우, 마부 없는 대표 프로필의 ilvl 참조 B에 해당 마부의 Native 검증 E를 한 번만 추가하는 것이 제품의 미래 파밍 목표와 일치한다. 마부를 선택하지 않은 경우 기존 79×2 참조 B·G/T·시뮬레이션/캐시/세션 정체성은 불변이다.

- **자동 ilvl 기준:** `B_effective=B_reference+sum(E)`, `G_effective=G_reference+sum(E)`, `T_effective=B_effective+O`. E는 새로 발생한 G 내의 **고정 스탯**, 재분배 금지. 기존 J/F/O/L 산술과 자유분배 floor를 유지한다. 기준표 값은 수정하지 않는다.
- **사용자 수동 최종 T:** 입력 T는 이미 기름과 실제 선택 마부를 포함한 공식 최종 총량이다. `B=T-O`, E는 B 내 잠긴 하한일 뿐 **T/B를 다시 증가시키지 않는다**. 작은 수동 총량이 E/L/F 등 고정치에 못 미치면 Native 전 차단.
- **숫자 주입:** 기존 SimC `gear_*` 덮어쓰기 특성상 후보에서 이미 포함된 E를 별도 더하지 않는다. 오직 후보의 변경된 `B_effective`와 `O`를 기존 한 번씩 적용하며 Native JSON2 최종 rating 정합을 확인한다.
- **엄격한 범위:** 지금 구현은 원본 v202/v203 증거의 **Linux 냉법334, 정확 전체 프로필·바이너리 SHA, finger1 item158366/enchant8025, E=가속30**이라는 개발용 선택 경로 한정. 다른 37종·Windows 사용자 마부 UI는 계속 미승격. 일반 사용자 `v106`에서 개발용 마부 필드 거부 유지.
- **검증 지위:** 코드/오프라인 검사 경로 추가는 새 PASS가 아니다. 과거 v203 `B3150/T3182` Native6·캐시6은 역사 증거이며 새 `B3180/T3212` 결과 증거가 될 수 없다. v204 오프라인 Ubuntu/Windows 및 최대 Native6+cache6의 새 영수증은 정확한 Actions 실물로 확인 후 별도 기록한다.
- **변경 영향:** 예산 소스/참조 증거, L/E/O 중복, candidate bounds, 시나리오 digest, profile/case/cache key, 강제 종료·부분 재개, 구형 세션 보존, Web/Windows 마부 선택 잠금, CI 비용·메모리/I/O·정적 캐시 불변을 한꺼번에 검토한다. 상세 `docs/V204_SELECTED_ENCHANT_BUDGET_IMPACT_AND_EVIDENCE.md`.

본 보충은 GitHub 격리 코드·문서에만 적용됐다. 공식 v1.4.1 원문·ChatGPT Project Sources/Instructions·Work OS·main·v003 immutable 승격과 무관하다.

### v204 검증 영수증 (2026-10-31)

- 오프라인 양 OS [#41099416253](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41099416253) Ubuntu/Windows 각 36 PASS/0 FAIL; 테스트 대상은 자동 일회 증가, 수동 T 불변, 원본 참조표 불변, 기존 v089/v091/v096, E 하한, 미관측 마부 잠금/특수 L 슬롯 중복 차단. 초기 [#41099272753](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41099272753)에서 신규 오프라인 fixture가 기름 없는 정규화 시나리오에 O=16을 넘긴 **테스트 구성 오류**로 1 FAIL; 수정 후 36/36 PASS. 역사 FAIL 삭제 금지.
- 신규 Linux Native [#41099779751](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41099779751), Source HEAD `91c9d1c05cb715828f92e5f26837599353014f69`: 정확한 SimC 바이너리 SHA`f105b8a34fd911c340e735f0440e0d1eadf0d0dbc25f18923c048810cf69095d` 확인. `B=3180,T=3212,E_haste=30`, **신규 Native6 PASS, 4개 고유 rating**, 동일 결과 6/6 Native JSON2 SHA-검증 캐시 replay, 추가 Native0, 신뢰수준 95%, 전역최적해 입증하지 않음. 원본 artifact **12997053018** `audit_receipt.json` 실제 다운로드 확인. 이것은 v203의 B3150/T3182 Native6와 **독립적인 신규 결과**이다.
- 추가 최신 HEAD 범위 제한 `f1f1387...`의 후속 양 OS CI [#41100357780](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41100357780) 및 정확 동일 프로필로 '미선택/자동선택/수동 T' 세 경로를 계획만 생성하는 **0 Native** [#41101150249](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41101150249)는 상태 확인이 끝나기 전까지 PASS 주장하지 않는다.

이 영수증은 마부 8025를 실제 선택한 정해진 Linux 냉법 334 범위의 **개발용 기능 검증**이며, 일반 사용자가 고를 수 있는 마부 목록 승격이나 Windows Native 결과를 의미하지 않는다.

### 2026-10-31 v206/v207 — 사용자 직접 명확화: 마부 선택은 CHMV 예산 증가 조건이 아님

- 사용자가 영구 마부를 골랐다는 이유만으로 `B/T`를 증가시키지 않는다. **정확한 SimC Native 증거로 확인된 정적 치명·가속·특화·유연 rating 증가**가 있고 사용자가 자동 목표 ilvl 기준을 쓸 때만 해당 고정 `E`를 자동 `B/T`에 **한 번** 포함시키며 기존 자유분배가 아니라 스탯별 하한으로 보호한다. 사용자가 지정한 최종 `T`는 언제나 그대로다. 치명타 *효과* 강화·발동형·3차/주능력치 마부는 고정 CHMV 증가가 없으면 `B/T` 불변으로 SimC에 정확한 `enchant_id`만 전달하며, 효과 자체는 SimC 책임이다.
- `v191`은 소스 관측 ID/토큰/부위/최고 source rank의 시즌 38종을 가져왔고 전 38종의 정적 수치·실제 proc 메커니즘의 세밀한 결과를 자동 확보한 것은 **아니다**. `v197`은 반지 9종 source 유형을 분류한다. 미분류 또는 정적 E 미관측을 0으로 단정하여 자유 예산에 넣지 않고 해당 선택은 계속 제한한다. 전체 38×26 Native 전수 검증/독립 proc evaluator 신설은 제품 요건이 아니다.
- `독수리의 눈`(`enchant_id=7967`, 반지1)만 `v106→v098→v096→v094` 일반 Windows 사용자 입력으로 연결. [Windows v206 비교 #41107497147](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41107497147) 실제 Native2로 같은 징벌334 프로필의 고정 CHMV delta `{0,0,0,0}` 확인. [Linux/Windows focused #41108975367](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41108975367) **각 130/130 PASS, Native0**. 초기 Windows #41108763669는 CRLF checkout 때문에 UI 원본 LF 문자열 assertion 3 FAIL; 기존 v181 LF-preserve 체크아웃을 복구해 통과, 역사 실패 삭제 금지. [Windows v207 실제 선택 Native #41109265120](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41109265120) **새 Native6, SHA 캐시6/6, 추가 Native0**, `B3150/T3182`, 관측 DPS `185221.06034702563`/SEM `270.9787148736912`, 95% 단일 결과, 전역최적 미입증. 사용자 미선택 세션·DPS 캐시는 그대로, 선택시 시나리오/프로필/Native identity만 분리한다. 나머지 37종은 잠금, `8025` E+30 Linux 개발용 계약과 섞지 않는다.
- [v207 successor 영수증](V207_EAGLE_SELECTED_NATIVE_VALIDATED_SUCCESSOR_20261031.json)에 원본 artifact와 Native JSON2 SHA 6개를 고정. 원본 v205-v207 공용 probe의 잘못 이어진 `no_enchant_selection_promotion=true` 메타데이터는 선택한 독수리의 눈을 무효화한다는 의미가 아니며 원본을 수정하지 않고 새 successor에 교정. 검증하지 않은 결과·다른 전문화의 마부 효과 수치·95% 대조 우위는 주장하지 않는다. Windows 이전 ZIP 사용자 PC 적용·Project UI 원본 수정·main 승격 없이 **격리 개발**만 기록한다. 다음 P1은 정확 특수장비 고정 `L` 자체 준비를 사용자에게 요구하지 않는 내부 캐시-first 선택적 Native 확보 경로다.

### 2026-10-31 v208/v209 — 선택 특수장비 정확 L의 내부 캐시·단일 Native 확보

- 현재 사용자에게 전체 장비·개발용 프로필·filler·seed·정적 캐시 파일을 요구하지 않는다. 이미 내부 구성한 현재 시즌 대표 장비/실제 사용자 프로필을 `v098`의 비실행 `static_special_probe_only` 경로에서 재사용한다. 사용자가 단순 예산 미리 확인을 누르면 신규 Native 0회이며, **최적화 시작을 명시적으로 누른 경우**에만 정확한 고정 L이 필요한 특수장비 variant 전체를 한 번의 실제 Native JSON2로 관측할 수 있다. 기존 `v046` 동일 시즌 정적 기록만 append하고 기존 캐시/세션은 불변으로 보존한다. 실제 DPS는 기존 적응형 `v094`가 담당하며 최대 Native6, 결과/SEM/95%/캐시/취소·재개 계약을 재구현하지 않는다.
- 특수장비 고정 `L`은 `G/B`에 이미 포함돼 있고 고정 스탯 하한으로 보호하며 다시 더하지 않는다. 기름 O는 1회, 보석 J 및 마부 E 수치는 각각 별도다. **특수장비에 보석·마부가 붙어 그 수치가 L에 섞이는 경우**, 기존 `v062`의 정확한 bare 정적 레코드가 없는 상태에서 장식된 수치를 억지로 L로 잠그는 것은 금지한다. 이번 v208은 기존 v062 차단을 Native 이전에도 적용해 낭비를 줄인다. 보석 포함 variant의 원래 장비 base L 측정/귀속은 P1 잔여 과제다.
- [실제 Windows v208 Native 정적 L #41148967010](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41148967010): 정기 주술사331/특수 망토159288 정확 L=(0,0,51,61) Native1, `B3110,T3142` 유지, 정적 재실행0. [전체 한 세션 v209 #41149327977](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41149327977): 같은 범위에서 사용자의 시작→정적 Native1→DPS Native6→결과→캐시6/6, 재실행 Native0, 관측 1순위 DPS201953.1715·SimC SEM337.3012·95% 판정, 전역최적해 미증명. [최신 focused #41149118458](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41149118458) Ubuntu·Windows **각 114 PASS/0 FAIL, Native0**. `v209` 원본 ZIP SHA/실제 정적·DPS JSON2 SHA는 [v209 검증 영수증](V209_WINDOWS_ONE_SPECIAL_COMPLETE_NATIVE_VERIFIED_20261031.json)에 보존한다.
- 초기 특수 목걸이 대상 #41148641946/#41148763112/#41148833439는 옵션 가정 오차 및 기존 `v062` 안전 차단으로 **실제 실패**, 삭제하거나 성공으로 승격하지 않는다. 이를 바탕으로 이제 장식된 장비에서는 정적 Native 전에 차단. 전 26전문화·시즌 모든 특수장비·Windows GUI 클릭·사용자 PC 전수 검증과 혼동하지 않는다. v180 다전문화 Native36은 새 UI 변경에서 **skipped**. 차기 최우선은 bare L/J/E 안전 분리이며, 마부 38종의 SimC 효과 상세 source 분류는 P2에서 기존 v191 수집에 누락된 항목만 보강한다.
- GitHub `probe/chat-cache-v035-20261024` 격리 개발에 한정. `main`, 불변 `v003`, 원본 `v016`, Project Sources/Instructions 실제 적용 및 Work OS 공식 승격은 사용자 별도 권한 없이 변경하지 않는다.

### 2026-10-31 v210 — 특수장비 bare L과 보석 J·마부 E 분리 (사용자 최신 진행 승인)

- 특수장비의 L은 `시즌·아이템 ID·ilvl·슬롯·내재 옵션`이 정확히 같은 **보석·마부 제거 Native 정적 variant**에서만 확정한다. `bonus_id`, `redirected_base_stats`, `context`, `content_tuning` 등 내재 옵션은 제거하지 않는다. 소켓 `gem_id`와 영구 `enchant/enchant_id`만 정적 L의 수치 출처에서 제외하고, 사용자의 **실제 DPS 실행 프로필에는 그대로 보존**한다. 장식된 Native 레코드가 캐시에 있더라도 기본 L을 대신하지 못하며 누락 L=0 금지.
- `v062`의 `native_gear_stats.identity`는 실제 착용 장비의 풀 옵션 그대로여야 하므로, `v064`의 엄격한 프로필 일치 확인을 변경하지 않는다. 스탯의 원천은 별도 `native_gear_stats.numeric_source_identity`로 기본 L만 참조한다. 기본 L은 G/B에 이미 포함되어 스탯별 하한이고, 보석 J와 정확 확인된 고정 마부 E는 별도 계산·중복 가산하지 않는다. 수동 최종 T 우선, O는 한 번만.
- [Ubuntu/Windows focused #41152031433](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41152031433) 각 **127 PASS/0 FAIL·신규 Native0**; [기존 v098 회귀 #41151976759](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41151976759) SUCCESS. 초기 코딩 중 프로필/수치 identity 충돌로 발생한 Actions 실패는 역사로 보존.
- [실제 Windows v210 #41152171198](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41152171198), 정기 주술사331 특수 목걸이268250의 **원본 gem_id=240900/240900 유지**, 기본형 정적 Native1 `L={crit93,haste305,mastery0,vers0}`와 기존 DPS Native6·캐시6/6 HIT·추가 Native0, 관측 DPS202301.8300/SEM346.1753·95%, 전역최적해 미입증. [v210 증거 SHA](V210_WINDOWS_GEMMED_SPECIAL_BARE_L_REAL_NATIVE_SUCCESSOR_20261031.json)에 원본 artifact/digest 포함. 다른 아이템·보석·마부 조합을 전수 인증한 결과는 아니며 별도 SimC 효과 판독/최적화 엔진 미도입. v191의 38종 마부 effect 상세 수집은 기존 P2 별도 과제로 남는다.


### 2026-10-31 v211 — 시즌 마부 38종 원본 SimC 효과 분류 (read-only)

- v191의 38개 highest-source-rank permanent-enchant candidate를 SimC revision `710c2408bfd3ae4df71b8cd55cdf01f63fd6c926`, game build `12.1.5.70575`의 6개 source file로 identity/hash 고정 후 대조한다. 영구 마부 token·rank·item class·inventory/subclass mask가 모두 정확히 일치해야 하며, 반복 DBC enchant ID는 ID 단독으로 매칭하지 않는다. source compiler `runner/v211_enchant_source_effect_classification.py` 및 compact projection `data/current_season_enchant_effect_classification.json`이 38행의 source provenance를 보존한다.
- 분류 결과는 서로 겹치는 집계로 **정적 CHMV rating 8종**, **정적 비CHMV only/mixed 19종**, **spell effects 15종**, Native E scope 2종이다. CHMV ring families: mastery 7965/7969, crit 7995/7997, haste 8021/8025, versatility 8023/8027. DBC static non-CHMV는 primary/stamina/tertiary이며, 일부는 별도 spell utility를 함께 가진다. 7963의 실제 DBC stat은 avoidance+stamina; 이름에서 agility를 추정하지 않는다. Weapon temporary CHMV procs (예: 8041 mastery, 8689 adaptive secondary)는 고정 E가 아니고 SimC DPS 중 효과다.
- **Native E 증거는 7967 E0 한 Windows 징벌334/finger1 scope, 8025 haste30 한 Linux 냉법334/finger1/item158366 scope뿐**이다. 8025를 제외한 나머지 7개 static CHMV ring enchant의 DBC source classification은 정확 Native E 수치 측정이 아니다. 8025는 developer-only. 일반 UI 선택은 기존 7967 한 scope만 유지; 나머지 36은 잠금. Source classification/tooltip은 사용자 승인, item slot/profile eligibility, Native acceptance 또는 budget E proof를 대신하지 않는다.
- SimC는 spell/proc timing, dynamic stat buffs, damage, APL interaction, DPS를 전담한다. source에 custom handler가 안 보인다는 사실은 unsupported나 Native acceptance를 뜻하지 않는다. 우리 코드는 독립 proc/effect evaluator를 만들지 않는다. 정확 Native로 확인된 **영구 정적 CHMV E만** 자동 참조 B/T 회계에 기존 v204 계약대로 반영; 수동 최종 T 불변, T=G+J+F+O/B=G+J+F, O once, special L fixed floor, cache/session identity 불변.
- [source compiler #41155772497](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41155772497) Ubuntu·Windows 각 6 tests PASS, all38 pinned source/manifest match, Native0. [catalog integration #41155959636](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41155959636) 각 OS 56 tests PASS, 38 rows visible read-only, selectable count1, Native0. [UI #41155959593](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41155959593) 두 OS PASS; [Windows source beta #41155959570](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41155959570) Python3.12/3.14 SUCCESS; refreshed v211 guide package [#41157484148](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41157484148) Python3.12/3.14 SUCCESS, artifact #13025173397 SHA256 `edfa49030145622c8dc31ee84daf3ba9d4784a1e7749419ad054c107fe538141`, Native0. Full details and original source compiler artifact hash: `docs/V211_ENCHANT_EFFECT_SOURCE_CLASSIFICATION_AND_EVIDENCE_20261031.md`.
- 추가 7개 CHMV ring enchant를 실제 사용자 선택으로 확장하려면 정확한 ring ID·slot·전문화·프로필 조건을 정하고 필요한 Native E만 최소 횟수로 측정한 뒤 별도 승인해야 한다. 38×26 Native matrix 불필요. v211은 classification only, no UI unlock, no Native.


## 7. 2026-10-31 사용자 직접 승인 — 장비 수집 DB와 원클릭 Environment Builder 통합 목표

**최종 제품은 장비 수집 DB, 원본 기반 자동 발견·분류·자가검증 엔진, 기존 SimC 최적화 엔진을 결합하여 사용자가 원클릭으로 실행 환경을 구축하는 프로그램이어야 한다.** 개별 마부/장비 UI를 만드는 것이 최종 목표가 아니다. 새로운 시즌/아이템/효과를 사용자가 일일이 알려주거나 개발자가 매번 하드코딩하지 않아도, 승인된 원본을 탐색해 후보를 발견하고 출처·정체성·적용 부위·효과 유형·정적 스탯·검증 범위를 구조화하며 필요한 선택 조건만 최소 검증해야 한다.

### 승인된 최종 구성

1. **시즌 장비 수집 DB:** 기존 v161–v190 API-first/zero-seed 수집 체계를 재사용해 장비·티어·장신구·특수장비·제작/장식·보석·마부·소모품 후보를 모은다. 다른 프로젝트/WEQUIP를 시드로 쓰지 않는다.
2. **자동 발견·분류·자가검증 엔진:** SimC generated DBC/enum/spelltext/handler와 DB2/item metadata를 정확 ID·token·source revision/build/SHA로 연결한다. 부위별 적용성은 실제 inventory/subclass mask 및 아이템 데이터로 결정한다. 미확인·누락·충돌은 UNKNOWN/PENDING/CONFLICT로 보존하고 0이나 전 부위 허용으로 추정하지 않는다. 동일 효과·동일 부위·비교 가능한 강도만 축약한다.
3. **기존 제품 카탈로그 연결:** v191 thin aggregator, v211 source classifier, v196/v197 catalog bridge를 재사용한다. 현재는 각각 별도 후보/manifest와 제한된 UI 승인 경계를 갖고 있으므로, 단일 버전형 Environment Manifest로 출처를 참조·결합하는 통합이 미완료다. 새 수집기나 중복 데이터베이스를 만들지 않는다.
4. **목표 환경 구축:** 승인된 사용자 선택을 기존 v098 대표 프로필 생성 및 v062 예산 계산에 전달한다. v208 exact selected-special bare L lookup과 v046 static cache를 재사용한다. 전체 DPS 프로필에는 사용자가 선택한 보석/마부/장비 옵션을 그대로 보존한다. 26개 DPS 전문화 대표 프로필 공급을 완성한다.
5. **기존 SimC 최적화:** 봉인된 프로필/manifest를 v093/v094/v095 적응형 SimC에 넘긴다. DPS/SEM/95%/대안/캐시/취소/재개를 새로 만들지 않는다.

### 원클릭 Environment Build 동작 계약

- 사용자 명시 요청 시 실행하는 증분 동기화이며 상시 폴링/백그라운드 감시가 아니다.
- 동일 source identity/build/hash의 기존 artifact와 검증 캐시는 재사용한다. SimC revision 변경만으로 정적 시즌 아이템 캐시를 폐기하지 않는다.
- 변경된 source row만 파생 카탈로그/검증 의존성을 무효화한다. DPS 결과 캐시는 SimC binary/version, full profile/options, 후보, O, 전투조건, iterations identity로 별도 관리한다.
- Preview/Plan은 Native0. 명시적 Start 시 실제 선택된 항목의 미관측 정적 수치만 필요한 최소 Native로 조회한다. v208은 여러 선택 특수장비 L miss를 한 번의 Native로 해결할 수 있다. 26×아이템/마부 전수 Native 금지.
- Environment Manifest는 season/game build, SimC revision/binary, 원본 경로·SHA/artifact, 카탈로그 schema/version, exact item/options/slot identity, Native profile/binary/JSON2 SHA scope, static CHMV status, cache references, unresolved dependencies를 보존한다.
- 준비 상태는 READY / READY_WITH_LIMITATIONS / BLOCKED로 구분하고 새로 발견·갱신·재사용·미확인·차단 항목, Native 횟수/cache hit, 적용 범위를 보고한다. 한 항목의 미확인이 무관한 선택지를 제거하지 않되, 그 항목 자체는 fail-closed 한다.

### 불변 제품 경계

- 사용자 지원은 **증강 기원사 제외 DPS 26전문화**. 탱커/힐러 제외.
- 목적은 목표 ilvl 또는 수동 최종 T에 대한 최적 절대 CHMV rating 탐색이지 현재 장비 재분배나 장비 조합/획득 경로 추천이 아니다.
- T=G+J+F+O, B=G+J+F, O once. 선택 특수 bare L은 G/B 내부 하한이며 재가산하지 않는다. Gem J와 영구 마부 E는 L에서 별도 귀속한다. 정확 Native E가 확인된 선택 정적 CHMV 마부만 기존 v204 자동 ilvl reference 규칙을 적용하며, 비CHMV 7967은 B/T 불변, 수동 최종 T는 재증가 금지.
- SimC가 장비효과/proc/APL/buff/DPS를 소유한다. 우리 코드는 출처·ID·옵션·적용성·프로필·예산·정적 JSON2 정합·통계·캐시·오케스트레이션을 담당한다.
- 기존 GitHub 격리 브랜치 문서 반영은 Project Sources/Instructions UI 적용이 아니다. main, v003 immutable, 원본 v016, 저장소 visibility, 공식 Work OS 승격은 별도 권한.

### 구현 순서 및 현재 결손

- **P3-A:** v191/v211/v196/v098/v208을 참조하는 단일 버전형 Environment Manifest 및 source dependency/invalidation contract. Native0 readiness preview와 unresolved join report.
- **P3-B:** v191 source candidate → v211 classification → v196 approved catalog의 직접 artifact handoff. 부위별 카탈로그는 exact mask/item join에서 생성하고 discovery/classification과 UI selection을 분리.
- **P3-C:** 승인된 선택값 → v098 대표 프로필/예산 → v208 선택 L → 기존 optimizer를 하나의 sealed environment로 연결하고 26 DPS 프로필 공급 확장.
- **P3-D:** Windows 원클릭 Build/Start, progress, cancel/resume, incremental refresh, cache/evidence diagnostics.
- 현재 v191은 source-pinned candidate aggregator이며 automatic UI promotion=false; v196은 고정 source candidate JSON과 별도 approval boundary를 읽는다; v211은 38 마부 분류만 수행한다; v098은 source-backed archetype subset만 지원한다. 따라서 **통합 Environment Builder, end-to-end manifest, 26 DPS 전체 프로필 공급, 최종 Windows one-click UX는 미완료**다.
- 설계 상세 및 최초 통합 단위: `docs/P3_ENVIRONMENT_BUILDER_TARGET_ARCHITECTURE_20261031.md`. 이번 반영은 아키텍처/정책 문서화이며 코드 통합 완료나 사용자 배포 승격을 뜻하지 않는다.


#### P3-A 구현 진척 — v212 Environment Manifest (2026-10-31)

- `runner/v212_environment_manifest.py` 추가. 기존 v191 season aggregation, v211 enchant classification, v196 approved UI catalog, v098 target-profile preparation 결과를 입력받아 **하나의 결정적 Environment Manifest**로 참조 결합한다. 수집·API·SimC Native·최적화 실행을 하지 않는 얇은 provenance/readiness join이다.
- exact schema/build/SimC revision 일치, 마부 38행/현재 UI 선택 1개 경계, source 단계 Native0/no auto-promotion, v098 READY plan, target profile files, SimC binary SHA, 선택 static-cache SHA를 검증한다. 프로필 파일 변경은 환경 digest를 변경하고, source/build/revision/approval/path mismatch는 fail-closed.
- 결과는 절대 로컬 경로와 전체 사용자 프로필 내용을 복제하지 않고 SHA·상대 profile file identity만 보존한다. 현재 26 DPS 프로필 공급 및 단일 source-to-catalog handoff가 미완료이므로 READY_WITH_LIMITATIONS가 정상 결과다.
- 신규 `tests/test_v212_environment_manifest.py` **8 tests**; [Ubuntu/Windows Actions #41159726342](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41159726342) 각각 **8/8 PASS**, compile PASS, Native0/network0. v210/v211 기존 Native/캐시 증거는 재실행하지 않았고 무효화하지 않았다.
- 이 단계는 P3-A의 artifact manifest/readiness 핵심만 구현했다. v191/v211/v196/v098을 자동 실행하는 production command, Build UI/API, 모든 26 DPS profile supplier, Windows one-click progress/cancel/resume는 미완료. 상세 `docs/P3_ENVIRONMENT_BUILDER_TARGET_ARCHITECTURE_20261031.md` §8.
