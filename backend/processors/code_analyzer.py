"""
Code static analysis for bug detection.
Extracts AST patterns and matches against known bug patterns.
"""

import ast
import re
from typing import Any
from dataclasses import dataclass
from enum import Enum


class BugType(Enum):
    OFF_BY_ONE = "OFF_BY_ONE"
    NULL_DEREF = "NULL_DEREF"
    SILENT_EXCEPT = "SILENT_EXCEPT"
    WRONG_COMPARISON = "WRONG_COMPARISON"
    MUTATING_DEFAULT = "MUTATING_DEFAULT"
    UNCLOSED_RESOURCE = "UNCLOSED_RESOURCE"
    RACE_CONDITION = "RACE_CONDITION"
    INTEGER_OVERFLOW = "INTEGER_OVERFLOW"
    SQL_INJECTION = "SQL_INJECTION"
    AUTH_BYPASS = "AUTH_BYPASS"
    DEAD_BRANCH = "DEAD_BRANCH"
    INFINITE_LOOP = "INFINITE_LOOP"


@dataclass
class BugFlag:
    bug_type: BugType
    line_number: int
    code_fragment: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str


class CodeAnalyzer:
    """Static code analyzer for common bug patterns."""

    def __init__(self, code: str, language: str = "python"):
        self.code = code
        self.language = language
        self.lines = code.split('\n')
        self.flags: list[BugFlag] = []
        
    def analyze(self) -> list[BugFlag]:
        """Run all analysis patterns and return flags."""
        if self.language == "python":
            self._analyze_python()
        elif self.language in ["javascript", "js"]:
            self._analyze_javascript()
        else:
            # Fall back to pattern matching for unknown languages
            self._analyze_generic()
        
        return sorted(self.flags, key=lambda f: f.line_number)

    def _analyze_python(self):
        """Analyze Python code for bugs."""
        try:
            tree = ast.parse(self.code)
        except SyntaxError:
            return

        visitor = PythonBugVisitor(self.code, self.lines)
        visitor.visit(tree)
        self.flags.extend(visitor.flags)

    def _analyze_javascript(self):
        """Analyze JavaScript code for bugs."""
        # Pattern-based analysis for JS
        self._check_js_patterns()

    def _analyze_generic(self):
        """Generic pattern-based analysis."""
        self._check_generic_patterns()

    def _check_js_patterns(self):
        """Check JavaScript-specific patterns."""
        # Off-by-one in loops
        loop_pattern = r'for\s*\(\s*\w+\s*=\s*0;\s*\w+\s*[<|<=]\s*\w+\.(length|size);'
        for match in re.finditer(loop_pattern, self.code):
            line_num = self.code[:match.start()].count('\n') + 1
            self.flags.append(BugFlag(
                bug_type=BugType.OFF_BY_ONE,
                line_number=line_num,
                code_fragment=self._get_fragment(line_num),
                severity="MEDIUM",
                description="Potential off-by-one error in loop bounds"
            ))

    def _check_generic_patterns(self):
        """Generic pattern checks for any language."""
        # Look for common patterns regardless of language
        pass

    def _get_fragment(self, line_num: int, context_lines: int = 2) -> str:
        """Get code fragment around a line."""
        start = max(0, line_num - 1 - context_lines)
        end = min(len(self.lines), line_num + context_lines)
        return '\n'.join(self.lines[start:end])


