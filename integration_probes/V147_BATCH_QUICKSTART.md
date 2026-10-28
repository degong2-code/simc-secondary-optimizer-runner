# P1 — 24개 DPS 전문화 일괄 SimC 실측·적응형 실행

이 파일은 개발용 **격리 브랜치**의 로컬 실행 안내입니다. 실제 SimC 실행·전문화 지원 승격을 완료했다는 보고가 아닙니다. 기존 조화·황폐 2개 Windows Native 증거는 재검증하지 않고 재사용하며, 아래 일괄 처리 대상은 나머지 **24개**입니다.

## 실행 전 준비

- Windows PC에 Python 3과 실행 가능한 **실제 SimulationCraft** (`simc.exe`)가 있어야 합니다. GitHub Actions에서 성공한 모의/오프라인 테스트만으로 실제 SimC 실행을 대체할 수 없습니다.
- 사용하는 SimC 바이너리의 **정확한 Git revision(7~40자리 16진수)**을 확인합니다. 아래 `ACTUAL_SIMC_REVISION`은 자리표시자이며 그대로 실행하면 안 됩니다. 실행 결과의 JSON2 `git_revision`과의 동등성 검사에서 불일치가 나면 실패로 분류됩니다.
- 기본 입력은 `v146_character_starter_examples.json`에서 추출된 종족·특성·장신구 예시입니다. 현재 착용 장비·스탯은 기준으로 복사하지 않습니다. 물리 실측은 목표 ilvl334, 기름 0, 수동 T 없음으로 한정하며, 향후 개별 사용자 선택 옵션의 Native 검증을 대신하지 않습니다.

## 1. 전체 준비만: 실제 Native 0회

저장소 **루트**에서 실행합니다.

```powershell
python integration_probes/v147_all_dps_targeted_native_batch.py --simc "C:\path\to\simc.exe" --revision ACTUAL_SIMC_REVISION
```

24개 전문화의 물리 프로필 준비·0 Native 계획을 만듭니다. 그 외 `--execute`가 없으면 `--max-new-physical`, `--optimize-accepted` 플래그를 허용하지 않습니다.

## 2. 전체 일괄 Native (사용자가 명시적으로 실행)

Windows에서는 두 인수로 제공하는 CMD 실행기가 가장 간단합니다.

```bat
integration_probes\RUN_ALL_24_SIMC_NATIVE.cmd "C:\path\to\simc.exe" ACTUAL_SIMC_REVISION
```

같은 기능을 Python으로 직접 실행하려면:

```powershell
python integration_probes/v147_all_dps_targeted_native_batch.py --simc "C:\path\to\simc.exe" --revision ACTUAL_SIMC_REVISION --execute --max-new-physical 24 --optimize-accepted
```

- **새 물리 시험**은 전문화당 최대 1회, 총 최대 24회. 이미 성공했고 정확히 같은 바이너리·revision·프로필·JSON2가 있는 경우에는 0회 재사용합니다.
- **적응형 최적화**는 물리 시험 PASS 전문화에 대해서만 기존 `v098 → v096 → v094`로 진행합니다. 기존 Native 후보 최대 6회/전문화, 24개 전체의 **새 호출 이론적 상한은 24 + 144 = 168회**입니다. 실제 호출 수는 성공한 물리 프로필과 기존 캐시 등에 의해 감소할 수 있습니다.
- 실제 Native 실행은 **동시 실행 1개**입니다. 각 전문화는 독립 폴더·영수증·원본 SimC 로그·캐시를 가지며 실패해도 다른 전문화는 계속합니다. 적응형 상태는 기존 취소·재개 메커니즘을 사용합니다.
- 프로필을 생성할 수 있다는 사실만으로 **Native 지원 완료나 최적 CHMV 글로벌 입증**을 주장하지 않습니다. 결과는 관측 DPS, SEM 및 **95% 판단**만 전달합니다.

## 재개 및 취소

동일 명령, 동일 바이너리·revision, 동일 기본값으로 **재실행하면 캐시를 재검증하면서 계속합니다.** 기존 실패한 물리 시험의 오류·영수증은 덮어쓰지 않습니다. 각 전문화의 기존 적응형 결과·검증된 캐시는 원래 `v094` 기능으로 재사용됩니다.

실행 폴더의 최상위 `CANCEL` 빈 파일은 **다음 전문화 시작 전** 전체 배치를 중지합니다. 적응형 시험 도중 중단은 해당 전문화의 기존 `CANCEL` 경로를 사용합니다. 종료 후 재개하려면 `CANCEL`을 제거하고 **동일 명령**을 실행합니다. 프로그램이 종료될 때까지 Windows SimC 프로세스를 강제로 중복 실행하지 마세요. 중단 직전에 영수증이 확정되지 않은 물리 결과는 새 호출 없이 자동으로 성공 처리하지 않습니다.

새 물리 호출 수를 2회로 제한해 부분 배치만 진행하려면 `--execute --max-new-physical 2`를 지정합니다. 이미 물리 PASS를 받은 전문화만 최적화하려면 `--execute --max-new-physical 0 --optimize-accepted`를 사용합니다. 특정 전문화만 지정할 때는 `--spec mage/frost --spec warrior/fury`처럼 반복합니다.

## 파일·보고

- `~/SIMC_Secondary_Optimizer/v147_batch/simc_<binary SHA prefix>_<revision>/SUMMARY.json` : 최신 전체 현황, 전문화별 PASS·실패·대기·캐시 상태, DPS 결과
- 같은 하위 `physical/<spec>__<user SHA>/` : 실제 물리 입력, 원본 SimC 로그, 실패/성공 영수증, JSON2
- 같은 하위 `adaptive/<spec>__<user SHA>/` : 기존 `v098/v094` 최적화 세션과 Native 후보 캐시·취소·재개 기록

Windows에서는 실행 종료 시 해당 결과 폴더가 **한 번만** 열립니다. 실패 상세는 `SUMMARY.json`의 `simc_raw_log` 또는 `error`에 연결되며, 실제 SimC 에러의 원문은 절대 임의 재해석·효과 인증하지 않습니다.

**검증 범위:** GitHub Actions의 모의 Native 24/24와 Ubuntu/Windows 오프라인 회귀는 배치 제어·정확한 검증 연결만 증명합니다. 새 24개에 대한 실제 Windows Native 성공 영수증은 아직 없습니다. 사용자 장비 추천/아이템 DB 확장도 이 범위에 포함되지 않습니다.
