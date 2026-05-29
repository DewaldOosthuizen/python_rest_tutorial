# Spec Approved

Approved at: 2026-05-29T13:31:30.950072+00:00

## Reviewer verdict

APPROVED
Reason: The proposal accurately describes all three defects visible in the live source. Register.post() (lines 66-69), Retrieve.post() (lines 100-104), and Save.post() (lines 135-140) all use bracket-access on the raw get_json() result with no None guard, exactly as stated. The module-level constants invalid_user_json and invalid_password_json are returned without an HTTP status tuple, confirming the HTTP 200 bleed-through on error paths. The status 303 in Save.post() at lines 152-156 is present and correctly flagged. The proposed fix pattern — None guard first, .get() extraction, field presence check, then auth checks, with explicit HTTP status tuples on every return — is technically correct, follows Flask idioms, and maps cleanly to each task in the task list. Collapsing user-not-found and wrong-password into a single "Invalid credentials" 401 is the right security posture to prevent user enumeration. Tasks are atomic, independently implementable, and stay within the issue scope. No scope creep, no architectural overreach.
