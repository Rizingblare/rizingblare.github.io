---
id: dec-NNNN-<slug>-<YYYYMMDD>
kind: decision
form: decision@1
created: <YYYY-MM-DD>
status: active | rolled-back | superseded-by <id>
gated_by: <evaluation id>
targets: [<이 결정이 관할하는 대상을 지정하는 선택자 — 시험 자료 선택을 구동함>]
required_checks: [<이 결정이 필수로 만드는 검사 id>]
# 다음 두 키 중 정확히 하나만 허용된다.
verification_receipt: <observation id>
# verification_not_applicable: <구체적인 사유>
---

# 결정 — <한 줄 제목>

> 에이전트 요약: 결과만 기록한다. 추론은 제안에, 판정은 평가에, 경과는 관찰에
> 속한다. 결정을 뒤집기 위해 이 문서를 수정하지 않는다. 되돌릴 때는 상태 변경과
> 새 결정을 함께 남겨 한때 참이었던 내용의 기록을 보존한다.

## 결정한 내용

<다른 문서를 읽지 않고도 적용할 수 있도록 결정 자체를 적는다.>

## 범위

<이 결정이 관할하는 것과 의도적으로 관할하지 않는 것을 적는다.>

## 적용 위치

<결정을 적용한 커밋과 변경한 정본 문서를 적는다. 적용 기록이 없는 결정은 효력이 없다.>

## 철회

<이 결정을 롤백하거나 다른 결정으로 대체할 때 상태가 어떻게 바뀌는지와 그 시점에 다시 검사해야 할 것을 적는다.>

## 이 범주의 규칙

**결과만 기록한다.** 추론 서사는 상위 제안에 두고 링크하며 아래로 복사하지 않는다. 결정에 추론을 직접 담으면 결정을 대체할 때 그 추론도 다시 써야 하며, 증거 사슬은 대체된 결정이 당시 타당해 보인 이유를 보여 줄 능력을 잃는다.

롤백과 대체는 **이 문서의 상태 전이**로 표현한다. 삭제하거나 별도의 정정 문서로 만들지 않는다.

영향받는 대상은 직관으로 선언하지 않고 실제 차이와 레지스트리에서 파생한다. 직관으로 만든 영향 목록은 작성자가 건드린 사실을 잊은 파일을 어김없이 누락한다.

검증 실행 증빙 식별자와 검증이 적용되지 않는 명시적 사유 중 **정확히 하나만** 둔다. 둘 다 없으면 오류이며, 검증기는 인용한 실행 증빙이 존재하는지 독립적으로 확인한다. 출구를 하나가 아니라 둘로 두는 이유는 누구도 정직하게 통과할 수 없는 게이트는 우회되기 때문이다. 실제로 검증이 적용되지 않는 변경은 그렇지 않으면 실행을 꾸며내야 한다.

## English brief

A decision records only the outcome and is gated by exactly one concluded evaluation. Reversal is represented as a status transition plus a new decision, while affected targets and verification evidence are derived and checked independently.
