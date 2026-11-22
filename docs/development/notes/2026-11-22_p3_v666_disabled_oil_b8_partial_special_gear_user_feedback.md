# P3 v666 — 사용자 개인 PC v665 화면 4건 추가 피드백

2026-11-22 KST · 격리 브랜치 `probe/chat-cache-v035-20261024`

## 실제 사용자 제보와 코드로 확인한 원인

1. `최적 스탯 찾기` 버튼이 비활성화된 사유가 보이지 않음. `app.js::buttonState`는 `state.token`, 준비 중/실행 중, 목표 ilvl, 현재 시즌 설치 연결, 장신구 2개 유무 등을 단일 `disabled`로 축약하고 안내를 따로 생성하지 않았다. 클릭 불가능한 요소의 hover tooltip만으로 해결하지 않는다.
2. 기름 `사용` 시 `무기 기름 사용이 선택되어 있지만 ... 검증된 전체 무기 조합이 없습니다`. 이는 SimC 효과/예산 O가 검증된 손별 아이템 조합과 연결되지 않으면 실행을 중단하는 기존 보호 동작이다. **미승인 기름을 자동 선택하거나 검증 없이 O=0으로 바꾸지 않는다.** 이 케이스는 검증 환경 준비 또는 사용자가 명시적으로 `미사용` 선택.
3. 사용자 화면에는 특수효과 장비 후보가 10개만 나타남. `drawInlineEquipment`의 최대 80개 렌더링 상한에 걸린 것은 아님. 서버는 **정확한 v212/v213 설치 원본에 포함된** `special_effect_gear_candidate`만 노출한다. v167 응답은 `full_season_completeness_confirmed: false`이며, 시즌 전체 특수효과 아이템이 빠짐없이 수집됐다는 입증이 없다. 역사 v167 packaged 70575의 14개를 70961의 누락 항목 또는 승인 선택지로 혼용하지 않는다. 실제 누락 범위는 동일 시즌 원본 수집/분류의 별도 조사 대상이며, 이번 수정에서 ID를 추측해 추가하지 않는다.
4. 기름을 `미사용`으로 바꾼 뒤 `WEB_SELECTED_B8_PROFILE_OR_STATIC_VARIANTS_PENDING` 오류. 서버 `LocalJobs.plan`의 `selected_fresh` 분기는 **선택한 특수효과 장비 또는 장식이 있을 때만** 진입한다. 따라서 해당 코드 자체는 O=0 검증 에러가 아니고 **선택 장비의 정적 스탯 변형·최종 SimC 프로필 근거가 부족하다**는 별도 차단이다. 직접 원인인 `bootstrap.preview_from_environment_build` 상태를 이제 static variant 미확정과 season profile 입력 누락으로 구분한다. 단, 스크린샷만으로 어느 세부 상태가 발생했는지는 확정할 수 없다. 기존 정적 L, 최종 SimC 캐시/시즌 바인딩을 임의로 충족시켜 통과시키지 않는다.

## 범위가 제한된 변경

