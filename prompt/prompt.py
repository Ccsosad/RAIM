# (1) Architecture-Aware File Localization
feature_report_template = """
The new feature request is as follows:

### New Feature Analysis Report ###
```json
{problem_statement}
```

### Candidate Files ###
{structure}
###
"""

file_system_prompt_overall = """
You are an expert software development assistant. You will be presented with a detailed feature analysis report in JSON format and the project's file structure.
Your task is to analyze the ENTIRE report as a whole to understand the full scope of the feature.

Based on your holistic understanding, identify the TOP 10 MOST IMPORTANT Python source code files (`.py`) that need to be modified to implement this entire feature.
Rank these 10 files from most important to least important.

- Focus exclusively on `.py` source code files.
- Ignore documentation, tests, and configuration files.
- Your goal is to find the most central and critical files for the implementation.
"""

file_summary_overall = """
Based on your analysis, provide a single ranked list of the top 10 file paths.

The output MUST be a list of file paths enclosed in ```, with each file on a new line.
Do not include any other text, explanation, or JSON formatting.

Here is an example of the required output format:
```
path/to/most_important_file.py
path/to/second_most_important.py
path/to/third_most_important.py
```
"""

file_loc_with_graph_system = """You are an expert software engineer. Based on the module call graph and code skeletons provided, please re-analyze and re-rank the relevance of each file to the given problem statement."""

file_loc_with_graph_user = """
The new feature request is as follows:

### New Feature Analysis Report ###
```json
{problem_statement}
```

### Candidate Files ###
{structure}
###

{module_call_graph}

{code_skeletons}

Please re-analyze the files based on the module call graph and code skeletons, and output the top 10 most relevant files in a code block format, one file per line.

Example:
```
file1.py
file2.py
file3.py
```
"""

# (2) Architecture-Aware Iterative Function Localization
initial_func_loc = """
                You are an expert code analyst. Based on the following problem statement and file skeletons, 
                identify the top 3 most relevant functions that are likely to contain the bug or need to be modified.
                
                Problem Statement:
                {problem_statement}
                
                File Skeletons:
                {file_skeletons}
                
                Please provide the complete set of locations as either a class name or a function name.
                The returned items should be separated by new lines, ordered by most to least important, and wrapped with ```.
                The returned items MUST be enclosed in ```...```.
                Since your answer will be processed automatically, please give your answer in the example format as follows.
                ```
                top1_file_fullpath.py
                function: Class1.Function1

                top2_file_fullpath.py
                function: Function2

                top3_file_fullpath.py
                function: Class3.Function3
                ```
                Replace 'top_file_fullpath.py' with the actual file path, 'Class' with the actual class name, and 'Function' with the actual function name.
                For example, 
                ```
                sklearn/linear_model/__init__.py
                function: LinearRegression.fit
                ```
                """
query_gen_prompt = """
            You are an intelligent assistant specializing in software issue localization for new feature additions.
            Your primary goal is to identify up to 10 unique code functions from a given codebase that are most likely to require
            modification to implement a provided software feature.
            
            ### Available Tools
            "name": "search"
            "description": "Searches the codebase for functions relevant to the query. Returns a list of candidate functions found based on the description of the issue passed to the tool."
            "parameters": "issue_description"
            
            "name": "finish"
            "description": "Call this tool when you are confident you have identified all the top relevant functions."
            "parameters": null
            
            ### Helpful Pointers
            1. Use 'search' with complementary angles across rounds.
            2. Prefer high-coverage, low-duplicate results.
            3. After each 'search', explain why each new function is relevant.
            4. Then justify your query reformulation before making the next call.
            5. Use 'finish' when confident.
            
            ### Expected Response Format
            Your response MUST follow this format, and all content MUST be wrapped with special identifiers:
            
            <QUERY_GENERATION_START>
            THOUGHT: Summarize what you just learned from the latest search results. For EACH newly added function, provide a brief relevance explanation describing why it may relate to the issue description.
            
            REFORMULATION: Explain how you will adjust the next search query to improve coverage/diversity and reduce duplicates.
            
            ACTION: {{"name": "...", "arguments": {{ ... }}}}
            <QUERY_GENERATION_END>
            
            Based on the following problem statement and the functions that have been identified, generate a new search query
            to find more relevant functions that might be related to the new feature implementation.
            
            Problem Statement:
            {problem_statement}
            
            Identified Functions:
            {function_contents_text}
            
            Please generate a response following the expected format above, using the search tool to find more relevant functions. Make sure to wrap all content with <QUERY_GENERATION_START> and <QUERY_GENERATION_END>.
            """

