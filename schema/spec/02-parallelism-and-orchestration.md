# 제2장 — 병렬성, 세션, 오케스트레이션

이 장에서는 둘 이상의 에이전트 세션이 서로의 작업을 훼손하지 않으면서 같은 저장소에서 동시에 일하게 하고, 장기간의 작업이 여러 세션에 걸쳐 이어져도 살아남게 하는 메커니즘을 다룬다.

이 장 전체의 예시는 경로 그룹 `docs/reference/`, `docs/guides/`, `docs/api/`와 운영 계약 디렉터리 `ops/`가 있는 문서 사이트 저장소다. 각자의 레이아웃에 맞게 바꾸어 읽으면 된다.

예시에서는 이 명세가 들어 있는 스켈레톤과 의도적으로 다른 디렉터리 이름을 사용하며, 스켈레톤은 운영 계약 계층을 또 다른 이름으로 부른다. 이는 실수가 아니며 한 문장으로 짚을 가치가 있다. 예시와 스켈레톤의 이름이 일치하면 양쪽의 모든 이름이 규정된 것으로 읽히기 때문이다. 두 곳 모두에서 이름은 placeholder다. 메커니즘이 제약하는 것은 계층 사이의 *관계*이지 이름이 아니다.

evidence에 관한 주의: 이 harness는 정확히 한 프로젝트에서 실행되었다. 규칙의 tier가 단 한 번 관찰된 실패에 근거하는 경우, 그 실패 모드가 자신의 맥락에서도 발생 가능한지 판단할 수 있도록 본문에 그 사실을 명시한다.

---

## C1 — 지속적 통합을 수반하는 dedicated worktree 격리

**Tier: CORE** — 병렬 세션이 하나의 checkout을 공유하면 서로의 진행 중인 history와 staging state를 훼손하며, 이미 벌어진 뒤에는 어떤 후속 discipline으로도 복구할 수 없다.

### 이것은 무엇인가

각 세션은 세션 시작 시점의 최신 mainline snapshot에서 만든 자기 branch와 자기 git worktree에서 작업한다. 모든 쓰기는 그 worktree 안에서 일어난다. 어떤 세션도 다른 세션의 worktree에 쓰지 않으며, 두 세션이 하나의 checkout을 공유하지 않는다.

이 격리에는 반대 방향의 압력이 맞선다. **semantic unit이 소비 가능한 상태가 되는 순간—완성된 문서, 완료된 generated artifact, 닫힌 하위 task—즉시 mainline에 land한다.** 기본 landing 경로는 working branch를 현재 mainline tip 위로 rebase한 뒤 mainline을 그 branch까지 fast-forward하는 것이다. commit 일부만 선택적으로 land할 때는 cherry-pick을 사용한다. 두 힘은 의도적인 조합이다. 격리는 간섭을 막고, 즉시 landing은 분기를 막는다. 열흘치 작업을 worktree에 쥐고 있는 세션은 격리되어 있지만 쓸모가 없다. 다른 모든 세션은 그 작업이 빠진 mainline 위에서 계속 만들고 있으며, merge surface는 매시간 커진다.

정리는 **zero-residue check**를 통과해야 하며, 검사 방식은 landing 경로에 따라 다르다. 전부 fast-forward로 land했다면 working branch가 mainline의 ancestor인지 확인한다. cherry-pick을 하나라도 사용했다면 대신 patch-equivalence를 확인한다. cherry-pick된 commit은 hash가 달라지므로 commit 수를 세거나 tip을 비교하면 실제로 branch에 unlanded 작업이 남아 있어도 조용히 "nothing left"라고 보고할 수 있다. residue가 0임을 확인한 뒤에만 worktree를 제거하고 branch를 삭제한다.

### 왜 존재하는가

두 세션이 하나의 checkout을 공유하면 index와 진행 중인 history rewrite가 서로 뒤섞인다. 최근 commit에 correction을 fold하려고 rewrite하는 세션은 그 사이 다른 세션이 같은 checkout에 commit한 내용을 함께 집어 들고, 하나의 semantic unit이라고 주장하는 commit에 무관한 작업을 조용히 흡수한다. rewrite는 성공으로 보고된다. 오염은 나중에 누군가 commit을 읽고 subject와 전혀 관계없는 변경을 발견할 때 드러난다.

통합을 미루면 작은 conflict가 큰 conflict로 바뀐다. land되지 않은 소비 가능한 unit 하나하나가 다른 모든 세션이 결국 조정해야 하는 divergence이며, 조정 비용은 지연 시간에 대해 초선형으로 증가한다.

unlanded commit이 남아 있는 worktree를 제거하면 오류 없이 작업이 파괴된다. 순진한 검사—"branch와 mainline의 commit 수가 같다"—는 patch가 빠져 있어도 cherry-pick landing 뒤에 통과한다. cherry-pick이 hash를 다시 쓰기 때문이다. 이를 잡을 수 있었던 검사는 patch-equivalence 비교이며, 이를 명시하는 이유는 직관적인 검사가 틀린 검사이기 때문이다.

### 도입 방법

1. **Session start**: mainline tip에서 worktree와 branch를 한 단계로 만들고, work unit에서 유래한 branch name을 사용한다(`wt/api-reference-rebuild`). 이를 문서에 기록하지 않는다. worktree list를 query하면 복구할 수 있기 때문이다(C4 참조).
2. **During the session**: 소비 가능한 semantic unit을 commit하고 validate할 때마다 현재 mainline tip 위로 rebase한 뒤 mainline을 fast-forward한다. 이를 별도 잡무가 아니라 unit 완료의 일부로 취급한다.
3. **Mainline에 merge commit을 만들지 않는다.** 통합은 rebase + fast-forward 또는 cherry-pick이다.
4. **Session end**: 사용한 landing 경로에 맞는 residue check를 실행한다. residue가 0이 아니면 정리 전에 land한다. cleanup이 먼저 오는 일은 없다.
5. **공유 checkout에서 history를 rewrite하지 않는다.** correction을 기존 commit에 fold해야 한다면 이 세션만 쓰는 worktree에서 수행한다.

### 의존 관계 / 없으면 깨지는 것

- **E1 (producer wiring duty)** — 각 unit을 만드는 절차에 validator run이 연결되어 있지 않으면, 지속적 landing은 batch integration보다 더 *빠르게* 검증되지 않은 commit을 shared line으로 퍼뜨린다. 지속적 통합은 부재까지 포함해 현재 quality gate를 증폭한다.
- **C2를 활성화한다** — 직렬화된 issuance critical section은 최신 상태로 rebase하고 즉시 land하는 과정으로 정의되며, 이 메커니즘이 없으면 둘 다 존재하지 않는다.
- **C3와 D1을 활성화한다** — session boundary와 multi-agent orchestration은 모두 각 세션이 내용에 대한 단독 소유권을 가진 isolated workspace를 전제로 한다.

### 변경한다면

선형이며 merge가 없는 history는 **PARAMETER**다. 원본 프로젝트가 이를 선택한 이유는 "모든 것이 land했는가?"에 단 한 번의 ancestry test로 답하고, commit이 braid의 한 점이 아니라 하나의 semantic unit으로 읽히게 하기 위해서다. merge commit을 선호하는 프로젝트도 이 메커니즘의 나머지는 유지할 수 있지만, 대안은 두 속성을 보존해야 한다. (a) workspace를 파괴하기 전에 수행할 저렴하고 신뢰할 수 있는 residue check, (b) 둘 이상의 세션이 쓰는 checkout에서 history rewrite 금지. merge 쪽으로 가면 한 줄짜리 ancestry check를 잃고 장기 branch에서 rebase conflict가 줄어드는 이점을 얻는다. branch 수명이 길수록 이 tradeoff는 유리해지지만, 이는 다시 더 자주 land해야 한다는 논거이기도 하다.

---

## C2 — 직렬화된 identifier 발급 critical section

**Tier: CORE** — isolated workspace에서 전역 순차 resource를 발급하면 반드시 collision이 생기며, isolated validation은 collision을 발견할 수 없다.

### 이것은 무엇인가

일부 resource는 event record, decision record, migration step 등 "current maximum + 1" 형태의 identifier처럼 하나의 전역 sequence에서 번호를 받는다. isolated workspace에서 이들 중 하나를 발급하려면 끊어지지 않는 4단계 절차가 필요하다.

1. Working branch를 현재 mainline tip 위로 **Rebase**한다.
2. 해당 category의 current maximum을 **Recompute**하고, uncommitted working directory까지 포함한 모든 active worktree와 branch를 포괄하는 **global collision scan**을 실행한다.
3. Issuance를 **Commit**한다.
4. Fast-forward로 **즉시 land**한다.

1단계부터 4단계 사이에 세션은 다른 일을 하지 않는다. 두 번째 issuance도, 관련 없는 commit도, 오래 걸리는 delegation도 없다. "maximum을 계산한 시점"과 "내 번호가 mainline에 올라간 시점" 사이가 exposure window이며, 이 절차의 목적은 사람이 감독하는 process로 가능한 한 그 구간을 줄이는 것이다.

인접한 두 규칙이 메커니즘을 완성한다.

**Delegated execution과 isolated execution은 아예 발급하지 않는다.** Subagent, delegated worktree, 다른 agent에게 넘긴 branch 등은 numbered resource를 발급하지 않는다. 이들은 **unnumbered draft**를 반환한다. Sequence를 소유한 세션이 최신 mainline snapshot 위에서 번호를 할당한다. 유일한 예외는 owner 자신의 worktree이며, 위 4단계 절차를 통할 때만 가능하다. owner라도 절차 밖에서 발급하면 규칙 위반이다.

**Landing 실패 시 landing만 재시도하지 말고 전체 절차를 다시 시작한다.** adopter가 가장 먼저 빼먹는 부분이므로 아래에서 논거를 자세히 설명한다.

### 왜 존재하는가

두 isolated working copy가 각각 "current maximum + 1"을 계산해 같은 번호를 발급한다. 어느 copy의 validator도 상대를 볼 수 없으므로 둘 다 통과한다. Duplicate는 둘 다 land한 뒤에야 드러나며, 그때는 ambiguous identifier를 가리키는 reference가 이미 두 track에 모두 작성된 상태다.

Reference-based scan은 uncommitted file을 보지 못한다. Branch ref를 순회하는 scan은 다른 worktree의 uncommitted file이 같은 번호를 차지하고 있어도 clean sequence를 보고한다. Scan은 ref만이 아니라 active worktree의 working directory도 순회해야 한다.

**No-partial-retry rule**: 2단계와 4단계는 결합되어 있다. 2단계에서 계산한 maximum은 *오직 1단계가 만든 mainline snapshot에 대해서만* 유효하다. Fast-forward 실패는 mainline이 움직였다는 증거이고, 이는 2단계의 input이 이제 stale이라는 증거다. 더구나 mainline을 움직인 commit이 같은 category에서 번호를 발급했을 수도 있다. Landing만 다시 시도하는 것은 obsolete로 판명된 snapshot을 기준으로 계산한 번호를 publish하면서, conflict를 찾아냈을 바로 그 단계를 건너뛰는 행위다. 다시 시작할 때 버리는 것은 issuance commit이 아니라 *번호의 유효성*이다. Rebase하고 다시 계산하며, 재계산한 maximum이 움직인 경우에만 번호를 다시 매긴다.

마지막 요소는 **duplicate recovery**다. Convention에 의한 예방은 construction에 의한 예방이 아니기 때문이다.

- **나중** issuance의 번호를 다시 매긴다. 앞선 issuance와 이를 가리키는 모든 reference는 immutable하다. 선후는 first-add commit time으로 결정한다.
- 번호를 다시 매긴 문서는 어떤 번호에서 왜 바뀌었는지 기록한다.
- **Reference rewrite는 provenance-bounded이며 fail-closed다.** 기존 identifier는 적법한 앞선 issuance와 duplicate가 공유하므로 repository-wide substitution은 앞선 issuance의 reference를 나중 문서로 조용히 돌려버린다. 따라서 rewrite candidate는 duplicate가 처음 commit된 *뒤에* 추가된 reference로 제한한다. 그 전에 작성된 reference는 반드시 앞선 문서를 가리킨다. 각 candidate를 history와 대조해 개별 확인한다. Candidate 하나라도 구별할 수 없으면 **automatic rewriting을 중단하고 manual judgment로 넘긴다**. 잘못 가리키는 것보다 중단이 안전하다.
- Closure에는 uniqueness check를 다시 실행해 0을 확인하고 identifier를 가진 manifest row를 같은 commit에서 갱신하는 일이 필요하다.

