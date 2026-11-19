# P3 v638 — 기존 282파일 Windows 베타 ZIP 자체에서 현재 70961 ZERO-SOURCE→실 사용자 Native4 검증

2026-11-19 KST · 격리 브랜치 `probe/chat-cache-v035-20261024` · **실제 배포 ZIP 바이트는 변경하지 않음**

## 실제 목적과 가장 싼 기존 재사용

- 인계 P3의 첫 미입증 경계: `v181`에서 이미 배포한 ZIP을 압축 해제한 상태에서, 현 KR 빌드를 다시 발견해 ZERO-SOURCE G/J/F/O와 마부 E를 인증한 후 실 사용자 브라우저의 최적화 Native를 시작·취소·재개할 수 있는지.
- 기존 v181 ZIP의 Windows Python3.12/3.14 BAT/CMD·로컬 HTTP·3개 plan PASS, v572 이전 추출 ZIP Native4, v624 E0 Native64·DPS/SEM/95%·저장·재열람, v637 E+ 수동 T Chrome Native4 영수증을 재사용. **동일 시나리오의 완결을 임의 합성하지 않음.**
- 배포 ZIP artifact [#14512093279](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44490716235/artifacts/14512093279), 내부 ZIP SHA256 `855e8bca8e53f2e7f6efabaa39a20f92c2308f7f409cb4b75a1adc75eb022bfd`, 282개 원래 source file manifest SHA 전부 PASS. 새 패키저/배포 목록 변경 없음.
- QA workflow `.github/workflows/p3_v638_latest_zip_current_70961_native4_once.yml`는 원래 ZIP을 다운로드해 임시 폴더에 풀고 **원래 v637 Chrome 프로브만 임시 추출 작업공간에 복사**하여 실행. 이 보조 스크립트들은 원본 ZIP 안에 넣지 않았음. 실제 `v113/v216/v222/v632` 제품 모듈은 ZIP 내부 파일 경로에서만 로드됨. ZIP의 역사 `70575` 미승인 source는 임시 검증 workspace에서 격리하고, 현 `70961`은 API/SimC로 새로 구축. 출시 ZIP이 자체로 과거 데이터를 자동 READY 승격했다는 의미 아님.

## 실제 Windows 실행 영수증

- 최초 [Actions #44508544646](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44508544646) **FAIL (Native0)**: 282파일 SHA PASS 뒤, 검증 workflow가 `fastapi` 설치 전에 Python import를 수행해 `ModuleNotFoundError`. **검증기 사전 순서 오류**였고 제품 코드/ZIP의 장애 증거가 아님. 오프라인 모듈 위치 확인을 `PathFinder.find_spec`로 교정한 후 시험 1회 재실행.
- 최종 [Windows Actions #44508695759](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44508695759) **SUCCESS**, 실행 HEAD `8ced0eb641c0b3cfed8a407d7ae67c78ad09dce0`, 원본 compact [artifact #14521371380](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44508695759/artifacts/14521371380), 내부 JSON SHA256 `219d17fecb5ebc3735ed0e1d58006cc7a2a63a8ae785bea793be15cc5c68f1aa`.
- 원본 JSON `status=PASS_REAL_CHROME_MANUAL_T_TWO_POSITIVE_E_RINGS_CANCEL_RESUME`; 실 KR/SimC `12.1.5.70961`, SimC rev `9933ffb946fb55b1fa66657b848f519ac19006e1`, Windows binary SHA256 `4f4472ac8687d029cd7d6041741f44aa98750ea1b3e953dfa7002dee1f38879f`.
- 원래 ZERO-SOURCE 결과 `G2850/J92/F165/O0/B=T3107`, 환경 READY 및 설치 true, `native_calls=15` (=기본6+E실측9), 38/38 영구 마부 등록, 필수 `requires=[]`.
- 사용자 실제 표시 선택: `chest:7957(E0),finger1:8025(가속+29),finger2:7997(치명+29)`; 정적 `E_total=58`. `manual_final_T=3500`이 자동 `3165`보다 우선, `signed_actual_base_B=3500`, 각 마부 SimC 프로필 한 번씩. 프로필 SHA `942159de9015672f686990be28a97c60b740533a585c4235da2e6c59913af358`.
- 실제 사용자 Native 2 → Chrome Cancel → 로컬 서버 재시작 → 수동 T/E/세션 복원 → 같은 세션 추가 Native → **누적4**, 중단 상태 `PAUSED_USER_CANCEL`, `native_attempts_were_reused_without_reset=true`. 사용자 DPS Native4·재컴파일0·기존 캐시 강제 폐기0.
- **검증 범위:** 이 최신 ZIP에서 현 시즌 설치·실 사용자 E+ 옵션·수동 T·Native 취소/재개까지 SUCCESS. 이 세션의 최종 Native64 완주·결과/95%·저장·재열람은 **시험하지 않음**. 해당 기능은 별도 v624 실제 Native64·저장/재열람 증거를 재사용하되 동일 ZIP/동일 세션 E2E 완료라고 주장하지 않음.

## 결론·STOP

- 제품 코드 버그 발견 **0**, 새 최적화 엔진/효과 Gate/컴파일/마부 전수 반복 없음. QA 사전 점검 순서만 1회 교정. 기존 배포 ZIP·제품 Python/JS/SimC·사용자 캐시를 바꾸지 않음.
- 현 ZIP의 Native4 이전 첫 미입증 접합 경계는 이제 한 시나리오에서 실증됐으므로 동일 범위 Native4 재실행 **STOP**. 최종 `full_product_e2e=PENDING` 및 공식 `15/78 COMPLETE`·`next_review=B10` 유지.
- 이후 실제 출시 인수에 필요한 한 단계는 **같은 배포 ZIP의 최종 사용자 결과·읽기 전용 재열람 범위**를 기존 v624 증거와 대조해 *부족한 차이만* 검증할지 판단하는 것. 필요성 없이 또 Native64/26전문화/38마부 전체 반복 금지.
- `main`, v003 immutable, 원본 v016, Project UI/Work OS 공식 승격, 주 제품 개발 소유권 불변.