- `runner/webui/app.js`: 버튼 비활성 사유를 `optimizer-submit-note`에 상시 표시. 장신구 미선택·중복, 시즌 설치 필요, ilvl 범위, 서버 연결·동시 작업, 검증되지 않은 기름 ON 등을 정확한 액션으로 설명. 시즌 환경 미준비 상태는 **버튼으로 준비 가능하게 유지**하고, running/busy일 때는 반드시 잠금.
- 기름 OFF 변경 시 확인된 O=0 설치 SHA만 재연결. 기존 양수 O 설치본이 읽기 목록에 없어져도 O=0으로 가정하지 않도록 보수적으로 invalidation 처리. 명시적 `oil_main/oil_off` 체크 및 정확한 물리 ItemID는 비우며, 출처 미확정이면 `선택 환경 검증·준비` 안내. 실행 가능했던 이미 검증된 O=0 설치본은 불필요하게 무효화하지 않는다. 무기 기름 기본 사용 의도는 변경하지 않음.
- 특수효과 장비 목록에는 정확한 현재 후보 수와 검색 일치 수, 전체 시즌 완전성 미입증을 명시한다. **장비 전체 DB / 구매 추천**으로 기능 확장하지 않는다.
- `runner/v113_local_web_api.py`: 기존 실행 전 `v098` 선택 프로필 preflight 결과의 `B8_SELECTED_PROFILE_STATIC_VARIANTS_PENDING_NO_NATIVE` → `WEB_SELECTED_B8_EXACT_STATIC_VARIANTS_PENDING`, `V216_TO_V098_SOURCE_PROFILE_PENDING` → `WEB_SELECTED_B8_PROFILE_SOURCE_PENDING`. 둘 외에는 과장 없이 기존 일반 보류 코드로 응답. `blocked()` 기존 안전한 경로만 전달하며 선택된 SimC 원문·프로필·경로·비밀키를 HTTP에 노출하지 않음.
- UI에서는 B8을 '기름 미사용 실패'로 오역하지 않고, 선택 장비의 정적 캐시 또는 원본 프로필 미확정임을 알려준다. 필요한 근거가 없으면 해당 선택 조합의 실행은 계속 차단. 검증된 일반 대표 장비만으로 확인하려면 특수효과·장식 선택을 해제하고 실행할 수 있으나 사용자 장비를 무단 제거하지 않음.
- `runner/webui/index.html` / `styles.css`: 버튼 사유를 `role=status`, `aria-live=polite`, 텍스트 명시, hover 의존 제거, 반응형 가독성 보강.
- 새 `tests/test_v666_user_feedback_readiness_oil_b8_coverage.py`: 실제 JS 조각으로 oil ON 미검증/명시적 OFF/장신구 누락/시즌 준비/동시 작업/잘못된 ilvl의 버튼·사유, B8 코드/미확정 장비 목록 표기 검사. v568 UI 계약 갱신, 기존 v114 O=0 선택 재사용 회귀 보존. Windows v181 기존 실행/패키징 검증에 추가.

## 검증 경계와 남은 구현

- 이번 변경은 Native DPS 호출·G/J/F/O 신규 수집·전수 장비 DB 구축을 요구하지 않는다. 기존 시즌 정적 캐시와 예산/캐시·취소·재개·95% 통계, 26 DPS 최적화 범위 유지.
- **미구현**: 모든 특수효과 장비의 현 시즌 누락 없는 원본 등록, 선택 B8에 누락된 실제 정적 변형의 Native/캐시 측정 및 최종 프로필 완성, 미검증 손별 기름 O의 실제 시즌 등록. UI와 오류 안내 개선은 이들 기능의 완료 증거가 아니다.
- 메인 채팅의 개발 소유권, GitHub 격리 원칙, main/v003/Project UI/Work OS M0/공식 15/78 조건 변경 없음.

## 최종 검증·배포 영수증
- [Windows Beta v181 Actions **#45029795299 SUCCESS**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45029795299): Win2022 Python 3.12·3.14 **각 336 tests PASS/0 FAIL**, packaging 5 PASS, 실제 Windows CMD 압축 해제/로컬 HTTP 보안/3계획 복원 PASS. Native DPS 신규 호출 0회. Windows ZIP 원본은 286개 소스 파일 + 정확한 manifest 1개이며 포함된 286개 SHA256과 ZIP CRC 모두 검증 PASS.
- [v113 Local Web API Windows+Ubuntu **#45029795353 SUCCESS**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45029795353), [v182 UI Windows+Ubuntu **#45029795294 SUCCESS**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45029795294), [v180 130 오프라인 source-first **#45029795301 SUCCESS**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45029795301), 실제 Native 6-case SKIPPED.
- 배포: [GitHub Actions ZIP artifact #14756992592](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45029795299/artifacts/14756992592)의 중첩 wrapper를 제거한 **`SIMC_SECONDARY_OPTIMIZER_v666_WINDOWS_BETA.zip`**, **1,525,280 bytes**, SHA256 **`099acb940b1afc4022c549f5743d9724542c116891d859ff5987c818dbafe04a`**. 실행 파일(simc.exe)·사용자 캐시 미포함. 실제 사용자의 Windows 기름/장비 조합을 새 Native로 실행했다는 증거는 아님.
- 초기 테스트의 오래된 `설치 SHA` 정확 문구 요구 및 이전 `start-btn` 조건 문자열 검사로 인한 FAIL은 유효한 source/예산 차단 자체가 아닌 **테스트의 UI 표현 계약 드리프트**였음. 기존 O=0 중복·불일치 원본 차단 정책은 유지한 채 검사를 새 사용자 안내·차단 조건으로 보완했으며 최종 PASS를 확인.
