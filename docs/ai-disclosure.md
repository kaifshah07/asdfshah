# AI Tool Usage Disclosure

This document provides a clear, honest, and transparent account of how artificial intelligence tools were used during the development of the Gridbricks UK wind generation forecast and decision-support dashboard.

---

## 1. Purpose of AI Assistance

The primary purpose of using AI assistance in this project was to accelerate technical learning, work through complex domain requirements, troubleshoot development roadblocks, and explore robust architectural patterns. Developing a full-stack energy decision-support system involves integrating energy market rules (such as Elexon BSC settlement periods and gate-closure mechanics), statistical time-series error metrics, async Python APIs, and interactive React charting. AI served as a valuable interactive learning partner, sounding board, and technical advisory resource throughout this process.

---

## 2. AI Tools Used

The following AI assistance tools were utilized during the project:

- **ChatGPT (OpenAI):** Used as the primary conversational AI assistant for technical learning, conceptual explanations, understanding error messages, troubleshooting code, exploring alternative implementation approaches, and receiving step-by-step guidance.
- **Other Free AI Assistance Tools:** General free web-based AI tools and code completion utilities were occasionally referenced for routine syntax lookups, quick technical explanations, and drafting documentation.

No paid, proprietary enterprise code-generation suites or unconfirmed external models were used.

---

## 3. How AI Was Used

AI assistance was actively integrated into multiple facets of the development lifecycle, supporting both conceptual understanding and hands-on implementation:

- **Understanding Concepts & Technical Architecture:** Clarifying the relationship between continuous power flow (MW) and discrete settlement intervals, understanding pre-auction gate-closure rules to prevent lookahead bias, and designing a clean, decoupled frontend/backend architecture.
- **Investigating Errors & Troubleshooting:** Diagnosing build warnings, package dependency conflicts, TypeScript type mismatches, and PowerShell/shell environment issues.
- **Exploring Implementation Approaches:** Evaluating methods for vectorized metric calculations (MAE, RMSE, Bias, WAPE), handling edge cases such as division-by-zero protection, and designing multi-stage Docker containerization.
- **Guidance on Debugging, Testing & Deployment:** Formulating automated unit and integration tests, configuring CORS middleware for cross-origin deployments, setting up Nginx reverse proxying, and configuring cloud deployment platforms (Vercel and Render).
- **Improving Technical Understanding & Documentation:** Structuring architectural summaries, drafting clear technical explanations for API endpoints, and organizing documentation for maintainability and readability.

AI assistance directly supported the implementation work alongside conceptual exploration, providing code examples, debugging suggestions, and configuration snippets.

---

## 4. My Role in Development

I actively drove the development and delivery of the Gridbricks project from start to finish. My involvement included:

- Directing the overall project roadmap and prioritizing requirements against the challenge specification.
- Engaging with AI tools to ask targeted technical questions, evaluate proposed solutions, and adapt suggestions to the specific needs of the application.
- Applying technical guidance directly to the codebase, participating in the implementation of frontend and backend components, structuring tests, and configuring deployment pipelines.
- Manually testing, running, and verifying the application across local environments, Docker containers, and live cloud deployments on Render and Vercel.
- Taking complete ownership of the final repository, ensuring that all components work together cohesively, and remaining fully responsible for understanding, presenting, and explaining the system's architecture, methodology, and codebase.

AI acted as a supporting development accelerator and learning resource, while I retained responsibility for decision-making, code review, integration, and project delivery.

---

## 5. Model and Version Limitations

ChatGPT was the primary conversational assistant used during development. However, because development occurred interactively across sessions over time, **the exact ChatGPT model/version used during development was not consistently recorded.**

In accordance with strict reporting transparency, no specific historical model version (such as GPT-3.5, GPT-4, or GPT-4o) is claimed here, as session logs did not capture model versions deterministically. Only tools and workflows that can be genuinely confirmed are documented.
