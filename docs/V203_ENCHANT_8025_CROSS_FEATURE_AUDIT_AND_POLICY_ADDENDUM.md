# v203 마부 정적 rating 8025 — 기능 간 호환성 감사 및 개발 정책 보충

**감사 시점:** 2026-10-31 KST · **권한 범위:** `probe/chat-cache-v035-20261024` 격리 개발 브랜치 · `main`/v003 immutable·공식 Project Sources UI 불변.

## 우선 적용하는 기존 승인 설계

사용자 전달 **Developer Notes v1.4.1**의 §5 `T=G+J+F+O=B+O`, §7.3 “마부의 고정 스탯은 자유 CHMV 예산에 넣지 않음”, §11 SimC DPS·SEM·95% 통계, §13 캐시와 취소/재개가 상위 정책이다. v202/v203의 기술 회계에서 **`E`는 독립적으로 총량을 증가시키는 다섯 번째 예산 항목이 아니다.** 검증된 마부가 차지한 스탯을 *이미 있는 목표 `G` 안*의 **비자유분배 슬롯별 하한**으로 보호하는 보조 표기다. `T`나 자유 분배 `B`, `gear_*` 숫자에 `E`를 추가 가산하지 않는다. 기존 `F,J,O,L`의 소유권도 변경하지 않는다.

## 증거와 강제 경계

- 실제 SimC `710c2408bf` + Linux 바이너리 SHA `f105b8a34fd911c340e735f0440e0d1eadf0d0dbc25f18923c048810cf69095d`; 대표 냉법334, `finger1`, 아이템 `158366`, 마부 `8025`에 한정.
- [v199 원본 Native 2회](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41075851509) + [v200 원본 SHA 재분석 0회](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41076597270): 자연 장비의 `buffed_stats` 가속 **1004→1034**, 마부 고정 E=가속30. JSON2 슬롯 `gear.finger1.haste_rating`에서 차이가 0인 것은 마부 부재의 증거가 아니다. v198 초기 E=0 판독은 역사적 오판으로 보존.
- [v201 실제 Native 추가 2회](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41078102843): 동일 장비·마부 적용 전후에 `gear_* = 700`을 지정하면 `buffed_stats` 가속이 양쪽 모두 735; **마부로 인한 차이 0**. 따라서 마부 E30을 `gear_haste_rating`에 다시 더하는 것은 중복.
- [v203 전체 적응형 6 Native PASS + cache-only 6/6 HIT](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41083301873): 동일 대표 조건에서 B=3150, T=3182, 4개 고유 관측 후보, 95% 분석 및 전역 최적 미입증 표시. 동일 세션의 JSON2 SHA 6개는 캐시 전후 불변. 테스트 전용 개발 세션으로 기존 실사용 캐시를 덮어쓰지 않음.
- v203 Native에서 실제 완료된 **source profile SHA `8305a811137db6f557f8076dfa44a4a1a359111d60bb7452225e1573bf72a401`**를 v202 승인 경로에 추가 고정. 이제 **동일 전문화/ilvl이라는 이유만으로 달라진 종족·특성·장신구·장식·보석·소모품·전투조건·유효 장비에 E30을 재사용하지 않는다.** 정확한 전체 프로필 및 바이너리 SHA가 둘 다 맞아야 함. 신규 user loadout에는 별도 정확성 확인 또는 새 관측이 필요하며 E=30 일반화 금지.

## 전체 경로의 충돌 예방 규칙

