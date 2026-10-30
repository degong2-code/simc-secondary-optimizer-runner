# v202 — 실측 마법부여 E를 기존 적응형 탐색의 후보 하한에 연결 (2026-10-30)

## 목적 / 채택한 최소 구현
- 현재 시즌의 **미래 절대 CHMV rating 최적화**와 기존 v094/SimC DPS·SEM·95% 판정·취소/재개/캐시 유지. 새 탐색 알고리즘 없음.
- 이전 Native 근거: [v199](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41075851509)에서 일반 대표 냉법334 반지1 `item_id=158366`의 `enchant_id=8025`가 **가속 +30**을 `buffed_stats`에 실제 제공함. [v200](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41076597270)에서 같은 JSON2 두 개의 SHA를 재사용해 0 신규 Native로 교정 검증.
- 실제 `gear_*` 후속 근거: [v201](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41078102843)은 같은 프로필 전/후의 `gear_crit/haste/mastery/versatility=700`을 명시한 **2 Native PASS**, `buffed_stats` 가속은 양쪽 735, **차이 0**. 즉 **gear_*가 enchant의 자연 정적 rating을 대체한다**. 마부 +30을 gear_*에 별도로 가산하면 T 중복 위험.
- 구현: `runner/v065_v015_scheduler_adapter.py::budget_with_fixed_components`에 선택적 `fixed_enchant_E` 인자 추가. 기본 4인자는 기존 로직·반환값 그대로. 증거가 있는 옵션에서만 `B`의 per-stat 하한을 `max(기존, L+E+max(0,F-O))`로 높이고 **총 B/T, gear_* 주입, DPS 함수, SimC의 효과 처리는 변경하지 않는다**.
- `data/v202_verified_enchant_8025_source.json`과 `runner/v202_one_enchant_admission.py`는 적용 범위를 **mage/frost / ilvl334 / finger1 item158366 / enchant_id8025 / 정확 Linux SimC SHA f105b8a3… / rev710c240**으로 좁힌 개발용 선택이다. v098 내부 대표 장비 구성 → v096 프로필/manifest·SHA → v093 seed/scout/confirm 공통 후보 하한·세션 identity → v094 기존 실행 경로를 그대로 사용한다. 선택한 프로필은 새 SHA/Native 캐시 case_key로 분리. **일반 v106/웹 사용자 입력에는 이 검증 한정 선택을 허용하지 않는다.**
- [v202 CI #41078917430](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41078917430) **Ubuntu/Windows 양쪽 오프라인 E 회계 6 PASS**, [실제 Source First 334 plan CI #41079877720](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41079877720) **SUCCESS / 신규 Native=0**, `B=3150`, 기존 가속 하한 0 → E 적용 가속 하한 30, 기존과 동일한 raw gear target, 다른 source input SHA와 case_key/session digest 확인. 기존 26전문화 전수 SimC Native 재실행 없음.
- v196 시즌 카탈로그에서는 해당 단일 조건의 가속 +30을 **read-only** 관측값으로만 표시. 신규 마부 38종 전체를 Native 인정하거나 최종 사용자 선택 UI로 승격하지 않음.

## 아직 하지 않은 작업
- 동일 마부의 Windows 바이너리·다른 아이템레벨·다른 전문화 적용 범위 검증/자동 승인.
- 영약/보석/기타 37개 마부/일반 소비재 효과/품질 확장.
- 검증된 대표 조건의 선택을 실제 Windows 일반 사용자 UI에 노출하고 6 Native 결과/세션·캐시 전 구간 실측.
- 임시 공개 중인 GitHub 저장소를 자동 비공개 변경하는 행위(별도 알림만 등록됨).

## 효율과 안전
일반 사용자 입력→기존 26 전문화/기본 CHMV 경로·캐시 **완전 보존**. 추가 정적 게이트/상시 업데이트/SimC 독립 proc 모델/전수 Native 반복 없음. 신규 Native 총 **v201 두 회** (v199는 이전 이력 두 회), v202 개발 중 신규 Native **0회**. v202는 새로운 실사용 기능의 부분 구현이지 제품 전체 완료가 아니다.
