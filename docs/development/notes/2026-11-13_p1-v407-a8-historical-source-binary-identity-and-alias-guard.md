# v407 — A8 SimC revision·소스/실행 바이너리: 역사 영수증 재사용 및 별칭 경로 보수

**범위:** A8 `historical=PASS`(한 조건), `generic/current_source/product_integration=PENDING`, `policy.next_review=A8`, USER-E2E=PENDING. 기존 실행·원본 바이트를 재다운로드하거나 Native를 실행한 것은 아니다. 기존 `v229/v275/v241/v217/v216` 소스 검증과 `v234/v277/v291` Native/캐시를 재사용한다.

## 기존 영수증 — 같은 바이너리·빌드 한 조건

- [v342 공식 Windows CLI 원본 Actions #43046174810](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43046174810): `official-windows-source-no-dps` job SUCCESS. `simc-1210.01.de11f57-win64.7z`, archive SHA256 `a4c4d5e7b349172d80897721daa3e849ce25874a82bbdfb96aeab4dbdc560eb0`, 실제 exe SHA256 `1fc927d2be7f1b6064c75f004b5b22245b064a6b3e56e572af4048ba822a986d`, 무프로필 CLI banner의 `12.1.5.70783` 확인, DPS Native0. `simc-publish` publisher HEAD를 엔진 Git revision으로 오인하지 않는다.
- [v344 실제 Windows Chrome→Native64 Actions #43114134208](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208): tested SHA `d8620d733140b148deb534975485f45ee22cf118`, job SUCCESS. 위와 같은 exe SHA를 확인하고 `SIMC_PINNED_SOURCE_COMMIT=de11f57df75dda668bae6ac7043a43b98831fa96`를 사용. KR `12.1.5.70783`, ilvl334 생존 사냥꾼 조건에서 환경 Native3→DPS Native64·SEM·95%·취소/재개 성공. 관련 [v383 영수증 재조회](2026-11-13_p1-v383-a10-a11-g2-archived-native-receipt-reuse.md)의 원래 ZIP·SHA는 그대로 재사용한다.
- 실행 코드 `v234.observe`는 JSON2 `git_revision`을 정확한 source commit prefix와 대조하고, `v291`은 실행 바이너리 SHA/세션 identity를 검증한다. **이번 감사는 이전 영수증의 한정 범위 재인정이지 새로운 Native 실행 결과가 아니다.**

## 실제 코드 최소 보수

`runner/v277_zero_history_native_G_stage.py::collect`에서 원래 `Path(binary).resolve(strict=True)` 이후 `is_symlink()` 검사는 원본 symlink를 잃는 순서 오류였다. 경로 정규화 전에 직접 supplied binary 경로의 symlink 여부를 거부한다. 정상 바이너리 SHA, Native 횟수, 기존 stage·DPS cache identity, SimC 오류 원문, B/T 계산은 변경하지 않는다. `tests/test_v277_zero_history_native_G_stage.py`에 symlink alias의 Native-before 차단 회귀를 추가한다. 테스트 결과는 Actions 종료 후 별도 판정.

## 미완료/다음 작업

- `generic`: 실제 현재 source+binary 관계와 변경 season/build/revision/ID/바이너리 SHA 변형 회귀의 해당 범위 영수증을 확인.
- `current_source`: v229/v275/v241의 봉인 SHA·실행 바이너리 CLI build/Native revision이 **같은 실제 요청에서 사용**됐는지 확인. 기존 v236의 `compiled_game_build_not_proven=True`는 정당한 제한으로 유지하며, CLI 표시/파일명만으로 바이너리 컴파일 출처의 독립 재현·서명을 주장하지 않는다.
- `product_integration`: v113→v216→v212/v098→v291/v293 사용자 경로에서 정확 identity·캐시/불일치 차단을 새로운 범위의 실제 사용자 영수증으로 확인.
- A9는 A8 완료 범위 판정 이후 기존 v275 원본 파일만 재검토한다. 신규 Gate·새 알고리즘·전수 Native·대규모 DB2 재수집 없음.

**권한:** 격리 브랜치만. main/v003/Project UI/Work OS/Shared State 무변경.