rerank_prompt = """
        You are CodeRanker, an intelligent code reviewer that can analyze GitHub issues and rank code functions based on their relevance to containing the faults causing the GitHub issue.
        
        I will provide you with code functions, each indicated by a numerical identifier []. Rank the code functions based on their relevance to containing the faults causing the following GitHub issue: {problem_statement}
        
        ### Code Functions
        {function_contents_text}
        
        ### Response Format
        All the code functions should be included and listed using identifiers, in descending order of relevance. The output format should be [] > [], e.g., [2] > [1]. Only respond with the ranking results, do not give any explanation.
        
        ### Special Identifier Requirements
        Please wrap the final ranking results with the special identifiers <RANKING_START> and </RANKING_END> to facilitate result extraction and parsing.
        For example:
        <RANKING_START>[2] > [1] > [3]</RANKING_END>
        """

# (3) Multi-Design-Based Patch Generation
CONTEXT_SELECTION_PROMPT = """You are an expert software engineer analyzing the impact of a new feature.
Your task is to identify additional critical code context from the direct dependencies of the initially located functions.

**CONTEXT:**
---
**1. Overall Feature Requirement Analysis:**
{analysis_result_json}

**2. Relevant Code Snippets from Initially Located Functions:**
```python
{code_context}
```

**3. Candidate Context Functions (Direct Callers and Callees):**
This is a Call Tree of functions that directly call, or are called by, the core functions. Each has a unique ID.
{call_graph_context}
---

**YOUR TASK:**

1.  Read the **Overall Feature Requirement**.
2.  Review the **Initially Located Core Functions**.
3.  Analyze the **Candidate Context Functions** list.
4.  Must Identify the **TOP 3 most important functions** from the **Call Tree** that you believe are most critical to include as additional context for planning the implementation. Do **NOT** select functions from the "Initially Located Core Functions" list.

Your entire response **MUST BE** a single JSON object with one key: "top_3_additional_qnames". The content of top_3_additional_qnames cannot be empty.

### Example Output Format:
```json
{{
  "top_3_additional_qnames": [
    "path/to/caller.py:caller_function",
    "utils/helpers.py:a_key_utility_function_it_calls",
    "another/file.py:another_important_callee"
  ]
}}
```
"""

DESIGN_PROMPT_TEMPLATE = """You are a Staff Software Engineer, an expert in writing clean, reusable, and maintainable code.
Your task is to devise **{k_plans}** distinct and viable implementation plans for a given software requirement.

**CRITICAL SCOPE AND FILE CONSTRAINTS:**
---
1.  **PYTHON SOURCE CODE ONLY**: All your proposed `CREATE` or `MODIFY` actions **MUST** target Python source code files (files ending with `.py`).
2.  **NO TEST FILES**: You **MUST NOT** propose any changes to test files. Ignore any files located in directories named `test/`, `tests/`, or files starting with `test_`.
3.  **NO DOCUMENTATION/OTHER FILES**: You **MUST NOT** propose changes to documentation (`.md`, `.rst`), configuration, or any other non-`.py` files.
---

**CONTEXT:**
---
**1. Overall Requirement Analysis:**
{analysis_result_json}

**2. Implementation Hints (Augmentations):**
{augmentations_text}

**3. Call Graph & Dependencies of Initially Located Functions:**
{call_graph_context}

**4. Full Code of TOP Most Important Functions/Classes:**
```python
{final_code_context}
```
---

**YOUR TASK:**

Based on ALL the context provided and adhering strictly to the **SCOPE AND FILE CONSTRAINTS**, propose **{k_plans}** different but valid implementation plans.

**Diversity Requirement:**
The plans should explore different architectural approaches if possible (e.g., one plan focused on minimal local changes, another on abstraction/refactoring, another on extending existing patterns). If only one obvious approach exists, provide variations in implementation details (e.g., different helper function names or locations).

**CRITICAL INSTRUCTION FOR CREATE ACTIONS:**
- You should **ONLY** propose a `CREATE` action (for new files, functions, or classes) if the **Implementation Hints (Augmentations)** section explicitly suggests a name for a new entity.
- If hints for new entities are provided, AT LEAST ONE of your plans **MUST** incorporate a `CREATE` action that uses the **exact names** given in the hints.

Your entire response **MUST BE** a single JSON object. Do not include any text or explanation outside of the JSON structure.

The JSON object must have a single root key "plans", which is a list of {k_plans} plan objects. Each plan object must follow this exact schema:
{{
  "plans": [
    {{
      "name": "Plan 1: [Descriptive Title]",
      "strategy": "A brief summary of this plan's strategy, its pros, and its cons.",
      "actions": [
        {{
          "type": "MODIFY",
          "target": "path/to/source_code.py:ClassName.method_name",
          "description": "A detailed, actionable description of the code changes."
        }},
        {{
          "type": "CREATE",
          "target": "path/to/new_utils.py",
          "description": "Create a new function `def new_helper(data): ...` using the exact name from the Implementation Hints."
        }}
      ]
    }},
    ... (Total {k_plans} plans)
  ]
}}
"""