class PythonBugVisitor(ast.NodeVisitor):
    """AST visitor to detect Python-specific bugs."""

    def __init__(self, code: str, lines: list[str]):
        self.code = code
        self.lines = lines
        self.flags: list[BugFlag] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Check function definitions for issues."""
        # Check for mutable defaults
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.flags.append(BugFlag(
                    bug_type=BugType.MUTATING_DEFAULT,
                    line_number=node.lineno,
                    code_fragment=self._get_fragment(node.lineno),
                    severity="HIGH",
                    description="Function has mutable default argument - will persist across calls"
                ))
        self._check_auth_bypass(node)
        self._check_null_deref(node)
        self._check_unclosed_resource(node)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """Check for bare/silent exception handling."""
        # Check if handler is empty or just passes
        if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
            # Bare except without type is worse
            if node.type is None:
                self.flags.append(BugFlag(
                    bug_type=BugType.SILENT_EXCEPT,
                    line_number=node.lineno,
                    code_fragment=self._get_fragment(node.lineno),
                    severity="CRITICAL",
                    description="Silent exception handler - errors will be hidden"
                ))
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare):
        """Check for problematic comparisons."""
        # Check for 'is' with mutable values
        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(op, ast.Is):
                # Comparing with mutable objects using 'is' is wrong
                if isinstance(comparator, (ast.List, ast.Dict)):
                    self.flags.append(BugFlag(
                        bug_type=BugType.WRONG_COMPARISON,
                        line_number=node.lineno,
                        code_fragment=self._get_fragment(node.lineno),
                        severity="MEDIUM",
                        description="Using 'is' to compare with mutable value - should use '=='"
                    ))
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        """Check loops for issues."""
        # Check for infinite loops (no state changes)
        self._check_infinite_loop(node)
        self.generic_visit(node)

    def visit_With(self, node: ast.With):
        """Check resource management."""
        # This is good - resources are being managed
        self.generic_visit(node)

    def _check_infinite_loop(self, node: ast.For):
        """Heuristic check for infinite loops."""
        # Very basic check - if loop variable never changes condition
        pass

    def _check_auth_bypass(self, fn_node: ast.FunctionDef):
        """Detect obvious auth bypass patterns like `x or True`."""
        for node in ast.walk(fn_node):
            if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
                if any(isinstance(v, ast.Constant) and v.value is True for v in node.values):
                    self.flags.append(BugFlag(
                        bug_type=BugType.AUTH_BYPASS,
                        line_number=node.lineno,
                        code_fragment=self._get_fragment(node.lineno),
                        severity="CRITICAL",
                        description="Authentication check short-circuits to True"
                    ))

    def _check_null_deref(self, fn_node: ast.FunctionDef):
        """Detect use of maybe-None variables without a nearby guard."""
        assigned_from_call: dict[str, int] = {}
        guarded_names: set[str] = set()
        nullable_call_markers = ("get", "fetch", "find", "load", "query", "lookup")

        for node in ast.walk(fn_node):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                callee_name = None
                if isinstance(node.value.func, ast.Name):
                    callee_name = node.value.func.id.lower()
                elif isinstance(node.value.func, ast.Attribute):
                    callee_name = node.value.func.attr.lower()
                for target in node.targets:
                    if isinstance(target, ast.Name) and callee_name and any(m in callee_name for m in nullable_call_markers):
                        assigned_from_call[target.id] = node.lineno
            if isinstance(node, ast.If):
                test = node.test
                if isinstance(test, ast.Name):
                    guarded_names.add(test.id)
                if isinstance(test, ast.Compare):
                    for expr in [test.left, *test.comparators]:
                        if isinstance(expr, ast.Name):
                            guarded_names.add(expr.id)

        for node in ast.walk(fn_node):
            if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
                name = node.value.id
                if name in assigned_from_call and name not in guarded_names:
                    self.flags.append(BugFlag(
                        bug_type=BugType.NULL_DEREF,
                        line_number=node.lineno,
                        code_fragment=self._get_fragment(node.lineno),
                        severity="HIGH",
                        description=f"Possible null dereference on `{name}` without a guard"
                    ))
                    return
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                name = node.value.id
                if name in assigned_from_call and name not in guarded_names:
                    self.flags.append(BugFlag(
                        bug_type=BugType.NULL_DEREF,
                        line_number=node.lineno,
                        code_fragment=self._get_fragment(node.lineno),
                        severity="HIGH",
                        description=f"Possible null dereference on `{name}` without a guard"
                    ))
                    return

    def _check_unclosed_resource(self, fn_node: ast.FunctionDef):
        """Detect file handles opened with open() but never closed."""
        opened_vars: dict[str, int] = {}
        closed_vars: set[str] = set()

        for node in ast.walk(fn_node):
            if isinstance(node, ast.With):
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call) and isinstance(item.context_expr.func, ast.Name):
                        if item.context_expr.func.id == "open":
                            if isinstance(item.optional_vars, ast.Name):
                                closed_vars.add(item.optional_vars.id)

            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Name) and node.value.func.id == "open":
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            opened_vars[target.id] = node.lineno

            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "close" and isinstance(node.func.value, ast.Name):
                    closed_vars.add(node.func.value.id)

        for var_name, line in opened_vars.items():
            if var_name not in closed_vars:
                self.flags.append(BugFlag(
                    bug_type=BugType.UNCLOSED_RESOURCE,
                    line_number=line,
                    code_fragment=self._get_fragment(line),
                    severity="HIGH",
                    description=f"Resource `{var_name}` opened without a close() call"
                ))

    def _get_fragment(self, line_num: int, context_lines: int = 2) -> str:
        """Get code fragment around a line."""
        start = max(0, line_num - 1 - context_lines)
        end = min(len(self.lines), line_num + context_lines)
        return '\n'.join(self.lines[start:end])


def validate_bug_description(description: str, bug_type: BugType) -> bool:
    """Validate that a bug description is specific and not generic."""
    # Check criteria:
    # - Under 20 words
    # - Starts with a verb
    # - Not too generic
    
    words = description.split()
    if len(words) > 20:
        return False
    
    # Starts with verb
    verbs = ['breaks', 'fails', 'crashes', 'returns', 'throws', 'causes', 'allows', 'loses']
    if not any(description.lower().startswith(v) for v in verbs):
        return False
    
    # Check for generic phrases
    generic_phrases = ['error', 'problem', 'issue', 'needs', 'should']
    phrase_count = sum(1 for phrase in generic_phrases if phrase in description.lower())
    if phrase_count > 2:
        return False
    
    return True
