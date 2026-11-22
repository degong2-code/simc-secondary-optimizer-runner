# P3 v656 — Windows UI/업데이터 구 테스트 계약 최신화 (2026-11-22)

## 근거: v655 실제 Windows CI 및 upstream 바이너리 조사

- 최근 배포 기준 v655 source HEAD: `945ecebab7f6e2eddcfef80251966a39f6695125`; v653 디자인·v655 PC ZIP SHA `61a224653458eaf4a036880a4f4c1e827d64886da96a2c9cb9122593cf66bcca` 유지.
- 기존 문서에 'v655 Windows 전체 CI 미실행'으로 적혀 있었으나, 소스 변경에 의해 실제 Windows v181 Actions가 실행됨. [run #44998171337](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44998171337), Windows Python3.12/3.14 **각 299건 중 5 FAIL**. 패키징 5 PASS, 실제 압축 해제 Windows CMD/HTTP/3 plans는 실패 단계 이전 통과; 종합 PASS 주장 금지.
- 구 테스트 5개는 승인된 후속 UI 변경을 예전 순서·문구/API로 고정: `test_v114_local_web_ui_offline`에서 v652 Omnium/augmentation 순서와 v651 session passive poll comment, `test_p3_v643_simc_update_feedback_offline`에서 v655 구 `/check` API와 원본 빌드 불명확 성공 문자열, `test_p3_v644_settings_ui_and_sevenzip_feedback_offline`의 과거 `7z.exe` 문구, `test_p3_v646_season_recovery_navigation_offline`에서 더 이상 사용하지 않는 GitHub artifact 상세 404 링크 제목을 기대. **제품 코드를 과거 버전으로 회귀시키지 않고** 4개 테스트 파일만 현재 기능·보안 요구에 맞춰 수정.
- 새 테스트를 적용한 격리 브랜치: `tests/test_v114_local_web_ui_offline.py`, `tests/test_p3_v643_simc_update_feedback_offline.py`, `tests/test_p3_v644_settings_ui_and_sevenzip_feedback_offline.py`, `tests/test_p3_v646_season_recovery_navigation_offline.py`. 직접 Node에서 실제 v655 `checkSimcUpdater()` 함수의 새 API·일치 빌드·오류/버튼 상태 `V656_ACTUAL_UI_CHECK_MOCK_PASS` 확인. v655 ZIP SHA/내부 283개 product bytes는 변화 없음.
- **Windows CI 재실행:** [run #44999676032](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44999676032), 수정한 테스트들 기준 Python3.12/3.14. 최종 판정은 Actions 실제 상태 확인 후 별도로 기록. (기록 시점 queued/in_progress). `UnicodeDecodeError` readerthread 경고도 Windows 로그에 보였으나 최초 실패 5개 원인과 분리하여 관찰; 원인 확정 전 서비스 코드 임의 변경하지 않는다.
- [Upstream 공식 simc-publish 11/14 #43556804260](https://github.com/simulationcraft/simc-publish/actions/runs/43556804260) Windows x64 job **SUCCESS**, artifact available이지만 사용자가 확인한 `0d19401` 내장 Live 70783. [11/18 SimC source CI #44328474174](https://github.com/simulationcraft/simc/actions/runs/44328474174)는 Git SHA `9933ffb`에 Live 70961 source 포함, Windows x64 **CI build job success**이지만 artifact 목록 **0** (2026-11-22 확인). Windows 컴파일 성공 **!=** 다운로드 가능한 실행파일. 현재 확인된 공식 Windows 70961 일치 바이너리 artifact/다운로드 링크 **없음**; 가공/생성해서 링크 노출 금지.
- 기존 SimC `0d19401` 수동 파일·v655 설치/호환성 UI·시즌 G/J/F/O·v229/v217·cache/세션/95%/Native 임의 변경 없음. 새로운 외부 다운로드·SimC Native/DPS 실행=0. 사용자가 최신 Windows x64를 얻을 수 있도록 공식 배포 모니터링은 별도 요청/설정 가능; 영구 AI 런타임 의존성 추가하지 않음.
- v653 디자인 변경 없음. 이 턴 소스 수정은 테스트 4개뿐이며 main·Project UI·공식 완료 게이트, v003 불변. `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` 유지.

## 결론/다음 순서

Windows run #44999676032의 정확한 PASS/FAIL 확인 → 사용자 PC v655 환경에서 공식 호환성 조회 메시지와 실제 `simc.exe` 데이터 빌드 확인 → 공식 70961 Windows 배포본이 확인되는 때에만 정확한 다운로드 주소와 SHA·기능 테스트 → 이후 최소 시즌 환경 검증. CI pending 상태에서는 Windows PASS로 표시하지 않는다.