LINE_LOC_FROM_PLAN_PROMPT = """You are an expert software engineer tasked with pinpointing the exact code lines for implementing a pre-approved modification plan.

**CONTEXT:**
---
**1. Overall Feature Requirement Analysis:**
{analysis_result_json}

**2. The Approved Implementation Plan:**
{plan_text}

**3. Code Context for the Plan:**
{code_context}
---

**YOUR TASK:**

Based on the **Approved Implementation Plan**, identify the precise line numbers or code blocks for **EACH ACTION**.

- For **MODIFY** actions on an **existing** function/class, specify the target function/class name and the exact line number(s) or a range (`start-end`) within it that need to be changed.
- For **CREATE** actions in an **existing file**, your goal is to find the best insertion point. To do this, you MUST specify an **EXISTING** function or class as an "anchor" and provide a line number near it. For example, specify the last line of a function if you want to insert new code after it.
- For **CREATE** actions in a **new file** (provided as a skeleton), the location is simply `line: 1`.

Your entire response MUST be wrapped in a single ``` block.

### EXAMPLES of OUTPUT FORMAT ###

**Example 1: Modifying existing functions**
```
src/module1/file1.py
class: RequestHandler
function: handle_new_feature
line: 120

src/module2/utils.py
function: validate_input
line: 45
line: 96
```

**Example 2: Creating a new function in an existing file**
(The plan is to create a new helper function `new_util_func` in `src/module2/utils.py` after `validate_input`)
```
src/module2/utils.py
function: validate_input
line: 105 
```
*(Note: You identified that line 105 is the end of the `validate_input` function, which is the correct place to insert the new code after.)*

**Example 3: Creating a new file**
(The plan is to create a new file `src/module3/new_file.py`)
```
src/module3/new_file.py
line: 1
```

Return only the locations, wrapped in ``` (no extra explanation).
"""

