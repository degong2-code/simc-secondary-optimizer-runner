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

## 실제 v689 Windows Actions 및 자체 생성 원본 ZIP 영수증 — PASS

실행 커밋 `14fb5da51c8bd13ae4fa0a778a903c6aec22acd2`; [Windows Actions #45227006628](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45227006628) 한 번 SUCCESS. 이전 소스 바이트가 아니라 기존 `v610`의 자체 실제 원본 Season Build를 실행하고 같은 실행의 native source-bound Windows SimC CLI cache를 재사용. 미리 만들어진 이전 설치 문서/원본 stage 주입하지 않음.

아티팩트 `p1-v689-real-70961-optional-user-native-dps-once` #14844787176의 실제 JSON 두 파일 `V688_REAL_70961_OPTIONAL_USER_PROFILE_ONCE.json`, `V688_REAL_OPTIONAL_USER_STAGE.json` 및 Windows job 로그 확인:

- 게임/SimC: `12.1.5.70961` / `9933ffb946fb55b1fa66657b848f519ac19006e1`; 실제 새 v212 설치 SHA `dfaf381217c19229b338274a97c4d6a5a4321cf1ab5360ed107fab6d5a23b970`. 이는 v688 당시의 `f96e...` 설치와 **별도의 새 설치**, 한 user Native run 안에서는 동일 SHA를 유지함.
- 공식 설치 예산: `G=2850`, `J=92`, `F=165`, `O=0`, `B=3107`, `T=3107`. 설치 `food=35` / `potion=1`. Blooming Feast ID `242273`, SimC token `blooming_feast`, source quality rank `0`, 정확 한 번 표기. 증강 미해결은 BASE를 차단하지 않음.
- 원래 사용자 v113 exact installed catalog GET HTTP200 → plan POST HTTP200 → 원래 `v106.worker` exit=0 → `v094` **PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE**, **6/6 후보 Native**, cache hit0. 이는 소모품 포함 실제 SimC 프로필로 Native가 완료됨을 의미하지만, 개별 효과가 어떤 경로에서 적용됐는지 독립 메커니즘 인증하지 않음(SimC가 담당).
- 관측 1순위 절대 rating: 치명 `736` / 가속 `736` / 특화 `735` / 유연 `900`, 합계3107. DPS `158317.48307790104`, SEM `247.27365039703332`. **95% 선택 확인 후보 방향 지지: False(미확정)**. 전역 최적 입증 아님.
- 실질적 다른 근접 대안 **2**: (치명425/가속1047/특화735/유연900) DPS `157460.3`, `OBSERVED_NEAR_UNRESOLVED_AT_95`; (치명1047/가속425/특화735/유연900) DPS `156838.0`, `OBSERVED_NEAR_BUT_LOWER_AT_95`. 대안 수는 검색된 후보 범위이지 글로벌 공간의 전수 목록 아님.
- 사용자 결과 API HTTP200, 새로운 웹 서버 앱 인스턴스에서 동일 저장 세션 `GET /result` HTTP200으로 같은 결과 확인. 최종 결과 JSON SHA `59a9c9cef88fccb0eae189799640bfbb9595e359b52cc5dae89a2dafb58ce3ea` 변경 없음. 실제 사용자 프로필 SHA `1ffacb73a0010f6399016ed942337ad3005ce0ce88df894b0287dc2fbb772186`; 저장 전체 프로필/비밀키를 artifact에 내보내지 않음.
- native 비용은 원본 시즌 구축 `15`, 새 사용자 DPS `6` = 합계 **21회**, 신규 수집 단 1 build, 사용자 개인 PC 시험 0, 64후보/26전문화 Native 전수0. 재열람은 추가 Native0.
- 검증 범위는 **일반 사용자의 정확 설치 → 음식 선택 → 사용자 SimC Native DPS 및 저장 결과 재열람 1개 시나리오**. 통계는 95%만 사용. 새 시즌 품질 효과 전체 숫자 비열등성, 추가 전문화 전체, 모든 옵션의 Native, 실제 PC UI 수작업 수락 등은 여전히 미완료.

**실제 receipt 메타데이터 발견/정정:** v688에서 원래 `user_optimizer_executed=False`로 시작한 플래그를 v689 성공 후 True로 고치지 않아 실제 archive 안에 False가 남음. 단, 같은 archive와 log에 워커 exit0, Native 6/6, user DPS/SEM 및 결과 재열람 증거가 일치하므로 측정 성공 자체는 사실. 해당 과거 receipt는 변경/재서명하지 않고, source code가 실제 worker 호출 후 True로 기록되게 수정. **새 Native 재실행 0**, 변경 후 별도 같은 예산 Native PASS 주장하지 않음.

## STOP

정확한 Blooming Feast의 이번 user Native + 95% 결과는 실증됐으므로 **동일 70961 원본 수집/6 Native를 다시 수행할 필요 없음**. 기존 캐시·결과 UI 유지, 사용자 첫 화면/서버 재시작 및 필수 시즌 설치 갱신 동선의 남은 UX를 중점적으로 검토. 공식 `15/78 COMPLETE`는 전체 제품 완료율이 아니며 `full_product_e2e=PENDING`, `next_review=B10`, PC v677 시험 보류와 main/immutable v003/v016/Project UI/Work OS/주 개발 채팅 authority 불변.
