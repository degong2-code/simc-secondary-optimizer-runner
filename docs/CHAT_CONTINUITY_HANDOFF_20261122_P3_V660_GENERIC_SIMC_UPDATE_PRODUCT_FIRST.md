# SIMC SECONDARY OPTIMIZER — 2026-11-22 P3 v660 최신 독립 복원·인계

> **첫 응답 READ-ONLY 계약:** 새 일반 채팅은 정확한 GitHub 최신 HEAD·CURRENT·코드·Actions·Native/ZIP 영수증을 다시 확인하고, 아래 지정된 **7항목만 보고한 뒤 STOP**한다. 별도 사용자 `진행` 전에는 코드·문서·GitHub 권한·Actions·Native·HTTP·DB2 호출/변경을 개시하지 않는다. 이 인계는 역사 요약이나 새 프로젝트 시작이 아니며, 주 제품 개발 채팅의 소유권을 무단 이전하지 않는다.
>
> **인계 작성 직전 스냅샷 HEAD** `1060c7d7998c01c58761038a5dbf560b1567d8f4` (2026-11-22 19:37 KST 해당 HEAD). **문서 기록 커밋 이후 달라지므로 새 채팅은 반드시 최신 HEAD를 재조회**한다.

## 1. 정본·읽기 순서

- Repo: `degong2-code/simc-secondary-optimizer-runner`; 격리 브랜치: `probe/chat-cache-v035-20261024`. `main` 병합/공식 승격 권한은 부여되지 않았다.
- 첫 문서 **이 파일** → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` → `docs/development/notes/2026-11-22_p3_v660_generic_oneclick_clean_windows.md` → `docs/development/notes/2026-11-22_p3_v659_generic_selfbuilt_import_actual_70961.md` → `docs/development/notes/2026-11-22_p3_v658_generic_simc_windows_builder.md` → `docs/development/notes/2026-11-22_p3_v657_generic_simc_updater_candidate_discovery.md`.
- 이어 `docs/CHAT_CONTINUITY_HANDOFF_20261120_P3_V647_PRODUCT_FIRST_SOURCE_ROOT_CAUSE.md`, `docs/development/notes/2026-11-19_p3-v639_published_zip_70961_final_result_restore.md`, `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `docs/development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md`, `docs/development/UI_DESIGN_VERSION_REGISTRY.md`, `WINDOWS_BETA_START_HERE.md`, 실제 GitHub Actions workflow/receipt 및 Windows ZIP source manifest를 필요 범위에서 확인한다.
- 오래된 v647 인계 문서·`WINDOWS_BETA_START_HERE.md` 상단에는 수동 SimC/7-Zip 안내가 남아 있다. **v660의 실제 단일 ZIP·py7zr 신규 사용 흐름에 관한 최신 노트와 코드를 우선**한다. 오래된 문장을 그대로 사용자에게 최신 사용법이라고 안내하지 않는다.
- 사용자 직접 결정 > 최신 승인 정책 > 실제 최신 코드·CURRENT·CI 영수증 > 이전 인계 문서. 오래된 v1.4.1의 27 DPS/증강 포함 기록보다 최신 **26 DPS·증강 제외** 직접 결정을 우선한다. Project Sources 실제 교체 여부를 추정하지 않는다.

## 2. 제품의 실제 목적 — 업데이트 관리자 개발로 잊지 말 것

**최종 제품은 사용자가 목표 ilvl(기본 334) 또는 수동 최종 CHMV T를 지정하면, 미래 파밍 목표가 되는 치명·가속·특화·유연의 최적 절대 rating을 실제 SimC DPS로 탐색하는 일반 Windows 프로그램**이다. 26개 DPS 전문화만, 증강 기원사·탱커·힐러 제외. 현재 착용 장비 전체 스탯 재분배나 전 장비 선택·장비 추천/파밍 경로·시즌 전체 장비 DB가 아니다. 런타임 생성형 AI 호출 0.

제품 입력→시즌 자동 발견→**동일 시즌 G/J/F/O 전체 자동 구축**→`B=G+J+F`, `T=B+O`, 수동 T 우선 `B=T-O`, `c_final=c_base+o`→정확한 L/E/O 중복 방지 및 고정 하한→대표 일반 장비·무기·티어4세트/장신구2·선택 특수장비·장식 최대2·최고품질 선택지→기존 적응형 SimC→관측 최고 절대 rating, 비율, DPS, SEM, **95%** 우위/미확정 및 실질적으로 다른 대안→캐시·취소·재개·저장·재열람.

