# 제0장 — 개요, 등급, 도입 경로

이 명세는 여러 세션에 걸쳐, 그리고 필요할 때는 병렬로 git 저장소에서
작업하는 AI agent를 위한 운영 harness를 설명한다. 이 명세는 domain과
무관하다. 저장소가 무엇을 위한 것인지는 전혀 다루지 않는다.

세 개 장에 걸쳐 서른 개 메커니즘을 명세한다. **이 모두를 도입하라는 뜻이
아니다.** 이 장에서는 처음 시작할 세 가지, 등급 label을 읽는 법, 그리고
어떤 메커니즘이 어떤 다른 메커니즘 없이는 무용한지를 설명한다.

## 한 문장으로 요약하면

Agent는 유능하고 잘 잊는다. harness는 기억하고, 검사하고, 거부하는 시스템의
일부다.

## 이것이 아닌 것

이것은 framework가 아니다. 설치할 것도, 의존할 package도, 추적할 version도
없다. 메커니즘을 저장소에 복사하면 유지 관리 책임까지 포함하여 그것은
여러분의 것이 된다.

이것은 model output을 개선하지 않는다. 여기 있는 모든 메커니즘은 유능한
agent라도 session 경계에서 상태를 잃고, 두 번째 agent와 충돌하고, 아무것도
검사하지 않는 단계를 건너뛸 수 있다고 전제한다.

## 출처와 표본 크기

이 harness는 agent가 주된 committer로 수개월 운영된 한 저장소에서 추출했다.
**표본은 하나다.** 메커니즘의 등급이 관찰된 단일 실패에 근거하는 경우에는
본문에서 이를 명시하므로, 그 실패가 여러분의 맥락에서도 일어날 수 있는지
판단할 수 있다. 횟수, 임계값, category 체계는 부수적인 것으로 보고, 실패
양상은 발견 사항으로 보라.

## 등급

모든 메커니즘에는 정확히 하나의 등급이 있다. 등급은 허용되는 자유의 정도를
알려 주며, 본문은 그 이유를 설명한다.

| 등급 | 의미 | 할 수 있는 일 |
|---|---|---|
| `CORE` | 제거하면 harness가 작동하지 않는다. | 형태는 바꿀 수 있지만 속성은 바꾸지 않는다. 각 CORE 메커니즘은 대체물이 보존해야 할 속성을 열거한다. |
| `DEFAULT` | 이 특정 형태를 뒷받침하는 근거가 있으며, 다른 형태도 작동할 수 있다. | 명시된 제약에 맞춰 자유롭게 대체한다. |
| `PARAMETER` | 프로젝트가 정하는 값이다. | 값을 정한다. 본문은 source 프로젝트의 값, 그 근거, 양쪽 방향의 trade-off를 제시한다. |
| `OPTIONAL` | 명시된 사전 조건이 성립할 때만 적용한다. | 사전 조건이 거짓이면 생략한다. 생략하기 전에 사전 조건을 확인한다. |

등급은 메커니즘에 적용되지만, CORE 메커니즘의 개별 부분이 PARAMETER인
경우가 흔하다. 예를 들면 orchestration 메커니즘 안의 report 길이 상한이나
numbering discipline 안의 자릿수다. 본문에서는 이를 inline으로 표시한다.

## 전체 목록

**A — 계층과 구조** (제1장)

| | 메커니즘 | 등급 |
|---|---|---|
| A1 | 출처 기반 계층 분리 | CORE |
| A2 | 구조 선언 registry | CORE |
| A3 | 계층 추가 또는 이동 gate | CORE |
| A4 | Manifest와 generated-view 규율 | CORE |

**B — 근거와 자기 개선** (제1장)

| | 메커니즘 | 등급 |
|---|---|---|
| B1 | Event chain | CORE (6분할: DEFAULT) |
| B2 | Numbering discipline | CORE (naming 형태: PARAMETER) |
| B3 | 승격 사다리와 preference lifecycle | CORE (3단계 scope: DEFAULT) |
| B4 | 문서 재구축 임계값 | DEFAULT (임계값: PARAMETER) |

**C — 병렬 작업과 세션** (제2장)

