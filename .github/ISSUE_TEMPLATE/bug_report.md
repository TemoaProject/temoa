---
name: Bug report
about: Report a reproducible bug or unexpected behavior.
title: "[Bug]: Clear and concise description of the bug"
labels: bug, needs-triage
assignees: ''

---

## Bug Description

Clearly and concisely describe the bug you've encountered. What is the unexpected behavior? What did you expect to happen instead?

## Steps to Reproduce

Provide a clear, step-by-step procedure to reproduce the bug. This is crucial for us to understand and fix the issue.

1.  Go to '...'
2.  Click on '....'
3.  Scroll down to '....'
4.  See error '....'

## Code or Configuration Example

If the bug involves code or configuration, please provide a minimal, reproducible example that demonstrates the issue. This should be the smallest amount of code/config necessary to trigger the bug.

```python
# Example of bug-inducing code (if relevant)
import my_library

# Setup or initialization
config = {
    "setting_a": "value",
    "setting_b": 123
}
processor = my_library.Processor(**config)

# Action that triggers the bug
try:
    processor.process_data(invalid_data)
except Exception as e:
    print(f"Error: {e}")
```

## Error Message / Stack Trace

If an error message or stack trace was produced, please include it here. Use code blocks for better readability.

```text
# Example Error Message/Stack Trace
Traceback (most recent call last):
  File "<stdin>", line 7, in <module>
    processor.process_data(invalid_data)
  File "/path/to/my_library/processor.py", line 42, in process_data
    raise ValueError("Invalid data provided")
ValueError: Invalid data provided
```

## Screenshots / Videos

If applicable, add screenshots to help explain the problem. You can drag and drop images directly into the issue description.

## Expected Behavior

Describe what you expected to happen when following the reproduction steps.

## Actual Behavior

Describe what actually happened, including any unexpected output or results.

## Environment

Please provide details about your environment. This helps us reproduce the issue.

*   **Operating System:**
*   **Python Version:**
*   **Project Version:**
*   **Relevant Dependencies:** 

## Checklist

*   [ ] I have searched existing issues to ensure this bug hasn't already been reported.
*   [ ] I have provided clear steps to reproduce the bug.
*   [ ] I have provided a minimal, reproducible code example (if applicable).
*   [ ] I have included any relevant error messages or stack traces.
*   [ ] I have described the expected and actual behavior.
