# P3 v647 — 환경 설정·결과 확인·2차 스탯 최적화 UI 공통 서식 조정 (2026-11-20)

**사용자 직접 승인 방향:** 환경 설정에서 과도하게 제거한 선 일부는 큰 구획용으로 복원한다. 결과 확인과 2차 스탯 최적화에서는 개별 행·컨트롤의 중복 구분선을 줄인다. 전역 진행/결과 상태 표시줄은 기존 테두리+음영 박스 대신 예산 입력 영역의 **좌측 강조선 + 명확한 텍스트 + 매우 약한 하이라이트**로 나타낸다. 개발/패키징 및 상태 표기는 이전 v646과 분리한다.

## 실제 수정 범위 (제품 코드)

- `runner/webui/styles.css`: v361/v363의 **실제 기존 선택자**를 고쳐 누적된 장식 규칙을 정돈했다. 최종 파일 끝에 광범위 `!important` 덮어쓰기를 추가하지 않았으며, 기존 focus/hover/disabled 의미와 원래 컴팩트 그리드 구조를 유지한다.
- **전역 `#notice`**: CSS `.notice`의 사면 border/radius/채운 박스를 제거하고 왼쪽 3px 골드 강조선·은은한 단방향 tint·적정 font-weight로 대체. `.notice.error`는 분홍빛 좌측 강조로 차별화. `setNotice()`, `textContent`, role=status/aria-live 및 전역 공지 대상·정체성은 불변.
- **설정 `#view-settings`**: 큰 패널(시즌 환경/SimulationCraft) 사이 1개 약한 separator와 여백을 복원. 고급 시즌 설정·SimC 관리 부분에는 문맥상 필요한 얇은 상단 구분선 1개씩만 보존. 개별 폼 필드/버튼을 가로질러 늘어난 full-width 밑줄은 복구하지 않음.
- **결과 `#view-results`**: panel의 매 영역 bottom border 제거, 대형 섹션 사이/section-head에만 은은한 separator 유지. 진행/세션/복원 그룹은 의미 있는 상단 경계만 남기고, metrics DPS·SEM과 95% footer, 대안의 각 숫자별 border-bottom/right 삭제. 관측 DPS는 얇은 좌측 강조선, 대안 여러 행 사이에는 한 줄만 유지. empty state 아래 빈 선 제거. 기존 `dps`, `sem`, `conf95`, `budget`, `stat-bars`, `alt-list`, session/longrun 이벤트·DPS/95% 실데이터는 불변.
- **최적화 `#view-optimizer`**: 최적화 환경 상태줄을 박스형 대신 좌측 2px 강조선과 약한 배경으로 변경; 주요 profile/conditions/gear 구획과 section-heading, 장비 종류 사이의 선만 계속 유지. 입력·선택 필드는 매번 하단선보다 짙지 않은 배경 면으로 그룹화하고, 해당 필드 focus 경계는 분명하게 보존. fold/gear-row 및 장비 후보 아이템·체크박스/자동 값·마법부여 선택의 과도한 매행 밑줄 제거. 입력 레이블·행 높이·모바일 그리드·장신구/특수장비 버튼 클릭 ID는 보존.
- `runner/webui/app.js::seasonBuildRecoveryPlan`: 사용자 PC에서 나온 `V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH`의 화면 제목을 `SimC 세트 효과 원본의 빌드 정보를 확인하지 못했습니다.`로 바꾸고, 세트 효과 데이터 헤더/빌드 확인이 중단된 것임을 쉽게 설명. 코드는 **보조 기술 진단**으로 후미에 표시. `게임 빌드 불일치가 확정된 것은 아닙니다`를 명시하여 분류 증거를 과장하지 않는다. 네트워크 접속·revision·원본의 문제는 별개일 수 있으며, 저장된 설정 자체의 READY/증명으로 승격하지 않는다.

## 검증 기준과 경계

- 신규 `tests/test_p3_v647_visual_hierarchy_offline.py`: 실제 CSS 셀렉터와 기존 HTML의 유일 ID·live status·DPS/SEM/95% 데이터 타깃·세 화면 의미 있는 구분선과 미니멀한 행 표시 보존, Node에서 실제 `setNotice` 상태/오류 변경 동작을 시험.
- 기존 Windows v181 workflow의 동일 세션/보안/UI/HTML+real loopback/소스 ZIP 패키징 테스트에 연결. 공식 Native/DPS 0회; 새 시즌 원본 수집·검증·G/J/F/O/예산/캐시·API·session JS 변경 없음.
- CSS 정적/기능 테스트는 브라우저에서 사람이 보는 최종 미관·가독성 인수와 다르다. 이미지가 필요한 별도 미리보기는 만들지 않고 사용자 PC 검토에 따라 세부 여백/명암을 최소 조정한다.
- 편집한 원본 화면은 CSS·1개 사용자 복구 안내 문구뿐. 결과 확인 화면의 실제 stat/결과 시맨틱, 95% 유의성 및 global-optimum disclaimer 삭제·변경 없음. 새 독립 검증 Gate/SimC Native 전수 작업 없음.
- 소스 수정 및 시험 증거는 격리 브랜치에만; main·v003 immutable·Project Sources/UI·Work OS 공식 승격 금지. 공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` 유지.

## 실행 결과

- 최초 [Windows beta v181 CI #44676987811](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44676987811)는 v361 역사적 테스트가 **반복 fold/gear-row 밑줄을 반드시 유지하라는 구 디자인 규칙**을 요구한 탓에 기존 288 PASS / 1 FAIL(기능·DOM 결함 아님). 기존 테스트 자체를 삭제/비활성화하지 않고, 실제 CSS의 주요 `section-head` separator 유지 + fold/gear-row 반복선 제거라는 새 사용자 승인 기준으로 기대값 수정. 해당 테스트 변경 시도 Windows ZIP CI를 다시 실행하도록 Workflow `paths`에도 추가.
- 최종 [Windows beta v181 #44677378569](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44677378569): Windows Python **3.12·3.14 양쪽 모두 SUCCESS**, 각각 패키징 **5 PASS**, 기존 웹/세션/보안 및 신규 3-view UI 계약 **289 PASS**, 실제 ZIP 압축 해제+CMD launcher+localhost HTTP 3가지 계획 PASS, 이번 변경으로 신규 Native/DPS 호출 **0**.
- 최종 ZIP artifact [#14603195195](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44677378569/artifacts/14603195195): 내부 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip`, 바이트 **1,500,443**, SHA256 `debb25affa7e0539f2197a267deb5286d566b57510cec1d3412e838b28edfdd2`. ZIP 내 `V181_PACKAGE_MANIFEST.json` 283개 소스 파일 각각 **283/283 SHA·bytes 일치**, ZIP CRC 검사 PASS; 사용자 세션·SimC 실행파일 미포함.
- 비주얼 인수 한계: CI는 CSS/DOM/기능의 정적·모의 검사와 실제 Windows localhost 실행을 확인했으나 사용자 PC의 실제 디스플레이 렌더링/미적 확인까지 대체하지 않는다. 과거 Native 근거를 새로 실행한 것처럼 주장하지 않는다.
