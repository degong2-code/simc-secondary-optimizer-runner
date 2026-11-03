# SIMC SECONDARY OPTIMIZER · P3-CJ · 2026-11-03 최신 엔진 우선 인계 정본

**단일 진입점.** 새 채팅은 이 파일을 먼저 열고 **GitHub 실제 branch/main HEAD와 영수증을 독립 조회**한다. 첫 응답은 복원 결과와 장·단기 로드맵만 보고한다. 사용자 **"진행" 전에는 코드/문서 수정, 신규 수집·Native·테스트·Actions 실행, 개발 주도권 이전을 금지**한다.

**인계 작성 전 확인한 기준:** 저장소 degong2-code/simc-secondary-optimizer-runner, 격리 브랜치 probe/chat-cache-v035-20261024 HEAD **f230da67243b85fb6c1b513a3e5081b3fd5fb04a**; 독립 조회한 main **07133e0aaf738d6e4816a6486057b1cd49c018de**. 인계 문서 커밋은 HEAD를 바꾸므로 새 채팅에서는 **다시 조회할 것**. 최신 코드 HEAD [focused CI #41642574658](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41642574658)는 독립 로그 조회로 **122 PASS/0 FAIL**, 이전 코드 HEAD #41642094743 역시 122 PASS. 이번 인계 자체는 새 제품 실행/실게임 HTTP/SimC Native를 수행하지 않는다.

## 1. 절대 목적·승인 권한

- **최종 제품은 개별 아이템 기능 모음이 아닌, 26 DPS 전문화(증강 기원사 제외)에서 재사용 가능한 시즌 환경 구축 + SimC CHMV 절대 rating 최적화 엔진**이다. 기본 목표 ilvl334 또는 사용자 입력 최종 T로 미래 파밍 목표 Crit/Haste/Mastery/Vers rating을 찾는다. 결과는 관측 DPS 1위, 예상 DPS/SEM, **95%** 우위 확정 여부(전역 최적 입증과 구별), 비율 및 실질적으로 다른 근접 대안. 캐시·취소·재개 필수.
- 유효 승인 순서: **최신 사용자 직접 결정 > [v1.4.3 시즌별 G/J/F/O 자동 구축](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 및 비충돌 승인 v1.4 계열 > 실제 GitHub 코드·원본·Actions/Native 영수증 > 당시 기록**. v1.4.1 첨부의 27 DPS/증강 포함, 과거 6개 일반보석·J138·특수보석 머리 고정은 현재 범용 규칙이 아니다.
- 사용자 입력: 직업/전문화/종족/특성, 목표 ilvl 또는 기름 포함 최종 T, 장신구 2개, 선택 특수장비·장식 최대 2개, 소켓·보석·영약·기름·소모품·전투조건. 전체 장비나 필수 원본 SimC 프로필을 입력받지 않는다. 내부에서 대표 방어구·무기·4티어·주능력치 및 SimC 프로필 생성. 업로드 SimC 프로필은 캐릭터 정보 선택 추출용, 현재 장비 스탯은 목표 예산으로 복사하지 않는다.
- 예산: **G(일반 대표 장비/무기) + J(검증된 보석) + F(검증된 최고 품질 영약) = B; T=B+O; c_final=c_base+o**. O는 적용 손마다 고정, gear_*에서 **한 번만** 처리. 수동 최종 T 우선. 특수장비 고정 L은 G 안에 있고 하한 보호, E 중복 방지, 장신구 고정치는 자유 G 밖, 제작 초기 50:50은 L 아님. 새 시즌에 옛 79×2/J138/F165/기름당+16/+16을 증거 없이 복사하지 않는다. G 합계 표준화는 nearest 10; J/F/O는 증거의 정밀값 유지.
- SimC는 아이템·proc·APL·DPS 처리. 새 효과 엔진, 인증 Gate, 전수 시즌 아이템 DB, 장비 조합 추천·획득 경로, 새 최적화 엔진 금지. 일반 임시 마부 제외, 영구 마부·별도 무기 기름 지원. 시즌 특수 시스템은 사용자 ON/OFF 가능한 별도 모듈.

## 2. 새 채팅 복원 순서 · 읽기 전용

1. GitHub 격리 브랜치와 main의 **현시점 HEAD를 별개로 조회**. 설계 승인과 적용/승격 상태 분리.
2. [개발 연속성 PROTOCOL](development/PROTOCOL.md) → [기능별 INDEX](development/INDEX.md) → [이번 P3-CJ 노트](development/notes/2026-11-03_p3-cj-engine-evidence-first-handoff.md) → [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) → [개발자 실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md) → [v1.4.3 승인 설계](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md). 역사 [P3-BY 인계](CHAT_CONTINUITY_HANDOFF_20261103_P3_BY_ENGINE_FIRST_RESTORE.md)는 이전 단계 증거/문맥만 재사용.
3. INDEX에서 해당 capability의 prior evidence/최근 note를 **먼저** 읽는다. 특히 [P3-CB](development/notes/2026-11-03_p3-cb-zero-history-one-engine-entry.md)→[CD](development/notes/2026-11-03_p3-cd-collected-source-to-original-compiler.md)→[CE](development/notes/2026-11-03_p3-ce-pinned-simc-source-producer.md)→[CF](development/notes/2026-11-03_p3-cf-physical-v251-to-v191-tier.md)→[CG](development/notes/2026-11-03_p3-cg-zero-history-native-g.md)→[CH](development/notes/2026-11-03_p3-ch-flask-oil-native-pair.md)→**[P3-CI](development/notes/2026-11-03_p3-ci-physical-flask-and-item-enhancement-items.md)**. 보석은 [P3-BY](development/notes/2026-11-03_p3-by-continuity-handoff-gem-sockets.md), [P3-BX](development/notes/2026-11-03_p3-bx-simc-socket-native-contrast.md), [P3-CA](development/notes/2026-11-03_p3-ca-physical-gems-j-normal-build.md) 확인. 현재의 false/PENDING이나 옛 요약만으로 증거 부재를 추론하지 않는다.
4. 필요한 실제 코드·원본만 범위 한정 조회: **v216** 단일 normal Environment Build; **v161/v217/v229/v241/v275/v274/v276** source/seal/컴파일; **v190/v191/v213** 영약·아이템 강화 물리 ID와 SimC 원본 분리; **v233/v234/v236/v277** G; **v101/v135/v139/v271/v270** 가변 소켓·보석; **v269/v278** F/O 실제 SimC JSON2 델타; **v091~v093/v222/v262** 고정 O·GJFO 회계; **v212/v098/v094~v097** 정책 A·사용자 실행/적응형·캐시. 원본 제품 v015/v016은 사용자 보고 기준과 실제 바이트·영수증을 구분.
5. [최신 최종 HEAD focused #41642574658](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41642574658), [코드 HEAD focused #41642094743](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41642094743), [P3-CI 소스→카탈로그 #41642094705](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41642094705), [v211 #41642094697](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41642094697), [v212 양 OS #41642094695](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41642094695), [Windows #41642094662](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41642094662), [UI #41642094770](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41642094770), [실제 소켓 Native #41601140696](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696)를 **각각 원본 적용 범위대로** 확인. 필요 없는 Native/HTTP/CI 반복 금지.

## 3. 확립 사실과 제품 접합 여부를 분리

| 기능 | 현재 구현·검증 및 증거 범위 | 실제 남은 범위 |
|---|---|---|
| 제로베이스 normal Build·source | v113→v216 원래 Build에서 최초 수집, v217 SHA 봉인·동일 build 재개, v274→v241 기존 v191/v211/v213 컴파일, v275 정확한 SimC 원본; P3-CB~CE focused PASS | 실제 신규 시즌을 빈 설치에서 전체 완주해 Environment READY/등록/26 DPS 실행한 E2E 영수증 없음 |
| 대표 티어·G | v250/v251 exact 13×5/65 tier SimC·DB2 후보; v276 물리 대조→기존 v191 입력. v277→원래 v236/v234 Native G·v222 표준화 및 캐시/no-rerun, focused #41628248531 87 PASS와 #41633621369 102 PASS는 **모의/제한 범위** | 실제 새 시즌 모든 목표 ilvl G 근거와 제품 READY는 별개. observed raid/season source candidate를 완전 시즌 인증으로 승격하지 않음 |
| 보석 J | v101 특수보석 240967의 기존 4색 조건, v271 물리 보석/가변 소켓/ID별 J 대조, P3-CA 71 PASS. P3-BX 실제 Native **4/4**에서 gem 240906이 +16 Crit/+8 Haste | 게임 내 소켓 허용성/최고품질·보석 원본 +16/+7과 Native +16/+8의 +1 원인 미해결. **J=24 승격 금지**, 특수보석 1개 실제 장착/소켓별 개수 유지 |
| F 영약 | P3-CI: 기존 v190의 한 Wago Item/ItemSparse 순회로 **Class0/Subclass3 영약 실제 물리 ID 후보** 추가; v191 별도 출처 보존. v269/v278 기존 SimC 정적 델타 측정/공유 baseline 테스트 P3-CH 110 PASS | 정확한 item ID→use spell→SimC token/effect·품질 동등성/최고 품질·해당 rating F 귀속 **미검증**, F 예산·UI 자동 등록 미완료 |
| O 무기 기름 | P3-CI: **Class0/Subclass6은 일반 아이템 강화** ID 후보만; v191의 pinned temporary enchant 토큰/품질 후보와 **별개**. v269/v278 O 델타 관측 seam; 과거 v091~093 고정 O/중복방지 실측 증거 | (0,6) 전부 기름이라고 간주 금지. exact 아이템→사용 주문/effect→oil token 연결, 무기·손 허용, 최고 품질/실제 새 시즌 O 정밀 벡터 미확정 |
| 예산·제품 | v222/v262, v091~093 L/E/O 및 수동 T 회계, v094~097 적응형 SimC·95%·캐시·취소/재개 등 역사 기능 재사용 가능 | 유효 시즌 G/J/F/O→B/T→정책 A 선택지 자동 발행→사용자 대표 프로필→실제 적응형 DPS/SEM/대안의 **하나의 정상 E2E 미완성**. 원본 v016 통합 영수증 미확인 |

**증거 부재 vs 연결 미완료:** 물리 티어 ID·기존 SimC 효과 파서·G 관측 파이프라인·기름 1회 회계·보석 4색 조건·원래 adaptive 실행기는 **이미 코드/범위 증거가 있다**. 반복 조사하지 말고 CONNECT/REUSE 우선. 실제로 부족한 것은 F/O **exact ID↔use spell↔SimC token·품질·손** 관계와 신규 J 허용·정적 원본/Native +1 차이, 해당 시즌 대표 예산의 유효성이다. 실제 GJFO 값을 과거 시즌 상수로 채우지 않는다. P3-CI의 **122 PASS는 오프라인 focused**, 전체 시즌·26 DPS E2E나 신규 Native 인증이 아니다.

## 4. 병목·대안·로드맵

- **즉시 병목 (다음 최소 CONNECT/EXTEND):** P3-CI가 이미 확보한 동일 빌드 flask(0/3) 및 광범위 item-enhancement(0/6) 물리 ID를 **실제 아이템 사용 주문/효과 ID**와 pinned SimC 소스 토큰에 연결하고 품질·적용 무기를 근거별로 판정. 이름만 비교하거나 별도 독립 효과 엔진을 만드는 대신 **기존 Wago/SimC source JOIN과 v217 stage 재사용**. 후보 전체를 새로 수집하지 않는다.
- **단기:** ① F/O의 exact 관계·highest quality·손 조건을 기존 파서 및 최소 필요 부분만 보완 ② v271/보석 소켓·J 원본 정합(+1은 필요한 범위만 조사)과 측정 G 소스 조건 확립 ③ 기존 v222로 B/T 및 L/E/O 중복 방지, v212 Policy A 검증 옵션만 자동 설치 ④ 사용자 한 시나리오 target ilvl/수동 T → 대표 SimC → 기존 adaptive DPS/SEM·95%·대안까지 E2E. 신규 Native는 **무효화/부족 증거에 필요한 최소 1개**부터.
- **장기:** 새 설치·빈 캐시에서 동일 v216 Environment Build가 Wago/SimC 등 **신규 정상 외부 수집을 허용**해 G/J/F/O→B/T→검증된 선택지→26 DPS 공용 profile/기존 적응형 실행·캐시·취소/재개·95% 결과를 완성. 같은 시즌 재실행은 SHA stage와 Native/DPS 캐시를 재사용. 26 DPS에 바로 전수 Native를 돌리지 않는다.
- **효율/완료 기준:** 변경 전 INDEX 선조회→REUSE/CONNECT/EXTEND/NEW/STOP 판정, 독립 작업 묶기, 기존 완료 기준 및 CI/Native 재사용, 신규 HTTP·Native·메모리·I/O·실행시간/캐시 검토. 새 코드 PASS, 역사 영수증, 제품 READY/실서비스 Native를 각각 구분. 반복적인 확인→차단→재확인 루프 대신 **실제 통합에 필요한 최소 변경 후 같은 기준의 1회 집중검증**.

## 5. 권한·첫 응답/정지·새 채팅 시작 프롬프트

- 이번 인계는 **격리 브랜치의 문서 갱신만**. main, immutable v003, 원본 v015/v016, 승인 v1.4.3 본문, 실제 ChatGPT Project Sources/Instructions UI, Work OS M0/Shared State, MAIN/WORK 소유권·공식 승격은 변경/확정하지 않는다. GitHub 문서 반영은 Project UI 등록 증거가 아니다. 일반 제품 구현/시험과 공식 Work OS Gate는 별개.
- **새 채팅의 첫 답변은 읽기/복원 보고만**: 핵심 목적, 실제 두 HEAD, 최신 승인 26 DPS/GJFO, 재사용 가능한 구현/영수증의 적용 범위, 제품 연결 미완료와 정말 빠진 증거, 병목/효율 대안, 단기·장기 로드맵, 미반영 권한을 간결히 보고. 그다음 **사용자가 "진행"이라고 명시하기 전 모든 개발·수정·새 데이터 수집·Native/Actions/테스트 실행 금지**.

### 새 채팅에 붙여 넣을 시작 프롬프트

SIMC SECONDARY OPTIMIZER 인계를 복원해. 우선 GitHub 저장소 degong2-code/simc-secondary-optimizer-runner, 격리 브랜치 probe/chat-cache-v035-20261024의 실제 최신 HEAD와 main HEAD를 독립 확인해. 인계 정본은 docs/CHAT_CONTINUITY_HANDOFF_20261103_P3_CJ_ENGINE_EVIDENCE_FIRST_RESTORE.md이고, 여기서 지정한 순서대로 PROTOCOL→기능별 INDEX→최근 P3-CJ/P3-CI 등 작업 노트→CURRENT→개발자 실행 노트→승인 v1.4.3→실제 코드/원본·Actions/Native 영수증을 선조회해. 최신 직접 결정인 26 DPS(증강 제외), 시즌 G/J/F/O 전부 자동 구축과 B/T, 가변 소켓/특수보석 1개 실장착 정책을 우선해. 과거 27 DPS, 6개/J138, 새 시즌에 검증되지 않은 구형 참조값을 사용하지 마. 기존 구현·확립된 증거와 제품 접합 미완료, 정말 부족한 원본 증거를 분리하고 P3-BX 실제 Native 4/4의 +16/+8을 원본 +16/+7을 덮는 J=24 증거로 취급하지 마. **개별 기능이 아닌 재사용 가능한 하나의 엔진(제로베이스 시즌 원본→G/J/F/O→B/T→대표 SimC→기존 adaptive DPS/95%·캐시)** 완성이 장기 목표인지 항상 자가점검해. 이후 매 작업 전 INDEX/소스/영수증을 읽고 REUSE/CONNECT/EXTEND/NEW/STOP 중 하나로 분류, 독립 작업 묶기, 동일 완료 기준과 기존 검증 증거 재사용, 추가 Native/HTTP·I/O/메모리/시간·캐시 영향 최소화. **첫 응답에서는 현재 HEAD/핵심 증거/완료·미완료·병목 및 단기·장기 로드맵과 권한 경계만 보고한 후 중단해. 내가 "진행"하기 전에는 코드·문서 수정, 신규 원본 수집, 테스트/Native/Actions 실행, 개발 작업을 시작하지 마.**
