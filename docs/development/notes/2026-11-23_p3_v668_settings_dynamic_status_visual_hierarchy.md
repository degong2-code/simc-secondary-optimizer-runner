# P3 v668 — 환경 설정의 동적 상태·변경 값 시각적 위계

2026-11-23 · 격리 브랜치 probe/chat-cache-v035-20261024

## 사용자 실측 문제와 범위
- 개인 Windows PC에서 환경 설정의 설명·실제 SimC 연결 결과·빌드·revision이 같은 크기·색으로 섞여 현재 상태를 한눈에 구분하기 어려움.
- 사용자 수동 SimC 입력 revision 710c240, 실제 CLI 출력 데이터 빌드 12.1.5.70575. 과거 시즌 환경 12.1.5.70961과의 호환성은 독립 검증 대상이며 이번 UI가 일치를 입증하지 않음.
- 미래 ilvl/T 26 DPS CHMV 최적 rating과 G/J/F/O/95%/기존 Native·캐시·세션·취소·재개는 변경 0. UI 표시 전용.

## 구현
- runner/webui/index.html: SimC/시즌 결과 아래에 각각 고유한 결과 그룹 추가. 기존 상세 안내·ARIA live 경고는 보존. 공식 용어·API 자격·관리 SimC 등 고정 문구가 아닌 동적 상태에는 settings-live-status 적용.
- runner/webui/styles.css: 상태 제목 14px, 값 13px 굵게, 라벨 10px 중립, 설명 11px. 배경색 카드 남발 없이 한 줄 구분선. 완료·대기·실패는 텍스트로도 명시, 모바일 580px 이하 한 열, 긴 SHA와 숫자 줄바꿈.
- runner/webui/app.js::renderSettingsStatusFacts: createElement/textContent만 사용해 인젝션 없이 표시, 길이/개수 제한, group accessibility 유지.
- displaySimcConnectionFacts: saved 설정을 불러온 경우 CLI 재검증 전(PENDING), 실제 verified_now=true 확인 버튼 응답만 CLI 실행·저장 완료. SimC 출력 게임 빌드와 저장 당시 게임 빌드 구별; 입력 revision은 CLI 출력 일치일 때만 별도 확인됐다고 표시. 게임 시즌 일치는 별도.
- displaySeasonEnvironmentFacts: environment_ready 및 environment_installed가 모두 true이고 G/J/F/O/T 정확한 정수일 때만 최종 예산 숫자 강조; source-only 후보는 숫자로 표시 금지. 설치본 재사용 상태는 실제 서버 REUSED_VERIFIED 결과로만 표시.
- displaySeasonEnvironmentAttempt: 요청 중·오류·요청 도중 설정 변경의 세 상태를 구분해 이전 READY 증거를 현재 설정에 잘못 재사용하지 않음.

## 신규 검증
- tests/test_v668_settings_dynamic_status_readability_offline.py: 실제 JS Node 분리 테스트로 restored vs verified-now, 70575와 시즌 확인 구분, revision 독립 인증 수준, READY 숫자 vs pending/blocked 은폐, 사용자 문자열 HTML 인젝션 방지, DOM 중복 및 반응형 스타일 검증.
- Windows [#45093009034](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45093009034) Python 3.12·3.14 각각 344 PASS/0 FAIL, 286개 파일 manifest, 실제 Windows 압축 해제→로컬 HTTP·기존 3개 계획 복원 PASS, 신규 DPS Native 0회/SimC C++ 컴파일 0회.
- API [#45093009038](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45093009038) Ubuntu+Windows SUCCESS, UI [#45093008960](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45093008960) Ubuntu+Windows SUCCESS, 기존 adaptive offline [#45093009123](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45093009123) SUCCESS (Native six-case skipped), focused [#45093009083](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45093009083) SUCCESS.
- 실제 단일 v668 ZIP (GitHub wrapper 제거) 1,529,712 bytes, SHA256 c4666ca21b20da1bd60cfb94a271574d544097253d7bf832c88f5f6c56d3ea90; ZIP CRC/286개 file SHA/JS·HTML·CSS v668 markers PASS. [Actions artifact #14782331499](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45093009034/artifacts/14782331499)는 wrapper 형식, 배포 파일과 혼동하지 않음. 실제 소스 HEAD 7fef8f75f510c51922ea33d7ff0cd8d3137e451f.
- 초기 FAIL은 실제 JS 함수를 잘라 실행하는 기존 테스트가 신규 표시 전용 함수/변수 인자를 전달하지 않거나 이전 .hint 클래스 정확 문자열을 전제로 해서 발생. 테스트 연결을 갱신했으며 최종 green, 과거 FAIL을 삭제하지 않음.

## 미완료/소유권
- 사용자 개인 Windows 환경의 실제 v668 화면 렌더링은 아직 별도 확인 필요. UI는 수동 SimC 70575와 이전 시즌 검증 70961의 호환성을 자동 인증하지 않음.
- 기존 F/J 중복본 선택, B8 선택 장비 static variant, 시즌 무기 기름, 음식/물약 기본 사용, 특수효과 시즌 후보 완전성, 26 DPS E2E 모두 별도 미완료이며 이번 UI로 해결했다고 주장하지 않음.
- 전체 시즌 DB/장비 추천 기능 확대 없음. main·v003 immutable·Project Sources UI·Work OS M0·78 공식 승격, 주 제품 개발 채팅 소유권 변경 없음.
