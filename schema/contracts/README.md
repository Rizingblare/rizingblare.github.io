# 계약

위반하면 실패로 판정하는 규칙이다. 이것은 승격 사다리의 중간 단계다. 기법 메모(위반 개념 없음) → 계약(버전과 범위가 정해짐) → 자동 검사(닫힌 카탈로그에 있는 id) 순으로 승격한다.

각 단계를 서로 구분해 유지한다. 모든 것을 규칙으로 만들면 규칙 집합을 사용할 수 없게 되고, 아무것도 규칙으로 만들지 않으면 검증된 발견 사항이 영원히 권고에 머문다.

권장하는 세부 구분은 계층 헌장, 산출물 형태, 품질 기준, 통제 어휘, 개별 사용자 선호 사항, 운영 정책이며, 어느 것도 필수는 아니다.

원본 프로젝트에서 본떠 쓸 만한 형태가 두 가지 있다.

**선호 사항마다 파일 하나.** 선호 사항에는 진술, 범위, 근거 링크, 그리고 candidate, active, superseded, conflict 중 하나인 상태를 둔다. 공유 문서의 글머리표는 항목별 상태를 담을 수 없다. 편집 과정에서 superseded 관계가 사라지고 conflict 상태를 둘 곳도 없기 때문이다.

**범위 수준은 두 개가 아니라 세 개다.** 이 산출물, 이 산출물 클래스, 전역이다. 지역과 전역만 있으면 "이 클래스에는 참이지만 모든 곳에서 참은 아님"을 둘 곳이 없으므로, 나중에 모순이 생겼을 때 누군가 앞선 규칙을 삭제해야 하고 그 규칙이 옳았던 경우도 함께 사라진다.

## English brief

Contracts are scoped, versioned rules whose violation is a failure, positioned between informal technique notes and automated checks. Keep those promotion stages distinct, store each preference in its own file with evidence and lifecycle status, and use artifact, artifact-class, and global scope levels so contradictions can be represented without erasing valid earlier rules.
