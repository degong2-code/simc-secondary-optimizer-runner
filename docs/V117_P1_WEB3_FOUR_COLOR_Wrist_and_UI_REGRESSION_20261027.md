# SIMC SECONDARY OPTIMIZER — P1-WEB-3 / v117 focused regression correction

2026-10-27 · 격리 브랜치 전용 · 사용자 실제 Windows 오프라인 시험 결과 반영. **이번 교정 코드의 Python PASS는 아직 확인 전**.

## 직접 관측된 신규 FAIL

회사 PC가 최신 브랜치 전체 ZIP에서 다음을 실행했다.

```powershell
py -3 -m unittest -q tests.test_v101_common_representative_equipment tests.test_v114_local_web_ui_offline
```

실제 결과는 **Ran 18 tests / FAILED (failures=1, errors=2)**.

- 잠행 도적과 정기 주술사 `test_powerful_diamond_representative_gems_cover_all_four_colors`: `REPRESENTATIVE_SIX_ORDINARY_GEMS_REQUIRED`. 실제 v104 소스 고정식 대표 장비가 손목을 일반 아이템으로 교체할 때 구 소스 `gem_id`를 제거해서 **6→5개**가 되었다.
- `test_missing_session_is_not_saved_as_verified_and_polling_backs_off`: 테스트가 구 문구 `기존 세션 조회 성공`을 요구하지만 v116 UI 구현에서는 `기존 세션·입력 복원 성공`으로 변경되어 실패. UI 제품 행동 오류가 아니라 테스트 기대 문자열의 구버전 잔존.

## 해당 원인에 대한 최소 교정

`runner/v101_common_representative_equipment.py`:

- 기존 `ensure_representative_gem_colors(rows,diamond_id,need)`는 **diamond_id=240967에서만** 동작하는 정책 유지.
- 원본 소스가 손목 소켓 1개를 이미 확인한 두 대표 장비에만 source-pinned replacement mapping 추가:
  - 잠행 도적: 원본 `271506` 손목에 `240900` 1개, 대표 일반 손목 `268240`.
  - 정기 주술사: 원본 `244584` 손목에 `240906` 1개, 대표 일반 손목 `273775`.
- `240967` 선택 후 일반 보석이 정확히 5개이고 **다섯 개가 해당 소스 고정 보석 ID로 전부 일치**하며 새 손목에는 `gem_id`가 없는 경우에만 그 한 소켓에 대표 소스 보석 ID 하나를 구성하여 총 6개를 맞춘 뒤 기존 4색 최소 치환 수행.
- 그 외 임의 5개/부적합 아이템/불명 소켓 구성은 `REPRESENTATIVE_SIX_ORDINARY_GEMS_REQUIRED` 차단 그대로 유지.
- 소스 대표 프로필 원본 바이트, 기존 `240983`·선택 안 한 다이아몬드 경로, 기존 캐시·Native6/6 징벌 결과, B/O/T/95% 알고리즘 변경 없음.
- **주의:** 2개 대표 일반 손목 아이템의 실제 SimC gem socket 수용은 새 `240967` Native 실기 전까지 독립 입증된 것이 아니다. 개발 소스에서 원래 손목의 보석 존재만 확인됐음.

`tests/test_v101_common_representative_equipment.py`: 두 경로의 원본 5개·`240983` 무변경·`240967` 6개 복원·알 수 없는 5개 배치 fail-closed 시험 추가.

`tests/test_v114_local_web_ui_offline.py`: 성공 메시지 기대값을 실제 `기존 세션·입력 복원 성공`으로 업데이트.

## 검증 상태와 다음 단계

- 관측됨: 사용자 기존 시험 18개 중 15개 통과, 2 ERROR 및 1 FAIL — **미화하거나 PASS로 바꾸지 않는다.**
- 신규 코드 구현 완료: 위 3곳 교정. 신규 테스트 추가로 예상 테스트 수는 **20개**(이전 18+2). **이 변경에 대한 Windows Python 회귀 PASS, GitHub Actions PASS, 240967 실제 SimC Native 검증은 아직 미실행/미확인.**
- 사용자는 격리 브랜치 **최신 전체 ZIP**을 새 폴더에 받고 동일 두 테스트 명령만 먼저 반복한다. 이것이 PASS면 기존 징벌 세션 `abca493c00d6ee2599f1`의 조회만 확인(추가 Native 불필요). 실제 240967 경로의 최소 선택/Socket Native 검증은 별도 정밀한 확인 절차로 이어간다.
- main 병합·v003 immutable·Project Sources/UI·공식 Work OS/Shared State 변경 없음.
