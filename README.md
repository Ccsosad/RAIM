# RAIM: Repository-level Architecture-aware Feature Implementation via Multi-design

This repository contains the supplementary data, analysis scripts, and prompt details for the paper **"RAIM: Repository-level Architecture-aware Feature Implementation via Multi-design"**.

## File Structure

The directory structure of the uploaded data is organized as follows:

```text
.
├── evaluation
│   └── nocode-bench-verified
│       ├── RQ1  <-- Evaluation results of RAIM using different LLMs
│       ├── RQ2  <-- Scripts for Cross-File Modification Performance Analysis
│       ├── RQ3  <-- Results of the ablation study
│       ├── RQ4  <-- Experimental results on Multi-Design and Selection Strategies
│       └── RQ5  <-- Scripts for analyzing failure type distributions
└── prompt
    └── prompt.py  <-- Key prompts of the RAIM framework
```

## Data Description

**1. Evaluation Data and Scripts**
The directory `./evaluation/nocode-bench-verified/` contains the experimental results and analysis scripts corresponding to the research questions (RQs) discussed in the paper:

*   **RQ1**: This folder stores the evaluation results of the RAIM framework on the *NoCode-bench Verified* dataset across different Large Language Models (LLMs).
*   **RQ2**: This folder contains scripts used to analyze the performance of the RAIM framework regarding **Cross-File Modification**. It evaluates the system's capability in handling both single-file and cross-file edits.
*   **RQ3**: This folder holds the data and results from our **Ablation Study**, demonstrating the contribution of individual components within the framework.
*   **RQ4**: This folder contains experimental results verifying the **Effectiveness of Multi-Design and Selection Strategies**, highlighting how these mechanisms improve patch quality.
*   **RQ5**: This folder contains scripts for comparing **Failure Type Distributions**. It analyzes and categorizes the errors made by RAIM versus baseline methods across different LLMs.

**2. Framework Prompts**
The file `./prompt/prompt.py` contains the critical prompt templates designed for the RAIM framework. It explicitly details the instructions provided to the LLM during the four key stages of our approach:
1.  **Architecture-Aware File Localization**
2.  **Architecture-Aware Iterative Function Localization**
3.  **Multi-Design-Based Patch Generation**
4.  **Impact-Aware Patch Selection**