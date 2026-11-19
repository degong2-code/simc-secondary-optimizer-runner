# P2 v637 — 사용자 수동 최종 T + 검증된 양수 E 다부위 선택, Windows 실제 취소·재개 PASS

2026-11-19 · 격리 브랜치 `probe/chat-cache-v035-20261024`

## 1. 제품 목적과 최소 시험 판단

새 시즌의 전체 영구 마부를 원본/SimC로 자동 등록하는 v633, 대표 G의 선택 E 소유권이 v222→v212에서 유지되도록 한 v636의 개발을 이어 **일반 사용자가 양수 E 마부를 선택하고 수동 최종 T를 입력하는 실제 흐름**을 검증한다. 사용자 T는 `B=T-O`로 권위적이고, 마부 E는 해당 총량 내 스탯별 **고정 하한**이다. 수동 T에 E를 추가하여 사용자 총량을 변경하거나 기존 대표 G에 중복 더해서는 안 된다.

이번 범위는 v635/v636의 **기존 일반 Windows Chrome/UI→v098→v096→v093/v094 적응형 SimC→취소·HTTP 재시작·기존 세션 재개**를 입력만 다르게 시험한 것. **제품 엔진 변경 없음**; `integration_probes/p1_v621_real_70961_browser_enchant_cancel_resume_once.py`에 안전한 `manual_final_T` 선택 인자와 실제 visible checkbox/field 사용, 예산/복원 확인만 추가. `p2_v637_...` 얇은 wrapper 및 기존 v635 workflow에서 분기한 **1회 Windows 테스트 workflow**만 신규. 새 엔진·별도 데이터 Gate·원본 E 재측정 방식·64후보 반복 없음. v621/v624/v627/v635 과거 코드 경로의 기존 인자 기본값은 그대로.

## 2. 실제 증거

- [Windows Actions #44488595284](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44488595284) **SUCCESS** (syntax-only PASS, actual Chrome Windows PASS), 실행 HEAD `ebc7566b18f448c3bf3dbfa4acbbe04762b75610`.
- [실제 compact artifact #14512640169](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44488595284/artifacts/14512640169), 파일 `V637_REAL_CHROME_MANUAL_T_TWO_POSITIVE_E_RINGS_CANCEL_RESUME.json`, SHA256 `ae9b1458c1037122e3336e5bc19c14c2d3fd4cc76d39456e37574389b332878b`. 원본 ZIP 내 JSON 직접 열어 `status=PASS_REAL_CHROME_MANUAL_T_TWO_POSITIVE_E_RINGS_CANCEL_RESUME`, `manual_T_authoritative_verified=true`, `real_user_manual_T_restored=true`, `actual_browser_same_session_resumed=true`, `native_attempts_were_reused_without_reset=true` 확인.
- 동일 빌드 `12.1.5.70961`, SimC revision `9933ffb946fb55b1fa66657b848f519ac19006e1`, 정확 SimC Windows 바이너리 SHA `4f4472ac8687d029cd7d6041741f44aa98750ea1b3e953dfa7002dee1f38879f` 캐시 HIT/재컴파일0.
- 실제 v212 설치 **38/38 등록**; 베이스 `G2850+J92+F165=3107`, O0. 사용자 브라우저에서 선택한 영구 마부 `chest:7957(E0),finger1:8025(가속+29),finger2:7997(치명+29)` **세 마부 각각 SimC 프로필에 딱 1회**. `ΣE=58`.
- 사용자 Chrome의 실제 보이는 수동 T checkbox 켜기 + `final_T=3500` 입력 → 실제 HTTP 요청 `manual_final_T=3500` → 최종 `scenario.json` 내부 `mode=manual_total, manual_total=3500`, **공식 사용자 T=3500/B=3500**, E는 3500 안의 고정 하한. v636 자동 ilvl `B=T=3165`과 다름. `actual_generated_profile_sha256=942159de9015672f686990be28a97c60b740533a585c4235da2e6c59913af358`.
- 최초 실제 Native2→Chrome Cancel→서버 중단/재시작→일반 saved-session 복원→수동 T checkbox·값 3500 및 동일 E 선택 복원→Resume→Native 누적4→안전 중단 `PAUSED_USER_CANCEL`. `new_native_calls=4`, `case_count_after_resume=4`. 결과 창 64후보 전체 완료가 아님.
- **실행 비용**: 신규 환경 구축 Native15 (=G/J/F/O6+미확정 E 실측9), 사용자 DPS Native4, SimC 재컴파일0, 새 Native 64전수 0, 역사 DPS/정적 캐시 강제 폐기0. 이번은 원본 SimC·환경·선택 사용자 경로를 실제로 한 번 통과시키기 위한 수락 시험이며 동일 증거를 위해 반복하지 않는다.
- 변경된 공유 테스트 코드에 대한 [Focused #44488507182](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44488507182) **689 tests / 2 SKIP / 0 FAIL**, [v401 정적 계약 #44488595219](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44488595219) SUCCESS.

## 3. 기존 최종 결과 재열람 증거와 검증 경계

- 이전 **v624 실제 E0 한 부위 64후보 완료→DPS/SEM/95%·근접 대안→Windows UI 결과 저장·HTTP 재시작·읽기 전용 결과 재열람 PASS**는 별도 이전 실증이며 여기서 **재실행하지 않았다**. 결과 저장/재열람은 기존 `v291/v293/v570/v622` 경로를 사용한다.
- **이번 v637의 실증은 양수 E+ 두 반지·E0 가슴·수동 T3500이 정확한 세션으로 생성되고 Native4까지 취소/재개되는 것**이다. 이번 세션은 64후보에 도달하지 않았으므로 최종 DPS·SEM·95% 결과 저장/재열람을 달성했다거나 전역 최적을 보장한다고 주장할 수 없다. `full_product_e2e=PENDING`.
- 향후 일반 제품의 첫 실제 단절을 발견하면 해당 원인만 정확히 수정한다. 무조건적인 38개 마부 재측정, 26전문화 Native 전수, 동일 시즌 반복 DPS64·SimC 재컴파일은 금지. 추가 64 E+ 실제 완주 시험은 **다른 증거로는 메울 수 없는 최종 제품 E2E 필요성이 생겼을 때 한 번만** 시행한다.

**권한/공식 상태:** `main` 미병합, 기존 주 제품 개발 채팅이 계속 소유, Project Sources/UI·Work OS M0 공식 권한 변경 없음. `15/78 COMPLETE`, `next_review=B10`, `full_product_e2e=PENDING` 그대로.
