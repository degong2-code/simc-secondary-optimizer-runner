# P2 v636 — 검증된 G 소유권 전달 누락 교정과 E+ 실제 Windows 사용자 흐름 PASS

2026-11-19 · 격리 브랜치 `probe/chat-cache-v035-20261024`

## 제품 목적/수정 필요성/근본 원인

제품은 새 시즌의 **전 영구 마부를 확인**하되 이미 검증된 E0/정확한 E는 SimC Native로 다시 측정하지 않고, 사용자에게 허용된 물리 부위에 선택된 **정확한 정적 E만** 공식 최종 CHMV 총량·스탯별 하한에 **한 번** 반영한다. 이번에 남았던 **실사용 첫 차단**은 `FRESH_SELECTED_ENCHANT_POSITIVE_E_G_OWNERSHIP_UNKNOWN`이었다.

- **소유권 증거는 이미 존재:** 정상 새 시즌 `v216._zero_history_default... ` 원본은 `v233` **무마부 대표 장비**로 표준 G를 구성하고 검증된 `trusted_budget_evidence.G_reference_excludes_selected_E=True`를 `v222.preprofile_budget`에 제공한다. `v222`는 입력 bool을 확인하고 E/L 정합·G/B/T를 계산했으나 **출력 반환 객체에 이 필드를 버렸다.**
- **실행 중 증거 소실:** `v212.compile_fresh_installed_environment`는 반환된 `v222` 계산 객체를 서명된 설치 문서의 `v222_reconciled_budget`에 넣으므로 원래 G의 E 소유권 사실이 더 이상 없다. 실제 E+를 선택한 `v212.preview_installed_selected_enchant_budget`는 값을 유추하거나 임의 E0로 처리하지 않고 정상적으로 **차단**했다.
- **최소 필수 엔진 수정:** `runner/v222_season_budget_contract.py`가 기존 `G_reference_excludes_selected_E` 검증값을 **동일 예산 결과에 전달**하고, 이미 존재하는 `v212`의 서명/재검증·마부 G 소유권 검사에서 소비한다. 새 수집·인증 Gate, 새로운 E 계산·Native/Solver, 별도의 게임 효과 판정, 기존 캐시 폐기는 **없다**. 과거 서명된 E0 설치 문서에 빠진 필드를 허위로 주입하지 않으며, 새 `v222→v212` 서명으로 정당하게 보존한다.
- 코드 `910e5656`, 관련 반례/하위 호환 테스트 `31d45a6c`, `5b930b1d`, `168c4dfd`; 최종 실제 Win 트리거 문서 주석 변경 `937ea1c8`. **작업 흐름의 기존 v098/v096/v093 E+ 경로는 이번 문제 해결에서 재설계하지 않음.**
- 이전 실제 [v635 Windows #44484358694](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44484358694) **FAIL** 원본 영수증 `FRESH_SELECTED_ENCHANT_POSITIVE_E_G_OWNERSHIP_UNKNOWN`; 38 마부 등록/웹 선택/ID 요청은 통과했으나 사용자 Native DPS 0. 이는 신규 효과·Native 증거 부족 때문이 아니라 예산 소유권 투영 단절이었다.

## 실제 Windows 검증 — 동일 시즌 최초 양수 E+ 세 부위 소비 성공

[Actions #44486603654](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44486603654) **SUCCESS**, 실행 제품 HEAD `937ea1c88f0a6e6fc39c4a466b583baba85bfd9f`. 실제 증거 [compact artifact #14510568693](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44486603654/artifacts/14510568693), 원본 `V635_REAL_CHROME_TWO_POSITIVE_E_RINGS_CANCEL_RESUME.json`, 파일 SHA256 `24f929bcae50856b38d5b4878fb43a9324be2809ca6cb810b7f4f19c56691fdf`.

- 실제 게임 빌드 `12.1.5.70961`, SimC revision `9933ffb946fb55b1fa66657b848f519ac19006e1`, 동일 Windows SimC 바이너리 SHA256 `4f4472ac8687d029cd7d6041741f44aa98750ea1b3e953dfa7002dee1f38879f`; **재컴파일 0**.
- 기존 새 시즌 `G=2850,J=92,F=165,O=0`, **기본 B=T3107**. 등록 영구 마부 총 **38/38**. Chrome의 사용자 실제 검색 목록에서 **가슴 7957(E0), 첫 반지 8025(가속 +29), 둘째 반지 7997(치명 +29)** 선택. 실제 웹 요청의 마부 ID `{"chest":7957,"finger1":8025,"finger2":7997}`·기존 두 장신구/ilvl334/SimC 빌드 정확 일치.
- `ΣE=58`, **최종 자동 B=T3165**, E0 가슴 포함 각 실제 SimC 장비 라인의 `enchant_id` **정확 1회**, 원본 프로필 SHA256 `942159de9015672f686990be28a97c60b740533a585c4235da2e6c59913af358`. 서명된 새 `v212` manifest SHA256 `4c50ce6ac77d3c1441b269da5c3fc1ca83e1240b550d1a12efafaed66f7750bb`, 같은 세션 시작 및 재개.
- **실제 새 사용자 Native 4회:** 처음 2회→Chrome Cancel→HTTP 서버 중단·재시작→기존 세션 복원→최소 Native 추가 실행 후 누적 4회→추가 중단 상태 `PAUSED_USER_CANCEL`; `native_attempts_were_reused_without_reset=true`. 실제 비동기 캐시/취소·재개를 재현했으며 **64후보 완료/최종 DPS·95%/전역 최적해 실증이 아님**. 이전 E0 단일 v624 Native64/95% 성공은 **독립 역사 증거**.
- 이번 작업의 총 실환경 비용 **기존 시즌 G/J/F/O용 Native6 + 마부 E 측정 Native9 = 환경 Native15**, 신규 사용자 DPS Native **4**, 기존 SimC 바이너리 cache HIT/재컴파일0, 64후보 재실행0, 역사 DPS/정적 캐시 강제 삭제0. 새 시즌 설치 영수증에는 원래 빠진 G 소유권이 포함돼야 하므로 **이 한 번의 현재 빌드 재구축은 실험 목적상 필요**, 단순 코드 변경 때마다 Native를 무조건 실행하는 정책은 아님.
- 신규 회귀: [focused #44486351071](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44486351071) **689 tests, 2 SKIP, 0 FAIL**, [v212 Windows/Ubuntu #44486351166](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44486351166) **각 535 tests, 4 SKIP, 0 FAIL**, [v410 #44486351247](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44486351247) PASS, [78 계약 #44486351061](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44486351061) PASS. 실환경 트리거 HEAD의 [focused #44486603790](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44486603790)도 SUCCESS.

## 검증 경계 및 다음

- **완료 범위:** 70961 38개 등록, 실 사용자 3개 부위 E+/E0 중첩, 자동 B/T에 E 1회, SimC 프로필 입력, 한 세션 Chrome 취소→HTTP 재시작→동일 세션 Native 재개 4회까지. `v222` 소유권 정보 유실의 일반적 재발 방지. 과거 v212 E0 설치에 임의 `G_reference_excludes_selected_E`를 추가하지 않는 반례 테스트 포함.
- **여전히 미완료:** 사용자 수동 T+양수 E의 실제 Chrome/SimC 실행(오프라인 회계 PASS는 별도), 이 3부위 세션의 64후보 최종 결과·95% 판정/재열람, 다른 모든 부위/장신구/26 DPS 조합 전수 검증, 독립 배포 E2E. 사용자 목적은 일반 제품 전체 완료이지 78항목 수 채우기 아님. 현 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` **공식 원장 상태 유지**.
- **효율 원칙:** 다음 사용자 단절만 기존 v098/v096/v093/v094/v291 안에서 해결. 70961 정적 E 38개 전부 재측정 금지, 같은 E0/양수 E Chrome Native64 반복 금지, P1 일반 사용자 설치→시즌→DPS→결과 저장·재열람 전체 흐름이 필요한 최소 부분만 검증.

본 작업은 격리 브랜치에서만 수행하며 `main` 병합, `v003` 불변 기록, Project UI 실제 적용, Work OS 공식 권한, 기존 주 제품 개발 채팅 소유권을 변경하지 않는다.
