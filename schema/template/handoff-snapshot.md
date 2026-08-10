---
id: handoff-NN-<unit-slug>-<YYYYMMDD>
kind: handoff-snapshot
form: handoff-snapshot@1
created: <YYYY-MM-DD>
unit: <작업 단위>
---

# 인계 — <작업 단위>

> 에이전트 요약: 휘발성 문서다. 후속 담당자가 인수하면 이 문서를 삭제하고 종료 실행
> 증빙에 한 줄로 기록한다. 인계와 함께 수명이 끝나는 내용만 적는다. 조회로 복구할 수
> 있는 내용은 여기 두지 않는다. 인계 뒤에도 남아야 하는 내용은 각자의 정본 위치에 두고
> 아래 포인터 절에서 참조한다.

## 종료 상태

<이 작업 단위가 끝나는 커밋, 검증기 결과, 반영되지 않은 것이 있는지를 적는다.>

## 재개 방법

<후속 담당자가 수행할 첫 번째 구체적 조치를 적는다. 작업 요약이 아니라 다음 단계다.>

## 다음 작업 단위의 범위

<후속 담당자가 맡는 것과 명시적으로 맡지 않는 것을 적는다.>

## 승계한 의무

<이 작업 단위가 전달해야 했지만 전달하지 못한 알림을 포함해, 후속 담당자가 달리 알 수 없는 필수 조치를 적는다.>

## 대기 중인 사항

<이 작업이 기다리는 결정, 승인 또는 다른 작업 단위를 적는다.>

## 포인터

<인계 뒤에도 남는 모든 항목의 정본 위치를 적는다. 대기열 항목, 여기서 수립한 상시 규칙, 실행 증빙이 해당된다. 포인터만 적고 내용을 다시 서술하지 않는다. 그렇지 않으면 이 파일을 삭제할 때 정보가 사라진다.>

## English brief

A handoff snapshot is volatile and contains only the state needed for the successor's first action. Durable information stays in canonical locations referenced here, and the successor deletes the snapshot after takeover while recording that cleanup.
