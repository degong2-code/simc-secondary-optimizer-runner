# P2 v628 — 제품 런타임의 AI 비개입·엔진 기능 효율·중복 v212 파일 읽기 감사

2026-11-19 KST · 사용자 직접 요청: **“효율적으로 진행할 것. 또한 엔진 기능 개발, AI개입 없는지도 점검.”** 격리 브랜치 `probe/chat-cache-v035-20261024`. 기존 v624의 한 부위 70961 64회 최종 사용자 결과 및 v627의 실제 E0 머리·가슴 동시 선택/실 DPS Native4·Cancel/Resume 증거 재사용.

## 1. 사용자 제품 소비 위치

- 사용자 흐름: **26 DPS 전문화·목표 ilvl/수동 최종 T → 시즌 G/J/F/O/B/T → 내부 대표 장비/4pc/SimC 프로필·장신구/검증된 영구 마부 → 기존 적응형 SimC/캐시/취소·재개 → 절대 CHMV rating·DPS·SEM·95%·근접 대안**.
- v627 실제 두 E0 마부 경계는 이미 PASS. 다만 `runner/v098_target_user_scenario_bootstrap.py`의 `_selected_installed_E0_multi_on_final_user_items`는 선택 슬롯마다 `_selected_installed_E0_on_final_user_item`을 호출하며, 이전에는 동일한 v212 JSON을 **부위 수만큼 다시 읽고 전체 설치 문서 봉인을 중복 검사**했다. 최종 사용자 rating·실 SimC 정확도에는 도움되지 않는 I/O. 최대 14슬롯 선택은 제품 UI 구조일 뿐 현재 실제 승인 E0 슬롯 수는 별도.
- **필요한 작업은 기존 검증 데이터의 세션 내 재사용뿐**. 신규 마부 효과/발동 인증, 독립 최적화 엔진, 새 SimC 후보, 전체 등록 38/30 전수 승격·Game DB 수집, Native 실험은 필요 없음.

## 2. v628 최소 코드 및 실제 검증

