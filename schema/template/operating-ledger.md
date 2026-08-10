---
id: <unit>-ledger
kind: operating-ledger
form: operating-ledger@1
unit: <작업 단위 또는 역할>
owner: <현재 보유자의 세션 식별자>
updated: <YYYY-MM-DD>
---

# 운영 대장 — <작업 단위 또는 역할>

> 에이전트 요약: 지속성 문서다. 현재 담당 세션이 갱신하며 세션 교체 뒤에도 남는다.
> 저장소 안에 보관한다. 임시 디렉터리에 둔 대장은 다음 실행 환경 재시작 때 사라지며,
> 그 손실은 드러나지 않는다.

**의도적으로 제외한 항목**: 작업 목록, 작업 트리 상태, 창 또는 터미널 핸들, 버전 이력. 모두 조회로 복구할 수 있으며, 복구 가능한 상태를 중복하면 두 정본이 서로 어긋나기 시작한다. 담당 교체 스냅샷은 별도의 휘발성 파일이다.

## 1. 사용자 결정을 기다리는 항목

<이 대기열은 어떤 단일 세션보다 오래 남는다. 항목이 해결되어도 삭제하지 말고 처리 결과를 기록해 행을 유지한다.>

## 2. 아직 배정되지 않은 제안

## 3. 종료 검증 게이트

<작업 단위의 작업 공간을 철거하기 전에 확인해야 할 것을 적는다.>

## 4. 이 대장을 열어 둔 동안 수립한 상시 규칙

<아직 정본 계약으로 승격되지 않은 규칙을 적는다. 규칙이 안정화되면 승격하고 이 항목을 포인터로 교체한다.>

## English brief

An operating ledger is persistent state maintained by the current session across session turnover. It excludes queryable runtime state and retains unresolved decisions, unassigned proposals, closure checks, and standing rules until they move to canonical homes.