### 도입 방법

1. 저장소에서 전역 순차 resource가 무엇인지 열거한다. 하나도 없다면 이 메커니즘은 필요하지 않지만, migration number, ordered decision log, fixture id 같은 암묵적 sequence도 확인한다.
2. Sequence마다 **single writer**를 지정한다. 원본 프로젝트는 "한 번에 하나의 active session"을 운영 기본값으로 삼으며, 병렬 상황에서 실제 issuance가 필요하면 사용자에게 escalate한다. 문서에 writer-designation field를 두지 않는다. 그런 field 자체를 갱신하는 데 또 single-writer discipline이 필요해 bootstrap loop가 되기 때문이다.
3. Resource를 만드는 runbook에 4단계를 하나의 atomic procedure로 적고, 그 사이에는 다른 작업이 없다는 제약도 절차 일부로 명시한다.
4. **Ref와 active working directory 둘 다** 훑는 collision scan을 구현한다. Numeric prefix만 비교한다. 관찰된 collision 형태는 같은 번호에 descriptive suffix가 다른 경우이며, whole-filename 비교로는 놓친다.
5. Recovery net으로 repository validator에 uniqueness check를 구현하고, 필요해지기 전에 위 duplicate-recovery procedure를 작성한다.
6. Delegated execution은 unnumbered draft를 반환한다고 명시한다.

### 의존 관계 / 없으면 깨지는 것

- **B2 (numbering discipline)** — 이 메커니즘은 B2의 parallel-execution 절반이다. B2의 single-global-writer rule과 recovery procedure가 없으면 critical section이 보호할 대상이 없다.
- **C1 (worktree isolation)** — 1단계와 4단계는 최신 상태 위로 rebase하고 fast-forward로 land하는 것으로 정의된다.
- **E1 (producer wiring duty)** — uniqueness check는 언제 실행되는지에 가치가 전적으로 달린 recovery net이다. Reference가 퍼지기 전에 detection하는 것은 기억에 기대는 것이 아니라 resource를 만드는 모든 절차에 check가 wiring됨으로써 보장된다. E1이 없으면 duplicate는 propagation 뒤에 발견되고, fail-closed reference rewriting은 진행을 거부하므로 정리가 manual이 된다.
- Minimal viable set **A1 + A2 + E1**이 모습을 드러내는 여러 지점 중 하나다. Wired enforcement가 없으면 나머지는 실행되지 않는 paperwork에 불과하다.

### 변경한다면

메커니즘은 CORE지만 *구현*은 고정되어 있지 않다. 원본 프로젝트는 sequence가 세션당 몇 번만 발급되고 lock 자체가 새 failure mode를 추가하므로 commit hook이나 counter의 compare-and-swap 없이 clause-level discipline을 의도적으로 택했다. 하루에 수백 번 번호를 발급하는 프로젝트라면 mechanize해야 한다.

Mechanized substitute는 네 속성을 보존해야 한다. Maximum을 issuance가 land할 같은 snapshot을 기준으로 계산할 것, uncommitted state를 포함한 모든 isolated workspace를 computation이 볼 것, computation과 landing 사이의 window를 최소화할 것, 그리고 sequence 도중 어디서든 실패하면 내부에서 resume하지 않고 전체 sequence를 restart할 것. 순진한 lock은 처음 세 속성은 보존하면서 네 번째를 조용히 깨뜨린다. Landing 실패 뒤에도 살아남는 lock은 바로 이 규칙이 금지하는 partial retry를 유도하기 때문이다.

---

## C3 — 작업 unit별 session 경계와 handoff 기준

**Tier: CORE** — 정의된 unit boundary가 없으면 context가 저하될 때까지 session이 이어지고, successor는 한 번도 기록되지 않은 state를 재구성해야 한다.

### 이것은 무엇인가

**하나의 implementation unit은 하나의 session과 같다.** Multi-part effort의 한 wave든 대규모 standalone work item이든 unit이 끝나면 해당 session은 handoff를 수행하고 종료한다. 다음 unit은 새 session에서 시작한다. 같은 session에서 다음 unit까지 계속하는 것은 사용자가 명시적으로 지시한 경우뿐이다.

Handoff는 다음 조건이 모두 충족될 때만 완료된다.

1. **생성된 모든 것이 commit되어 있고**, working tree가 clean하며 repository validator가 failure 0개를 보고한다.
2. **Successor가 재조사하지 않고 시작하는 데 필요한 모든 것이 committed canonical artifact에 들어 있다**—receipt, record, manifest, queue state. *Conversation에만 존재하는 state는 handoff의 근거가 아니다.* 아직 conversation에만 있는 decision과 observation은 handoff 일부로 지금 durable artifact로 promote한다.
3. **소비된 volatile working file을 삭제한다.** Intermediate inventory, candidate list, throwaway script가 이에 해당한다. Durable evidence는 (2)의 artifact가 맡는다. 다음 unit이 상속할 original만 명시적으로 retain한다.
4. **Handoff snapshot을 commit하고 entry-point pointer를 같은 commit에서 갱신한다.** Pointer는 새 session이 실제로 읽기를 시작하는 곳에서 snapshot으로 연결되는 link다. Pointer를 나중 commit으로 미루는 것은 금지한다. 누구도 link하지 않은 snapshot은 resume path에서 발견되지 않는다.
5. 사용자가 handoff를 명시적으로 요청한 경우와 reasoning이 누적된 긴 session을 끝낼 때는 **conversation preservation**이 필수다. 이는 state handoff와 별개의 축이며, 그 대체물이 아니다.

**Interrupted handoff를 위한 두 번째 경로**가 있으며 규칙은 반대로 바뀐다. Context limit이나 forced stop 등으로 unit을 완료할 수 없을 때 completion path를 따르지 않는다. 대신 다음을 수행한다.

- **Volatile working file까지 모두 commit해 freeze한다.** Completion path의 cleanup rule은 적용되지 않는다. Freeze 완료 조건은 dirty 및 untracked 항목이 0인 것이다.
- **File list는 file을 commit하는 일을 대신하지 않는다.** 정말 commit할 수 없는 것이 있다면 그 내용을 보존하는 patch나 artifact를 만들고, 그 hash와 recovery location을 durable carrier에 commit한다. 이것조차 불가능하면 **handoff 완료를 선언하지 않는다**. Unfinished stop으로 보고한다.
- Interrupted snapshot에는 last known-good commit, finished-and-verified와 반드시 re-run할 항목의 명시적 분리, outstanding failure를 포함한 known validator state, 보존해야 할 worktree와 branch 및 그 이유, resume 시 첫 command를 기록한다.
- 이 경로에서는 unit-completion receipt 발급, unit complete 표시, volatile file 삭제, worktree 제거가 **금지된다**. 이 모든 것은 unit을 실제로 끝내는 session의 몫이다.

### 왜 존재하는가

세 unit을 이어가는 session은 뒤쪽 판단의 품질이 떨어질 만큼 context가 쌓이고, session 내부에서는 그 저하가 보이지 않는다. Boundary는 context hygiene을 강제하는 장치다.

가장 흔한 handoff failure는 predecessor가 알고 있던 state를 successor가 다시 도출하는 것이다. Predecessor의 knowledge가 conversation 안에만 있었고 conversation은 전달되지 않기 때문에 발생한다. "durable하지 않으면 존재하지 않는다"라는 completion criterion이 전부를 방어한다.

Entry pointer를 갱신하지 않고 snapshot만 작성하면 아무도 그것을 찾지 못한다. Successor는 resume canon에서 읽기 시작해 여전히 이전 handoff를 가리키는 pointer를 따라가며 stale state를 기준으로 일한다. 한편 정확하고 최신인 snapshot은 repository 안에서 참조되지 않은 채 놓여 있다.

Interrupted session이 completion path를 따르면, completion path가 volatile을 정리하라고 하기 때문에 진행 중인 작업을 스스로 삭제한다. Interrupted path를 exception clause가 아니라 별도 절차로 작성하는 이유가 여기에 있다. 규칙이 실제로 뒤집히며, exception clause는 틀린 default를 적용하게 만든다.

### 도입 방법

1. 프로젝트에서 unit으로 보는 범위를 정의한다. 유능한 session 하나가 한 번에 끝내고, verify하고, land할 수 있는 크기여야 한다.
2. 위 다섯 기준을 순서대로 completion checklist라는 runbook에 작성하고, 1단계의 validator run을 명시적이고 이름이 정해진 command로 둔다.
3. Mandatory section을 갖춘 snapshot form(C4 참조)을 제공한다. 새 session이 읽기를 시작하는 방법, 종료 시점의 전체 state, 이 unit의 lesson에서 상속받은 obligation을 포함한 다음 unit scope, open 및 waiting list, pointers section이 필요하다.
4. Interrupted path를 각주가 아니라 별도 procedure로 작성한다.
5. Commit message만으로 session을 넘기지 않는다는 closing rule을 추가한다. Commit message는 history이지 starting surface가 아니다.

### 의존 관계 / 없으면 깨지는 것

- **C1** — unit boundary와 worktree lifecycle은 같은 lifecycle이다. Isolation이 없으면 "unit이 끝났다"는 말에 clean workspace teardown이라는 의미가 없다.
- **C4** — handoff artifact의 lifetime rule을 제공한다. 이것이 없으면 snapshot은 다른 곳에 있어야 할 content를 축적하고, handoff surface는 repository state의 두 번째 drifting copy가 된다.
- **E1** — completion criterion (1)은 실제로 실행되는 validator를 요구한다. Wired validation이 없으면 "zero failures"는 assertion일 뿐이다.
- **C5 (complement, not prerequisite)** — criterion (1)은 모든 것이 commit되었다고 말하며, C5는 각 commit을 개별적으로 읽을 수 있게 한다. 세 unit이 섞인 commit 하나로도 handoff는 criterion (1)의 문구를 충족할 수 있고, successor는 clean tree와 unreadable history를 함께 물려받는다.
- **B1 (event chain)** — successor의 one-line takeover receipt와 conversation에만 있던 decision을 durable record로 promote하는 일은 모두 evidence chain에 land한다.

### 변경한다면

CORE이지만 granularity는 프로젝트가 정한다. 대안이 보존해야 할 것은 다음과 같다. State를 durable form으로 강제하는 정의된 boundary, 명시적인 "conversation state does not transfer" 규칙, successor의 실제 entry point에서 handoff artifact로 이어지고 artifact와 원자적으로 함께 갱신되는 discovery path, 그리고 끝내지 않고 멈출 때 사용하는 별도 절차로서 finishing procedure의 cleanup default가 반전되는 절차다.

---

## C4 — Handoff 수명 분리

**Tier: CORE** — lifetime rule이 없으면 handoff surface는 정리할 때 permanent knowledge를 잃거나, 나중 session이 current로 읽는 stale state를 축적한다.

### 이것은 무엇인가

메커니즘은 state를 어디에든 쓰기 전에 각 조각에 적용하는 **classification test**다. 다음 순서로 실행한다.

1. **Query로 재구축할 수 있는가?** Task list, worktree state, terminal 또는 pane handle, branch state, commit history, version-control system이나 coordination runtime이 요청 시 열거할 수 있는 모든 것. → **절대 기록하지 않는다.** 기록된 copy는 real source에서 drift하지만 여전히 신뢰받는 두 번째 source of truth다.
2. **Successor가 takeover하면 lifetime이 끝나는가?** 현재 work 위치, successor가 처음 만질 것, 아직 보고하지 않은 것. → **Volatile handoff snapshot**.
3. **Session보다 오래가지만 이 ongoing unit에 속하는가?** 사용자 결정을 기다리는 decision backlog, assignment rationale, 이행하지 않은 notification duty, 다음 assignment에 영향을 주는 incident history. → **Persistent operating ledger**. 현재 role holder가 갱신하며 삭제하지 않는다.
4. **Unit 자체보다 오래가는가?** Standing discipline, deferred work item, 기록된 judgment failure. → **자기 canonical home**으로 보내고 snapshot은 **pointer만** 둔다.