# (4) Impact-Aware Patch Selection
PATCH_EVALUATION_PROMPT = """You are an experienced software engineer responsible for maintaining a GitHub project.
A new feature implementation has been requested.
Engineer A has written a test script designed to verify the new feature.
Engineer B has written a patch to implement the feature.

NOTE: both the test and the patch may be wrong.

--- FEATURE DESCRIPTION ---
{problem_statement}

--- CHANGE IMPACT REPORT (CRITICAL CONSTRAINTS) ---
{impact_report}

--- CANDIDATE PATCH ---
Plan Name: {plan_name}
Patch Content:
```diff
{patch_diff}
```

--- EVALUATION TASK ---
You need to perform a multi-stage evaluation of the candidate patch:

## STAGE 1: REGRESSION TEST ANALYSIS
First, analyze the regression test results to ensure the new feature implementation does not break existing functionality.
- Check if the regression tests pass or fail
- If they fail, determine the root cause: is it due to the patch breaking existing functionality, or is it due to test issues?

## STAGE 2: FEATURE IMPLEMENTATION EVALUATION WITH REPRODUCTION TESTS
Next, evaluate the feature implementation using the reproduction test results:
- Analyze the reproduction test results at a granular level: how many test cases passed vs. failed
- Examine the detailed error information for failed tests
- Distinguish between two scenarios:
  1. **Test Issues**: The test itself is flawed, incorrect, or incompatible with the codebase
  2. **Patch Implementation Issues**: The patch fails to correctly implement the feature as described
- For each failed test, provide a brief analysis of whether it's a test issue or a patch issue
- Consider the pass rate as an indicator of partial feature implementation

## STAGE 3: CODE CHANGE IMPACT ANALYSIS
Finally, evaluate the patch using the code change impact analysis:
- Assess if the patch introduces any breaking changes
- Check if it complies with the critical constraints identified in the impact report
- Evaluate code quality, edge case handling, and overall implementation effectiveness

CRITICAL PRIORITY: NEW FEATURE IMPLEMENTATION ACCURACY IS THE MOST IMPORTANT FACTOR. Only consider other factors when multiple patches have equally accurate implementation logic.

Your task is to:
1. Evaluate the Test Results in detail:
   - Determine whether each test case is valid for verifying the new feature implementation
   - For failed tests, distinguish between test issues and patch implementation issues
   - Calculate an effective pass rate by excluding invalid tests
   - Determine the expected correct behavior based on the feature description

2. Evaluate the Candidate Patch:
   - Compare the patch implementation against the expected correct behavior
   - Double check: refer to the feature description to confirm the feature's implementation
   - Assess if the patch correctly handles all requirements

3. Score the Patch:
   - Assess the patch comprehensively based on the criteria below, with FEATURE IMPLEMENTATION ACCURACY as the FIRST PRIORITY
   - Consider both the regression test results and the reproduction test results
   - Weight the evaluation towards the feature implementation accuracy

--- EVALUATION CRITERIA ---

1. FEATURE IMPLEMENTATION SCORE (0-2) [HIGHEST PRIORITY]:
   - 0: Incorrect: changes do not implement the feature correctly or break existing functionality
   - 1: Partially correct: changes address some cases but are incomplete (passes some reproduction tests)
   - 2: Fully correct: changes completely implement the feature as described (passes most/all reproduction tests)

2. Patch Quality Considerations [SECONDARY]:
   - Effectiveness in implementing the core feature
   - Handling of edge cases
   - Implementation quality and code style
   - Potential regression risks (based on regression test results)
   - Compliance with impact report constraints

3. Detailed Scoring (0-2 for each with clear criteria):
   - relevance: How well does it implement the core feature described? [HIGH PRIORITY]
     * 0: Does not implement the feature at all
     * 1: Partially implements the feature, missing key aspects
     * 2: Fully implements the feature as described
   - syntax: Is the code valid and well-formed?
     * 0: Contains syntax errors that prevent execution
     * 1: Valid syntax but with minor issues like unused variables
     * 2: Valid, clean, and well-structured code
   - upstream_safety: Does it violate any breaking changes or risks? [LOWER PRIORITY]
     * 0: Introduces critical breaking changes for upstream code
     * 1: Introduces minor compatibility issues
     * 2: No breaking changes, safe for all upstream callers
   - downstream_correctness: Does it use downstream APIs correctly? [LOWER PRIORITY]
     * 0: Incorrect API usage that will cause failures
     * 1: API usage with potential edge case issues
     * 2: Correct and safe API usage following best practices
   - regression_safety: Does it maintain compatibility with existing functionality? (based on regression test results) [LOWER PRIORITY]
     * 0: Breaks existing functionality in significant ways
     * 1: May affect some edge cases or non-critical functionality
     * 2: Maintains full compatibility with all existing functionality

--- OUTPUT FORMAT ---
Return a strictly valid JSON object:
{{
    "scores": {{
        "relevance": (0-2),
        "syntax": (0-2),
        "upstream_safety": (0-2),
        "downstream_correctness": (0-2),
        "regression_safety": (0-2),
        "feature_implementation_score": (0-2)
    }},
    "is_valid_patch": boolean,
    "critical_issues": ["List specific flaws found"],
    "reasoning": "Detailed analysis including multi-stage evaluation results.",
    "test_validity": "valid" or "invalid",
    "expected_behavior": "Describe the expected correct behavior based on the feature description.",
    "test_analysis": {{
        "total_reproduction_tests": (number),
        "passed_reproduction_tests": (number),
        "failed_reproduction_tests": (number),
        "effective_pass_rate": (float, 0.0-1.0),
        "test_issues": ["List test cases that are problematic"],
        "patch_issues": ["List patch implementation issues identified from tests"]
    }}
}}
"""

