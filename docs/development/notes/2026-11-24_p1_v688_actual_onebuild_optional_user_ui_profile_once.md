# P1 v688 — 실제 70961 단일 원본 시즌 구축→옵션 포함 v212 설치→v113 사용자 프로필

2026-11-24. 격리 브랜치 `probe/chat-cache-v035-20261024`, 기준 SHA `9f13f1a6472e2bc6f7326aaf67f3c65b149b5e82`.

## 왜 기존 원본만으로는 충분하지 않은가

실 Windows v630 `V618_REAL_INSTALLED_V212.json`은 실제 70961 G/J/F/O 및 영구 마부 설치 증거이지만 `installed_optional_consumables` 필드가 없다(해당 기능 이전 생성). 실 Windows v684는 Wago→SimC 59개 연결, food35/potion1 v212 source-only 투영으로 성공했으나 일회성 원본 stage가 artifact에 남지 않았다. 서로 다른 실행의 설치 문서에 59개 행을 붙여 동일 빌드/원본 설치 SHA를 발명할 수 없다. 따라서 **실제 사용자 옵션이 추가된 설치+사용자 프로필을 확인하려면 동일 실행의 새 원본 Build 1회가 필요**하다. 이미 관측한 원본 소모품 수를 다시 세기 위해 실행하는 것이 아니다.

## 구현/실행

- 기존 Windows `.github/workflows/p1_v611_current_live_70961_enchant_build_once.yml`에서 **이미 성공한 exact pinned 70961/SimC source CLI cache 및 실제 v610 원본 시즌 빌드**를 재사용. 새 workflow나 source/Native 계산 엔진 없음. 딱 한 번 `[v688-real-optional-user-once]` 커밋 메시지에만 실제 job 실행.
- 기존 `p1_v610_real_installed_enchant_one_build.run(postinstall=...)`를 그대로 활용해 **같은 원본 v216/v217/v212 실행에서 만든 실제 설치 SHA**가 있을 때만 후속 `v113`을 호출. 이 경로는 새 Native/효과 인증 Gate가 아닌 원래 고객용 앱을 사용하는 통합 수락 실험이다. 완료 상태 `PASS_REAL_INSTALLED_OPTIONAL_USER_PROFILE_NO_NATIVE`는 DPS 완료로 오해하지 않도록 기존 native 성공 상태와 구분.
- 실제 v212 `installed_optional_consumables`에서 음식 1개를 읽고, 기존 v113 FastAPI TestClient의 **실제 GET `/api/v1/season-option-catalog`**에서 동일 설치 SHA/아이템 ID/SimC token을 확인. 같은 앱의 POST `/api/v1/sessions/plan`으로 일반 징벌 성기사 대표 장비/장신구 사용자 프로필을 만들고 `generated/profile.simc`에서 `food=token` 한 번, 미선택 물약·증강 disabled, 설치 B/T 동일함을 확인한다.
- HTTP는 CI 내 **loopback TestClient**만 사용, 외부 웹 요청은 기존 시즌 원본 Build의 필수 수집만. 최종 SimC DPS/SEM/95% 계산·user Native는 실행하지 않는다. 기존 G/J/F/E core 원본 Native가 필요한 경우 이를 0이라고 주장하지 않는다. 같은 빌드가 아니면 v610이 그대로 차단한다.
- 성공/첫 결손/실제 UI 목록 개수와 SHA만 작은 JSON으로 저장, 사용자 프로필 전체·소스 CSV·자격증명/SimC 바이너리는 업로드하지 않는다. 기존 실 인증 stage·캐시·메모리/디스크 사용 경로를 재사용한다.
- 사용자 개인 PC v677 시험은 계속 보류, 더 많은 전 전문화 Native 전수/새 독립 효과 인증·최적화기 금지.

## 수락 판정

