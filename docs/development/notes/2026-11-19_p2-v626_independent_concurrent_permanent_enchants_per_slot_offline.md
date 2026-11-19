# P2 v626 — 모든 영구 마부는 서로 다른 장착 부위에서 동시 선택 (부위당 하나), 검증 범위 구별

2026-11-19 · 사용자 최신 직접 결정: **“모든 마부는 동시 선택 가능해야해.(당연히 한 부위에는 하나만 골라야 하지만)”**. 격리 브랜치 `probe/chat-cache-v035-20261024`. v625의 머리·어깨·가슴·장화 2–4부위만 허용, 반지/방어구 혼용 불허, 같은 마부 ID를 양쪽 반지에 중복 지정 불허는 **최종 제품 정책으로 폐기**. v625 코드와 실증은 과거 단기 범위 증거만 유지.

## 1. 정확한 사용자 제품 설계와 증거 구별

- 최종 사용자에게 제공할 영구 마부 입력은 **실제 적용 가능한 각 물리 부위마다 정확히 0 또는 1개 선택**이다. 서로 다른 부위의 동시 사용을 임의 개수·부위 그룹·마부 ID 전역 중복 금지로 차단하지 않는다. 현재 표준 대표 장비 프로필의 대상은 머리/목/어깨/등/가슴/손목/손/허리/다리/발, 반지 1·2, 주무기·보조무기 등 14개 실제 슬롯(장착 구조에 따라 보조무기 유무 별도 판단). 같은 ID라도 각 슬롯별 적용 조건이 만족되면 양쪽 반지나 양 무기 손 등에서 재사용 가능.
- 한 **무기 손**에 일반 영구 마부와 DK 룬벼리기 등 다른 영구 강화가 중복 적용되면 안 된다. 무기 기름은 **별도 O 선택·회계**이고 일반 임시 마부는 범위 밖.
- **슬롯 입력 문법/표시 가능 ≠ 실제 새 시즌 승인**: 정확한 최고 품질·기록된 시즌·설치 SHA, 각 최종 대표 물리 ItemID/무기 손·서브클래스 마스크, 동일 빌드 SimC 입력, 원본 소유권 및 정적 E 고정치는 v216/v212/v098/v096의 기존 근거로 각 부위별 독립 확인해야 한다. 미검증 마부를 E0로 추정하거나 승인 등록하지 않는다.
- 양수 E를 포함한 모든 **검증된** 영구 마부 동시 선택이 **최종 제품 요구**다. 그러나 이번 코드에서 실제 새 세션 실행까지 확장한 범위는 기존 서명 **E0 19개 등록**의 부위별 적용이다. 38개 품질 원본, 30개 정적 E 증거, 19개 등록을 동일 READY로 과장하지 않으며 **양수 E의 합계 고정치·G 참조 소유권/수동 T/스탯별 하한**이 부위별로 검증돼 연결되기 전에는 그 옵션만 보류한다. 과거 exact E+ 단일 프로필 사례는 그 유효 범위의 이력이며 범용 다부위 승인 아님.

## 2. 최소 코드 연결

- `v106.user_scenario`: 입력을 각 허용 물리 슬롯→enchant_id 맵으로 취급. 임의 최대 4/방어구 그룹 제한 제거. 트링킷은 자유 G 밖으로 여전히 일반 영구 마부 입력 대상에서 제외.
- `v098._final_user_enchant_source_mask`: 기존 v216의 **각 최종 실제 부위/ItemID/마스크** 비교를 슬롯마다 반복 사용; 한 부위라도 불일치하면 전체 실행 차단. 기존 v212 E0와 최종 `options.enchant_id` 정확 1회 기록. 같은 enchant_id를 다른 슬롯에 쓰는 것 자체는 차단하지 않음.
- `v096._signed_installed_user_E0_profile`: 각 장비 라인의 해당 ItemID와 `enchant_id`를 **정확 1회씩** 확인. 프로필 전체에서 같은 마부 ID 등장 횟수는 실제 **선택한 물리 슬롯 수**와 정확히 일치해야 함. 서명된 설치·CHMV 소유권·전체 선택 identity/캐시 분리 및 기존 적응형 v094/v291 유지.
- `v212.preview_installed_selected_enchant_budget`: 기존 원본의 `WEAPON_SUBCLASS_NOT_YET_USER_SLOT_CERTIFIED` 계열은 주무기·보조무기 후보 손으로만 매핑하되, v216의 실제 물리 아이템/손 검증 완료 전 승인하지 않는다.
- 웹: 10개 일반 방어구 + 양쪽 반지 + 주/보조무기 슬롯별 UI. 독립 드롭다운 선택이 다른 부위의 선택을 지우지 않는다. 구형 `season_enchant_other`는 숨긴 **단일 기존 세션 호환 미러**로 보존하고 같은 부위에 마부 둘을 합치거나 중복 전송하지 않음. 미승인 ID/다른 부위/같은 무기의 룬벼리기 충돌 차단. 저장 세션 복원은 별도 UI 승인 근거가 아님.
- SimC 효과/발동/APL/DPS, 시즌 G/J/F/O·L/E/O, 통계 95%, 캐시·취소·재개, 적응형 엔진은 **재구현하거나 변경하지 않음**.

