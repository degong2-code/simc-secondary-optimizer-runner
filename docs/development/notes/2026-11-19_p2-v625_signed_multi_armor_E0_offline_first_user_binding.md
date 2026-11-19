# P2 v625 — 승인된 E0 방어구 마부 2~4부위의 실제 사용자 입력 연결 (오프라인 PASS)

2026-11-19 · 격리 브랜치 `probe/chat-cache-v035-20261024` · 최신 v624의 실제 70961 E0 한 부위 사용자 Chrome 64회 및 최종 결과 PASS를 재사용. 사용자 `진행` 지시에 따라 P2의 **첫 사용자 입력 단절**만 최소 수정.

## 1. 제품 목적·첫 실제 단절

- 미래 목표 ilvl/수동 T에서 26 DPS 전문화의 **절대 CHMV rating**을 기존 SimC DPS로 최대화. 사용자에게 현재 전체 장비를 입력시키거나 마부 효과/proc/APL을 독립 인증하지 않음.
- v618 실제 70961 설치 자동 등록 **19개는 E=0이며, 정확한 설치 SHA·부위·최고 품질·SimC 토큰·CHMV 영수증이 있는 항목**. 검증되지 않은 양수 E와 마부 효과 메커니즘은 사용자 선택지로 임의 승격 불가.
- v620~v624는 승인된 단일 가슴 E0 사용→Chrome 실제 SimC64 결과까지 PASS. 그런데 사용자는 머리·어깨·가슴·발 마부를 **동시에** 착용하지만 UI `synchronizeInstalledEnchantChoice`, `buildRequest`, v106/v098/v096이 한 부위만 허용해 해당 제품 사용자 입력을 막고 있었음.
- **최소 범위:** v212 등록·실제 최종 물리 부위와 E0가 일치하는 **머리/어깨/가슴/발 2~4개의 조합**만 허용. 한 부위 선택·반지/역사 양수 E 파일럿은 기존 경로 유지. 반지와 방어구 혼합, 미등록 ID, 양수/미확정 E, 무기 마부는 추가 승인 없이 여전히 불허.

## 2. 구현 — 내부 회계/SimC 엔진 불변

1. `v106.user_scenario`: 2~4개 부위별 입력을 typed syntax로 받아 기존 사용자/session identity에 포함. 이는 원본 등록 승인이 아니므로 `v098/v096` 자체 재검증 보존.
2. `v098._final_user_enchant_source_mask`: 원래 v216 정확한 최종 대표 ItemID/slot/mask source 소비자를 **각 부위에 별도 재사용**, 일부 한 부위라도 부적합하면 전체 차단. `_selected_installed_E0_multi_on_final_user_items`는 원래 `v212.preview_installed_selected_enchant_budget`에 각 선택을 전달하고 static E0/정확한 owner SHA/중복 ID 거부 후 각 최종 아이템의 `options.enchant_id`를 1회 기록. 순서 정규화/봉인 identity를 통째로 v096에 전달.
3. `v096._admitted_fresh_season_source`: 원래 실 `v217/v212` 봉인 및 `_signed_installed_user_E0_profile`을 **부위별로 다시 사용**하고, 프로필의 각 `id` 및 `enchant_id` 1회, E0·총 B/T·O 불변을 검증. 새 선택 묶음 SHA를 세션 DPS identity에 반영. 기존 v094/v291 적응형 엔진/95%/Native runner는 변경 없음.
4. `webui/app.js`: 직접 노출된 4개 부위 선택창이 서로의 선택을 지우지 않고 복수 선택 가능. 기존 `season_enchant_other`는 **단일 장비 선택시에만** 미러링. 새 요청은 이미 검증된 설치 E0 set 및 실제 옵션을 각 부위마다 재확인. 저장된 다부위 세션의 각 물리 슬롯을 복구하며 미검증 과거 선택은 실행 승인으로 사용하지 않음.
5. 예산: **모두 E=0**이므로 유효 `B=G+J+F` 및 `T=B+O`, `L/E/O` 정적 중복 가산 없음. 영구 마부 주문 발동·기타 효과는 SimC가 계산.

