# P1 v624 — 실제 70961 서명 영구 마부 웹 64후보 완료·95% 결과·저장 세션 재열람 PASS

2026-11-19 · 격리 브랜치 `probe/chat-cache-v035-20261024` · 사용자 직접 `진행` 지시 후, P1의 남은 **같은 실제 웹 사용자 시나리오 최종 결과 소비** 경계만 검증. 성공한 ZERO-SOURCE/적응형 SimC/마부 자동 등록/취소·재개 구조는 변경하지 않음.

## 1. 제품에서의 정확한 위치 및 필요성

- 사용자 **징벌 성기사, ilvl334, 가슴 영구 마부 enchant_id=7957, 장신구 270175/270173, 기름 없음, 자동 최종 T** 선택.
- 실제 Chrome의 `Start` → 같은 설치 빌드의 G/J/F/O 산출·내부 대표 프로필 → 기존 `v113/v293/v291` 적응형 SimC → Cancel·HTTP 서버 재시작·동일 세션 Resume → **64후보 원래 상한 완료** → 실제 95% 결과(DPS/SEM/rating/비율/대안) → `v622` 최근 저장 세션 목록 → 서버 재시작 후 같은 결과 재열람.
- 과거 v570은 **70783**의 Chrome 64/최종 결과, v619는 **70961** 내부 E0 6 Native DPS/SEM/95%, v621은 **70961** Chrome 선택·취소·재개 누적 4회이므로, 이 셋을 서로 섞어 동일 **70961 E0 웹 최종 완료**를 주장할 수 없었음. v624에서 **필요했던 바로 그 단일 실환경 경계** 확인.

## 2. 실환경 Actions·원본 영수증