이렇게 하면 하나의 handoff surface 아래에서 lifetime이 다른 두 compartment가 생긴다. 예를 들면 snapshot용 `ops/handoff/`와 ledger용 `ops/handoff/ledgers/`다.

그 결과 세 가지 운영 규칙이 따른다.

**Successor가 takeover하면 snapshot을 삭제한다.** Archive가 아니라 삭제다. Takeover 사실은 successor의 closing receipt에 한 줄—무엇을, 언제, 어느 commit에서 takeover했는지—로 남는다. History는 git의 일이다. Deletion commit과 entry pointer 제거는 **같은 commit**이어야 한다. 삭제된 문서를 가리키는 pointer는 link check를 실패시키고 그 failure가 enforcement mechanism이기 때문이다. 둘을 나눈 commit은 이미 broken임을 아는 state를 ship한다.

**Snapshot의 pointers section은 convention이 아니라 mandatory form field다.** 이 항목이 없을 때 permanent knowledge를 volatile document 안에 inline하게 된다.

**두 compartment 모두 repository 안에 둔다.** Repository 바깥의 path는 persistence mechanism이 아니다.

Volatile compartment의 content는 정당하게 사라지므로, structure registry는 해당 series와 함께 명시적인 persistence exception을 선언해야 한다. 그렇지 않으면 routine deletion이 registry가 찾아야 하는 undeclared-or-missing-path failure를 일으킨다.

Snapshot filename에는 per-unit counter, slug, date만 있으면 된다(`handoff-02-api-reference-rebuild-YYYYMMDD.md`가 한 가지 유효한 형태다). Counter는 의도적으로 global sequence가 **아니다**. Consumption이 이전 entry를 삭제하므로 global counter에는 permanent hole이 생기며, 필요도 없는 문서에 single-writer issuance discipline 전체(C2)를 끌어들인다. Ordering canon은 date와 history다.

### 왜 존재하는가

**Temporary directory에 둔 operating ledger는 통째로 사라진다.** Runtime restart나 system의 scratch area cleanup이 handoff record 전체를 없앤다. 원본 프로젝트에서는 규칙이 작성되기 전에 같은 class의 document에서 이 일이 두 번 발생했다. 이를 낳은 reasoning은 설득력 있어 보인다. In-progress state는 repository content가 아니므로 repository 바깥에 속한다고 여겼다. Correction은 *content type*이 아니라 *durability requirement*가 home을 결정한다는 것이다. 다음 session이 읽어야 하는 ledger는 durability requirement다.

**Takeover 뒤에도 남은 snapshot은 active work처럼 읽힌다.** Handoff surface는 "무엇이 in flight인가"에 답하기 위해 scan되며, consumed snapshot은 틀린 답을 준다. 나중 session이 이를 열고 두 unit 전의 세계 상태에서 작업한다. 이는 한 프로젝트의 관찰된 incident 하나지만 D1의 stale-pane problem과 형태가 같다. Instance가 아니라 failure class가 일반화되는 것으로 보인다. Liveness를 위해 scan하는 surface는 이를 consume한 주체가 cleanup해야 하며, enforcement는 habit이 아니라 structural이어야 한다.

**Volatile document에 세워 둔 permanent knowledge는 올바른 행동 때문에 파괴된다.** Successor는 지시대로 snapshot을 consume하고 delete하며, 다른 home이 없는 standing rule이나 open decision도 함께 사라진다. Volatility가 loss가 된다. 그러므로 먼저 canonical home으로 보내고 그다음 pointer를 둔다.

**Query-recoverable state를 문서에 복사하면 없는 것보다 나쁘다.** 한 번 작성되고 갱신되지 않으며 authoritative로 읽힌다. 기록된 worktree list는 세 개라고 하고 실제 list는 다섯 개라고 한다.

### 도입 방법

1. 두 compartment를 만들고 owner rule을 각각 둔다. Snapshot은 outgoing session이 작성하고 incoming session이 삭제한다. Ledger는 현재 role holder가 갱신한다.
2. Classification test를 handoff form 자체의 "what does not go here" section에 작성한다. 원본의 ledger는 의도적으로 넣지 않은 항목과 그 이유를 먼저 밝힌다. 그 한 paragraph가 다른 곳에 적힌 규칙보다 더 많은 일을 한다.
3. Pointers section을 snapshot form의 required field로 만든다.
4. Structure registry에 두 compartment를 모두 선언하고 persistence exception은 volatile compartment에만 한정한다.
5. Deletion과 pointer removal을 한 commit으로 만들고 link check에 위반 detection을 맡긴다.
6. Successor의 closing receipt에 one-line takeover record를 요구한다.

### 의존 관계 / 없으면 깨지는 것

- **A2 (structure declaration registry)** — series와 persistence exception을 함께 선언하는 registry가 없으면 routine snapshot deletion이 undeclared-path 또는 missing-path failure로 읽힌다. 이를 "고치기" 위해 snapshot을 영원히 보존하라는 압력이 생기고 메커니즘이 파괴된다. Minimal viable set A1 + A2 + E1이 이 장에서 실제 하중을 받는 지점이다.
- **A4 (manifest discipline)** — ledger는 manifest-class document다. Named update owner가 없으면 조용히 stale해진다.
- **C3** — C3의 checklist가 만들고 consume하는 artifact를 정의한다.
- **B1 (event chain)** — takeover receipt와 unit보다 오래가는 content의 canonical home(deferred queue, record layer)은 B1의 structure다. B1이 없으면 4단계 content를 보낼 곳이 없어 모든 것이 다시 snapshot으로 무너진다.
- **Link checking (E-family enforcement)** — same-commit deletion rule은 link check로 enforce된다. 이것이 없으면 dangling pointer가 쌓이고 규칙은 request 수준으로 약해진다.

### 변경한다면

Lifetime split은 CORE지만 compartment 수는 프로젝트가 정한다. 어떤 프로젝트는 세 tier(per-handover, per-unit, per-role)를 원할 수 있다. 대안이 보존해야 할 것은 (a) preference가 아니라 prohibition으로 쓰인 query-recoverable exclusion, (b) "what is in flight" surface를 truthful하게 유지하도록 consumption 시 삭제되는 compartment 하나 이상, (c) repository 안에 있으며 삭제되지 않는 compartment 하나 이상, (d) unit보다 오래가는 content를 deleted compartment 밖에 두는 pointer discipline, (e) consumption된 artifact가 남거나 pointer가 target보다 오래갈 때 실패하는, deletion에 대한 structural enforcement다.

Auditability를 위해 consumed snapshot을 보존한다면 다른 방식으로 liveness signal을 대체해야 한다. Successor가 반드시 flip하고 validator가 check하는 status field가 한 방법이다. 단순히 "date를 읽자"고 합의하면 stale-reads-as-active failure를 재현한다.

---

## C5 — Commit 규율

**Tier: DEFAULT** — 이것이 막는 실패는 decision sequence로 다시 읽을 수 없는 history다. 여기의 habit set은 이를 막는 하나의 실행 가능한 방법이며, mechanized equivalent가 있는 프로젝트는 자유롭게 대체할 수 있다.

### 이것은 무엇인가

C1은 history를 *어디에* 쓰고 *어떻게* land하는지를 다룬다. Session이 어느 workspace를 소유하는지, unit을 언제 integrate하는지, mainline이 어떤 shape를 유지하는지다. C5는 각각의 commit만 놓고 본 hygiene, 즉 무엇이 들어가고, 무엇이라 부르며, 누가 publish할 수 있는지를 다룬다. **C1을 도입한 adopter는 commit 질문도 이미 해결되었다고 생각하므로 이 boundary를 본문에 명시할 가치가 있다.** 그렇지 않다. 올바른 landing path를 가진 isolated worktree도 세 unit을 섞고, readable subject가 없으며, 사람이 손으로 한 작업을 조용히 되돌리는 commit을 만들 수 있다. Integration shape—merge commit 없음, rebase-and-fast-forward 또는 cherry-pick—는 C1에 속하며 여기서 의도적으로 다시 말하지 않는다.

일곱 규칙이 있다.

**의미 있는 completed operation은 commit으로 끝나며, 그 commit을 remote에 publish하는 일은 commit을 만드는 것과 별개의 authorization이다.** Session은 자신이 소유한 workspace 안에서 자유롭게 commit하지만 요청받지 않으면 push하지 않는다. "do the work"를 "publish the work"까지 포함한다고 읽는 agent는 두 permission을 하나로 합친 것이다. 첫째는 repository content, 둘째는 누가 언제 그 content를 볼지에 관한 permission이다.

**Working tree는 unit 종료 때뿐 아니라 request 시작 때 inspect한다.** Uncommitted change가 있고 다른 작업에 속한다면 이를 알리고, 새 변경과 섞기 전에 처리 방향을 확정한다. C3는 unit이 *닫힐 때* clean tree를 요구할 뿐 request가 *열릴 때* clean해야 한다고 하지 않는다. 이 틈에서 predecessor의 half-finished change가 unrelated commit에 흡수되고 영구적으로 그 commit에 귀속된다.

**Staging은 unit별로 explicit path를 사용한다.** Stage-everything 형태는 changed file 전부가 곧 commit할 unit에 속함을 확인한 뒤에만 사용한다. Commit boundary는 intent로 정한다. 아무것도 enumerate하지 않는 staging command는 그 시점 tree에 우연히 있던 모든 것을 기록하므로 timing이 boundary를 정한다.

**Commit binding은 file type이 아니라 provenance를 따른다.** Item을 consume하거나 promote할 때 one item은 one commit이며 그 item에서 나온 모든 것이 그 commit에 속한다. Promoted document, source 제거, 여기서 파생된 rule 또는 wiring이 모두 포함된다. 거부해야 할 직관적인 grouping은 모든 document를 한 commit, 모든 registry edit를 두 번째 commit, 모든 guidance edit를 세 번째 commit에 넣는 방식이다. 이렇게 하면 history는 나중에 누구나 묻는 "이 item이 무엇을 야기했는가"가 아니라 "어떤 종류의 file이 바뀌었는가"에 답한다. 이것이 일반 clause다. **F4**는 같은 binding을 volatile workspace layer의 consumption path에 적용한 것으로, 이 규칙의 source가 아니라 한 instance다. Optional workspace layer를 생략하는 adopter도 이 규칙은 필요하다.

**Unpushed commit의 correction은 그 commit 위에 쌓지 않고 그 commit에 fold한다.** History는 fix trail이 아니라 semantic unit sequence다. 한 unit 뒤에 그 자체를 고치는 세 correction이 붙으면 아무도 하나로 읽을 수 없는 한 unit이 된다. 이 규칙은 C1과 정면으로 만나는 곳이며 순서는 **C1 first**다. Fold-in은 history를 rewrite하고, C1은 다른 session이 쓰지 않는 checkout에서만 이를 허용한다. 안전하게 fold-in할 수 없다면 correction은 별도 commit으로 남기고 이유를 밝힌다. C1 제약 없이 이 규칙을 도입하면 C1이 기록한 contamination을 재현한다.

**사용자가 직접 한 변경은 사용자가 요청하지 않는 한 revert하지 않는다.** Agent가 hand-edited file이 자기가 만드는 것과 일치하지 않는다고 발견했다면 defect가 아니라 question을 발견한 것이다.

**Commit message는 fixed form을 사용한다.** 원본 프로젝트의 형식은 짧은 prefix, colon, subject line, 그리고 아래의 concise bullet이다. **Prefix set은 PARAMETER**다. Repository가 실제로 만드는 change kind를 나타내는 작고 closed된 list를 고르고, 선택 자체가 decision이 되지 않을 만큼 작게 유지한다. Open-ended prefix vocabulary는 prefix의 유일한 목적이던 grouping을 전혀 제공하지 않는다.

