# v115 · P1-WEB-3 특수장비 입력 확대 / 실제 대표 보석 색상 구성 (격리 브랜치)

**상태: 구현 커밋·focused 오프라인 테스트 코드 추가. 새 CI 실행 PASS 및 사용자 실제 Windows Edge/Chrome 실기는 아직 미확인. 신규 SimC Native 실행 0회(이번 변경 수행 범위).**

## 사용자 직접 승인 내용

- 특수효과 비장신구를 HTML UI 최대 **2 → 8개**로 확대. 이 8은 기존 `v106`/`v098` 사용자 계약의 상한이며 게임 아이템 종류의 영구 정책이 아님. 장식은 최대 2개 유지.
- 실제 일반 보석 6개를 SimC 대표 장비 소켓에 유지. `Powerful Eversong Diamond (240967)` 선택 시 **Garnet/Amethyst/Lapis/Peridot** 4종 보석 색상이 장착된 상태를 만들어 SimC에 전달. 필요 색상은 보석 **item ID**에 의해 결정되며 CHMV 스탯 이름 4개와 다름.
- 일반 보석 CHMV `J=6×23=138` 자유배분 예산 유지. 사용자가 보석 6개/전체 장비를 전수 입력하지 않으며 `gear_*`가 최종 정적 rating을 한 번에 덮어써 보석의 초기 스탯 종류를 고정하지 않음. Diamond 효과는 SimC 소유이고 별도의 proc/APL 인증 Gate 없음.

## 변경 범위

- `runner/webui/app.js`: 특수효과 장비 2개는 기본 표시, 추가 6행은 필요한 경우 버튼으로 순차 개방; 전체 최대 8개. 장식 최대 2개. HTML DOM API로 구성하고 실행/재개 호출 경로는 불변.
- `runner/v101_common_representative_equipment.py`: 기존 장비의 `gem_id`가 있으면 선택 특수/제작장비의 동일 슬롯에 기본 상속. `240967`일 때 일반 보석 6개의 실제 `gem_id` 슬롯을 열거해 누락된 보석 색상만 기존 관측 고품질 (+16/+7) 4색 ID에서 보충. 이미 4색이면 프로필 무변경; `240983`와 같은 색상 조건 없는 다이아몬드는 원본 구성 유지. 물리 슬롯에 실제 소켓을 확보할 수 없는 경우 `REPRESENTATIVE_SIX_ORDINARY_GEMS_REQUIRED`로 Native 이전에 차단.
- `runner/v098_target_user_scenario_bootstrap.py`: 변경 보석 구성을 **Native 실행 프로필 생성 전에** 확정해 프로필 해시·조건 identity가 추적되도록 함.
- `tests/test_v101_common_representative_equipment.py`: 기존 6개 소스 조합 4색/6보석, 240983 비변경, 특수장비 교체 슬롯 보존 검증 추가.
- `tests/test_v114_local_web_ui_offline.py`: HTML UI 8행 동적 확대 및 2장식 기존 계약 정적 회귀 추가.

## 기존 영수증·실기와의 경계

- 기존 사용자 Windows 징벌 334 · `240983` 세션 `abca493c00d6ee2599f1`은 읽기 전용 재조회 대상이며 수정·재해시·재실행하지 않음. 이전 사용자 Native6/6 및 캐시6/6 증거는 과거 증거로만 재사용.
- **신규 코드 변경 후 실제 Linux/Windows CI PASS는 아직 미확인.** 이번 변경 작업으로 새 Native·DPS·SEM 수치가 생성되었다고 주장하지 않음.
- `240967` 사용 및 임의 선택 특수장비의 모든 실제 Native SimC 효과 발동을 독자적으로 재검증하지 않음. 우리의 책임은 보석 ID·색상·개수·slot/입력·최종 rating 정합, SimC는 효과 계산 책임.
- 이미 존재하던 동일 조건/동일 세션의 과거 실행 프로필과 새로운 4색 프로필이 충돌한다면 영속 파일 `put_once` 보호를 우회하지 않고 중단하며, 이전 cache를 덮어쓰지 않음. 이 경우 실제 관측한 회복 경로만 후속 교정한다.

## 후속 P1-WEB-3

1. 사용자가 새 폴더에 격리 브랜치 **전체**를 다운로드 (개별 파일 교체 금지).
2. `py -3 -m pip install -r requirements-web.txt` → `py -3 runner/v113_local_web_api.py --port 8765` → `http://127.0.0.1:8765/`.
3. 기존 세션 `abca493c00d6ee2599f1`를 **열기 GET만** 수행하고 결과/브라우저 새로고침 복원 확인. 새 SimC 실행, resume, cache-only, 취소 클릭 금지. 기존 runs/SimC exe·캐시 보존.
4. 필요한 focused CI 확인 및 사용자 브라우저의 **관측 결함만** 교정. Native 호출·중복 실행·캐시·I/O·메모리·실행시간을 점검하며 기존 v098→v096→v094 엔진 불변.
5. 이후 WEB-4 더블클릭/설치형 웹뷰 진행. main/v003/공식 Work OS M0/Shared State/Project UI 미변경.
