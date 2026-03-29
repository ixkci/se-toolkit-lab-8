---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Tool Strategy

CRITICAL RULES FOR USING LMS TOOLS:

1. If the user asks for scores, pass rates, completion, groups, timeline, or top learners WITHOUT explicitly naming a specific lab (e.g. "Lab 01"), you MUST ONLY call `lms_labs` to get the list of labs. 
2. DO NOT call any other tool (like `lms_pass_rates` or `lms_completion_rate`) after calling `lms_labs` if the lab was not specified initially.
3. STOP execution immediately after `lms_labs` and ASK the user which specific lab they want to see.
4. NEVER loop through multiple labs to build a summary table unless explicitly asked to do so.
5. Use each lab title as the default user-facing label. Let the shared `structured-ui` skill decide how to present that choice.