| | 메커니즘 | 등급 |
|---|---|---|
| C1 | 지속적 통합을 수반하는 dedicated worktree 격리 | CORE (선형 history: PARAMETER) |
| C2 | 직렬화된 identifier 발급 critical section | CORE |
| C3 | 작업 unit별 session 경계와 handoff 기준 | CORE |
| C4 | Handoff 수명 분리 | CORE |
| C5 | Commit 규율 | DEFAULT (message 형태: PARAMETER) |

**D — Orchestration** (제2장)

| | 메커니즘 | 등급 |
|---|---|---|
| D1 | 세 role 분리와 orchestration 불변 조건 | CORE (role 수: DEFAULT) |
| D2 | Coordination runtime capability slot | slot 명세로서는 CORE; 구현은 OPTIONAL |
| D3 | 승인 경계 | CORE (질문 수: PARAMETER) |
| D4 | Delegation 규율 | CORE (tier map: DEFAULT) |

**E — 강제와 검증** (제3장)

| | 메커니즘 | 등급 |
|---|---|---|
| E1 | Producer wiring 의무 | CORE |
| E2 | Check catalogue governance | CORE |
| E3 | Regression fixture gate | CORE |
| E4 | 닫힌 frontmatter schema | DEFAULT |
| E5 | Protected span | CORE (bulk substitution: OPTIONAL) |

**F — 절차와 onboarding** (제3장)

| | 메커니즘 | 등급 |
|---|---|---|
| F1 | Canonical procedure에서 adapter 생성 | CORE |
| F2 | Trigger로 routing되는 절차 | DEFAULT |
| F3 | Onboarding 규율과 doc-gap loop | DEFAULT |
| F4 | Volatile workspace 계층 | OPTIONAL |
| F5 | Profile 조합 | OPTIONAL |
| F6 | Tool entry point: canon 하나, 얇은 link | CORE |
| F7 | 작업 언어 정책 | OPTIONAL |
| F8 | 사용자 보고 | DEFAULT |

## 의존성 그래프

메커니즘은 서로 독립적인 부품이 아니다. 가치는 wiring에서 나오며, 의존하는
대상 없이 도입한 메커니즘은 대개 아예 없는 것보다 나쁘다. 비용은 같으면서
덜 강제하므로, 모두에게 harness가 요식 행위일 뿐이라고 가르치기 때문이다.

하중을 지탱하는 edge는 다음과 같다.

```
A1 ──→ A2 ──→ A4 ──→ F1        structure becomes machine-readable, then generated
        │      │
        │      └──→ F2, F3      routing tables and manifests are generated views
        │
        ├──→ A3                 the gate protects what the registry declares
        │
        └──→ E1 ←── E2 ──→ E3   checks exist, run at a defined moment, and re-run
              ▲      ▲           when a contract changes
              │      │
B1 ──→ B2 ────┘      │          numbered records need a detection point
 │      │            │
 │      └──→ C2      │          issuing under isolation needs a critical section
 │           ▲       │
 │      C1 ──┘       │          isolation is what creates the collision
 │       │           │
 │       ├──→ C5                commit hygiene inside that isolation
 │       │                      (C1 owns integration, C5 owns the commit)
 │       ├──→ C3 ──→ C4         session boundary, then handoff lifetimes
 │       │     │      │
 │       └─────┴──→ D1 ──→ D2   orchestration sits on isolation and boundaries
 │                   │
 ├──→ B3 ──→ D3 ─────┘          approval needs evidence; orchestration routes it
 │     │
 │     └──→ E2                  a promoted rule terminates in a governed check
 │
 └──→ E5                        verbatim records are what protection protects
```

사람 및 tool을 향하는 edge는 두 번째의 더 작은 그래프를 이룬다. 도입자가
건너뛰는 절반이기 때문에, 그리고 그 edge 가운데 어느 것도 tree로 되돌아가지
않아 이것이 누락되어도 tree 안에서는 정확히 아무것도 실패하지 않기 때문에
따로 그렸다.

```
D1 ──→ D4 ──→ F6        delegation is orchestration one scale down; the tier
 │             │        NAMES live in each tool's own entry file
 │             │
 │             └──→ F7  language is a property of the files a tool loads
 │
 └──→ F8 ←── B1         what reaches the person, versus what the repository
                        remembers — same facts, different readers, both needed
```

