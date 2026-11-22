# 2026-11-22 P3 v665 — 실제 사용자 PC 스크린샷 기반 음식·마부·아이콘·장식 UX 5건

## 제품 목적과 실제 사용자 지적
26개 DPS 전문화에서 목표 ilvl 또는 사용자가 직접 입력한 T를 기반으로, 미래 CHMV 절대 rating과 실제 SimC DPS/SEM/95%/근접 대안을 찾는다. 사용자 PC는 `12.1.5.70961` G2850/J92/F165/O0/B=T3107 시즌 환경 설치까지 성공했으며 실제 최적화 DPS E2E는 아직 미실행이다. 사용자 화면의 음식/영약/물약 사용 기본, 불명확한 마부명/설명/낮은 같은 효과 선택지, 장신구·특수장비의 가짜 ◆ 아이콘, 장식의 부적절한 위치 5건을 접수.

## 구현된 변경과 한계
- **장식 위치**: `runner/webui/index.html`의 원래 `crafted-rows` DOM 블록을 고정 장비 패널에서 캐릭터 프로필 하단으로 재배치. 클래스만 `profile-embellishments` 추가, 반응형 스타일 `runner/webui/styles.css`. 장식 최대 2개·종류/부위/스탯/ItemID·중복검증·세션·SimC 입력 ID 전부 유지. 고정 장비는 장신구 2개+선택 특수효과 장비만.
- **마부명·기술 문구**: 기존 서버가 v212 인증 설치에서 전달하는 원래 `simc_token`, static E와 원본 분류를 이용해 화면 기본 선택지 이름을 먼저 표시한다. 공식 검증 한국어 명칭이 없으면 token을 가독성 있는 영어 이름으로 변환하되 그것이 공식 명칭이라고 주장하지 않는다. 정적 E가 양수면 `특화 +29`처럼 짧게 노출하며 `마부 #ID`, `실행 시 실제 아이템/SimC 재확인`, `정적 E=0 검증` 등 개발용 텍스트는 일반 기본 선택지에서 제거. 원래 검증된 ID·E·최종 프로필 확인은 기존 서버 계약에 그대로 남긴다. E0는 효과 없음이 아니므로 비 CHMV 마부는 이름/효과별로 유지.
- **같은 효과의 강한 반지 마부**: 정확한 `70961` v212 서명 설치본에 등록된 특정 같은 반지 슬롯·원본 token·효과 계열이 `v197.RING_EFFECTS`로 일치하고, 서로 다른 정확한 Native 정적 E가 각각 확인된 경우에만 일반 사용자 목록에서 작은 rating을 숨긴다. `7965/7969` 특화 +24/+29, `7995/7997` 치명 +24/+29, `8021/8025` 가속 +24/+29, `8023/8027` 유연 +24/+29. 모든 마부는 이미 원래 원본 품질 2로 등록된 서로 다른 이름·ID; 이것은 '낮은 품질'을 임의로 판단한 것이 아니라 **같은 정적 rating 효과의 강한 선택지만 기본 노출**하는 UI projection이다. 원래 v212 등록·캐시·저장된 과거 session/ID는 수정하거나 삭제하지 않는다. 새로운 시즌의 계열 증거가 없으면 추측으로 숨기지 않는다. 치명 효과 강화(독수리의 눈) 등 다른 효과는 별도 유지. 특정 실측 캐릭터만 허용된 역사 선택지는 원래 exact scope 보호.
- **장신구·특수효과 장비의 실제 아이콘**: 기존 동일 시즌 v212 인증 `installed_manifest_sha256`로 조회한 후보 ItemID(전체 시즌 DB 확장 아님)만 `GET /api/v1/season-item-icons` read-only endpoint에서 조회. 사용자가 이미 Windows 보안 저장소에 저장한 Blizzard API 자격증명만 서버에서 사용하고 OAuth/비밀키는 UI·영수증·캐시에 노출하지 않는다. `runner/v665_official_item_icons.py`에서 승인된 `kr.api.blizzard.com/data/wow/media/item/{id}?namespace=static-kr` 및 `render.worldofwarcraft.com` HTTPS 아이콘 URL·응답 item ID·크기·건수(최대 80, worker4)를 검증. 본문/대화 중 사용자 키 입력 요구 안 함. `runner/webui/app.js`의 기본 바로 선택 카드와 이전 상세 카드 모두 공식 아이콘 URL이 확인된 경우에만 image, 실패·미확인에는 중립 ◆ 표시. LocalJobs scope별 메모리 캐시, CSP는 공식 이미지 CDN만 허용. 추가 Native0, 새 게임 정적 DB 수집0. **실제 개인 PC의 Blizzard media 응답/이미지 렌더는 미확인**이며 live 실패 시 기본 장비 선택은 유지.
- **기본 영약 F 표시 보강**: 정확한 같은 v212 설치본에 `verified_base_flask_installs`가 연결된 경우에만 빈 placeholder를 `기본 검증 영약 사용 (현재 시즌 설치본 F)`로 표시하고, 그렇지 않으면 검증 대기로 표시. 실제 F 선택·예산·프로필 저장은 기존 서버가 결정, 대체 flask를 임의 최적화하지 않음.