### 왜 존재하는가

여기의 모든 규칙은 history가 readable하지 않게 되는 한 경로를 막는다. 손실은 누군가 history를 읽으려 할 때만 발견되며, 그때는 항상 나중이고 대개 시간 압박 속이다.

요청받지 않은 push는 local state를 다음에 pull하는 모든 사람에게 보이게 만든다. 공유 전에 review가 가장 필요한 state일수록 agent 자신은 가장 자신만만하다. 이를 되돌리는 행위는 다른 사람에게 보이는 또 다른 event가 될 수밖에 없다.

Dirty tree에서 조립한 commit은 잘못 귀속된다. Subject는 한 unit을 설명하지만 diff에는 그 unit과 이전 request가 남긴 것이 함께 들어간다. 아무것도 실패하지 않는다. Fold-in rule이 제약하고 C1이 다시 제약하는 history rewrite로 누군가 고치지 않는 한 오귀속은 영구적이다.

Commit을 file kind별로 묶으면 causal link가 끊어진다. 몇 달 뒤 질문은 "이 rule은 왜 존재하는가"이고, 답은 rule만 든 commit과 그 근원이 된 document만 든 옆 commit에 나뉘어 있으며 둘 사이를 묶는 것은 시간상 인접성뿐이다.

Correction을 별도 commit으로 쌓으면 unit이 thread가 된다. Change를 읽으려면 네 commit을 읽고 서로 diff해야 하며, 첫 commit만 읽은 reviewer는 이미 틀렸다고 알려진 version을 읽는다.

사람의 edit를 revert하는 일은 이 목록에서 cost 대비 visibility 비율이 가장 나쁘다. Agent는 자신감이 있고 change는 작으며, edit한 사람은 자신의 작업이 사라진 것을 직접 알아차려야 한다.

### 도입 방법

1. 이 규칙을 agent가 자동으로 load하는 instruction surface에 둔다. 사후에 참조하는 policy document에 두지 않는다. Commit discipline은 세션마다 여러 번 적용되므로 프로젝트당 한 번 읽는 규칙은 commit 시점에 적용되지 않는다(F6).
2. Prefix set을 고정하고 message form 옆에 closed list로 작성한다.
3. Push rule을 preference가 아니라 named exception이 있는 prohibition으로 쓴다. "Prefer not to push"는 "유용해 보이면 push"로 읽힌다.
4. Working-tree inspection을 agent가 request 시작 시 이미 수행하는 절차에 추가한다. Routing을 결정하는 같은 단계가 가장 저렴한 위치다.
5. Consumption 또는 promotion procedure를 작성할 때 그 procedure 안에서 commit binding을 명시하고, 거부하는 grouping을 구체적으로 적는다. 거부 대상 grouping을 보여주는 부분이 핵심이다. 올바른 grouping은 보고 나면 당연해 보이지만 스스로 선택되지는 않는다.

### 의존 관계 / 없으면 깨지는 것

- **C1** — fold-in rule을 실행할 수 있는 위치를 제한하며, 이 메커니즘이 재진술하지 않는 integration shape를 소유한다. C1의 shared-checkout prohibition 없는 C5는 hygiene rule을 contamination path로 바꾼다.
- **C3** — "unit"의 의미를 제공한다. Intent로 정하는 commit boundary는 어딘가에서 intent가 정의되어야 하며, work-unit boundary가 그 출처다.
- **B1 / B3** — provenance binding rule은 evidence chain의 consumption 및 promotion path를 위해 작성되었다. Provenance를 가진 record가 없으면 "bind by provenance"가 묶을 대상이 없다.
- **F4** — volatile workspace layer의 consumption path는 위 binding rule을 특별히 적용한 것이지 별도 규칙이 아니다.
- **F6** — 이 규칙은 commit 시점에 읽히므로 필요할 때 여는 document가 아니라 always-loaded entry surface에 속한다.

### 변경한다면

Set 전체는 DEFAULT다. 규칙들은 history가 decision sequence로 다시 읽힌다는 한 목적을 공유하지만 각각 독립적으로 대체할 수 있다. Mechanized equivalent가 있다면 이를 선호해야 한다. Unauthorized push를 거부하는 remote, prefix 없는 subject를 거부하는 hook이 예다. Enforced rule과 written rule은 다른 종류이며, 원본 프로젝트의 volume이 machinery를 정당화하지 않아 이 메커니즘은 enforced가 아니라 written인 것이다.

대안이 보존해야 할 것은 change와 publish를 하나가 아닌 두 authorization으로 분리하는 것, 우연히 tree에 든 항목이 아니라 intent로 commit boundary를 정하는 것, 1년 뒤에도 "무엇이 이것을 야기했는가"에 답하는 grouping rule, 그리고 요청 없이 사람의 작업을 되돌리는 것을 금지하는 것이다. Message form과 prefix set은 전체적으로 PARAMETER다.

---

## D1 — 세 role 분리와 orchestration 불변 조건

**Tier: CORE** — 아래 invariant는 multi-agent parallelism을 단순한 concurrency가 아니라 안전한 실행으로 만든다. 각 invariant는 isolation만으로 막지 못하는 failure 하나를 닫는다.

이 장에서 가장 큰 메커니즘이다. 아래 내용은 procedure order가 아니라 invariant별로 구성한다.

### 이것은 무엇인가

#### Role 분리

세 agent role에 앞서, role이 **아닌** 축 하나가 있다. Human authority는 role structure 바깥에 완전히 놓이며 contract는 구분을 암시로 남기지 않고 명시한다. 사용자는 repository에 무엇이 들어가는지 선택하고, goal을 정하며, feedback을 주고, 중요한 change를 승인한다. Agent는 반복 작업—processing, structuring, linking, integrating, verifying, improvement proposal—을 한다. 아래 세 role은 모두 이 구분 아래에 있다. 어느 role도 user role이 아니며, 가장 senior한 agent라는 이유로 user authority를 얻지 않는다. 이 구분을 적어야 이 메커니즘 뒤쪽의 routing rule을 실행할 수 있다. 사용자가 무엇을 하는지 한 번도 밝히지 않은 contract에서 "return it to the user"는 instruction이 아니다.

**Director**는 work를 assign하고, parallel unit 사이의 conflict를 control하며, handoff를 relay하고, assignment structure가 작동하는지 review한다. **Real work는 전혀 하지 않는다**—authoring, editing, numbered artifact issuance 모두 금지다. Director가 일을 시작하면 parallelize할 수 없는 유일한 일을 중단하고 assignment decision에 필요한 judgment capacity를 소진한다. 자기 closing receipt도 직접 작성하지 않고 delegate한다. 작성은 real work이기 때문이다.

**Worker**는 일을 한다. 각 work unit에는 C1과 C3에 따라 자기 worktree에서 동작하는 named worker session이 배정된다. **Worker는 자기 unit의 orchestrator다.** Sub-delegation, review commissioning, 내부 work split은 모두 worker의 authority이며 director는 unit 내부로 들어가지 않는다. Director의 scope는 unit *사이*이지 한 unit *안*이 아니다.

유일한 carve-out은 runtime resource allocation이다. Worker의 기본 sub-delegation mechanism은 in-session subagent이며, 새 top-level work surface를 만들려면 director의 사전 승인이 필요하다. 각 surface에는 interactive process와 runtime task item이 붙는다. 무제한 생성은 둘 다 범람시키고 director의 sweep set도 함께 커진다. Shared runtime resource allocation은 between-unit coordination이므로 이는 non-interference의 예외가 아니다.

**Intake desk**는 user request를 받고 minimal fact-finding을 수행한 뒤 assignment request를 file한다. Request intake가 director의 assignment design 뒤에서 queue되지 않게 하려는 role이다. 이 role이 하지 않는 네 가지가 있다. **User interview 없음**(unresolved point는 item을 실행할 worker를 위한 question list가 된다), **repository write 없음**, **spawning 없음**, **design work 없음**(decomposition, ordering, scope는 director와 worker의 몫이다). Fact-finding은 assignment decision에 필요한 범위—target path가 있는가, 얼마나 큰가, 해당 path에서 unit이 이미 active인가—로 제한한다.

**Desk는 director surface를 split하지 않고 자기 top-level work surface를 가진다.** Worker 배치와 같은 방식으로 desk를 두는 것이 뻔해 보이므로 이유를 밝힐 가치가 있다. 첫째, desk의 lifetime은 work unit의 lifetime이 아니다. Desk가 file하는 모든 unit보다 오래가므로 unit-lifetime 조건으로 할당한 surface는 잘못된 container다. 둘째, director surface의 split position은 worker가 필요로 하는 유한 resource다. Desk가 하나를 차지하면 실제 작업을 전혀 하지 않는 것에 worker slot을 쓴다. Worker는 split을 얻고 desk는 surface를 얻는다.

**Spawn authority는 director에게만 있으며**, 실제 privilege다. Work surface creation은 arbitrary command string을 받아 사실상 arbitrary process execution이 된다. 이 권한은 user action으로 부여되며 agent가 자기 permission을 edit해서 얻지 않는다.

**Worker model tier는 launch 시점에 pin**하며, director와 같은 tier를 explicit launch argument로 지정한다. Model을 강제하지 않고 agent type만 선택하는 shortcut은 조용히 더 낮은 tier를 만든다. 잘못 launch한 worker는 respawn하지 않고 제자리에서 바로잡는다. Worker의 accumulated context가 가장 비싼 부분이고 respawn은 이를 버리기 때문이다. Corollary로 director는 live worker의 surface를 닫지 않으며, worker가 죽으면 session resume으로 recover한다.

"Live"를 정확히 읽어야 한다. 반대편에서는 rule이 뒤집힌다. Worker가 전혀 시작되지 않은 surface—launch가 실패하고, session이 attach되지 않았으며, 안에서 아무것도 실행되지 않은 경우—에는 accumulated context가 없다. 이를 보존해도 아무것도 보존하지 못하며, slot을 차지하고 sweep마다 존재하는 unit으로 나타날 뿐이다. 닫고 다시 launch한다. **Discriminant는 surface의 나이가 아니라 context가 accumulated되었는가다.** 1분 전에 만들었고 live worker가 들어 있는 surface는 보호된다. 1분 전에 만들었지만 launch가 실패한 surface는 보호되지 않는다. 둘의 나이는 같다. "do not close workers"라고만 적으면 규칙은 preservation instinct로 읽히고 아무도 거두려 하지 않는 empty surface가 sweep set에 가득해진다.

#### Authority routing: 혼동하면 안 되는 두 경로

**User approval은 절대로 director를 통해 relay하지 않는다.** Worker가 자기 session에서 ordinary session처럼 interview를 제기하고 user가 그 자리에서 답한다. Contract-grade 또는 structure-grade 사안은 D3를 따른다.

Relayed approval은 네 가지를 동시에 깨뜨린다. Question이 발생한 context를 잃어 user는 paraphrase에 답하게 된다. Answer는 user own words가 아니라 director가 요약한 user decision으로 기록되어 verbatim capture가 가장 중요한 지점에서 evidence chain을 훼손한다. Worker는 second-hand answer를 캐물을 수 없다. User는 answer할 때 질문 대상 state를 볼 수 없다.

이 때문에 launch topology가 중요하다. Worker surface는 director surface에서 split되어 둘 다 한 화면에 남는다. User가 제자리에서 answer할 수 있을 때만 direct interview가 실제로 일어난다.

**Agent-to-agent coordination gate는 반대로 director가 중재한다.** 누가 issuance critical section에 먼저 들어가는지, 누가 mainline에 먼저 land하는지, 누가 contested path group을 양보하는지가 해당한다. 그 mediation이 바로 conflict-control role이다.

