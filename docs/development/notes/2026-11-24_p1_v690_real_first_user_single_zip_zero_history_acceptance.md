# v690 — Windows에서 단일 ZIP, 빈 사용자 환경, 최초 UI·시즌·실제 SimC로 이어지는 제로베이스 시험

2026-11-24. 최신 사용자 결정: '내 환경이라고 생각하고 제로베이스 시험' 요구. 격리 브랜치 기준 `9107504f5fc339d06cd30a0b8d5e47878a939bee`.

이전 증거: v640(실 ZIP 첫 웹 의존성·사용자 동의), v570(빈 세션→Chrome 시즌 구축→생존 사냥꾼 DPS64), v639(추출 ZIP→70961 Chrome64·결과 재열람), v689(70961 징벌 성기사+Bloo­ming Feast API→Native6/DPS SEM95) **각각 다른 실행**이다. 이를 한 번의 사용자 초기 설치 흐름으로 합칠 수 없다.

이번 수락 실험은 기존 `v181`의 **현재 HEAD 동일 소스 ZIP**을 만들고 `v573`의 실제 Windows BAT/venv 동의 취소·승인·pip 설치·Chrome 첫 화면을 재사용한다. 추출 뒤 원본 역사 데이터는 격리(이전 시즌 값 사용 금지), 사용자 HOME/LOCALAPPDATA/run/managed-SimC 비어 있어야 한다. v573의 신규 opt-in before/continue hooks 기본값 None으로 역사 동작/회귀 불변.

같은 실행에서 신규 브라우저가 UI의 **Blizzard/WCL 인증정보**를 사용자처럼 등록하며 비밀키를 로그·보고서·ZIP에 포함하지 않는다. Windows 공개 SimC **'자동 확보·설치'** 버튼을 실제 클릭하며 **기존 70961 바이너리를 주입하지 않는다.** 설치가 되지 않으면 `PENDING_PUBLIC_SIMC_NOT_INSTALLABLE`로 정확히 중단한다. 성공한 경우 **흑마법사/파괴**로 앞선 두 전문화와 다른 대상을 선택하고, 기존 원래 첫 클릭 `v113/v216/v217/v212`로 빌드 자동 확인 → 실제 같은 SHA 설치 → 원래 사용자 목록 장신구 두 개 선택 → 원래 최적화 버튼을 사용한다. 정상 조건에선 기존 사용자 장기 적응형 Native64, DPS/SEM/95% UI 표시까지 같은 창에서 확인. 새로운 Native/효과 엔진·모의 HTTP·수동 예산·과거 GJFO 값 주입 없음.

**CI에서 미리 제공되는 전제:** Windows 2022, Python3.12/Chrome, Github Actions Secret에 적법하게 사전 저장된 소스 API 인증정보와 인터넷 연결. 이는 개인 PC 설치(winget·Windows 권한·가정 네트워크) 증명은 아님. 바이너리는 자동 다운로드가 되는 경우에 한해서만. 새 게임 빌드 원본 G/J/F/O가 미검증이면 정상 READY로 승격하지 않고 원래 첫 차단을 기록. 실패 시 동일 시즌 원본/Native를 무조건 반복하지 않으며 첫 원인만 수정한다.

검증 영수증: ZIP 파일 SHA/동의 검증은 v573의 기존 bounded 리포트; v690은 신규 사용자 원본 세션과 실제 UI 상태·선택 전문화·SHA/B/T·최종 화면 DPS/SEM/95%에 한해 기록. 비밀키/세션 개인 정보/소스 원본/프로필 전체 절대 수집하지 않음. 실제 Native 결과는 단 하나의 최초 성공 시나리오이며 새 시즌/26전문화 완전 범용성 증명 아님. `15/78 COMPLETE`와 `full_product_e2e=PENDING`, 개인 PC 시험 보류 및 main/v003/v016/Project UI/Work OS 권한 불변.

**실행 증거가 없으면 어떤 PASS도 주장하지 않는다.**

## 첫 실제 Windows #45230565019 — 패키징 선행 차단, 원본/Native 0

