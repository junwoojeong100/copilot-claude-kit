# Screen Blueprints + 산업 매핑

8개 canonical 화면 archetype과 **산업/focus별 콘텐츠 매핑**. 고객 업무 archetype 3~5개와
`GitHub Ecosystem`, `Microsoft Foundry`, `App Platform(ACA/AKS)` 중 2~3개를 선택해 총 5~8개를
노출하고, 시연 동선은 목적에 필요한 4~6개 핵심 장면으로 압축한다.

공통 shell은 CEO·COO·CFO·CIO 등 청중별 journey selector, route bridge, `다음 장면` CTA를 제공한다.
Dashboard primary action과 공통 scenario trace가 업무 예외→Foundry 의사결정→GitHub 변경→App
Platform 운영을 동일 ID로 연결한다.

---

## 화면 1 — 대시보드 (항상 필수)
**목적**: "전사가 실시간으로 돌고 있다"는 첫인상.
**구성**: 결과형 `hero` → KPI 4개(`.grid-4`, 스파크라인+실시간 변동) → `.grid-2`[스트리밍 라인차트 | 활동 피드] → `.grid-2`[Agent/서비스/배포 상태 | 부문/권역 테이블].
**실시간**: KPI 미세 변동(2s), 차트 스트리밍(1.8s), 피드 prepend(3.5s), 주기 토스트(9s).

## 화면 2 — 운영 콘솔 (도메인 1, 필수) · **실시간 시각화**
**목적**: 핵심 현장 운영을 살아있는 화면으로.
**구성**: KPI 4 → `.grid-2`[SVG 맵/흐름(움직이는 객체) + focus별 primary action | 실시간 상태 테이블].
primary action은 업무 최적화, 트래픽 전환, rollout, 자동 복구처럼 고객 결과가 즉시 바뀌는 동작을 쓴다.
**패턴**: 노드(거점)·엣지(경로)를 SVG로, 객체를 `addTimer`로 경로 따라 이동. 액션 클릭 시 경로 재배열 + KPI 갱신 + 토스트.

## 화면 3 — 예측/시뮬레이터 (도메인 2, 권장) · **슬라이더→게이지**
**목적**: 입력을 바꾸면 결과를 미리 본다("사고 전에 예측").
**구성**: `.grid-2`[슬라이더 3개 | 반원 게이지 + 합격/주의/위험 배지] → 분포 히스토그램 + 통계 → 최근 이력 테이블.
**패턴**: 간단한 모델식 `calc()` → `gauge(v)`로 색/배지. 슬라이더 `oninput`.

## 화면 4 — 분석/개선 (도메인 3, 권장) · **실행→차트/칸반**
**목적**: 문제의 근본원인을 자동 분석하고 개선과제를 추적.
**구성**: `hero`+실행버튼 → `.grid-2`[진행 스텝(타이핑) + Top-N 기여요인 막대 | 효과 KPI + 보드(발굴/진행/완료)].
**패턴**: 버튼/진입 시 `.step` 순차 표시 + `.bar-fill` 막대 채움. 자동 1회 실행은 `addTimer(setTimeout(()=>{const b=$('#runAnalysis');if(b)b.click()},480))`.

## 화면 5 — 재무 인사이트 (권장)
**구성**: `.grid-2`[What-if 슬라이더(원가 변수) → 큰 마진 숫자+상태 | 원가 도넛] → 이상탐지 테이블(전월비·근거 코멘트·상태 배지). 24시간 감시 톤.