## 3. 신규 테스트·기존 영수증/비용

- 변경 코드 본체 `f1d8ae020a73bdb7b82e9e77ba019c1355b9e146`, 과거 한 부위 제한 가정과 사전 차단 위치에 맞춘 회귀 수정 `4d149d2e751187f199b678a8381926c8dc1bc506`, null-safe exact 사용자 ID 검사에 맞춘 회귀 수정 `bc43d6156dc5f3267695dcb0de30f3f6c32648e4`.
- [v182 UI Windows/Ubuntu #44461284221](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44461284221): 두 플랫폼 **SUCCESS** · 각 206 UI 테스트 PASS(별도 원본/장착 회귀 포함). [v113 API Windows/Ubuntu #44461284758](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44461284758): 두 플랫폼 **SUCCESS**, 각 **498 PASS / 1 SKIP**. [focused #44461284199](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44461284199) **685 PASS / 2 SKIP**. [v180 offline #44461284215](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44461284215) **SUCCESS / native-six-cases SKIP**. [공식 78 #44461284201](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44461284201) SUCCESS. 기타 v098/Windows 사전검사 SUCCESS.
- 첫 `f1d8ae0` push에서 일부 **이전 단일/무기 금지/정확한 에러 종류/고정 186 UI ID**를 전제로 한 회귀가 FAIL. 이는 기존 테스트가 직접 사용자 승인 설계 변경을 예상하지 않았던 것으로, 현재 테스트에서도 미승인/잘못된 슬롯/동일 손 영구 강화 중복 차단을 검증하며 수정. 이후 위 최종 CI PASS. 실 SimC 메커니즘·DPS 실패와 혼동 금지.
- 신규 실제 SimC Native **0회**, 시즌 게임 HTTP·DB2 수집 0회, SimC 재컴파일 0회, 기존 정적/DPS 캐시 무효화 0회. 기존 [v624 실제 70961 한 부위 E0 Chrome 64→결과 복원 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44454908607)는 보존. **이번 v626은 합성/소스 검증 오프라인 UI→대표 프로필 경계 PASS이지, 여러 마부의 실제 70961 Native DPS 새 결과가 아님.**

## 4. 다음 P2 및 STOP 원칙

1. 사용자가 실제 70961 설치 E0 두 부위(반지 양쪽 또는 기존 승인 방어구)를 Chrome에서 동시에 고르는 사례의 최종 프로필·서명 설치·동일 세션 취소/재개를 **이전 v621/v624 브라우저 도구 재사용**으로 bounded 1회 확인; 사용자 결과 64후보 전부 다시 돌리지 않는다. 실증 필요성·한도 지정 후 최소 Native.
2. 등록·G 소유권·정확한 부위/손이 증명된 **양수 E**의 복수 합산: `E_total = ΣE_slot`(정확히 한 번), 자동일 때 원본 G가 해당 E를 제외하면 해당 증가량만 한 번 B/T에 반영, 사용자 수동 최종 T는 최우선, E_total/L/J/F 및 스탯별 하한을 확인. 추측/프로시저적 효과 Gate를 추가하지 말고 SimC에 효과/APL/DPS 위임.
3. 미확정 선택지만 보류하며 verified E0 기본 제품 및 이전 캐시는 차단하지 않는다. 새로운 solver/전체 장비 DB/전 전문화 Native 전수/동일 64-case 반복 금지.

공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` **불변**. 격리 브랜치만 수정, `main` 병합·v003 immutable·원본 v016 직접 통합 완료 주장·Project UI Sources/Instructions 적용 주장·Work OS M0/Shared State 공식 승격·기존 주 제품 개발 채팅 소유권 이동 없음.
