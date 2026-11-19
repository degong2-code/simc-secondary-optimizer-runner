# P1 v623 — 제품 목적·실행비용 감사 및 완료 결과의 중복 HTTP/DOM 조회 STOP

2026-11-19 · 격리 브랜치 `probe/chat-cache-v035-20261024` · v622 이후 사용자 직접 요청 **“프로그램 목적과 취지에 맞는 비효율 없는지 확인”**에 대한 최소 제품 소비 경계 수정.

## 1. 목적·이미 성공한 경계

- 제품 목적은 **26 DPS 전문화, 목표 ilvl 또는 수동 최종 CHMV T에서 실제 SimC DPS를 최대화하는 최적 관측 절대 rating**과 SEM/95%/근접 대안을 제공하는 일반 사용자 프로그램이다. AI 런타임 0, 현재 장비 재분배/장비 추천/전 시즌 DB/독립 효과 엔진은 범위 밖.
- 실제 원본 **[v570 70783 Chrome 64 DPS+결과](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44074372451)** artifact `V570_REAL_WINDOWS_FIRST_USER_PRODUCT.json`: 일반 Chrome 시작→시즌 G2850 J92 F165 O0→64 실제 Native→결과 DOM `result_visible=true`, DPS=179563.608, SEM=316.821, confidence 95%, observed alternatives 5. 이는 **70783** 증거.
- 실제 원본 **[v619 70961 선택 가슴 7957 + DPS6](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44440673155)** artifact `V619_REAL_USER_ENCHANT_DPS.json`: 70961 E0 지정→실 Native 6·DPS/SEM/95%. 내부 사용 시나리오이지 Chrome 마부 선택은 아님.
- 실제 원본 **[v621 70961 Chrome E0 취소/재개](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44445250976)** artifact `V621_REAL_CHROME_ENCHANT_CANCEL_RESUME.json`: 새 Chrome 선택→기존 원본 설치→Start→Native 2→Cancel→HTTP 재시작→동일 세션 Resume→누적 Native4. **전체 64개 결과 완료는 아님.**
- v622는 `v113.recent_sessions`의 v106-only 색인 누락을 기존 `v293.read_status`와 연결해 최종 완료만 결과 저장으로 표시한다. 새 최적화 엔진 또는 추가 효과 Gate는 필요 없다.

## 2. 이번 실제 비효율 (사용자 소비 위치)

- 일반 사용자 브라우저 `runner/webui/app.js`: `beginPolling`은 `setInterval(...,1400)`으로 **완전히 종료된 동일 장기 세션**에서도 `readSession`을 계속 호출함.
- `readSession`은 매번 로컬 `/longrun/status` + 결과 준비 시 `/longrun/result` 두 GET을 발송. `pollOnce`는 매번 `renderResult`의 스탯 바 4개와 근접 대안 DOM 전체를 새로 생성. 성공적인 최종 `BUDGET_EXHAUSTED` 후 동일 sealed 세션에 새 후보가 자동 생기지 않으므로 **제품 가치·SimC 통계 개선 없이 로컬 HTTP/파일 I/O/DOM/메모리 churn만 발생**.
- 손대지 않으면 약 `3600/1.4 ≈ 2,571`번/시간의 polling, **최대 5,142 GET/시간**(결과 준비 시) 및 반복 DOM 갱신.
- 다른 경계: **실행 중** 1.4초 진행 상황 업데이트는 사용자에게 유용하므로 유지. 중단·차단·이전 결과/현재 worker 혼동의 기존 fail-closed 정책 유지. 같은 빌드 정적 원본·SimC 바이너리·Native 캐시·시즌 G/J/F/O는 변경하지 않음.

## 3. 최소 수정

- `runner/webui/app.js` `beginPolling`에서 `state.longrunCompleted===true`이면서 `filled-result.hidden===false`인 경우에만 **반복 polling STOP**. `state.longrunCompleted`는 기존 `renderProgress`의 `BUDGET_EXHAUSTED && result_ready` 조건으로만 true.
- **안전 예외:** 서버 결과 GET/렌더링이 실패하여 결과 UI가 아직 비어 있으면 지속 조회 가능. 새 실행·복원은 기존 `markSession`/명시적 `pollOnce` 경로를 사용하고, 불완료/취소/차단/재개 상태는 polling 유지. API/Native/95% 판단/데이터·캐시 구조 변경 0.
- `tests/test_v114_local_web_ui_offline.py`에 **실제 `beginPolling` JavaScript 본문 실행**으로 완료 후 HTTP 0, 활성/미완료 시 1, 결과 표시 실패 시 재시도, 성공 후 다시 0을 확인하는 Node 오프라인 회귀 추가.

## 4. 검증·비용

- 코드 커밋: `38c517e78da86f8657bfaa5ccedfabf50e1df6d4`; 회귀: `d27d3c3b38b74805371b857282ca130a8fa4333c`.
- [v182 UI #44452897531](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44452897531): Ubuntu+Windows **SUCCESS**, 각 **205 UI tests** PASS. [v113 API #44452897694](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44452897694): Ubuntu+Windows **SUCCESS**. [v180 #44452897556](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44452897556): offline **SUCCESS**, `native-six-cases` **SKIPPED**. [78 계약 #44452897596](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44452897596): **SUCCESS**.
- 이번 **새 SimC Native 0, 게임 HTTP/DB2 0, SimC compile 0, 기존 캐시 변경/무효화 0**, 구조 추가 0, 최종 결과 수치/통계 변형 0.
- 비용 감사: 실제 최신 70961 + E0 사용자의 완성 세션 확인은 여전히 아직 한 영수증에서 입증되지 않았다. 기존 v570의 70783 전체 64 결과와 v619 70961 E0 6회, v621 70961 Chrome 부분 4회를 합쳐 **새 70961 전체 PASS로 오인하면 안 된다**. 다만 제품 검증 범위가 바뀌지 않는 무조건적 새 64회·전 전문화 Native 반복은 STOP. 다음은 기존 결과 소비/재열람 UI와 v623 개선의 정확한 경계만 확인하고, 정말 단일 70961 전체 E2E 수락에 필요한 경우에만 한 번의 bounded Native를 별도로 판단.
- GitHub workflows는 소규모 UI 변경에도 복수의 **offline** Actions가 발생할 수 있으나 이 단계에서 CI 구조 변경 자체가 P1 사용자 기능을 개선하지 않으므로 신규 workflow/Gate를 만들지 않음. 향후 관련 수정 배치/기존 재사용으로 비용 통제.

## 5. 공식·권한 유지

`15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`. 격리 브랜치만 변경, main 병합/v003 immutable/원본 v016 통합/Project UI 적용/Work OS M0·Shared State 승격/주 제품 개발 채팅 소유권 변경 없음. **최종 제품 완료 선언 아님.**
