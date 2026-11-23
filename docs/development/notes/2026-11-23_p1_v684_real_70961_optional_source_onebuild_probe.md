# P1 v684 — 실제 70961 원본 1회 소모품 선택지 연결 시험

2026-11-23 KST. 격리 브랜치 `probe/chat-cache-v035-20261024`. 기준 HEAD `a85627afe9636e205faa3c25ba315d86adb20d98`.

## 목적과 원인

v681 파서 문자열 정규화, v682 SimC 부분문자열 충돌, v683 Wago ID 일부 부재 시 선택형 SimC DBC 부분 조회를 교정했지만 지금까지 선택지 수는 합성 자료로만 확인되었다. 기존 v630 70961 v212 설치 artifact는 v680 이전에 생산됐고 보존된 Wago/SimC 원본 stage가 없으므로 소모품 실등록 증거로 쓸 수 없다.

이번 조치는 신규 엔진이 아니라 **이미 개발된 v216 보통 시즌 원본 Build**의 70961/SimC pinned `9933ffb946fb55b1fa66657b848f519ac19006e1`에서 사용 가능한 첫 소모품 stage 확인이다. 실수집 비용이 필요한 이유는 GitHub의 작은 기존 영수증에 source CSV가 보존되지 않아서다.

## 실행 경로와 제약

- `integration_probes/p1_v684_real_optional_source_onebuild_once.py`: v216 `build_environment(fresh_collection_inputs=...)` 한 번만 호출. `v280` 기존 아이템-사용주문 스테이지, `v189/v190` 후보, `v230` DBC, `v680` source-owned bridge, `v212` 원래 source projection 함수를 재사용한다.
- `binary=None`, G/F/O Native 요청 false, DPS Native 0, 사용자 세션 생성 없음, source artifact 주입 없음, 시즌 숫자 복제 없음, 새 인증 Gate 없음.
- `v212` 전체 설치는 G/J/F/O 원본 증거가 없으므로 실행하지 않는다. 시험 중 v212 메뉴는 **원본에서 만든 projection**이며 설치·사용자 입력 SimC Native 성공이 아니다.
- 중복 데이터 다운로드/효과 인증을 만들지 않고 기존 한 번의 시즌 Build가 필요한 Wago 및 pinned SimC 원본만 수집한다. 병렬·전수·자동 재실행 없음.
- GitHub push 일회성 `[v684-source-once]` 조건, 정확한 스크립트·워크플로 경로 제한; 70961은 검증된 같은 시즌 사례이고 그날 최신 KR Retail을 임의로 단정하지 않는다.
- 출력은 stage status, 아이템/메뉴 수, 기존 SHA, 최대 12개 공개 소모품 후보 ID/토큰만. Wago CSV/비밀키/프로필/SimC 실행 결과는 업로드하지 않는다.

## 성공·실패와 STOP

최소 성공: 실제 v216 70961 소스 joined rows 및 v212의 소스 projection 확인. No joined rows면 `PENDING_NO_WAGO_SIMC_JOINED_ROWS`로 실제 첫 결손을 기록; 상류 누락 또는 인증 오류면 `BLOCKED_`/`PENDING_` 코드로 기록. 시험 끝나면 관련 그 한 구간만 판단하고 재수집·Native 반복하지 않는다.

미해결: 실 v212 설치 및 정확 설치 SHA→v113 사용자 메뉴→v218/v098 Native 프로필 관통, SimC parser 전체 유일성, 최고 품질 수치 비열등성, 개인 PC v677 시험. 기존 캐시/완료 원장/주 제품 개발 채팅 권한 불변; `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`.
