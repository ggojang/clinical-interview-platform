# Safety Escalation Specification

Safety rules have precedence over routine interview completion.

The Version 0.1 repository contains research-only respiratory warning-sign examples. They are not a complete clinical protocol and require expert review before real-world use.

## Runtime behavior

When a safety rule is triggered:

1. record the triggering facts and rule version;
2. avoid minimizing or diagnosing;
3. ask only necessary clarification if delay is acceptable;
4. transition to the configured escalation action;
5. preserve a full trace.

Generated or unreviewed safety rules must not be enabled in production.
