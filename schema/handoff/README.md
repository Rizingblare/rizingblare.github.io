# Handoff — 휘발성 snapshot

handover 하나마다 snapshot 하나를 둔다. 나가는 session이 작성하고 **들어오는
session이 삭제한다**. 보관하지 않는다. 삭제한다.

takeover 사실은 successor의 closing receipt에 한 줄로만 남긴다. 무엇을, 언제,
어느 commit에서 인계받았는지를 기록한다. 이력 관리는 version control의 몫이다.

snapshot 삭제 commit과 entry pointer 제거는 **같은 commit**이어야 한다. 삭제된
문서를 가리키는 pointer는 link check에서 실패하며, 그 실패가 이 규칙을 강제한다.
둘을 나누면 이미 깨진 것으로 알려진 상태를 배포하게 된다.

takeover 뒤에도 snapshot이 남아 있으면 진행 중인 작업으로 읽힌다. 이 surface는
"현재 진행 중인 것이 무엇인가"에 답하기 위해 scan되는데, 이미 소비한 snapshot은
그 질문에 잘못 답한다. 이후 session이 이를 열면 두 unit 전의 세계 상태에서 작업하게
된다.

**여기에 두지 않는 것.** query로 다시 만들 수 있는 모든 것, 즉 `worktree` 목록,
`branch` 상태, `task` 상태, `commit` 기록은 두지 않는다. handover보다 오래 남아야
하는 것도 두지 않는다. 먼저 canonical home으로 보낸 뒤 그것을 가리킨다. 휘발성
문서에 둔 영구 지식은 successor가 지시대로 snapshot을 소비하고 삭제하는 올바른
동작에 의해 파괴된다.

이름에는 unit별 `counter`, `slug`, `date`만 있으면 된다. 의도적으로
`global sequence`를 사용하지 않는다. 소비 과정에서 이전 entry가 삭제되므로
`global sequence`에는 영구적인 빈자리가 생기며, 필요하지 않은 문서에
single-writer 발급 규율까지 끌어들이게 된다.

## English brief

Each handover uses one volatile snapshot written by the outgoing session and deleted by
the incoming session after takeover. The snapshot deletion and entry-pointer removal must
land in the same commit, while durable knowledge belongs in its canonical home and only a
closing-receipt line records the takeover. Snapshot names use only a per-unit counter, slug,
and date rather than a global sequence.
