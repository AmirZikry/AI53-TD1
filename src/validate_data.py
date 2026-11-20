from __future__ import annotations

import json
from pathlib import Path
from PIL import Image

EXPECTED_SPLITS = {"train": 1034, "validation": 133, "test": 128}
EXPECTED_CLASSES = {"angular_leaf_spot", "bean_rust", "healthy"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def validate_dataset(raw_root: Path) -> dict:
    """Validate the raw dataset and return a deterministic quality report.

    Required Core checks:
      1. required splits exist;
      2. exactly the expected classes exist in every split;
      3. expected image counts are present;
      4. every image can be fully decoded by Pillow (`Image.load()` or equivalent);
      5. no split or class is empty.

    TODO: implement the checks and return a JSON-serializable report.
    The report must not contain timestamps because it is a DVC output.
    """
    if not raw_root.is_dir():
        raise FileNotFoundError(f"The {raw_root} is not found.")

    expected_classes_sorted=sorted(EXPECTED_CLASSES)
    splits_report: dict[str, dict] = {}
    total_images = 0

    for split_name, expected_count in EXPECTED_SPLITS.items():
        split_dir = raw_root / split_name
        # 1. Required splits exist
        if not split_dir.is_dir():
            raise RuntimeError(f"Missing required split directory: {split_dir}")

        # 2. Exactly the expected classes exist in every split
        actual_classes = sorted(
            d.name for d in split_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
        )
        if actual_classes != expected_classes_sorted:
            raise RuntimeError(
                f"Split '{split_name}' has classes {actual_classes}, expected {expected_classes_sorted}"
            )

        class_counts: dict[str, int] = {}
        split_image_count = 0

        for class_name in expected_classes_sorted:
            class_dir = split_dir / class_name
            image_files = sorted(
                f for f in class_dir.iterdir()
                if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
            )

            # 5. No class is empty
            if not image_files:
                raise RuntimeError(f"Class directory '{class_name}' in split '{split_name}' is empty")

            # 4. Every image can be fully decoded by Pillow
            for img_path in image_files:
                with Image.open(img_path) as img:
                    img.load()
            
            count = len(image_files)
            class_counts[class_name] = count
            split_image_count += count

        # 3 & 5. Expected image counts are present and split is non-empty
        if split_image_count == 0 or split_image_count != expected_count:
            raise RuntimeError(
                f"Split '{split_name}' has {split_image_count} images, expected {expected_count}"
            )

        splits_report[split_name] = {
            "images": split_image_count,
            "class_counts": class_counts,
        }
        total_images += split_image_count

    return {
        "status": "PASS",
        "classes": expected_classes_sorted,
        "splits": splits_report,
        "total_images": total_images,
    }

def main() -> None:
    report = validate_dataset(Path("data/raw"))
    Path("reports").mkdir(exist_ok=True)
    Path("reports/data_quality.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
# Add comment unchanged file