**Discriminant**는 이를 해결하는 데 approval, preference, scope, contract wording과 같은 user의 *authority*가 필요한지, 아니면 shared exclusive resource를 놓고 agent 사이를 *arbitrate*하기만 하면 되는지다. 전자는 user에게 직접 간다. 후자는 director에게 간다. **Ambiguous하면 user authority가 필요한 것으로 취급하고 돌려보낸다.** Asymmetry가 이를 지지한다. User에게 잘못 routing하면 latency 비용이 들지만 director에게 잘못 routing하면 authority 없는 decision이 생긴다.

두 가지가 이를 뒷받침한다. Director는 approval-shaped question에 **답변을 거부**하고 되돌려보낸다. 그리고 **모든 assignment spec에는 routing rule을 명시한 precedence clause가 있다.** 두 번째가 필요한 이유는 tooling이 worker startup 시 assignment spec과 충돌하는 preamble을 inject할 수 있기 때문이다. Refusal은 preamble이 이긴 상황을 조용한 relay가 아니라 즉시 visible하게 만든다.

같은 계열의 구분이 하나 더 있다. **Action approval은 wording approval이 아니다.** "Reflect this in the guidance"라는 지시는 반영 행위를 authorize할 뿐 resulting clause text까지 authorize하지 않는다. Canonical wording은 land 전에 user에게 보여주며 두 approval을 별도로 기록한다.

#### Perception: push를 신뢰하지 않고 active polling

**Director는 기다리는 대신 sweep한다.** 주기적으로 다섯 가지를 query한다. Unread message, work-item state, dead 및 ghost surface를 식별하는 work-surface list, worktree별 unlanded commit, 그리고 active worktree와 branch를 포괄하는 **모든 numbered sequence의 duplicate scan**이다.

서로 다른 두 failure mode가 이 규칙을 만든다.

*Report가 도착했지만 perceive되지 않는다.* Worker가 dispatch record에 등록된 coordinator address가 아니라 자신이 받은 message의 sender handle로 reply한다. Message는 deliver된다. Director의 blocking wait는 coordinator address를 보고 있어 wake하지 않는다. 양쪽 모두 communication이 일어났다고 믿는 동안 report는 unread로 남는다. 관련 variant로, status-report class를 빼놓은 wait filter는 status reply를 unread로 쌓고 director는 worker가 idle하다고 결론 낸다. 따라서 report는 항상 dispatch record에 등록된 address로 보내며, wait filter는 worker가 emit할 수 있는 *모든* class를 포함해야 한다.

*Reporting duty에 의존하면 missing report는 silence가 된다.* Conflict report duty는 worker diligence에 기대며, 이를 지키지 않으면 아무 일도 일어나지 않는다. 실제로 numbering collision이 report되지 않은 채 지나가 user가 지적할 때까지 발견되지 않았다. Duplicate scan은 그 silence를 깨는 축이므로 **모든 sweep에서 unconditional하게** 실행한다. Condition을 붙이면 condition이 틀렸을 때 detection이 약해지는 것이 아니라 완전히 사라진다.

Scan의 known limit 두 가지는 adopter가 읽는 곳에 모두 명시해야 한다. 관찰된 collision은 descriptive suffix만 다른 같은 번호이므로 whole filename이 아니라 **numeric prefix**를 비교한다. 그리고 **reference-based query는 uncommitted file을 보지 못하므로** sweep은 C2에 따른 issuing session 자체의 scan을 대체하지 않는다.

**Timeout은 failure가 아니라 checkpoint다.** Timeout이 나면 director는 surface output과 idle wait로 liveness를 확인하고 다시 기다린다. Heartbeat와 surface activity는 *liveness* signal일 뿐 *completion* signal이 아니다. Live worker는 completion report가 아직 없다는 이유만으로 interrupt, terminate, restart되지 않는다.

**Completion은 prose가 대체할 수 없는 structured signal이다.** Surface output이나 narrative "I'm done"은 work item을 close하지 않는다. Director는 계속 기다리고 worker는 이미 끝났다고 믿는다. 반대로 completion signal은 아무것도 verify하지 않는다. Closure section을 참조하라.

**같은 원리는 재귀적으로 적용된다.** Worker가 commissioned review, subagent, external command 같은 자기 sub-tool을 기다릴 때도 push하지 않는 counterpart 문제를 겪는다. 두 극단 모두 실패한다. Foreground에서 block하면 exclusive resource를 그동안 사용할 수 없고, check를 버리면 끝난 작업이 idle 상태로 놓인다. 규칙은 짧은 periodic check 사이에 다른 일을 하고, commissioning 시 check interval을 고정하며, 합의한 check count를 넘으면 director에게 escalate하는 것이다. 실무 함정을 유의하라. 무언가 깨워줄 것이 없다면 "check back in N minutes"는 실행할 수 없다. Interval을 정할 때 waking mechanism도 정한다.

#### Exclusivity: path group당 writer 한 명

**Director는 같은 path group을 쓰는 두 active unit을 동시에 assign하지 않는다.** Assign 전에 target group에서 어떤 unit이 active인지 확인하고 overlap을 serialize한다.

**Worktree isolation은 이 피해를 막지 못한다.** Isolation은 write interference를 막지만 judgment invalidation은 막지 못한다. Content에 대한 모든 judgment는 그것이 내려진 snapshot, 실무적으로는 file hash에 binding된다. 다른 track이 mainline에 land하면 write conflict가 없었더라도 그 file에 대해 이미 내려진 judgment가 invalidate된다. 원본 프로젝트에서는 같은 path group을 쓰는 두 session 때문에 baseline 전체를 다시 freeze하고, 이전에 pass한 많은 judgment를 invalidate해야 했다. 한 프로젝트에서 일어난 incident 하나지만, 프로젝트에 content state에 binding된 judgment—review verdict, approval, quality gate, cached analysis—가 있는지 확인할 가치가 있다. 있다면 isolation만으로 충분하지 않다.

**피할 수 없는 overlap은 assignment 시점에 비용을 책정한다.** Serialize할 수 없다면 assignment가 re-freeze cost—다시 issue해야 할 judgment 수, exemption을 결정할 사람—를 명시하고 그 비용을 unit scope에 포함한다. 나중에 비용을 발견하는 실패를 피해야 한다.

**Repository-wide retroactive unit은 path enumeration으로 control할 수 없다.** Terminology sweep이나 notation migration은 특정 path가 아니라 "condition이 성립하는 모든 곳"을 target으로 한다. 그런 unit은 (a) 동시에 active한 *모든* unit과 overlap한다고 가정하고 (b) conflict disposition을 미리 고정해 assign한다. 타당한 default disposition은 latest mainline content를 취한 뒤 자기 change를 그 위에 다시 적용하는 것이다. 두 unit이 같은 곳을 같은 방향으로 edit했다면 순서와 관계없이 결과가 같으며 latest를 취하면 history가 단순해진다.

**Path-group exclusivity와 global-resource exclusivity는 별도 축이며 어느 쪽도 다른 쪽을 대체하지 않는다.** Unit이 자기 path group에서 유일하더라도 globally sequential identifier(C2)를 놓고 contend할 수 있다. Globally exclusive resource 진입은 예외 없이 director가 중재한다.

**그 mediation이 구체적으로 어떤 모습인지는 여기서 정하지 않으며, 그렇게 밝히는 것 자체가 핵심이다.** 원본 프로젝트 contract는 모든 진입이 director를 거쳐야 한다는 requirement를 쓰고, 같은 clause 안에서 concrete entry-coordination procedure가 아직 contract에 없다고 말한다. 그 gap 자체가 아니라 이런 형식을 도입하라. **Contract가 요구하지만 아직 방법을 말할 수 없는 것이 있으면 그 requirement가 적힌 곳에서 바로 그 사실을 밝힌다.** 대안은 완성된 것처럼 읽히는 clause이며, 각 session이 자신은 procedure를 따른다고 믿으면서 서로 다른 improvised procedure를 만든다. 인정된 gap은 work item이다. 인정되지 않은 gap은 silent divergence이고, missing paragraph가 아니라 conflict로 발견된다. 같은 방식은 뒤의 adversarial review gate에도 나타난다. Gate가 structural하게 포괄할 수 없는 residue를 얼버무리지 않고 이름 붙인다.

**Conflict는 발견 시 report하며 self-repair했더라도 마찬가지다.** 같은 global resource에서 어느 두 unit이 만났는지는 다음 assignment decision의 input이다. Silent self-repair는 signal을 지워 같은 collision이 반복되게 한다. Report는 repair 뒤로 batch하지 않는다.

**Conflict는 허용 가능한 operating mode가 아니라 broken rule의 signal이다.** Report나 sweep으로 conflict를 알게 된 director는 disposition이 recovery procedure(C2)를 따랐는지 확인하는 *동시에* procedure가 새어 나온 지점을 식별해 닫는다. Root cause가 session 내부의 procedure violation이라면 assignment를 강화해도 recurrence를 막지 못한다. 고쳐야 할 것은 procedure compliance다.

**Conflict history를 위한 별도 ledger는 없다.** Conflict를 겪은 unit이 circumstance, root cause, disposition을 자기 durable receipt에 기록하고 director는 같은 resource에 대한 assign 전에 그 receipt를 query한다. Dedicated conflict ledger는 receipt에 이미 든 내용을 duplicate한다. C4의 query-recoverable exclusion과 같은 reasoning이다.

#### Reporting economy

Director에게 보내는 report에는 **verifiable value만** 담는다. Commit hash, issued identifier, check count, worktree state, blocked 여부와 scale, director judgment가 필요한 item이다. Narrative, verdict의 reasoning, lesson learned, considered alternative는 담지 않는다. 이들은 지속되는 unit durable receipt에 들어간다. 원본 프로젝트는 status report를 10줄, blocked 또는 conflict report를 20줄로 제한한다. Director의 judgment capacity는 유한하며 report volume이 decision보다 먼저 이를 소비하기 때문이다.

**Brevity는 volume에 관한 규칙이지 silence를 허가하지 않는다.** Compression rule에는 반대로 베는 날이 있다. Brief하라는 지시를 받은 agent는 brief하게 말하기 가장 어려운 것을 버리며, 바로 그런 내용은 recipient가 다른 곳에서 reconstruct할 수 없다. 따라서 uncertainty, blocker, significant finding, request for clarification, final status라는 다섯 signal은 길이를 이유로 절대 suppress하지 않는다. 이들 중 둘은 이미 mandatory-content list에 있지만 여기서 다시 쓰는 것은 duplication이 아니다. List만으로는 compression instruction이 override하는 것을 막지 못하고 이 clause가 그것을 막는다. 그래서 clause는 implied되지 않고 독자적으로 존재해야 한다. 다섯 항목을 버린 report는 clean result처럼 읽히며 clean result는 action으로 이어진다.

**Conflict report는 예외이며 compress하지 않는다.** Circumstance, root cause, disposition을 모두 기록한다. 이것이 다음 assignment의 input이기 때문이다.

#### Instruction ordering

Worker에게 보내는 message는 순차적으로 queue되며 일반적으로 cancel이나 reorder primitive가 없다. Arrival order로 instruction을 consume하는 worker는 shutdown하지 말아야 할 때 shutdown하는 경우까지 포함해 superseded instruction을 실행할 수 있다. 따라서 **worker는 행동 전에 unread queue 전체를 non-consuming read**하고 발견한 내용을 기준으로 execution order를 정한다. Instruction이 conflict하면 latest가 이기며 older를 먼저 실행하지 않는다. 이에 맞춰 instruction을 뒤집는 director는 이전 instruction을 명시적으로 void하는 *새* message를 보낸다.

#### Closure: adversarial review gate

**어떤 unit도 close하기 전에 worker가 자기 unit 전체 output에 대한 adversarial review를 commission한다.** Placement는 work 완료 뒤, handoff snapshot finalize 전이다.