기름 O는 고정·비자유분배이고, L은 G 안에 이미 포함해 재가산하지 않는다. E는 정적 예산 소유권에 따라 한 번만 반영. 제작 초기 50:50은 L 잠금 금지. 장신구 정적 gear 레코드 미관측은 0 실측/아이템 선택 차단이 아니다. 새로운 시즌에 기존 79×2 시즌 참조 B나 F165/J92/O 등 숫자를 증거 없이 복사하지 않는다. 검증된 같은 효과·조건의 최고 품질만 사용자 선택지에 노출. 확장팩 고유 시스템은 선택형 별도 모듈.

**SimC가 실제 APL, 장비·장신구·장식·보석·마부·proc, DPS 계산을 책임진다.** 우리 코드는 정확한 ID/ilvl/옵션/실행 프로필/예산/스탯 중복 방지/JSON2 정적 rating/후보·95% 통계·캐시를 책임진다. 독자 APL·효과 재구현·발동 인증 Gate·새 최적화 엔진 추가는 범위 밖. 95%만 사용하고 관측 최고가 통계적 우위·전역 최적해 증명임을 주장하지 않는다.

## 3. 재사용해야 할 이미 성공한 자산

- v567 ZERO-SOURCE 시즌 환경 구축 성공. 해당 시즌 실제 70961 대표 조건 v611: **G2850/J92/F165/O0, B=T3107**(다른 시즌의 고정값 아님).
- 영구 마부 v629~v633 **38/38 등록 PASS**, E0 30개 원본 재사용, 정확한 미확정 E8개만 추가 Native 검증. 독자 마부 효과 엔진 불필요.
- 기존 적응형 SimC/캐시·취소·재개·원본 영수증, v624 E0 Native64, v636~v638 최소 Native 취소·재개·수동 T/E+ 실증.
- **v639 실제 배포 ZIP** 대표 1건 징벌 성기사/334/70961 **Native64 최종 완주**, rating **1098/922/922/165**, DPS **161718.63**, SEM **243.11**, 95% 우위 미확정, 근접 대안 **5개**, 저장·서버 재시작·재열람 PASS. [run #44539361949](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44539361949). 개별 제품 조건의 역사적 성공이지 26전문화/모든 PC 보증 아님.
- 기존 SimC 안전 7z 압축 경로 검사·다운로드/캐시·원자적 활성 포인터/롤백과 시즌 정적 캐시를 **REUSE**. 같은 시즌의 정적 아이템 캐시는 단순 SimC revision 변화로 무효화 금지. DPS 캐시는 실제 바이너리 SHA·캐릭터·프로필·환경·후보·O·전투조건·iterations 별 분리.

## 4. 최근 v657~v660 핵심 기술 진척과 정확한 검증 경계

- **v657:** 공식 Nightly Windows x64 후보를 첫 1개가 아닌 최대 12개 검사; Git short SHA 사전순을 최신 커밋 순서로 착각하지 않는다. `client_data_version.inc` 저비용 사전 판별→일치 가능할 때 3개 생성 헤더 정밀검증; bounded source cache. 실행파일이 없으면 HEAD 원본은 `source_only`이고 다운로드/설치 가능이라고 주장하지 않음. [focused #45006800115](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45006800115) 양쪽 Python 각각 35 PASS.
- **v658:** 공식 `simulationcraft/simc` **전체 40자리 source SHA**로 Windows x64 Release CLI 전용 CMake/Ninja/CPack 컴파일, GUI 비활성, Windows CRLF 오탐 교정. `6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7` Live `12.1.5.70961`로 [run #45007868837](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45007868837) 실제 **Windows CLI 빌드·CPack .7z·display_build 기동 SUCCESS**. 이 자체 컴파일본은 공식 SimulationCraft 배포본이 아님.
- **v659:** 사용자 직접 지정한 자체 빌드 Actions ZIP의 정확한 멤버/영수증/full SHA/build/7z·exe SHA 검증과 기존 원자 설치·롤백 연계. 사용자 제공 ZIP 자체는 신뢰할 수 있는 공식 서명이 아니므로 `source_origin_authenticated=false`를 보존. 실제 70961 artifact 재사용 검증 [#45009357618](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45009357618) SUCCESS, 별도 Native DPS0.
- **v660:** **일반 사용자 단일 제품 Windows ZIP**에서 명시적 클릭으로 현재 KR Live 확인→기존 호환 바이너리 재사용→공식 Nightly→검증된 공개 자체 빌드 prerelease 캐시→HTTPS 다운로드, SHA/원본/내장 빌드 확인→py7zr로 외부 7z.exe 없이 안전 추출→원자 설치/롤백→2회차 중복 다운로드·컴파일 회피. API `POST /api/v1/simc-updates/prepare-auto`. [실제 Windows 제로베이스 #45012696519](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45012696519) SUCCESS: 빈 SimC/관리 폴더, 별도 7zip 없음, 공개 테스트 prerelease에서 70961 설치 및 재실행 재사용 PASS. [Windows 베타 ZIP #45012956028](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45012956028) Python3.12/3.14 각각 **323 PASS**, CMD/localhost HTTP3 plans PASS. [실제 ZIP 압축 해제→로컬 HTTP #45013234606](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45013234606) **SUCCESS**, 인증 없는 POST403, 실제 KR70961 공개 다운로드/py7zr/SimC SHA·display_build/캐시 재사용/롤백. Native DPS0.
- 최신 **한 개만 필요한** 베타 제품 ZIP: `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA_v660_SINGLE_ZIP.zip`, 1,517,555 bytes / SHA256 `a22ee056b6de4ab3287c5fa2bd5fdda878804ccdc8da0edaaba5a1e6781e2c93`, 285소스+manifest=286 entries/CRC PASS, 바이너리 직접 번들하지 않음. 과거 v659의 **별도 SimC ZIP 2개 다운로드 안내는 최신 기본 사용법이 아님**.
- 공개 `degong2-code/simc-secondary-optimizer-runner` GitHub Release의 **EXPERIMENTAL prerelease** tag `simc-cli-source-6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7`, asset `simc-win64-cli-6924096-12.1.5.70961.zip`, 8,834,290 bytes, SHA256 `8f94209f1b7013da23fca47ada972630d18a371abd0e3d86f491bbad27dec2fd`. 업스트림 SimC의 공식 릴리스/제품 공식 승격과 **별개**, 검증한 70961 테스트 공개 캐시. 동일 빌드 바이너리를 전문화마다 빌드하지 않는다.
- CI와 브라우저/Windows 런처 검증은 **일반 사용자 개인 PC의 전체 시즌 환경·26 DPS 완주**를 뜻하지 않는다. 전체 `full_product_e2e=PENDING` 유지.

## 5. 가장 중요한 남은 첫 장애와 우선순위

**현재 개발 우선순위의 1번은 ‘범용 SimC 업데이트 관리자’의 마지막 공백을 제품 목적·비용 관점에서 최소한으로 메우는 것이다.** 지금 v660은 **공식 배포 또는 공개 검증 캐시가 존재하는 경우** 단일 ZIP Windows 제로베이스 성공. 하지만 두 곳 모두 비어 있는 **새 시즌/새 패치**에서 원본만 일치하면 `SOURCE_BUILD_REQUIRES_REMOTE_BUILDER`로 차단되고, 사용자 PC/토큰 없이 신규 Windows CI를 요청하고 결과를 공개·검증하는 **신뢰된 중앙 빌드 브로커(혹은 예약·중앙 관리자 빌드/배포 파이프라인)는 아직 미구현**이다.

**다음 개발 단일 과제:** 기존 `v657/v658/v659/v660`을 재사용해 `공식 배포 → 호환 관리본/공개 캐시 → 캐시 미스 시 안전한 신규 빌드 요청·중복제거·검증·공개 배포 → 기존 안전 설치` 경로의 미구현 접합부만 결정하고 구현한다. 최소 안전·권한 검증: 클라이언트에 PAT/비밀키 넣지 않기, 공개 API 무인 workflow_dispatch 가능하다고 가정하지 않기, 사용자 PC에 컴파일러 강요 금지, 공개 수용 서비스의 남용·비용·요청 인증/상한·중복 빌드·빌드 원본 SHA/게임 build·배포 해시 및 만료 정책 검토. 사용자 별도 승인이 필요한 GitHub default branch/main workflow·외부 서버·운영 자격증명·공식 배포 승격은 **실행 전 명확히 경계·보고**한다. 이미 공개된 70961 결과를 또 컴파일해서 PASS 숫자만 늘리지 않는다.

**제품 중심 후속 순서:** 실제 사용자 PC에서 v660 **단일 ZIP만으로** `SimC 자동 확보·설치` → 70961 내장 빌드/연결 → 시즌 G/J/F/O 준비 → `최적 스탯 찾기`까지 확인. 사용자 PC 이전 `V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH`는 원본 파서·헤더 포맷·SimC revision/빌드·소스 접근의 어느 단계에서 실제 실패했는지 아직 확정되지 않았다. 새 정확 바이너리 설치만으로 해결이라고 단정하지 않는다. 같은 문제가 재발하면 기존 `v229`/진단 영수증의 **첫 실패**만 조사해 해당 부분 최소 FIX; 연쇄 PENDING 수십 개를 각각 새 엔진 개발 사유로 보지 않는다. 이미 성공한 v639 Native64/시즌 ZERO-SOURCE/38마부를 전체 반복하지 않고 미입증된 정확한 접합 1건에만 최소 Native. 사용자가 목표 CHMV 절대 rating·SEM·95%·대안·저장 결과까지 도달하면 STOP.

**개발 판단 순서: STOP → REUSE → CONNECT/FIX → 필요한 최소 EXTEND → 최후 NEW.** 특히 자동 업데이트 기능을 위해 현재 제품 목적을 장비 DB/새 optimizer/새 시즌 Gate/AI 서버 기능으로 바꾸지 않는다. 정확한 작업 전후 네트워크·CPU/RAM·I/O·GitHub Actions 비용/캐시 재사용·중복 처리 점검. 한 번 검증된 독립 컴파일 결과는 같은 소스·빌드 설정에서 재사용.

## 6. 현재 공식 신분과 권한 경계

- 공식 78개 상태 **`15/78 COMPLETE`**, `full_product_e2e=PENDING`, `next_review=B10`; **15/78은 개발 진척률을 뜻하지 않음**, B10/Work OS M0 미완료는 일반 제품 구현·Native 시험 중단 Gate가 아니다.
- 격리 브랜치 개발·일반 제품 SimC 시험은 기존 권한 범위 내. **`main` 병합**, v003 immutable 변경, Project Sources/Instructions UI 실제 적용 주장, 공식 78개 상태·Work OS M0/Shared State 승격, 원본 v016 제품 직접 통합 완료 주장은 사용자 추가 지시/실제 영수증 없이 하지 않는다. WEQUIP을 영구 runtime/authority로 만들지 않는다.
- **주 제품 개발 채팅의 공식 소유권은 새 채팅 인계만으로 이전되지 않는다.** 새 채팅은 인계받아 사용자가 `진행` 지시한 범위에서 GitHub 격리 개발을 지원한다. MAIN/WORK가 별도 사용자 허가 없이 주도권을 가져오지 않는다.
- **실제 현재 브랜치 HEAD/Actions/코드 우선**. 위 1060c7...은 작성 직전 시점에만 유효한 스냅샷. 향후 새 HEAD가 있으면 새 기록이 우선.

## 7. 새 채팅 첫 응답 7개 항목과 STOP

1. **GitHub 최신 HEAD·CURRENT·v660 실제 Actions/단일 ZIP**: 성공·실패·취소·skip, 신규 검증 vs 역사적 Native 증거를 나눈다.
2. **제품 최종 취지**: 26개 DPS, 미래 목표 CHMV rating/실제 SimC DPS, G/J/F/O·대표 프로필·AI 런타임0, 장비 재분배/추천 아님.
3. **기존 성공 자산**: ZERO-SOURCE, 시즌 회계·마부38/38, 적응형 SimC Native64, SEM/95%·대안·재개/캐시/저장/재열람.
4. **범용 업데이트 관리자 v657~v660 현 상태**: 공식 탐색/자체 컴파일/ZIP 안전 설치/단일 ZIP 자동 확보 성공; 공개 캐시 미스 신규 원격 빌드 부재를 명시.
5. **실제 사용자 PC 첫 장애/기술 주의**: v229 set-bonus 헤더/파서/빌드 미확정, 두 번째 ZIP 요구하지 않기, Git SHA≠게임빌드, official vs selfbuilt provenance/서명/TLS/만료·권한, UI v653 동결, CI≠개인 PC/전체 시즌 완료.
6. **가장 작은 다음 작업 하나와 STOP 조건**: 중복 빌드 없이 remote builder/cache-miss 경계 해결, 또는 사용자 승인된 PC 단일 ZIP 실측에서 나온 첫 실패 최소 FIX. 성공한 Native/영수증 재사용하고 과잉 신규 기능 중단.
7. **공식 상태·권한**: 15/78, full E2E pending, B10, main/immutable/Project UI/Work OS/주 채팅 ownership 보전.

**첫 응답은 읽기 전용 7개만. 그 다음 STOP, 사용자 `진행`을 기다린다.**
