# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

두 독자가 대등하다. 충돌 시 한쪽을 자동으로 우선하지 않는다 (사용자 확인, 2026-08-03).

1. **채용 담당자·면접관** — 방송·미디어 기술직 및 백엔드 경력을 평가하는 사람. 이력서와 포트폴리오로 역량을 검증하고, 위키·블로그에서 학습의 깊이와 지속성을 확인한다.
2. **김정도 본인** — 학습 시스템의 운영자이자 사용자. 개념 위키를 시험·학습 체계로 축적하고, 블로그에 구축 과정을 기록한다.

부차 독자: 위키·블로그를 읽으러 오는 외부 학습자·동료 개발자.

## Product Purpose

김정도의 개인 사이트. 이력서(Resume), 포트폴리오(Portfolio), 빌드 로그 블로그(Blog), 개념 학습 위키(Concept Wiki)의 네 영역으로 구성된다.

성공의 정의: (1) 방송·미디어 기술직 전환을 실질적으로 뒷받침하는 채용용 증거물로 기능하고, (2) 동시에 본인이 계속 쓰는 지식 시스템으로 살아 있는 것. 한쪽만 충족하는 상태는 성공이 아니다.

## Positioning

"설명에 그치지 않고, 동작하는 결과와 기록으로 증명하겠습니다" (랜딩 인용문, 기존 확정 카피).

이웃 사이트가 베낄 수 없는 주장: ERP 백엔드 실무(전자세금계산서 발행 안정화, 동시성 제어, 레거시 이전)라는 검증된 경력 위에, 신호처리·전파·방송·통신 도메인을 1,399개 canonical 개념 카탈로그(15개 topicDomain)로 직접 구조화해 가는 **전환 과정 자체가 공개된 증거**라는 점. 포트폴리오의 서술 축은 "무엇을 만들었나"가 아니라 문제 → 판단 → 결과다.

## Operating Context

- 커리어 방향: 백엔드 개발자(이카운트, 약 1년, 2026-07 종료) → **방송·미디어 기술직 전환** (사용자 확인, 2026-08-03). 위키의 도메인 구성(신호처리, 전파·안테나, 방송 미디어, 이동통신, 정보통신 법규, 일반상식 등 15개 topicDomain — 2026-08-06 분류 재설계, 규범 `knowledge/guides/taxonomy.md`)은 이 전환 준비와 연결된다.
- 위키 파이프라인: 원본 inventory 1,157건 → canonical catalog 1,399건(원자성 검토·분류 재설계 반영, 2026-08) → 작성 큐 → 공개 문서(현재 7건). 홈은 전체 노드를 렌더링하지 않고 도메인·최근 문서만 노출하며, 전체 탐색은 분할 검색 인덱스(`search/wiki/*.json`)가 담당한다.
- 블로그는 위키의 정형 교육 문서와 분리된 시계열 빌드 로그다.
- 저장소는 AGENTS.md 운영 계약(레이어 구분, `schema/` 증거 체인, `layout.yaml` 구조 선언 레지스트리, `scripts/check.sh` 게이트)의 지배를 받는다.

## Capabilities and Constraints

- 정적 HTML/CSS/JS, 프레임워크 없음. GitHub Pages 배포 (`.nojekyll`, `feed.xml`, `sitemap.xml`, `robots.txt` 존재). 빌드 산출 지표는 `build-report.json`에 기록된다.
- 테마 시스템: 공통 구조(`styles/core.css`, `styles/wiki-document.css`) + 테마 토큰(`styles/themes/atlas.css`, `pixel.css`) 2종 전환 구조, 라이트/다크 모드 지원. 이 계약은 블로그 글(theme-contract)로 문서화되어 있다.
- 콘텐츠 언어: 한국어 본문 + 영문 구조 라벨(RESUME, PORTFOLIO 등).
- **공개 범위 (확정, 2026-08-03): 플레이스홀더 전부를 실제 정보로 교체한다.** URL(`rizingblare.github.io`), GitHub(`github.com/Rizingblare`), 이메일(`rizingblare@gmail.com`)은 2026-08-03 실정보로 교체 완료. 남은 것: 자격증 모형 SVG(`assets/certificates/`) — 실물 스캔은 사용자가 제공해야 하며, 제공 전까지 날조하지 않는다.

## Brand Commitments

- 이름: 김정도 / Jeongdo Kim. 사이트 정체성 문구: "Developer & Knowledge Builder". 랜딩 키커: DEVELOPER · TROUBLESHOOTER · KNOWLEDGE BUILDER.
- 확정 카피: 랜딩 인용문("설명에 그치지 않고, 동작하는 결과와 기록으로 증명하겠습니다")과 포트폴리오 축(문제 → 판단 → 결과).
- 보이스: 과장 없는 증거 중심 서술. 성과는 수치·기록으로 말한다 (약 50회 배포, 3종 RDBMS 등 — 기존 확정 수치).

## Evidence on Hand

- 실무 경력: 이카운트 백엔드 개발자 약 1년(2026-07 종료) — 국세청 전자세금계산서 발행·상태 조회, 낙관적 잠금 기반 동시성 제어, C# → TypeScript 레거시 이전, PostgreSQL/MSSQL/MySQL 운영 경험. `resume/index.html`에 기록됨.
- 포트폴리오 케이스 5건: `portfolio/projects/` (tax-invoice-stability, vat-query-v5, legacy-typescript-migration, knowledge-wiki, mobile-knowledge-sync) + 프로젝트 SVG 자산 `assets/projects/`.
- 자격: 정보처리기사(한국산업인력공단). 현재 스캔은 모형(`assets/certificates/`)이며 실물 반영 예정 — 실정보 공개 방침 확정.
- 위키 실데이터: canonical 1,399건 카탈로그, 공개 문서 7건, 분할 검색 인덱스.
- 부재 사실 (날조 금지): 고객 추천사·언론 보도·벤치마크 수치는 존재하지 않는다. 방송·미디어 분야 실무 경력은 아직 없다 — 전환 "준비 중"이 사실이다.

## Product Principles

1. **증명은 동작하는 결과와 기록으로.** 검증 불가능한 주장을 만들지 않는다. 부재한 증거는 부재한다고 둔다.
2. **두 독자를 모두 지킨다.** 채용용 표면(이력서·포트폴리오)과 학습 시스템(위키·블로그)은 서로를 훼손하지 않는다. 한쪽을 위해 다른 쪽을 장식물로 만들지 않는다.
3. **개념은 원자 단위로 나누고 관계로 다시 연결한다.** 위키는 문서 더미가 아니라 탐색 가능한 카탈로그다.
4. **실명·실정보.** 플레이스홀더는 임시 상태다. 사실이 확정되면 실제 정보로 교체한다.
5. **전환 서사를 숨기지 않는다.** 백엔드 실무에서 방송·미디어 기술로 가는 과정 자체가 이 사이트의 콘텐츠다.

## English Brief

Personal site of Jeongdo Kim (김정도): resume, portfolio, build-log blog, and a concept wiki (1,399 canonical concepts across 15 topicDomains, 7 published documents). Static HTML/CSS/JS on GitHub Pages with a two-theme design system (Atlas / Pixel). Two equal audiences: recruiters evaluating a career transition from backend development (ERP, concurrency control, legacy migration) into broadcast/media engineering, and the owner himself using the wiki as a learning system. All remaining placeholders (site URL, email, certificates) are to be replaced with real information. No fabricated evidence: no testimonials, press, or benchmarks exist, and broadcast-field work experience does not yet exist.
