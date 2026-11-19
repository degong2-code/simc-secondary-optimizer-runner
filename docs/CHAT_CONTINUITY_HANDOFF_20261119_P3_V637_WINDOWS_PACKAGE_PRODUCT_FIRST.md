# SIMC SECONDARY OPTIMIZER — P3 최신 제품 우선·Windows 배포·v637 독립 복원 인계

**작성: 2026-11-19 KST · GitHub HEAD 확인 스냅샷 `be8754467f4cfd97b768a652eb8015153cc777ed`.** 본 파일 작성 후 HEAD는 바뀔 수 있으므로 새 채팅은 항상 최신 HEAD·CURRENT·Actions·Native 원본을 재조회한다. 이 문서는 역사적 v629 인계의 NEXT를 대체하지만 증거를 삭제·소급 승격하지 않는다.

> **새 채팅 첫 응답 = READ-ONLY 독립 복원, 아래 7항목 보고, STOP.** 사용자 별도 **`진행`** 전 GitHub/코드/문서/Actions/Native/HTTP/DB2/캐시·공식 78 상태 변경/실행 금지.
>
> **현재 가장 중요한 것은 추가 기술 연구가 아니라, AI 없이 실제 SimC로 미래 파밍 목표 CHMV 절대 rating·DPS·SEM·95%·대안을 구하는 일반 Windows 사용자 제품의 완성**이다. 이미 성공한 엔진과 원본을 보존하고 첫 실사용 단절만 가장 싼 방법으로 연결한다.

## 1. 정본·복원 순서