- 커밋 `7df3d786c21091c1c0d3adc54ff50f8dbb59bfb5`: `v098`에서 다부위 마부에 **설치된 v212 문서 1회 read/원본 확인 → 각 실제 물리 부위의 기존 `v212.preview_installed_selected_enchant_budget` 호출을 그대로 재사용**. 원래 v216 각 최종 ItemID·mask, v212 등록·서명·static E0, v096 SimC 프로필·cache identity는 변경하지 않음. 단일 마부/기존 세션 경로 그대로.
- 읽기 수(다부위 한 세션 기준): **N회 → 1회 (N=실제 선택 슬롯 수)**. 캐시 데이터 구조나 영구 글로벌 메모리 캐시는 추가하지 않음. 읽은 문서도 기존 v212 preview가 부위별로 다시 서명/소유권/장비/회계 검증하므로 fail-closed 보존.
- `tests/test_v098_target_user_scenario_bootstrap.py`의 실제 두 슬롯 원본 mask·기본 예산 회귀에 `read_json.call_count == 1` 추가. 두 부위 ID 각 1회·원래 B=T3107·부위 불일치 차단을 그대로 유지. 세션 리로드 시에는 새 원본 검사를 정상 수행하므로 원본 변경을 은폐하지 않음.
- 실 회귀 [v098 #44464806152](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44464806152) **514 PASS**, [focused #44464806168](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44464806168) **685 PASS·2 SKIP**, [Windows·Ubuntu UI #44464806153](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44464806153) 각 **206 PASS**, [Windows·Ubuntu API #44464806167](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44464806167) 각 **498 PASS·1 SKIP**, [계약 #44464806174](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44464806174) SUCCESS, [v180 #44464806183](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44464806183) offline SUCCESS/**native-six-cases SKIP**.
- **이번 신규 SimC Native 0, 재컴파일 0, 새 시즌 HTTP/DB2 0, 기존 정적/DPS 캐시 무효화 0**. 코드 한 묶음에도 여러 기존 offline Actions가 반응했음; 향후 변경을 실 사용자 결손 기준으로 모아 중복 CI fan-out을 줄일 여지가 있으나 **지금 새 workflow/Gate 개발은 제품 사용자 가치보다 비용이 커서 STOP**.

## 3. AI 개입 감사 — 실제 점검 범위와 경계

- **확인한 기본 실행 코드:** `runner/v113_local_web_api.py` (127.0.0.1 API), `v106_user_session_controller.py`, `v098_target_user_scenario_bootstrap.py`, `v096_unified_product_entry.py`, `v094_durable_inclusive_adaptive_runner.py`, `v291_durable_multiscale_native_runner.py`, `v293_local_longrun_session.py`, `runner/webui/app.js`. 설치 목록 `requirements-web.txt`에는 FastAPI/Uvicorn/httpx2가 있고 `requirements-web-test.txt`는 테스트용 httpx 추가. **검사한 기본 제품 실행 경로에서 OpenAI/ChatGPT/Gemini/Anthropic/LLM SDK, AI 모델 API 호출, 실시간 프롬프트 생성 의존성 발견하지 못함**. 외부 게임 빌드/Wago/SimC 다운로드와 로컬 HTTP는 AI 호출이 아님.
- `v291`은 기존 `v094/v065` SimC 실행·실제 DPS/SEM·캐시를 사용. 별도 `runner/v312_model_guided_multiregion_policy.py`는 **수학적 cubic response-surface 후보 순위 실험**(생성형 AI 서비스 아님). `v291.run`의 `model_guided_multiregion=False`가 기본이고 **명시적 opt-in 때만 실행**. 기본 제품에 이 실험을 새 필수 Gate로 승격하지 않음.
- **정확한 표현:** “점검한 기본 제품 실행 경로에 외부 생성형 AI 런타임 의존성 없음.” 이는 모든 과거 GitHub 실험/서드파티 코드의 전수 무결성을 증명한다는 주장은 아님. 개발자가 ChatGPT를 이용해 코드 리뷰·작성하는 행위와 최종 사용자 PC 제품에서 AI를 호출하는 것은 구분한다.

## 4. 양수 E의 첫 실제 단절과 제품 우선 STOP

- 현재 70961 자동 등록 **19개는 정적 E0**. 품질 출처 38계열/정적 E 증거 30/등록 E0 19는 상호 다른 검증 범주. 동일 v212 `published_verified_options`의 **실제 양수 E 등록·정확 물리 슬롯·G 회계 소유권**이 없는데 합산 엔진을 신설해도 일반 사용자는 소비하지 못함.
- `v212.preview_installed_selected_enchant_budget`는 **한 슬롯**의 E를 기존 `v222.retarget_verified_install`에 맞춰 정확히 한 번 추가하거나 수동 T를 유지하는 단일 증거. `v531_current_season_positive_E_bridge.py`는 특정 과거 70783 ID/캐릭터/프로필 원본이 고정된 단일 파일럿, 70961 전 부위 양수 E 런타임 승인 근거가 아님.
- **이 단계에서는 E+ 합산 새 엔진·가입력 없이 STOP**. 70961 같은 시즌·빌드에서 실제 등록 가능한 E>0가 생기면 우선 기존 v222 소유권/최종 T 수식 재사용. `E_total[k]=Σ E_slot[k]`를 부위별로 **한 번** 합산, 자동이면 G가 E 미포함인 검증된 값만 B/T에 반영, 수동 `B=T-O` 우선, `J/F/L/E_total` 및 스탯별 하한/배분 가능성, 부위별 `enchant_id` 1회, source SHA·캐시 정체성 확인. 미등록 옵션만 보류하고 E0 기본 사용자는 차단하지 않음.
- 기존 유효한 v624/v627 SimC Native PASS는 재실행하지 않음. 우선순위는 새로운 동시 선택 실제 등록 마부의 예산 소유권 증거 확보 후 **기존 경로 CONNECT/FIX**이며, 자체 효과/발동/APL 엔진이나 새 최적화 알고리즘은 범위 밖.

## 5. 공식 상태 및 권한

`15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` **그대로**. 이번 효율화는 전체 제품/전 26전문화 수락 완료가 아님. 격리 브랜치만 변경, main 병합·v003 immutable 변경·원본 v016 직접 통합·Project UI 적용/Work OS·Shared State 승격·기존 주 제품 개발 채팅 소유권 이전 없음.
