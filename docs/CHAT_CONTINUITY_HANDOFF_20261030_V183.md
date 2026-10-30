# SIMC SECONDARY OPTIMIZER — v183 새 채팅 인계·복원 기준 (2026-10-30)

**상태:** 사용자 요청으로 기존 개발 대화의 길이 제한 이후 개발을 **그대로 인계**. 새 제품/엔진/프로젝트 재시작 금지. 이 문서 **하나**가 새 채팅 인계의 정본이며, 복사할 시작 프롬프트도 아래 §8에 내장. 역사 문서 재전달·독립 파일 중복 생성을 최소화한다.

- 저장소 `degong2-code/simc-secondary-optimizer-runner`
- 실제 개발 격리 브랜치 `probe/chat-cache-v035-20261024`
- **최종 제품 코드/CI 검증 커밋(인계 문서 작성 전):** `c32ae1625299e18e3fd37f61d3110105caed5e84`.
- **인계 문서 작성으로 위 HEAD는 이동한다.** 새 채팅은 그 SHA로 최신 상태를 추정하지 말고 **GitHub 현재 브랜치 HEAD·CURRENT·Actions run**을 조회해야 한다.
- `main`, `v003` immutable, 원본 `v016_SCENARIO_CONTRACT` 실제 파일, Work OS·Project Sources/Instructions UI는 변경/승격하지 않음.

## 0. 복원 자료 — 이 순서만 읽고 필요할 때 확장

1. **이 문서** `docs/CHAT_CONTINUITY_HANDOFF_20261030_V183.md` — 권한·제품 목표·현재/미완료·시작 프롬프트.
2. **현재 HEAD**, `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` **맨 위 v182/v183 관련 문단**, GitHub v182 Actions/원본 영수증 — 실제 구현 증거.
3. `docs/DEVELOPER_NOTES_v1.4.2_LATEST_USER_POLICY_ADDENDUM_20261030.md` + `docs/APPROVED_PRODUCT_GEAR_USER_FLOW_20261029.md` 상단의 **2026-10-30 UI 교정** — 최신 사용자 결정. 비충돌 내용은 첨부 `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.1_DPS_ONLY_SCOPE_CORRECTION_20261029.md` 및 기승인 정책으로 보존. **v1.4.1에 남은 27개·증강 포함 = 역사 오기**. Project UI 실제 적용 확인하지 못했음.
4. 제품 코드 경로: `runner/v113_local_web_api.py`, `runner/webui/app.js`, `runner/webui/index.html`, `runner/v106_user_session_controller.py`, `runner/v098_target_user_scenario_bootstrap.py`, `runner/v108_native_consumable_inputs.py`, `runner/v167_product_season_gear_adapter.py`, `runner/v169_source_first_representative_stage.py`; 이후 필요시 기존 `v096→v093/v091/v092→v094/v065` 진입점.
5. 증거를 더 자세히 볼 때만: `docs/V181_P1D_WINDOWS_LOCAL_BETA_PACKAGE_REAL_HTTP_20261030.md`, `docs/V180_P1C_MULTILEVEL_CURRENT_SEASON_REAL_BATCH_20261030.md`, `docs/V178_V179_P1A_CANCEL_RESUME_P1B_INPUT_CHECKS_20261030.md`, `docs/V176_26_DPS_CURRENT_SEASON_PHYSICAL_NATIVE_RESULTS_20261030.md`, `docs/CHAT_CONTINUITY_HANDOFF_20261029_V162.md`(수집 역사). 이들을 새 구현 지침으로 삼아 이전 단계를 다시 시작하지 않는다.
6. 사용자 PC에서 최근 제공한 `V094_RESULT(20261030-005532).json`, `V106_USER_RESULT(10).json`, UI 스크린샷은 **최근 냉기 마법사 관측 사례**다. 새 채팅에서 파일이 실재하는지 확인하고 없으면 해당 수치/한계만 이 문서에서 재사용. 추가 장착/효과 진단에는 **사용자가 가진 해당 세션의 실제 생성 SimC profile과 Native JSON2/log**가 필요하다. 개인 파일을 GitHub에 업로드하지 않는다.