**두 diagram은 하중을 지탱하는 edge만 보여 주며, 어느 diagram도 도입
checklist가 아니다.** 각 메커니즘 자체의 "의존 대상 / 없으면 망가지는 것
(Depends on / breaks without)" section은 여기 선으로 그린 것보다 길며,
그것이 정본이다. C5는 C3, B1, B3,
F4, F6도 지목하고, F7은 E1, E4, E5도 지목한다. 그래프를 전체 사전 조건
목록으로 읽으면, 메커니즘 자체의 본문이 없으면 망가진다고 말하는 무언가를
빼고 그 메커니즘을 설치하게 된다. 그래프는 형태를 보기 위한 것이고,
section은 도입을 위한 것이다.

도입자가 가장 자주 끊는 세 edge를 읽어 보라.

- **E1은 그 무엇의 downstream도 아니며 모든 것의 upstream이다.** A2의
  registry check, A4의 drift check, E2의 전체 catalogue, E3의 receipt check,
  F1의 sync check는 각각 강제 방식으로 "check가 validator run에 wiring되어
  있다"고 명시한다. 그 문장은 E1에 관한 주장이다. 그것 없이는 이 모두가
  관례에 불과하다.
- **B1에 B3가 없으면 문서 보관함일 뿐이다.** Evidence chain에는 규칙이 되지
  않는 record가 쌓인다. Agent는 그 실수에 관한 observation이 folder에
  늘어나는 동안 같은 실수를 계속한다.
- **B3에 B1이 없으면 단언일 뿐이다.** 근거 흔적이 없는 승격은 가장 최근에
  주장한 사람이 이기는 것으로 축소되며, 그것이 바로 이 사다리가 막기 위해
  존재하는 실패다.

## 최소 실행 가능 집합: A1 + A2 + E1

여기서 시작하라. Event chain이나 orchestration부터 시작하지 말라.

- **A1** — 최상위 directory를 content의 출처에 따라 분리한다. 즉 immutable
  input, derived material, generated output, operating contract로 나눈다.
- **A2** — 하나의 file이 어떤 path가 존재하며 각각 무엇을 위한 것인지
  선언한다. 어느 declaration에도 resolve되지 않는 tracked path는 hard
  failure다.
- **E1** — artifact를 만드는 모든 절차는 commit 전에 check를 실행하며,
  실패 branch까지 명시한 written step으로 이를 둔다.

A1은 무엇이 참인지 말한다. A2는 이를 machine-readable하게 만든다. E1은
machine을 실행시킨다. 셋 중 둘만 있으면 부패한다. E1 없는 A1과 A2는 아무도
검사하지 않는 registry이고, A2 없는 A1과 E1은 명세가 없는 checker이며, A1
없는 A2와 E1은 아무 의미가 없는 filing scheme을 강제한다.

이 셋이 자리 잡으면 이후의 모든 메커니즘에 연결할 곳이 생긴다.

이 명세와 함께 제공되는 skeleton에는 A2와 E1이 이미 실행 중이다. registry는
전체 tree를 선언하고, 하나의 gate command가 wiring되어 있으며 green 상태다.
A1은 의도적으로 반쯤 구축된 채 제공된다. operating-contract 계층은 있지만
content 계층은 없는데, 프로젝트가 이들 중 무엇을 가지는지는 이 harness가
아니라 그 프로젝트의 속성이기 때문이다. 계층 하나를 만드는 일은 하나의
commit에서 directory, charter, registry declaration을 함께 추가하는 것이다.
그 tree의 나머지는 모두 placeholder다. **필요하지 않은 것은 강제되지 않은
채로 두지 말고 삭제하라.** 작성되어 있지만 한 번도 검사되지 않는 규칙은
그것을 읽는 모든 agent에게 여기 규칙이 장식에 불과하다고 가르치며, 그
교훈을 되돌리는 데는 큰 비용이 든다.

## 증상별로 다음에 추가할 것

전체 목록 순서로 도입하지 말라. 실제로 겪는 문제에 맞춰 도입하라.