- **Director가 아니라 worker가 commission한다.** Director를 통하면 worker의 orchestration role을 축소하고 항상 responsive해야 할 유일한 session에 load를 추가한다.
- **원칙적으로 cross-tool** — perspective independence가 목적이므로 reviewer는 worker와 다른 tool 및 model family에서 온다. Capacity 또는 interface 사유가 있을 때만 same-family high-reasoning subagent fallback을 허용한다.
- **Exemption 없음.** Gate는 worker 자신의 tool이나 model family와 관계없이 모든 unit과 worker에 적용된다. Exempt인 worker class도, exemption ground도 없다. Worker family는 어느 reviewer를 고를지만 결정하며 gate 실행 여부는 결정하지 않는다. 이를 명시하지 않으면 모든 worker가 어느 family에든 속하고 각 family의 차례는 내부에서 special case처럼 보여 gate가 전반적으로 optional이 된다.
- **Reviewer quality floor**: reviewer는 자기 family의 top reasoning model을 top reasoning effort로 사용한다. Fallback path에서도 floor를 낮추지 않는다.
- **Model과 effort가 실제 적용되었는지 verify한다.** Model 또는 effort argument를 받고도 조용히 버린 뒤 review prompt text에 섞어 넣는 execution path가 있으며 failure signal도 없다. Verification channel은 실행 tool이 저장한 invocation record다. Field를 완전히 생략할 수 있어 "not applied"와 "not printed"를 구별하지 못하는 log output이 아니며, model 자신의 자기 설명은 절대 아니다. Tool이 invocation을 기록하지 않으면 run은 unverifiable하고 gate를 만족하지 못한다. D4를 참조하라.
- **Moving pointer가 아니라 fixed commit range로 review scope를 정한다.** Moving pointer는 review 실행 중 advance하므로 gate가 final output을 끝내 cover하지 못한다. 정직한 structural residue가 있음을 주의하라. Gate 자체의 product—repair commit, review ledger—는 정의상 자신이 review한 range 바깥에 있다.
- **Worker가 adjudicate한다.** Context를 가진 주체이므로 각 finding을 review하고, 받아들인 것은 repair commit으로 land하며, reject rationale를 기록한다.
- **Review ledger는 handoff snapshot의 section이 된다.** Finding, verdict, repair commit, rejection rationale를 담는다. Section 하나를 추가할 뿐 C3 completion criteria를 redefine하지 않는다.
- **Order**: adversarial review → adjudication and repair → snapshot finalized → closure requested → director verification → shutdown.

**Task completion은 closure approval이 아니다.** Completion signal은 gate 실행 여부를 확인하지 않고 work item을 done으로 표시한다. Director는 무엇이든 cleanup하기 전에 commit, handoff document, review ledger를 verify하며 verification failure 시 item을 failed로 되돌리거나 reassign한다.

**Surface cleanup은 verification 뒤 director의 duty다.** Abandoned surface는 active unit처럼 읽혀 sweep을 오염시키고 resource를 잡아 둔다. 자기 closure를 자기가 approve하는 꼴이므로 worker는 자기 surface를 close하지 않는다. 규칙은 대칭적이다. Verification 전 close 금지, verification 후 close 의무다.

**Director turnover에서는 surface를 살려 둔다.** Director 자신의 context가 exhausted되면 session은 교체하되 surface는 닫지 않는다. Coordinator address가 surface에 binding되어 있기 때문이다. Surface를 유지하면 모든 worker report path와 dispatch record가 valid하게 남고 worker가 address를 다시 찾을 필요가 없다. Operating ledger(C4)는 successor에게 필요한 내용을 담고 turnover snapshot은 별도 volatile file이다. Handover list에는 **unfulfilled notification duty**, 즉 outgoing director가 worker에게 보내야 했지만 아직 보내지 못한 것을 명시한다. 공백 동안 worker는 평소처럼 report하고 escalate한다.

### 왜 존재하는가

각 invariant의 failure mode는 해당 invariant 옆에 적혀 있다. 그것이 non-negotiable하게 만드는 근거이기 때문이다. 일반 관찰은 하나다. Multi-agent setup에서 지배적인 failure class는 잘못된 action이 아니라 **성공하지 않았는데 success를 반환하는 action**이다. Accept되었지만 delivery되지 않은 message, accept되었지만 적용되지 않은 model argument, 도착했지만 읽히지 않은 report, 작동했지만 report되지 않은 repair가 그 예다. 여기의 모든 invariant는 return value를 신뢰할 수 없는 무언가에 verification path를 붙인다.

### 도입 방법

1. 세 role의 이름을 정하고 각 role이 *하지 않는 것*을 적는다. Prohibition이 permission보다 더 큰 하중을 받는다.
2. Authority-routing discriminant를 worker가 읽지 않을 수 있는 policy document가 아니라 모든 assignment spec의 standing clause에 둔다.
3. Director에게 fixed cadence의 written sweep list를 주고 unconditional sweep item을 표시한다.
4. Closure sequence를 정의하고 completion signal을 prose와 구조적으로 구분한다.
5. Adversarial review gate에 verification requirement를 포함해 쓴다. Model/effort confirmation과 fixed commit range가 가장 자주 빠지는 두 부분이다.
6. Path-group registry를 추가하고(flat list여도 된다) assignment 시점에 검사한다.
7. Report content rule과 length cap을 정한다. Narrative는 durable receipt로 보낸다.

### 의존 관계 / 없으면 깨지는 것

- **C1** — worktree isolation이 없으면 parallel worker가 서로를 훼손하며 assignment discipline으로 해결할 수 없다.
- **C3** — session boundary와 handoff criterion이 없으면 "unit"에 closure semantics가 없고 closure gate가 gate할 대상도 없다.
- **C4** — director 자신의 state management는 C4 classification test를 director role에 적용한 것이다.
- **C2 / B2** — duplicate scan과 issuance-order mediation은 모두 numbered-resource discipline을 전제로 한다.
- **D2** — runtime capability slot을 제공한다. 이것이 없으면 director는 dispatch, wait, enumerate할 수 없고 role discipline은 sequential operation으로 약해진다(D2 degradation mapping 참조).
- **D3** — D1이 routing하는 approval procedure의 *content*를 제공한다.
- **E1** — director verification step은 validator result를 검사한다. Wired validation이 없으면 verify할 대상이 없다.

### 변경한다면

전체로서 CORE다. 내부의 개별 **PARAMETER**는 report length cap(원본의 10줄과 20줄은 director 한 명의 capacity에 맞춘 것이다. 여유 capacity가 있으면 늘리고, assignment decision이 reading 뒤에서 queue되면 줄인다), sweep cadence, sweep item 수다.

**Role count**는 CORE보다 DEFAULT에 가깝다. Request volume이 낮으면 director와 worker만 있는 two-role setup도 작동한다. Desk는 intake가 assignment design 뒤에서 queue되지 않게 하려고 존재한다. Collapse할 수 없는 것은 director-versus-worker split이다. Real work를 하는 director가 바로 이 메커니즘 전체가 막는 failure다.

---

## D2 — Coordination runtime capability slot

**Tier: CORE**인 slot specification — D1의 role discipline이 작동하려면 이 다섯 capability가 어떤 형태로든 있어야 한다. 특정 implementation은 모두 OPTIONAL이며, 아래 fallback을 사용하면 coordination runtime이 전혀 없는 프로젝트도 D1을 도입할 수 있다.

### 이것은 무엇인가

Harness는 coordination tool을 지정하지 않는다. 다섯 capability와 각 capability가 보장해야 할 invariant를 지정한다. Adopter가 implementation을 공급한다.

먼저 cross-cutting rule 하나가 있다. **Runtime의 subcommand나 flag를 procedure에 hardcode하지 않는다.** Operation을 개념적으로 설명하고 실행 시점에 runtime 자체의 version-matched guide에서 concrete command form을 resolve한다. Flag 이름을 적은 procedure는 tool update 시 조용히 썩고, unit 도중 설명할 수 없는 failure로 처음 발견된다.

두 번째 cross-cutting rule은 **runtime coordination state가 globally volatile**하다는 것이다. Runtime이 reinitialize되면 work item, dispatch record, message가 사라진다. 따라서 assignment spec은 message body에 state를 담지 않고 *committed document를 point*하며, completion payload는 작업 내용에 대한 prose description이 아니라 commit hash와 path를 담는다. Runtime보다 오래가야 하는 것은 모두 repository에 둔다(C4).

#### 다섯 slot

**1. Work item registry.**
*Operation*: stable identifier가 있는 work item을 만들고, state를 query하며, transition한다.
*Invariant*: **ownership은 surface handle이 아니라 work-item identifier에 binding된다.** Handle은 process restart와 runtime reinitialization 때 rotate한다. Handle 기반 ownership model은 surface가 처음 restart될 때 누가 무엇을 소유하는지 잃는다.
*Breaks without it*: director가 "what is in flight"에 답하려면 물어보는 수밖에 없고, 이는 push-dependent라 신뢰할 수 없다.

**2. Fixed report destination을 가진 dispatch record.**
*Operation*: work item을 worker에 binding하는 assignment를 기록하고, 해당 assignment의 모든 report를 받을 coordinator address를 등록한다.
*Invariant*: report destination은 **worker가 받은 어떤 message와도 독립적으로 resolve 가능**해야 한다. Incoming message의 sender에게만 reply할 수 있으면 report는 director가 기다리는 address가 아니라 마지막으로 말한 address로 간다.
*Additional requirement*: send 직전에 live surface listing과 address를 다시 verify한다. Environment에 저장된 address가 runtime이 현재 관리하는 address와 달라질 수 있다.
*Breaks without it*: report가 delivery되지만 perceive되지 않는다(D1의 주 failure).

**3. Class filter가 있는 blocking wait.**
*Operation*: 지정 class set의 event가 오거나 timeout될 때까지 block한다.
*Invariant*: filter는 worker가 emit할 수 있는 **모든** class—최소한 completion, escalation, decision gate, plain status report—를 이름 붙일 수 있어야 한다. Timeout 시 error가 아니라 "nothing arrived"와 구별 가능한 result를 반환해야 한다.
*Breaks without it*: filter에서 빠진 class는 unread로 쌓이고 director는 worker가 idle하다고 결론 낸다. Timeout이 failure와 구별되지 않으면 director는 live worker를 kill한다.
*Usage requirement*: wait를 return 시 restart하는 background loop로 실행해 director가 언제나 무언가를 기다리게 한다.

**4. Completion signal.**
*Operation*: prose나 terminal output과 구분되는 structured signal로 work item을 transition하고 wait를 wake한다.
*Invariant*: **Prose 작성만으로 만족시키는 것이 불가능**해야 한다. Narrative output을 completion으로 오인할 수 있으면 closure detection은 reading-comprehension problem이 된다.
*Explicit non-guarantee*: signal은 closure precondition 충족을 **verify하지 않는다**. 이 분리를 눈에 보이게 유지하라. D1 closure gate는 director가 signal을 approval로 취급하지 않는 데 의존한다.

**5. Work-surface listing.**
*Operation*: active work surface와 current address, liveness를 enumerate한다.
*Invariant*: live surface와 dead surface를 구별하고, runtime list에는 있지만 아무것도 occupy하지 않은 ghost를 expose해야 한다.
*Breaks without it*: director는 cleanup할 수도, send 전 address를 verify할 수도 없고, sweep은 점차 stale entry로 가득 차 reality를 반영하지 못한다.

#### 다섯 slot 모두에 적용되는 한 속성

**Success return은 effect의 evidence가 아니다.** 원본 프로젝트 runtime에서는 send가 success를 반환했지만 recipient inbox에는 아무것도 없었고, submission이 accept되었지만 submit되지 않았다. 모든 slot에는 independent confirmation path가 필요하다. Return value를 읽지 말고 recipient가 행동하거나 item이 transition하는 등 effect를 관찰해 delivery를 confirm한다. Incident마다 따로 발견하지 말고 procedure에 이 expectation을 넣는다.

### 왜 존재하는가

Slot specification이 없으면 "use a coordination tool"은 실행 불가능한 advice이고, D1 mechanism은 requirement가 아니라 tool-specific trivia처럼 읽힌다. Slot을 이름 붙이면 harness가 필요한 것과 한 tool이 우연히 제공하는 것을 분리하므로 adopter는 candidate runtime을 써보다가 effort 중간에 gap을 찾는 대신 checklist에 대조할 수 있다.

