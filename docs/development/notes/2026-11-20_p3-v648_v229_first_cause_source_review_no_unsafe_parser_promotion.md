# P3 v648 — V229 최초 차단 원본 대조, 코드 지문 충돌 발견 및 안전 STOP (2026-11-20)

**범위:** 사용자 PC에서 표시된 `V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH`를 기존 v229/v216/v217 코드, 실제 SimC GitHub generated header, 과거 v639 Native 성공 증거에 대조했다. 일반 제품 시즌/Native 수집은 새로 수행하지 않았다. 사용자 PC의 원본 *복사된* 진단 영수증은 아직 확보되지 않았다.

## 1. 직접 확인된 증거와 미확정

- 격리 브랜치 조사 시작 HEAD `422f764fb145b07c53488d01a0b1b6ec494571eb`(v647 인계 문서).
- SimC commit `0d194013c7753feb7fe145741b82014de2fd5a26`: 공식 GitHub `engine/dbc/generated/item_set_bonus.inc` 첫 줄 `// Set bonus data, wow build 12.1.5.70783`, 둘째 줄 `std::array<item_set_bonus_t, 1183>`. 같은 revision의 `gem_data.inc`와 `temporary_enchant.inc`도 `12.1.5.70783` 헤더. 첫 두 줄은 현 `SET_HEAD`/`SET_COUNT` 정규식에 부합한다.
- 검증된 과거 SimC `9933ffb`와 소스 `6924096`의 set-bonus 헤더는 `12.1.5.70961`. v639 70961 Native64는 해당 범위의 역사 증거다.
- **조건부 원인:** 만약 사용자 실행의 실제 pinned revision이 `0d19401`이고 요청 게임 빌드가 `12.1.5.70961`이라면 v229에서는 **형식 실패가 아니라 검증된 헤더의 수치 불일치**가 발생한다. 그러나 사용자 .7z 다운로드 사실만으로 사용 중 바이너리·입력 revision·요청 빌드와 원본 diagnostic receipt를 확정할 수 없다.
- 현 `runner/v229_simc_only_source_seed.py::parse_set_bonus`는 `len(lines)>=3`, 첫 줄 헤더 형식, **헤더 빌드==요청 빌드**, 둘째 줄 배열 선언을 하나의 `V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH`로 처리한다. 코드만으로는 그 네 조건 중 무엇이 실제 PC에서 실패했는지 알 수 없다.
- `v216._collect_first_party_simc_seed_stage`는 해당 오류를 `fresh_pinned_first_party_simc_source.reason`으로 전달하며, v646 UI는 복합 코드의 불확실성을 그대로 표시한다. 새 시즌 READY를 임의 승격하지 않는다.

## 2. 교정 실험과 최종 원복 (제품 코드 순변경 0)

- 원인 구분을 위해 v229에서 정상 형식+틀린 빌드를 기존 `V229_GENERATED_SIMC_COMPILED_BUILD_MISMATCH`로 분리하고 테스트를 추가한 실험 커밋 `3dba66283989d1b2b9d2df20cacfd7321daf9a1a`, `39e075a2a9ce68a3f25a21b08f10b5482ccfbc3c`.
- v647 배포 ZIP **원본 소스 바이트에 동일 변경만 적용**하여 신규 Git blob SHA를 대조한 뒤, 오프라인 파서 4/4 PASS·기존 v646 JS 원인 분류 계약 PASS. 이는 사용자 PC/공식 Windows CI/Native PASS가 아님.
- **차단 가능한 회귀를 발견:** `v216`는 v229 코드의 dependency fingerprint를 `v217.execute_stage`의 sealed input identity로 기록한다. v229 실패로 남은 **RUNNING stage receipt** 또는 이미 COMPLETE 된 기존 stage에 코드 해시가 변경되면 `STAGE_INPUT_FINGERPRINT_MISMATCH`가 발생할 수 있다. 이 경우 정확한 오류 분리보다 앞서 복구가 막힌다. 기존 stage receipt를 수동 삭제/변조하거나 READY gate를 우회하지 않는다.
- 따라서 사용자 PC의 정확 원인 확인·기존 stage 복구 정책 정합 검증 없이 진단용 파서 변경을 배포하지 않기로 했다. 격리 브랜치의 **v229 구현과 해당 테스트 모두 원본 바이트로 원복**: `6fe6331c0e71acd144c247cd4a2373408dfcf3d0`, `fe10d9c3dbc687123c5c19837a86154e09380a3e`. v229 Git blob `fe31ee136989fe06fdd05582bf857c2b41b2dfd6`, 테스트 blob `fbb0b26d507958b0a504b23bd3a8a39018bef5bf` (인계 HEAD와 같음).
- 새로운 v648 ZIP/실제 Native/Blizzard·Wago DB2/API 조회 **없음**. 기존 v647 ZIP SHA `debb25affa7e0539f2197a267deb5286d566b57510cec1d3412e838b28edfdd2` 유효, v639 역사 Native64 재사용.

## 3. 다음 한 단계와 STOP

1. **먼저** 실제 개인 PC의 기존 `진단 영수증 복사` 자료(비밀정보 제외), 당시 요청 `game_build`, 활성 `simc.exe`의 `revision`/CLI `display_build=2`, 그리고 v229 `reason`을 대조한다. 아직 받은 적 없는 항목을 임의로 채우지 않는다.
2. 0d19401/70783 vs 70961이 **실제 활성 입력으로 확정**되면 파서가 아니라 *same-build Windows SimC/source 확보 문제*를 우선 해결한다. 최신 GitHub Nightly나 Git revision 날짜만으로 호환을 보장하지 않는다.
3. 실제 파서 문제만 확인되면 먼저 `v217` 단계 영수증 RUNNING/COMPLETE의 안전한 재사용·회복 계획을 증명한 뒤 최소 FIX+focused 테스트를 한다. 별도 source collector/optimizer/Native64는 만들지 않는다.
4. 최초 장애가 원인 확정 및 기존 경로에서 해결되면 중복 검증 없이 STOP.

**공식 판정 불변:** `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`; 주 개발 채팅/격리 branch, main·v003 immutable·Project UI·Work OS/Shared State 권한 제한 유지. 본 내용은 원인 분석·안전한 원복 기록이지 실제 개인 PC 시즌 READY 또는 전체 제품 완성 증거가 아니다.

### 원본 링크

- https://github.com/simulationcraft/simc/blob/0d19401/engine/dbc/generated/item_set_bonus.inc
- https://github.com/simulationcraft/simc/blob/9933ffb/engine/dbc/generated/item_set_bonus.inc
- https://github.com/degong2-code/simc-secondary-optimizer-runner/blob/probe/chat-cache-v035-20261024/runner/v229_simc_only_source_seed.py
