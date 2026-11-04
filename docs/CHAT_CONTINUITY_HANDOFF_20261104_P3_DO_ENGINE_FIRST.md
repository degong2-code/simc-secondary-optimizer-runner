# SIMC SECONDARY OPTIMIZER — P3-DO 단일 엔진 인계 정본 (2026-11-04)

**상태:** 사용자 제공 P3-DO 휴대 인계를 GitHub 개발 문서용으로 구조화한 포인터. P3-DF는 역사 인계. 이 문서는 승인 v1.4.3 원문, Project UI, main, Work OS, immutable v003, 원본 v016을 변경하지 않는다.

## 1. 복원 권위·독립 조회

- 저장소: `degong2-code/simc-secondary-optimizer-runner`, 격리 `probe/chat-cache-v035-20261024`.
- P3-DO 인계 직전 격리 HEAD: `90bbd7d9c9b8915a4ef103ae2e6bbd7aad8d51e9`; main: `07133e0aaf738d6e4816a6486057b1cd49c018de`. **읽을 때마다 각 HEAD를 새로 조회한다.**
- 최종 P3-DN 제품 코드 `3a1252f1d07403ebcf1e3aff3581522b1b0d8864`; 이후 격리 HEAD까지 문서 3개만 변경된 이력.
- 최신 사용자 직접 결정 > 승인 v1.4.3·비충돌 v1.4 계열 > 실제 코드/원본·Actions/Native > 과거 인계/인덱스. v1.4.1의 27 DPS/증강 포함 서술은 역사 기록이다. **최신 범위는 26 DPS, 증강·탱커·힐러 제외.**

## 2. 단일 제품 엔진

장비 조합·파밍 경로 추천이나 현재 장비 재분배가 아닌 **미래 목표 ilvl(기본 334)/사용자 수동 최종 T의 최적 절대 CHMV rating**을 기존 SimC DPS로 탐색한다. 관측 1순위, DPS/SEM, **95%** 우위/미확정, 유의미하게 다른 근접 대안과 비율, 캐시·취소·재개를 제공하되 전역 최적 증명으로 과장하지 않는다.

유일한 정상 엔진 흐름: `v216 Environment Build` (대표 장비·무기·티어4 및 시즌별 G/J/F/O 원본 전체 구축) → `v222` 회계 → `v220/v196/v212` 검증된 최고 품질 정책 A 자동 선택지/시즌 승인 → `v098` 사용자 대표 SimC 프로필 → 기존 `v096→v094` 적응형 DPS/SEM/95%·캐시·취소·재개.

공식 `B=G+J+F`, `T=B+O`, `c_final=c_base+o`; 사용자 수동 최종 T 우선(`B=T-O`). 정확 L은 G 내부 하한, 영구 마부 E는 승인 회계에 한 번, 손별 기름 O는 비자유분배이고 `gear_*`에 한 번. 장신구 고정치는 자유 G 외부, 정적 레코드 미출력을 0으로 확정하지 않는다. 제작장비 50:50 배분을 L로 고정하지 않는다. **새 시즌에 구 시즌 79×2/J138/F165/O16+16을 복사하지 않는다.**

SimC가 proc/아이템/APL/DPS를 처리한다. 새 최적화 엔진·효과 인증 Gate·시즌 전체 장비 DB·무조건 26×ilvl Native 반복은 범위 밖. 일반 임시 마부는 제외, 기름은 별도 지원. 음식·물약·증강은 선택적, Omnium 등 특수 콘텐츠는 OFF시 프로필·예산/캐시에서 제거하는 선택 모듈.

## 3. 완료 범위(Evidence)와 실제 연결(Integration)