## 1. 장기 제품 목표 및 확정 정책

**목표:** **26개 DPS 전문화(증강 기원사·탱커·힐러 제외)**에 대해 사용자가 지정한 목표 ilvl **266–344(기본334)** 또는 **수동 최종 CHMV 총량 T**를 기준으로, **치명·가속·특화·유연의 미래 파밍 목표 절대 rating** 중 SimC DPS가 높은 분배를 기존 적응형 탐색으로 찾는다. 보고는 최종 rating·비율·관측 1순위·DPS·SEM·**95%만**의 통계 판단·실질적으로 다른 근접 대안·전역 최적 미증명을 구분한다.

- **현재 장비 스탯 재분배기/장비 조합 추천/파밍 경로 추천이 아니다.** 일반 장비·무기·주능력치·티어 4세트·APL 기반 대표 프로필은 내부에서 결정하며 사용자에게 일반장비 전체 ID 조회/선택을 요구하지 않는다.
- 사용자: 직업/전문화/종족/특성, 목표 ilvl 또는 기름 포함 최종 T, 시즌 장신구 2개, 선택 특수효과 장비, 제작장식 최대 2개, 보석·영약·옴니움·기름·전투조건. 업로드 SimC 프로필은 캐릭터/특성 읽기 선택 기능이며 현재 착용 장비를 기본 예산으로 쓰지 않는다.
- **`T=G+J+F+O`, `B=G+J+F`, `T=B+O`; `c_final=c_base+o`.** 기름 고정 O는 `gear_*`에 정확 한 번, 비자유분배. 정확한 특수장비 고정 하한 L은 G/B **안에 이미 포함**되므로 한 번만 보호하고 추가하지 않음. 장신구 정적 스탯은 자유 G 밖이며 JSON2 gear 누락은 0/미지원 근거 아님. 제작 초기 50:50 배분은 L 잠금이 아님. 시즌 79×2 Native 기반 ilvl 참조 B는 **10 rating 단위 근사**; 사용자가 수동 최종 T를 입력하면 우선, exact Native G는 필수 Gate가 아님.
- SimC는 실제 장비/장신구/장식·발동/영약/보석 효과·전문화 APL·DPS 계산의 책임. 우리 코드는 정확 ID·ilvl·옵션·예산·주입 정합·후보/95%·캐시/취소/재개·UI. **독립 효과 지원 인증 Gate, APL/효과 재구현 금지.**
- 같은 시즌 정적 아이템 캐시는 SimC revision 변경만으로 폐기 금지, 사용자 승인 교정만 기록. DPS 캐시는 정확 바이너리/프로필/장비/스탯/O/조건/iterations별 SHA identity. `main`·v003·Project UI·Work OS 공식 승격은 별도 사용자 결정.

## 2. 시즌 장비 엔진과 최근 UI 결정

- 사용자 직접 정책: **다른 프로젝트/WEQUIP 장비 DB로 시드하지 않는 zero-seed 수집**. Blizzard·WCL 시즌/던전, 동빌드 wago DB2, Localbots의 새 시즌 `data/delve-loot.json` 구렁 ID를 wago ItemSparse로 확정. 2026-10-29 Zah'ran 79/79는 이미 확인; 매 시즌 79 재검증/79 고정 상수 금지.
- v161 10 DB2 CSV·레이드/소굴 보스 10/10·쐐기8/8 후보 매핑·제작106, v162 구렁79/79 ID 확정. v171 현재 시즌 선택 DB **511 후보**, 그중 **장신구63, 특수효과 비장신구14, 내부 일반장비328, 제작106**. 별도 티어 65 ID (13직업). 실제 시즌 귀속 후보와 개별 드롭/효과 인증을 구분한다.
- 최신 2026-10-30 v182 사용자 직접 UI 요구/구현:
  1. 마법사 등 **기름을 바를 보조무기가 없는 전문화**에서는 보조무기 기름 체크 불가.
  2. 특수효과 장비의 `bonus_id`, 촉매 원본 ID는 일반 사용자에게 숨기고 정확 내부 매핑으로만 관리.
  3. **장식 제작장비는 제작 item ID·bonus_id 수동 입력 금지**, **부위 + 장식 종류 + 두 제작 스탯**만 선택하게 하고 해당 부위·방어구 유형의 실제 제작 ID를 내부 적용. 지원 확인된 장식 외 임의 효과를 만들지 않는다. 구형 내부 API/과거 세션의 ID payload는 호환용 보존.
  4. **옴니움 장서는 4열만 치명/가속/특화/유연** 선택, 다른 행은 내부 고정. 최초 유연 source-name 오류는 `136820:1`로 교정.
