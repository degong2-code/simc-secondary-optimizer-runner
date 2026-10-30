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
