# P1 v148 — 24개 Windows SimC 결과를 로컬 웹에서 읽기 전용으로 열기

이 기능은 **사용자가 실제 Windows SimC로 완료한 v147_batch 결과 원본**을 로컬 웹 UI에서 확인하는 기능입니다. GitHub Actions에서 새 Native를 실행하지 않으며, 기존 168회 실측을 반복하지 않습니다. **실측 원본 폴더 전체**가 PC에 있어야 하고, SUMMARY.json만으로는 결과를 확인했다고 표시하지 않습니다.

## 집 PC에서 실행 (PowerShell)

```powershell
cd "$HOME\Desktop\simc-secondary-optimizer-runner"
git pull --ff-only
py -3 -m pip install -r requirements-web.txt
py -3 runner/v113_local_web_api.py --batch-root "$HOME\SIMC_Secondary_Optimizer\v147_batch"
```

서버 실행 창은 켜 둔 상태로 다른 PowerShell에서 브라우저를 엽니다.

```powershell
Start-Process "http://127.0.0.1:8765/"
```

웹앱의 **24개 전문화 실측 결과**에서 로컬 배치를 선택한 뒤 **저장된 24개 결과 보기 · Native 0회**를 누릅니다. 상세 디렉터리는 브라우저나 다른 사람에게 전송하지 않습니다. `summary.user_result`를 그대로 믿지 않고 로컬 physical.json의 원본 SHA, v145 receipt의 사용자·바이너리·revision·대표 프로필 SHA, 기존 v094 결과에서 다시 계산한 DPS/SEM/95% 표시값과 대조합니다. 일치하지 않는 전문화는 대체 추정값 대신 **미확인**으로 표시합니다.

## 회사 PC 등 복사본에서 열기

집 PC의 `C:\Users\degong2\SIMC_Secondary_Optimizer\v147_batch` **폴더 전체**를 회사 보안 정책에 맞게 개인 외장 드라이브 등에 복사합니다. 개인정보/캐릭터 특성/로컬 로그가 포함되므로 회사 정책과 보안에 유의하세요. 압축 파일을 풀었을 때 `v147_batch\simc_<binary SHA>_<revision>\SUMMARY.json`, `physical`, `adaptive` 구조를 그대로 보존합니다.

다른 PC의 실제 복사 폴더가 `D:\Private\v147_batch`라면:

```powershell
py -3 runner/v113_local_web_api.py --batch-root "D:\Private\v147_batch"
```

웹페이지는 `http://127.0.0.1:8765/`이며, 기존 Windows SUMMARY 안에 포함된 옛 `C:\Users\...` 경로로 파일을 열지 **않습니다**. 새 PC에는 SimC가 없어도 **결과 열람**은 가능하지만, 기존 144개 최적화 후보의 Native 캐시를 현재 PC 실행 경로로 **자동 승격/이식하지 않습니다**. GUI의 새 최적화 실행 버튼은 기존 `v106/v098` 경로로 계속 작동하며, 복사된 배치의 read-only 표시가 새 입력·특성·소모품·현재 PC 바이너리에 대한 허가를 주는 것은 아닙니다.

## 현재 검증 및 제한

- GitHub Actions는 FastAPI loopback 토큰 경계, 24-result read-only UI, Python 3.12 Ubuntu / Python 3.14 Windows, 파일 복사 경로·영수증/JSON2 SHA 변경·95% 결과 변경 시 fail-closed, Node 스크립트 문법 확인만 수행합니다. 신규 실제 Native 0회.
- v148은 **물리 원본 JSON2 SHA와 v094 완료 보고서의 표시 일치**를 확인하는 뷰어입니다. 모든 여섯 후보의 원본 Native 바이트를 별도 재검증하는 캐시 이식기는 아닙니다. SHA 불일치·미등록 입력·영수증 누락 시 결과 표시 차단.
- 프로그램을 집·회사에서 사용하는 장기 목표는 캐시/세션의 실제 안전한 경로 이식 및 일반 사용자 입력→대표 프로필→최적화 실행입니다. 이 기능은 그 중 **기존 24개 결과의 재계산 없는 열람**만 구현한 단계입니다.
