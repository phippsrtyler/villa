"""Run linker binding proof unconditionally before the pinned pair runner."""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load pinned module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--runner", required=True)
    p.add_argument("--resolution-check", required=True)
    p.add_argument("--library-sha256", required=True)
    p.add_argument("--renderer-sha256", required=True)
    args = p.parse_args()
    cfg_path = pathlib.Path(args.config).resolve(strict=True)
    manifest = json.loads(cfg_path.read_text(encoding="utf-8"))
    runner_path = pathlib.Path(args.runner).resolve(strict=True)
    resolver_path = pathlib.Path(args.resolution_check).resolve(strict=True)
    if manifest.get("schema") != "selected-read-final-source-cpu-sequence-v1":
        raise ValueError("unexpected sequence manifest schema")
    cfgs = [json.loads(pathlib.Path(p).resolve(strict=True).read_text(encoding="utf-8"))
            for p in manifest["configs"]]
    if len(cfgs) != 3:
        raise ValueError("the fixed CPU protocol requires exactly three paired repetitions")
    expected_orders = [["baseline", "candidate"], ["candidate", "baseline"], ["baseline", "candidate"]]
    if [cfg["order"] for cfg in cfgs] != expected_orders:
        raise ValueError("repetition order differs from the frozen AB/BA/AB protocol")
    contracts = [json.loads(pathlib.Path(c["contract"]).read_text(encoding="utf-8"))
                 for cfg in cfgs for c in cfg["crops"]]
    binaries = {pathlib.Path(c["binary"]).resolve(strict=True) for c in contracts}
    renderer_hashes = {c["binary_sha256"] for c in contracts}
    if len(binaries) != 1:
        raise ValueError("all fixed crop contracts must use one pinned renderer binary")
    if len(renderer_hashes) != 1:
        raise ValueError("crop contracts disagree on renderer binary hash")
    if next(iter(renderer_hashes)) != args.renderer_sha256:
        raise ValueError("renderer binary hash differs from the launch contract pin")
    libraries = {(cfg["candidate_library"], cfg["candidate_library_path"],
                  cfg["pins"][cfg["candidate_library"]]) for cfg in cfgs}
    if len(libraries) != 1 or next(iter(libraries))[2] != args.library_sha256:
        raise ValueError("all repetitions must use the same pinned candidate library and loader path")
    root = pathlib.Path(manifest["output_root"]).resolve(strict=True)
    proof = root / "linker-resolution.json"
    science_root = root / "science"
    if proof.exists():
        raise FileExistsError(f"linker proof path must be fresh: {proof}")
    if science_root.exists():
        raise FileExistsError(f"paired output parent must be fresh: {science_root}")
    resolver = load_module("selected_read_library_resolution_preflight", resolver_path)
    # This uses the same candidate search-path string that the generated
    # candidate producer passes as LD_LIBRARY_PATH to the renderer.
    library, search_path, _ = next(iter(libraries))
    resolver.verify(str(next(iter(binaries))), library, args.library_sha256, search_path, str(proof),
                    next(iter(renderer_hashes)))
    runner_dir = str(runner_path.parent)
    if runner_dir not in sys.path:
        sys.path.insert(0, runner_dir)
    runner = load_module("selected_read_paired_runner", runner_path)
    # Validate every config and source pin before the first timed arm.
    for cfg in cfgs:
        runner.preflight(cfg)
        if pathlib.Path(cfg["output"]).exists():
            raise FileExistsError(f"paired output must be fresh: {cfg['output']}")
    # Queue pre-creates only the descriptor output root. The reviewed runner
    # mkdirs each config.output without parents=True, so create this one
    # dedicated parent exactly once after all non-timing preflights.
    science_root.mkdir()
    pairs = [runner.execute(cfg) for cfg in cfgs]
    summary = {"status": "ALL_THREE_PAIRED_REPETITIONS_EXACT", "sequence_schema": manifest["schema"],
               "linker_proof": str(proof), "repetitions": pairs}
    (root / "cpu-paired-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

