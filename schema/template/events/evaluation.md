---
id: eval-NNNN-<slug>-<YYYYMMDD>
kind: evaluation
form: evaluation@1
created: <YYYY-MM-DD>
evaluates: <proposal id>
verdict: pass | fail | partial
---

# 평가 — <한 줄 제목>

> 에이전트 요약: 작업 시작 전에 동결된 기준에 결속된 판정이다. 이것은 결정을
> 제한하며, 평가 없이는 어떤 결정도 적용되지 않는다. 기준이 잘못되었다고 밝혀지면
> 그 사실을 여기 기록할 발견 사항으로 다루며, 기준을 다시 쓰는 허가로 삼지 않는다.

## 동결 당시의 기준

<제안의 동결된 기준을 그대로 재현한다. 여기 재현한 내용이 제안과 다르면 그 자체가 결함이며 판정을 막는다.>

## 기준별 결과

| # | 기준 | 결과 | 근거 |
|---|---|---|---|
| 1 | | pass / fail | <측정 방법> |

## 판정

<pass / fail / partial과 그 판정이 무엇을 제한하는지 적는다. partial 판정은 진행할 수 있는 부분과 진행할 수 없는 부분을 명시해야 한다.>

## 발견한 기준 결함

<기준을 측정할 수 없거나, 모호하거나, 쟁점에서 벗어났음이 드러났다면 기록한다. 이 내용은 다음 제안의 입력이며 현재 판정을 바꾸지 않는다.>

## 이 범주의 규칙

판정은 미리 등록된 기준, 즉 제안의 동결된 절이나 시험 자료 식별자에 **참조로** 결속된다. 기준을 여기서 다시 진술하지 않는다. 다시 진술한 기준은 결과 쪽으로 표류한다.

평가 이벤트는 판정이 결론 난 뒤에만 발급하므로 `verdict`는 언제나 `pass`, `fail`, `partial` 중 하나다. 진행 중인 평가 상태는 현재 단위의 운영 대장이나 인계 상태에 속하며 이벤트 기록이 아니다. 이벤트가 발급된 뒤에는 `evaluates` 참조를 변경할 수 없다.

어떤 시험 자료를 실행할지는 **선언이 아니라 결속**으로 결정한다. 작성자는 변경이 무엇을 건드리는지는 알기 때문에 그것을 기술한다. 다시 검증해야 할 대상은 장치가 파생하며, 작성자는 대개 그 전부를 알지 못한다. 작성자에게 대상을 선언하게 하면 이미 염두에 둔 의존 대상만 적는다. 바로 그 집합은 애초에 누락 위험이 없던 대상이다.

## English brief

An evaluation records a concluded verdict against criteria frozen before the work began. It cannot rewrite those criteria, and any defect in them becomes input to a later proposal rather than a change to the current verdict.
