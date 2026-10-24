"""Generate one launch-disabled descriptor holding the full AB/BA/AB sequence."""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


prior = json.loads((HERE / "prior-descriptor.json").read_text(encoding="utf-8"))
old_cfg = json.loads((HERE / "prior-config.json").read_text(encoding="utf-8"))
packet = json.loads((HERE / "benchmark-packet-v2.json").read_text(encoding="utf-8"))
resolver_sha = sha(HERE / "library_resolution_preflight.py")
wrapper_sha = sha(HERE / "run_pinned_paired_benchmark.py")
paired_runner_sha = sha(HERE / "paired_preparation_runner_v5.py")
helper_qualify_sha = sha(HERE / "qualify_render.py")
helper_audit_sha = sha(HERE / "audit_qualification_ledger.py")
qualified_producer = "/archive/selected-read-v5-optin-integration-qualification-v2-source/producer.py"
qualified_audit = "/archive/selected-read-v5-optin-integration-qualification-v2-source/audit_qualification_ledger.py"
qualified_identity = "/archive/selected-read-v5-optin-integration-qualification-v2-source/requested_crop_identity_v1.py"
qualified_stock = "/archive/selected-read-paired-preparation-v1-source/stock_finite_producer.py"
qualified_producer_sha = packet["source_correspondence"]["qualified_candidate_producer_sha256"]
qualified_audit_sha = packet["source_correspondence"]["qualified_audit_module_sha256"]
qualified_identity_sha = packet["source_correspondence"]["qualified_crop_identity_module_sha256"]
qualified_stock_sha = packet["source_correspondence"]["qualified_stock_producer_sha256"]
lib_sha = packet["source_correspondence"]["candidate_library_sha256"]
lib_cont = "/archive/selected-read-upstream-failclosed-v5-cpu-qualification/libutils.so"
lib_host = "/mnt/oldpc/vesuvius_park/selected-read-upstream-failclosed-v5-cpu-qualification/libutils.so"
remote_helper = "/work/takeover/scheduler/failclosed-v5-final-source-cpu-benchmark-v3-final"
host_helper = "/mnt/scrolls/vesuvius/takeover/scheduler/failclosed-v5-final-source-cpu-benchmark-v3-final"
runner_cont = remote_helper
runner_host = host_helper
new_src = "/archive/selected-read-failclosed-v5-final-source-cpu-benchmark-v3-final"
host_new_src = "/mnt/oldpc/vesuvius_park/selected-read-failclosed-v5-final-source-cpu-benchmark-v3-final"
jid = "selected-read-final-source-v5-cpu-preparation-v3"
root_host = "/mnt/oldpc/vesuvius_park/" + jid
root_cont = "/archive/" + jid

orders = [["baseline", "candidate"], ["candidate", "baseline"], ["baseline", "candidate"]]
cfg_paths = []
for i, order in enumerate(orders, 1):
    cfg = copy.deepcopy(old_cfg)
    cfg["output"] = f"{root_cont}/science/r{i}"
    cfg["order"] = order
    cfg.pop("protocol", None)
    cfg["candidate_library"] = lib_cont
    cfg["baseline_source"] = qualified_stock
    cfg["candidate_source"] = qualified_producer
    cfg["candidate_audit_source"] = qualified_audit
    cfg["candidate_library_path"] = lib_cont.rsplit("/", 1)[0] + ":/archive/production-renderer-library-restore-v5/science/lib"
    cfg["pins"].pop("/archive/selected-read-integrity-isolated-build-v3/libutils.so", None)
    cfg["pins"].pop("/archive/selected-read-paired-preparation-v1-source/selected_finite_producer.py", None)
    cfg["pins"][qualified_stock] = qualified_stock_sha
    cfg["pins"][qualified_producer] = qualified_producer_sha
    cfg["pins"][qualified_audit] = qualified_audit_sha
    cfg["pins"][qualified_identity] = qualified_identity_sha
    cfg["pins"][lib_cont] = lib_sha
    cfg["pins"]["/work/takeover/scheduler/failclosed-v5-final-source-cpu-benchmark-v2/library_resolution_preflight.py"] = resolver_sha
    cfg["pins"]["/work/takeover/scheduler/failclosed-v5-final-source-cpu-benchmark-v2/run_pinned_paired_benchmark.py"] = wrapper_sha
    cfg["pins"][remote_helper + "/paired_preparation_runner_v5.py"] = paired_runner_sha
    cfg["pins"][remote_helper + "/qualify_render.py"] = helper_qualify_sha
    cfg["pins"][remote_helper + "/audit_qualification_ledger.py"] = helper_audit_sha
    path = HERE / (jid + f"-r{i}-config.json")
    path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    cfg_paths.append(path)

manifest = {"schema": "selected-read-final-source-cpu-sequence-v1", "output_root": root_cont,
            "configs": [new_src + "/" + p.name for p in cfg_paths]}
manifest_path = HERE / (jid + "-sequence.json")
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

