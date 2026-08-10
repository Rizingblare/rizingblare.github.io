# 운영 원장 — 영속

세션보다 오래 유지되지만 진행 중인 작업 단위에 속하는 상태를 다룬다. 예를 들면 사용자의 결정을 기다리는 사안, 배정 근거, 아직 이행하지 못한 알림 의무, 다음 배정에 참고가 되는 사고 이력이다.

현재 해당 역할을 맡은 주체가 갱신한다. 절대 삭제하지 않는다.

**저장소 안에 둔다. 이 부분은 값비싼 시행착오로 배운 원칙이다.** 원본 프로젝트에서는 원장을 임시 디렉터리에 두었다가 런타임 재시작으로 통째로 잃는 일이 두 번 있었다. 그런 위치를 선택하게 되는 논리는 그럴듯하다 — 진행 중인 상태는 저장소 콘텐츠가 아니므로 저장소 밖에 있어야 할 것처럼 보인다. 바로잡아야 할 점은 콘텐츠 유형이 아니라 *영속성 요구 사항*이 저장 위치를 결정한다는 것이다. 다음 세션이 반드시 읽어야 하는 원장은 영속성 요구 사항에 해당한다.

저장소 밖에 두는 것은 영속성 확보 수단이 아니다.

각 원장은 무엇을 의도적으로 제외했는지와 그 이유를 밝히며 시작한다. 그 한 문단이 같은 규칙을 다른 곳에 기록해 두는 것보다 더 큰 역할을 한다.

## English brief

Operating ledgers hold ongoing-unit state that must outlive a session. Durability, rather than content type, determines that they belong inside the repository, where the current role holder updates them and they are never deleted. Each ledger begins by stating what it deliberately excludes and why.
