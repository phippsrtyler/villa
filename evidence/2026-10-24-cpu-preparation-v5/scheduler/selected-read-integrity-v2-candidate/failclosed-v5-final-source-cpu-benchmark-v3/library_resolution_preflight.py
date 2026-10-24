"""Fail-closed ELF resolution check, run before (and outside) timed arms."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify(binary: str, library: str, expected_sha256: str, search_path: str, out: str,
           expected_renderer_sha256: str) -> dict:
    exe = pathlib.Path(binary).resolve(strict=True)
    lib = pathlib.Path(library).resolve(strict=True)
    if not exe.is_file() or not lib.is_file():
        raise ValueError("renderer and candidate library must be regular files")
    actual_renderer_sha256 = sha(exe)
    if actual_renderer_sha256 != expected_renderer_sha256:
        raise ValueError(f"renderer binary hash differs from frozen crop-contract pin: expected={expected_renderer_sha256} actual={actual_renderer_sha256}")
    if sha(lib) != expected_sha256:
        raise ValueError("candidate library hash differs from frozen pin")
    dirs = [pathlib.Path(p).resolve(strict=True) for p in search_path.split(":") if p]
    if not dirs or dirs[0] != lib.parent:
        raise ValueError("candidate library directory must be first in loader search path")
    env = dict(os.environ, LD_LIBRARY_PATH=search_path)
    proc = subprocess.run(["ldd", str(exe)], env=env, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"ldd failed ({proc.returncode}): {proc.stdout[-4000:]}")
    matches = []
    for line in proc.stdout.splitlines():
        m = re.match(r"\s*libutils\.so\s+=>\s+(\S+)", line)
        if m:
            matches.append(pathlib.Path(m.group(1)).resolve(strict=True))
    if len(matches) != 1 or matches[0] != lib:
        raise ValueError(f"libutils.so must resolve exactly once to {lib}; got {matches}; ldd={proc.stdout}")
    receipt = {"status": "PASS_LINKER_RESOLUTION", "renderer": str(exe),
               "renderer_sha256": actual_renderer_sha256, "resolved_library": str(matches[0]),
               "library_sha256": sha(matches[0]), "search_path": search_path,
               "ldd_stdout": proc.stdout}
    pathlib.Path(out).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--renderer", required=True)
    p.add_argument("--library", required=True)
    p.add_argument("--sha256", required=True)
    p.add_argument("--search-path", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--renderer-sha256", required=True)
    args = p.parse_args()
    print(json.dumps(verify(args.renderer, args.library, args.sha256, args.search_path, args.output,
                           args.renderer_sha256), indent=2))
