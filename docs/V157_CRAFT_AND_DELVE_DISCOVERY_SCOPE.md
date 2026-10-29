# v157 — 새 시즌 제작법 정보의 독립 수집

이 기능은 **빈 데이터에서 시작**한다. 어떠한 기존 WEQUIP/v047/v057/
외부 제작 장비 목록이나 과거 시즌 아이템 ID도 읽지 않는다.

1. Blizzard `profession/index`에서 전문기술 목록을 발견한다.
2. 선택된 profession의 `skill_tiers`를 받은 뒤 **해당 확장팩 명칭**으로
   정확히 일치하는 tier 하나를 찾는다. 임의 ID나 최고 ID를 추정하지 않는다.
3. 공식 `skill-tier`가 제공하는 **전체 recipe ID/이름 목록**을 기록한다.
4. 임의 기존 아이템 ID가 아닌 **API에서 받은 recipe ID 정렬 순서로 최대
   3개** 상세 조회하고 명시된 `crafted_item(s)` ID를 기록한다.
5. Blizzard Recipe 상세에서 출력 ID가 없으면 UNKNOWN으로 남긴다.
   레시피 이름과 비슷한 아이템이 공식 API에 있더라도 직접 제작 연결로
   확정하지 않는다.

현재 단계는 데이터 수집 연결의 bounded 파일럿이다. 이후 전체 profession/tier
수집을 구현할 때는 명시적 호출 예산·지속적인 cursor/checkpoint·실패
재개가 필요하며, 기본 사용자 최적화 엔진의 실행 선행조건으로 만들지 않는다.

GitHub Actions의 실제 API 작업은 `SIMC_ALLOW_SEASON_API_PROBE=true`와
명시 `[api-probe]` 커밋 태그가 **모두** 필요하다. 일반 코드 변경은
오프라인 시험만 실행한다. Native SimC 실행 0회.

구렁 보상은 레시피나 보스 저널 데이터의 의미와 다르며, 별도
공식 보상 ID 출처가 확인될 때까지 획득 목록은 UNKNOWN이다.