[GitHub Actions #45230565019](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45230565019)는 새 ZIP 빌드 전 `V181_MINIMUM_PRODUCT_RUNTIME_FILES_MISSING`로 실패했다. `v181_windows_beta_packager.py`가 항상 `data/current_season_source_to_catalog.json`을 과거 packaging source metadata로 요구하지만 새 체크아웃에는 해당 바이너리/과거 소스가 없다. 다른 런타임 모듈은 존재함을 repo 파일 목록으로 확인. 이번 실행은 사용자 화면·Native 이전에 종료되어 *사용자 제로베이스 PASS가 아니고* Native0, 소스 수집0.

**최소 원래 계약 재사용:** 기존 정상 `v181_windows_beta_packaging.yml`과 동일하게 과거 **봉인된 v213 read-only source artifact** #13104842881 (Actions #41360273361)를 ZIP **메타데이터 생성 단계에만** 바인딩한다. 압축 해제 직후 사용자 앱이 시작되기 **전에** v690이 해당 역사 소스 파일을 별도 격리 폴더로 이동/삭제하여 최초 시즌 빌드와 세션이 과거 내용을 소비하지 못하게 한다. 사용자 준비물도, 새 시즌 원본·G/J/F/O 인증도 아니며 역사 70783(?) 수치를 새 시즌으로 복제하지 않는다. 현재 `v181` 패키저 자체의 역사 메타데이터 의존성은 범용 패키지 설계 과제로 명시적으로 남긴다(한 번의 시즌 Build 실행 경로와 분리). 신규 원본 Native 호출은 아직 없고 수정 후 실제 1회 Actions 결과가 나와야 통합 성공 여부를 판정한다.

## #45231076160 — 현재 ZIP 286개 패키징 PASS, 시험 인자 오류 차단

기존 역사 `v213` 패키징 전용 source artifact를 정상 복원·검증하고, `v181` **286파일 현재 HEAD ZIP 생성 PASS**. 그 다음 첫사용자 실행 시작 전 `p1_v690...stage(args)`가 `argparse.Namespace`를 폴더 경로 객체인 것처럼 `pathlib.Path(out)`에 전달해 `TypeError`. 제품 SimC/환경/native 모두 호출 0. 실제 사용자 실패가 아닌 신설 harness의 범위 한정 오류. `stage(args)`에서 명시 `args.out`을 쓰도록 1곳 수정. 같은 ZIP을 새 사용자 런타임에서 검증하는 목적 유지, Native 중복 0. 다음 run 결과만으로 첫 사용자 제품 성공을 판정.

## #45231378708 — 실제 제로베이스 ZIP·동의·Chrome 첫 화면 PASS, 인증정보 패널 미전개 차단

Windows [Actions #45231378708](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45231378708), artifact #14846088982의 원본 `V573_...` + `V690_...` 확인: **286파일 현재 HEAD ZIP**, 역사 파일13개 런타임 전 격리, 빈 사용자 세션/managed SimC, 사용자 동의 거절 상태 미설치→승인 실제 pip/venv 설치→실제 Chrome 첫 화면/26개 전문화 표시 성공. 이후 인증정보 입력 전에 `ElementNotInteractableException`: UI 인증정보 필드가 `<details id=season-credentials-panel>` 안에 있는데 신규 Selenium 시험이 summary를 열지 않고 키를 입력. 상품이 오류 메시지를 표시하거나 데이터 구축을 거부한 것이 아님. 신규 harness에서 **실제 패널 summary 클릭 후 입력**하도록 교정. 다음 오류 지점은 비밀키/SimC 소스 원문 노출 없이 `last_completed_stage`로 추적. 인증정보는 Windows Credential Manager에 쓰였다면 로컬 안전한 /clear API로 사용자 시험 종료 시 삭제; 토큰 자체는 JSON이나 로그에 기록하지 않는다. 이 시점까지 시즌 Native 0·DPS Native0, 실제 SimC 자동 설치와 새로운 전문화 원본 구축 여전히 미검증.

## #45232046418 — 새로운 공개 SimC 실제 자동 설치 PASS, 시험의 화면 전환 누락

원본 [Windows Actions #45232046418](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45232046418) 및 실제 ZIP artifact #14845689656: ZIP286, 과거 시즌 원본13개 앱 시작 전 격리, 새 HOME/LOCALAPPDATA, 처음 사용자 취소→승인→pip/venv/Chrome 첫 화면, 실제 사용자 UI를 통한 보안 저장소 API 키 등록·시험 후 삭제 **PASS**. 사용자 사전 실행파일/기존 관리 SimC 주입 없이 UI **SimC 자동 확보·설치 성공**: `PUBLIC_SELF_BUILT_BINARY_INSTALLED`, 게임 `12.1.5.70961`, revision `6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7`, 설치된 바이너리 SHA `1195a3401a716c9f28b4de113d228cc3a669aebf83c0c47e5989db521d87c3c9`. 공개 자체 빌드가 최신 게임 빌드와 맞더라도 아직 시즌 G/J/F/O·DPS Native 증명은 아님.

다음 단계 실패 위치 `last_completed_stage=SIMC_ONE_CLICK_RETURNED` + `RuntimeError`: 신규 harness가 **설정 화면에서 숨겨진 클래스/전문화 visible listbox를 직접 찾으려 했음**. 실제 앱 UI 설계에 따라 먼저 `navigate(driver,"optimizer")`로 탭 이동한 뒤 원래 `choose_visible_search`로 클릭하도록 정정. 기존 v344/V570 자체 검증 코드의 안전한 내부 오류 코드만 추가 기록해 단계별 원인 식별성 확보. 제품 코드·Native·시즌 캐시 변경0, 지금까지 새 시즌 수집/Native0. 후속 실행에서 실제 사용자 시즌 구축 및 Native가 가능하지 않으면 해당 첫 제품 차단 이유만 기록하고 반복하지 않는다.

## #45232773634 — 사용자 실제 전문화 선택 단계 Timeout, 원인 분기 검사만 보강

[v690.4 Windows Actions #45232773634](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45232773634), 원본 아티팩트 #14846743961: ZIP/첫 웹 동의/비밀키 입력 및 삭제/현재 빌드 SimC 원클릭 자동 확보까지 PASS. `last_completed_stage=VISIBLE_OPTIMIZER_TAB`에서 `TimeoutException`. **신규 시험이 사용한 실제 visible class/spec combobox의 정확한 현재 상태/라벨을 기록하지 않아** 자료 부족으로 제품 검색 UI 오류인지 harness 대기 조건 문제인지 구분 불가능. 기존 제품 JS/Native 변경 대신 한 번의 다음 시험에서 실제 활성 탭·클래스/전문화 검색 입력 존재/disabled·class options의 UI 공개 라벨·검색 이벤트 후 마지막 정상 단계를 bounded JSON에만 기록하도록 시험 진단 강화. 비밀키·원본 전문 데이터/비공개 내부 문자열/HTML·개인정보 수집 없음. 실제 GJFO 시즌 구축/DPS Native는 아직 0, 원본을 반복 수집하지 않음. 다음 정확 첫 결손이 나오면 해당 UI 경계만 해결하며 반복적인 전체 시즌 실측 Native는 STOP.

## #45233714558 — 실제 흑마법사/파괴 class/spec 검색 성공, 다음 초기 UI 클릭에서 Timeout

[GitHub Windows Actions #45233714558](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45233714558), artifact #14848526190 원본 진단: 현재 286 ZIP/새 사용자 동의/비밀키 저장 및 cleanup/공개 70961 SimC 설치 PASS, 실제 optimizer 탭, `choice-class-choice` 및 `choice-spec` 존재·enabled, class UI에 **흑마법사 라벨** 있음. `last_completed_stage=SPEC_SELECTED`, 즉 실제 검색 목록에서 클래스·전문화 선택 두 단계 성공. 이후 `TimeoutException`은 다음 사용자 초기 UI 동작 중 발생, 환경/사용자 Native0. 신규 Selenium helper의 입력/선택 레이블 문제가 아니었음. 상품 엔진/원본 변경 없이 같은 함수의 실제 기름 체크박스·첫 시즌 버튼 단계별 상태만 기록해 다음 재현에서 **첫 클릭을 특정**할 것. 이미 70783/70961 이전 다른 전문화의 oil UI 동작 증거를 재활용하고, 원본 수집/Native는 아직 한 번도 호출하지 않았다. 테스트의 실패를 제품 버그라고 임의 지정하지 않음.

## v690.7 — 숨겨진 체크박스 대신 사용자 가시 메뉴 사용, 저비용 선행 검증

[#45234577569](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45234577569) v690.6 영수증에서 `failure_after_stage=OIL_BUTTON_BEFORE_CLICK` / `oil_input_visible=false` / `oil_input_enabled=true` / `oil_initial_checked=true` / `TimeoutException` 확인. 정확 실제 UI `runner/webui/index.html`의 `optimizer-oil-enabled`는 `hidden aria-hidden` 내부 미러이고, 일반 사용자가 조작하는 컨트롤은 `optimizer-oil-use-mode` 선택 메뉴(`use`/ `off`)다. `app.js`는 visible select의 `change` 이벤트를 기존 `applyOilUseToggle`에 연결하므로 **제품 로직은 수정하지 않는다**.

새 harness는 Selenium `Select(oil_mode).select_by_value("off")`로 사용자에게 보이는 '미사용'을 선택, `state.busy`가 끝난 뒤 visible menu=off 및 hidden mirror checked=false를 읽기 전용으로 검증한다. 실제 사용자 키보드/마우스 조작에 부합하며 내부 요소를 직접 click하지 않는다. 원본 시즌 G/J/F/O, Native/SimC 결과 계산, ZIP 및 캐시 알고리즘 변경 없음.

재차 전체 Windows ZIP/SimC 자동 설치를 실행하기 전에 기존 v690 workflow의 **패키징 앞 단계**에서 `tests/test_v690_visible_oil_user_contract.py` focused 3개 검증(HTML visible option, JS change wiring, Selenium visible Select 코딩)을 먼저 실행한다. 정적 계약은 Chrome 실제 UI 조작 PASS의 대체물이 아니며 실제 Windows Actions 영수증 이후에만 제로베이스 단계 성공을 판정. 과거 v690.6 Native0·실시즌 원본0. 개인 PC 시험·26개 전문화/신규 시즌 전수 미검증. 공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`; 기존 권한 변경 없음.

## v690.8 — 실제 사용자 기름 선택 비동기 반영·시즌 설치 scope 판정 교정

[v690.7 Windows #45236131013](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45236131013)의 기존 ZIP/SimC 자동 설치·실제 흑마법사/파괴 선택까지 성공. **새 저비용 UI 3 tests PASS**, 실제 286파일 ZIP 패키징 PASS. 실제 사용자 선택 메뉴 `optimizer-oil-use-mode`에서 `use` 상태를 `off`로 선택했지만 직후 `V690_VISIBLE_OIL_OFF_NOT_APPLIED`가 발생함. 실제 아티팩트 #14850306538은 `VISIBLE_OIL_MODE_BEFORE_SELECT`, `oil_visible_mode_before=use`와 Native0을 확인하며, 변경 후 `mode/checked/state.busy`는 미기록이어서 비동기 기름 카탈로그 반영 경합인지 실제 UI 처리 오류인지는 아직 확정 불가.

**선행 원본 코드 대조:** `runner/webui/app.js`의 class/spec 변경 핸들러가 `void withBusy(refreshInstalledOilLoadouts)`를 실행할 수 있고, visible oil 사용 변경 시 `state.busy`면 메뉴를 원래 intent로 되돌림. v690.7 harness는 전문화 선택 직후 바로 mode 조작·단발 `wait_idle` 검사를 해서 이 상태와 경합 가능. 따라서 제품 로직 변경 없이 (1) 전문화 변경 비동기 처리 완료까지 기다리고, (2) 사용자 visible select의 `off` 선택, (3) mode=off/hidden O mirror checked=false/busy=false를 완료까지 40초 재확인하며, (4) 실패하면 제한된 공개 `mode/mirror_checked/busy/status`만 기록한다. 재현 뒤에도 실패하면 제품 버그와 테스트 비동기 문제를 분리하여 첫 원인만 수정한다.

**다음 설치 단계에 대한 독립 코드 대조:** 기존 harness의 `showSeasonEnvironmentBuild` hook은 `e.environment_ready`/`e.environment_installed`을 참조했으나 실제 제품은 `e.web_environment_scope.environment_ready` 및 `.environment_installed`이 authoritative. 수정된 실 검사도 제품에서 사용하는 *그 동일 필드*로만 READY 판단해 정상 원본 설치를 허위 PENDING으로 만들지 않도록 했다. 원래 v216/v212 예산·원본·Native/캐시·제품 UI 코드는 변경하지 않음.

이 단계는 유효한 하나의 실제 Windows 첫사용자 시나리오 수락을 위한 harness 정확도 개선이며 새 Native/효과 인증 독립 Gate가 아님. 세 번째 재시도 이상 원본 시즌 Native 반복 방지 원칙 유지. 이번 v690.7까지 사용자 원본/Native 0, 전체 E2E PENDING. 공식 15/78, next_review B10, 개인 PC 보류·기존 승인 권한 변경 없음.

## v690.9 — focused 3건 테스트의 JS 개행 비교식만 수정

[v690.8 Windows #45237038136](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45237038136)는 현재 원본 ZIP 생성/브라우저/Native 호출 이전 **추가한 선행 정적 회귀 3개 중 1개 FAIL**: 기대 문자열이 `getElementById('optimizer-oil-enabled').checked`로 한 줄이어야 한다고 잘못 가정. 실제 harness는 같은 객체의 `.checked`를 다음 줄에 표기한 올바른 JS이다. 나머지 HTML visible control/JS change wiring focused 2개 PASS. 테스트 문자열을 공백·줄바꿈을 허용하는 정확한 대상 정규식으로 변경. 제품 코드·harness 동작·원본/시즌 캐시/Native 변경 0. 실제 제로베이스 결과는 다음 GitHub Actions 영수증 이후에만 확정한다.

## v691 — 원본 영수증에서 확인한 최초 진단 단절 (제품 J/F 원인 미확정)

2026-11-24. v690.9 #45237310462 artifact #14849293119의 두 JSON 원본과 v689 #45227006628 artifact #14844787176의 두 JSON 원본을 직접 읽었다. 실패 requires에는 FOUR_ORDINARY_TYPES_SAME_BUILD_SOURCE_PENDING, SELECTED_AUTO_GJFO_V271_PHYSICAL_GEM_J_NUMERIC_PENDING 및 SELECTED_AUTO_GJFO_SELECTED_FLASK_NATIVE_RATING_PENDING이 존재한다. v690 환경 Native3, 사용자 DPS0. v689의 실제 G2850/J92/F165/O0와 G/J/F/O owner 모두 존재, 설치 성공 및 Native6은 다른 정확 revision의 역사 증거이다. v610 및 v690은 같은 v113.build_season_environment→v216 경로를 사용하며 70961 nominal JSON은 repo에 없고 70783만 존재. 신규 revision 자체, 파서, 보석 품질 순위, F 정적 delta 중 무엇이 원인인지는 단정하지 않는다.

기존 v216은 이미 J metadata/DBC/Native preview, F source selection/pair 및 J/F numeric/quality owner 사유를 반환한다. 기존 v690 receipt는 requires 및 상태만 보존해 실제 내부 첫 결손을 구분할 수 없다. 따라서 기존 브라우저 response에서 boundedJF projection으로 그 필드만 추출한다. 원본 전문·경로·raw native log·인증정보는 보존하지 않는다. 기존 UI/제품 코드·예산/승인·캐시·Native 엔진 변경0. 실제 동일 JS projection에 J/F failure, 비밀/로그 제외, missing, numeric fixture를 적용해 확인(실제품 실증 아님). 원본 stage가 과거 bounded artifact에 없고 동일 공개 자동 설치 바이너리/작업공간도 보존되지 않았으므로 현재 기존 one-shot을 딱 1회만 재사용해 원래 결손을 특정한다. 새 workflow/수집기/독립 Gate 없음. 결과 전 J/F 복구 또는 제품 E2E PASS 선언 금지. 공식 15/78, B10, full_product_e2e=PENDING, 개인 PC 보류 및 권한 불변.

## v691 후속 — 원본 확보 이후 공통 Native 실행 실패, 좁은 비교 시험

#45313992491 완료 FAIL, 원본 artifact #14884308203: J v221/v230 후보75개, pinned DBC FOUR_LEADING_CHMV_TYPES_INCOMPLETE, J v278 SIMC_ORDINARY_GEM_NATIVE_FAILED_NO_AUTO_RETRY (1회), F 실제 ID241320 선택 성공 후 SIMC_CONSUMABLE_NATIVE_FAILED_NO_AUTO_RETRY (1회). G1 포함 환경 Native3, DPS0. v689 설치 원장 #14845336340 F ID241320 / flask_of_thalassian_resistance_2. 즉 원본 수집 및 F 선택 자체를 재개발할 필요 없음. v278 결과에 native_error=null인 경우 subprocess 비정상 종료 또는 JSON2 미생성 가능; 해당 receipt의 native_status/variant/returncode/raw log가 보존되지 않았으므로 구체 원인 미확정. 실제 v573/v216 경로 구성을 이용한 Windows CI 길이 추정 stage root197, v277 output255, v278 output263. 전체 신규 시즌 시험을 반복하지 않고 기존 v690 workflow의 별도 opt-in job에서 기존 공개 exact binary SHA 1195a340...를 한 번 확보해 동일 공개 대표 무기 기반 통제 profile의 v278 baseline을 짧은/긴 경로에 최대 2회 실행한다. 짧은 control 실패면 STOP. 사용자 데이터/인증정보·Wago·Blizzard·WCL·새 시즌 구축·DPS 최적화 없음. 이는 실제 제품 원인 입증 또는 J/F 승인 자체가 아닌 좁은 가설 확인이며, 결과를 보기 전 제품 코드/캐시 변경하지 않는다. 기존 v691 focused/78 SUCCESS, 공식 15/78/B10/full_product_e2e=PENDING 및 권한 불변.

## v692 — 공통 v278 Windows 경로 결함의 통제 재현 및 국소 수정

#45316228437 artifact #14885606192 원본: same exact binary SHA1195a340..., same controlled public profile. input124/json2 125 chars exit0 NATIVE_JSON2_CAPTURED; input262/json2 263 chars exit60 NATIVE_FAILED, SimC `Error: Incorrect option format: Unable to open input parameter file ... input.simc`. Native2/season_collection0/DPS optimizer0. 이는 Windows 경로 가설의 통제 재현이며 과거 v690 J/F 실측 오류 원문과 직접 동일함은 아직 확인되지 않았다. 기존 v278 Windows 긴 경로(>=260)만 cwd 상대 input.simc/native.json 사용, 해당 변경 호출에만 io_mode identity를 추가하여 기존 짧은 경로 cache/영수증과 기존 실패 attempt를 변경하지 않는다. 같은 새 identity 재호출은 기존 cache 사용. 실제 기존 Windows long path만 1회 실행, 이전 short control PASS 재사용, 전체 ZIP/원본 수집 없음. focused fixture와 실제 native 수리 결과 미확인 상태. J/F 설치 및 제품 E2E는 PENDING. 개인 PC 시험 요구 없음, 공식 상태/권한 불변.

## v693 — 상대 파일명 실패 확인, 실제 짧은 실행 경로 사용

2026-11-24. #45316688570 artifact #14885800452 직접 읽음: long_fixed input262/json2 263 chars, stage197, io_mode=cwd_relative_v1, Native1, exit60, SimC `Error: Incorrect option format: Unable to open input parameter file 'input.simc'.` NATIVE_FAILED; 시즌 수집0, DPS0. 신규 focused/78 SUCCESS 및 Windows mock1 PASS와 실제 Native 실패를 구분. 따라서 상대 이름만 줄이는 방식은 기각. 이전 실제 짧은 경로 성공을 재사용하여 v278 long Windows case에만 실제 short TEMP cwd 적용. 실행 input bytes는 canonical sealed folder와 동일, stable relative JSON2 filename, exact JSON2를 원래 폴더에 복사, 원래 receipt/hash/log/attempt lock/일반 short path 유지, temp는 종료 시 정리. TEMP가 짧지 않으면 Native 전 명시 오류. 기존 실패 receipt를 덮어쓰지 않는 새 io_mode; 새 identity 반복은 cache hit. 추가 원인 재현 또는 별도 Native path probe 대신 기존 v690 실제 사용자 흐름 1회, focused precheck(새 scratch 경로·cleanup·SHA·재실행0) 후 실행. J/F 진단은 failed_variant/native_status/native_returncode와 제한된 실제 Error lines 보존(known local roots/secrets redacted). 원본 수집, 효과/계산/승인 정책은 수정하지 않음. 신규 Windows product result와 실제 비용 PENDING, 개인 PC 요청 없음, 공식 상태 15/78/B10/full_product_e2e=PENDING 및 권한 불변.

## v693.1 — Windows 사전검사 경로 비교 수정, 제품 재변경 없음

#45317848502 job #138188914308 원본 로그: Windows precheck에서 test_v278 line149 `self.assertTrue(path.is_relative_to(root))` FAIL. 동일 test의 mock process 2회, F108, cache Native0, scratch cleanup, io_mode assertions는 앞에서 통과했으며 뒤의 input/JSON2 hash assertions는 미실행. ZIP 생성 전 중단, 실제 환경 Native0, DB2/시즌 수집0, 사용자 DPS0, artifact 없음. 제품 코드가 원본 stage root를 resolve하는 사실을 기준으로 시험 양측을 resolve하여 동일 파일 위치를 비교한다. TEMP alias는 유력한 설명이나 실제 Windows 별칭 문자열 미수집으로 확정하지 않는다. 실제 제품 수리 PASS는 아직 미확인. 기존 workflow의 테스트 파일 path filter 추가 후 opt-in 1회만 실행. 새 제품 변경, 별도 Native probe, 승인 조건 변경, 개인 PC 요청 없음. 15/78/B10/full_product_e2e=PENDING 및 권한 불변.

## v694 — 첫 사용자 연속 실행 PASS, 개인 PC 후보 준비

#45318051264 job #138189588432 SUCCESS, 원본 artifact #14886722098: 기존 13 source 격리, 새 AppData, 내장/주입 SimC 없음, 실제 Chrome 동의 설치·자동 SimC 연결(6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7 / SHA1195a3401a716c9f28b4de113d228cc3a669aebf83c0c47e5989db521d87c3c9)→12.1.5.70961 ilvl334 J92/F165/O off, B=T3107 (G2850 역산), Native15(J3/F2), core missing0, requires[], v212 installed READY SHA d2fb21b7873007f5bcf739e48d17d7f7e1eb7a340772c8c7db244bef4b551170. 파괴 흑마법사 장신구270161/270160, exact installed SHA request, 실제 start/worker result UI DPS157131.6 SEM181.25 95% 미확정, session hash b67fcc6f331e7f6f1d6a2b31d2fcea0c0a9cfa9cbe8c13070fdc749c5e9aa3b1, setup exit0, credentials cleared. v693 수정으로 J/F 차단 해소. 원본 new_dps_native_calls=0는 초기값, worker Native count 미수집, last_completed_stage 미갱신: 과거 artifact 보존, 향후 DPS 시작시 null 및 결과 단계 기록. 26 DPS 전체/다른 시즌/기름 양수·수동 T/개인 PC 이번 증거로 확장 금지. 기존 v181 ZIP을 동일 tested HEAD 및 SHA6862a73920d3dd727b82e31f5b4069db9abbf17fcd61c5d39ae3c73d22567c4d로 재현하고 실제 pre-launch quarantine 13개 제외, 나머지 273개 exact bytes 재포장/manifest 갱신/후보 SHA. 패키지 자체 실행 재검증 없이 개인 PC review 후보. 추가 시즌·Native·전체 E2E0, 제품 코드 변경0, 공식 15/78/B10/full_product_e2e=PENDING 권한 불변.

## v694 사용자 시험용 배포 후보 생성 완료

#45319502242 SUCCESS, artifact #14886533851 직접 확보. `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA_V693_1_FIRST_USER.zip` 1,452,985 bytes, SHA256 9c6a200210eac417015fbf98f32fa975d80c9dcaa87f12829d83e46d8defbacd. 기존 실증 parent ZIP SHA6862a73920d3dd727b82e31f5b4069db9abbf17fcd61c5d39ae3c73d22567c4d 재현 성공, pre-launch quarantine 13개 제외, 잔여 273개 payload 정확한 SHA 및 ZIP CRC 별도 확인. Native0, 시즌 구축0, 제품 변경0. 후보 ZIP 직접 전달, 개인 PC 최초 실행·사용 편의성·실사용 오류 확인 요청. 기존 Windows CI의 동일 실행 payload 증거를 활용하며 후보 archive 자체의 재실행 또는 개인 PC 완료를 주장하지 않음. 기존 PC 세션/캐시 삭제 불필요. 공식 상태/권한 불변.

## v695 — 개인 PC 실제 사용자 평가와 1차 수정

사용자 캡처: 초기 자동 시즌 요청 V216_UNQUALIFIED_MULTIPLE_INSTALLED_FJ_VARIANTS_SELECT_EXACT_SHA, build 직접 입력(12.1.5.70961) 후 동일 표기의 F165/J92/4소켓/O0 두 설치본이 보임. 검증환경1 연결 후 장신구 Gebbo's Bottomless Bag/Wavecaller's Seastone 선택 및 실제 22/64 진행, 최종 관측 DPS168805.6 SEM228.32 T3107, CHMV 1327/225/1390/165, 56 observed unique/6 alternatives, 95% 미확정. 기존 개인 PC 설치본 재사용 경로 PASS(사용자 캡처/보고; raw Native count/receipt 미수집), 신규 개인 PC zero-history build는 미검증. 사용자 요청: 탱커 장신구 유지, 장신구와 특수효과 목록 확대, 부위별 상세 중복 선택 숨김, 결과 4bar 전체폭 및 대안 rating 같은 글자 크기. UI: hidden parent로 8 internal slot rows/automatic assignment/restoration 유지; max-width880 제거, 13px alt rating, 11/2 counter 숫자 덧셈. Source: v165 current M+ provenance의 이전 expansion 차단을 user trinket/special에 한정 해소; old/unscoped item과 internal G/craft/tier unchanged. v163 raid/M+/craft source 및 v216 compile_pool(...,None,...) optional delve 제외 확인. 이 결함이 개인 PC의 모든 누락을 설명한다는 주장은 금지. 정확한 item list 차이와 보충 원본 범위는 후속 분석. 자동 current build 수집과 복수 FJ 표시/선택 cycle 및 이름 누락 문제는 다음 해결. 추가 Native0, 시즌 재수집0, 신규 scoped tests PENDING. 사용자에게 동일 최적화 반복 요청하지 않음. 공식 상태 권한 불변.

## v696 — 자동 빌드 확인과 기존 환경 선택 분리

v695 HEAD c77b7353의 12 workflow 모두 SUCCESS 확인 (v165 #45327255743, v113 #45327255678, v181 #45327255568, focused #45327255535, 78 #45327261776 포함). 실제 개인 PC의 자동 빌드 실패는 v113에서 이미 Retail KR 조회 후 v216 복수 설치본 예외가 build identity를 제거하는 흐름으로 확인. 해당 자동 오류에만 live build/SHA/ilevel/READY=false 안전 detail, UI는 요청 scope 일치 시 기존 local GET 1회로 FJ 목록을 표시하고 선택 화면 이동. 사용자가 게임 빌드 입력할 필요 없음; 정확한 설치 SHA 선택은 유지하고 READY/예산/프로필 연결은 원래 경로만 담당. 신규 focused server/JS 회귀 PENDING, 신규 Native0·DB2 수집0. 목록 확대는 v695의 active M+ 원래 expansion 필터 결함 수정 통과, 설치된 v212/v213 바이트 불변이며 사용자 기존 목록 자동 교체 미구현. Localbots 보충원본의 실제 시즌 귀속/이름-only 해결 및 중복 설치본 의미 비교는 남음. 별도 E2E/개인 PC 반복 없음.
