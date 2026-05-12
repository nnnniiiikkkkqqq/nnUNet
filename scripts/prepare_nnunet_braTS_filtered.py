#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import sys
from typing import Dict, Tuple

import SimpleITK as sitk


def parse_label_map(items) -> Dict[str, int]:
    labels = {}
    for item in items:
        if ":" not in item:
            raise ValueError(f"Invalid label mapping: {item}. Use name:id.")
        name, idx = item.split(":", 1)
        name = name.strip()
        idx = int(idx.strip())
        labels[name] = idx
    return labels


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def link_or_copy(src: str, dst: str, link_type: str) -> None:
    if os.path.exists(dst):
        return
    if link_type == "symlink":
        os.symlink(src, dst)
        return
    if link_type == "hardlink":
        try:
            os.link(src, dst)
            return
        except OSError:
            link_type = "copy"
    if link_type == "copy":
        shutil.copy2(src, dst)
        return
    raise ValueError(f"Unknown link_type: {link_type}")


def save_binarized_label(src: str, dst: str) -> None:
    image = sitk.ReadImage(src)
    array = sitk.GetArrayFromImage(image)
    array = (array > 0).astype("uint8")
    out = sitk.GetImageFromArray(array)
    out.CopyInformation(image)
    sitk.WriteImage(out, dst)


def discover_cases(source_dir: str, modality_suffix: str) -> Tuple[int, Dict[str, Tuple[str, str]]]:
    cases = {}
    for case_name in sorted(os.listdir(source_dir)):
        case_dir = os.path.join(source_dir, case_name)
        if not os.path.isdir(case_dir):
            continue
        image_path = os.path.join(case_dir, f"{case_name}-{modality_suffix}.nii.gz")
        label_path = os.path.join(case_dir, f"{case_name}-seg.nii.gz")
        if os.path.exists(image_path) and os.path.exists(label_path):
            cases[case_name] = (image_path, label_path)
    return len(cases), cases


def write_dataset_json(dataset_dir: str, channel_name: str, labels: Dict[str, int], num_training: int) -> None:
    dataset_json = {
        "channel_names": {"0": channel_name},
        "labels": labels,
        "numTraining": num_training,
        "file_ending": ".nii.gz",
    }
    out_path = os.path.join(dataset_dir, "dataset.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dataset_json, f, indent=2)
        f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare nnUNet raw dataset from filtered BraTS folder.")
    parser.add_argument("--source", required=True, help="Path to filtered_dataset root.")
    parser.add_argument("--dataset-id", type=int, default=501, help="nnUNet dataset ID.")
    parser.add_argument("--dataset-name", default="BraTSFiltered", help="nnUNet dataset name suffix.")
    parser.add_argument("--channel-name", default="t2f", help="Modality/channel name.")
    parser.add_argument("--label-map", nargs="+", required=True, help="Label map: name:id (space-separated).")
    parser.add_argument("--link-type", choices=["symlink", "hardlink", "copy"], default="symlink")
    parser.add_argument("--binarize-labels", action="store_true", help="Convert labels to 0/1.")
    args = parser.parse_args()

    source_dir = os.path.abspath(args.source)
    dataset_dir_name = f"Dataset{args.dataset_id:03d}_{args.dataset_name}"
    nnunet_raw = os.environ.get("nnUNet_raw")
    if not nnunet_raw:
        print("ERROR: nnUNet_raw environment variable is not set.", file=sys.stderr)
        return 2
    dataset_dir = os.path.join(nnunet_raw, dataset_dir_name)

    images_tr = os.path.join(dataset_dir, "imagesTr")
    labels_tr = os.path.join(dataset_dir, "labelsTr")
    ensure_dir(images_tr)
    ensure_dir(labels_tr)

    labels = parse_label_map(args.label_map)

    num_training, cases = discover_cases(source_dir, args.channel_name)
    if num_training == 0:
        print("ERROR: no valid cases found.", file=sys.stderr)
        return 3

    for case_name, (image_path, label_path) in cases.items():
        nnunet_image = os.path.join(images_tr, f"{case_name}_0000.nii.gz")
        nnunet_label = os.path.join(labels_tr, f"{case_name}.nii.gz")
        link_or_copy(image_path, nnunet_image, args.link_type)
        if args.binarize_labels:
            save_binarized_label(label_path, nnunet_label)
        else:
            link_or_copy(label_path, nnunet_label, args.link_type)

    write_dataset_json(dataset_dir, args.channel_name, labels, num_training)
    print(f"Prepared {num_training} cases at {dataset_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