또한 specification을 tool churn에서 보호한다. 위 invariant는 underlying runtime의 여러 version보다 오래 살아남았고 flag는 그렇지 않았다.

### 도입 방법

1. Candidate runtime을 다섯 slot과 invariant에 대조해 evaluate한다. 실패하는 invariant를 기록한다. 바로 그 failure mode를 겪게 된다.
2. Parallel effort를 시작한 뒤 첫 사용 시가 아니라 *전에* runtime availability를 verify한다. Coordination layer가 optional 또는 experimental feature에 의존하면 enabled인지 확인한다.
3. Newly spawned worker마다 work를 assign하기 전에 **read-only round-trip check**를 실행한다. Worker 자신의 surface에서 runtime state와 worker inbox를 query한다. Round-trip이 실패한 worker에게는 work를 주지 않는다. Silent-non-delivery class를 가장 싼 시점에 잡는다.
4. Concrete command는 실행 시 resolve하고 procedure는 slot name을 기준으로 작성한다.
5. 모든 assignment spec이 state를 직접 담지 않고 committed document를 point하게 한다.

### 의존 관계 / 없으면 깨지는 것

- **D1** — D1을 지원하기 위해 존재한다. Slot은 tool feature list가 아니라 D1 invariant에서 도출된다.
- **C3** — assignment spec은 committed handoff document를 point하며, 그러려면 document가 존재하고 canonical이어야 한다.
- **C4** — durability boundary를 제공한다. Runtime에 든 것은 정의상 volatile이고 살아남아야 하는 것은 repository로 간다.

### 변경한다면

Slot spec은 CORE다. **Implementation은 OPTIONAL이며 precondition은 coordination runtime이 존재하는 것**이다. Runtime이 없는 프로젝트도 degraded sequential form으로 D1 role discipline을 도입할 수 있다. Degradation mapping은 다음과 같다.

| Slot | Coordination runtime이 있을 때 | 없을 때 |
|---|---|---|
| Work item + state query | id와 state가 있는 runtime task record | Committed assignment queue file, unit마다 한 row, column에 state |
| Dispatch record + fixed report destination | dispatch record에 등록된 coordinator address | Known path 아래 commit으로 report가 land한다. "destination"은 path 자체이며 rotate하지 않는다. |
| Blocking wait with class filter | Class filter가 있고 return 시 restart하는 wait call | 다음 session이 startup 때 queue와 report path를 읽는다. "wait"는 session boundary다. |
| Completion signal | Structured done message | 특정 machine-checkable marker를 가진 committed receipt. Validator가 presence를 assert할 수 있다. |
| Work-surface listing | Surface/session enumeration | Worktree listing + branch listing. Stale해질 수 없으므로 오히려 더 reliable한 경우가 많다. |

Sequential fallback이 잃는 것은 real concurrency와 두 agent의 live contest를 arbitrate하는 능력이다. 유지하는 것은—바로 이것이 핵심인데—role discipline 전체다. Assignment는 여전히 work보다 먼저 일어나며 assigning turn은 여전히 real work를 하지 않는다. Approval은 summarizing intermediary가 아니라 user에게 직접 간다. Unit은 close 전에 여전히 adversarial review를 통과한다. 한 path group에는 한 번에 한 writer만 있다(한 worker뿐이므로 자명하다). Closure는 assertion이 아니라 verified state다. Concurrency-arbitration 관련 invariant를 제외한 모든 D1 invariant가 degradation 뒤에도 살아남는다. Coordination runtime이 없는 adopter는 D1을 생략하지 말고 이 형태로 도입해야 한다.

다른 runtime으로 대체한다면 다섯 invariant 전부, 특히 조용히 실패하는 slot 2의 independently-resolvable destination과 slot 3의 exhaustive class filter를 보존해야 한다.

---

## D3 — 승인 경계

**Tier: CORE** — 이것이 없으면 agent가 structural change를 적용한 다음 논의하며, design conversation을 rollback negotiation으로 바꾼다.

### 이것은 무엇인가

Structural, contract-level, schema-level change는 고정 sequence를 따른다.

**1. Standalone turn에서 observation을 prose로 report한다.** Structured question을 하기 전에 무엇을 발견했고, 상황을 어떻게 이해하며, 어떤 flow를 의도하는지 ordinary prose로 다른 내용을 넣지 않은 한 turn에 말한다. Courtesy가 아니라 mechanical requirement다. Tool call과 같은 turn에 둔 text는 user에게 아예 닿지 않을 수 있고 option description 안에 압축된 explanation은 explanation으로 읽히지 않는다. 그러면 user는 framing을 한 번도 보지 못한 채 option을 고른다.

**2. Structured question으로 direction을 align한다.** 원본 프로젝트의 규칙은 서로 다른 angle을 다루는 question을 최소 세 개, question마다 실제로 선택 가능한 option을 최소 세 개 제공하는 것이다. User answer에 directive가 들어 있으면 다음 question 전에 그 directive를 실행한다.

**3. Synthesize하고 다시 confirm한다.** Answer에서 조립한 resolution을 제시하고 finalize 전에 confirm받는다. 각각의 question에 대한 answer가 합쳐지면 user가 의도하지 않은 전체가 될 수 있으며, synthesis step이 이를 드러낸다.

**4. Explicit approval을 얻는다.**

**5. Approved scope만 execute한다.**

두 absolute rule이 이 위에 놓인다.

**Review 또는 design round 중에는 아무것도 apply하지 않는다.** Approval 없이 적용된 것은 apology와 함께 유지하지 않고 revert한 뒤 approval request로 다시 제출한다.

**Action approval은 wording approval이 아니다.** 무언가를 incorporate하라는 instruction은 incorporation을 authorize하지만 특정 clause text를 authorize하지 않는다. Canonical wording은 land 전에 보여주며 두 approval을 distinct event로 기록한다.

Boundary는 contract-level 및 structure-level matter에 적용한다. Mechanical execution work에는 **적용하지 않으며**, 거기 적용하는 것 자체가 failure다. Routine action마다 interview하면 user는 읽지 않고 approve하는 습관을 들이고, 중요한 곳에서 정확히 signal을 파괴한다.

**Repository 바깥에 접근하는 일은 별도 approval axis이며 위 boundary와 직각으로 교차한다.** Web search, page fetch, external material import는 일반적인 do-the-work instruction에 포함되지 않는다. 그 instruction은 work를 authorize할 뿐 reach를 authorize하지 않는다. 이 축은 contract-versus-mechanical 구분과 독립이다. 순전히 mechanical work 중 external fetch도 별도 authorization이 필요하고, approved contract change가 이를 딸려 보내지도 않는다.

그 authorization의 scope는 **session이 아니라 purpose로** 자른다. Composition standard가 citation을 요구하거나 review가 claim을 original과 대조해야 하는 것처럼 procedure 자체의 contract가 trustworthy source를 요구하는 경우, *그 source 취득을 위한* external access는 task approval에 포함된다. 그 수단 없이는 task를 수행할 수 없고 유일한 실행 수단을 거부하면서 task를 approve하는 것은 coherent하지 않기 때문이다. 다른 모든 purpose는 별도 approval 상태로 남는다. 악용되는 방향 때문에 cut이 중요하다. Cited source 하나를 fetch하라는 approval은 같은 session의 다른 것을 search하라는 approval이 아니며, session은 permission이 attach되는 unit이 아니다.

### 왜 존재하는가

한 round에서 review를 제시하고 recommendation을 apply하는 agent는 conversation의 대상을 바꾼다. User objection은 design question으로 논의되는 대신 committed state를 revert하는 일로 실행되어야 한다. 이미 적용된 change는 discussion을 bias한다. 이미 끝난 일을 반대하기가 proposal을 반대하기보다 어렵고 양쪽 모두 sunk cost를 느낀다.

Prose preamble이 없는 structured question은 informed하지 않은 approval을 만든다. User는 framing을 보지 못한 question의 세 option 중 하나를 고르고, resulting approval은 충분히 숙고한 decision처럼 기록된다.

Question 세 개 미만 또는 question당 option 세 개 미만은 agent가 token alternative를 장식해 preferred answer를 제시하는 형태로 퇴화한다. User는 rubber-stamp하고 evidence chain은 agent judgment를 user decision으로 기록한다. 세 개보다 훨씬 많으면 cost가 역전된다. Interview가 govern하는 change보다 커지고 user는 batch-approve하기 시작한다.

Wording confirmation을 건너뛰면 모든 future session을 binding하는 document에 누구도 approve하지 않은 canonical text가 생긴다. Incorporate하라는 instruction은 실제였지만 resulting clause는 agent가 작성했고 user가 exact term을 endorse한 것처럼 취급된다.

"Do the work"가 external access까지 포괄한다고 읽는 agent는 user가 delegate하지 않은 decision을 내린다. 무엇이 repository를 떠나고, 무엇이 어디에서 들어오는지다. 두 방향 모두 instruction이 가격을 매기지 않은 cost가 있다. Outbound 방향에서는 query 안의 것이 밖으로 나간다. Inbound 방향에서는 provenance가 unknown인 material이 layering(A1)의 존재 이유인 provenance가 있는 material 옆에 land하며, 누구도 change로 분류하지 않은 action으로 layer boundary를 넘는다.

### 도입 방법

1. Operating contract에 5단계 sequence를 작성하고 standalone-prose-turn requirement를 mechanical constraint로 명시하며 이유를 붙인다.
2. Scope에 속하는 change를 정의한다. Structure registry, layer contract, procedure, quality standard처럼 구체적으로 쓰고 mechanical work는 out of scope임을 명시한다.
3. Question 및 option count와 reasoning을 정한다.
4. Pre-applied change에 대한 revert-and-resubmit rule을 추가한다.
5. Action과 wording이라는 두 approval kind를 분리하고 둘 다 기록한다.
6. External access를 자체 axis로 쓰고 purpose-scoped carve-out을 바로 옆에 둔다. 다른 document에 carve-out을 두면 아무도 기억하지 않는 exception으로 읽혀, reader가 어느 쪽을 추측하느냐에 따라 blanket permission 또는 blocked procedure가 된다.

### 의존 관계 / 없으면 깨지는 것

- **B1 (event chain)** — user own words로 무엇이 approve되었는지를 durable record로 남기지 않으면 approval은 무가치하다. Evidence chain이 없으면 approval은 session을 넘지 못하는 conversation 안에만 존재한다(C3의 conversation state does not transfer rule이 여기도 완전히 적용된다).
- **B3 (promotion ladder and preference lifecycle)** — D3는 change를 *어떻게* approve할지 govern하고, B3는 evidence가 rule이 될 *자격이 있는지*를 govern한다. B3가 없으면 feedback 하나가 바로 approval interview로 가서 data point 하나로 global rule이 된다.
- **D1** — D1은 interview를 *누가* 수행할지(executing worker, 절대 director 아님) 정한다. D3는 interview가 무엇인지 정한다. D1 no-relay rule 없이 D3를 도입하면 잘 짜인 approval process를 틀린 party와 수행하게 된다.

### 변경한다면

**Three-questions / three-options count는 PARAMETER**다. 원본은 contract-grade change에만 세 개와 세 개를 사용했다. 수를 늘리면 interview fatigue 비용으로 coverage를 얻고, 세 개 미만으로 낮추면 장식을 붙인 single recommendation 쪽으로 무너진다.

대안은 세 속성을 보존해야 한다. **Multi-angle coverage**—question은 preferred answer를 단순 확인하는 것이 아니라 실제로 answer를 바꿀 수 있어야 하며, 모두 같은 방향을 가리키는 question set은 하나의 question이다. **Genuine alternative**—각 option은 agent가 실제로 implement할 의사가 있는 것이어야 한다. **Synthesis re-confirmation step**—각각 합리적인 answer가 불합리한 전체로 합쳐질 수 있고, 개별 question만으로 잡지 못하는 failure가 이것이기 때문이다.

Prose-first turn과 no-pre-application rule은 parameter가 아니다. 이 둘이 메커니즘이다.