| 잘못되고 있는 것 | 추가할 것 |
|---|---|
| Session 경계에서 작업을 잃거나 다시 도출한다 | C3, 그다음 C4 |
| 두 agent가 충돌한다 — 같은 file, 같은 identifier | C1, C2, 그다음 D1 |
| 규칙을 작성하고도 무시한다 | E2, 그다음 E3 |
| Index와 generated file이 stale하거나 hand-edit된다 | A4, 그다음 F1 |
| 같은 correction을 계속 다시 논쟁한다 | B1, 그다음 B3 |
| 문서를 계속 patch해서 아무도 읽을 수 없다 | B4 |
| Agent가 이미 존재하는 절차를 다시 만들어 낸다 | F2 |
| Newcomer가 저장소에서 할 수 있는 일을 찾지 못한다 | F3 |
| Mechanical rename이 quoted text를 손상했다 | E5 (다음 bulk edit 뒤가 아니라 전에 추가한다) |
| History가 fix trail처럼 보이고, push가 누군가를 놀라게 했다 | C5 |
| Delegated work의 결과가 그럴듯하지만 틀리다 | D4 |
| 두 tool이 서로 다른 version의 규칙을 따르고 있다 | F6 |
| Agent가 실제로 지난 turn에 한 일을 알 수 없다 | F8 |
| 저장소가 영어로 작동하지 않는다 | F7 |

**두 개의 축이 있지만 도입자는 하나만 본다.** 전체 목록을 다시 읽고 A, B,
C, E는 path, record, branch, check 등 *저장소를 조작하는 방법*에 관한 것이고,
D, F6, F7, F8은 *agent가 사람 및 다른 tool을 대하는 방법*에 관한 것임을
주목하라. 첫 번째 축은 그 실패가 tree에 눈에 보이는 손상을 남기기 때문에
도입된다. 두 번째 축은 조용히 실패한다. 전달된 승인, 아무도 검증할 수 없는
delegated report, 한 tool의 instruction file에만 있고 다른 tool에는 없는
규칙이 그 예다. 첫 번째 축만 있는 harness는 깨끗한 저장소를 운영하면서도
그 소유자를 놀라게 한다.

이 중 둘은 증상이 나타나기 *전에* 추가할 가치가 있다. 증상 자체가 손상이기
때문이다. **E5**는 다시 생성할 수 없는 text를 보호한다. 그 실패는 조용하고
영구적이다. **C2**는 어느 per-workspace check도 발견할 수 없는
identifier collision을 방지한다. 이를 알아차릴 때쯤이면 reference가 이미
퍼진 뒤다.

## 되풀이되는 원칙

네 가지 발상은 여러 메커니즘에 등장한다. 이를 알아보면 여러 메커니즘을
구현하는 대신 하나의 pattern을 여러 번 구현할 수 있다.

**부재는 통과가 아니라 실패다.** 선언되지 않은 path는 실패한다. Judgment
contract가 없는 manifest는 실패한다. 어떤 classification rule과도 일치하지
않는 문서는 실패한다. Manifest file 누락은 fail-open hole이므로, 이 file은
count가 0인 header와 함께 유지한다. 이 harness를 warning으로 구현하는
도입자는 한 번도 실패하지 않으면서 부패하는 version을 만든다.

**하나의 canonical source, 기계적 생성, drift check.** A4는 사람이 소유하는
file 안의 region에 이를 적용하고, F1은 file 전체에 적용한다. 불변 조건은
같다. generated 대상은 결코 edit point가 아니고, generator는 idempotent하며,
drift check가 wiring되어 있다.

**성공 return은 effect의 근거가 아니다.** 수락됐지만 전달되지 않은 message.
수락됐지만 버려진 model argument. 전달됐지만 읽히지 않은 report. Disposition이
틀렸는데도 통과하는 registration. Return value를 신뢰할 수 없는 곳마다
메커니즘은 독립적인 confirmation path를 붙인다.

**금지된 것을 묻지 말고 허용된 것을 물어라.** 이 harness 자체 구현에 대한
adversarial review에서 발견한 모든 결함은 같은 실수였다. 나쁜 shape를
열거하는 guard는 하나를 놓쳤다. 회피 기법마다 pattern 하나를 둔 scrubber는
일곱 번째 기법을 만났다. Containment test는 질문이 path 집합에 관한 것인데
path string을 비교했다. 올바른 keyword를 아는 near-miss probe는 keyword
하나의 오타를 보지 못했다. 거부 대상을 열거하면 항상 항목 하나가 부족한
목록이 된다. 가능하면 통과하는 단 하나의 shape를 명시하고 나머지를 모두
거부하라. 그리고 두 component가 같은 것을 판단한다면 같은 code를 통해
질문하게 하라. 서로 다르게 판단하는 두 규칙은 어느 한 규칙만 있는 것보다
나쁘기 때문이다.

