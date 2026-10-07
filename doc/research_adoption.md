# Research adoption and follow-up work

Last checked: **2026-10-07**.

This record tracks public evidence of VillagerBench task use, VillagerAgent integration, baseline comparisons, and related research. A citation alone does not establish code or dataset reuse. The entries below are selective; no total adoption or citation count is inferred.

## Task reuse and framework integration

| Work | Authors / year | Relationship | Primary evidence location |
|---|---|---|---|
| [MultiAgentBench: Evaluating the Collaboration and Competition of LLM agents](https://aclanthology.org/2025.acl-long.421/) | Zhu et al., ACL 2025 | Environment, tools, and construction target reuse | [Paper](https://arxiv.org/html/2503.01935v1), Minecraft appendix: **Environment Description** and **Benchmark Curation Details** |
| [CausalMACE: Causality Empowered Multi-Agents in Minecraft Cooperative Tasks](https://aclanthology.org/2025.findings-emnlp.777/) | Chai et al., EMNLP 2025 | VillagerBench evaluation settings | [Paper PDF](https://aclanthology.org/2025.findings-emnlp.777.pdf), **Appendix C**, printed p. 14421 (PDF p. 12) |
| [Gated Coordination for Efficient Multi-Agent Collaboration in Minecraft Game](https://arxiv.org/abs/2604.18975) | Jian et al., arXiv preprint, April 2026 | VillagerAgent integration and construction benchmark extension | [Paper](https://arxiv.org/html/2604.18975v1), **Sections 4.1 and 4.4**, **Table 2**, and appendix **Custom VillagerAgent Split** |

### MultiAgentBench / MARBLE

The authors adapt the Minecraft environment from VillagerAgent, select 11 construction-related tools, and reuse the same 100 target structures. This establishes direct construction-target reuse and environment/tool adaptation, rather than merely related-work citation. Author repository: [ulab-uiuc/MARBLE](https://github.com/ulab-uiuc/MARBLE).

### CausalMACE

Appendix C follows VillagerBench task counts and metrics for construction, farm-to-table cooking, and escape-room evaluation. This supports benchmark-setting use; it does not independently establish wholesale reuse of our implementation. The linked [author repository](https://github.com/qccq315/CausalMACE) currently contains a minimal README rather than a released implementation.

### Gated Coordination

The paper evaluates native VillagerBench construction tasks and modifies resource distribution and teammate-state sharing for a custom collaboration setting. Its VillagerAgent + Ours experiments establish reported integration of the communication mechanism. The 200 episodes in Section 4.1 describe the **MindCraft** custom dataset, not the VillagerBench split. The paper remains a preprint; this record does not claim independent reproduction.

## Baseline comparison

| Work | Authors / year | Verified relationship | Evidence |
|---|---|---|---|
| [DeMAC: Enhancing Multi-Agent Coordination with Dynamic DAG and Manager-Player Feedback](https://aclanthology.org/2025.findings-emnlp.757/) | Liu et al., EMNLP 2025 | VillagerAgent appears as an Overcooked comparison baseline | [Paper PDF](https://aclanthology.org/2025.findings-emnlp.757.pdf), **Section 4.2 and Table 1**, printed pp. 14077–14078 |

DeMAC studies dynamic DAG updates and manager-player feedback. Its comparison table supports a baseline-comparison relationship; it does not establish Minecraft task/data reuse or VillagerAgent code integration.

## Related research citing or discussing our work

| Work | Authors / year | Research direction | Evidence and scope |
|---|---|---|---|
| [PillagerBench: Benchmarking LLM-Based Agents in Competitive Minecraft Team Environments](https://arxiv.org/abs/2509.06235) | Schipper et al., IEEE CoG 2025 | Competitive team-vs-team environments and TactiCrafter | [Paper](https://arxiv.org/html/2509.06235v1), **Section II-B** discusses VillagerAgent. [Code](https://github.com/aialt/PillagerBench). No direct reuse established from this discussion. |
| [Multi-agent Framework for Time-Sensitive Complementary Collaboration in Minecraft](https://arxiv.org/abs/2606.15684) | Yi et al., arXiv preprint, June 2026 | TickingCollabBench: heterogeneous agents, dynamic tasks, and real-time constraints | [Paper](https://arxiv.org/html/2606.15684v1), **Introduction and Table 1** compare with VillagerBench. This is a benchmark-design discussion, not verified task reuse. |

## Maintaining the list

For an addition, provide the paper or author repository URL, the exact section/file that identifies VillagerBench or VillagerAgent, and what was used: task definitions/targets, evaluation settings, tools, implementation, or a comparison baseline. Record the publication year and distinguish preprints from conference papers.

Search scope for this update: public primary papers and author repositories mentioning VillagerBench, VillagerAgent, or arXiv 2406.05720, with emphasis on 2025–2026. Statements above describe the cited authors' reported use; they are not a reproduction study.