# The queue runs the host supervisor, which runs the already-qualified Docker
# exec/inner-guard contract. Keep that ownership/lifecycle exactly as before.
launch = json.loads((HERE / "prior-launch-contract.json").read_text(encoding="utf-8"))
launch["output_root"] = root_host
launch["inside_identity"] = root_cont + "/identity.json"
launch["seconds"] = 2320
launch["argv"] = [
    "docker", "exec", "-e", "PYTHONOPTIMIZE=0", "-e", "PYTHONDONTWRITEBYTECODE=1",
    "-e", "HIP_VISIBLE_DEVICES=", "-e", "CUDA_VISIBLE_DEVICES=", "-e", "OMP_NUM_THREADS=2",
    "-e", "OPENBLAS_NUM_THREADS=2", "vesuvius-gfx906-oldpc-v1", "env", "-u", "ROCR_VISIBLE_DEVICES",
    "python3", "/work/takeover/combined-loader-benchmark-v1/study_inner_guard_candidate.py",
    "--bounded-file", "/work/takeover/scheduler/shutdown-candidate-20261023-v1/bounded_process_shutdown_candidate.py",
    "--seconds", "2200", "--gib", "4", "--log", root_cont + "/guard.log", "--identity", root_cont + "/identity.json", "--",
    "python3", "-B", remote_helper + "/run_pinned_paired_benchmark.py", "--config", new_src + "/" + manifest_path.name,
    "--runner", runner_cont + "/paired_preparation_runner_v5.py",
    "--resolution-check", remote_helper + "/library_resolution_preflight.py", "--library-sha256", lib_sha,
    "--renderer-sha256", "1eb7d7248c2e52eb79b8c0c3be0daf02411ffbe7b448600e4356c2435f48561a",
]
launch_sh = dict(launch["source_hashes"])
launch_sh.pop("/mnt/oldpc/vesuvius_park/selected-read-integrity-isolated-build-v3/libutils.so", None)
launch_sh.pop("/mnt/oldpc/vesuvius_park/selected-read-paired-preparation-v1-source/selected_finite_producer.py", None)
launch_sh[lib_host] = lib_sha
launch_sh[host_helper + "/library_resolution_preflight.py"] = resolver_sha
launch_sh[host_helper + "/run_pinned_paired_benchmark.py"] = wrapper_sha
launch_sh[host_helper + "/paired_preparation_runner_v5.py"] = paired_runner_sha
launch_sh[host_helper + "/qualify_render.py"] = helper_qualify_sha
launch_sh[host_helper + "/audit_qualification_ledger.py"] = helper_audit_sha
launch_sh["/mnt/oldpc/vesuvius_park/selected-read-v5-optin-integration-qualification-v2-source/producer.py"] = qualified_producer_sha
launch_sh["/mnt/oldpc/vesuvius_park/selected-read-v5-optin-integration-qualification-v2-source/audit_qualification_ledger.py"] = qualified_audit_sha
launch_sh["/mnt/oldpc/vesuvius_park/selected-read-v5-optin-integration-qualification-v2-source/requested_crop_identity_v1.py"] = qualified_identity_sha
launch_sh["/mnt/oldpc/vesuvius_park/selected-read-paired-preparation-v1-source/stock_finite_producer.py"] = qualified_stock_sha
for p in cfg_paths + [manifest_path]:
    launch_sh[host_new_src + "/" + p.name] = sha(p)
# Pin the versioned experiment contract and the exact v5 provenance evidence.
for name in ["CPU_ONLY_PROTOCOL_AMENDMENT_V2.md", "benchmark-packet-v2.json", "prepare_v5_descriptors.py"]:
    launch_sh[host_helper + "/" + name] = sha(HERE / name)
launch_sh["/mnt/oldpc/vesuvius_park/selected-read-upstream-failclosed-v5-source/selected-read-cpu-final-v5.patch"] = packet["source_correspondence"]["candidate_patch_sha256"]
launch_sh["/mnt/oldpc/vesuvius_park/selected-read-upstream-failclosed-v5-postcheck-v1/result/verification.json"] = packet["source_correspondence"]["build_postcheck_sha256"]
launch_sh["/mnt/oldpc/vesuvius_park/selected-read-v5-optin-integration-qualification-v2/science/integration.json"] = packet["source_correspondence"]["production_caller_qualification_sha256"]
launch_sh[packet["source_correspondence"]["fixture_report"]] = packet["source_correspondence"]["fixture_report_sha256"]
launch_sh[packet["source_correspondence"]["build_log"]] = packet["source_correspondence"]["build_log_sha256"]
launch_sh[packet["source_correspondence"]["guard_receipt"]] = packet["source_correspondence"]["guard_receipt_sha256"]
launch["source_hashes"] = launch_sh
launch_path = HERE / (jid + "-launch-contract.json")
launch_path.write_text(json.dumps(launch, indent=2) + "\n", encoding="utf-8")
launch_host = host_new_src + "/" + launch_path.name

