# SIMC SECONDARY OPTIMIZER — 2026-10-31 v203 정본 인계

**정본:** 이 문서 하나에 복원·증거·장단기 로드맵·시작 프롬프트를 통합한다. 이전 v183/v162 인계와 LAST-CHAT(2).txt는 역사·대조 자료. 새 채팅은 프로젝트를 재시작하지 않는다.

**저장소/브랜치:** `degong2-code/simc-secondary-optimizer-runner` / `probe/chat-cache-v035-20261024`. 인계 문서 이전 실제 코드·CI 기준 HEAD **`b2d727c7bfdf6c84017e0705075eb460ecce6e8c`**. 이후 문서 수정으로 HEAD가 이동하므로 새 채팅은 **최신 HEAD를 다시 조회**하고 문서-only 커밋을 코드 검증과 혼동하지 말 것. `main`·v003 immutable·원본 v016·Project UI/Work OS는 이번 인계로 변경되지 않는다.

## 0. 새 채팅 복원 순서

1. GitHub **현재 브랜치 HEAD, repo visibility, 최신 Actions** 조회(읽기 전용).
2. **이 문서 전체** → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 최상단 **v203/v202** → `docs/DEVELOPER_NOTES_v1.4.2_LATEST_USER_POLICY_ADDENDUM_20261030.md` §1 및 최신 §5 → `docs/V203_ENCHANT_8025_CROSS_FEATURE_AUDIT_AND_POLICY_ADDENDUM.md` → `WINDOWS_BETA_START_HERE.md`.
3. 해당 근거가 필요할 때만 코드 `runner/v202_one_enchant_admission.py`·`v065_v015_scheduler_adapter.py`·`v098_target_user_scenario_bootstrap.py`·`v096_unified_product_entry.py`·`v093_inclusive_adaptive_scheduler_bridge.py`·`v094_durable_inclusive_adaptive_runner.py`, 웹 `v106/v113`와 실제 Actions 영수증 검토.
4. 이전 `docs/CHAT_CONTINUITY_HANDOFF_20261030_V183.md`, 첨부 LAST-CHAT(2).txt, v1.4.1 원문은 과거 비교용. 첨부 LAST-CHAT 끝의 **27 DPS/증강 포함은 잘못 재인용한 구형 정책**. 최신 사용자 직접 승인 **26 DPS/증강 제외**가 우선.
5. 새 채팅 **첫 턴은 읽기 전용 복원 보고로 종료**. 사용자 **`진행` 전에는 새 구현·파일 편집·CI·Native·배포·권한/가시성 변경 금지**.

## 1. 확정 제품 목적·경계

- **26개 DPS 전문화만**, 증강 기원사·탱커·힐러 제외. 목표 ilvl **266–344(기본334)** 또는 수동 **기름 포함 최종 T**에서 미래 파밍 목표인 **치명/가속/특화/유연 절대 rating의 SimC DPS 최대화**. 비율·DPS·SEM·95% 판정·관측 최고·실질적으로 다른 근접 대안과 전역최적 미증명을 함께 보여준다. 현재 장비 스탯 재분배/장비 조합·획득 경로 추천 범위 밖.
- 사용자 선택: 직업/전문화/종족/특성, 목표 ilvl/T, **장신구2**, 선택 특수효과, **장식 최대2**(일반 UI에서 부위/장식종류/제작 스탯2), 보석/영약/음식/물약/기름/전투조건. **일반 장비·무기·티어4·대표 SimC 프로필·예산은 내부 구성**. 업로드한 현재 장비/T를 목표로 복사 금지.
- **`T=G+J+F+O`, `B=G+J+F`, `T=B+O`**. O는 비자유분배 기름 고정치로 한 번만 `gear_*` 적용, 정확 L은 G 안의 특수장비 하한, 제작 초기 50:50은 L 아님, 장신구 정적 JSON2 미출력은 0 아님. 현 시즌 ilvl 참조 B는 Native 기반 근사/수동 T 우선, exact Native G는 선택 경로.
- **마부 E** 역시 G 내부 비자유분배 고정 하한(동일 슬롯 L 중복 잠금 금지), 새 T/B/O 항목 또는 `gear_*` 중복 가산이 아니다. SimC가 APL/아이템 효과/proc/DPS 계산 책임, 우리는 입력 정확성·고정 예산/JSON2·후보/통계/캐시·취소/재개 담당. 신규 최적화 엔진/독립 효과 인증 Gate 금지.
- 시즌 카탈로그 zero-seed, 511 시즌 대표 장비 후보/65 티어 ID. 마부 **38종은 현재 모두 읽기 전용**. 원시 음식192/물약61을 최종 승인된 선택 개수로 오인하지 말 것. 같은 시즌 정적 아이템 캐시는 SimC revision 변경만으로 폐기하지 않음. DPS 캐시는 프로필·장비/마부·전투·바이너리·iterations별 분리.