External-access axis도 parameter가 아니다. 달라지는 것은 carve-out이다. Procedure가 external source를 전혀 요구하지 않는 프로젝트에는 적을 carve-out도 없으며, question을 open 상태로 두지 말고 없다고 말해야 한다. Answer하지 않은 carve-out question은 처음 필요해진 순간 answer가 yes이기를 원하는 agent가 ad hoc으로 answer한다.

---

## D4 — Delegation 규율

**Tier: CORE**(task-class-to-tier map은 **DEFAULT**). Delegation은 session이 자기 context를 넘어서는 방법이며, discipline 없는 delegation은 work처럼 읽히지만 work가 아닌 것을 반환한다.

### 이것은 무엇인가

서로 다른 delegated-result failure를 닫는 다섯 규칙이 있다.

**Task class에 따른 tier.** Investigation과 mechanical verification은 lighter model에 보내고, full-rewrite-level generation은 available한 가장 강한 model에 보낸다. 중요한 것은 구체적 이름이 아니라 class다. Corpus를 읽고 내용을 report하는 일은 lower tier에서 완만하게 degrade하지만 blank page에서 document를 작성하는 일은 그렇지 않다.

**Launch label과 completion report 양쪽에 model과 reasoning effort를 명시한다.** Courtesy가 아니라 다음 규칙을 check 가능하게 만드는 요소다. **누구도 직접 입력하지 않은 값도 포함한다.** Session default에서 inherit한 model 또는 effort level도 argument로 전달한 값과 똑같이 명시한다. Omitted field는 "inherited"가 아니라 "not applicable"로 읽히며, inherited value야말로 아무도 이 task를 위해 의도적으로 고르지 않은 값이기 때문이다. 조용히 잘못된 tier로 실행되는 delegation은 wrong argument를 가진 것이 아니라 argument가 전혀 없는 것이다.

**실제 tier 적용 여부를 executing tool 자체 record로 verify한다.** Model 또는 effort argument를 받아 failure signal 없이 버리는 execution path가 있다. 더 나쁘게는 forwarding agent나 자기 contract가 "leave effort unset unless explicitly requested"라고 말하는 wrapper 같은 intermediary가 tool이 보기 전에 argument를 strip할 수 있다. 이때 tool은 거짓말하지 않는다. 애초에 전달받지 못했다. Verification channel은 *tool*이 작성하는 record, 즉 stored invocation이어야 한다. Log output도, model 자신의 자기 설명도 아니다. Model을 생략한 log는 model을 무시한 run과 구별할 수 없다.

**Non-mechanical work는 agent당 artifact 하나다.** 세 document를 쓰라는 agent는 첫 document는 잘 쓴다. Sweep, format conversion, link rewiring 같은 mechanical pass는 breadth에 따라 quality가 떨어지지 않으므로 exempt다.

**Report가 아니라 assembly를 verify한다.** Delegated component는 받은 test를 전부 pass하고도 자신이 속할 전체에 맞지 않을 수 있다. Receiving session의 check는 "report가 true인가"가 아니다. 대개 true다. "assembled whole이 run하는가"를 검사한다.

위 다섯 규칙은 delegation을 *어떻게* execute할지를 govern한다. 세 규칙이 더 있어 delegation이 *일어날지*, 얼마나 *깊어질 수 있는지*, 일찍 멈추면 *무엇을 할지*를 govern한다. Execution 전후의 질문이며 가장 자주 쓰이지 않는 부분이다.

**When not to delegate는 when to delegate만큼 규칙이다.** Full context를 tightly control해야 하는 task, user가 실제로 뜻한 것을 interpret해야 하는 task, sensitive judgment가 필요한 task, thread를 가진 session이 지금 decision을 내려야 하는 task는 delegate하지 않는다. 정말 independent perspective가 필요할 때—자기 prior reading과 assumption에 물들지 않은 agent의 관점—, 제한된 context와 함께 work를 전달할 수 있고 orchestrating session이 execution보다 orchestration에 더 가치 있을 때, task가 크고 boundary가 clear할 때, 서로 다른 area를 parallel로 explore할 수 있을 때 delegate한다. 그리고 user가 delegation을 요청하지 않았고 delegation이 cost, latency, scope, user가 볼 수 있는 것 중 하나라도 바꾼다면 delegate 전에 묻는다. 이 네 축 중 하나라도 걸리면 delegation은 private working-method choice가 아니라 user situation에 관한 decision이 된다.

Negative half가 빠지는 이유는 careless해서가 아니라 structural하다. Delegation rule은 delegation을 잘하는 방법을 생각하는 사람이 작성하므로 실제로 일어나는 delegation을 위한 quality control이 축적되고, 일어나지 말아야 할 delegation은 언급하지 않는다. Positive half만 읽은 agent는 delegation이 default이며 이 규칙은 원활하게 수행하기 위한 것이라고 결론 낸다.

**Sub-delegation은 default로 recurse하지 않는다.** 자신도 delegate된 agent는 다시 onward delegation하지 않는다. Onward delegation이 실제로 도움이 되면 진행 전에 위 level에 report하고 그 사실을 말한다. 자신이 무엇을 결정하는지 볼 수 없는 session을 대신해 결정하지 않는다. Control 대상은 depth다. 각 level은 original intent를 자기 말로 다시 표현하므로 third-level agent는 paraphrase의 paraphrase에서 일하고, 위로 돌아오는 report는 계속 first-hand처럼 읽힌다. Exception은 존재한다. Clearly efficient한 경우 recursion을 허용할 수 있지만 아래 level이 가져가는 권한이 아니라 위 level이 부여하는 권한이다.

**Interrupted delegation은 restart 전에 resume한다.** Usage limit, network failure, tool error로 delegated run이 끊기면 첫 질문은 fresh agent를 launch할지가 아니라 이미 한 work를 이어받을 수 있는지다. Restart가 더 쉽게 설명되는 reflex이지만 real time이 든 accumulated context를 버리고 output이 이미 disk에 있을 수도 있는 work를 다시 한다. D1이 mid-unit에 죽은 worker에 적용하는 것과 같은 principle을 한 level 아래에 적용한다. Session을 respawn하지 말고 recover한다.

**Tier name이 사는 위치 자체가 규칙이다.** 어떤 task kind가 available한 가장 강한 model로 가고 어떤 것이 lighter model로 가는지 정하는 class-to-tier *role* map은 이 specification과 repository canonical contract에 속한다. Tool이 바뀌어도 role은 바뀌지 않기 때문이다. 그 role을 채우는 구체적인 *name*은 tool과 함께 바뀌며, 해당 tool이 실행될 때 반드시 load되는 surface인 tool own entry file에 속한다. 따라서 이 specification은 어디에도 model 이름을 적지 않으며 그 silence는 omission이 아니라 deliberate하다. 여기에 적힌 name은 모든 adopter에게 틀리고 원본 프로젝트에서도 stale해질 것이다. **F6**가 이 split의 entry-file side—file과 canon의 관계, 무엇을 duplicate할 수 있는지, canonical rule이 바뀌면 어떻게 되는지—를 소유한다. Placement question을 두 번 해결하지 않는다.

다른 곳의 두 규칙은 delegation 시점에 읽히므로 여기서 다시 적는다. Delegated execution은 numbered resource를 발급하지 않으며(B2), document rebuild는 original을 읽지 않은 agent가 작성한다(B4).

### 왜 존재하는가

**Delegated component는 자기 test 89개를 pass했지만 assembly가 시작되지 않았다.** 같은 kit의 starter configuration은 한 top-level key를 사용했고 옆에 ship된 engine은 다른 key를 기대했다. 각 half는 내부적으로 correct했고 separately verified되었다. Receiving session은 kit를 empty repository에 복사하고 documented first command를 실행해 이를 발견했다. 어느 test suite도 하지 않은 바로 그 일이다. Report를 그대로 accept했다면 unit을 passing으로 기록했을 것이다.

**지정된 reasoning effort가 조용히 drop되어 review가 floor보다 한 tier 낮게 실행되었다.** Forwarding layer의 own contract는 user가 explicitly ask하지 않으면 effort argument를 pass하지 말라고 했고, 따라서 argument는 tool에 도달하지 않았다. Log에는 model이나 effort line이 전혀 없었다. Scope는 정확했고 실제 finding도 있어 run은 완전히 normal해 보였다. Tool stored invocation record를 비교해서야 다른 run에는 있던 field가 여기 없음을 알 수 있었다. "log가 올바르게 보이는가"가 check였다면 pass했을 것이다.

**세 document를 받은 agent는 하나는 잘 쓰고 나머지 둘은 첫 문서의 summary처럼 쓴다.** Breadth는 output에서는 보기 어렵고 일주일 뒤 다시 읽을 때는 분명한 방식으로 depth를 희생한다.

### 도입 방법

1. Task-class map을 delegation 시 agent가 실제로 읽는 document에 명시한다. 사후에 보는 policy file에 두지 않는다.
2. Launch label과 completion report에 model 및 effort를 prose가 아니라 fixed field로 요구한다.
3. Tooling이 실제 invocation을 어디에 기록하는지 찾고 *그것*을 verification channel로 삼는다. 아무것도 기록하지 않는다면 그것이 finding이다. Confirm할 수 없는 quality floor는 지킬 수 없다.
4. Non-mechanical delegation을 agent당 artifact 하나로 제한하고 어떤 work가 mechanical인지 밝힌다.
5. Receiving check를 assembly check로 만든다. Delegated component가 실제로 살 위치에서 newcomer가 사용할 path로 실행한다.
6. Delegating criterion과 같은 곳에 withholding criterion을 쓴다. When to delegate list와 when not to list를 따로 두면 첫 list를 찾은 모두가 그것을 전체 규칙으로 읽는다.
7. Tier role은 canonical contract에, tier name은 각 tool entry file에 두고, 한쪽 변경이 다른 쪽의 hand edit를 요구하지 않는지 검사한다(F6).
8. 필요해지기 전에 resumption check를 정한다. Delegated run이 무엇을 남겨 successor가 이어받을 수 있는지, 어디에 남기는지다. Recoverable artifact가 없는 resumption rule은 빈 곳을 검사하라는 instruction이다.

### 의존 관계 / 없으면 깨지는 것

- **D1** — delegation을 ad-hoc habit이 아니라 orchestration act로 만드는 role structure다. D1 adversarial-review gate에서 tier-verification rule이 처음 필요해졌다.
- **B2** — delegated execution의 no-issuance rule을 제공한다.
- **B4** — rebuild protocol의 role split은 이 discipline을 특정 job에 적용한 것이다.
- **E3** — assembly check는 fixture question이다. Assemble하지 않는 component test는 integration과 정확히 같은 모양의 hole이 있는 fixture set이다.
- **F6** — tier-name placement rule은 entry-point split을 delegation에 적용한 것이다. Role은 canon, name은 tool file에 둔다. F6가 없으면 name이 살 tool file도 없고, name은 canon으로 이동해 다음 tool change에서 fail 없이 틀리게 된다.

### 변경한다면

Tier map은 **DEFAULT**다. Tier와 task class는 프로젝트가 정한다. 대안이 보존해야 하는 것은 delegation 전에 존재하는 stated class-to-tier rule, delegate가 아니라 tool이 작성하는 verification channel, assembled whole을 exercise하는 receiving check다. 세 번째를 버리면 report에서는 pass하는 unit을 얻게 된다.

여기에 stated withholding rule을 추가한다. 어떤 task를 do-not-delegate 쪽에 둘지는 프로젝트가 정하며 서로 다를 수 있다. 그런 쪽이 아예 없는 것은 이 메커니즘의 variant가 아니라 absence다. Good delegation만 설명하는 discipline은 delegation을 권장하는 글로 읽히기 때문이다.

---

## English brief

This chapter defines repository-safe parallelism through isolated worktrees, serialized issuance, durable handoffs, single-writer ownership, and verified orchestration. It separates human approval from agent arbitration and treats runtime coordination state as volatile while keeping durable state in the repository. Delegation and closure require verified model bindings, fixed review scopes, and assembly-level checks rather than trusting prose or successful return values.