- 저장소 `degong2-code/simc-secondary-optimizer-runner` / 격리 브랜치 `probe/chat-cache-v035-20261024`. 본 인계 작성 전 검증 HEAD `be8754467f4cfd97b768a652eb8015153cc777ed`; **스냅샷이지 고정 정본 SHA가 아니다.**
- **먼저** 이 문서 → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` → `docs/development/APP_PACKAGE_FILE_REGISTRY_20261113.md` → `WINDOWS_BETA_START_HERE.md`를 읽는다. P3가 현재 NEXT이며 이전 v629의 '19→30 재등록 시험'은 **v630에서 완료**, 8개 양수 E도 **v633에서 완료**. 과거 문서의 NEXT를 다시 실행하지 않는다.
- 실제 E+ 사용자 실행: `docs/development/notes/2026-11-19_p2-v637_manual_final_T_signed_Eplus_real_windows.md`, `2026-11-19_p2-v636_signed_G_owner_Eplus_user_flow_real_win.md`, `2026-11-19_p2-v633_full_season_permanent_enchant_native_E_auto_registration.md`, 이전 v624/v627 기록. 정책 `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md` 및 `POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md`, `PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md` 최신 사용자 결정, `ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md`, `78_ELEMENT_COMPLETION_CONTRACTS.json`.
- 소스별 실제 소비 경로를 읽는다: 배포 단일 `integration_probes/v181_windows_beta_packager.py::select()` → `START_HERE_AUTO_SETUP_AND_RUN.bat` / `START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd` / `runner/webui/app.js` / `v113_local_web_api.py` → 시즌 `v216/v217/v212/v222` → 대표 프로필 `v098/v096/v139` → 적응형 `v093/v094/v290/v291/v293`. 관련 Actions jobs, 실제 다운로드된 원본 영수증과 정확 SHA를 직접 대조한다.

## 2. 제품 목적과 런타임 소유권 — 개발 최상위 판단

**지원 범위는 26개 DPS 전문화(증강 기원사·탱커·힐러 제외), 목표 ilvl 기본 334 또는 사용자가 수동 지정한 최종 CHMV 총량에서 SimC DPS를 최대화하는 치명·가속·특화·유연의 `절대 rating`을 찾는 것.** 관측 DPS/SEM/명목 95% 비교·최상위/실질적으로 다른 근접 대안·비율도 반환한다. 전역 최적해 입증과 관측 1순위/95% 통계적 우위 확정은 구별한다.

- 일반 사용자: 직업/전문화/종족/특성, 목표 ilvl 또는 최종 T, 장신구 2개, 선택 특수 장비·장식 최대 2개, 시즌이 검증한 보석·영약·영구 마부·기름·전투조건 선택. **전체 현재 장비/현 CHMV·내부 전체 filler를 입력받지 않는다.** 선택 업로드 SimC 프로필은 주로 캐릭터/특성 추출이다.
- 프로그램 내부: 실제 시즌 자동 발견 → 대표 일반 장비/무기/주능력치/티어4세트 및 G/J/F/O 검증 → B/T/L/E/O 중복 방지·최종 프로필 → **기존 적응형 SimC** → DPS/SEM/95%/대안 → 저장·읽기 전용 재열람·캐시·취소·재개.
- SimC가 아이템·마부·보석·기름·장신구·장식 효과/proc/APL/DPS를 계산. 자체 코드는 원본 출처·ID·빌드·일치하는 슬롯/손/품질·정적 rating/예산·프로필 및 JSON2 정합·통계/캐시/세션만 소유. **마부 효과 엔진/발동 인증 Gate/APL·최적화 solver 신설 금지.**
- **AI 활용은 개발 단계만; 배포 제품 기본 실행 경로의 생성형 AI API·GPT·에이전트 필수 의존성은 0.** v628은 지정한 기본 런타임 경로에서 생성형 AI 호출 미발견을 확인했으며 모든 간접 의존성의 무조건적 전수 인증은 아니다. opt-in `v312` 수학적 실험은 기본 비활성.
- 공식 식 `B=G+J+F`, `T=B+O`, 수동 최종 T 우선 시 `B=T-O`, `c_final=c_base+o`. 선택 L은 해당 G 내부 고정 하한, E는 **검증된 소유권에 따라** 한 번만 반영/고정 하한, O는 무기 기름 비자유분배 고정치. E0은 정적 CHMV 0인 **정상 효과 마부**, E 미관측을 0으로 대체 금지. 장신구 정적 스탯은 자유 G 밖이고 레코드 미출력을 0이라고 추측하지 않는다.
- 미래 시즌 전체 G/J/F/O를 새 원본으로 산출한다. 70961의 `G2850/J92/F165/O0`, 역사 참조 79×2/F165 등은 **새 시즌 검증값이 아니다**. 품질은 정확히 동등한 효과·조건을 증명한 최고 품질만 일반 선택지로 노출. 임시 마부는 제외하되 별도 **무기 기름은 지원**; 시즌 특수 콘텐츠는 일반 제품 이후 선택 모듈.

## 3. 성공한 내용 — 재개발 금지 / PASS 범위 엄격 구분

- **v567** ZERO-SOURCE 시즌 환경 자동 구축 PASS. **v570** 실제 Windows Chrome 현재 시즌 한 시나리오 Native64 완료 및 결과 PASS. **v572** 추출 Windows ZIP의 실제 SimC Native2→중단/재시작→추가2, 누적4 재개 PASS. **v290/v291/v293** 기존 적응형·캐시·95%·통계·세션 경로 재사용.
- **v624** 실제 70961 Chrome 한 부위 E0(가슴 7957) 사용자 시나리오: SimC Native64 최종 CHMV rating·DPS/SEM/95%·근접 대안6·결과 저장·재시작 후 읽기 전용 재열람 PASS. [Actions #44454908607](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44454908607). 통계적 최고 확정/모든 전문화 PASS/전역 최적은 아님.
- **v627** 머리7959+가슴7957 서로 다른 E0 마부 동시 선택, 실제 Native2→Cancel→HTTP 재시작·동일 세션 Native4 PASS. **v628** 중복 v212 파일 읽기 N→1 및 기본 런타임 생성형 AI 미사용 감사.
- **v629–v630** 원본 v213→v196 슬롯 가족 전달 누락을 수정하여 70961 영구 마부 등록 **19→30** 실제 PASS. 원본 미확정 8개는 정상 보류로 구별. 옛 19→30 '재실측 전' 상태를 현재 상태로 다시 보고 금지.
- **v631–v633** 새 시즌 발견 마부 **전부를 분류**하되 38개 수는 시즌 상수가 아님. 70961에서는 30개 정적 E0 출처 증거를 재사용, 정적 E 미확정8개만 기존 `v278` 전·후 Native와 `v297` 초기 gear rating 비교로 **baseline1+활성8=9 Native**, 각각 실제 정확한 E를 확정. 치명/가속/특화/유연 각각 **+24/+29**(목표 ilvl334/70961), `v220/v196/v212` 기존 Policy A로 **38/38 자동 등록 PASS** [Actions #44478946469](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44478946469). 그룹화는 Native 수치나 다른 마부 자동 승인 증거가 아님.
- **v635–v636** 70961 실제 E0 가슴7957 + E+ 반지1 8025 가속29 + 반지2 7997 치명29, `E_total=58`, **자동 B=T3165**; Native2→취소/재시작→누적4 PASS [Actions #44486603654](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44486603654). v636 원인은 v216이 증명한 `G_reference_excludes_selected_E`가 v222 결과에서 누락되어 v212가 E+ 소유권을 판정할 수 없었던 것. **기존 source bool을 서명된 결과에 전달하는 최소 수정**으로 복구. 새로운 E/G 엔진을 만든 사례가 아님.
- **v637** 같은 세 마부의 실제 일반 사용자 Chrome **수동 최종 T3500 입력 우선**, `O0`, 따라서 **B=T3500**, E58은 총량 안의 고정 하한, 각 ID SimC 프로필 1회, Native2→Cancel/HTTP 재시작·같은 세션·수동 T 및 마부 값 복원→누적4 PASS [Actions #44488595284](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44488595284). **v637 최종 DPS64/SEM/95% 결과 완료·재열람 PASS가 아니다.** v624 별도 E0 결과 PASS를 명시적으로 재사용한다.
- **P3 최신 Windows 배포 후보 점검 (2026-11-19):** 현재 HEAD 소스를 기존 **단일 v181 packager**로 묶은 **282파일 Python Windows 베타 ZIP**, SHA256 `855e8bca8e53f2e7f6efabaa39a20f92c2308f7f409cb4b75a1adc75eb022bfd`, [Windows #44490716235](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44490716235) **Python 3.12·3.14 각각 SUCCESS**, [artifact #14512093279](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44490716235/artifacts/14512093279) (7일 보존 가능). ZIP 실제 열어 v632/v222/v098/v096/v093/웹 UI/BAT/시작 안내 포함, 압축 해제·BAT/CMD·localhost HTTP·3개 시나리오·기본 보안 회귀 PASS. **이 ZIP 시험은 Native0/DPS0/컴파일0이며 최신 ZIP 자체에서 70961 E+ 사용자 결과 전체를 완료했다고 주장할 수 없다.**
- 현 ZIP의 과거 `v213` 빌드 `12.1.5.70575`는 `automatic_ui_promotion=false`인 **미승인 역사 source 후보**이며 현재 시즌 READY 근거 아님. 일반 `v113`는 실제 현재 KR 빌드를 조회하고 기존 `v216` ZERO-SOURCE 경로를 사용한다. ZIP은 **독립 EXE 아님**, SimC CLI 미포함, Python 3.12+/웹 의존성 사용자 동의·별도 SimC 및 때때로 개인 인증 출처 키 필요. 기존 ZIP/사용자 세션은 새 HEAD 코드로 자동 업그레이드되지 않는다.

## 4. 현재 우선순위 — P3 제품 최종 인수, 첫 단절 하나씩

**최상위 NEXT: '최신 배포 후보 ZIP 자체'에서 사용자 설치/동의→로컬 웹→현 빌드 ZERO-SOURCE·검증된 옵션→대표 SimC→적응형 DPS→완료 결과·저장/재열람의 첫 실제 단절을 확인한다.**

- 먼저 v181 ZIP의 이미 확인한 282 파일 SHA/기동·HTTP 결과를 재사용하고, v572 **추출 ZIP Native 재개**, v624 **최종 결과/재열람**, v637 **E+·수동 T·Native 재개**를 차례로 대비한다. **이 증거들의 조합을 동일 ZIP·동일 시나리오의 완료로 무단 합성하지 않는다.**
- 실제 사용자 가치는 **받은 ZIP에서 표준 입력으로 AI 없이 목표 CHMV rating/DPS를 얻고 중단·재열람할 수 있느냐**에 있다. 최초 실사용 장애가 확인되면 사용자에게 보이는 증상→첫 실패 경계→직접 소유 모듈·source owner→재사용 가능한 성공 증거를 좁혀서 **1개만 CONNECT/FIX**. 다른 실패가 없다면 STOP하고 기존 증거 재사용으로 보고. 단지 P3 인수 수치를 높이기 위해 매번 새 Native64/26전문화 전수·모든 마부 38개 재측정·환경 재수집을 실행하지 않는다.
- 완결 증거가 정말 없고 현재 배포 ZIP 고유 결함 여부를 구별할 다른 방법이 없을 때에만 **딱 필요한 동일 조건 1개 실환경 경로**를 추가 시험한다. 비용을 사전 기록하고 가능한 동일 SimC binary/원본/캐시 HIT 재활용. 합성 테스트·초기 DPS2·Native4/64완주/최종 결과 저장·읽기 전용 재열람을 각각 구별.
- 제품이 제공하는 출시 형태의 정확한 현재 경계: `START_HERE_AUTO_SETUP_AND_RUN.bat`→Python 소스 ZIP 및 사용자 설치·동의 경로; 단독 EXE 배포 확정도, 사용자 개인 PC의 모든 Windows 정책에서 설치 검증도, 현 시즌 26 전문화 전체 E2E도 아직 아님. **이런 범위를 해결하겠다고 불필요한 '새 패키징 엔진'·폴더 복제·배포 목록 수동 이중 관리**를 만들지 않는다. 파일 선정은 `v181.select()` 하나로 관리.

**별도 후순위:** 새 확장팩 특수 모듈/선택형 콘텐츠, 전체 26전문화·모든 장비/마부 조합 전수 실험, 독립 EXE 배포 완성, 원본 v016 직접 통합 등은 현 사용자 제품 첫 단절보다 우선하지 않는다. 단, 실제 선택한 옵션에 필수 증거가 없으면 해당 옵션만 보류/정확 오류 보고.

## 5. 최근 근본원인·효율 유의사항

1. **매 코드 변경 전** (a) 사용자 입력·화면에서 실제 쓰는 위치, (b) 첫 불편/결함, (c) 기존 원본·코드/캐시·Native/Actions 증거, (d) 기존 기능 연결만으로 해결되는지, (e) Native·HTTP/DB2·CPU/RAM/I/O·새 캐시 비용, (f) STOP/선택옵션 격리 기준을 짧게 명시. **`STOP → REUSE → CONNECT/FIX → 필요한 최소 EXTEND → 최후 NEW`**. 필요성이 없으면 '개발하지 않음'이 올바른 선택이다.
2. 특정 ID를 수동 승인하는 대신, **다음 시즌에서도 생기는 유형의 원인**을 고친다: v629 원본 슬롯 가족 projection 누락, v631 스케일 E 미확정 작업 분류, v633 측정→정적 receipt→Policy A 등록, v636 G 소유권 투영 누락. 측정 없는 E0 추정/타 항목 scaling 비례 숫자 복사 금지. 기존 검증에 없는 새 자료를 요구하는 과잉 Gate 금지.
3. UI Selenium이 숨겨진 `<select>`를 조작해 실제 표시 상태가 맞지 않았던 v635 첫 시험 사례처럼 **실제 사용자가 누르는 visible 검색형 선택기**로 시험한다. 합성 fixture ID·임의 마부 품질·70783/70961 E와 binary·DB2/SHA 혼합 금지. 완성 ZIP 속 70575 history 원본의 자동 승격 금지.
4. G/J/F/O 새 시즌 정상 구축과 **선택 마부/특수 콘텐츠 미확정**은 다르다. BASE를 쓸 수 있는데 해당 옵션 문제로 전체 제품을 막지 않는다. 반대로 진짜 필수 G/J/F/O가 미검증이면 READY라 하지 않는다.
5. 같은 시즌 아이템 정적 캐시는 SimC revision만으로 폐기 금지; DPS 캐시는 실제 바이너리/프로필/후보/마부 E·기름 O·전투/iterations identity를 정확히 분리. 취소·재개·SHA·파일 읽기 반복, Native 수·HTTP/DB2·메모리/I/O/컴파일 비용을 매 변경에서 확인.
6. 검증 명칭 분리: **코드 추가 ≠ 오프라인 PASS ≠ 실제 시즌 E 등록 PASS ≠ Native DPS 실행 PASS ≠ 한 시나리오 결과64 PASS ≠ 배포 ZIP 최초 실행 PASS ≠ 최종 full_product_e2e COMPLETE**. 성공한 단계의 역사 증거를 새 빌드의 동일 PASS라고 복사하지 않는다.

## 6. 공식 상태와 권한

- 공식 원장 **`15/78 COMPLETE` / `full_product_e2e=PENDING` / `next_review=B10`**. 15/78은 코드 전체 완성률 아님, B10은 공식 판정·감사 순서로 **현재 P3 실제품 개발의 차단 Gate 아님**. 사용자 승인 없는 공식 상태 갱신 금지.
- **격리 브랜치 개발은 사용자 `진행` 이후 계속 허용**, 단 `main` 병합, `v003 immutable`, 공식 Work OS M0/Shared State, Project Sources/Instructions UI 실제 등록, 원본 `v016` 직접 통합 완료 주장은 사용자 별도 권한/실증이 필요. 본 문서 기록은 그 대상의 적용·승격이 아님.
- 새 채팅 READ-ONLY 복원 또는 인계만으로 현재 주 제품 개발 채팅의 공식 주도권이 자동 이전되지 않는다. 사용자가 새 채팅에서 `진행`하면 최신 HEAD·첫 사용자 장애·기존 권한 조건을 확인한 뒤 격리 범위 개발한다. 기존 산출을 재시작하거나 과거 자료 전면 재감사하지 않는다.

## 7. 새 채팅의 **첫 응답 7항목** (READ-ONLY, STOP)

1. **최신 HEAD/Actions**: 실제 HEAD·최근 커밋·SUCCESS/FAIL/CANCEL/SKIP, v637 실제 수동 T Native4, 최신 P3 배포 ZIP Windows PASS; 실행 시점별 코드/바이너리 범위.
2. **최종 제품 목적**: 26 DPS(증강 제외), 목표 절대 CHMV+SimC DPS/SEM/95%, AI 런타임0, 사용자 현재 전체 장비 선택 금지, SimC/자체 책임.
3. **시즌/마부 자동 등록**: v567 ZERO-SOURCE, 70961 G/J/F/O=2850/92/165/0, 현재 **38/38 승인(30 E0 +8 E+24/29)**, v629→v633 실제 원인 수정·원본/SHA/Native 경계.
4. **이미 성공한 실제 사용자 흐름**: v624 E0 Native64/최종 DPS·결과 재열람, v627 다부위 E0 재개, v636 자동 T3165 E+ Native4, v637 수동 T3500 E+ Native4, v181 최신 282파일 ZIP 첫 실행/HTTP PASS(그 자체 Native0).
5. **필수 미완료/선택 보류**: 현 ZIP 자체의 동일 출처 ZERO-SOURCE→USER Native·최종 결과·저장/재열람 완결, 개인 PC/독립 EXE/전26 E2E 등 범위 구분; 선택 시즌 모듈은 후순위.
6. **가장 싼 다음 작업 1개**: ZIP 최초 실행의 **실제 미입증 첫 경계만** 확인; 기존 v572/v624/v637 증거 재사용, 새 Native/DB2/64/패키징 신설 전 STOP 판단·비용.
7. **공식/미확인 경계**: `15/78`, PENDING, B10, 역사 source 70575/현재 70961, 설치·AI 비의존 과장 금지, `main`/`v003`/`v016`/Project UI/Work OS/주 개발 채팅 권한 제한.

**7항목 보고 후 STOP.** 사용자가 별도로 **`진행`**이라고 지시한 다음부터 현재 GitHub·원본/Actions를 다시 읽고 가장 좁은 사용자 제품 단절을 수정한다.
