# 2026-11-22 P3 v664 — 개인 PC의 v229 short revision 대용량 조회 첫 차단 / 안전한 40자리 입력 수정

## 실제 개인 PC 사용자 진단 (개인 PC 영수증, 이 커밋의 Native 결과 아님)
- 사용자가 수정 v663 Windows ZIP으로 공개 자체 빌드 SimC `6924096` / 한국 Live `12.1.5.70961` 설치 후 CLI 확인·연결 저장까지 완료한 사진을 제공. 기존 키 저장 UI는 `Blizzard·WCL API 인증정보 저장됨`을 표시하며 실제 API 접근·현행 시즌 인증 완료와는 별개임.
- 사용자가 시즌 구축 후 직접 제공한 `v384_user_copied_season_build_diagnostic_v1`: `outcome=FRESH_WAGO_DB2_COLLECTED_MORE_SOURCES_PENDING`, `season_discovery_status=AUTHENTICATED_SOURCE_DISCOVERED_SEASON_JOIN_PENDING`, `season_join_status=DB2_WCL_CANDIDATES_JOINED_SEASON_CONDITIONS_PENDING`.
- 최초 분명한 중단은 `simc_revision_resolution_status=SIMC_SOURCE_COMMIT_RESOLUTION_PENDING` + `simc_revision_resolution_reason=V229_REVISION_LOOKUP_RESPONSE_TOO_LARGE` (기존 v229 GitHub `/commits/<7-digit>` 본문 120KB 한도 초과). `simc_source_status=SIMC_PINNED_REVISION_NOT_AVAILABLE_PENDING`, 8개 compiler inputs 후속 PENDING, G/J/F/O owner 모두 false, `environment_ready=false`, 신규 Native 0. 이것은 `V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH`가 **이번 PC 재현의 원인**이라는 증거가 아니며, 실제 첫 원인이 변경된 것을 구별한다.
- 사용자에게 별도 API 재발급·SimC 재설치 없이 이미 소스·해더를 확인한 공개 자체 빌드의 full source commit `6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7`를 **SimC Git revision** 칸에 직접 입력하고 ‘SimC 연결 확인·저장’ 후 동일 시즌 환경 준비를 재시도하도록 안내. CLI 출력의 짧은 Git token만으로 서명/프로필 인증을 주장하지 않는다.

## 기존 코드·재사용된 검증된 사실
- `runner/v229_simc_only_source_seed.py::resolve_exact_commit`은 short 7~12자일 때만 GitHub commits API 응답을 120001바이트까지 받고 120000 초과를 명시적으로 차단; full 40자리면 해당 네트워크 lookup 없이 정확한 SHA를 그대로 반환. 이후 기존 `discover_generated_tree`/generated blob header/build SHA 검증은 계속 수행됨.
- v660/v663 관리 자체 빌드의 `installed.source_revision_full`에는 원본 40자리 Git commit이 기록되고, 이는 기존 public source 3 header proof + self-built ZIP receipt와 함께 Windows 실측됐음. **이 자료의 source origin은 SimulationCraft 공식 실행파일 서명이 아닌 EXPRIMENTAL 자체 빌드 provenance**로 유지.
- v216 stage `fresh-v257-exact-simc-commit-<revision_hint>`는 short/full이 서로 다른 고정 stage_id이므로 새 full 입력은 이전 short 실패 receipt를 수정하지 않고 새 시도로 진행한다. 다음 v229 generated collector/기존 v217 SHA 검증은 동일. v648에서 v229 모듈을 수정해 `STAGE_INPUT_FINGERPRINT_MISMATCH`가 발생할 위험을 발견하고 원복한 이력은 보존; 이번에도 v229/v216/v217 원본 바이트는 변경하지 않음.

## 최소 변경 — 새 제품 UI에만 적용
- `runner/webui/app.js`에 `managedFullSimcSourceRevision(data)`를 추가: 관리 자체 빌드의 full 40자리 SHA·7~12자리 short·정확한 prefix가 모두 검증된 경우에만 전체 Git source SHA를 화면에 사용, 없으면 기존 짧은 revision 유지. 공식 Nightly·임의 사용자 실행파일의 revision 자동 추정 금지.
- 신규 자동 설치 `applyManagedSimc`는 full source SHA가 있으면 그대로 `revision` 입력칸에 사용. 기존 저장된 `6924096` 복원 경로에서도 `refreshSimcUpdater`가 조회한 관리 실행파일 경로가 현재 입력값과 정확히 동일하고 revision이 저장된 short와 같을 때만 full 40자리로 입력칸을 갱신한다. 다른 수동 실행파일/수정한 revision은 변경하지 않고 저장도 자동 수행하지 않음. ‘SimC 연결 확인·저장’ 명시 사용자 동작은 보존.
- API 인증/저장, 시즌 G/J/F/O·L/E/O, v229 parser·조회 한도, v216/v217 sealed stage, v653 UI 디자인, 세션/Native/DPS 캐시/취소·재개는 변경 0. 이 수정은 **첫 차단 회피용 source identity 입력**이지 시즌 READY/최적화 PASS가 아님.

## 검증 경계·비용
- 새 [Windows full beta ZIP·localhost·focused #45025031742](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45025031742): Python 3.12·3.14 **각 326 tests PASS/0 FAIL**(이전 325에서 UI 계약 1 추가), packager 5/5 PASS, 285파일 source ZIP, 실제 Windows local CMD + HTTP 3 plans PASS. **새 DPS Native 0, C++ 컴파일 0, 시즌 원본 신규 수집 0**.
- 앞선 첫 테스트 [#45024781660](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45024781660)는 신규 Node harness가 잘못 삽입돼 테스트 코드의 JS 구문 오류로만 FAIL; 제품 app.js 코드는 Node `--check` 포함 기존 시험에서 통과. 해당 손상 테스트 파일은 직전 정상본에서 복원하고 안전한 focused UI source contract 검증으로 교체한 뒤 Windows 3.12·3.14 모두 최종 PASS. 이전 실패를 제품 오류로 기록하지 않음.
- `v229` 실시간 GitHub short-commit 응답 전체를 다시 전송받거나 크기 한도를 늘리지 않아 새로운 비용/비인가 네트워크 경로 추가 없음. 관리 source full SHA가 있는 환경에서는 GitHub short lookup API 왕복 1회가 사라짐. 새로운 사용자 개발자 입력/키 필요 없음.
- v639 Native64/SEM/95%/재열람, v660-v663 Windows auto install/py7zr와 공개 70961 source proof는 **과거 영수증 재사용**. 이번 v664가 사용자 PC에서 실제 G/J/F/O READY 또는 SimC 최적 DPS 결과를 만들어냈다는 주장은 불가.

## 다음 첫 제품 검증 및 STOP
- 현재 사용 중인 **기존 v663 ZIP에서도** 사용자 본인의 SimC Git revision 필드를 위 40자리로 바꿔 저장·시즌 준비를 다시 클릭할 수 있다. v664 UI 자동 수정을 받기 위해 사용자가 또 다른 ZIP을 반드시 재설치할 필요 없음. 기존 RUNNING receipt 임의 삭제·변조하지 않음.
- 사용자에게 새로운 `진단 영수증 복사`를 받아 SHORT_LOOKUP 차단이 사라졌는지 확인하고, 다음 실제 남은 첫 PENDING(시즌/레이드 조인, tier/G/J/F/O 등)을 정확히 하나씩 처리. 기존 파일·캐시·Native 영수증 유지. full_product_e2e=PENDING. main/v003/Project UI/Work OS·78 공식 승격 및 주 제품 채팅 소유권 불변.
