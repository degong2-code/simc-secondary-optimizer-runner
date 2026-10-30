# SIMC Secondary Optimizer — Windows 로컬 베타 시작

**대상:** Windows 10/11, Python 3.12 이상, 사용자 PC의 SimC CLI (`simc.exe`).

## 시작하기

1. `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip`을 **압축 해제**합니다. 압축파일 내부에서 직접 CMD를 실행하지 않습니다.
2. 먼저 Python 3.12 이상을 설치하고, 압축 해제한 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA` 폴더에서 터미널을 열어 아래 중 본인 Python 환경에 맞는 **한 줄만** 실행합니다.
   `py -3 -m pip install -r requirements-web.txt` 또는 `python -m pip install -r requirements-web.txt`.
   - Python과 FastAPI/Uvicorn은 공개 PyPI 의존성입니다. 실행기는 **자동으로 패키지를 설치하거나 다운로드하지 않습니다**.
3. 같은 폴더의 `START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd --check`를 먼저 실행해 웹 서버 의존성을 확인할 수 있습니다. 실제 SimC 호출도 웹 서버 기동도 하지 않습니다.
4. `START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd`를 **더블클릭**합니다. 서버는 **본인 PC의 127.0.0.1:8765**에만 열리고, 해당 서버가 실제 시작된 뒤에만 기본 브라우저가 열립니다. 종료 시 CMD에서 `Ctrl+C`.
5. 브라우저에서 26개 DPS 전문화 중 하나를 선택합니다. 목표 ilvl **266–344**(기본 334), 수동 최종 T(선택), 장신구 2개, 특성/종족 및 나머지 사용자 설정을 입력합니다. **최신 시즌 대표장비**가 새 사용자 폼의 기본입니다. 일반 방어구/무기/티어 4세트는 내부 구성됩니다.
6. 사용자가 별도로 설치/확보한 실제 Windows SimC CLI 파일의 **전체 경로(`simc.exe`)**와 그 실행 파일에 대응하는 **실제 SimC Git revision(7–40자리 16진수)**을 입력합니다. 해당 값은 임의로 가정하면 안 됩니다. **ZIP에는 SimC 실행 파일 자체가 포함되지 않습니다.**
7. **예산 미리 확인**은 SimC Native 0회입니다. 입력과 예산이 맞으면 **SimC 최적화 실행**을 눌러 실행합니다. 이것만 실제 SimC 후보 계산을 시작합니다. 원래 적응형 탐색의 기본 최대 6후보, 95% 판정·DPS·SEM·CHMV 비율·근접 대안을 화면에서 확인합니다.
8. 사용 중 **취소 → 같은 세션 재개**, **완료 결과 캐시 6/6 재검증**, **이 PC의 이전 세션 복원**을 사용할 수 있습니다. 완료된 SimC JSON2 영수증을 검증해 재사용하며 다른 PC의 캐시는 자동으로 신뢰하지 않습니다.

## 저장·보안·문제 해결

- 사용자 세션·진행정보·캐시는 `%USERPROFILE%\SIMC_Secondary_Optimizer\runs`에 저장합니다. 새 ZIP으로 업데이트해도 기존 `runs` 폴더를 삭제/덮어쓰지 마세요.
- 특별히 선택한 특수장비의 정확한 Native 정적 스탯 L 기록이 없다면 기존 규칙상 계획이 차단됩니다. **L=0으로 가정하지 않습니다.**
- `--check`가 `ERROR: No Python 3.12+ ...`를 보이면 사용 중인 Python 버전과 `requirements-web.txt` 설치 여부를 확인하세요.
- 이미 포트 **8765**를 다른 프로세스가 점유 중이면 잘못된 웹페이지를 자동으로 열지 않습니다. 기존 프로세스를 종료한 다음 실행하세요.
- 로컬 웹서버는 개인 PC 루프백에 한정됩니다. 다른 IP/네트워크·공개 인터넷에 노출하지 않습니다. 공개 인터넷으로 SimC 프로필을 업로드할 필요가 없습니다.
- `v147_batch` 기존 영수증이 함께 있으면 **읽기 전용 조회**만 합니다. 신규 프로필 캐시로 가져와 재계산을 생략하지 않습니다.
- 이 파일은 **소스·의존성 안내를 포함한 Windows 베타 ZIP**이며, 독립 EXE 설치 프로그램 또는 SimC 바이너리 통합 패키지가 아닙니다. 실제 Windows 사용자의 SimC 설치 환경에서 새 시즌 v180 계산을 끝까지 실행했는지 여부는 별도의 사용자 PC 실측으로 구분합니다.

## 유효한 검증 범위

GitHub Windows Actions는 베타 ZIP의 진위·추출·의존성·Windows Python·로컬 서버·계획 생성·세션 분리·복원·안전 장치를 검사합니다. 실제 Win64 SimC Native 실행은 **사용자 SimC 설치·환경과 연결된 경우에만** 가능합니다. 기존 Linux v180 실제 SimC 36건과 과거 Windows v111 Native 실측은 별개의 증거입니다.
