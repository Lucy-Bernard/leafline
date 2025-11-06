"""
SECONDARY ADAPTER: Sandbox Executor Implementation

THIS IS A CRITICAL SECURITY COMPONENT.

Implements safe execution of AI-generated Python code using RestrictedPython.
The Diagnostic Kernel sends AI-generated code to this adapter for execution.

Security Model:
The AI generates code that could potentially be malicious or accidentally harmful.
We use RestrictedPython to create a "jail" that prevents dangerous operations:

1. NO FILE SYSTEM ACCESS: Can't read/write files (no 'open', no 'os' module)
2. NO NETWORK ACCESS: Can't make HTTP requests or socket connections
3. NO IMPORTS: Can't import any modules except explicitly whitelisted ones (only 'json')
4. NO DANGEROUS BUILTINS: Can't use 'eval', 'exec', '__import__', 'compile', etc.
5. LIMITED SCOPE: Can only access the 'params' dict we provide

What the code CAN do:
- Basic Python: if/else, loops, variables, functions
- Math operations: +, -, *, /, etc.
- Dictionary/list operations
- Access the diagnosis_context from params
- Set a 'result' variable with action/payload

Hexagonal Architecture: This is a SECONDARY ADAPTER implementing the
ISandboxExecutor port. The application core depends on the interface,
not on this RestrictedPython implementation.
"""

import json
import logging
import re
from typing import Any

from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import (
    guarded_iter_unpack_sequence,
    guarded_unpack_sequence,
    safer_getattr,
)

from adapter.sandbox_executor import ISandboxExecutor


