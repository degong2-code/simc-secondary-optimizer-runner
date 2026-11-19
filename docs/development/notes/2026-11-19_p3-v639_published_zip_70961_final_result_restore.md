# P3 v639 — 기존 282파일 Windows 베타 ZIP 원본 그대로, 현 시즌 70961 실제 최종 64/95% 결과 저장·재열람 PASS

2026-11-19 KST · 격리 브랜치 `probe/chat-cache-v035-20261024` · 원본 ZIP·제품 런타임 코드 수정 **0**

## 1. 목적·필요성·기존 증거 재사용

- v638은 **기존 배포 ZIP 자체**에서 실제 KR 70961 ZERO-SOURCE·G/J/F/O·38/38 영구 마부·실제 Chrome 수동 `T=3500`·마부 E58·Native4 취소/재개를 검증했지만, 배포 ZIP 자체에서 `SimC Native64 → 최종 DPS/SEM/95%/대안 → 저장/HTTP 재시작/재열람`까지 **같은 세션의 최종 출력 인수**는 미확인.
- 별도 checkout v624에서 이미 같은 시즌·SimC 바이너리로 E0 사용자 Native64·결과 저장/재열람 PASS가 있으나, **v624 이후 세션·환경·UI 등 결과 관련 파일 변경**으로 원본 배포 ZIP의 동일 결괏값·복원을 무검증 간주할 수 없음. 26개 전문화/전체 마부/전체 시나리오 반복 없이 **최초 대표 1건만** 64회 한정 실검증.
- 기존 `integration_probes/p1_v624_real_70961_browser_enchant_full_result_once.py`와 `p1_v621`의 이미 성공한 시나리오·원래 `v113/v216/v212/v093/v291` 엔진을 **재사용**. 새 최적화 엔진·효과 구현·독립 SimC/AI·G/J/F/O 재산출 로직 없음.
- Workflow `.github/workflows/p3_v639_published_zip_final64_once.yml`: **기존** [v181 Windows ZIP 배포 artifact #14512093279](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44490716235/artifacts/14512093279) 다운로드 → 내부 ZIP SHA256 `855e8bca8e53f2e7f6efabaa39a20f92c2308f7f409cb4b75a1adc75eb022bfd`, SHA 검증된 **282파일** 압축 해제 → 외부 source/SimC 아이덴티티 확인 및 역사적 미승인 `70575` 자료는 **임시 시험 폴더에서만 격리**. QA 프로브만 임시 추출 폴더에 복사, ZIP 원본에 삽입 없음. `v113/v216/v222/v632`를 실제 압축 해제 ZIP 내부 파일 경로에서 가져오는 모듈 출처검사 PASS.
- SimC 원본 동일 시즌 캐시 Windows binary: revision `9933ffb946fb55b1fa66657b848f519ac19006e1`, build `12.1.5.70961`, SHA256 `4f4472ac8687d029cd7d6041741f44aa98750ea1b3e953dfa7002dee1f38879f`.

## 2. 원본 Windows Actions·실환경 결과

- [Actions **#44539361949 SUCCESS**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44539361949), 검증 시 HEAD `001d0432d0c53e81b69ee2ce05372898f698aff3`, [artifact #14538770682](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44539361949/artifacts/14538770682), JSON `V624_REAL_CHROME_ENCHANT_FULL_RESULT_RESTORE.json` SHA256 `518e656d150378182ad146a4449a6e2eeda4579c45529916735359095747069f`. 별도 실제 신규 영수증으로, 역사적 v624 결과 복사·DPS 캐시 주입 아님.
- 영수증 `status=PASS_REAL_CHROME_SIGNED_E0_64_FINAL_RESULT_REOPEN`, source `12.1.5.70961` 실시간 일치, `G=2850,J=92,F=165,O=0,B=T=3107`; 설치된 시즌 환경 `environment_ready=true`, `requires=[]`, 영구 마부 **38/38**. 환경 `native_calls=15` (6 기본+9 마부 실측), 기존 바이너리 사용/재컴파일 **0**.
- 사용자 실제 Chrome UI: **징벌 성기사**, 목표 ilvl **334**, 실물 장신구 `270175/270173`, 가슴 영구 마부 `7957(E0)`, 기름 없음, 기본 자동 T3107. 현재 장비 전체 재분배/착용 장비 입력 아님. 수동 T3500/E58 v638은 **별도** 증거임.
- **현재 ZIP 자체 실사용자 SimC Native64**: 최초 Native **2** → Chrome 취소 → 실 HTTP 재시작 → 같은 서명된 세션 및 선택값 복원 → 새 Native **3**부터 계속 → 총 **64** 완료, 세션 `BUDGET_EXHAUSTED`; 출력 저장 후 다시 HTTP 서버 재시작/브라우저 refresh해 **동일 저장 결과 재열람**, Native 카운트 **64 그대로**, 재열람 추가 Native **0**.
- 관측 최고 후보: `crit=1098,haste=922,mastery=922,versatility=165`, 합 T **3107**, 비율 각각 `35.3396%,29.6749%,29.6749%,5.3106%`; `observed_dps_mean=161718.63361731684`, `simc_sem=243.11319629437276`. **95% 방향 우위 미확정**, 근접 대안 **5개**, `global_optimum_proven=false`. 실제 Chrome `DPS 161,718.6, SEM243.11, conf95=미확정, 4 ratings, 5 alternatives` 표시 및 재열람 시 정확히 동일.
- 저장된 `V291_RESULT.json` SHA256 `9e3e3f8631bc92859762f5ee732fb361ac6aa0c9e9c9f4d4bd3a0e142f1a22fb`, 저장 세션 탐색 목록 표시 `v622_saved_result_index_visible=true`, `browser_final_verified=true`, `http_restart_final_result_reopened=true`, `native_attempts_after_readonly_reopen=64`.
- 역사적 별도 checkout v624의 다른 관측 DPS 161540.47·rating944/792/1206/165를 **현 ZIP 결과로 복사하지 않음**. 시즌/목적함수 동일이라는 이유만으로 두 관측 최적 후보의 동일성·통계 확정/차이 원인을 단정하지 않음.

## 3. 종료 판정·효율·제품 경계

- **PASS:** 동일한 기존 배포 ZIP을 통한 실제 KR70961 ZERO-SOURCE→검증된 옵션→실 사용자 대표 프로필→원래 적응형 SimC64→DPS/SEM/95%/절대 CHMV·5대안→결과 저장·HTTP 재시작/재열람의 **대표 1건 종단 E2E**.
- **비용:** 환경 Native15 + 사용자가 탐색한 **64 Native 한 차례**, SimC 컴파일0·제품 코드수정0·원본 ZIP 재패키징0·26전문화 전수 반복0·마부 38건 별도 DPS 전수0·유저 데이터 업로드/실사용 PC 설치0. 이 실행은 v624와 달리 **최신 배포 ZIP 최종 결과/재열람이라는 남은 최초 인수 경계**를 증명하기 위해 제한적으로 수행함.
- **범위 밖:** 실제 개인 Windows PC 설치, 모든 26전문화/선택 조합, 자동 설치/외부 인증키 없이 전 사용자 성공, 수동 T3500·양수 E58 시나리오의 Native64 최종 결과, 향후 시즌, 확장팩 특수 모듈 전체 완료. 이 한 사례 PASS만으로 제품 **전범위** 완료라 표시하지 않음.
- **STOP:** 본 ZIP E0 최종 결과·재열람 실증 경계 완료. 같은 64 Native 재실행/전수 확장 **중단**. 후속은 실제 사용자 설치/의존성·동의·명료한 오류 안내와 제품 범위/릴리스 검토로 한정; 관련 최신 기존 영수증 먼저 재사용.
- **공식 상태 유지:** `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`. 78 요소 계약의 공식 승격/Shared State·Work OS·Project UI 적용은 별도 사용자 권한. 현재 격리 브랜치 외 main/v003 immutable 변경 없음. 주 제품 개발 채팅 소유권 불변.
