---
id: fb-NNNN-<slug>-<YYYYMMDD>
kind: feedback
form: feedback@1
created: <YYYY-MM-DD>
scope: local | recurring
source_locator: <원본 발화의 안정적인 포인터>
source_sha256: <보호된 바이트를 나타내는 64 lowercase hex>
source_byte_count: <보호된 바이트의 UTF-8 바이트 수>
---

# 피드백 — <한 줄 제목>

> 에이전트 요약: 사용자 본인의 말을 보존한다. 이 문서의 가치는 이 문서가
> 해석이 **아니라는** 데 있다. 해석은 이 문서를 인용하는 제안(`proposal`)에서
> 이루어진다. 인용 영역은 바이트 단위로 불변이다. 그 안에서는 줄바꿈을
> 바꾸거나 번역하거나 고치거나 요약하지 않는다.

## 원문

<!-- protected span: begin -->
<사용자의 말을 정확히 옮긴다. 오타를 포함해 어떤 이유로도 이 영역 안을 편집하지
않는다. 인용문에 맥락이 필요하면 영역 밖에 덧붙인다.>
<!-- protected span: end -->

## 맥락

<이 피드백이 어떤 산출물이나 동작에서 비롯되었는지와 그 시점을 적는다. 보호 영역
밖에 작성한다.>

## 즉시 적용한 로컬 수정

<즉시 바로잡은 내용이 있다면 적는다. 로컬 수정만으로 같은 유형의 결함이 다시
발생할 수 있는 피드백까지 종결되는 것은 아니다.>

## 범위 판단

<하나의 산출물에만 적용되는지, 반복되는 유형에 적용되는지, 아니면 규칙을
정당화하는지 적는다. 피드백 하나는 전역 규칙이 아니다. 승격에 어떤 추가 근거가
필요한지 밝힌다. 승격은 여기서 직접 이루어지지 않고 제안을 거친다.>

## 이 범주의 규칙

보호 영역 안의 사용자 말은 **바이트 단위로 보존**한다. 명백한 실수를 고치려는
경우조차 번역하거나 요약하거나 정규화해서는 안 된다. 사용자 말과 그것에 대한
해석 사이의 구분은 제목 수준이 아니라 바이트 수준에 있다. `source_locator`,
`source_sha256`, `source_byte_count`는 그 영역을 원본 발화에 결속하고, 두 정확한
표식 사이의 바이트와 일치하는지 검사된다.

보호하지 않은 정정은 선의에서조차 에이전트가 이미 믿고 있던 내용에 맞게
바꿔 쓰이게 된다. 검토할 때는 이런 압축이 드러나지 않는다. 요약은 자연스러워
보이고, 사용자가 고른 특정 단어, 즉 실제 제약을 담은 바로 그 단어는 사라진다.
바이트 보존만이 나중에 정정을 다시 읽고 그 뜻이 시스템이 내린 결론과 달랐음을
발견할 수 있게 한다.

**피드백 하나는 규칙이 아니다.** 산출물 하나에 대한 정정은 해당 산출물에
한정된 기록으로 남는다. 서로 *다른* 산출물에서 같은 선호가 반복되면 후보가 될
수 있으며, 승격은 제안(`proposal`)을 거쳐 명시적으로 승인받아야 한다.

## English brief

This template preserves the user's exact words inside a byte-immutable protected span and binds them to `source_locator`, `source_sha256`, and `source_byte_count`. Content between the exact begin and end markers must never be reflowed, translated, corrected, summarized, or normalized. A single feedback record remains local; only recurrence across different artifacts may become a candidate, and promotion requires a proposal and explicit approval.