class SandboxExecutorImpl(ISandboxExecutor):
    """
    Sandbox Executor using RestrictedPython for secure code execution.

    This adapter creates a heavily restricted Python environment where AI-generated
    code can run without access to dangerous operations. It's the security boundary
    that makes the Diagnostic Kernel safe to use with untrusted AI-generated code.
    """

    def __init__(self) -> None:
        self._safe_builtins = self._create_safe_builtins()

    @staticmethod
    def _safe_getitem(obj: Any, key: Any) -> Any:
        """
        Safe dictionary/list access for RestrictedPython.
        Allows code to access diagnosis_context['plant_vitals'] etc.
        """
        return obj[key]

    @staticmethod
    def _safe_write(obj: Any) -> Any:
        """
        Safe variable assignment for RestrictedPython.
        Allows code to set result = {...}
        """
        return obj

    @staticmethod
    def _safe_apply(f: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Safe function calling for RestrictedPython.
        Allows code to call whitelisted functions like len(), dict(), etc.
        """
        return f(*args, **kwargs)

    @staticmethod
    def _safe_iter(obj: Any) -> Any:
        """
        Safe iterator for RestrictedPython.
        Allows code to iterate over lists and other iterables.
        """
        return iter(obj)

    def _create_safe_builtins(self) -> dict[str, Any]:
        """
        Create the restricted builtins dictionary for sandboxed code execution.

        This is the security heart of the sandbox. We explicitly define EVERY
        function and module the AI-generated code can access. Anything not in
        this dictionary is completely unavailable.

        SECURITY PRINCIPLE: Whitelist, never blacklist.
        We don't try to block dangerous functions - we only allow safe ones.

        Allowed Operations:
        - Basic types: str, int, float, bool, list, dict, tuple, set
        - Safe functions: len, min, max, sum, abs, all, any, sorted, range, enumerate, zip
        - JSON module: For parsing diagnosis_context
        - RestrictedPython guards: For safe iteration and attribute access

        Explicitly BLOCKED (not in whitelist):
        - open() - Can't read/write files
        - __import__() - Can't import modules
        - eval()/exec() - Can't execute arbitrary code
        - os module - Can't access operating system
        - sys module - Can't access Python internals
        - subprocess - Can't execute shell commands
        - socket - Can't make network connections
        - Any file I/O, network I/O, or system access

        Returns:
            dict: The safe builtins dictionary for code execution
        """
        safe_builtins: dict[str, Any] = safe_globals.copy()
        safe_builtins["_getiter_"] = self._safe_iter
        safe_builtins["_getattr_"] = safer_getattr
        safe_builtins["_unpack_sequence_"] = guarded_unpack_sequence
        safe_builtins["_iter_unpack_sequence_"] = guarded_iter_unpack_sequence
        safe_builtins["json"] = json
        safe_builtins["_getitem_"] = self._safe_getitem
        safe_builtins["_write_"] = self._safe_write
        safe_builtins["__name__"] = "restricted_module"
        safe_builtins["__metaclass__"] = type
        safe_builtins["_apply_"] = self._safe_apply
        safe_builtins["len"] = len
        safe_builtins["str"] = str
        safe_builtins["int"] = int
        safe_builtins["float"] = float
        safe_builtins["bool"] = bool
        safe_builtins["list"] = list
        safe_builtins["dict"] = dict
        safe_builtins["tuple"] = tuple
        safe_builtins["set"] = set
        safe_builtins["range"] = range
        safe_builtins["enumerate"] = enumerate
        safe_builtins["zip"] = zip
        safe_builtins["min"] = min
        safe_builtins["max"] = max
        safe_builtins["sum"] = sum
        safe_builtins["abs"] = abs
        safe_builtins["all"] = all
        safe_builtins["any"] = any
        safe_builtins["sorted"] = sorted
        return safe_builtins

    @staticmethod
    def _extract_code_from_markdown(code: str) -> str:
        """
        Extract Python code from markdown code blocks.

        AI models sometimes wrap code in markdown:
            ```python
            result = {"action": "ASK_USER", ...}
            ```

        We need to extract just the Python code, removing the ``` markers.

        Args:
            code: Raw AI response that may contain markdown

        Returns:
            str: Pure Python code without markdown formatting
        """
        code = code.strip()
        pattern = r"^```(?:python)?\s*\n(.*?)\n```$"
        match = re.match(pattern, code, re.DOTALL)
        if match:
            return match.group(1).strip()
        return code

    async def execute_code(self, code: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Execute AI-generated Python code in a RestrictedPython sandbox.

        Execution Process:
        1. Extract code from markdown if AI wrapped it in ```
        2. Validate syntax using Python's AST parser
        3. Compile code with RestrictedPython (adds security restrictions)
        4. Create isolated execution environment with only safe builtins
        5. Execute code with diagnosis_context as the only accessible data
        6. Extract and return the 'result' variable set by the code

        Security Layers:
        - RestrictedPython compilation: Blocks dangerous operations at compile time
        - Limited builtins: Code can only call explicitly whitelisted functions
        - Isolated scope: Code can't access server memory, just the params dict
        - Syntax validation: Catches malformed code before execution

        Expected Code Pattern:
            diagnosis_context = params["diagnosis_context"]
            # AI's logic here analyzing the context
            result = {"action": "ASK_USER", "payload": {"question": "..."}}

        Args:
            code: Python code string generated by AI
            params: Dictionary containing {"diagnosis_context": {...}}

        Returns:
            dict: The result dict set by the code with 'action' and 'payload' keys

        Raises:
            ValueError: If code has syntax errors, security violations, or doesn't set result
        """
        try:
            import ast

            logging.info("Received AI-generated code (raw):\n%s", code)

            code = self._extract_code_from_markdown(code)
            logging.info("Extracted code (post-markdown removal):\n%s", code)

            try:
                ast.parse(code)
                logging.info("Syntax validation passed")
            except SyntaxError as syntax_error:
                error_message = (
                    f"AI-generated code has syntax error on line {syntax_error.lineno}: "
                    f"{syntax_error.msg}. Code must be valid Python."
                )
                logging.exception("Syntax validation failed:\n%s", code)
                raise ValueError(error_message) from syntax_error
            # compile the code with RestrictedPython checking for security violations
            compile_result = compile_restricted(
                code,
                filename="<user_code>",
                mode="exec",
            )

            if hasattr(compile_result, "errors") and compile_result.errors:
                error_message = f"Code compilation errors: {compile_result.errors}"
                logging.error("Compilation failed: %s", error_message)
                raise ValueError(error_message)

            compiled_code = (
                compile_result.code
                if hasattr(compile_result, "code")
                else compile_result
            )

            exec_globals: dict[str, Any] = {
                "__builtins__": self._safe_builtins,
                "params": params,
            }
            exec_locals: dict[str, Any] = {}
            # actually runs the already compiled code in the restricted environment
            logging.info("Executing code with params: %s", params)
            exec(compiled_code, exec_globals, exec_locals)  # noqa: S102

            if "result" not in exec_locals:
                error_message = "Code must define a 'result' variable"
                logging.error("Code execution succeeded but no result variable found")
                raise ValueError(error_message)

            logging.info("Code execution successful. Result: %s", exec_locals["result"])
            return exec_locals["result"]

        except Exception as error:
            logging.exception("Failed to execute code:\n%s", code)
            error_message = f"Code execution failed: {error!s}"
            raise ValueError(error_message) from error