- 최종 실제 Windows Chrome [Actions #44454908607](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44454908607) **SUCCESS** (syntax-only + real-chrome jobs PASS). 원본 compact [artifact 14497471706](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44454908607/artifacts/14497471706), `V624_REAL_CHROME_ENCHANT_FULL_RESULT_RESTORE.json`, 파일 바이트 **6,740**, SHA256 `217c3e517a948d2d0d4f8223c3d3e6aec2c37827b81b83040c0b846daab1cc93`.
- 원본 `status=PASS_REAL_CHROME_SIGNED_E0_64_FINAL_RESULT_REOPEN`, 실제 Windows Chrome, live game build `12.1.5.70961` = SimC pinned source `9933ffb946fb55b1fa66657b848f519ac19006e1`.
- 정확한 Windows `simc.exe` SHA256 `4f4472ac8687d029cd7d6041741f44aa98750ea1b3e953dfa7002dee1f38879f`. 기존 v618 동빌드 바이너리 캐시 **HIT**, 신규 재컴파일 **0회**. 빌드 또는 바이너리 identity drift면 Native 실행 전 차단하는 기존 v621 preflight 보존.
- 실 설치 v212 `installed_manifest_sha256=cec60f651324fd5ce843717ad305825424fee40e0770f2f41344c014cb36bac1`의 승인 영구 마부 **19건**. 사용자가 Chrome에서 고른 `chest:7957`이 원래 UI→`enchant_choices={"chest":7957}`→동일 설치 SHA로 전달됨. v621 과거 설치 SHA와 **서로 다른 이번 실 설치 identity**이며 동일하다고 주장하지 않음.
- 이번 설치 환경 G=2850 J=92 F=165 O=0, B=T=3107; 실 환경 Native **6회**. 일반 사용자 SimC DPS Native **2회 → 사용자 취소 → HTTP 서버 재시작·동일 세션 복원 → Resume → 누적 64회**, 재열람 이후에도 **64회 그대로**, worker `BUDGET_EXHAUSTED`, 완료 후보 64/64. 기존 통계/엔진/캐시 의미 변경 0.

## 3. 실제 관측 1순위·95% 결과 (제품 그대로, 다른 성능 보장 아님)

- 관측 1순위: 치명 **944 (30.3830%)**, 가속 **792 (25.4908%)**, 특화 **1206 (38.8156%)**, 유연 **165 (5.3106%)**; 총 T **3107**. 이는 장비 추천이나 현재 장비 재분배가 아닌 미래 목표 ilvl의 **절대 rating**.
- 실제 SimC DPS **161540.4715838059**, SEM **251.7748534675002**. 브라우저 표시는 DPS **161,540.5**, SEM **251.77**, 4개 rating 줄과 근접 대안 **6개**를 원본 결과 그대로 표시.
- **95% 선택 확인 쌍의 우위 방향 미확정**(`pairwise_direction_supported_at_95=false`, UI `미확정`). 다중 선택 보정 없음, 전역 최적해 입증 아님. `confidence_level=0.95`, `global_optimum_proven=false`, `selected_pair_95_only=true`. 유리하다고 날조·과장하지 않음.
- `v622_saved_result_index_visible=true` (실제 사용자 저장 세션 목록의 `결과 저장` 노출), `browser_final_verified=true`, `http_restart_final_result_reopened=true` (같은 세션, 화면 수치·상태 동일), `native_attempts_after_readonly_reopen=64`. 원본 `V291_RESULT.json` SHA256 `14e43707167f3aa213421d64d569e392fbdbeea89e4362f2aa9010a7590bc878`은 복원 전후 불변.
- 기존 v623 완료 후 불필요한 주기적 GET/DOM 갱신 차단도 이 실제 완료 UI에서 그대로 통과.

## 4. 재사용·수정·효율 / STOP 기준

- **기존 제품 코드 변경 없음.** 기존 v621 시험의 `run(...,complete_after_resume=False)` 기본 동작을 보존하면서, v624만 `True`로 64후보·결과 검증을 추가; 얇은 v624 wrapper + 일회성 Windows cache-HIT workflow를 추가. v570/v344의 브라우저 결과/복원 관찰을 재사용하고 독립 SimC executor·효과 인증 Gate·통계 엔진을 추가하지 않음.
- v624 관련 코드 `f57de796`, 클릭 수정 `172c79b7`, 별도 wrapper `0c708d58`, 워크플로 `9a90d772`, 실제 one-shot 호출 `3c3b04e6`. 사전 [syntax-only #44454839888](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44454839888) PASS/real job SKIP. 실제 한 번만 승인 실행한 #44454908607에서 **환경 Native 6 + DPS Native 64**, 별도 26개 전문화 전수 Native **0**, SimC 재컴파일 **0**, 기존 캐시 무효화 **0**.
- 이번 64후보는 **이전 증거의 실제 미검증 단절인 동일 빌드 웹 마부 E2E 완료**를 해소하기 위한 **1회 비용**. v624 PASS 이후 같은 경계에 대해 Native 64회를 재반복할 필요 없음. 다른 전문화·양수 E·복수 부위에 대한 독립 실환경 Native 검증은 이 영수증이 자동으로 대체하지 않음.

## 5. 공식 수락과 다음 비용 대비 작업

- **이번 70961 가슴 E0 단일 시나리오의 일반 사용자 웹 입력→실 Native64→최종 결과 표시·저장·재열람: PASS**. 이는 전체 26개 전문화/모든 사용자 옵션/Windows 배포판 인수 완료가 아님.
- 다음 우선순위: **기존 검증된 E>0 및 복수 부위 E 회계·적용**에서 실제 일반 사용자 입력→내부 대표 프로필→SimC를 가로막는 **첫 구체 단절**만 찾아 `STOP→REUSE→CONNECT/FIX→필요 최소 EXTEND`로 연결. 추가 효과 메커니즘 연구·전 마부 효과 인증·새 solver/전 시즌 전체 DB·동일 Native64 무조건 반복 금지. 미승인 마부는 선택지만 보류하고 E0 기본 제품을 막지 않음.
- 공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` **변경 없음**. `main`/v003 immutable/원본 v016 실제 통합/Project Sources UI/Work OS M0·Shared State/기존 주 제품 개발 채팅 소유권 변경 없음.
