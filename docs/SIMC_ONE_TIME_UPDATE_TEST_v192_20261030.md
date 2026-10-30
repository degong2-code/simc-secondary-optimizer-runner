# v192 — SimC 한 번 업데이트를 이용한 통합 조사 엔진 실제 검증

**수행 기준**: 2026-10-30, 사용자 요청. 매 SimC 업데이트마다 재조사할 필요는 없다. 중간 패치·시즌·확장팩 변경을 기본 요청형 트리거로 유지하며, 이번 SimC 업데이트는 일회성 정합 테스트다.

## 이전 vs 최신 SimC / 데이터 일치

- 기존 최적화 증거 SimC `7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd` (2026-10-20), 생성 영구마부·임시마부·보석 `12.1.5.70448`.
- 공식 SimC Midnight 브랜치 확인 최신 커밋 `710c2408bfd3ae4df71b8cd55cdf01f63fd6c926` (2026-10-28).
- 이번 신규 생성된 세 자료의 내장 게임 빌드는 모두 **`12.1.5.70575`**, 기존 같은 시즌 Wago DB2 스냅샷의 빌드 `12.1.5.70575`와 정확 일치.
- `unique_gear_midnight.cpp`/ `consumable.cpp` 등록 소스 blob은 두 커밋에서 동일. 음식 효과 등록 37, 물약 전용 핸들러 5, 장식/다크문 20(비활성 1)을 **재수집 결과**로 보존. 숫자가 전체 아이템/효과 인증 수가 아님.

## 실제 영수증

- [`v192` 새 SimC 소스 + 게임 DB 카탈로그 Actions #41017578894](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41017578894): pinned 새 SimC 소스 `v189` + 재사용 기존 Wago `v161` 스냅샷으로 `v190` + `v191` 통합 **오프라인 12 PASS**, 최신 카탈로그 일치 검증 PASS, Native 0인 catalog 단계. [원본 후보 영수증](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41017578894/artifacts/12959844108).
- [`v191` 새 SimC 기준 후속 Actions #41018119033](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41018119033): 추가 `current_season_enchant_candidates()`로 **Midnight `enchant_...` 형식만 현재 시즌 후보**, 전문기술 도구 마부 제외, 실제 item class/inventory/subclass 비트마스크 보존, 동일 토큰·동일 적용 조건에서 최고 품질만 보존. **최신 시즌 장비 마부 38종** 후보, `v191` 오프라인 6 PASS + 실제 새 소스 통합 PASS. 이 38종은 영어 SimC 토큰/장착 조건·랭크 후보이며 한국어 이름·툴팁/실제 시즌 제작 레시피·정확한 정적 rating/SimC 수용까지 확인된 선택 옵션이라는 뜻이 아님. [영수증](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41018119033/artifacts/12960680728).
- 기존 511개 장비 DB/65개 티어 ID/192개 음식 DB 원시 아이템/61개 물약 DB 원시 아이템 및 등록 37/5/20은 신규 별도 전수 요청 없이 재사용. 동명의 저품질 마부와 실제 효과가 다른 마부는 구분. 효과의 수치 비교가 아직 불가능한 품목을 ‘약하다’고 추론해서 제거하지 않음.
- **v192 최신 SimC 바이너리 실제 Native PASS**: [Actions #41017578894](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41017578894) catalog/native 두 작업 모두 SUCCESS. 새 Linux CLI를 리비전 `710c2408bfd3ae4df71b8cd55cdf01f63fd6c926`에서 직접 빌드. 바이너리 SHA256 `f105b8a34fd911c340e735f0440e0d1eadf0d0dbc25f18923c048810cf69095d`. 냉법334 물리 SimC **신규 Native 1/1 PASS**, JSON2 실제 `git_revision=710c2408bf`, 주무기 `159137` **지능549**, 보조무기 `159667` **지능289**, 실제 티어 `271564/271562/271565/271563` 4부위 확인. 오일 없이 35 iterations 물리 수용만 실측했으며 새 버전의 6후보 DPS 최적화·95% 결과가 아님. [원본 JSON2/SimC/stdin/stdout/영수증 artifact #12960377241](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41017578894/artifacts/12960377241). 새 바이너리 캐시는 기존 `v035`와 별도 디렉터리·새 SHA로 분리, 과거 v185 냉법 188,520 DPS/SimC SEM과 직접 비교/삭제/대체하지 않음.
- **v191 최신 최고 품질 현재 시즌 마부 후보 최종**: [Actions #41018700283](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41018700283) SUCCESS, 오프라인 6/6 및 실제 pin 통합 PASS. [artifact #12961140046](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41018700283/artifacts/12961140046) 실제 JSON에 총 **38개·모두 현재 SimC 등급2**: 장화3, 가슴4, 머리6, 반지9, 어깨6, 무기10. 무기 마부는 `inventory_type_mask=0`에 따른 정확한 주/보조 무기 클래스/종류 매핑 후 UI 사용해야 하므로 여기서 부위 자동 선택 인증이 아님. 처음 [#41018575044](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41018575044) 실험 CI의 결과 출력 코드 `os` 누락 FAIL은 수정하여 #41018700283 PASS, 이전 실패 영수증 보존.
- 통합 `v191` 워크플로는 선택적 `workflow_dispatch`에서 정확 SimC 커밋과 기존 matching `v189/v190` artifact run/name을 받을 수 있도록 일반화; 주기·자동 업데이트 없음. 새 시즌이나 확장팩을 과거 현재 시즌 DB로 단순 재명명하는 시도는 명시 차단.

## 현재 통합 엔진의 현실적 경계

- **구현·검증**: v189/v190/v191 추출·조인·원본 해시/빌드 정합, 통합 후보 JSON 생성, 최고 rank/슬롯 구분, 기존 DB 재사용. 이번 커밋 업데이트로 빌드 정합 해소 확인.
- **미구현·미승격**: 모든 음식/물약/영약/증강룬/보석/장식의 실제 아이템 품질·스펠 연결 및 저품질 제거, 마부 38개에 실제 효과 설명과 koKR locale 연결, 유효 부위별 실제 사용자 UI 선택, 마부/보석/장식 선택이 기존 CHMV J/F/O/L에 미치는 영향과 정적 rating 정합, 제품 Windows 사용자 SimC 실행 바이너리 교체. 현재 UI v188은 그대로 유지. 선택 항목 중 확정된 것만 이후 변경·표적 검증한다.
- 새 시즌 데이터가 정말 달라진 것이 아닌 이상 `v161` CSV 전체 재수집·26전문화×6 Native 전수 반복은 하지 않는다. 관리 메인/원본 v003/Project UI 미변경, isolating branch만 사용.
