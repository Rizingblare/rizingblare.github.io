# 카탈로그 원자성 루브릭 (atomicity rubric)

문서 작성 전 카탈로그 항목이 지켜야 하는 단위 원칙이다. 2026-08-05 사용자
지시로 확립: **개별 문서 페이지는 특정 개념을 원자 단위로 다루고, 합성 개념과
상위 개념은 별도의 문서 페이지로 구분한다.**

## English brief

Unit principle for the catalog worklist: one document page = one atomic
concept; composite and parent concepts get their own separate pages that
reference their constituent atoms (`atoms` field). Review verdicts:
atomic-ok / split / composite-ok / composite-missing-atoms / reclassify.

## 판정 어휘

- **원자(atomic)**: 더 나누면 독립적으로 설명·시험·참조할 수 없는 단일 개념.
  한 문장 정의가 가능하고, 정의에 다른 미정의 신개념을 2개 이상 끌어오지 않는다.
  예: 각주파수, 나이퀴스트 주파수, 양자화 오차.
- **합성(composite)**: 여러 원자를 조합해야 성립하는 개념·시스템·절차.
  자체 문서를 가진다 — 단, 구성 원자들이 카탈로그에 독립 항목으로 존재해야
  하고, `atoms` 필드에 그 id 목록을 기록한다. 예: PCM(표본화+양자화+부호화),
  SFN(동기화+주파수 재사용+보호구간).
- **상위(taxonomy/layer-model 등)**: 하위 개념들을 묶는 분류·체계.
  합성과 동일하게 자체 문서 + `atoms`(하위 항목 id).

## 검토 판정 5종

| verdict | 의미 | 갱신 동작 |
|---|---|---|
| `atomic-ok` | 원자 기준 부합 | 없음 |
| `split` | atomic 라벨이지만 실제로 복수 개념을 묶음 | kind를 composite 계열로 교정, 구성 원자를 신규 항목으로 추가, `atoms` 기록 |
| `composite-ok` | 합성/상위이며 구성 원자가 이미 모두 존재 | `atoms`에 기존 id 연결만 기록 |
| `composite-missing-atoms` | 합성/상위인데 구성 원자 일부가 카탈로그에 없음 | 누락 원자를 신규 항목으로 추가 + `atoms` 기록 |
| `reclassify` | kind 라벨 오류(내용은 단일 개념이거나 유형 오기) | kind만 교정 |

## 분해 판단 신호

split을 의심할 신호: 제목에 나열·괄호 병기("A와 B", "A·B·C", "A (X→Y→Z)"),
요약이 두 개 이상의 정의를 병렬, "…들", 비교 항목이 각 대상의 정의를 겸함.
반대로 **과분해 금지**: 하나의 개념의 속성·표기·단위·특수경우는 별도 원자가
아니다(예: "ω=2πf"는 각주파수의 속성이지 새 원자가 아님). 시험 출제 단위로
독립 설명이 필요한 것만 원자로 만든다.

## 도메인 특례

- **current-affairs(시사·상식)**: 시점 의존 지식 항목이므로 개념 원자성 대신
  "한 항목 = 한 사건/제도/사실" 기준을 적용한다. 여러 독립 사건을 묶은 항목만
  split 대상.
- **exercise(코딩 추적 등)**: 문제 단위가 곧 문서 단위 — 원자성 검토 대상 아님.
- **regulation**: 조문·기준 하나가 한 항목이면 통과. 복수 제도를 묶으면 split.

## 신규 항목 규칙

- id: 의미 있는 영문 kebab-case 슬러그(기존 예: `angular-frequency`).
  전 도메인에서 유일해야 하며, 동일 개념이 타 도메인에 이미 있으면 새로 만들지
  않고 그 id를 `atoms`에서 참조한다.
- 필수 필드는 기존 스키마 그대로: type/id/title/aliases/status(proposed)/kind/
  profile/summary/primaryDomain/domain(호스트 도메인)/topics/route(null)/url(null).
- `atoms`: 합성·상위 항목에만 두는 선택 필드로, 구성 원자 id의 배열.
  (2026-08-05 스키마 확장 — 차터에 기록)
- **구성 미상 합성**: 합성임은 확실하나 구성 원자를 콘텐츠 없이 확정할 수
  없는 항목(예: 세대별 구성이 다른 코어망)은 `atoms`를 비워 둘 수 있다.
  문서 작성 시점에 반드시 확정한다 — 비워 둔 채 발행하지 않는다.

## 절차

검토는 도메인 단위로 위임하되 **드래프트만 반환**받는다(무번호 초안).
병합·id 충돌 검사·카탈로그 반영·샤드 재빌드(`python3 scripts/build_search.py`)·
게이트는 단일 작성자인 소유 세션이 수행한다.