성공은 **같은 실제 원본 Build가 설치한 v212 SHA에서 사용자 선택 메뉴→v113 계획→선택된 SimC 프로필까지** 일치했을 때만 표시. 실패 시 해당 단계의 첫 결손 코드 기록, 다른 시즌·옛 설치 SHA로 대체 금지. 검증이 SimC parser Native acceptance나 식품 품질 수치 비열등성, 일반 사용자 DPS full E2E를 입증하지 않으므로 이 셋은 계속 PENDING. `15/78 COMPLETE`(완료율 아님)/`full_product_e2e=PENDING`/ `next_review=B10` 및 main·v003·v016·Project UI·Work OS 권한 불변.

## v688 실제 Windows Actions 결과 — 실행 및 ZIP 원문 검증 완료

- 격리 HEAD `f3c5307b88732432a9d81778e4d30ce6204b54c8`에서 [기존 70961 v611/v610 Windows Actions #45223542078](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45223542078)는 **SUCCESS**. 이전 70783 v610 workflow는 조건이 달라 SKIPPED; 한 번의 70961 원본 Build만 실행. 기존 source SHA 확인+Windows SimC cache HIT, ZIP+기존 web requirements 사용, 시즌 전체 원본 주입 없음.
- 실 artifact #14842556797: 정확 [v216/v217/v212에서 생성한 동일 실행 설치 문서] `V618_REAL_INSTALLED_V212.json`, `manifest_sha256=f96ed468a74f877ef2ceecd0ae57846b01335aebc890cb86cb2e176b04481bf5`, `game_build=12.1.5.70961`, `simc_revision=9933ffb946fb55b1fa66657b848f519ac19006e1`, ilvl334, `G=2850`, `J=92`, `F=165`, `O=0`, `B=T=3107`. **실제 installed_optional_consumables** 음식 35 (`SOURCE_BACKED_OPTIONS_READY`), 물약 1 (`SOURCE_BACKED_OPTIONS_READY`), 증강 0 (`SOURCE_NOT_YET_RESOLVED`). 실제 기존 영구 마부 38개도 등록. 본 설치는 이전 v630 설치 파일과 다른 content-addressed SHA이며 사후 합성·값 복사는 없음.
- 실 artifact #14841678917의 `V688_REAL_OPTIONAL_USER_STAGE.json`: `PASS_ORIGINAL_V113_OPTIONAL_PROFILE_ZERO_NATIVE`. 같은 설치 SHA를 검증한 실제 `/api/v1/season-option-catalog` HTTP200 및 `/api/v1/sessions/plan` HTTP200, 선택 음식 `Blooming Feast` ItemID 242273 / `blooming_feast`(source quality rank 0) 사용자 징벌 성기사 프로필 `food=blooming_feast` 정확 1회, 미사용 물약·증강 `disabled`, 동일 B/T 3107, 사용자 프로필 SHA `1ffacb73a0010f6399016ed942337ad3005ce0ce88df894b0287dc2fbb772186`, `READY_ZERO_NATIVE`.
- 실행 비용은 **기존 시즌 원본 G/J/F/E 확인용 Native 15회**, 추가 사용자 최적화 Native/DPS 0회. 기존 소스·SimC 캐시 재사용. 음식·물약 효과 메커니즘 인증/SimC 파서 Native 실제 수락·이 아이템의 모든 효과 수치 비열등성/전체 품질 판정·최종 사용자 DPS/SEM/95%는 **미실증**. 이를 `full_product_e2e=PASS`로 승격하지 않는다.
- STOP: 동일 70961 원본 수집/소모품 후보 목록 반복 탐색·합성 회계 증명·불필요한 전 전문화 Native 금지. 다음 수락은 기존 **실 설치 SHA로 생성된 프로필 1개**에 대한 SimC 원본 Native 확인과 기존 적응형 DPS·캐시/재열람 가능 여부를 변화 부분만 최소 측정, 이전 v639/v624 일반 Native 성공은 재사용하되 소모품 신규 사용 성공 증거로 과장하지 않음. 26전문화 DPS 전수 및 개인 PC v677 수동 시험 계속 보류.
