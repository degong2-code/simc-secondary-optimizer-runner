# v348 — Windows 사용자 소유 Blizzard/WCL 키 보관 및 원본 v216 수집 연결

- **Capability:** `ENVIRONMENT.WEB`, `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** v348, P1, local credentials, Windows Credential Manager, own Blizzard WCL client id secret, opt-in, zero secret persistence, v216, v242.
- **Prior evidence:** [v347 비밀키 없는 Windows GJFO PENDING](2026-11-12_p1-v347-credentialless-gjfo-current-once.md), [v346 기본 64회 검증 시즌 설치 선행](2026-11-12_p1-v346-current-default-season-install-boundary.md), v242 기존 인증 원본 수집·v155 OAuth.
- **Decision:** `CONNECT` — 사용자의 최신 직접 결정대로 자신이 발급받은 Blizzard/WCL API Client ID·Secret으로 앱에서 시즌을 갱신한다. 개발자가 GitHub Actions/릴리스에 시즌 데이터나 비밀키를 지속 제공할 의무를 만들지 않는다. Windows Credential Manager `CRED_TYPE_GENERIC` `CRED_PERSIST_LOCAL_MACHINE` 단일 로컬 사용자 계정 레코드; ZIP에 키/복호화 암호 내장하지 않는다.
- **Changes:** `runner/v348_windows_user_source_credentials.py` WinCred API 저장·상태·삭제/읽기, `v113` same-origin token-protected local HTTP status/save/clear, 일반 UI 직접 키 입력/즉시 클리어. 기존 `v216.build_environment(fresh_collection_inputs.credentials)`가 `v242`로 전달하도록 시즌 Build cache miss 시에만 키를 메모리에서 조회한다. 원본 캐시·시즌 정책·Native/GJFO admission 변경 없음. Windows ZIP mandatory source 모듈 포함. Linux는 저장 불가/원래 환경변수 CI만 유지.
- **Verification:** Windows·Linux focused/HTTP/패키지 영수증 확인 전 **PENDING**. 비밀키 비노출·로컬 인증 방화벽·WinCred OS 왕복·일반 서버 Build->기존 내부 수집 전달·미설치 PENDING 유지·Native0을 분리해 시험한다.
- **Remaining:** 사용자가 본인 키로 실제 인터넷 Blizzard+WCL 인증부터 현재 시즌 G/J/F/O READY까지 실행한 원본 영수증은 아직 없음. v242는 현 확장팩 범위가 인증돼도 해당 시즌 활성 레이드 확정은 별도 원본 검증이다. 로그인 계정 단위 Windows API 키 보관과 개인 Windows 컴퓨터 실제 설치도 별도 검증 필요.
- **Efficiency:** 자격증명 확인/상태에는 Network0/Native0; cache hit 시 Windows secret read 안 함. 원본 v216 collector에만 1회 전달, 원본 Wago 정적 캐시와 v344 실 Native64 영수증 재사용. 본 코드로 새로운 SimC 연산은 수행하지 않는다.
