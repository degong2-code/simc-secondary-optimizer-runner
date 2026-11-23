# P1 v689 — 실 70961 음식 선택 후 기존 Native adaptive DPS/SEM/95% 결과 및 재열람

2026-11-24. 직전 격리 HEAD `e3b48dd9282ce866319652569ab09d6a22538e01`. 최신 사용자 지시 `진행`으로 앞서 검증한 선택 음식의 실제 SimC DPS 연결을 진행.

## 범위와 책임

이미 Windows v688 [#45223542078](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45223542078)에서 소스 일치 설치 `f96ed468a74f877ef2ceecd0ae57846b01335aebc890cb86cb2e176b04481bf5`, food35/potion1, 선택 `blooming_feast` 정확 1회, API GET/POST HTTP200, B=T=3107, 새 사용자 Native0를 확인. 기존 원본 stage는 임시이며 설치 JSON artifact만 복제하여 Native를 허용하지 않는다.

기존 `v610.run(postinstall=...)`와 `v688.followup`를 **한 시즌 빌드+선택 세션으로 다시 실행**. 이미 성공한 v688 확인 뒤, `V689_REAL_USER_DPS_ONCE=true`인 이번 정확 커밋에서만 **기존 `v106.worker(folder,binary,revision)`**를 호출한다. 기존 stage-sealed `v218/v098`, `v096.run_manifest`, `v094` 적응형 6 Native 상한을 그대로 재사용. 자체 Native engine/통계/food effect Gate 작성하지 않음.

성공 수락은 같은 v212 설치 SHA/ B/T / `food=blooming_feast`를 가진 사용자 실제 SimC 프로필로 v106 워커가 PASS, 동일 세션의 원래 v113 `GET /api/v1/sessions/{id}/result`에서 절대 CHMV rating 합계 T, DPS 양수, SEM ≥0, 95% 판정, 관측 1순위/근접 대안 배열이 확인되고, 새 v113 서버에서 결과를 읽어도 내용·봉인 결과 SHA가 바뀌지 않음. SimC가 실제 실행 중 받아들이는 효과 계산은 SimC 책임이며 자체 효과 인증 게이트 추가 안 함.

필수 시즌 원본 Native가 여러 번 재발할 수 있는 이유는 이전 v688 원본 workspace 임시 폐기. 기존 source-bound CLI cache와 같은 실행 원본 stage만 재사용하고, 실패 시 **첫 실제 차단 이유**만 기록하여 또다시 불필요한 전수 원본 수집/Native 반복을 STOP한다. 기존 6-case adaptive 상한 보존, 64회 장기 실행/26전문화 일괄 Native 없음.

## 보고 경계

- 신규 [v689] 커밋에만 기존 v611 workflow 의 한 job을 조건부 동작, 새 workflow 생성 없음. 기존 v688 profile-only 모드는 유지; source/E0 Native/역사적 v610 반환 semantics 호환.
- 결과 artifact는 전체 프로필·사용자 원본·바이너리/비밀키가 아닌 선택 item ID/token, 설치 SHA, 프로필 SHA, user Native calls, 관측 rating/DPS/SEM/95/대안 수, 재열람 비교 결과만 보존. 실패면 원본 SimC 오류는 기존 워커 로그에, 상태 artifact는 제한된 코드로 보존.
- 95%는 *관측된 두 후보 간 방향 지지*이며 전역 최적 증명이 아님. 핵심 예산 `G+J+F+O`, 기름 O 및 L/E 중복 방지 불변.
- 제품 전체 `full_product_e2e=PASS` 선언은 전체 사용자 UX 수락과 다른 미검증 범위가 있어 하지 않는다. 공식 `15/78 COMPLETE`는 완료율이 아니며 `next_review=B10`, 개인 PC v677 시험 보류 및 기존 main/v003/v016/Project UI/Work OS/주 제품 개발 채팅 권한 그대로.

이 문서는 코드 경로 계획이며 **Windows Actions 완료 영수증 전에는 실제 v689 Native PASS를 주장하지 않음**.