## 2. 완료 및 증거: 최초 실측과 재사용을 구별

| 단계 | 확인된 PASS·범위 |
|---|---|
| v176 | [#40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357): 26/26 기본 대표 프로필 **물리 Native** 성공; 모든 옵션 DPS 인증 아님 |
| v178/v180 | [#40978510648](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40978510648) 후보 사이 취소 Native2→재개 신규4→캐시6. [#40980268952](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40980268952): 26×5 ilvl=130 계획 + **6세션×6=Native36 및 36 캐시**; 전체 26×모든 장비 실측 아님 |
| v181/v182 | Windows 소스 베타·실제 CMD/localhost HTTP·세션, 사용자용 기름/특수장비/제작장식/옴니움4열. 유연 룬 초기 FAIL→`136820:1` 최소 1건 교정 PASS. 이전 FAIL 숨기지 않음 |
| v196~v198 | 최고 소스 품질 영구 마부 38종 **read-only**, 9종 반지 효과군·정적 rating E 회계·2 Native 도구. v198 gear 슬롯 값만 읽어 E0으로 판단한 최초 결과는 **정정된 역사 오류** |
| v199/v200 | [#41075851509](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41075851509) **Native2** + [#41076597270](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41076597270) **기존 JSON2 SHA 재분석 Native0**: finger1 item158366/enchant8025 자연 정적 가속 **1004→1034 = +30** |
| v201 | [#41078102843](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41078102843) **Native2**: 동일 `gear_*=700` 양쪽 가속 **735→735**, 자연 E는 override에 의해 대체됨; E 숫자 재가산 금지 |
| v202 | 같은 마부의 증거 범위에서 기존 v098→v096→v093 후보 **하한 E30/프로필 SHA·cache case_key 분리**. [#41079877720](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41079877720) 제품 경로 PASS, 신규 Native0 |
| **v203 실제 적응형** | [#41083301873](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41083301873): Linux SimC `710c2408bf` 특정 **냉법334 전체 프로필 SHA `8305a811137db6f557f8076dfa44a4a1a359111d60bb7452225e1573bf72a401`**, finger1 158366/8025, **Native6/6 PASS, 고유 rating 4, B3150/T3182, 95% 비교**, 동일 세션 재실행 **캐시6/6 HIT·추가 Native0·원본 JSON2 SHA 불변**. 전역 최적·다른 조건 입증 아님 |
| **v203 호환성** | 동일 finger1의 특수 L/제작장식 중복 차단, v200/v201 정확 원본 SHA/artifact ID 고정, 전체 프로필 SHA 적용 범위 제한, 증거 누락 시 기존 시즌 38개 목록과 소비재 선택 유지. [#41084413183](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41084413183) **Ubuntu/Windows 각 21단위 + 2 패키징 PASS**, 추가 Linux 소스 확인 PASS·Native0 |
| **최신 코드 HEAD `b2d727c7`** | [Windows ZIP #41085651541](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41085651541) Windows Python3.12·3.14 SUCCESS, artifact **12991367479**; [UI #41085651522](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41085651522) Ubuntu/Windows SUCCESS; [Web API #41085651503](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41085651503) Ubuntu/Windows SUCCESS. 같은 HEAD의 v167/v177/v180은 **오프라인 SUCCESS, Native 잡은 SKIPPED**; 앞의 Native 영수증 재사용 |

사용자 Windows 실측 `V096/V094` 구 기록에는 `T=3182/B=3150`, 관측 DPS **200784.877/SEM340.631**, rating `286/1396/750/750`인 세션과, 이전 v183의 DPS **158716.23/SEM225.73**가 있다. 다른 시점/구성의 결과를 바로 '개선' 또는 '하락'으로 단정하지 않는다. 원본 profile.simc/JSON2/log 없이 티어4·장신구/proc·APL 효과까지 인증했다고 주장하지 않는다.

## 3. 아직 미완료·승격 금지

- 일반 사용자 **Windows 마부 선택 UI는 비활성**, 마부 38종 read-only. Windows 바이너리의 해당 마부 Native 값 실측, 다른 37마부/다른 아이템레벨·장비·특성·전투조건의 정확 E는 미완료. v203 전체 프로필 SHA 외 E30 적용 금지.
- 마부 조건에서 **Native 중간 강제 종료 → 부분 재개**는 미실측(v203은 완료 6회 후 cache6 확인). 이미 완료된 기존 v178 후보 사이 취소·재개 증거는 재사용.
- 실사용 Windows 세션의 실제 장착 티어/무기/장신구·소모품/버프·프로필/JSON2/log 입력 정합, 전체 사용자 옵션 조합, 원본 v015/v016 직접 병합 및 설치형 EXE는 미완료. 신규 Gate나 전수 Native로 P1을 막지 않는다.
- `main`·v003 immutable·공식 Work OS/Shared State·ChatGPT Project Sources/Instructions 실제 적용/승격 **없음 또는 미확인**. GitHub v1.4.2 보충 문서 갱신이 Project UI 적용은 아니다.
- **저장소 Public 위험:** 2026-10-31 조회 시 Public. 2026-11-01 **23:24 KST** Private 복원 **확인 알림**만 등록(자동 변경 아님). 과거 Git 이력·로그·사용자 PC 증거의 외부 복제는 재비공개 후도 회수 불가. 최신 visibility 조회, 사용자 로컬 세션을 공개 repo에 업로드 금지.

## 4. 장·단기 로드맵, 최단 효율 대안

**장기:** 미래 절대 CHMV rating·DPS/SEM/95%·실질 대안·캐시/취소·재개를 **DPS 26개**에 제공하는 Windows 일체형 사용자 흐름. 원본 적응형 v094/SimC 사용, 장비 추천/독립 효과 모델로 확대 금지.

**단기, 새 채팅 첫 턴 아님—사용자 `진행` 이후:** (1) 기존 영수증을 먼저 활용해 Windows 동일 마부의 **한 조건만** 최소 정적 Native·`gear_*` 비교(필요 시) 및 사용자 기존 JSON2/profile/log 입력 진단을 묶기; (2) 기존 L/E 충돌·캐시·증거 누락 fallback·Windows UI/HTTP를 **한 묶음 오프라인/CI**로 검증하고 정확한 선택지부터 활성화, 미증거 옵션은 잠금; (3) 변경된 코드만 Windows/Ubuntu focused 회귀 후 배포. 이미 PASS한 Linux v203 6+6, v180 36, 26 기본 물리, v178 취소 재개를 다시 실행하지 않음. 각 변경 때 Native·API 호출 중복, 실행시간, 메모리/I/O·GitHub artifact, 소스 구조 단순화, 세션 identity를 평가.

## 5. 인계 준비에서 실제 갱신/미갱신

- `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` v203 상단 **구형 27 DPS 표기→26**.
- `docs/V203_ENCHANT_8025_CROSS_FEATURE_AUDIT_AND_POLICY_ADDENDUM.md` 구형 27 DPS 표기→26.
- `docs/DEVELOPER_NOTES_v1.4.2_LATEST_USER_POLICY_ADDENDUM_20261030.md`에 v203 실측·E/L·정확 증거·미승격 **§5 추가**. v1.4.1 원문/Project UI 수정 아님.
- **본 정본 인계 문서**에 상태·로드맵과 시작 프롬프트 통합. 기타 v183/v162 인계는 역사로 보존. **이번 인계 준비 신규 Native0·새 CI0·최적화 코드 변경0**.

## 6. 새 채팅 시작 프롬프트 — 이 절을 그대로 복사

> 너는 **SIMC SECONDARY OPTIMIZER** 기존 주 제품 개발 채팅의 후속 담당자다. **이번 첫 응답은 상태를 읽기 전용으로 복원·검증하여 간결히 보고한 뒤 중단하라. 내가 '진행'이라고 하기 전에는 구현·파일 쓰기·커밋·GitHub Actions 재실행·Native·패키징·main/Project UI/공개상태 변경을 하지 말고 대기하라.**
>
> 정본은 GitHub `degong2-code/simc-secondary-optimizer-runner` 격리 브랜치 `probe/chat-cache-v035-20261024`의 **`docs/CHAT_CONTINUITY_HANDOFF_20261031_V203.md`**이다. 최신 HEAD와 visibility를 조회한 후 이 문서 **§0 읽는 순서**대로 CURRENT 상단/v1.4.2 §1·§5/v203 감사/Windows 안내를 읽어라. 정확 Native 6+캐시6 [#41083301873](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41083301873), v203 호환성 [#41084413183](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41084413183), 최신 HEAD Windows [#41085651541](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41085651541)/UI [#41085651522](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41085651522)/Web [#41085651503](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41085651503)을 구분하라. **최신 사용자 승인: DPS 26개(증강·탱커·힐러 제외)**, 첨부 LAST-CHAT 및 구형 v1.4.1의 27개는 역사 오기.
>
> **장기 목표를 지속 점검하라.** 미래 목표 ilvl266~344(기본334)/수동 최종 T에서 치명·가속·특화·유연의 최적 **절대 rating**을 SimC DPS로 찾고 비율·SEM·95% 판정·실질 근접 대안·취소/재개·정확 SHA 캐시를 제공하는 Windows 제품이다. 일반 장비/무기/티어4는 내부 생성, 장신구2·선택 특수효과·장식0~2·보석/소모품/전투 조건만 사용자 선택. `T=G+J+F+O`, O는 고정·중복가산 금지, 특수 L과 Native 마부 E는 기존 G 안의 서로 중복 없는 고정 하한. 전역 최적 증명과 95% 국소 판정 분리. SimC proc/APL/DPS 엔진 재구현/새 Gate 금지.
>
> v203 Native/캐시 PASS는 **정확한 Linux 냉법334·item158366/enchant8025·전체 프로필 SHA 한 조건**에만 해당하며 사용자 Windows 마부 UI는 잠겨 있다. **독립 작업을 묶어 처리하고 동일 기준 완료 검증을 재사용하라.** 새 Native는 실제 변경으로 무효화된 최소 조건만, 이전 v176/v180/v178/v203 Native·UI/Windows PASS를 전수 반복하지 마라. 모든 코드 수정마다 중복 계산·캐시·메모리/I/O·시간/구조 단순화 검토. `main`, v003, Project UI·Work OS, 공개상태 변경은 별도 사용자 권한. 11월 1일 23:24 KST Private 복원은 확인 알림일 뿐 자동 전환 아님.
>
> 첫 보고에는 **HEAD/visibility·승인 정책·완료와 PASS 적용 범위·미완료/미승격·장단기 로드맵·가장 효율적인 다음 묶음**을 포함하고, 보고 후 **반드시 내 '진행'을 기다려라.**
