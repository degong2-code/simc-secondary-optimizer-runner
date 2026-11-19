# P1 v620 — 실제 설치된 E0 영구마부 → 부위별 웹 선택창 (2026-11-19 KST)

## 정확한 완료 범위

**제품 최종 목표는 26개 DPS 전문화의 미래 목표 ilvl(기본 334)/수동 CHMV T에 대한 절대 치명·가속·특화·유연 rating SimC DPS 최적화**다. 장비 조합 추천이나 현재 장비 재분배가 아니다. 이번 변경은 **v618의 실 시즌 70961 영구 마부 19개 자동 등록 및 v619의 실제 마부 7957 사용자 Native DPS·SEM·95% PASS**에 이어 **웹에서 마부를 고르는 기존 사용자 입력 경로**를 보강한 것이다.

이전 UI에서는 `season_enchant_other` 통합 선택이 실제 v212 서명 E0 후보를 제어했지만, 바로 옆에 표시된 `env-enchant-helm/shoulders/chest/boots` 부위별 선택창은 항상 `disabled`였다. 이 때문에 등록된 19개와 사용자가 시각적으로 누르는 부위별 선택칸이 일치하지 않았다.

**코드 변경:**
- `runner/webui/app.js`: 기존 v113 `verified_installed_enchant_registrations`에서 **동일 설치 SHA 및 정적 `verified_fixed_E={crit_rating:0,haste_rating:0,mastery_rating:0,versatility_rating:0}`, 정확한 부위, 유효 CHMV 영수증**을 통과하는 선택지만 부위별 머리/어깨/가슴/장화 셀렉터에도 자동 표시. UI는 인증·승인 주체가 아니다. 최종 `v106.enchant_choices`는 이미 지원된 `season_enchant_other` 값의 `slot:enchant_id` 검증 경로를 **동일하게 재사용**한다.
- `synchronizeInstalledEnchantChoice`는 부위별 셀렉터 → 일반 통합 셀렉터를 미러링하고, 반지·다른 일반 부위를 동시에 선택한 경우에는 이전 값을 해제. `v106/v098/v096`의 **한 번에 마부 1부위** 제한을 변경하지 않는다. 기존 `start/resume/cancel` 또는 DPS 엔진을 변경하지 않고 기존 session identity로 기록된다. 서버는 실제 마지막 대표 장비의 ItemID·마스크·부위·enchant_id 정확 1회·CHMV 예산을 매번 검증.
- 설치 SHA/게임 빌드가 바뀌거나 API가 실패하면 `renderSeasonOptionCatalog(null)`에서 모든 부위별 신규 선택을 원래대로 잠근다. 미검증/고정 E 미확정·E>0/실물 손 및 무기 범위 미검증 항목을 활성화하지 않는다. 저장된 옛 세션 입력은 표시할 수 있어도 최신 시즌 승인으로 전환하지 않는다.
- `runner/webui/index.html`: 사용자가 읽는 조건 문구를 실제 정책에 맞게 변경. **마부 전투 효과·proc·품질별 DPS 인증을 별도 Gate로 요구하지 않음**, 효과와 DPS는 SimC 전담. 기존 일반 장비 통합 선택은 부위별 선택창과 호환되도록 유지한다.

**회귀 검증:**
- `tests/test_v114_local_web_ui_offline.py`의 기존 v467 서명된 E0 발 마부 실제 UI 노출, 다른 부위 잠금, SHA 변경 및 API 실패 후 재잠금, 정적 E+ 차단·미확정 E 차단.
- 신규 v620 Node 기반 **실제 소스 함수** 검증: head/shoulders/chest/feet 한 번에 1개 선택, 기존 공통 마부 요청 필드 미러링, 반지 선택과 상호배제, 임의의 미서명 ID를 전달하지 않음. 기존 v600 필드 유효성·v464 저장세션 restoration 테스트는 함께 유지. 과거 v464 테스트 목 객체에 신규 DOM 셀렉터 4개를 추가했으며 제품 실행 로직 실패가 아닌 fixture 차이.
- [v113 Local Web API #44442806896](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44442806896) **Ubuntu+Windows SUCCESS**.
- [v182 실 웹 UI/API 오프라인 #44442806922](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44442806922) **Ubuntu+Windows SUCCESS**.
- [공통 오프라인 #44442806947](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44442806947) **SUCCESS**, [장비/적응형 계약 #44442806981](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44442806981) SUCCESS, [78 원장 #44442807078](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44442807078) SUCCESS.
- 초기 기존 `v464` DOM fixture가 새 ID들을 몰라서 [v113 중간 SHA](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44442616567) Ubuntu test FAIL, fixture 보완 후 위 최종 Windows+Ubuntu **PASS**. 실패 숨김 금지.

## 남은 것과 권한

- **새 UI 클릭으로 특정 실제 사용자 세션을 시작→취소→재개하는 브라우저 E2E와 실 신규 Native**는 이번 v620에서 별도로 하지 않았다. 이미 [v619 실제 70961 마부 7957 → 최종 chest 268222 → SimC Native 6회](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44440673155) 및 DPS·SEM·95% 실증이 있으므로 같은 scope Native 전수를 반복하지 않고 **검증된 소스/캐시를 재사용**할 것.
- 검증된 선택지라고 해도 `v212` 설치 SHA와 최종 실물 부위를 일치시켜야 한다. 새 시즌 Build 시 G/J/F/O를 다시 검증하며 수동 T가 우선, L/E/O 중복 가산 금지.
- **현재 마부 선택은 한 부위 E0**로 제한된다. 다부위/양수 E, 다른 무기 손, 추가 사용자 UI 옵션은 정확한 정적 회계와 현재 프로필 연결 근거 없이는 승인하지 않는다. 전체 제품 `full_product_e2e=PENDING`; 공식 `15/78 COMPLETE`는 변경하지 않는다.
- **신규 SimC Native 0회, 신규 시즌 Wago/DB2 수집 0, GitHub Actions 바이너리 컴파일 0**, 기존 캐시 무효화 0. 변경은 GitHub 격리 브랜치만; main 병합·immutable v003/v016·Project UI·Work OS/Shared State 승격·주 제품 개발 채팅 소유권 변경 없음.
