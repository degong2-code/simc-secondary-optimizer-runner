# P2 v627 — 실제 70961 두 부위 영구 마부 동시 선택 → SimC Native → 취소·재개 PASS

2026-11-19 · 격리 브랜치 `probe/chat-cache-v035-20261024` · **사용자 최신 결정: 지원되는 모든 마부는 부위당 하나씩 동시에 선택 가능**. v626의 14개 슬롯 UI 및 v106→v098/v216→v212→v096 다중 E0 서명 검증 경계를 실제 Windows Chrome·동일 빌드 SimC로 최소 검증. 사용자 일반 제품의 전체 26전문화 인수 완료를 주장하지 않음.

## 1. 결론과 실제 사용자 경로

- **최종 Actions [#44463091504](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44463091504): SUCCESS** (사전 Python/JavaScript syntax-only PASS; Windows actual Chrome job PASS). 원본 [artifact #14500284190](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44463091504/artifacts/14500284190), 내부 `V627_REAL_CHROME_TWO_ARMOR_E0_CANCEL_RESUME.json`, **7,635 bytes**, SHA-256 **`3ad8cc3e360b6806ddd071db5e79f16078d7118745afb7b151e0b3ee522c6c23`**.
- 정확한 사용자 선택: **징벌 성기사 / 목표 ilvl334 / 머리 `enchant_id=7959` / 가슴 `enchant_id=7957` / 장신구 270175·270173 / 기름 O=0 / 수동 T 미사용**. 사용자 장비 전체를 선택받지 않고 내부 대표 장비 사용.
- **실제 빌드 `12.1.5.70961`** = SimC 소스 `9933ffb946fb55b1fa66657b848f519ac19006e1`; Windows `simc.exe` SHA `4f4472ac8687d029cd7d6041741f44aa98750ea1b3e953dfa7002dee1f38879f` 기존 캐시 재사용. **재컴파일 0**.
- 실 설치 `v212` SHA **`1dbdfa0eac3ac2ad354e62d1bc435136755c346aa74a93857e6664b78dcb2511`**; 서명된 E0 등록 19건. 실제 Chrome의 활성화된 머리 7959/가슴 7957 각각 선택, 독립 선택 유지, `buildRequest().controls.enchant_choices={"head":7959,"chest":7957}`; 요청 및 HTTP 재시작 후 저장 UI 모두 **같은 설치 SHA**로 확인.
- 내부 대표 프로필 SHA **`24c2880a4c63bbf8a820b42a9a678330307a4604a880f2d323732cb014dc88cf`**. 실제 최종 `head=` 장비 라인과 `chest=` 장비 라인에 각각 **해당 ItemID + `enchant_id` 정확 한 번**, 프로필 전체 중복 0. 별도 효과/proc 처리기 없음(원래 SimC 책임).
- 검증된 예산 **G2850 + J92 + F165 + O0 = B=T3107**. 선택 마부 둘 모두 정적 E0임. `L/E/O` 중복 가산 없음.
- 실제 사용자 브라우저에서 **Start → DPS Native2 → Cancel → HTTP 서버 재시작·같은 세션 복원 → Resume → 누적 Native4 → 재취소**, 진행 상태 `PAUSED_USER_CANCEL`, 이전 2회 작업 무효화/재시작 없음. 보고서 `status=PASS_REAL_CHROME_TWO_SIGNED_E0_START_CANCEL_RESTART_RESUME`, `new_native_calls=4`, `native_attempts_were_reused_without_reset=true`, `two_final_armor_enchants_exact_once=true`, `actual_browser_same_session_resumed=true`.
- 이번 **최종 후보 64회 / 결과 화면 DPS·SEM·95% 출력은 실행하지 않음**. 최종 단일 E0 Chrome 결과는 독립적인 과거 [v624 #44454908607](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44454908607)의 scope PASS이며, 이번 두 E0 실제 증거와 합쳐서 모든 다부위 결과 완료 또는 전역 최적해 증명으로 과장하지 않음.

## 2. 첫 실패도 보존 — 실제 등록 목록을 확인하지 않은 합성 ID 재사용

- 최초 [Actions #44462375530](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44462375530) **FAILURE**, 원본 [artifact #14500438727](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44462375530/artifacts/14500438727), 내부 JSON **1,479 bytes**·SHA `490678901a698875f78bcdd0d73badc58f0c7e42071a733e7d32366f0d9c2e89`. `first_blocker=V621_SIGNED_HEAD_7951_E0_NOT_IN_REAL_V212`.
- 원인: v625 **합성 테스트 fixture의 머리 7951**을 실제 70961 등록 마부 ID로 잘못 사용. 실제 원본 [v618 설치 artifact #14489588587](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44438148520/artifacts/14489588587)에는 **머리 7959(`enchant_helm__hex_of_leeching`) 및 가슴 7957**이 각각 최고 검증 품질 rank 2, 고정 E0·슬롯·정확한 SimC token 및 Policy A 영수증과 함께 등록. 첫 예시 7951은 이번 실제 설치의 등록 ID가 아니다.
- **첫 시험도 Native 이전 fail-closed 정상 동작**: 환경 구축 Native6 이후 등록 검사 차단, **DPS Native0**. 잘못된 ID를 보정 없이 허용하거나 E 미확정을 0으로 가정하지 않음. 두 번째 시험은 v618 원본 승인 목록에서 **7959**를 택한 뒤 한 번만 재시험. 첫/두 번째 실행은 별도 원본 및 세션이며 같은 설치 SHA로 과장하지 않음.
- **재발 방지:** 새 실환경 Native 시험의 영구마부 ID는 시험 fixture에서 발췌하지 않는다. 해당 시즌·빌드 실제 **v212 `published_verified_options`**의 `ui_selectable=true`, 슬롯·E·정확한 품질/원본에서 선정 후 사용. 일치하지 않으면 최소비용 차단, 코드가 자동 승인하지 않음.

## 3. 구현·비용 경계

- 기존 `v621` 브라우저 시험을 `run(...,multi_armor=False)` 기본 보존 + opt-in **`multi_armor=True`**로 확장. 새 wrapper `p2_v627_real_70961_two_armor_E0_cancel_resume_once.py`; 원래 v570/v344 Selenium 선택·v293 장기 세션·v291 64 상한·v212 서명·v096 프로필 검증 재사용.
- 새 CI `.github/workflows/p2_v627_real_70961_two_armor_E0_cancel_resume_once.yml`는 Native 0 syntax-only 선행, 실제 Windows job은 **명시적 one-shot** `[v627-real-two-E0-once]` 커밋에서만 실행. v621/v624의 기존 기본 실행 결과를 교체하지 않음.
- v627 최초 실패 실환경 Native 비용: **환경6 + DPS0**, 재시험 PASS: **환경6 + DPS4**. 총 새 환경 Native12 + 새 DPS Native4, 재컴파일0, 신규 알고리즘0, 26전문화 전수0, **동일 64후보 반복0**. 실패한 환경 재구축은 이력이 남는 **불필요 비용**이므로 다음은 실제 원본 선택으로 방지.
- v626의 14개 슬롯 입력은 제품 **설계 범위**. 실제 70961 현재 등록 19개의 E0는 머리·어깨·가슴·발 중심이며, 다른 슬롯의 미승인 마부 또는 E>0를 자동 승인한 것이 아님.
- **P2 다음 우선순위**: 양수 E에서 `E_total=Σ E_slot`의 원본 G 소유권·스탯별 고정 하한·수동 T 우선·SimC 프로필/캐시를 하나로 연결. 현재 `v212.preview_installed_selected_enchant_budget`는 **한 부위 E만** 계산하고 `v531`은 과거 특정 70783 단일 프로필 pilot. 각 부위 E를 원본 B에 반복 더해서는 안 됨. 실제 70961 `published_verified_options` 등록·물리 슬롯·G 제외 여부가 확인된 양수 E만 자동 등록할 것; 원본이 부족한 항목만 보류.
- 공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`은 임의 변경 없음. 격리 브랜치 원칙·main/v003 immutable/Project UI·Work OS·기존 주 제품 개발 채팅 권한 불변.
