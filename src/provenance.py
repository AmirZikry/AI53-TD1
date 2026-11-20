from __future__ import annotations

import hashlib
import json
from pathlib import Path

import importlib.metadata
import platform
import subprocess
import torch


def training_data_identity(
    train_manifest: Path = Path("data/processed/manifests/train.csv"),
    validation_manifest: Path = Path("data/processed/manifests/validation.csv"),
) -> str:
    """Return a deterministic identity for the training + validation manifests.

    This helper is provided because the final evaluator uses the same identity
    to verify that the selected MLflow Run matches the current prepared data.
    Do not hard-code the value.
    """
    paths = (train_manifest, validation_manifest)
    if any(not path.exists() for path in paths):
        return "unavailable"

    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()

def _get_git_info() -> tuple[str, bool]:
    """Return (commit_sha, is_dirty) from Git, with safe fallbacks."""
    try:
        commit_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        commit_sha = "unknown"

    try:
        status_out = subprocess.check_output(
            ["git", "status", "--porcelain"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        is_dirty = bool(status_out)
    except Exception:
        is_dirty = False

    return commit_sha, is_dirty


def _package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"

def build_run_manifest(params: dict, device: str, mlflow_run_id: str) -> dict:
    """Build experiment provenance metadata.

    TODO: collect at least:
      - Git commit SHA and whether the working tree is dirty;
      - identity of the prepared training + validation manifests;
      - Python, PyTorch, torchvision, DVC and MLflow versions;
      - OS/platform and CUDA runtime (when available);
      - compute device; random seed; image size; training parameters;
      - MLflow Run ID.

    Hints: subprocess, platform, importlib.metadata, torch,
    training_data_identity().
    """
    commit_sha, is_dirty = _get_git_info()
    data_identity = training_data_identity()

    data_cfg = params.get("data", {})
    train_cfg = params.get("train", {})
    aug_cfg = params.get("augmentation", {})

    return {
        "git": {
            "commit_sha": commit_sha,
            "dirty": is_dirty,
        },
        "data": {
            "training_data_identity": data_identity,
        },
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "torch": _package_version("torch"),
            "torchvision": _package_version("torchvision"),
            "dvc": _package_version("dvc"),
            "mlflow": _package_version("mlflow"),
            "cuda_runtime": torch.version.cuda if torch.cuda.is_available() else None,
        },
        "execution": {
            "mlflow_run_id": mlflow_run_id,
            "device": device,
            "random_state": train_cfg.get("random_state"),
        },
        "configuration": {
            "image_size": data_cfg.get("image_size"),
            "batch_size": train_cfg.get("batch_size"),
            "epochs": train_cfg.get("epochs"),
            "learning_rate": train_cfg.get("learning_rate"),
            "dropout": train_cfg.get("dropout"),
            "augmentation": {
                "enabled": aug_cfg.get("enabled"),
                "horizontal_flip": aug_cfg.get("horizontal_flip"),
                "rotation_degrees": aug_cfg.get("rotation_degrees"),
            },
        },
    }


def write_run_manifest(params: dict, device: str, mlflow_run_id: str, path: Path) -> dict:
    manifest = build_run_manifest(params, device, mlflow_run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest
