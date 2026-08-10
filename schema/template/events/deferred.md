---
id: def-NNNN-<slug>-<YYYYMMDD>
kind: deferred
form: deferred@1
created: <YYYY-MM-DD>
status: todo | done
severity: blocking | quality | polish
---

# 보류 항목 — <한 줄 제목>

> 에이전트 요약: 실재하지만 지금 처리하지 않는 정정 또는 개선 사항이다. 이 대기열은
> "지금 아님"이 "영원히 안 함"이나 즉각적인 방해가 되지 않게 한다. 항목은 절대
> 삭제하지 않으며, 완료된 항목은 처리 결과와 함께 `done` 집합으로 옮긴다.

## 잘못되었거나 빠진 내용

<처음 발견하지 않은 사람도 조치할 수 있을 만큼 구체적으로 적는다.>

## 위치

<경로를 적는다. 고정된 목록이 아니라면 영향받는 집합을 찾는 선택자를 적는다.>

## 보류한 이유

<무엇을 기다리느라 막혔는지 또는 이를 발견한 작업 단위의 범위 밖이었던 이유를 적는다.>

## 처리 결과

<완료할 때 채운다. 수행한 작업과 해당 커밋을 적거나, 조치 없이 닫았다면 그 이유를 적는다.>

## 이 범주의 규칙

항목은 **절대 삭제하지 않는다.** 미완료 디렉터리에서 완료 디렉터리로 옮긴다.

명시적인 보류 상태가 없으면 "지금 아님"과 "아니오"를 구분할 수 없다. 같은 결함이 다시 보고되고, 사용자는 자신의 요청 가운데 무엇이 누락되었는지 기억해야 하며, 미처리 목록은 아무도 버리기로 결정하지 않았는데도 사라진다.

이 대기열 옆 수신함에는 의도적으로 스키마가 없다. 제목과 문장 하나면 충분하다. 에이전트는 그 안의 내용을 대기열 항목으로 바꾸고 수신함을 비운다. 포착할 때의 마찰이 미처리 목록을 죽이는 원인이다.

## English brief

A deferred record preserves a real correction or improvement that is intentionally outside the current unit. Entries are never deleted; completed items move to the `done` set with their disposition recorded.