| 기능 | 불변/검사 규칙 | 실제 근거 |
|---|---|---|
| 미래 파밍 총량 | `T=G+J+F+O`, `B=T-O` 보존, `E`를 `T`에 추가하지 않음 | v202/v203 회계 회귀 |
| 고정 특수 `L`·제작장식 | 동일 `finger1`이 선택 `L` 또는 제작장식에 중복 등록되면 **대표 장비 구성 이전 차단**. `L+E` 겹침 방지 | v203 조기 충돌 검사 |
| 후보 탐색 | `E=30`은 기존 v065 floor에만 추가. seed/scout/material/confirm 모두 동일 bound 사용; 기존 최적화 로직 그대로 | v203 실제 6 Native |
| SimC 효과/정적 통계 | 마부 ID는 실제 item row에 전달. `gear_*`에 E 추가 가산 금지; 실제 발동 효과·DPS는 SimC | v199·v201 |
| 식별/캐시/재개 | 마부 유무에 따라 source/profile SHA, case_key, session digest 변경. 동일 세션은 Native JSON2 6개 SHA 검증 후 캐시 재사용 | v202 오프라인 + v203 6/6 |
| 사용자 v106 / API | 내부 `verified_enchant` 필드는 **일반 사용자 입력에서 차단**. Windows 바이너리·타 전문화·타 ilvl에 자동 적용 안 함 | v203 경계 단위시험 |
| 시즌 카탈로그 / UI | 38개 마부 후보 **전부 read-only**, 실제 조건의 E30은 출처 표시에만 이용. E 증거 파일 손상/누락으로 기존 시즌 카탈로그/음식·물약·영약 등의 기능 전체가 사라지지 않음 | v203 fallback·API 검사 |
| Native 증거 무결성 | v200/v201 4개 원본 JSON2 SHA와 artifact ID를 **정확한 값으로 고정**. 임의 64자리 SHA는 증거 불인정; 증거 검증 실패 시 item option 원본을 수정하지 않음 | v203 무결성·원자적 처리 |
| Windows 패키징 | source-only / SimC·사용자 프로필·DPS 캐시 미포함 유지, Windows Python 3.12/3.14 실제 HTTP 테스트 | 기존 v181 및 v203 호환성 감사 |

**2026-10-31 검증:** [v203 Ubuntu·Windows 호환성 감사 #41084413183](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41084413183) — 두 OS 각각 단위검사 **21 PASS + 패키징 2 PASS**, Linux 전체 source SHA 개발용 재현 1 PASS, 신규 Native 0. [v203 전체 Native #41083301873](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41083301873) — 6 PASS/6 캐시 HIT, 신규 Native 정확히 6. 실측 범위를 넘어서는 완전한 조합공간 증거는 아님.

## 남은 비검증/미승격 범위

1. **Windows 사용자 SimC `710c240`**에 이 마부를 선택하는 정식 UI는 아직 없음. Linux 한정 개발용 증거를 Windows 정적 rating 검증으로 오인하지 않는다.
2. 다른 반지(특히 `finger2`), 장신구/특수효과 장비 교체, 제작/티어와 중복 부위, 타 스탯 마부, 영약·기름 개수·선택 보석/소모품·종족/특성/전투 설정 변경 조합의 **새 E30 재사용 승인 없음**. 기존 일반 입력에서 마부 선택 자체가 비활성인 것은 의도한 안전 경계.
3. 취소·부분 세션 재개의 **기존 프로그램 회귀**는 보존하지만, v203은 신규 6회 완료 후 cache-only 재실행만 실제 관측했다. 중간 강제 종료를 이용한 **마부 조건 고유의 부분 재개 Native**까지 재실행했다고 주장하지 않는다.
4. **최신 사용자 직접 승인 범위는 DPS 26개 전문화(증강 기원사·탱커·힐러 제외)**다. 이 문서의 초기 작성 시 인용한 v1.4.1의 27개·증강 포함은 2026-10-29~30 사용자 직접 변경보다 오래된 역사 규정이며, v1.4.2 보충본과 실제 26전문화 구현을 우선한다. 26/26 기본 물리 시험을 모든 부가 선택 조합의 DPS 완료로 과장하지 않는다.
5. 기존 v015/v016 원본 직접 통합·전역 최적 증명은 계속 미완료. 95%는 선택한 두 후보의 통계적 비교만 의미함.

## 개발 지속 규칙

변경 시 Native 신규 호출 수, 반복/케이스 캐시 충돌, 기름 O 및 마부 E 이중 계산, 정확한 item options/SimC SHA, 메모리·I/O, 전체 사용자 계약 호환성을 비례 확인한다. 성립한 SHA 동일 범위 결과는 재사용하며 전체 26전문화 전수 Native·새 효과/발동 독립 Gate·새 최적화 엔진·상시 감시 기능을 만들지 않는다.

**승격/권한:** 이 문서는 사용자의 이번 요청으로 작성하는 **격리 개발 지침 보충자료**이며, v1.4.1 승인 설계 원문 및 Project UI Sources 등록을 수정한 것으로 주장하지 않는다. 공식 Project Sources 교체/MAIN 병합/Work OS 상태 승격은 별도 실제 실행·검증이 필요하다.