## 의도적으로 미구현: 요청 1의 음식/물약 기본 사용·영약별 DPS 자동 선택
- **현재 실제 실행 계약:** `runner/v218_v098_profile_stage_adapter.py::current_season_approved_optional_choices`는 food/potion/augmentation 각 `source_default`만 허용하고, 현재 빌드에서는 SimC `disabled`로 변환. `/api/v1/options`도 동일 승인 계약이다. 옛 v108의 음식/물약 토큰은 소스에 있다는 것만으로 지금 시즌의 동일 ItemID/효과/품질/사용 조건 인증이 아니므로 화면의 기본값을 '사용'으로만 바꾸면 제품이 거짓말한다.
- **후속 제품 작업**: 현재 시즌 food 아이템·최고 품질·기본 주스탯 수치·정확 SimC token 및 현재 대표 특성의 유효성, DPS 물약 전문화별 기본 SimC 프로필과 실제 사용/발동 조건, 검증된 영약 목록(정확 F/ItemID/J/O 설치 일치)을 기존 v216/v212/v218 경로에 정확히 연결. 같은 효과 낮은 품질은 목록에서 숨기고, 서로 다른 F/효과 구조는 세션·캐시 identity를 보존한 채 실제 SimC DPS 후보로 비교하여 선택. 임의 stat 최상치/과거 고정 F를 신시즌 기본으로 복사하지 않음. 이것은 별도의 소모품 admission P1 작업이며 이번 UI 수정으로 완료 표시하지 않는다.

## 검증/권한/비용
- 코드는 기존 격리 브랜치에만 적용. API는 정확한 현 시즌 v212 source identity가 있어야 이미지 대상 선택지가 나오고, 최대 80 ItemID, 인증된 자격증명을 1회 OAuth + icon GET 최대 80회(4 병렬)로 사용; 동일 세션/설치 SHA는 메모리 HIT(HTTP0). 이미지 부재는 효과나 DPS 차단 사유가 아니다.
- UI DOM ID·SimC session/CHMV G,J,F,O/E/L·adaptive Native/95%·DPS cache/취소·재개·v217 fingerprint/영구 runtime dependency는 그대로. 실제 보안 보호와 source-only verdict 유지.
- 이 변경에 대응하여 v114/v182 위치 회귀를 교정하고 v665 icon URL·권한·DOM·same-effect+E projection 시험을 추가. `main`/v003 immutable/Project Sources UI/Work OS M0/공식 78 계약 승격, 주 제품 채팅 소유권 불변. 15/78은 제품 진척도 비율로 사용하지 않는다.

## 다음 검증 필요
- 이번 신규 Windows Python3.12/3.14 패키징·기존 API·UI 회귀 최종 결과와 exact signed same-family projection을 확인한 후 제한된 사용자가 ZIP 1개만 설치하여 실제 아이콘 출력·UI 장식 위치와 마부 가독성을 확인.
- 음식·물약/영약 검색은 아직 미구현. 실제 개인 PC에서 다음 최적화 Native DPS·SEM/95% 결과는 별도의 최초 E2E 시험으로 확인할 필요가 있다. 무조건 26전문화 전수 Native 반복 금지.

## 최신 검증과 실사용 ZIP (2026-11-22)
- **최종 Windows 제품 ZIP [Actions #45028652387](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45028652387) SUCCESS**: Win2022 Python 3.12와 3.14 각각 **333 tests PASS / 0 FAIL**, 패키징 5 PASS, 실제 압축 해제 → Windows CMD 실행 → localhost HTTP 3개 기존 계획 + 보안 PASS. 패키지 원본 286 파일(기존 285 + v665 모듈), 신규 Native DPS 0회.
- 배포 ZIP [artifact #14757116064](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45028652387/artifacts/14757116064) 에서 중첩 GitHub Actions wrapper를 제거하고, 실제 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip` 1개를 사용. SHA256 **`476bb9dbbf68b23df68e33b98531fdd9c0552f30eed7f781cbf1155324490fbe`** · 크기 **1,523,483 bytes**, 원본 286개 각각 SHA-256과 ZIP CRC 전부 PASS, EXE 포함되지 않으며 설치 후 기존 공개 SimC 이용.
- **실제 API/가독성 회귀**: [v113 Linux+Windows #45028652352](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45028652352) SUCCESS, [v182 Windows+Linux #45028652470](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45028652470) SUCCESS, [공통 focused #45028652344](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45028652344) SUCCESS. 선택지 source-only/CHMV 상태·26 spec 기본 범위, 장식 이동에 따른 원래 v114/v182 예상 위치 테스트를 새 승인 UI에 맞춰 교정.
- **정확한 한계**: Blizzard 미디어 CDN이 개인 PC에서 응답하는지, 실제 사용자에게 아이콘이 표시되는지 아직 현장 확인이 없음. 기본 음식/전문화별 물약의 nondefault admission과 DPS 기반 영약 결정은 **미구현**. 이번 Windows 333 PASS를 이들 기능 완성이나 일반 DPS 최적화 E2E로 오해하지 않는다.
