# 2026-11-22 P3 v661 — Windows CLI 빌더 ↔ 공개 캐시 연결 (부분 완료)

## 제품 목적·실제 해결 범위
최종 제품은 26개 DPS의 미래 목표 CHMV 절대 rating을 실제 SimC DPS로 최적화한다. v660은 공식 Nightly 또는 검증된 공개 자체 빌드 캐시가 있으면 Windows 단일 ZIP에서 자동 확보·설치할 수 있다. 둘 다 없을 때 `SOURCE_BUILD_REQUIRES_REMOTE_BUILDER`는 여전히 발생한다.
**v661은 신규 공개 원격 요청 브로커를 만들지 않는다.** 기존 v658 신뢰된 격리 브랜치 요청이 이미 발행되었다는 전제하에, 공개 캐시 검증 → HIT 중복 컴파일 생략 / MISS 기존 Windows CLI 컴파일 → v659 4멤버 검증 ZIP 생성 → EXPERIMENTAL prerelease 자동 공개를 연결한다.

## 실제 변경
- `integration_probes/v661_public_simc_cache.py`: v658 요청의 고정 upstream 40 SHA·게임빌드 재사용. 공개 GitHub 태그 GET 1회(최대 300KB); 정확한 404만 MISS로 처리, 기타 TLS/HTTP/리다이렉트/JSON 오류는 차단. GitHub 태그·prerelease·asset URL/이름/크기/상태/SHA256 검증은 v660 `published_candidates` 재사용. 손상된 기존 태그는 덮어쓰거나 무조건 재빌드하지 않음.
- `integration_probes/v661_public_simc_cache.py`: 새 빌드 산출물 `build_receipt.json`, `source_proof.json`, `display_build.txt`, CPack 7z 정확히 네 파일만 ZIP으로 묶고 실제 v659 `inspect_artifact` 검사 후 SHA 확인. 기존 소스/게임빌드/실행파일 provenance 회계 보존.
- `.github/workflows/p3_v658_generic_simc_windows_cli.yml`: 적법한 요청 push에서 캐시 HIT면 checkout/CMake/CPack/업로드/게시 전부 건너뜀. MISS만 원본 SHA 고정 Windows CMake CLI 빌드와 기존 14일 artifact를 실행. 성공 결과는 지속 공개 EXPERIMENTAL 자체 빌드 Release로 등록. 워크플로의 CI 임시 GITHUB_TOKEN에만 `contents: write`; 사용자 PC/PAT/외부 비밀키는 변경 없음.
- `tests/test_p3_v658_generic_simc_win64_build_offline.py`: HIT/MISS/손상 태그 거부, 정상 4멤버 압축, 추가 입력·덮어쓰기 거부와 workflow 연결 회귀.
- 사용자 승인 v653 디자인, v660 제품 ZIP/클라이언트, v193/v659 설치, 시즌 G/J/F/O·L/E/O, 95%·Native·캐시·취소/재개/세션, 주 채팅 소유권은 **변경 없음**.

## 근거·효율
- **신규** [v658/v661 focused #45018158514](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45018158514): Python3.12·3.14 각각 7/7 PASS, FAIL 0, Native DPS 0, 신규 C++ 컴파일 0. [공통 focused #45018158522](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45018158522), [78계약 일관성 #45018158594](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45018158594): SUCCESS. 이 시험은 신규 Windows CACHE_MISS 컴파일 실측이 아님.
- **현재 기존 공개 실측 캐시 재확인:** source `6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7` / Live `12.1.5.70961`, asset SHA256 `8f94209f1b7013da23fca47ada972630d18a371abd0e3d86f491bbad27dec2fd`(GitHub 공개 Release API). 기존 컴파일 [#45007868837](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45007868837), v660 제로베이스·ZIP·제품 HTTP [#45012696519](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45012696519)·[#45012956028](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45012956028)·[#45013234606](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45013234606), v639 Native64는 **역사 영수증 재사용**, 신규 재실행 아님.
- 비용: 요청당 GitHub 공개 API 1회, HIT면 C++ 컴파일·원본 checkout·artifact/Release 중복 업로드 0. MISS일 때만 1회 컴파일 및 공개. 사용자 세션·시즌 정적 캐시·DPS 캐시에는 추가 I/O나 폐기 없음. 외부 인증 실패는 대규모 대체 컴파일 대신 안전하게 차단.

## 남은 첫 접합부와 STOP
**새 패치에서 일반 사용자 PC가 인증 없이 원격 빌드 요청을 내는 브로커는 여전히 미구현.** v661은 이미 운영자가 적법하게 발행한 request push → 성공 산출물 자동 게시만 연결했다. GitHub default branch에서만 동작하는 schedule 또는 인증된 중앙 서비스/브로커를 실제 운영하려면 main/workflow·운영 권한을 별도 사용자 승인받아야 한다. 익명 workflow_dispatch, 사용자 PAT/컴파일러, 무제한 공개 빌드를 도입하지 않는다.
개인 PC v229 첫 장애, 신규 시즌 G/J/F/O READY, 26전문화 E2E는 미확인. 기존 v660 단일 제품 ZIP SHA 및 사용자 UI 변경 0. 공식 `15/78 COMPLETE`는 원장에만 유지, `full_product_e2e=PENDING`. main/v003/Project UI/Work OS/공식 승격·기존 주 제품 개발 소유권 불변.