- `v216/v217/v241/v191/v211/v213`: 기존 원본 컴파일·SHA/재개. [P3-DN](development/notes/2026-11-04_p3-dn-v217-staged-source-relation-policy-a.md)은 기존 봉인 영수증에서 정확 ID/token/mask `source_relation` **하나만** 정책 A 입력에 연결. 외부 게임 사실·동등 품질·실제 손·소켓·SimC 수락·CHMV/E 회계 인증이 아니다.
- `v277 G`, `v271 J/가변 소켓`, `v278/v281 F/O`, `v285/v286 무기 마스크`, `v222 B/T`의 미승격 수치/조인 경로는 이미 존재한다. P3-DG~DK에서 원본 gear/tier SHA, `v216→v098` source-only 프로필, 기존 `v271→v139(socket_plan)→v098` 연결. P3-DF 작성 당시 raw gear/tier SHA 미연결 서술은 **P3-DG에서 교정**.
- [P3-DM](development/notes/2026-11-04_p3-dm-policy-a-receipts-normal-build-connect.md): `v220.decide`·`v196` 내부 eligible(**UNPUBLISHED**)·`v216`의 항목별 보류 이유. 신규 옵션 **실제 발행 0**, 새 시즌 **READY false**.
- 기존 인정된 동일 시즌에만 [P3-DD](development/notes/2026-11-04_p3-dd-admitted-season-v096-native-entry.md)의 `v098→v096→v094` 실행 진입점(오프라인)이 재사용 가능. 신규 시즌 `v212` 승인/26 DPS Native E2E는 불완전.
- 이전 실 Native [F/O A](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666305288), [F/O B](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666925906), [소켓](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696), [실 무기 소스](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41732744145)는 정확한 기존 시즌/빌드/아이템·variant 적용 범위 안에서만 재사용.

## 4. P3-DN 검증과 남은 3 family

- 최종 코드 `3a1252f1...`의 [v212 Ubuntu/Windows](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41790639319): OS별 **444 tests (440 PASS, 4 SKIP), 0 FAIL**, 로그 `V212_ENVIRONMENT_MANIFEST_NATIVE0_PASS`. [focused](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41790639275): 226 PASS/0 FAIL·DEV_LEDGER_PASS. [API](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41790639406), [Windows](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41790639465), [UI](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41790639331) 오프라인 SUCCESS. 신규 게임 HTTP/Native 0. 초기 실패는 P3-DN 노트에 보존.
- `simc_input`: 실제 Native 입력 수락·정확 token proof가 있는지 기존 v108/v189/v211/v213/v278/v281/v098 확인. token 존재는 수락 증거 아님.
- `product_input`: v167/v169/v271/v285/v286의 item ID·exact slot/hand/socket·사용 조건과 실제 사용자 선택 경로를 맞춘다. source mask만으로 적용 가능 단정 금지.
- `chmv_budget`: v222/기존 Native JSON2에서 정적 L/E/O/변형·중복 방지 소유권 확인. 미관측을 0으로 간주 금지.
- 정확 same-build/item에 네 가족 + 최고 품질 조건이 모두 충족되어야 정책 A eligible→`v196/v212` **원자적 실제 발행**. 선택적 후보 결손은 필수 G/J/F/O READY 판정과 분리. 구시즌 7967 경로는 보존.

## 5. 다음 최소 작업 / 효율 / 권한

작업 전 [PROTOCOL](development/PROTOCOL.md) → [INDEX](development/INDEX.md) (`SOURCE.SEAL`, `CATALOG.AUTOADMIT`, `BUDGET.GJFO`, `PRODUCT.E2E`) → P3-DN/DM 및 관련 노트 → [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) → [실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md) → [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) → 실제 코드·원본·영수증 순서로 읽는다. Evidence와 Integration을 분리하여 **REUSE/CONNECT/EXTEND/NEW/STOP**으로 판정; 새 게임 사실 조사/Native는 기존 증거 범위를 먼저 확인하고 사용자와 논의.

순서: 기존 3종 proof 최소 연결 → 실제 정책 A 발행/신규 시즌 READY → 기존 v098/v096/v094 제품 E2E 1개 → 재사용 가능한 26 DPS → 동일 v216의 과거 시즌 자료 없는 신규 설치 Build 통제실험(정상 신규 수집 허용, 결과 선봉인). 동일 기준 PASS/캐시를 재사용하며 중복 Native/HTTP/Actions, 메모리/I/O, 실행시간을 줄인다.

기존 주 제품 개발 채팅 소유권 유지. `main`, immutable v003, 원본 v016, Project UI/Sources/Instructions, Work OS M0·Shared State는 별도 권한. **새 채팅 첫 응답은 독립 HEAD·증거 복원 보고만 하고 사용자의 '진행' 전 개발·코드/문서 수정·CI/Native/HTTP·승격을 하지 않는다.** 본 파일 자체는 공식 Source/UI 적용·시즌 READY가 아니다.
