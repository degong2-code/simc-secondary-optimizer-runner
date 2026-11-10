# Native·Actions 증거 지도 — 범위별 재사용

> 각 run은 당시 정확한 HEAD/바이너리/프로필/시즌/iterations 범위의 역사 증거다. 이 문서를 만드는 것은 신규 PASS가 아니다.

| 증거 원본 | 실제 범위 | 입증하지 않는 것 |
|---|---|---|
| [P2 적응형 격자·비례 정규화 문서 focused #42739383687](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42739383687), [설계 노트](notes/2026-11-10_p2-percentage-grid-proportional-normalization.md) | 격리 HEAD `8cd7259f`에서 530 tests=528 PASS/2 SKIP/0 FAIL, `DEV_LEDGER_PASS OFFLINE_NO_NATIVE_NO_NETWORK`; 개발 노트·INDEX·FILE_MAP·결정·인계 링크/정책 일관성 확인 | 문서/오프라인 회귀만; 코드 미구현, 신규 SimC Native0, 격자 DPS 우위·탐색 품질 미증명 |
| [새 사용자 상한·격자 연구 #42732836728](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42732836728), [개발노트](notes/2026-11-10_p2-user-configurable-final-stat-cap-and-grid-study.md) | 격리 HEAD `cfa7b1be` 530 tests=528 PASS/2 SKIP/0 FAIL·ledger PASS. 새 기본 60% 이하·사용자 25~100%/정확 T+O·50% 미만 구 세션 재개; v098 CI #42732685225, v113 Win/Linux #42732685036, v182 UI #42732684987 각 SUCCESS | 신규 SimC Native0, 실 DPS/격자 고점 탐색 품질 증명 아님; 변경 코드 HEAD `54a2b557` 초기 ledger 메타데이터 실패는 수정됨 |
| [P2 비율 경계 후속 #42730376972](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42730376972), [개발노트](notes/2026-11-10_p2-fractional-bounded-neighbor-proposals.md) | HEAD `f1ab1651`의 528 tests=526 PASS/2 SKIP/0 FAIL·DEV_LEDGER_PASS. B3107/B6214 상대 이동 clipping 및 0 경계·fallback 회귀 | 신규 SimC Native0. 실제 DPS 최적 조합 발견 성능·전역 최적/95% 선택편향 해결 증거가 아님 |
| [무이력 4보석 Build #42664089225](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42664089225), [노트](notes/2026-11-10_p1-four-ordinary-real-zero-history-ready.md) | 실 70783 Ret334 O0, G2850/J92/F165/T3107, Native3·검증 설치/프로필 PASS | 다른 시즌·이 구성의 실 DPS·Windows 개인 클릭 |
| [focused #42723497273](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42723497273) | HEAD 1b59ec52에서 526 tests=524 PASS/2 SKIP/0 FAIL·DEV_LEDGER_PASS | 새 Native·전문 26개 웹 E2E |
| [실 P2 Native10 #42501052586](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42501052586), [감사](notes/2026-11-09_p2-real-native-ten-case-region-audit.md) | 8 scout×35 + 2 confirm×320; 정확 당시 profile/binary/seed, **선택된 두 후보만** 명목 95% 비교 | 먼 고점 부재·family-wise 95%·전역 최적 |
| [정확 캐시 #42504040076](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42504040076) | 같은 identity Native10 재사용, 신규 Native0 | 임의 바이너리·iterations·프로필에 동일 DPS 주장 |
| [실 O32 웹 DPS #42598051977](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42598051977) | Ret334 기름 O32·수동 T3500/B3468 웹→SimC Native2 | O0 4보석 조건의 DPS로 전용 금지 |
| [기본 26/26 #40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357) | 26 DPS 기본 물리 프로필 SimC 수용 | 모든 선택지·PC·장기 Native 실사용 |
| [합성 6형상 #42611070381](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42611070381), [감사](notes/2026-11-09_p2-multimodal-equal-count-offline-audit.md) | 동일 112 제안 횟수, 5 동률/기존 1 우세/신규0 | 실제 SimC DPS, iterations·CPU 동등 |

## 판정 용어

`CODE_IMPLEMENTED` ≠ `OFFLINE_PASS` ≠ `REAL_NATIVE_PASS` ≠ `USER_WEB_E2E_PASS`. **미검증**과 **재현된 실제 결함**도 별도. 실 실행의 SHA/SimC binary/프로필/옵션/CHMV/O/iterations/전투조건 일치를 검토해 캐시를 재사용하고, 95%는 선택편향·전역 미증명을 명확히 한다.
