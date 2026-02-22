# SOTA Multi-Agent Teams: Research & Practice (2024-2026)

Comprehensive research survey covering academic papers, production frameworks, and real-world deployment patterns for state-of-the-art multi-agent AI teams.

**Last updated:** 2026-02-22

---

## Table of Contents

- [1. Multi-Agent Software Engineering Teams](#1-multi-agent-software-engineering-teams)
- [2. Agent Orchestration Frameworks](#2-agent-orchestration-frameworks)
- [3. Role-Based Agent Architectures](#3-role-based-agent-architectures)
- [4. Agent Communication Protocols](#4-agent-communication-protocols)
- [5. Self-Improving Agent Teams](#5-self-improving-agent-teams)
- [6. Benchmarks & Leaderboards](#6-benchmarks--leaderboards)
- [7. Failure Modes & Limitations](#7-failure-modes--limitations)
- [8. Planning & Task Decomposition](#8-planning--task-decomposition)
- [9. Memory & Context Sharing](#9-memory--context-sharing)
- [10. Human-AI Teaming](#10-human-ai-teaming)
- [11. Agent-Computer Interfaces (ACI)](#11-agent-computer-interfaces-aci)
- [12. Mixture of Agents (MoA)](#12-mixture-of-agents-moa)
- [13. Constitutional AI & Governance for Agent Teams](#13-constitutional-ai--governance-for-agent-teams)
- [14. Autonomous Coding Agents in Production](#14-autonomous-coding-agents-in-production)
- [15. Long-Horizon Planning](#15-long-horizon-planning)
- [16. Self-Play & Self-Improvement](#16-self-play--self-improvement)
- [17. Economic / Market-Based Coordination](#17-economic--market-based-coordination)
- [18. Emergent Communication](#18-emergent-communication)
- [19. Scaling Laws for Agent Teams](#19-scaling-laws-for-agent-teams)
- [20. Agentic RAG & Tool Use](#20-agentic-rag--tool-use)
- [21. Multi-Agent Debate & Verification](#21-multi-agent-debate--verification)
- [22. Claude Code Team Patterns](#22-claude-code-team-patterns)
- [23. Production Frameworks & Adoption](#23-production-frameworks--adoption)
- [24. Key Takeaways](#24-key-takeaways)
- [25. Full Reference Index](#25-full-reference-index)

---

## 1. Multi-Agent Software Engineering Teams

### ChatDev — Communicative Agents for Software Development

- **Authors:** Qian et al. (OpenBMB)
- **Venue:** ACL 2024 Long Paper
- **arXiv:** [2307.07924](https://arxiv.org/abs/2307.07924)
- **GitHub:** [github.com/OpenBMB/ChatDev](https://github.com/OpenBMB/ChatDev)
- **Architecture:** 7 social roles (CEO, CTO, Programmer, Reviewer, Tester, Designer) interacting through structured chat pairs in a "chat chain"
- **Key insight:** Communicative dehallucination — agents verify each other's outputs through structured dialogue
- **Evolution (ChatDev 2.0):** Puppeteer-style paradigm with a learnable central orchestrator optimized via RL to dynamically activate and sequence agents. Presented at NeurIPS 2025
- **MacNet extension (June 2024):** [github.com/OpenBMB/ChatDev/tree/macnet](https://github.com/OpenBMB/ChatDev/tree/macnet) — replaced chain topology with DAGs. Supports 1000+ agents. Random/Erdos-Renyi graph topologies outperform structured meshes by 1-3% due to small-world properties. Paper: [arXiv:2406.07155](https://arxiv.org/abs/2406.07155)
- **Limitation:** Correctness on complex tasks as low as 25% (per MAST study). High communication costs (>$10 per HumanEval task)

### MetaGPT — Meta Programming for Multi-Agent Collaboration

- **Authors:** Hong et al. (DeepWisdom)
- **Venue:** ICLR 2024 Oral
- **arXiv:** [2308.00352](https://arxiv.org/abs/2308.00352)
- **GitHub:** [github.com/FoundationAgents/MetaGPT](https://github.com/FoundationAgents/MetaGPT)
- **Architecture:** Standardized Operating Procedures (SOPs) encoded as prompt sequences. Roles: Product Manager, Architect, Project Manager, Engineer, QA Engineer
- **Key insight:** SOPs prevent hallucination cascades by giving each agent structured, intermediate artifacts to validate
- **AFlow (ICLR 2025 Oral, top 1.8%):** Monte Carlo Tree Search over code-represented workflows to automatically discover optimal agent coordination patterns. [arXiv:2410.10762](https://arxiv.org/abs/2410.10762)
- **MGX (February 2025):** Production product — "first AI agent development team"
- **Generated tests accuracy:** ~80%. SOPs reduce drift but don't eliminate it

### MAGIS — Multi-Agent GitHub Issue Resolution

- **Authors:** Tao et al.
- **Venue:** NeurIPS 2024
- **Paper:** [proceedings.neurips.cc/...MAGIS](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5d1f02132ef51602adf07000ca5b6138-Abstract-Conference.html)
- **Architecture:** 4 agents — Manager, Repository Custodian, Developer, QA Engineer
- **Result:** 13.94% of SWE-bench issues resolved — 8x improvement over direct GPT-4 application
- **Key insight:** QA Engineer alone adds 1.57-3.31% resolved ratio. Dedicated verification agent provides measurable gains

### AgentCoder — Multi-Agent Code Generation with Iterative Testing

- **Authors:** Huang et al.
- **arXiv:** [2312.13010](https://arxiv.org/abs/2312.13010) (updated May 2024)
- **Architecture:** 3 agents — Programmer, Test Designer, Test Executor. Iterative feedback loop
- **Results (GPT-4):** 96.3% pass@1 on HumanEval, 91.8% on MBPP, with lower token overhead (56.9K vs 138.2K for alternatives)
- **Key insight:** Separating test design from code generation prevents the "write tests that trivially pass your own buggy code" problem

### PairCoder — Pair Programming via Multi-Plan Exploration

- **Authors:** Wu et al.
- **Venue:** ASE 2024 (Distinguished Paper Award)
- **arXiv:** [2409.05001](https://arxiv.org/abs/2409.05001)
- **Architecture:** Navigator (high-level planning, plan selection) + Driver (implementation, testing)
- **Result:** 12-162% relative pass@1 improvement over direct prompting across 5 benchmarks
- **Key insight:** Navigator/Driver split enables dynamic plan abandonment when execution feedback indicates dead end

### MapCoder — Multi-Agent Code Generation for Competitive Problem Solving

- **Authors:** Pramanik et al.
- **Venue:** ACL 2024 Long Paper
- **Paper:** [aclanthology.org/2024.acl-long.269](https://aclanthology.org/2024.acl-long.269/)
- **arXiv:** [2405.11403](https://arxiv.org/abs/2405.11403)
- **Architecture:** 4 agents — Recall (retrieves similar examples), Plan, Code, Debug
- **Results:** 93.9% HumanEval, 83.1% MBPP, 22.0% APPS, 28.5% CodeContests, 45.3% xCodeEval
- **Key insight:** RAG-augmented exemplar retrieval agent significantly boosts code quality for competitive programming

### OpenHands (formerly OpenDevin) — Open Platform for AI Software Developers

- **Authors:** Wang et al.
- **Venue:** ICLR 2025
- **arXiv:** [2407.16741](https://arxiv.org/abs/2407.16741)
- **GitHub:** [github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands)
- **Architecture:** 10+ agents with AgentDelegateAction for multi-agent subtask delegation. CodeAct 2.1
- **Results:** 72% SWE-Bench Verified (Claude Sonnet 4.5 + extended thinking), 67.9% GAIA
- **Key insight:** Inference-time scaling with a dedicated critic model achieves SOTA. MIT-licensed, 188+ contributors
- **Blog:** [openhands.dev/blog/sota-on-swe-bench-verified-with-inference-time-scaling-and-critic-model](https://openhands.dev/blog/sota-on-swe-bench-verified-with-inference-time-scaling-and-critic-model)

### AgentMesh — Cooperative Multi-Agent for Software Development Automation

- **arXiv:** [2507.19902](https://arxiv.org/html/2507.19902v1) (July 2025)
- **Architecture:** Cooperative multi-agent framework with mesh-style agent communication

---

## 2. Agent Orchestration Frameworks

### AdaptOrch — Task-Adaptive Multi-Agent Orchestration

- **arXiv:** [2602.16873](https://arxiv.org/abs/2602.16873) (February 2026)
- **Key finding:** As LLMs converge in capability, HOW you orchestrate agents matters more than WHICH model you use
- **Contributions:**
  1. Performance Convergence Scaling Law
  2. Topology Routing Algorithm mapping DAGs to optimal orchestration in O(|V|+|E|)
  3. Adaptive Synthesis Protocol with provable termination guarantees
- **Result:** 12-23% improvement over static single-topology baselines on SWE-bench, GPQA, and RAG tasks

### Multi-Agent Collaboration Mechanisms Survey

- **arXiv:** [2501.06322](https://arxiv.org/html/2501.06322v1) (January 2025)
- **Contribution:** Comprehensive taxonomy of collaboration mechanisms — centralized, decentralized, hierarchical. Reference architecture for choosing between role-based (CrewAI), graph-based (LangGraph), and conversational (AutoGen) approaches

### AgentOrchestra — Hierarchical Multi-Agent Framework

- **arXiv:** [2506.12508](https://arxiv.org/html/2506.12508v1) (June 2025)
- **Architecture:** Planning Agent as central orchestrator with TEA (Tool-Environment-Agent) protocol

### Multi-Agent Collaboration via Evolving Orchestration

- **Authors:** Dang, Qian et al.
- **arXiv:** [2505.19591](https://arxiv.org/html/2505.19591v1) (May 2025)
- **Key insight:** Network-style organizations with dynamic agent selection using code-based process representations

### Anthropic — Building Effective Agents (December 2024)

- **Authors:** Erik Schluntz, Barry Zhang (Anthropic)
- **Link:** [anthropic.com/research/building-effective-agents](https://www.anthropic.com/research/building-effective-agents)
- **Key principles:**
  1. Simplicity over frameworks — most successful implementations use simple composable patterns
  2. Workflows (predefined code paths) vs. Agents (autonomous decision-making)
  3. Six composable building-block patterns for agentic systems
  4. Carefully crafted agent-computer interfaces through thorough tool documentation

### Anthropic — Multi-Agent Research System (2025)

- **Link:** [anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system)
- **Architecture:** Orchestrator-worker. Lead agent (Claude Opus 4) coordinates specialized subagents (Claude Sonnet 4) in parallel
- **Result:** Outperformed single-agent Claude Opus 4 by 90.2% on internal research evaluations
- **Key learnings:**
  - Each subagent needs: concrete objective, task boundaries, output format, tool guidance
  - Without specificity, subagents duplicate work or leave gaps
  - Spawn fresh subagents with clean contexts + careful handoffs near context limits
  - Token cost: ~15x single-agent

---

## 3. Role-Based Agent Architectures

### MegaAgent — Large-Scale Autonomous Multi-Agent System Without Predefined SOPs

- **Authors:** Li et al.
- **Venue:** ACL 2025 Findings
- **arXiv:** [2408.09955](https://arxiv.org/abs/2408.09955)
- **Key insight:** Dynamic role generation based on task analysis outperforms static role assignment
- **Scale:** 590 agents in a national policy simulation. Significantly outperforms MetaGPT

### LMA Systems for Software Engineering — Literature Review

- **Authors:** Rasheed et al.
- **Venue:** ACM TOSEM 2024
- **arXiv:** [2404.04834](https://arxiv.org/html/2404.04834v4)
- **Key finding:** Adopting established software process models (Waterfall, Agile-like iterations) as agent coordination templates is more effective than ad-hoc role assignment

### Self-Organized Agents (SoA)

- **Architecture:** Mother agents managing high-level abstractions, delegating subtasks to specialized Child agents
- **Finding:** Hierarchical role structures outperform flat peer-to-peer arrangements for complex tasks

---

## 4. Agent Communication Protocols

### Voting or Consensus? Decision-Making in Multi-Agent Debate

- **Venue:** ACL 2025 Findings
- **Paper:** [aclanthology.org/2025.findings-acl.606](https://aclanthology.org/2025.findings-acl.606.pdf)
- **Finding:** Consensus strategies refine decisions; voting selects from proposed solutions. Neither dominates universally — task type determines optimal approach
- **Rule of thumb:** Voting for well-defined tasks with discrete answers; debate/consensus for open-ended reasoning

### ACC-Collab — Actor-Critic Multi-Agent Collaboration

- **Venue:** ICLR 2025
- **Paper:** [openreview.net/forum?id=nfKfAzkiez](https://openreview.net/forum?id=nfKfAzkiez)
- **Key insight:** Structured actor-critic communication outperforms unconstrained multi-agent debate for most practical tasks. Formalizes collaboration as Actor (answer provider) + Critic (feedback provider)

### Beyond Self-Talk — Communication-Centric Survey

- **arXiv:** [2502.14321](https://arxiv.org/html/2502.14321v1) (February 2025)
- **Taxonomy:** Message passing, shared memory pools, debate, voting
- **Finding:** Shared memory pools enable a "team mind" but create consistency challenges

### Multi-LLM-Agents Debate — Performance, Efficiency, and Scaling Challenges

- **Venue:** ICLR 2025 Blog Track
- **Link:** [d2jud02ci9yv69.cloudfront.net/2025-04-28-mad-159/blog/mad](https://d2jud02ci9yv69.cloudfront.net/2025-04-28-mad-159/blog/mad/)
- **Finding:** Gains plateau after 3-4 debate rounds. Token costs scale quadratically with debate rounds

### Google A2A Protocol (April 2025)

- **Link:** [a2a-protocol.org/latest](https://a2a-protocol.org/latest/)
- **Status:** Housed by Linux Foundation, 50+ technology partners
- **Role:** Agent-to-agent communication standard (complementary to MCP for agent-tool communication)

### Anthropic MCP — Model Context Protocol (November 2024)

- **Link:** [modelcontextprotocol.io](https://modelcontextprotocol.io/)
- **Role:** Agent-tool communication standard. Open source

---

## 5. Self-Improving Agent Teams

### CoMAS — Co-Evolving Multi-Agent Systems via Interaction Rewards

- **Authors:** Xue, Zhou et al.
- **Venue:** ICLR 2026 (accepted)
- **arXiv:** [2510.08529](https://arxiv.org/abs/2510.08529)
- **Key contribution:** Agents generate intrinsic rewards from inter-agent discussion dynamics via LLM-as-a-judge, optimizing each agent's policy via RL
- **Significance:** First practical framework for autonomous, unsupervised agent co-evolution. Scalability improves with more diverse agents

### AFlow — Automating Agentic Workflow Generation

- **Authors:** Zhang, Xiang et al. (MetaGPT team)
- **Venue:** ICLR 2025 Oral (top 1.8%)
- **arXiv:** [2410.10762](https://arxiv.org/abs/2410.10762)
- **Method:** MCTS over code-represented workflows. Composable "Operators" (Ensemble, Review, Revise)
- **Result:** 5.7% average improvement over SOTA. Smaller models outperform GPT-4o at 4.55% of its inference cost
- **Key insight:** Agent workflows should be searched/optimized, not hand-designed

### COPPER — Reflective Multi-Agent Collaboration

- **Authors:** Du et al.
- **Venue:** NeurIPS 2024
- **Paper:** [proceedings.neurips.cc/...COPPER](https://proceedings.neurips.cc/paper_files/paper/2024/hash/fa54b0edce5eef0bb07654e8ee800cb4-Abstract-Conference.html)
- **Method:** Shared reflector fine-tuned with counterfactual PPO. Generates personalized reflections per agent role
- **Key insight:** Counterfactual rewards solve the credit assignment problem in multi-agent settings

### Meta-Thinking in LLMs via Multi-Agent RL Survey

- **arXiv:** [2504.14520](https://arxiv.org/html/2504.14520v1) (April 2025)
- **Covers:** DPSDP, JoyAgents-R1, MAPORL (multi-agent post-co-training via RL)

---

## 6. Benchmarks & Leaderboards

### SWE-bench Verified (as of February 2026)

- **Leaderboard:** [swebench.com](http://www.swebench.com/)
- **Top results:**
  - Sonar Foundation Agent: 79.2% (LlamaIndex-based, $1.26/resolution, 10.5 min avg)
  - Claude Opus 4.5 + Live-SWE-agent: 79.2%
  - Verdent: 76.1% pass@1, 81.2% pass@3
  - OpenHands + critic model: 72%
  - TRAE: 70.4% (multi-model + o1 selector)
  - Devlo: 70.2% (three-LLM diversity)
- **Analysis paper:** [arXiv:2506.17208](https://arxiv.org/html/2506.17208v2) — profiles architectural patterns of top submissions

### SWE-bench Pro (harder, long-horizon)

- **Leaderboard:** [scale.com/leaderboard/swe_bench_pro_public](https://scale.com/leaderboard/swe_bench_pro_public)
- **Top results:** Claude Opus 4.5 (45.89%), Claude 4.5 Sonnet (43.60%), Gemini 3 Pro (43.30%)
- **Gap:** Verified ~79% vs Pro ~23-46% reveals agents struggle with complex multi-file engineering

### SWE-EVO — Long-Horizon Software Evolution

- **arXiv:** [2512.18470](https://arxiv.org/html/2512.18470) (December 2025)
- **Extends SWE-bench:** Multi-step software evolution, not just single-issue fixes
- **Finding:** Current agents struggle with sustained multi-commit development

### GAIA — General AI Assistants

- **Leaderboard:** [hal.cs.princeton.edu/gaia](https://hal.cs.princeton.edu/gaia)
- **Current SOTA:** ~90% (end 2025). Claude Opus 4.5: 77.5% overall (84.5% web search subscore)
- **466 questions** requiring reasoning + web browsing + tool use

### The Agent Company — Real-World Enterprise Tasks

- **arXiv:** December 2024
- **Link:** [the-agent-company.com](https://the-agent-company.com/)
- **175 manually designed tasks** spanning office operations, project management, technical development
- **Multi-tier scoring:** Process assessment, result assessment, interaction assessment

### AgentBench — 8 Environments

- **Scope:** 29 LLMs across 8 diverse environments
- **Finding:** Significant commercial vs. open-source gap

### OSWorld — Open-Ended Computer Tasks

- **Top score:** 34.5% (Simular Agent S2, 50-step)
- **~65% of tasks still fail**

### WebArena — Web Tasks

- **812 tasks** on self-hosted websites
- **Top:** 61.7% (IBM CUGA). WebChoreArena variant: only 37.8%

### Holistic Agent Leaderboard (HAL)

- **arXiv:** [2510.11977](https://arxiv.org/pdf/2510.11977)
- **Purpose:** Unified aggregation across multiple agent benchmarks

---

## 7. Failure Modes & Limitations

### MAST — Why Do Multi-Agent LLM Systems Fail?

- **Authors:** Cemri, Pan, Yang et al.
- **Venue:** ICLR 2025 / NeurIPS 2025 Spotlight
- **arXiv:** [2503.13657](https://arxiv.org/abs/2503.13657)
- **Contribution:** First Multi-Agent System Failure Taxonomy. 1600+ annotated traces across 7 frameworks. High inter-annotator agreement (kappa=0.88)
- **14 failure modes in 3 categories:**
  1. System design issues
  2. Inter-agent misalignment
  3. Task verification failures
- **Critical finding:** Correctness of SOTA open-source MAS like ChatDev can be as low as 25%. Verifier presence is not a silver bullet
- **Hallucination propagation:** One agent's hallucination is treated as valid input by others, creating reinforcement cascades
- **Token overhead:** 4-220x more input tokens than single-agent. Even with perfect reuse, 2-12x more for response generation

### Large Language Models Miss the Multi-Agent Mark

- **Authors:** La Malfa et al.
- **Venue:** NeurIPS 2025 (Position Paper)
- **arXiv:** [2505.21298](https://arxiv.org/abs/2505.21298)
- **Argument:** Most "multi-agent" LLM systems appropriate MAS terminology without engaging with foundational MAS principles (autonomy, social interaction, structured environments)

### AgentArk — Distilling Multi-Agent Intelligence into Single LLM

- **arXiv:** [2602.03955](https://arxiv.org/abs/2602.03955) (February 2026)
- **Finding:** Multi-agent debate dynamics can be distilled into a single model via fine-tuning, preserving reasoning quality at single-agent cost
- **Implication:** For deployment, training with multi-agent dynamics and deploying single distilled agent may be more practical than running full MAS

### Uncertainty in Multi-Agent Systems

- **arXiv:** [2602.04234](https://arxiv.org/html/2602.04234) (February 2026)
- **Analyzes:** How uncertainty propagates through multi-agent interactions, highlighting systemic risks in cascading decisions

### The "17x Error Trap" (Towards Data Science)

- **Link:** [towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/)
- **Finding:** "Bag of Agents" anti-pattern (throwing multiple agents at a problem without structured coordination) multiplies errors 17x. Beyond 4 agents, explicit topology is mandatory

---

## 8. Planning & Task Decomposition

### GoalAct — Global Planning + Hierarchical Execution

- **arXiv:** [2504.16563](https://arxiv.org/abs/2504.16563) (April 2025)
- **Method:** Continuously updated global planning with hierarchical decomposition into high-level skills (searching, coding, writing). Global plan adapts based on execution feedback

### Adaptive DAG-Based Decomposition (multiple papers)

- **Key approach:** Lazy decomposition — create next-level sub-task DAGs only when needed
- **Why:** Initial plans are often wrong. Decompose one level, execute, then decompose the next

### HiPlan — Milestone-Guided Planning

- **Method:** Global milestone guides (coarse-grained) + local stepwise hints (fine-grained), with retrieval-augmented milestone library from expert trajectories

---

## 9. Memory & Context Sharing

### A-MEM — Agentic Memory for LLM Agents

- **Authors:** Xu, Liang et al.
- **Venue:** NeurIPS 2025
- **arXiv:** [2502.12110](https://arxiv.org/abs/2502.12110)
- **Method:** Self-organizing memory inspired by Zettelkasten. Interconnected knowledge networks through dynamic indexing and linking. Memories evolve: new memories trigger updates to contextual representations of existing ones
- **Key insight:** Memory systems should be agentic (self-organizing) rather than passive stores

### Collaborative Memory — Multi-User Sharing in LLM Agents

- **arXiv:** [2505.18279](https://arxiv.org/html/2505.18279v1) (May 2025)
- **Evaluates:** Shared vs. isolated memory configurations across varying query overlap rates
- **Finding:** Shared memory enables "team mind" but requires explicit conflict resolution protocols

### MemOS — Memory Operating System for AI

- **Paper:** [statics.memtensor.com.cn/files/MemOS_0707.pdf](https://statics.memtensor.com.cn/files/MemOS_0707.pdf) (July 2025)
- **Argument:** RAG is a retrieval-and-transient-composition pipeline lacking lifecycle tracking, versioning, permission-aware scheduling. Proposes OS-level abstraction for agent memory

### Agentic RAG with Knowledge Graphs for Complex Multi-Hop Reasoning

- **arXiv:** [2507.16507](https://arxiv.org/abs/2507.16507) (July 2025)
- **INRAExplorer:** LLM-based agent with multi-tool architecture for dynamic KG querying and iterative multi-hop reasoning

### Memory in LLM-based Multi-Agent Systems Survey

- **Link:** [TechRxiv preprint](https://www.techrxiv.org/users/1007269/articles/1367390/master/file/data/LLM_MAS_Memory_Survey_preprint_/LLM_MAS_Memory_Survey_preprint_.pdf)
- **Finding:** Serialized turns (agents act one at a time) is simplest consistency mechanism but creates bottlenecks. Shared memory pools require explicit conflict resolution

---

## 10. Human-AI Teaming

### HULA — Human-In-the-Loop Software Development Agents (Atlassian)

- **Venue:** ICSE 2025 (SEIP)
- **arXiv:** [2411.12924](https://arxiv.org/abs/2411.12924)
- **Scale:** 2,600 practitioners, 22,000+ JIRA issues
- **Architecture:** AI Planner + AI Coder + Human Agent
- **Results:**
  - 79% of work items got coding plans
  - 82% of plans approved by engineers
  - 25% reached PR stage
  - 59% of PRs merged
- **Key insight:** Human approval at the plan stage (before code generation) is the most efficient intervention point

### LLM-Based Human-Agent Collaboration Survey

- **arXiv:** [2505.00753](https://arxiv.org/html/2505.00753v4) (May 2025)
- **Taxonomy:** One-by-one (sequential turns), simultaneous (concurrent real-time), adaptive (dynamic switching)
- **Finding:** Combining human intuition/creativity/ethics with LLM speed/knowledge yields best results

### Trustworthy Human-Agent Collaboration in SE

- **arXiv:** [2505.04251](https://arxiv.org/html/2505.04251v1) (May 2025)
- **Focus:** Trust calibration — when should humans trust agent output vs. intervene?

### Mental Models of Early Adopters of Multi-Agent Tools

- **arXiv:** [2510.06224](https://arxiv.org/html/2510.06224v1) (October 2025)
- **Studies:** Gaps between user expectations and system capabilities

---

## 11. Agent-Computer Interfaces (ACI)

### SWE-agent — Agent-Computer Interfaces Enable Automated Software Engineering

- **Authors:** Princeton NLP
- **Venue:** NeurIPS 2024
- **arXiv:** [2405.15793](https://arxiv.org/abs/2405.15793)
- **GitHub:** [github.com/SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent)
- **Core insight:** How agents interact with computers matters as much as the model itself. Custom interfaces with simplified commands, concise documentation, and consolidated operations dramatically outperform raw shell access
- **Validation:** mini-swe-agent (100 lines) scores >74% on SWE-bench Verified
- **Limitation:** ACI design is currently task-specific; generalization requires new interface designs

---

## 12. Mixture of Agents (MoA)

### Mixture-of-Agents Enhances Large Language Model Capabilities

- **Authors:** Together AI
- **Venue:** ICLR 2025
- **arXiv:** [2406.04692](https://arxiv.org/abs/2406.04692)
- **GitHub:** [github.com/togethercomputer/MoA](https://github.com/togethercomputer/MoA)
- **Architecture:** Layered pipeline — each layer contains multiple LLMs, each agent takes all outputs from previous layer as auxiliary context
- **Key discovery:** LLMs exhibit "collaborativeness" — generate better responses when given reference outputs from other models, even weaker ones. Diversity matters more than individual quality
- **Result:** Open-source MoA achieved 65.1% on AlpacaEval 2.0, surpassing GPT-4 Omni (57.5%)
- **Limitation:** Latency scales linearly with layers; best on text generation quality, less clear for action-oriented tasks

---

## 13. Constitutional AI & Governance for Agent Teams

### Governance-as-a-Service (GaaS)

- **arXiv:** [2508.18765](https://arxiv.org/abs/2508.18765) (August 2025)
- **Approach:** External enforcement constraining observable outputs rather than aligning internal behavior. Addresses enterprise environments with dozens of heterogeneous autonomous agents

### Policy-as-Prompt

- **arXiv:** [2509.23994](https://arxiv.org/abs/2509.23994) (September 2025)
- **Method:** Converts unstructured design documents into verifiable runtime guardrails

### Building a Foundational Guardrail for General Agentic Systems

- **arXiv:** [2510.09781](https://arxiv.org/abs/2510.09781) (October 2025)
- **Focus:** Pre-execution plan analysis and intervention

### Agentic AI Security — Threats, Defenses, Evaluation

- **arXiv:** [2510.23883](https://arxiv.org/abs/2510.23883) (October 2025)
- **Comprehensive survey** of security threats specific to agentic AI systems

### Anthropic Multi-Agent Safety Research

- **Link:** [aigl.blog/multi-agent-risks-from-advanced-ai](https://www.aigl.blog/multi-agent-risks-from-advanced-ai/)
- **Collaborative report:** 50+ researchers from DeepMind, CMU, Harvard, Anthropic
- **Findings:**
  - Many single-agent safeguards don't translate to emergent multi-agent settings
  - Credit assignment harder with multiple learning agents
  - Sabotage risk: "very low, but not fully negligible"

---

## 14. Autonomous Coding Agents in Production

### Honest Assessment Table

| Tool | Strength | Weakness |
|------|----------|----------|
| **Claude Code** | Deepest reasoning, trusted for debugging and architecture | Token-intensive, CLI-only |
| **Cursor** | AI-native IDE, Composer v3 for multi-file | Pricing backlash (usage-based model) |
| **Devin** | Background agents, parallel throughput | Slower, expensive; acquired Windsurf for $250M |
| **Windsurf** | "Flow" persistent context, fast indexing | Latency/crashes in long sessions |
| **Cline** | Maximum flexibility, any model, git-native | Setup effort, token management on user |
| **Aider** | Git-native CLI, writes ~70% of its own code | Niche, surpassed on polyglot benchmarks |

### Key Sources

- [Faros AI: Best AI Coding Agents 2026](https://www.faros.ai/blog/best-ai-coding-agents-2026)
- [RedMonk: 10 Things Developers Want from Agentic IDEs](https://redmonk.com/kholterhoff/2025/12/22/10-things-developers-want-from-their-agentic-ides-in-2025/)
- [Anthropic 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf)

---

## 15. Long-Horizon Planning

### METR — Measuring AI Ability to Complete Long Tasks

- **Link:** [metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)
- **Updated:** [metr.org/blog/2026-1-29-time-horizon-1-1](https://metr.org/blog/2026-1-29-time-horizon-1-1/)
- **Metric:** Task-completion time horizon — length of tasks (as measured by human expert time) that agents complete with 50% reliability
- **Trend:** Exponentially increasing. Doubling time: ~89 days (accelerating from ~7 months in 2019-2023)
- **Current state:** Reliably minutes-long tasks; some hour-long tasks achievable but unreliable
- **Projection:** Month-long autonomous tasks by 2027 if trend continues

---

## 16. Self-Play & Self-Improvement

### SWE-RL — Self-Play for Superintelligent Software Agents

- **arXiv:** [2512.18552](https://arxiv.org/abs/2512.18552) (December 2025)
- **Method:** Agent iteratively injects software bugs and repairs them, with complexity increasing over time
- **Result:** +10.4 points on SWE-bench Verified, +7.8 on SWE-bench Pro

### Self-Improving AI Agents through Self-Play

- **arXiv:** [2512.02731](https://arxiv.org/abs/2512.02731) (December 2025)

### MARS — Multi-Agent Reasoning through Self-Play

- **arXiv:** [2510.15414](https://arxiv.org/abs/2510.15414) (October 2025)
- **Method:** Cooperative + competitive self-play games to cultivate multi-agent capabilities

### Multi-Agent Evolve — LLM Self-Improve through Co-evolution

- **arXiv:** [2510.23595](https://arxiv.org/abs/2510.23595) (October 2025)
- **Method:** Three agents from one base model with Task-Relative REINFORCE++ for co-evolution

### Your Self-Play Algorithm is Secretly an Adversarial Imitator

- **arXiv:** [2602.01357](https://arxiv.org/abs/2602.01357) (February 2026)
- **Critical finding:** Self-play methods can be recast as imitation learning toward a prescribed objective, implicitly inducing a capacity ceiling. Existing LLM self-play algorithms **cannot achieve infinite capability gains**

### PSV — Self-Play via Formal Verification

- **Link:** [emergentmind.com/papers/2512.18160](https://www.emergentmind.com/papers/2512.18160)
- **Method:** Propose, Solve, Verify using formal verification signals
- **Result:** Improves pass@1 by up to 9.6x over baselines

---

## 17. Economic / Market-Based Coordination

### Market Making as a Scalable Framework for Multi-Agent LLM Systems

- **arXiv:** [2511.17621](https://arxiv.org/abs/2511.17621) (November 2025)
- **Method:** Agent interactions as prediction market exchanges. Market maker offers prices on propositions, agents buy/sell based on beliefs, prices converge through iterative trading
- **Key property:** Promotes truthful contributions (lying is unprofitable). Myopic agents prevent long-term scheming
- **Result:** Up to 10% accuracy gains while preserving interpretability

### Agent Exchange (AEX)

- **arXiv:** [2507.03904](https://arxiv.org/abs/2507.03904) (July 2025)
- **Adapts:** Real-time bidding systems (like ad tech) for agent task allocation

### Decentralized Adaptive Task Allocation

- **Published:** Nature Scientific Reports, 2025
- **Link:** [nature.com/articles/s41598-025-21709-9](https://www.nature.com/articles/s41598-025-21709-9)

---

## 18. Emergent Communication

### Emergence of Machine Language in LLM-based Agent Communication

- **Paper:** [openreview.net/forum?id=zy06mHNoO2](https://openreview.net/forum?id=zy06mHNoO2) (Submitted to ICLR 2026, withdrawn)
- **Finding:** Two LLM agents develop shared language for 541 objects through 4 rounds, 3 attempts per round. Emergent language exhibits compositionality, generalizability, morphemes, and polysemy
- **Safety concern:** Non-human-interpretable communication makes monitoring harder

### Emergent Coordination in Multi-Agent Language Models

- **arXiv:** [2510.05174](https://arxiv.org/abs/2510.05174) (October 2025)

### A Survey of AI Agent Protocols

- **arXiv:** [2504.16736](https://arxiv.org/abs/2504.16736) (April 2025)
- **Four phases of protocol evolution:** Exploration → Signal Consolidation → Protocol Optimization → Protocol Maturation

---

## 19. Scaling Laws for Agent Teams

### Towards a Science of Scaling Agent Systems (Google/DeepMind/MIT)

- **arXiv:** [2512.08296](https://arxiv.org/abs/2512.08296) (December 2025)
- **Blog:** [research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)
- **Scale:** 180 configurations across 5 architectures x 3 LLM families x 4 benchmarks
- **Critical findings:**
  1. Benefits diminish when single-agent baseline exceeds ~45% accuracy
  2. Centralized coordination: +80.8% on parallelizable tasks
  3. Decentralized: +9% on web navigation via peer debate
  4. Sequential reasoning: every multi-agent variant degrades by 39-70%
  5. Error amplification: 17.2x (independent agents) vs 4.4x (centralized)
  6. Optimal communication: 0.39 messages per turn
  7. Predictive framework: correctly predicts optimal strategy for 87% of held-out configs

### More Agents Is All You Need

- **Authors:** Li et al.
- **Venue:** TMLR 2024
- **arXiv:** [2402.05120](https://arxiv.org/abs/2402.05120)
- **Method:** "Agent Forest" — sampling-and-voting across multiple instances
- **Finding:** Performance scales with agent count; smaller models + more agents can beat larger models + fewer agents
- **Caveat:** Challenged by Google/DeepMind scaling paper — only holds for certain task types

### Chain of Agents — Long-Context Task Collaboration (Google Research)

- **Venue:** NeurIPS 2024
- **arXiv:** [2406.02818](https://arxiv.org/abs/2406.02818)
- **Method:** Worker agents sequentially process text segments, passing accumulated information. Manager synthesizes final output
- **Finding:** Outperforms RAG and long-context window approaches on QA, summarization, and code completion

---

## 20. Agentic RAG & Tool Use

### Agentic RAG Survey

- **arXiv:** [2501.09136](https://arxiv.org/abs/2501.09136) (January 2025)
- **4 design patterns:** Reflection, Planning, Tool Use, Multi-Agent Collaboration
- **Dominant pattern:** Iterative retrieve → evaluate quality → re-retrieve if insufficient → validate → generate

### MA-RAG — Multi-Agent RAG with Collaborative Chain-of-Thought

- **arXiv:** [2505.20096](https://arxiv.org/abs/2505.20096) (May 2025)
- **4 agents:** Planner, Step Definer, Extractor, QA Agent
- **Communication:** Chain-of-thought prompting for progressive refinement

---

## 21. Multi-Agent Debate & Verification

### DMAD — Breaking Mental Set (ICLR 2025)

- **Paper:** [openreview.net/forum?id=t6QHYUOQL7](https://openreview.net/forum?id=t6QHYUOQL7)
- **GitHub:** [github.com/MraDonkey/DMAD](https://github.com/MraDonkey/DMAD)
- **Problem:** Standard debate uses same reasoning methods despite different personas ("fixed mental set")
- **Solution:** Force genuinely distinct reasoning strategies, not just different personas
- **Result:** Outperforms standard debate and self-reflection in fewer rounds

### FREE-MAD — Consensus-Free Multi-Agent Debate

- **arXiv:** [2509.11035](https://arxiv.org/abs/2509.11035) (September 2025)
- **Challenges:** The assumption that consensus is always the goal

### Graph of Thoughts (GoT)

- **Venue:** AAAI 2024
- **arXiv:** [2308.09687](https://arxiv.org/abs/2308.09687)
- **Method:** Generalizes reasoning from chains and trees to arbitrary graphs with feedback loops
- **Result:** 62% improvement over Tree of Thoughts, >31% cost reduction

### From Lazy Agents to Deliberation

- **arXiv:** [2511.02303](https://arxiv.org/abs/2511.02303) (November 2025)
- **Problem:** In multi-agent reasoning, one agent dominates while others contribute nothing ("free-riding")
- **Solution:** Verifiable reward mechanisms for credit assignment

### Group Think — Multiple Concurrent Reasoning Agents

- **arXiv:** [2505.11107](https://arxiv.org/abs/2505.11107) (May 2025)
- **Innovation:** Token-level granularity collaboration (not just turn-level)

---

## 22. Claude Code Team Patterns

### Official Agent Teams (Experimental, February 2026)

- **Docs:** [code.claude.com/docs/en/agent-teams](https://code.claude.com/docs/en/agent-teams)
- **Enable:** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- **Architecture:** Team lead + teammates with shared task list + mailbox messaging system
- **Cost:** ~7x tokens compared to standard sessions
- **Guide:** [Addy Osmani's Definitive Guide](https://addyosmani.com/blog/claude-code-agent-teams/)

### Subagents

- **Docs:** [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)
- **Custom agents:** `.claude/agents/*.md` with YAML frontmatter
- **Features:** Model routing, worktree isolation, persistent memory, tool whitelists, MCP server scoping
- **Deep dive:** [cuong.io/blog/2025/06/24-claude-code-subagent-deep-dive](https://cuong.io/blog/2025/06/24-claude-code-subagent-deep-dive)

### Hooks System (17 events)

- **Docs:** [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)
- **Guide:** [code.claude.com/docs/en/hooks-guide](https://code.claude.com/docs/en/hooks-guide)
- **Blog:** [GitButler: Automate Your AI Workflows with Claude Code Hooks](https://blog.gitbutler.com/automate-your-ai-workflows-with-claude-code-hooks)
- **Types:** Command (shell), Prompt (single-turn LLM), Agent (multi-turn with tools)

### Agent SDK

- **Docs:** [platform.claude.com/docs/en/agent-sdk/overview](https://platform.claude.com/docs/en/agent-sdk/overview)
- **Python:** [github.com/anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)
- **TypeScript:** [github.com/anthropics/claude-agent-sdk-typescript](https://github.com/anthropics/claude-agent-sdk-typescript)

### Community Orchestrators

| Project | Stars | Approach | Link |
|---------|-------|----------|------|
| claude-squad | ~5.6k | TUI + tmux + worktrees | [github.com/smtg-ai/claude-squad](https://github.com/smtg-ai/claude-squad) |
| claude_code_agent_farm | -- | 20+ parallel agents, tmux dashboard | [github.com/Dicklesworthstone/claude_code_agent_farm](https://github.com/Dicklesworthstone/claude_code_agent_farm) |
| claude-flow | -- | MCP-based swarm + RAG | [github.com/ruvnet/claude-flow](https://github.com/ruvnet/claude-flow) |
| claude-swarm | -- | Task decomposition, rich TUI | [github.com/affaan-m/claude-swarm](https://github.com/affaan-m/claude-swarm) |
| ccswarm | -- | Channel-based, zero shared state | [github.com/nwiizo/ccswarm](https://github.com/nwiizo/ccswarm) |
| overstory | -- | SQLite-based mail system | [github.com/jayminwest/overstory](https://github.com/jayminwest/overstory) |
| CCPM | -- | GitHub Issues as project DB | [github.com/automazeio/ccpm](https://github.com/automazeio/ccpm) |
| ccmanager | -- | Multi-tool session manager | [github.com/kbwo/ccmanager](https://github.com/kbwo/ccmanager) |

### Monitoring & Observability

| Project | Approach | Link |
|---------|----------|------|
| claude-code-hooks-multi-agent-observability | Hooks → JSONL → Bun server → WebSocket → Vue | [github.com/disler/claude-code-hooks-multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability) |
| claude-code-otel | OpenTelemetry + SigNoz dashboards | [github.com/ColeMurray/claude-code-otel](https://github.com/ColeMurray/claude-code-otel) |
| Datadog AI Agents Console | Enterprise-wide Claude Code monitoring | [datadoghq.com/blog/claude-code-monitoring](https://www.datadoghq.com/blog/claude-code-monitoring/) |

### Spec-Driven Development Frameworks

| Project | Description | Link |
|---------|-------------|------|
| Spec-Flow | Production-ready SDD with quality gates | [github.com/marcusgoll/Spec-Flow](https://github.com/marcusgoll/Spec-Flow) |
| cc-sdd | Kiro-style SDD commands | [github.com/gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) |
| claude-code-spec-workflow | Automated SDD | [github.com/Pimzino/claude-code-spec-workflow](https://github.com/Pimzino/claude-code-spec-workflow) |

---

## 23. Production Frameworks & Adoption

### AutoGen v0.4 (Microsoft, January 2025)

- **GitHub:** [github.com/microsoft/autogen](https://github.com/microsoft/autogen)
- **Blog:** [devblogs.microsoft.com/autogen/autogen-reimagined-launching-autogen-0-4](https://devblogs.microsoft.com/autogen/autogen-reimagined-launching-autogen-0-4/)
- **Three-layer architecture:** Core (event-driven), AgentChat (high-level API), Extensions

### Magentic-One (Microsoft, November 2024)

- **arXiv:** [2411.04468](https://arxiv.org/abs/2411.04468)
- **Link:** [microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks](https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/)
- **5 agents:** Orchestrator (dual-ledger), WebSurfer, FileSurfer, Coder, ComputerTerminal

### OpenAI Agents SDK (2025)

- **GitHub:** [github.com/openai/openai-agents-python](https://github.com/openai/openai-agents-python)
- **Docs:** [openai.github.io/openai-agents-python](https://openai.github.io/openai-agents-python/)
- **Predecessor:** Swarm ([github.com/openai/swarm](https://github.com/openai/swarm)) — experimental, now deprecated

### LangGraph 1.0 (October 2025)

- **Link:** [langchain.com/langgraph](https://www.langchain.com/langgraph)
- **4 runtime pillars:** Durable execution, streaming, memory (short + long-term), human-in-the-loop
- **Adoption:** 6.17M monthly downloads. LinkedIn, Uber, Replit, Elastic, 400+ companies

### CrewAI

- **Link:** [crewai.com](https://www.crewai.com/)
- **Funding:** $18M Series A. 100K+ agent executions/day. Claims 60% of Fortune 500

### Google AI Co-Scientist (February 2025)

- **arXiv:** [2502.18864](https://arxiv.org/abs/2502.18864)
- **Architecture:** Coalition of specialized agents (Generation, Reflection, Ranking, Evolution, Proximity, Meta-review) on Gemini 2.0
- **Result:** Hypothesis generation reduced from weeks to days; wet-lab validated predictions

### Production Reality (LangChain Survey, December 2025, 1340 respondents)

- **Link:** [langchain.com/state-of-agent-engineering](https://www.langchain.com/state-of-agent-engineering)
- **57% have agents in production** (67% of enterprises with 10k+ employees)
- **Quality:** #1 barrier (32%)
- **Security:** Top challenge (62%)
- **40% of multi-agent pilots fail** within 6 months
- **Forrester prediction:** 75% of firms building complex agentic architectures independently will fail

### Domain-Specific Multi-Agent Applications

**FinCon — Financial Decision Making (NeurIPS 2024)**
- **arXiv:** [2407.06567](https://arxiv.org/abs/2407.06567)
- Manager-analyst hierarchy with conceptual verbal reinforcement

**MDAgents — Medical Decision Making (NeurIPS 2024)**
- Adaptive collaboration strategy using multi-agent debate for medical decisions

---

## 24. Key Takeaways

### When Multi-Agent HELPS

| Scenario | Best Architecture | Evidence |
|----------|-------------------|----------|
| Parallelizable tasks | Centralized orchestrator + workers | +80.8% (Google/DeepMind scaling study) |
| Web navigation / exploration | Decentralized peer debate | +9% (Google/DeepMind) |
| Code generation with tests | Programmer + Test Designer + Executor | 96.3% HumanEval (AgentCoder) |
| Text quality improvement | Mixture of Agents (layered) | 65.1% AlpacaEval beating GPT-4o (MoA) |
| Research / information synthesis | Orchestrator + parallel searchers | +90.2% (Anthropic multi-agent research) |

### When Multi-Agent HURTS

| Scenario | Degradation | Evidence |
|----------|-------------|----------|
| Sequential reasoning | -39% to -70% | Google/DeepMind scaling study |
| Tasks where single agent >45% accuracy | Diminishing/negative returns | Google/DeepMind scaling study |
| Unstructured "bag of agents" | 17x error amplification | MAST study, TDS analysis |
| Extended autonomous operation | Confident wrong execution for hours | Multiple practitioner reports |

### Five Paradigm Shifts

1. **Interface > Model** — ACI design often matters more than LLM choice (SWE-agent, NeurIPS 2024)
2. **Orchestration > Model** — Topology-aware coordination yields 12-23% over model switching (AdaptOrch, 2026)
3. **External Governance > Internal Alignment** — GaaS pattern more practical than per-agent alignment (2025)
4. **Throughput > Speed** — Background agents running in parallel (METR time horizons doubling every ~89 days)
5. **Standardized Protocols > Custom Integration** — MCP + A2A becoming the TCP/IP of agent systems

---

## 25. Full Reference Index

### Top Venue Papers (NeurIPS, ICLR, ICML, ACL, AAAI)

| Paper | Venue | Link |
|-------|-------|------|
| ChatDev: Communicative Agents for Software Development | ACL 2024 | [arXiv:2307.07924](https://arxiv.org/abs/2307.07924) |
| MetaGPT: Meta Programming for Multi-Agent Collaboration | ICLR 2024 Oral | [arXiv:2308.00352](https://arxiv.org/abs/2308.00352) |
| MAGIS: Multi-Agent GitHub Issue Resolution | NeurIPS 2024 | [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5d1f02132ef51602adf07000ca5b6138-Abstract-Conference.html) |
| MapCoder: Multi-Agent Code Generation | ACL 2024 | [aclanthology.org/2024.acl-long.269](https://aclanthology.org/2024.acl-long.269/) |
| PairCoder: Pair Programming Framework | ASE 2024 Distinguished | [arXiv:2409.05001](https://arxiv.org/abs/2409.05001) |
| COPPER: Reflective Multi-Agent Collaboration | NeurIPS 2024 | [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2024/hash/fa54b0edce5eef0bb07654e8ee800cb4-Abstract-Conference.html) |
| Chain of Agents (Google Research) | NeurIPS 2024 | [arXiv:2406.02818](https://arxiv.org/abs/2406.02818) |
| FinCon: Financial Decision Making | NeurIPS 2024 | [arXiv:2407.06567](https://arxiv.org/abs/2407.06567) |
| SWE-agent: Agent-Computer Interfaces | NeurIPS 2024 | [arXiv:2405.15793](https://arxiv.org/abs/2405.15793) |
| Graph of Thoughts | AAAI 2024 | [arXiv:2308.09687](https://arxiv.org/abs/2308.09687) |
| Mixture-of-Agents (Together AI) | ICLR 2025 | [arXiv:2406.04692](https://arxiv.org/abs/2406.04692) |
| OpenHands: Open Platform for AI Software Developers | ICLR 2025 | [arXiv:2407.16741](https://arxiv.org/abs/2407.16741) |
| AFlow: Automating Agentic Workflow Generation | ICLR 2025 Oral (top 1.8%) | [arXiv:2410.10762](https://arxiv.org/abs/2410.10762) |
| ACC-Collab: Actor-Critic Multi-Agent Collaboration | ICLR 2025 | [openreview.net](https://openreview.net/forum?id=nfKfAzkiez) |
| MAST: Why Do Multi-Agent LLM Systems Fail? | ICLR 2025 | [arXiv:2503.13657](https://arxiv.org/abs/2503.13657) |
| DMAD: Breaking Mental Set in Multi-Agent Debate | ICLR 2025 | [openreview.net](https://openreview.net/forum?id=t6QHYUOQL7) |
| Voting or Consensus in Multi-Agent Debate | ACL 2025 Findings | [aclanthology.org](https://aclanthology.org/2025.findings-acl.606.pdf) |
| MegaAgent: Large-Scale Autonomous Multi-Agent | ACL 2025 Findings | [arXiv:2408.09955](https://arxiv.org/abs/2408.09955) |
| HULA: Human-In-the-Loop Agents (Atlassian) | ICSE 2025 SEIP | [arXiv:2411.12924](https://arxiv.org/abs/2411.12924) |
| A-MEM: Agentic Memory | NeurIPS 2025 | [arXiv:2502.12110](https://arxiv.org/abs/2502.12110) |
| LLMs Miss the Multi-Agent Mark | NeurIPS 2025 Position | [arXiv:2505.21298](https://arxiv.org/abs/2505.21298) |
| Magentic-One (Microsoft) | arXiv Nov 2024 | [arXiv:2411.04468](https://arxiv.org/abs/2411.04468) |
| CoMAS: Co-Evolving Multi-Agent Systems | ICLR 2026 | [arXiv:2510.08529](https://arxiv.org/abs/2510.08529) |

### Key arXiv Preprints

| Paper | Date | Link |
|-------|------|------|
| AgentCoder: Multi-Agent Code Generation | 2024 | [arXiv:2312.13010](https://arxiv.org/abs/2312.13010) |
| More Agents Is All You Need | 2024 | [arXiv:2402.05120](https://arxiv.org/abs/2402.05120) |
| LMA SE Systems Survey | 2024 | [arXiv:2404.04834](https://arxiv.org/html/2404.04834v4) |
| MacNet: DAG-based Multi-Agent Collaboration | June 2024 | [arXiv:2406.07155](https://arxiv.org/abs/2406.07155) |
| Multi-Agent Collaboration Mechanisms Survey | Jan 2025 | [arXiv:2501.06322](https://arxiv.org/html/2501.06322v1) |
| Agentic RAG Survey | Jan 2025 | [arXiv:2501.09136](https://arxiv.org/abs/2501.09136) |
| Beyond Self-Talk: Communication-Centric Survey | Feb 2025 | [arXiv:2502.14321](https://arxiv.org/html/2502.14321v1) |
| AI Co-Scientist (Google) | Feb 2025 | [arXiv:2502.18864](https://arxiv.org/abs/2502.18864) |
| GoalAct: Global Planning + Hierarchical Execution | Apr 2025 | [arXiv:2504.16563](https://arxiv.org/abs/2504.16563) |
| Meta-Thinking via Multi-Agent RL Survey | Apr 2025 | [arXiv:2504.14520](https://arxiv.org/html/2504.14520v1) |
| AI Agent Protocols Survey | Apr 2025 | [arXiv:2504.16736](https://arxiv.org/abs/2504.16736) |
| LLM-Based Human-Agent Collaboration Survey | May 2025 | [arXiv:2505.00753](https://arxiv.org/html/2505.00753v4) |
| Trustworthy Human-Agent Collaboration | May 2025 | [arXiv:2505.04251](https://arxiv.org/html/2505.04251v1) |
| Group Think: Multiple Concurrent Reasoning | May 2025 | [arXiv:2505.11107](https://arxiv.org/abs/2505.11107) |
| Collaborative Memory: Multi-User Sharing | May 2025 | [arXiv:2505.18279](https://arxiv.org/html/2505.18279v1) |
| MA-RAG: Multi-Agent RAG | May 2025 | [arXiv:2505.20096](https://arxiv.org/abs/2505.20096) |
| Multi-Agent Evolving Orchestration | May 2025 | [arXiv:2505.19591](https://arxiv.org/html/2505.19591v1) |
| SWE-bench Leaderboard Analysis | Jun 2025 | [arXiv:2506.17208](https://arxiv.org/html/2506.17208v2) |
| AgentOrchestra | Jun 2025 | [arXiv:2506.12508](https://arxiv.org/html/2506.12508v1) |
| Agent Exchange (AEX) | Jul 2025 | [arXiv:2507.03904](https://arxiv.org/abs/2507.03904) |
| AgentMesh | Jul 2025 | [arXiv:2507.19902](https://arxiv.org/html/2507.19902v1) |
| Agentic RAG with Knowledge Graphs | Jul 2025 | [arXiv:2507.16507](https://arxiv.org/abs/2507.16507) |
| Governance-as-a-Service | Aug 2025 | [arXiv:2508.18765](https://arxiv.org/abs/2508.18765) |
| FREE-MAD: Consensus-Free Debate | Sep 2025 | [arXiv:2509.11035](https://arxiv.org/abs/2509.11035) |
| Policy-as-Prompt | Sep 2025 | [arXiv:2509.23994](https://arxiv.org/abs/2509.23994) |
| Mental Models of Multi-Agent Tool Users | Oct 2025 | [arXiv:2510.06224](https://arxiv.org/html/2510.06224v1) |
| Building Foundational Guardrails for Agentic Systems | Oct 2025 | [arXiv:2510.09781](https://arxiv.org/abs/2510.09781) |
| Emergent Coordination in Multi-Agent LMs | Oct 2025 | [arXiv:2510.05174](https://arxiv.org/abs/2510.05174) |
| MARS: Multi-Agent Reasoning via Self-Play | Oct 2025 | [arXiv:2510.15414](https://arxiv.org/abs/2510.15414) |
| Multi-Agent Evolve via Co-evolution | Oct 2025 | [arXiv:2510.23595](https://arxiv.org/abs/2510.23595) |
| Agentic AI Security Survey | Oct 2025 | [arXiv:2510.23883](https://arxiv.org/abs/2510.23883) |
| HAL: Holistic Agent Leaderboard | Oct 2025 | [arXiv:2510.11977](https://arxiv.org/pdf/2510.11977) |
| Lazy Agents to Deliberation | Nov 2025 | [arXiv:2511.02303](https://arxiv.org/abs/2511.02303) |
| Market Making for Multi-Agent LLM Systems | Nov 2025 | [arXiv:2511.17621](https://arxiv.org/abs/2511.17621) |
| Scaling Graph Chain-of-Thought | Nov 2025 | [arXiv:2511.01633](https://arxiv.org/abs/2511.01633) |
| SWE-RL: Self-Play for Software Agents | Dec 2025 | [arXiv:2512.18552](https://arxiv.org/abs/2512.18552) |
| Self-Improving Agents through Self-Play | Dec 2025 | [arXiv:2512.02731](https://arxiv.org/abs/2512.02731) |
| SWE-EVO: Long-Horizon Software Evolution | Dec 2025 | [arXiv:2512.18470](https://arxiv.org/html/2512.18470) |
| Scaling Agent Systems (Google/DeepMind/MIT) | Dec 2025 | [arXiv:2512.08296](https://arxiv.org/abs/2512.08296) |
| AgentArk: Distilling Multi-Agent into Single LLM | Feb 2026 | [arXiv:2602.03955](https://arxiv.org/abs/2602.03955) |
| AdaptOrch: Task-Adaptive Orchestration | Feb 2026 | [arXiv:2602.16873](https://arxiv.org/abs/2602.16873) |
| Uncertainty in Multi-Agent Systems | Feb 2026 | [arXiv:2602.04234](https://arxiv.org/html/2602.04234) |
| Self-Play as Adversarial Imitation (Capacity Ceiling) | Feb 2026 | [arXiv:2602.01357](https://arxiv.org/abs/2602.01357) |

### Industry Reports & Blog Posts

| Source | Link |
|--------|------|
| Anthropic: Building Effective Agents | [anthropic.com/research/building-effective-agents](https://www.anthropic.com/research/building-effective-agents) |
| Anthropic: Multi-Agent Research System | [anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system) |
| Anthropic: Multi-Agent Safety Report | [aigl.blog/multi-agent-risks-from-advanced-ai](https://www.aigl.blog/multi-agent-risks-from-advanced-ai/) |
| Anthropic: How AI Transforms Work at Anthropic | [anthropic.com/research/how-ai-is-transforming-work-at-anthropic](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic) |
| Google: Towards a Science of Scaling Agent Systems | [research.google/blog/...](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/) |
| METR: Time Horizons | [metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) |
| METR: Time Horizon 1.1 | [metr.org/blog/2026-1-29-time-horizon-1-1](https://metr.org/blog/2026-1-29-time-horizon-1-1/) |
| LangChain: State of Agent Engineering 2025 | [langchain.com/state-of-agent-engineering](https://www.langchain.com/state-of-agent-engineering) |
| O'Reilly: Designing Effective Multi-Agent Architectures | [oreilly.com/radar/designing-effective-multi-agent-architectures](https://www.oreilly.com/radar/designing-effective-multi-agent-architectures/) |
| TDS: The 17x Error Trap | [towardsdatascience.com/...](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/) |
| Addy Osmani: The 80% Problem in Agentic Coding | [addyo.substack.com/p/the-80-problem-in-agentic-coding](https://addyo.substack.com/p/the-80-problem-in-agentic-coding) |
| Addy Osmani: Claude Code Agent Teams | [addyosmani.com/blog/claude-code-agent-teams](https://addyosmani.com/blog/claude-code-agent-teams/) |
| incident.io: Shipping Faster with Worktrees | [incident.io/blog/shipping-faster-with-claude-code-and-git-worktrees](https://incident.io/blog/shipping-faster-with-claude-code-and-git-worktrees) |
| Sequoia: 2026 - This is AGI | [sequoiacap.com/article/2026-this-is-agi](https://sequoiacap.com/article/2026-this-is-agi/) |
| Faros AI: Best AI Coding Agents 2026 | [faros.ai/blog/best-ai-coding-agents-2026](https://www.faros.ai/blog/best-ai-coding-agents-2026) |
| Anthropic 2026 Agentic Coding Trends Report | [resources.anthropic.com/...](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf) |

### Benchmarks & Leaderboards

| Benchmark | Link |
|-----------|------|
| SWE-bench | [swebench.com](http://www.swebench.com/) |
| SWE-bench Pro | [scale.com/leaderboard/swe_bench_pro_public](https://scale.com/leaderboard/swe_bench_pro_public) |
| Live-SWE-agent | [live-swe-agent.github.io](https://live-swe-agent.github.io/) |
| GAIA | [hal.cs.princeton.edu/gaia](https://hal.cs.princeton.edu/gaia) |
| The Agent Company | [the-agent-company.com](https://the-agent-company.com/) |
| Epoch AI SWE-bench Tracker | [epoch.ai/benchmarks/swe-bench-verified](https://epoch.ai/benchmarks/swe-bench-verified) |

---
---

# APPENDIX: Presentation Materials

Detailed structured content for building a presentation on SOTA multi-agent teams. Each section maps to a potential slide or group of slides, with speaker notes, data points, and narrative flow.

---

## Presentation Structure Overview

**Recommended flow (30-40 slides):**

1. Opening Hook (1 slide)
2. Context & Scale of the Field (2 slides)
3. Evolution Timeline (1 slide)
4. Taxonomy of Architectures (3 slides)
5. Key Research Breakthroughs (5 slides)
6. Benchmarks & Real Numbers (3 slides)
7. When Multi-Agent Helps vs Hurts (2 slides)
8. Failure Modes (3 slides)
9. Communication Protocols (2 slides)
10. Memory & Context (2 slides)
11. Human-AI Teaming (2 slides)
12. Production Reality (3 slides)
13. Claude Code Specific Patterns (3 slides)
14. Five Paradigm Shifts (2 slides)
15. What's Next (1 slide)
16. References (1 slide)

**Target audience options:**
- A: Engineering leadership — focus on ROI, production readiness, risks
- B: ML/AI researchers — focus on papers, architectures, benchmarks
- C: Product/strategy teams — focus on capabilities, timelines, competitive landscape

---

## Slide 1: Opening Hook

**Title:** "Multi-Agent AI Teams: What 60+ Papers and 1,340 Practitioners Tell Us"

**Key data point for hook:**
> "57% of enterprises now have AI agents in production. But 40% of multi-agent pilots fail within 6 months."
> — LangChain State of Agent Engineering, December 2025 (1,340 respondents)

**Speaker notes:**
- This is the central tension: the technology works, but the implementation is hard
- The field has exploded: research papers on multi-agent systems went from 820 in 2024 to 2,500+ in 2025
- We now have enough data to distinguish what actually works from what's hype
- Source: [langchain.com/state-of-agent-engineering](https://www.langchain.com/state-of-agent-engineering)

---

## Slide 2: Scale and Context

**Title:** "The Multi-Agent Explosion"

**Data points for visualization:**

```
Research papers on multi-agent LLM systems:
  2023: ~200
  2024: ~820
  2025: ~2,500+

Market signals:
  Claude Code: $1B annualized run rate within 6 months of launch
  CrewAI: $18M Series A, 100K+ agent executions/day
  LangGraph: 6.17M monthly downloads
  Devin: $10.2B valuation (acquired Windsurf for $250M)

Enterprise adoption (LangChain Survey):
  57% have agents in production
  67% of enterprises with 10K+ employees
  Top use cases: customer service (26.5%), research & analysis (24.4%), coding
```

**Speaker notes:**
- This is not a lab curiosity anymore — it's a production technology
- But the gap between demos and production is the #1 challenge
- Quality (32%) and security (62%) are the top cited barriers
- Sources: LangChain Survey, Anthropic reports, Faros AI analysis

---

## Slide 3: Timeline — Evolution of Multi-Agent Systems

**Title:** "From ChatDev to Agent Teams: 2023-2026"

**Timeline data:**

```
2023 Jul — ChatDev: First role-playing software development agents
2023 Aug — MetaGPT: SOP-driven multi-agent framework
2023 Aug — Graph of Thoughts: Beyond linear reasoning

2024 Feb — "More Agents Is All You Need": Scaling-by-voting
2024 May — SWE-agent: Agent-Computer Interface concept (NeurIPS)
2024 Jun — Mixture of Agents: Layered LLM aggregation (Together AI)
2024 Jun — MacNet: DAG-based 1000+ agent topology
2024 Oct — OpenAI Swarm: Experimental orchestration
2024 Nov — Anthropic MCP: Agent-tool protocol standard
2024 Nov — Magentic-One: Microsoft 5-agent system
2024 Dec — Anthropic "Building Effective Agents": Foundation guidance
2024 Dec — The Agent Company benchmark: Enterprise-realistic tasks

2025 Jan — AutoGen v0.4: Complete Microsoft redesign
2025 Feb — AFlow (ICLR Oral): Automated workflow discovery via MCTS
2025 Mar — MAST: First failure taxonomy for multi-agent systems
2025 Apr — Google A2A Protocol: Agent-to-agent standard
2025 May — Anthropic Multi-Agent Research System: 90.2% improvement
2025 Jun — Mixture of Agents at ICLR: Open-source beats GPT-4o
2025 Aug — SWE-RL: Self-play for code agents (+10.4 pts)
2025 Oct — LangGraph 1.0: Production standard
2025 Dec — Google/DeepMind/MIT: Science of Scaling Agent Systems

2026 Jan — Claude Code Agent SDK renamed from Code SDK
2026 Feb — Claude Code Agent Teams (experimental)
2026 Feb — AdaptOrch: Orchestration > Model Selection
2026 Feb — AgentArk: Distill swarm into single model
```

**Speaker notes:**
- Key inflection points: MCP (Nov 2024) standardized tool communication; Google scaling paper (Dec 2025) provided the first empirical science
- The trend: from ad-hoc chatbots to structured, measurable, production-grade systems
- Note the accelerating pace — 2025 had more foundational work than all prior years combined

---

## Slide 4-6: Taxonomy of Architectures

### Slide 4: "Five Architecture Patterns"

**Title:** "How Agent Teams Are Organized"

```
┌─────────────────────────────────────────────────────────┐
│                 ARCHITECTURE TAXONOMY                     │
├──────────────────┬──────────────────────────────────────┤
│ 1. SINGLE +      │ One LLM with self-reflection,        │
│    REFLECTION     │ tool use, and multi-step reasoning    │
│                   │ Example: ReAct, Chain-of-Thought      │
├──────────────────┼──────────────────────────────────────┤
│ 2. INDEPENDENT   │ Multiple agents, no coordination.     │
│    (Bag of        │ Majority voting on outputs            │
│     Agents)       │ Example: "More Agents Is All You Need"│
├──────────────────┼──────────────────────────────────────┤
│ 3. CENTRALIZED   │ Orchestrator assigns tasks to workers. │
│    (Hub-Spoke)    │ Workers report back to orchestrator   │
│                   │ Example: Anthropic Multi-Agent,       │
│                   │ Magentic-One, MetaGPT                 │
├──────────────────┼──────────────────────────────────────┤
│ 4. DECENTRALIZED │ Agents communicate peer-to-peer.      │
│    (Mesh/Debate)  │ No central authority                  │
│                   │ Example: Multi-Agent Debate, ChatDev   │
├──────────────────┼──────────────────────────────────────┤
│ 5. HYBRID        │ Hierarchical: orchestrator + sub-teams │
│    (Hierarchical) │ with internal peer communication      │
│                   │ Example: MegaAgent, Self-Organized     │
└──────────────────┴──────────────────────────────────────┘
```

**Speaker notes:**
- Google/DeepMind tested all five across 180 configurations
- No single architecture wins everywhere — task structure determines optimal choice
- Source: [arXiv:2512.08296](https://arxiv.org/abs/2512.08296)

### Slide 5: "Which Architecture for Which Task?"

**Decision matrix (data from Google/DeepMind/MIT, 180 configurations):**

```
Task Type                    → Best Architecture        → Improvement
─────────────────────────────────────────────────────────────────────
Parallelizable work          → Centralized orchestrator  → +80.8%
  (code review, testing,
   multi-file generation)

Exploration / search         → Decentralized debate      → +9%
  (web browsing, research)

Sequential reasoning         → SINGLE AGENT (don't use   → Multi-agent
  (math, logic chains)         multi-agent!)               DEGRADES -39% to -70%

Easy-to-verify tasks         → Independent + voting      → Scales with N
  (code with tests)

Quality-critical generation  → Layered MoA               → Beats GPT-4o
  (text, summaries)
```

**Speaker notes:**
- The -39% to -70% degradation for sequential reasoning is the most important finding
- If your single agent is already >45% accurate, adding agents may not help
- Optimal communication: 0.39 messages per turn — less is more
- Source: [arXiv:2512.08296](https://arxiv.org/abs/2512.08296)

### Slide 6: "Architecture in Practice — Three Tiers"

**For Claude Code specifically:**

```
TIER 1: Subagents (Stable, Recommended)
├── Custom .claude/agents/*.md files
├── Own context window, tools, model
├── Git worktree isolation
├── Up to 10 parallel tasks
├── Persistent memory across sessions
└── ROI: Highest. Start here.

TIER 2: Agent Teams (Experimental, Feb 2026)
├── Team lead + teammates
├── Shared task list + mailbox
├── ~7x token cost
└── Use for: tasks requiring agent-to-agent communication

TIER 3: External Orchestrators (Community)
├── claude-squad (5.6K stars): TUI + tmux + worktrees
├── claude_code_agent_farm: 20+ parallel agents
├── overstory: SQLite-based inter-agent mail
└── Best for: custom workflows beyond built-in capabilities
```

**Speaker notes:**
- Most teams should start with Tier 1 and only move up when they hit clear limitations
- Tier 2 costs 7x tokens — only economical for high-value tasks
- Source: [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents), [code.claude.com/docs/en/agent-teams](https://code.claude.com/docs/en/agent-teams)

---

## Slide 7-11: Key Research Breakthroughs

### Slide 7: "Breakthrough #1 — Orchestration Beats Model Selection"

**Paper:** AdaptOrch (February 2026)
**Source:** [arXiv:2602.16873](https://arxiv.org/abs/2602.16873)

**Key visual data:**
```
Performance gain from switching model:     ~3-5%
Performance gain from optimal orchestration: 12-23%

As LLMs converge in capability,
architecture of coordination > choice of model
```

**Three contributions:**
1. Performance Convergence Scaling Law
2. Topology Routing Algorithm: O(|V|+|E|) — maps DAGs to optimal orchestration
3. Adaptive Synthesis Protocol with provable termination guarantees

**Speaker notes:**
- This is the most important strategic insight: invest in orchestration design, not just model upgrades
- The Topology Routing Algorithm makes this actionable — you can automatically select the right coordination pattern
- Tested on SWE-bench, GPQA, and RAG tasks

### Slide 8: "Breakthrough #2 — The Science of Scaling"

**Paper:** Towards a Science of Scaling Agent Systems (Google/DeepMind/MIT, December 2025)
**Source:** [arXiv:2512.08296](https://arxiv.org/abs/2512.08296)

**Six critical findings:**

```
1. Benefits DIMINISH as base model improves
   └── Single agent >45% → adding agents may hurt

2. Error amplification is real
   └── Independent agents: 17.2x error multiplication
   └── Centralized coordination: 4.4x (containment)

3. Communication has an optimum
   └── 0.39 messages per turn — beyond this = redundancy

4. Architecture MUST match task structure
   └── Centralized: +80.8% on parallel tasks
   └── Decentralized: +9% on exploration
   └── Sequential reasoning: EVERY variant degrades -39% to -70%

5. Model families behave differently
   └── OpenAI models: gain from centralized/hybrid
   └── Google models: plateau quickly
   └── Anthropic models: higher variance

6. Predictive power
   └── Their framework predicts optimal strategy for 87% of configs
```

**Speaker notes:**
- This is the first truly empirical, large-scale study of multi-agent scaling
- 180 configurations tested — not theoretical, not cherry-picked
- The 87% prediction accuracy means we can now make principled architecture decisions

### Slide 9: "Breakthrough #3 — First Failure Taxonomy"

**Paper:** MAST — Why Do Multi-Agent LLM Systems Fail? (ICLR 2025)
**Source:** [arXiv:2503.13657](https://arxiv.org/abs/2503.13657)

**14 failure modes in 3 categories:**

```
Category 1: SYSTEM DESIGN ISSUES
├── Poorly defined agent roles
├── Inadequate tool integration
├── Missing error recovery mechanisms
├── Inflexible workflow structures

Category 2: INTER-AGENT MISALIGNMENT
├── Role confusion / swapping
├── Hallucination propagation (cascade)
├── Conflicting objectives
├── Communication breakdown
├── Infinite message loops

Category 3: TASK VERIFICATION FAILURES
├── Superficial verification
├── Missing edge case coverage
├── Incorrect success criteria
├── Premature task completion
├── No ground truth validation
```

**Critical numbers:**
```
ChatDev correctness: as low as 25%
Token overhead: 4-220x vs single agent
Verifier presence: NOT a silver bullet
1,600+ annotated traces across 7 frameworks
```

**Speaker notes:**
- First systematic study with 1,600+ traces and high agreement (kappa=0.88)
- The hallucination cascade is the most dangerous failure: Agent A hallucinates → Agent B treats it as fact → Agent C builds on it → compound error
- Having a verifier helps but doesn't solve the problem — you need multi-layered verification

### Slide 10: "Breakthrough #4 — Self-Improving Teams"

**Two key papers:**

```
CoMAS (ICLR 2026) — Co-Evolving Multi-Agent Systems
├── Agents generate intrinsic rewards from interaction quality
├── LLM-as-a-judge formulates rewards
├── Each agent optimizes its policy via RL
├── First practical framework for autonomous co-evolution
├── Scalability improves with more diverse agents
└── Source: arXiv:2510.08529

AFlow (ICLR 2025 Oral, top 1.8%) — Automated Workflow Discovery
├── Monte Carlo Tree Search over code-represented workflows
├── Composable "Operators": Ensemble, Review, Revise
├── Smaller models outperform GPT-4o at 4.55% inference cost
├── 5.7% average improvement over SOTA
└── Source: arXiv:2410.10762
```

**Key message:** Agent workflows should be searched/optimized, not hand-designed

**Speaker notes:**
- CoMAS shows teams can improve without human supervision
- AFlow shows the workflow itself (not just the agents) can be automatically optimized
- Together: a path toward self-improving, self-organizing agent teams
- But note the capacity ceiling paper (arXiv:2602.01357): infinite self-improvement is not possible

### Slide 11: "Breakthrough #5 — Human-AI Teaming at Scale"

**Paper:** HULA — Human-In-the-Loop Agents at Atlassian (ICSE 2025)
**Source:** [arXiv:2411.12924](https://arxiv.org/abs/2411.12924)

**The largest real-world deployment study:**

```
Scale: 2,600 practitioners, 22,000+ JIRA issues

Architecture: AI Planner → Human Review → AI Coder → Human Review → PR

Results funnel:
  100% work items received
   79% got AI coding plans
   82% of plans approved by engineers
   25% reached PR stage
   59% of PRs merged

Key insight: Human approval at PLAN stage (not code stage)
is the most efficient intervention point
```

**Speaker notes:**
- This is the gold standard for real-world validation — 22K issues, not a toy benchmark
- The plan-stage review is critical: catching problems early is 10x cheaper than code review
- 59% merge rate means the AI is genuinely useful, not just generating noise
- This maps directly to the spec-driven development pattern used in Claude Code

---

## Slide 12-14: Benchmarks & Real Numbers

### Slide 12: "SWE-bench — The Coding Agent Olympics"

**Title:** "Where Are We Actually At?"

```
SWE-bench Verified (well-defined bug fixes):
  2024 Feb: ~15% (first agents)
  2024 Dec: ~50% (rapid improvement)
  2025 Jun: ~72% (OpenHands + critic)
  2026 Feb: ~79% (Sonar Foundation Agent, Claude Opus 4.5)

SWE-bench Pro (harder, multi-file engineering):
  Best scores: 23-46%

The gap: Verified (79%) vs Pro (23-46%) reveals the real state
```

**Winning techniques:**
```
1. Multi-model diversity: Generate patches with 3 different models,
   select with a reasoning model (o1/o3)
   → Used by: TRAE (70.4%), Devlo (70.2%)

2. Inference-time scaling + critic: Dedicated critic model
   evaluates candidate patches
   → Used by: OpenHands (72%)

3. Agent-Computer Interface design: Custom tools > raw shell
   → mini-swe-agent (100 lines) scores >74%

4. Cost-effective: Sonar Foundation Agent
   → $1.26 per issue, 10.5 min average
```

**Speaker notes:**
- The 79% vs 23% gap is the real signal — don't be fooled by best-case scores
- SWE-bench Pro tasks require sustained, multi-commit engineering — today's agents struggle here
- Sources: [swebench.com](http://www.swebench.com/), [scale.com/leaderboard/swe_bench_pro_public](https://scale.com/leaderboard/swe_bench_pro_public)

### Slide 13: "Beyond Code — General Agent Benchmarks"

```
GAIA (466 real-world questions requiring reasoning + tools):
  SOTA: ~90% (end 2025)
  Claude Opus 4.5: 77.5% overall
  Human-AI gap: Still substantial

OSWorld (open-ended computer tasks):
  Best: 34.5% (50-step budget)
  ~65% of tasks still fail

WebArena (812 web tasks):
  Best: 61.7% (IBM CUGA)
  WebChoreArena variant: 37.8%

The Agent Company (175 enterprise tasks):
  First benchmark testing realistic corporate workflows
  Multi-tier scoring: process + result + interaction
```

**Speaker notes:**
- Agent performance drops sharply as tasks become more open-ended
- OSWorld at 34.5% means agents fail on 2 out of 3 general computer tasks
- The Agent Company is the closest to testing real-world utility
- Sources: [hal.cs.princeton.edu/gaia](https://hal.cs.princeton.edu/gaia), [the-agent-company.com](https://the-agent-company.com/)

### Slide 14: "Time Horizons — The Exponential Curve"

**Source:** METR (Measuring AI Ability to Complete Long Tasks)

```
Task-completion time horizon
(task length agents complete with 50% reliability):

2019-2023: Doubling every ~7 months
2024-2025: Doubling every ~4 months
Latest estimate: Doubling every ~89 days

Current (Feb 2026): Reliably minutes-long tasks
                    Some hour-long tasks (unreliable)

Projection if trend continues:
  Mid 2026: Hour-long tasks reliably
  Early 2027: Day-long tasks
  Late 2027: Week-long tasks
  2028: Month-long autonomous tasks
```

**Speaker notes:**
- This exponential curve is the most important strategic planning input
- Architecture decisions should account for capability doubling every ~3 months
- Build for checkpointing, resumption, and human review at natural breakpoints
- Caveat: the trend may plateau for qualitatively harder tasks
- Sources: [metr.org/blog/2025-03-19](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/), [metr.org/blog/2026-1-29](https://metr.org/blog/2026-1-29-time-horizon-1-1/)

---

## Slide 15-17: Failure Modes Deep Dive

### Slide 15: "The 17x Error Trap"

**Source:** [TDS Analysis](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/)

```
"Bag of Agents" anti-pattern:
  Just throwing multiple agents at a problem
  without structured coordination

Result: 17x ERROR AMPLIFICATION

Independent agents: 17.2x error multiplication
Centralized coordination: 4.4x (contained)

The coordination tax:
  Accuracy gains saturate or fluctuate beyond 4 agents
  without structured topology
```

**Speaker notes:**
- "More agents" is NOT always better — this is the most common misconception
- The 4-agent threshold is practical guidance: beyond 4, you need explicit topology
- Error amplification means each agent's mistakes compound through the pipeline

### Slide 16: "Hallucination Cascade"

```
The most dangerous multi-agent failure mode:

Agent A: Generates response with hallucinated fact
    ↓
Agent B: Treats Agent A's output as ground truth
    ↓
Agent C: Builds on the compounded false context
    ↓
Agent D (Verifier): Checks against Agent C's output
    ↓
Result: "Verified" hallucination that passed QA

Why verifiers fail:
  - They verify against agent-generated context, not ground truth
  - Superficial checks pass ("Does the code compile?" ≠ "Is it correct?")
  - ChatDev-style verifiers: only ~80% accurate themselves
```

**Speaker notes:**
- This is why multi-layered verification is necessary
- Best practice: verify against external ground truth (test suites, formal specs), not agent output
- The Atlassian HULA model works because humans verify the plan, not the generated artifacts
- Source: [arXiv:2503.13657](https://arxiv.org/abs/2503.13657) (MAST study)

### Slide 17: "Production Failure Statistics"

```
LangChain Survey (1,340 respondents, December 2025):
  40% of multi-agent pilots fail within 6 months
  Quality: #1 barrier (32%)
  Security: Top challenge (62%)

Forrester prediction:
  75% of firms building complex agentic architectures
  independently will fail

Common failure causes:
  1. Treating agent systems like deterministic software
  2. No observability (can't debug what you can't see)
  3. Context window exhaustion under production load
  4. Pilot tested 50-500 queries; production handles 10K-100K+
  5. "The model changed underneath you" — behavior drift with updates
```

**Speaker notes:**
- The demo-to-production gap ("Valley of Death") is real
- Solutions: LangGraph 1.0 (durable execution, streaming, memory, HITL), AutoGen v0.4 (event-driven), hooks-based guardrails
- Source: [langchain.com/state-of-agent-engineering](https://www.langchain.com/state-of-agent-engineering)

---

## Slide 18-19: Communication Protocols

### Slide 18: "How Agents Should Talk to Each Other"

```
PROTOCOL          BEST FOR                      EVIDENCE
─────────────────────────────────────────────────────────
Actor-Critic      Most tasks                    ICLR 2025
                  Structured feedback            ACC-Collab

Multi-Agent       Hard problems with             21+ papers
Debate (MAD)      verifiable answers             ICLR/ACL 2025
                  ⚠️ Plateau after 3-4 rounds

Majority Voting   Well-defined, discrete          ACL 2025
                  answers

Market/Auction    Need truthfulness,              arXiv 2511
                  interpretability

Shared Memory     "Team mind" — immediate         arXiv 2505
                  knowledge sharing
                  ⚠️ Requires conflict resolution
```

**Speaker notes:**
- Actor-Critic is the safest default — it's structured and well-validated
- Debate works but has quadratic token costs and plateaus quickly
- Market mechanisms are the most novel and underexplored

### Slide 19: "Standardizing Agent Communication"

```
Two complementary protocols:

MCP (Model Context Protocol) — Anthropic, November 2024
├── Agent ↔ Tool communication
├── Open source standard
├── Like USB for AI tools
└── modelcontextprotocol.io

A2A (Agent-to-Agent Protocol) — Google, April 2025
├── Agent ↔ Agent communication
├── Linux Foundation, 50+ partners
├── Like HTTP for AI agents
└── a2a-protocol.org

Together: The TCP/IP of agent systems
```

**Speaker notes:**
- MCP + A2A are the most important infrastructure standardization of 2024-2025
- Production systems adopting these early report significantly lower integration costs
- Build tools as MCP servers regardless of framework — ecosystem interoperability pays for itself

---

## Slide 20-21: Memory & Context

### Slide 20: "The Memory Problem"

```
The fundamental constraint:
  Context window = 1M tokens (all models)
  Performance degrades at 80%+ utilization
  Multi-agent: each agent has its OWN context window

Solutions evolving:

RAG (2023-2024):
  ├── Retrieve → Generate
  └── Problem: Transient, no lifecycle tracking

Agentic RAG (2025):
  ├── Retrieve → Evaluate → Re-retrieve → Validate → Generate
  └── Better, but still stateless

Agentic Memory (2025+):
  ├── A-MEM (NeurIPS 2025): Self-organizing Zettelkasten
  ├── MemOS: OS-level memory management for AI
  ├── Collaborative Memory: Team-shared with access control
  └── Memory that EVOLVES: new memories update old ones
```

**Speaker notes:**
- Memory is increasingly recognized as the bottleneck, not model capability
- The Zettelkasten pattern from A-MEM is elegant: memories link to and update each other
- For Claude Code: persistent agent memory across sessions, `/compact` at 65-70%, subagents for context isolation
- Sources: [arXiv:2502.12110](https://arxiv.org/abs/2502.12110), [arXiv:2501.09136](https://arxiv.org/abs/2501.09136)

### Slide 21: "Context Management in Practice"

```
Claude Code practical strategies:

1. /clear between unrelated tasks
   └── Prevents "kitchen sink session" — most common failure

2. /compact at 65-70% capacity (NOT 80%)
   └── Last 20% gives disproportionately poor results

3. Subagents for context isolation
   └── Each subagent gets its own 1M window

4. Skills architecture for on-demand loading
   └── Load domain knowledge only when needed
   └── Saves ~15,000 tokens/session (82% improvement)

5. CLAUDE.md: 50-100 lines maximum
   └── Only what Claude can't infer from code
   └── Check into git, prune regularly

Anthropic's production pattern:
  "When context limits approach, spawn fresh subagents
   with clean contexts + careful handoffs"
```

---

## Slide 22-23: Human-AI Teaming

### Slide 22: "The Atlassian Model — Largest Real-World Study"

```
HULA: 2,600 engineers × 22,000+ JIRA issues

                 100% Work items
                      ↓
              ┌─── AI Planner ───┐
              │    79% got plans  │
              └────────┬──────────┘
                       ↓
              ┌─── Human Review ──┐
              │  82% approved     │
              └────────┬──────────┘
                       ↓
              ┌─── AI Coder ─────┐
              │   25% reached PR  │
              └────────┬──────────┘
                       ↓
              ┌─── Human Review ──┐
              │   59% merged      │
              └───────────────────┘

Key insight: Review the PLAN, not the code.
  → Catching problems at plan stage = 10x cheaper
```

**Source:** [arXiv:2411.12924](https://arxiv.org/abs/2411.12924) (ICSE 2025)

### Slide 23: "Anthropic's Internal Data"

**Source:** [anthropic.com/research/how-ai-is-transforming-work-at-anthropic](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic)

```
132 engineers, 200K+ Claude Code sessions:

Usage: 59% of all engineering work involves Claude
Self-reported productivity boost: 50% average

Evolution over 6 months:
  Task complexity: 3.2 → 3.8 (scale 1-5)
  Code design/architecture: 1% → 10% of usage
  New feature implementation: 14% → 37%

Concern: Engineers worry about losing deep expertise
  "The mentorship and code review culture that AI replaces"
```

---

## Slide 24-26: Production Reality

### Slide 24: "What Companies Actually Report"

```
SUCCESS STORIES:
  Amazon: Modernized thousands of legacy Java apps in weeks
  Genentech: Agent ecosystems for complex research workflows
  Atlassian: 59% of AI-generated PRs merged (22K issues)
  Anthropic: 90.2% improvement with multi-agent research system
  incident.io: Parallel feature shipping with git worktrees

FAILURE PATTERNS:
  40% of multi-agent pilots fail within 6 months
  75% of independently-built complex architectures will fail (Forrester)
  Token costs: 4-15x for multi-agent (up to 220x worst case)
  The "almost right" problem: 66% get close-but-wrong solutions
```

### Slide 25: "Cost Reality"

```
Token cost multipliers:

Single agent baseline:                    1x
Subagents (Claude Code):                  2-3x
Agent Teams (Claude Code):                ~7x
Full multi-agent swarm:                   4-15x
Worst case (unoptimized debate):          up to 220x

Cost management strategies:
  1. Model tiering: Opus for orchestration, Haiku for scanning
  2. Prompt caching: Automatic for repeated content
  3. /clear and /compact hygiene: 50-70% token reduction
  4. MCP Tool Search: 95% reduction in tool description tokens
  5. Skills-based loading: 82% improvement over upfront loading
  6. Batch API: 50% discount for async processing

Break-even rule of thumb:
  Multi-agent is worth it when task value > 10x token cost
  For $1 of tokens, task should generate >$10 of value
```

### Slide 26: "The Winning Workflow"

```
The pattern used by most successful teams:

    ┌──────────────────────────┐
    │  1. SPEC (human writes)  │ ← 80% of the effort here
    │     Requirements doc     │
    │     Architecture doc     │
    │     Task breakdown       │
    └───────────┬──────────────┘
                ↓
    ┌──────────────────────────┐
    │  2. REVIEW (human)       │ ← Cheap to fix here
    │     Approve plan         │
    │     Catch design errors  │
    └───────────┬──────────────┘
                ↓
    ┌──────────────────────────┐
    │  3. EXECUTE (agents)     │ ← 20% of the effort
    │     Parallel subagents   │
    │     Git worktree isolation│
    │     Hooks for guardrails │
    └───────────┬──────────────┘
                ↓
    ┌──────────────────────────┐
    │  4. VERIFY (agents+human)│
    │     Automated tests      │
    │     Critic model review  │
    │     Human final check    │
    └──────────────────────────┘

"1 iteration with structure ≈ 8 iterations without"
```

---

## Slide 27-28: Five Paradigm Shifts

### Slide 27: "Five Things That Changed"

```
1. INTERFACE > MODEL
   How agents interact with tools matters more than which LLM
   Evidence: mini-swe-agent (100 lines) = 74% SWE-bench
   Source: SWE-agent, NeurIPS 2024

2. ORCHESTRATION > MODEL
   Coordination architecture matters more than model choice
   Evidence: 12-23% gain from orchestration vs 3-5% from model switch
   Source: AdaptOrch, February 2026

3. EXTERNAL GOVERNANCE > INTERNAL ALIGNMENT
   External enforcement > hoping each agent is aligned
   Evidence: GaaS, Policy-as-Prompt frameworks
   Source: arXiv 2508/2509

4. THROUGHPUT > SPEED
   Background parallel agents > faster single agent
   Evidence: Time horizons doubling every ~89 days
   Source: METR, January 2026

5. STANDARD PROTOCOLS > CUSTOM INTEGRATION
   MCP + A2A = TCP/IP of agent systems
   Evidence: 50+ A2A partners, universal MCP adoption
   Source: Anthropic, Google, Linux Foundation
```

### Slide 28: "What This Means for Your Team"

```
START WITH:
  ✓ Custom subagents with focused prompts and tool restrictions
  ✓ Git worktrees for parallel work isolation
  ✓ Hooks for automated formatting, testing, and safety
  ✓ Spec-driven workflow: Plan → Review → Execute
  ✓ CLAUDE.md under 100 lines, checked into git

AVOID:
  ✗ "Bag of agents" without structured coordination
  ✗ Multi-agent for sequential reasoning tasks
  ✗ Full autonomy without human checkpoints
  ✗ Stuffing everything into CLAUDE.md
  ✗ Running agent teams when subagents suffice (7x cost!)

WATCH:
  → Self-improving teams (CoMAS, AFlow)
  → Automated workflow discovery (MCTS over coordination patterns)
  → Agent-to-agent protocols (A2A maturation)
  → Distillation (train with multi-agent, deploy single agent)
  → Time horizon expansion (hours → days within 12 months)
```

---

## Slide 29: "What's Next"

```
Near-term (2026):
  ├── Agent teams becoming production-ready
  ├── MCP + A2A standardization completing
  ├── Automated workflow optimization (AFlow-style) going mainstream
  └── Reliable hour-long autonomous tasks

Medium-term (2027):
  ├── Day-long autonomous engineering tasks
  ├── Self-improving agent teams in production
  ├── Distilled single-agent deployment of multi-agent knowledge
  └── Agent memory systems replacing ad-hoc RAG

The open question:
  "Will agents compose into reliable systems,
   or will coordination overhead always limit scaling?"

  Google/DeepMind says: depends on task structure.
  The answer is nuanced, not universal.
```

---

## Slide 30: "Key References"

```
MUST-READ (5 papers that define the field):

1. Scaling Agent Systems — Google/DeepMind/MIT (Dec 2025)
   The empirical science of when multi-agent works
   arXiv:2512.08296

2. MAST: Why Do Multi-Agent LLM Systems Fail? (ICLR 2025)
   First failure taxonomy, 1600+ traces analyzed
   arXiv:2503.13657

3. Building Effective Agents — Anthropic (Dec 2024)
   Foundation guidance: simplicity, transparency, interfaces
   anthropic.com/research/building-effective-agents

4. AFlow: Automating Agentic Workflow Generation (ICLR 2025 Oral)
   Automated workflow discovery via MCTS
   arXiv:2410.10762

5. HULA: Human-In-the-Loop Agents — Atlassian (ICSE 2025)
   Largest real-world deployment study
   arXiv:2411.12924

Full reference list: 60+ papers and 15+ industry reports
in the accompanying research document.
```

---

## Additional Presentation Data Points

### For Q&A Preparation

**Q: "Is multi-agent really better than a single strong model?"**
> Google/DeepMind tested 180 configurations. For parallelizable tasks, centralized multi-agent gives +80.8%. For sequential reasoning, it degrades by 39-70%. The answer depends on task structure. If your single agent already scores >45%, adding agents may not help.

**Q: "What's the ROI?"**
> Anthropic internal study: 50% self-reported productivity boost across 132 engineers, 200K sessions. Atlassian: 59% merge rate on AI-generated PRs across 22K issues. Amazon: modernized thousands of legacy apps in weeks. But token costs are 4-15x higher for multi-agent setups.

**Q: "What about security?"**
> 62% of enterprises cite security as a top challenge (LangChain survey). Anthropic reported cyber-espionage actors using Claude Code for automated reconnaissance. Solutions: PreToolUse hooks for blocking dangerous commands, tool whitelists per subagent, external governance (GaaS pattern).

**Q: "How do we start?"**
> 1. Custom subagents in `.claude/agents/` with restricted tools. 2. Git worktrees for isolation. 3. Hooks for automated quality checks. 4. Spec-driven workflow (plan → review → execute). 5. CLAUDE.md under 100 lines. Do NOT start with agent teams or swarms.

**Q: "Can agents improve themselves?"**
> Yes, but with limits. CoMAS (ICLR 2026) shows autonomous co-evolution via interaction rewards. SWE-RL shows +10.4 pts from self-play on code. But February 2026 paper proves there's a capacity ceiling — infinite self-improvement is not possible with current methods.

**Q: "When will agents handle day-long tasks?"**
> METR tracks this exponential curve: time horizons double every ~89 days. Current: minutes reliably, some hours. Projection: day-long tasks by early 2027 if trend continues. But the curve may plateau for qualitatively harder tasks requiring cross-team coordination and handling ambiguity.

### Comparative Architecture Table (for handout)

```
FRAMEWORK     YEAR  ARCHITECTURE         RESULT           COST
─────────────────────────────────────────────────────────────────
ChatDev       2023  7 roles, chat chain  25% correctness  >$10/task
MetaGPT       2023  SOP-driven, 5 roles  ICLR 2024 Oral   Medium
AgentCoder    2024  3 agents, iterative  96.3% HumanEval  56.9K tokens
MapCoder      2024  4 agents, recall-based 93.9% HumanEval Medium
Magentic-One  2024  5 agents, dual-ledger Competitive     High
OpenHands     2025  Agent delegate + critic 72% SWE-bench  Medium
Anthropic MAS 2025  Orchestrator+workers  +90.2% vs solo   ~15x tokens
Claude Teams  2026  Lead + teammates      Experimental     ~7x tokens
Sonar Agent   2026  LlamaIndex-based      79.2% SWE-bench  $1.26/issue
```

### Key Quotes for Slides

> "The most successful implementations use simple, composable patterns, not complex frameworks."
> — Anthropic, "Building Effective Agents" (December 2024)

> "Multi-agent overhead is real: systems consume 4-220x more tokens than single-agent alternatives."
> — MAST study, ICLR 2025

> "As LLMs converge in capability, how you orchestrate agents matters more than which model you use."
> — AdaptOrch, February 2026

> "Benefits of multi-agent diminish as base model improves. When single-agent accuracy exceeds ~45%, adding agents may yield diminishing or negative returns."
> — Google/DeepMind/MIT, December 2025

> "59% of AI-generated PRs were merged. Human approval at the plan stage is the most efficient intervention point."
> — HULA/Atlassian, ICSE 2025

> "Agent workflows should be searched and optimized, not hand-designed."
> — AFlow, ICLR 2025 Oral (top 1.8%)