PATCH_SELECTION_PROMPT = """You are an experienced software engineer responsible for maintaining a GitHub project.
A new feature implementation has been requested.
Engineer A has written a test script designed to verify the new feature.
Engineer B has proposed several candidate patches to implement the feature.

Your task is to evaluate the candidate patches and select the best one based on a multi-stage evaluation process.

NOTE: both the test and candidate patches may be wrong.

--- FEATURE ---
{problem_statement}

--- CANDIDATES ---
{candidates_analysis}

--- INSTRUCTIONS ---
Since both the test and candidate patches may be wrong, you must comprehensively analyze all patches - do not judge patches solely based on test execution results.

CRITICAL PRIORITY: NEW FEATURE IMPLEMENTATION LOGIC ACCURACY IS THE MOST IMPORTANT FACTOR. Only consider code change impact analysis when multiple patches have equally accurate implementation logic.

You need to perform a multi-stage selection process:

## STAGE 1: REGRESSION TEST SCREENING
First, screen out patches that severely break existing functionality:
- Check regression test results for each patch
- Patches that fail most or all regression tests should be deprioritized
- Consider the root cause of regression failures: is it due to the patch or test issues?

## STAGE 2: FEATURE IMPLEMENTATION ASSESSMENT
Next, evaluate the feature implementation accuracy using reproduction test results:
- Analyze the reproduction test results at a granular level (pass rates, detailed errors)
- Distinguish between test issues and patch implementation issues
- Consider the effective pass rate after excluding invalid tests
- Score each patch's feature implementation accuracy (0-2)

## STAGE 3: CODE QUALITY AND IMPACT ANALYSIS
Finally, when multiple patches have similar feature implementation scores, evaluate them based on:
- Code change impact analysis results
- Compliance with critical constraints
- Code quality and implementation effectiveness
- Edge case handling
- Potential long-term maintainability

Your task is to:
1. Evaluate each candidate patch against the feature description
2. Consider the detailed test results, including pass rates and error analysis
3. Distinguish between test issues and patch implementation issues
4. Compare the patches against each other, prioritizing feature implementation accuracy
5. Select the best patch based on the criteria below

--- SELECTION CRITERIA ---

1. FEATURE IMPLEMENTATION SCORE (0-2) [HIGHEST PRIORITY]:
   - 0: Incorrect: changes do not implement the feature correctly or break existing functionality
   - 1: Partially correct: changes address some cases but are incomplete (passes some reproduction tests)
   - 2: Fully correct: changes completely implement the feature as described (passes most/all reproduction tests)

2. Patch Quality Considerations [ONLY CONSIDER WHEN MULTIPLE PATCHES HAVE SAME FEATURE IMPLEMENTATION SCORE]:
   - Effectiveness in implementing the core feature
   - Handling of edge cases
   - Implementation quality and code style
   - Potential regression risks (based on regression test results)
   - Compliance with impact report constraints
   - Test results and their validity, including detailed pass rates and error analysis

--- OUTPUT FORMAT ---
Return a strictly valid JSON object with the following format:
{{
    "selected_plan_index": int,  # Zero-based index of the best patch
    "selection_reason": "Detailed analysis of why this patch was selected, including multi-stage evaluation results",
    "patch_scores": [
        {{"index": 0, "feature_implementation_score": 2, "reasoning": "Analysis of patch 0, including test pass rates and implementation quality"}},
        {{"index": 1, "feature_implementation_score": 1, "reasoning": "Analysis of patch 1, including test pass rates and implementation quality"}},
        ...
    ]
}}

The selected_plan_index should be the index of the patch with the highest feature_implementation_score. Only when multiple patches have the same feature_implementation_score, consider other factors like code change impact, test pass rates, and implementation quality.
"""