## 3. 신·구 검증과 비용

- 단일 선택/부위별 정확한 SHA 적용 + 기존 70961 실제 Chrome 64회 결과 **v624 과거 영수증 재사용**, 이번 신규 실 Native **0**.
- 신규 focused synthetic/offline 시험: `tests/test_v106_user_session_controller.py`의 다부위 typed·혼합/타입/부위 차단; `tests/test_v098_target_user_scenario_bootstrap.py`의 **최종 두 부위 각각 다른 실물 item·source mask·E0 영수증** 및 불일치 차단; `tests/test_v096_unified_product_entry.py`의 **두 마부 SimC 입력 정확 1회씩/동일 B=T3107/서명된 캐시 identity**와 오염된 profile 거부; `tests/test_v114_local_web_ui_offline.py`의 **실제 JS 2부위 요청/미승인 ID 차단/과거 v600 단일·v620 UI 재검증**.
- [v113 Web/API Ubuntu+Windows #44457447332](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44457447332) **SUCCESS**; [v182 UI Ubuntu+Windows #44457419158](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44457419158) **각 206 UI PASS**; [v098 #44457496060](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44457496060) **512 PASS**; [focused v096 포함 #44457496052](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44457496052) **684 PASS / SKIP2**; [78 계약 #44457496069](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44457496069) SUCCESS.
- 중간 [v113 #44457116762](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44457116762)은 **구 단일 마부 테스트가 이전 JS 구간을 함수로 잘라 SyntaxError + 이전 선택 덮어쓰기 가정을 검증한 2 FAIL**. 기존 단일 동작을 유지하도록 테스트 경계 업데이트 후 [최종 #44457447332](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44457447332) PASS. 제품 효과나 DPS Native 실패로 해석하지 않음.
- 현재 신규 Native 0 / 새 시즌 HTTP·DB2 수집 0 / 새 SimC 컴파일 0 / 기존 정적·DPS 캐시 무효화 0. 새 solver·새 schema·런타임 AI·독립 효과 인증 Gate 0.

## 4. 검증 경계·다음 STOP/REUSE 판단

- 이번 PASS는 **합성 봉인 데이터에서의 제품 UI→v106→v098→v096 다부위 E0 사용자 입력 경계의 각각의 원본 경로 오프라인 검증**이다. **실제 70961 사용자가 두 부위를 동시에 고른 Native SimC DPS/SEM/95% 새 실측은 아니다.** 기존 v624 한 부위 실제 64회 성공을 다부위 실제 PASS라고 과장하지 않음.
- 다음 비용 대비 경계: 새 다부위 프로필이 실제 동일 빌드에서 **정확 두 개의 마부 SimC 입력을 수용**하는지, 기존 v621 실제 Chrome 선택·취소·재개 도구를 재사용해 **단일 최소 Native 시나리오**로 확인하는 것이 유효. 이미 완료된 v624 E0 한 부위 64회는 재실행 금지; 26전문화 전수 금지. 신규 Native 필요시 한 번의 상한·실제 installed SHA·빌드 drift 차단.
- **양수 E**는 현재 38 계열 물리 품질 원본과 30 정적 E 증거를 19 등록 E0처럼 혼동하지 말고, 실제 고정 E의 **미확정 G 소유권 + 최종 물리 부위 + 등록**이 증명되는 항목만 다음에 처리. 입증되지 않은 E는 0으로 취급하지 않고 선택지만 보류.
- 공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` 변경 없음. `main` 병합, v003 immutable, 원본 v016 직접 통합, Project UI/Work OS M0·Shared State 승격, 기존 주 제품 개발 채팅 소유권 이전 없음.
