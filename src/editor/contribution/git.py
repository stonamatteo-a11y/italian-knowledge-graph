"""Read-only Git repository inspection."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

READ_ONLY_COMMANDS = {
    ("rev-parse", "--is-inside-work-tree"),
    ("diff", "--name-only", "HEAD"),
    ("ls-files", "--others", "--exclude-standard"),
}


@dataclass(frozen=True, slots=True)
class GitState:
    available: bool
    dirty_paths: tuple[str, ...]


class GitInspector:
    def __init__(self, root: Path) -> None:
        self.root = root

    def _run(self, arguments: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        if arguments not in READ_ONLY_COMMANDS:
            raise ValueError(f"Git command is not allowed: {arguments}")
        return subprocess.run(
            ("git", *arguments),
            cwd=self.root,
            capture_output=True,
            check=False,
            text=True,
            encoding="utf-8",
            timeout=10,
        )

    def inspect(self) -> GitState:
        repository = self._run(("rev-parse", "--is-inside-work-tree"))
        if repository.returncode != 0 or repository.stdout.strip() != "true":
            return GitState(False, ())
        tracked = self._run(("diff", "--name-only", "HEAD"))
        untracked = self._run(("ls-files", "--others", "--exclude-standard"))
        dirty = {
            path.strip().replace("\\", "/")
            for output in (tracked.stdout, untracked.stdout)
            for path in output.splitlines()
            if path.strip()
        }
        return GitState(True, tuple(sorted(dirty)))
