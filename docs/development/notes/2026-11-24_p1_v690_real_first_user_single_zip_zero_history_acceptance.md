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