**정본을 공유하지 않는 두 방어선.** Registry는 disposition을 선언하고,
registry를 보지 않는 invariant layer는 어쨌든 distribution을 gate한다.
Identifier를 발급하는 session은 collision을 scan하고, sweep은 바깥에서 다시
scan한다. 각각은 상대가 구조적으로 발견할 수 없는 것을 발견한다.

## Blank form은 schema가 아니라 출발점이다

한 가지 경고는 어느 한 메커니즘보다 여기에 두는 편이 맞다. 이 kit에서 어떤
것이든 복사하는 순간, 그리고 어떤 메커니즘도 도입하기 전에 적용되기
때문이다.

**이 kit의 form은 제안이다. 여러분 저장소의 contract가 정본이다.** 둘은
조용히 불일치한다. 잘못된 shape로 작성된 문서도 여전히 well-formed이고,
읽을 수 있고, 사람이 보기에는 명백히 옳다. 불일치는 check가 읽는 field에만
존재하며, check만이 이를 보고한다. 그러므로 이 form 가운데 하나를 처음
사용할 때는, 그 shape가 수십 개 문서에 퍼진 뒤가 아니라 commit하기 *전에*
그 결과를 여러분의 check로 검사하라.

이는 F6의 반대 방향이다. F6은 tool에 특화된 content가 canon에 들어가지
않도록 "다른 tool에서도 이것이 여전히 참일까?"라고 묻는다. 여기서 실패는
반대 방향으로 진행된다. tool 및 저장소와 무관하게 작성된 content가 그보다
구체적인 canonical contract를 대체하며, 아무 signal 없이 그렇게 한다.

두 방향 모두 관찰됐다. Source 프로젝트에서 agent 하나가 이 kit의 generic
form을 사용해 record draft를 만들고 저장소 자체 contract와 frontmatter를
diff하지 않은 채 identifier를 발급했다. 그 결과는 validation failure 16개와
함께 반영됐다. 나중에는 반대 방향으로, 이 kit 자체의 blank form 하나가
*recipient*라면 붙일 이름으로 명명됐다는 이유만으로 host 저장소의 check
catalogue와 충돌했다. Form은 destination에는 올바르고 저장되어 있던 tree에는
잘못됐다. 어느 쪽도 form의 결함은 아니었다. 둘 다 같은 실수였다. 특정
contract가 이미 관할하는 곳에 generic shape를 사용한 것이다.

여기서 나오는 규칙은 짧다. **Form을 도입한 뒤 곧바로 여러분의 check가 이를
판단하게 하라.** 아직 check가 없다면 먼저 A2와 E1을 도입하고 돌아오라.

## 메커니즘 entry 읽는 법

모든 entry에는 똑같은 여섯 부분이 있다.

1. **등급 줄(Tier line)** — 등급과 그 이유를 설명하는 한 문장.
2. **정의(What it is)** — 평이한 말로 쓴 메커니즘.
3. **존재 이유(Why it exists)** — 막으려는 실패를, 일어났던 일이 아니라 일어나는 일로
   서술한다. 메커니즘이 여러분에게 적용되는지 결정할 때 가장 먼저 읽을
   부분이다.
4. **도입 방법(How to adopt)** — 구체적인 단계.
5. **의존 대상 / 없으면 망가지는 것(Depends on / breaks without)** — 메커니즘 id별 edge.
6. **변경할 경우(If you change it)** — 대체물이 보존해야 하는 것.

훑어본다면 등급 줄(tier line)과 "존재 이유(why it exists)" section을 읽어라.
나머지는 도입할 메커니즘에만 필요할 구현 세부 사항이다.

## English brief

This chapter introduces a domain-independent operating harness for repository-based AI agents and classifies its thirty mechanisms as `CORE`, `DEFAULT`, `PARAMETER`, or `OPTIONAL`. It maps the mechanisms’ load-bearing dependencies, recommends A1 + A2 + E1 as the minimal viable set, and explains which additions address common operational symptoms. It also states recurring fail-closed and single-source principles, warns that generic blank forms do not override repository-specific schemas, and defines the six-part structure used by later mechanism entries.