## 화면 6 — GitHub Ecosystem (플랫폼 선택)
**구성**: `hero`+"Copilot에 이슈 배정" → KPI 4(리드타임·PR·GitHub Actions·보안검사) →
`.grid-2`[코드 diff 타이핑(`.code .add/.delete`) | 계획→PR→Actions→AKS/ACA 배포 스텝 +
이슈 테이블(상태→PR#)].
**주요 기능**: GitHub Issues·Projects, GitHub Copilot, Pull Requests, GitHub Actions, GitHub Advanced
Security, environment protection. **주요 지표**: lead time, deployment frequency, PR throughput,
review time, CI success, security coverage.
화면 상단에는 enabled business outcome, 사업 KPI 2개, buyer next step을 먼저 보여주고 기술 지표와
Issue-to-PR flow를 뒤에 배치한다.

## 화면 7 — Microsoft Foundry + Microsoft Agent Framework (플랫폼 선택)
**목적**: 임원이 직접 질문하고 Agent들이 협업하며 평가·추적되는 모습을 보여준다.
**주요 기능**: 모델·Agent·도구 연결, prompt/hosted agent, Microsoft Agent Framework orchestration,
knowledge grounding, evaluation, tracing, safety. **주요 지표**: Agent 성공률, P95 latency, 평가
커버리지, 근거 기반 응답률, tool-call 성공률.
초기 viewport에는 Agent 목록보다 의사결정 패키지와 사업 효과를 먼저 보여준다. 통제 증거에는
Microsoft Entra Agent ID, Microsoft Purview, Azure AI Content Safety, Foundry evaluation/trace를
구조화해 표시한다.
**구성**: `.agent-layout`(310px 1fr)[에이전트 목록 + 오케스트레이션 플로우 + "시나리오 실행" 버튼 | 채팅(헤더·로그·추천칩·입력)].
**★ 필수**: 목록의 **모든 행 클릭 시 그 에이전트로 전환**(헤더·아바타·인사·추천질문·답변). 누락하면 "첫 행만 동작"하는 버그.
실제 구현은 `runtime/runtime.js`의 `renderAgents()`가 source of truth다. Extension에서도 아래 lifecycle을 유지한다:
```js
let current = 0;
let conversationVersion = 0;
function selectAgent(index) {
  conversationVersion += 1; // 이전 Agent의 지연 응답 무효화
  current = index;
  renderAgentRows(); // profile 문자열은 escapeHtml 후 렌더
  bindAgentRows();
  renderConversation();
}
function bindAgentRows() {
  $$('#agentList .agent-row').forEach(row => {
    row.onclick = () => selectAgent(Number(row.dataset.index));
  });
}
function ask(question) {
  const originAgent = current;
  const originVersion = conversationVersion;
  addTimer(setTimeout(() => {
    if (originVersion !== conversationVersion || originAgent !== current) return;
    renderSanitizedAnswer();
  }, 800));
}
```
Rich text는 Renderer가 허용한 태그/class만 사용하고, 사용자 입력·일반 spec 문자열은 반드시
`escapeHtml`을 거친다. **오케스트레이션**은 중앙 `.flow-node.core` + 도메인 노드로 구성하고,
"시나리오 실행" 시 노드 순차 `hot` + `<animateMotion>` 펄스 + assistant bubble을 사용한다.

## 화면 8 — App Platform · Azure Container Apps + AKS (플랫폼 선택)
**목적**: workload별 runtime 선택과 배포·확장·보안·관찰성·비용 상태를 한 화면에서 판단.
**구성**: `hero` → enabled business outcome·사업 KPI·buyer next step →
`.grid-3`[platform readiness | SLO 달성률 | 용량 효율] →
`.grid-2`[주요 기능 테이블(ACA revision·traffic split·KEDA·scale-to-zero, AKS node pool·HPA·cluster
autoscaler·GPU·networking, identity·security·observability) | readiness trace + workload 현황] →
4단계 Build→Deploy→Operate→Optimize 루프.
**주요 지표**: SLO, latency, error rate, saturation, replica/node utilization, queue lag, deployment
success, rollback time, cost per workload.
Readiness action은 점수를 올리지 않고 미해결 Gap과 owner·effort를 노출한다. 별도의 remediation plan
action에서만 예상 점수와 예상 효과를 표시한다.

---

## Focus → route scope와 중심 역할

| `DEMO_FOCUS` | 고객 주요사업 5개 | GitHub Ecosystem | Foundry · Agent Framework | App Platform · ACA/AKS |
|---|---|---|---|---|
| **균형형** | 핵심 업무와 가치 흐름 | 계획→PR→Actions | 업무 Agent 협업 | workload 운영과 SLO |
| **AI 중심** | Agent context와 action | Agent 변경의 안전한 delivery | 평가·오케스트레이션 중심 | Agent runtime과 tool endpoint |
| **App Platform·CI/CD 중심** | workload·traffic·capacity·incident | GitHub delivery 중심 | SRE·Release·FinOps 지원 | Actions→ACA/AKS→운영 signal 폐루프 |

제품 역할은 모든 focus에서 이어지지만 화면마다 제품 catalog를 만들지 않는다. `Microsoft Foundry +
Microsoft Agent Framework`, `GitHub Copilot + GitHub Platform`, `AKS + Azure Container Apps`를
각각 지능, 개발·delivery, runtime 역할에 연결한다.

---

## 산업 → 도메인 3종 + 에이전트 매핑 예시
| 산업 | 운영 콘솔(실시간) | 시뮬레이터(예측) | 분석/개선 | 도메인 에이전트(5~6) | 핵심 KPI·단위 |
|---|---|---|---|---|---|
| **레미콘/건설소재** | 레미콘 배차 관제(트럭 이동) | 28일 압축강도 예측 | 공정개선 Six Sigma | 배차·품질·공정·재무·안전·Copilot | 출하 ㎥·배차분·MPa·합격% |
| **금융(은행·보험·증권)** | 거래·이상거래·보험금/주문 관제 | 부도·연체·청구·유동성 위험 예측 | 심사·회수·AML·민원 개선 | 여신·리스크·이상거래·보험금·컴플라이언스·Copilot | 거래건·승인율·오탐률·연체%·VaR/손해율 |
| **유통/리테일** | 매장·물류 실시간 현황 | 수요예측 시뮬 | 재고/폐기 개선 | 수요·재고·가격·CRM·물류·Copilot | 매출·회전율·결품%·폐기 |
| **물류/3PL** | 차량·허브 실시간 관제(맵) | ETA/적재율 예측 | 라스트마일 개선 | 배차·적재·경로·창고·정산·Copilot | 적재율%·리드타임·정시율 |
| **식음료/CPG** | 생산 배치·냉장물류·로트 추적 | 수요·수율·유통기한/폐기 예측 | 품질편차·에너지·폐기 개선 | 수요·생산·품질·공급망·식품안전·Copilot | OEE%·수율%·폐기율%·OTIF·kg/h |
| **제조(일반)** | 라인 OEE 실시간 모니터 | 수율/불량 예측 | 설비예지보전 | 생산·품질·설비·SCM·안전·Copilot | OEE%·수율%·불량ppm |
| **제약/바이오** | 배치·공정·콜드체인 실시간 관제 | 배치 성공률·수율·공급 위험 예측 | 편차·CAPA·라인클리어런스 개선 | 제조·품질·검증·공급망·규제·Copilot | 배치·수율%·편차건·CAPA 리드타임·온도이탈 |
| **헬스케어/병원** | 병상·응급·검사·수술실 현황 | 재원일·노쇼·재입원 위험 예측 | 대기·동선·청구·인력 개선 | 환자흐름·진료지원·검사·청구·안전·Copilot | 병상가동률·대기분·재원일·재입원%·TAT |
| **에너지/유틸리티** | 발전·수요 실시간 밸런싱 | 수요/발전량 예측 | 손실/정비 최적화 | 수급·정비·거래·탄소·안전·Copilot | MWh·피크·손실%·탄소t |
| **소프트웨어/SaaS** | 서비스·배포·Incident·고객지원 현황 | 용량·장애·이탈·배포 위험 예측 | DORA·SLO·결함·비용 개선 | 제품·SRE·지원·FinOps·보안·Copilot | 가용성%·지연ms·MTTR·배포빈도·변경실패율 |
| **App Platform·Platform Engineering** | AKS cluster·ACA revision·traffic·workload·Incident 현황 | 용량·비용·rollout·rollback 위험 예측 | DORA·SLO·platform adoption·software supply chain 개선 | Platform·SRE·Release·FinOps·Security·Copilot | 가용성%·배포빈도·lead time·변경실패율·MTTR·비용 |
| **교육/에듀테크** | 학습참여·출석·콘텐츠 이용 현황 | 이탈·성취·수강수요 예측 | 학습경로·상담·운영 개선 | 학습·콘텐츠·상담·운영·개인정보·Copilot | 출석률·이수율·참여도·상담대기·NPS |
| **사이버보안/SOC·MSSP** | 경보·Incident·위협·자산 노출 관제 | 경보 우선순위·침해 확산 위험 예측 | 탐지규칙·Triage·대응 플레이북 개선 | SOC·Threat Intel·취약점·Identity·컴플라이언스·Copilot | MTTD·MTTR·오탐률·Dwell Time·패치 SLA |

> 매핑 원칙: ① 운영 콘솔은 **움직이는 시각화**가 가능한 업무, ② 시뮬레이터는 **입력→결과** 인과가 분명한 업무,
> ③ 분석/개선은 **근본원인→과제** 흐름, ④ 에이전트는 위 도메인 + 재무/안전·컴플라이언스 + Copilot.
> 모든 화면에 그 산업의 **실제 용어·단위**를 써야 현실감이 산다. 임원 노출 문구는 `meta.language`를
> 따르고, 한국어일 때만 한글을 우선한다. 공식 제품명·일반 약어·단위는 원문을 유지한다. 숫자는
> 리서치로 현실 범위에 맞추되 `시연 데이터`.

## 규제·고위험 산업 경계

| 산업 | 데모 기본 경계 |
|---|---|
| **식음료** | HACCP·로트 추적·콜드체인은 고객 맥락에서 확인된 경우만 사용하고, 인증 취득이나 식품 안전 보장을 주장하지 않는다. |
| **제약/바이오** | GxP·CSV·CAPA·21 CFR Part 11 등은 실시간 조사로 적용 범위를 확인한다. 배치 출하·품질 판정은 사람 승인 단계를 유지한다. |
| **헬스케어** | 합성·비식별 시연 데이터가 기본이다. 진단·치료 권고보다 병상·검사·청구·환자흐름 같은 운영 시나리오를 우선한다. |
| **금융** | 신용·보험금·투자·AML 고위험 결정은 설명 근거와 사람 검토를 유지하고, 시연 점수를 실제 심사 결과처럼 표현하지 않는다. |
| **교육** | 입학·성적·징계 같은 고영향 결정을 자동화하지 않는다. 학습지원·상담·운영 최적화를 우선하고 개인정보 경계를 표시한다. |
| **소프트웨어/보안** | 운영 배포·계정 차단·격리·복구 같은 고위험 조치는 기본적으로 승인 후 실행한다. 실제 고객 시크릿·취약점·공격 절차를 데모 데이터에 넣지 않는다. |

## 서사 프레임(대시보드 hero에 1줄)
- **AI 중심**: "<CUSTOMER>는 AI를 쓰는 데서 끝나지 않고, <INDUSTRY> 노하우를 복리로 키우는
  학습 루프를 소유합니다."
- **App Platform·CI/CD 중심**: "<CUSTOMER>는 계획에서 코드·배포·운영·학습까지 하나의 안전한
  platform loop로 연결합니다."
- **균형형**: "<CUSTOMER>는 GitHub에서 만든 변경을 AKS/ACA에서 안전하게 운영하고,
  Microsoft Foundry Agent가 그 운영 신호를 다음 결정으로 연결합니다."
