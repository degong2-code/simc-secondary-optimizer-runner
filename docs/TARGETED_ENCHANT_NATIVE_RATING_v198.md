# v197–v198: 정확한 마법부여 rating과 현재 G 예산 연결

**권위:** 2026-10-30 사용자 승인 방향. 실제 프로필·Native 결과·현재 시즌 DB가 정한 값만 사용. SimC의 발동 효과는 재구현하지 않음.

## 현재 확보한 결과와 한계

- SimC 고정 revision `710c2408bfd3ae4df71b8cd55cdf01f63fd6c926`/게임 빌드 `12.1.5.70575`, 마부 38개 소스 최고 품질 rank2. 기존 `v191` 38건 정합 영수증 재사용.
- `runner/v197_enchant_effect_families.py`: **반지 9종** 중 치명/가속/특화/유연의 일반형 4종과 상위형 4종을 같은 효과군으로 표시. `Eyes of the Eagle`은 치명타 **rating**이 아니라 치명타 **효과**이므로 5번째 독립 목적. 상위/일반형 판정의 근거는 Wowhead·WoW-professions 명시 효과 설명이며 **게임 DB 정확한 정적 rating 수치 인증이 아님**. 디스플레이에서 둘을 구별하되 아직 38개 모두 입력 선택 불가.
- `runner/v197_verified_effect_budget.py`: 정확한 companion Native JSON2 두 개와 영수증에 근거한 고정 마부의 정적 rating `E`만 **현재 G 내부에서 보호**하는 오프라인 계산 계약. `T=G+J+F+O` 유지, `G = T-J-F-O`, `G_free=G-L-E`. 스탯별 하한 `c_final >= J+F+O+L+E`. E를 T에 추가하지 않고 O도 다시 더하지 않음. `T`에 모순되거나 floor 미달인 후보는 차단.
- `integration_probes/v198_targeted_enchant_native_rating.py`: 기존 v098/v106 **stage/profile.simc**를 받아 기존 `v140`의 물리 표본 생성기를 재사용. `gear_*` 자유수치 4개만 제거한 상태로 같은 장비의 **마부 미부착 vs 선택 마부 부착** 입력 두 개를 작성. `simc.exe` Native JSON2 최대 2회(35 iterations), `players[0].gear[slot]`의 치명/가속/특화/유연 차이와 비대상 장비 정합·정확한 enchant id·SimC revision·파일 SHA를 출력. 원본 사용자 profile/기존 DPS 캐시/최적화 state는 절대 수정하지 않는다. 같은 SHA·조건의 재실행은 Native JSON2 재사용 가능.
- 이 감사는 **정적 rating 확인**이지 proc/효과 구현 자체를 독립 Gate로 인증하는 절차가 아니다. Proc는 SimC가 계산. `v198` receipt를 동반하는 실제 Native 정보가 확보되기 전 `v197`의 임의 정수(예: 웹 tooltip에 나온 29)를 승인된 E로 저장하거나 UI 선택을 활성화하지 않는다.

## 요청형 실행 경로 (개발 확인 용도)

기존 stage/profile.simc와 실제 Windows SimC 710c240 바이너리가 있는 환경에서만 실행 가능한 옵션:

```powershell
python integration_probes/v198_targeted_enchant_native_rating.py --profile "<기존 세션의 stage/profile.simc>" --binary "<실제 simc.exe 경로>" --revision 710c240 --slot finger1 --enchant-id 8025 --iterations 35 --max-new 2 --out "<사용자 선택 증거 폴더>"
```

이 커맨드는 일반 베타 실행에 **필수 입력이 아니다**. 신규 Linux/Windows GitHub Actions 실행은 동일 시점 GitHub hosted runner job 자체가 step 0개로 실패하는 상태라 본 명령에 대한 **실제 신규 Native 증거는 아직 없다**. 이전 사용자 SimC 710c240 6/6 최적화 성공과 v192 기존 물리 1/1 영수증은 역사 증거이며 신규 마부의 E 값 증거로 재해석하지 않는다.

## 다음 최소 연결

1. `v198`의 동일 장비·다른 enchant 입력 2개가 진짜 Native JSON2로 확보되면 source/CLI SHA를 대조, stat E와 비정적 장식/proc-only 항목 분리. **모든 마부별 전수 Native는 기본 요구하지 않음**; 정적 스탯/효과군별 대표 증거 우선, 검증되지 않은 군만 추가.
2. 확인된 E를 기존 v094 후보 생성/하한에 반영하되, F/J/O/L의 소유권을 유지하며 `gear_*`로 정적 rating을 이중 적용하지 않음. 사용자 선택에 정확한 enchant ID·슬롯을 포함해 프로필/바이너리 identity로 캐시 분리.
3. 동일 방식으로 음식·물약·영약·증강룬·일반 보석·특수 다이아몬드·장식에 실제 item/spell/quality/slot 연결. 효과 동일성/수치가 확실한 경우에만 최고 품질 및 최고 강도 정규화. 기존 SimC를 주기적으로 새로 다운로드하는 상시 감시 기능 금지.

**완료 범위:** 분류 코드·별도 오프라인 budget primitive·표적 Native 도구·테스트 소스/회귀 workflow *작성*. **미완료:** 신규 테스트 PASS 영수증(현재 hosted runner 배정 전 실패), 신규 Native rating 실측, v094 실제 candidate planner 연동, 전체 사용자 UI 선택. main/원본 v003/Project UI 불변.