d = copy.deepcopy(prior)
d["id"] = jid
d["priority"] = 100
d["stage"] = "cpu-selected-read-final-source-qualification"
d["failure_domain"] = jid
d["cwd"] = runner_host
d["output_dir"] = root_host
d["dependencies"] = list(packet["design"]["dependencies"])
d["launch_authorized"] = False
d["timeout_s"] = 2420
d["purpose"] = "Prospective source-pinned CPU-only selected-read paired preparation benchmark; no GPU or inference claim."
d["scientific_scope"] = "Linux CPU preparation only; fixed crops, stock vs final failclosed source, exact-output gate."
d["benchmark_protocol"] = "selected-read-final-source-v5-cpu-only-protocol-amendment-v2"
d["requirements"].update({"container": "vesuvius-gfx906-oldpc-v1", "exclusive_host": True,
                          "cpu_slots": 2, "ram_gib": 5, "ram_floor_gib": 8,
                          "container_ram_gib": 4,
                          "disk_floors_gib": {"/mnt/scrolls": 50, "/mnt/oldpc": 40},
                          "output_gib_by_mount": {"/mnt/scrolls": 0, "/mnt/oldpc": 0.9}})
d["env"].update({"TMPDIR": root_host, "TMP": root_host, "TEMP": root_host,
                 "PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2"})
d["argv"] = [
    "python3", "/mnt/scrolls/vesuvius/takeover/scheduler/shutdown-candidate-20261023-v1/bounded_process_shutdown_candidate.py",
    "--seconds", "2380", "--gib", "1", "--shutdown-grace-s", "2", "--log", root_host + "/outer.log", "--",
    "python3", "-B", "/mnt/oldpc/vesuvius_park/production-local-fit-stock-v2-source/production_fit_host_supervisor_v2.py",
    "--contract", launch_host, "--sha256", sha(launch_path),
]
pair_paths = [root_host + f"/science/r{i}/pair.json" for i in range(1, 4)]
d["guard_receipts"] = [root_host + p for p in ("/outer.log.json", "/supervisor-guard.json", "/guard.log.json")]
d["outputs"] = ([{"path": root_host + f"/science/r{i}/pair.json", "min_bytes": 100} for i in range(1, 4)]
                + [{"path": root_host + "/cpu-paired-summary.json", "min_bytes": 200},
                   {"path": root_host + "/linker-resolution.json", "min_bytes": 300},
                   {"path": root_host + "/identity.json", "min_bytes": 100},
                   {"path": root_host + "/container.log", "min_bytes": 100}])
sh = dict(d["source_hashes"])
sh.pop("/mnt/oldpc/vesuvius_park/selected-read-integrity-isolated-build-v3/libutils.so", None)
sh[lib_host] = lib_sha
sh[host_helper + "/library_resolution_preflight.py"] = resolver_sha
sh[host_helper + "/run_pinned_paired_benchmark.py"] = wrapper_sha
sh[host_helper + "/paired_preparation_runner_v5.py"] = paired_runner_sha
sh[host_helper + "/qualify_render.py"] = helper_qualify_sha
sh[host_helper + "/audit_qualification_ledger.py"] = helper_audit_sha
sh["/mnt/oldpc/vesuvius_park/selected-read-v5-optin-integration-qualification-v2-source/producer.py"] = qualified_producer_sha
sh["/mnt/oldpc/vesuvius_park/selected-read-v5-optin-integration-qualification-v2-source/audit_qualification_ledger.py"] = qualified_audit_sha
sh["/mnt/oldpc/vesuvius_park/selected-read-v5-optin-integration-qualification-v2-source/requested_crop_identity_v1.py"] = qualified_identity_sha
sh["/mnt/oldpc/vesuvius_park/selected-read-paired-preparation-v1-source/stock_finite_producer.py"] = qualified_stock_sha
for p in cfg_paths + [manifest_path]:
    sh[host_new_src + "/" + p.name] = sha(p)
sh[launch_host] = sha(launch_path)
for name in ["CPU_ONLY_PROTOCOL_AMENDMENT_V2.md", "benchmark-packet-v2.json", "prepare_v5_descriptors.py"]:
    sh[host_helper + "/" + name] = sha(HERE / name)
sh["/mnt/oldpc/vesuvius_park/selected-read-upstream-failclosed-v5-source/selected-read-cpu-final-v5.patch"] = packet["source_correspondence"]["candidate_patch_sha256"]
sh["/mnt/oldpc/vesuvius_park/selected-read-upstream-failclosed-v5-postcheck-v1/result/verification.json"] = packet["source_correspondence"]["build_postcheck_sha256"]
sh["/mnt/oldpc/vesuvius_park/selected-read-v5-optin-integration-qualification-v2/science/integration.json"] = packet["source_correspondence"]["production_caller_qualification_sha256"]
sh[packet["source_correspondence"]["fixture_report"]] = packet["source_correspondence"]["fixture_report_sha256"]
sh[packet["source_correspondence"]["build_log"]] = packet["source_correspondence"]["build_log_sha256"]
sh[packet["source_correspondence"]["guard_receipt"]] = packet["source_correspondence"]["guard_receipt_sha256"]
d["source_hashes"] = sh
descriptor = HERE / (jid + ".json")
descriptor.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": "GENERATED_LAUNCH_DISABLED_PRIORITY_100_SUCCESSOR",
                  "descriptor": descriptor.name, "order": orders,
                  "pair_outputs": pair_paths, "source_pin_count": len(sh)}, indent=2))
