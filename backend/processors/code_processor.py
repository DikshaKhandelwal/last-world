from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass
class CodeFlag:
    flag_type: str
    line_number: int
    fragment: str


def _line_fragment(lines: list[str], index: int, span: int = 1) -> str:
    start = max(0, index - span)
    end = min(len(lines), index + span + 1)
    return '\n'.join(lines[start:end]).strip()


def _find_mutating_default(line: str) -> bool:
    return bool(re.search(r'def\s+\w+\(.*=\s*(\[\]|\{\}|set\(\))', line))


def _find_auth_bypass(line: str) -> bool:
    return 'or True' in line.replace(' ', '')


def _find_wrong_comparison(line: str) -> bool:
    return '== None' in line or '!= None' in line


def _find_open_resource(line: str) -> bool:
    return 'open(' in line and 'with ' not in line


def _find_infinite_loop(line: str) -> bool:
    return bool(re.search(r'\bwhile\s+True\b', line))


def _find_dead_branch(line: str) -> bool:
    return line.strip().startswith(('return', 'raise'))


def detect_code_flags(code: str, max_flags: int = 5) -> list[CodeFlag]:
    lines = code.splitlines()
    flags: list[CodeFlag] = []

    for idx, line in enumerate(lines, start=1):
        if _find_mutating_default(line):
            flags.append(CodeFlag('MUTATING_DEFAULT', idx, _line_fragment(lines, idx - 1)))
        if _find_auth_bypass(line):
            flags.append(CodeFlag('AUTH_BYPASS', idx, _line_fragment(lines, idx - 1)))
        if _find_wrong_comparison(line):
            flags.append(CodeFlag('WRONG_COMPARISON', idx, _line_fragment(lines, idx - 1)))
        if _find_open_resource(line):
            flags.append(CodeFlag('UNCLOSED_RESOURCE', idx, _line_fragment(lines, idx - 1)))
        if _find_infinite_loop(line):
            flags.append(CodeFlag('INFINITE_LOOP', idx, _line_fragment(lines, idx - 1)))
        if _find_dead_branch(line):
            next_line = lines[idx] if idx < len(lines) else ''
            if next_line.strip():
                flags.append(CodeFlag('DEAD_BRANCH', idx, _line_fragment(lines, idx - 1)))

        if len(flags) >= max_flags:
            break

    return flags


def pick_verification_line(flags: Iterable[CodeFlag]) -> str:
    first = next(iter(flags), None)
    if not first:
        return 'No flags detected. Provide a longer or more complex snippet.'
    return f'Check line {first.line_number} of your code. The condition described appears there.'