- 일반 사용자 UI에 일반 장비 ID 자유입력, 보통 장비 후보 리스트, 완전한 시즌 장비 DB 조회를 다시 도입하지 말 것.

## 3. 실제 완료 및 적용 범위 — 기존 PASS 재사용

| 단계 | 실제 확인 증거 | 완료 범위 / 과장하면 안 되는 부분 |
|---|---|---|
| v171~v174 | CURRENT·역사 v162 handoff 및 v174 Native | 511 시즌 장비 후보·65 티어·새 대표 프로필의 실제 한 전문화 물리 입력 확인. 시즌 모든 아이템 효과 인증 아님. |
| v175 | [Actions #40969073992](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40969073992) | 징기 첫 정적 CHMV rating·DPS·SEM·캐시. 전체 최적화 아님. |
| v176 | [#40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357) | **26/26 DPS 기본 대표 프로필 물리 Native PASS**, 신규25+v174 캐시1. 모든 장신구/특수옵션 아님. |
| v177 | [#40976501045](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40976501045) | 현 시즌 사용자→기존 v094 **6후보 Native**·95% 결과·캐시6/6 (징기334), 26전문화 전부 최적화 아님. |
| v178 | [#40978510648](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40978510648) | 첫 Native2 후 정상 취소, **기존 캐시2 + 신규4** 재개, 최종 cache6/6. 후보 사이 취소이지 SimC 프로세스 강제종료 아님. |
| v179 | [#40978882774](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40978882774) | 수동 최종 T/기름 O/장신구·전투설정·소모품/정확 L 누락 차단 **오프라인 47/47**, 변경옵션 별 Native DPS는 아님. |
| v180 | [#40980268952](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40980268952) | 26 spec×5 ilvl=130 계획 PASS; 분노266·야냥300·징기321·무법330·황폐340·냉법344 **6세션×6후보=Native36/36 + SHA 캐시36/36** PASS. 전 레벨×전 조건 Native 인증 아님. |
| v181 | [#40981704073](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40981704073) | Windows Py3.12/3.14 ZIP 추출/CMD/실제 HTTP서버/3개 계획 복원·보안 PASS; **Native0**, standalone EXE 아님. |
| v182 UI | [#40986181287](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40986181287) | Windows+Ubuntu UI 회귀 **신규4+기존51+ZIP2/각 환경 PASS**; Windows 재포장 ZIP [artifact #12946803072](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40986181287/artifacts/12946803072) **7일 임시**. 동 HEAD 웹 API [#40986181309](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40986181309) 두 OS PASS; v098 focused [#40986181282](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40986181282) **363 tests PASS**. |
| v182 옵션 Native | 초기 [#40985573830](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40985573830) → 교정 [#40985987787](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40985987787) | **초기 6종 중 5 PASS / 유연1 FAIL (exit80)**; 실제 source rune `136820:1` 교정 후 **유연 1회 재시험 PASS**. 최종 6종 물리 수용 결과는 5+1 증거로 판단, 이전 FAIL 삭제 금지, 개별 6후보 최적화 입증 아님. |

최근 원본 SimC 고정 GitHub Linux 바이너리 revision `7bc10711b5`, SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`(역사 실험용). **사용자 PC Windows 바이너리가 그와 동일하다고 추정하지 않는다.** GitHub Actions artifact는 단기 보관이며 만료되면 기존 원본 Actions 로그/브랜치 상태와 필요 최소 재패키징으로 대체한다. 영수증의 정확히 입증된 범위만 쓰고 동일 기준 시험을 반복하지 않는다.

## 4. 가장 최근 사용자 Windows 실측 — 낮은 냉법 DPS 관측과 미확인 사항

첨부 `V094_RESULT(20261030-005532).json`, `V106_USER_RESULT(10).json` 및 UI 스크린샷: **마법사/냉기**, 목표 ilvl334, 총 **6 Native 시도·고유 CHMV 4개**, **관측 최고 DPS `158716.232862584`, SimC SEM `225.73157454188464`**, `B=3150, O=(crit16,haste16), T=3182`, 관측 rating **치916/가766/특750/유750**. 두 확인 후보의 95% 방향 지지 `true`, **전역 최적해 미증명**, 근접 분배는 해당 표본 범위에서 0개.

- **정상 확인:** 사용자 Windows에서 실제 v094 실행·DPS·SEM·95% 표시·결과 저장까지 수행됐음. 스크린샷에 '6/6 후보 100%, Native 6, 캐시0' 표시.
- **미확정:** 체감 DPS가 낮은 이유. 이 JSON 두 개만으로 **실제 장착 티어 ID/4세트 적용, 원래 장신구 proc, 무기 성능, 소모품·전투버프/APL**의 실제 JSON2/SimC 프로필 입력 정합성을 증명하지 못한다. SimC 효과 지원 여부를 독립 재구현하지 않고 **원본 생성 `profile.simc`, 실제 Native `result.json`(JSON2)·SimC 로그·해당 세션 `manifest.json`**을 확인하는 최소 표적 입력 진단을 수행한다. 입력이 정상이라면 6후보 4고유 후보의 탐색 폭·사용자 기대 장비/전투 조건을 명시해 해석, 전역최적 주장 금지.
- 사용자 개인 세션·특성/전투 로그를 공개 GitHub에 원문 업로드하지 않는다. 이 인계 문서에는 비식별 결과 요약만 보존.

## 5. 장·단기 로드맵, 즉시 중요 작업과 효율 대안

**장기:** 모든 허용 전문화·사용자 시나리오에서 미래 목표 절대 CHMV rating·DPS/SEM/95%·실질적 대안·일관된 캐시·취소/재개를 제공하는 **간결한 Windows 실사용 제품**. 6후보 적응형 기존 엔진은 유지하고 탐색 효율·근접 대안 품질은 실제 증거가 필요할 때만 개선.

**단기 우선순위 (사용자가 `진행`을 지시한 뒤):**
1. **P1-D 최종 사용자 PC 증거와 낮은 DPS 원인 구분:** 업로드된 v094/v106의 정확 수치 복원, 가용하면 **동일 사용자 세션의 profile/Native JSON2/로그를 확인**해 내부 대표 일반장비의 ilvl·무기·티어4·장신구·기름 O·버프/APL 입력 정합. 실제로 확인되지 않은 효과를 PASS라 주장하지 말 것. **기존 영수증과 원본 파일로 우선 분석, 새 Native 호출 0을 목표.**
2. **v182 간단 UI의 실제 사용자 경로 확인:** 보조무기 기름 체크 상태, 특수장비 고급 ID 숨김, 제작 부위/안감/제작 스탯 선택→정확 ID, 옴니움4열 바뀜이 **현재 ZIP**에 포함·유지되는지 읽기 전용 확인. 기존 Android/브라우저 화면의 옛 v181과 새 v182는 구별. 미지원 정확 L/장식은 추정값으로 채우지 말고 사용자 친화적으로 알릴 것.
3. **실제 미완료 조건만 최소 검증·교정:** Windows 사용자 실제 Native(이미 냉법 1세션 실행한 증거 재사용), 브라우저 버튼 취소·재개 직접 확인이 필요한 경우만 보완; 소모품/정적 정확 variant·미지원 케이스는 필요한 1~몇 건만 선택적 Native. 실패 원문 보존, 배포 ZIP 재생성 후 Windows focused 회귀. v181 ZIP은 역사/대체하지 않음.
4. **배포 판단:** 설치형 EXE/SimC 동봉 여부는 요구된 제품 목적에 필수 아님. 현재 **Python+사용자 소유 SimC CLI 소스 베타**. 공식 main 병합·원본 v016 통합·Project UI 적용·Work OS 승격은 별도 사용자 승인/검증 필요.

**효율 대안:** 이미 성공한 26전문화 기본 물리, v180 36후보, v178 취소·재개, v182 5+1 선택물리 결과를 재활용. 독립적 오프라인/Windows UI 확인은 하나의 **병렬/배치 작업으로 묶기**, Native는 미관측 새 조건에만 제한. 매 변경에서 중복 SimC/API 호출·캐시 키·메모리·CSV/파일 I/O·GitHub artifact 크기·런타임 시간 검토. 필요 없는 새 Gate/전수 Native/SEM 극미세화/기존 자료 재감사 금지.

## 6. 갱신/미승격/미완료의 명시

- **이번 인계 준비에서 실제 GitHub에 기록:** `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 최신 v182 상태; `docs/APPROVED_PRODUCT_GEAR_USER_FLOW_20261029.md` 최신 v182 UI 우선 교정; `docs/DEVELOPER_NOTES_v1.4.2_LATEST_USER_POLICY_ADDENDUM_20261030.md`(최신 직접 결정·증거 한계); **본 문서**. 별도 README 링크만 추가(해당 커밋까지 최종 HEAD 확인). **코드·Native/CI 재실행 없음.**
- **미승격:** 실제 Project Sources에 v1.4.1→v1.4.2 보충본 등록/교체 **미확인**, 사용자 Project Instructions 교정 **미적용/미확인**, GitHub `main` 미병합, 원본 `v003` immutable·`v016` 실제 통합 변경 없음, 공식 Work OS M0/Shared State/승격 없음.
- **미완료:** Windows 냉법 저 DPS 원인 확정 및 실제 장착 티어4/장신구/무기/효과 입력 원본 감사, 현재 UI 실사용 선택 시 일부 exact-L/제작 변형의 실물 점검, 브라우저 직접 취소 버튼 E2E(기존 엔진 후보 사이 취소·재개는 완료). P1 전체 제품 공식 출시로 승격하지 않음.
- **개발 환경 책임:** GitHub 격리 브랜치에서 사용자가 허용한 일반 구현/테스트는 가능하나 새 채팅의 **첫 응답은 복원·검증 결과 보고로 종료**하고 반드시 사용자 `진행`을 기다린다.

## 7. 새 채팅 첫 턴의 필수 결과 (실행 없음)

- 브랜치 최신 HEAD/문서 HEAD·코드 HEAD 구분, CURRENT 맨 위 v182 상태, 승인된 26전문화·수식·정책, v182 원본 Actions(초기 FAIL→교정 PASS)를 실제로 확인하고 결과 보고.
- 완료/미완료/미승격·단기 로드맵·가장 효율적인 다음 묶음 작업과 Native 최소 검증 계획을 **간결한 자연어**로 설명.
- 첫 턴에서 **새 코드 작성/커밋·새 CI 실행·Native·패키지 배포·권한 승격·개별 효과 재연구를 시작하지 않는다.** 보고 후 사용자 `진행` 대기.

## 8. 새 채팅 시작 프롬프트 (이 절을 통째로 복사 가능)

> 너는 `SIMC SECONDARY OPTIMIZER` 기존 주 제품 개발 채팅의 후속 담당자다. **이번 첫 턴은 현재 상태 복원·GitHub 최신 HEAD/CURRENT·v182 Actions/Native 증거 검증 및 간결한 결과 보고까지만 수행하라. 내가 `진행`이라고 하기 전에는 구현, 파일 쓰기, GitHub Actions 재실행, Native, 배포, main 병합, Project Sources/Instructions 실제 적용, Work OS 공식 승격을 실행하지 말고 대기하라.**
>
> 정본 인계는 `degong2-code/simc-secondary-optimizer-runner` 격리 브랜치 `probe/chat-cache-v035-20261024`의 `docs/CHAT_CONTINUITY_HANDOFF_20261030_V183.md`다. 반드시 **현재 HEAD를 새로 조회**하고, 인계 문서 §0의 읽는 순서대로 CURRENT 상단·v1.4.2 최신 정책 보충·2026-10-29 승인 장비 정책의 2026-10-30 교정·최근 v182 코드/Actions 영수증을 읽어라. 2026-10-29 v162·v181 등은 역사 자료이며 CURRENT의 구형 '최신' 표현을 그대로 이어받지 마라. 27 DPS/증강 포함은 구형 v1.4.1 문구이고 실제 사용자 승인 제품 범위는 **26 DPS(증강 제외)**다. Project UI 교체 여부는 추정하지 마라.
>
> **장기 목표를 지속 점검하라.** 목표는 사용자 목표 ilvl266–344(기본334) 또는 수동 최종 T에서 **미래 파밍 목표 CHMV 절대 rating**을 SimC DPS 최대화로 찾고, 비율·DPS·SEM·95% 판정·관측 1순위·실질적 근접 대안·캐시·취소/재개를 제공하는 Windows 사용자 제품이다. 현재 장비 재분배/장비 조합·파밍 추천이 아니다. 대표 일반장비·무기·티어4는 내부 생성; 사용자 입력은 시즌 장신구2·특수효과·장식 제작 부위/장식종류/제작스탯·소모품·전투조건이다. `T=G+J+F+O`, `B=G+J+F`, O는 비자유 고정·한 번만 적용, L은 B 안의 보호 하한, 장신구 고정 스탯은 자유 G 밖. 95%만 사용하고 전역 최적이라고 주장하지 마라. SimC의 APL/장비·효과/proc/DPS 모델을 재구현하거나 새 효과 인증 Gate를 만들지 마라.
>
> 최신 v182 UI 변경 네 가지(마법사 보조무기 기름 불가, 특수장비 bonus/catalyst ID 숨김, 제작 부위+장식+두 스탯 입력, 옴니움 4열 CHMV)와 `136820:1` 유연 교정, 6종 옵션 Native의 **초기 5 PASS/1 FAIL → 해당 1개 수정 PASS**를 확인하라. v176 26/26 기본 물리, v180 6×6 적응형·캐시, v178 2+4 취소·재개, v181/v182 Windows 웹 통합과 동일 기준 PASS를 **재사용**하라. **독립 작업은 묶어서** 오프라인/웹/Windows 회귀를 확인하고, 이미 완료 검증을 같은 기준으로 재활용하며 실제 변경에 의해 무효화된 부분만 비례 검증하라. 기존 Native 전수 반복·새 엔진·불필요한 Gate/조합 연구·과한 정밀화는 금지.
>
> 가장 최근 사용자 Windows 냉법 결과는 334 / DPS 158716.23 / SEM225.73 / T3182 / 6 Native·고유4 후보. 낮은 DPS 원인, 실제 티어4/장신구/무기·효과 입력의 정상 적용은 **첨부 V094/V106만으로 확정되지 않았음**. 추후 내가 `진행`하면, 가용한 원본 SimC 프로필·JSON2·로그로 입력 정합을 우선 분석하고 새 Native를 최소화해 표적 보완하라. 사용자 로컬 자료를 GitHub에 그대로 업로드하지 마라.
>
> 첫 응답에서는 **핵심 제품 취지, 최신 복원된 HEAD/승인 설계, 완료와 증거 범위, 미완료·미승격, 단·장기 로드맵과 바로 다음 효율적인 묶음 작업**만 보고하고 반드시 내 `진행`을 기다려라.
