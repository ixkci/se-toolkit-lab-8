---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Tool Strategy

CRITICAL RULES:
1. If the user asks for scores without specifying a lab, you MUST call `lms_labs` first.
2. After getting the labs, you MUST NOT print them as a text list.
3. You MUST call the `mcp_webchat_ui_message` tool to display the labs as buttons. Format the payload exactly like this:
{
  "type": "choice",
  "text": "Which lab would you like to see scores for?",
  "options": [
    {"value": "lab-01", "label": "Lab 01"},
    {"value": "lab-02", "label": "Lab 02"}
  ]
}
