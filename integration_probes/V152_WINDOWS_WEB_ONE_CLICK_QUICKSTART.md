# P1 — Windows 로컬 웹앱 더블클릭 시작 (v152)

> 기존 GitHub 격리 브랜치에 코드가 있고 Python 3.12+ 및 `requirements-web.txt` 의존성이 설치된 상태에서 사용한다. **이 파일 실행 자체는 SimC Native를 전혀 호출하지 않는다.** 사용자가 웹앱에서 새 최적화 실행을 명시할 때에만 기존 v106→v098→v096→v094 Native 경로가 작동한다.

## 집 또는 회사 PC

1. GitHub 최신 코드가 있는 `simc-secondary-optimizer-runner` 폴더의 `START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd`를 **더블클릭**한다.
2. CMD는 `py -3` 우선, 없을 경우 `python`을 사용한다. 최소 Python 3.12과 `fastapi`, `uvicorn`이 설치되어 있는지 확인만 한다. 누락하면 오류와 수동 설치 명령을 알려주며 **자동으로 pip를 실행하지 않는다**.
3. 회사처럼 저장소 옆에 `..\v147_batch\`가 있으면 그 복사본을 **읽기 전용 열람 데이터**로 지정한다. 그렇지 않고 `%USERPROFILE%\SIMC_Secondary_Optimizer\v147_batch\`가 있으면 이를 사용한다. 둘 다 없으면 결과 열람 영역에 기존 실측 배치가 없다고 표시하지만 신규 세션 입력은 이용할 수 있다.
4. 서버가 실제로 `127.0.0.1:8765`에 바인딩되었을 때에만 기본 브라우저에서 화면을 연다. **이미 다른 프로세스가 8765를 점유하면 타 서버 페이지를 자동으로 열지 않는다.** 종료하려면 열린 CMD 창에서 `Ctrl+C`.
5. `START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd --check`는 의존성/경로 준비 상태만 보고 종료한다. 서버·브라우저·Native 모두 호출하지 않는다.

회사 PC 예시:
```text
C:\Users\yesfprop\Desktop\새 폴더\
├─ simc-secondary-optimizer-runner\START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd
└─ v147_batch\simc_b0ea12ee3ac233a4_7bc1071\SUMMARY.json
```

이 기능은 `v147_batch` 원본·확정된 DPS 캐시·세션 identity를 **재작성하거나 다른 PC의 실행 캐시로 자동 승격하지 않는다**. 홈/회사 간 기존 사용자 세션(`runs`)은 각 PC 로컬 저장소에 계속 별도 존재한다. 기존 API의 `--batch-root` 수동 인수도 그대로 사용할 수 있다. GitHub `main` 병합·새 시즌 지원·프로그램 설치 프로그램 완성은 아니다.
