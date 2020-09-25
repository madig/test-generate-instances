#!/bin/env python3

import argparse
import multiprocessing
from pathlib import Path

import ufoLib2
from fontmake.instantiator import Instantiator
from fontTools.designspaceLib import DesignSpaceDocument, InstanceDescriptor


def generate_and_write_autohinted_instance(
    designspace: DesignSpaceDocument,
    instance_descriptor: InstanceDescriptor,
    output_dir: Path,
):
    print(f"Generating {instance_descriptor.name}")
    # (Load all sources into memory completely rather than have the instantiator load
    # data on demand. This cleanly separates source loading from source preparation in
    # profilers. This may distort measurements if the sources have extra layers or any
    # data/ data or images.)
    designspace.loadSourceFonts(ufoLib2.Font.open, lazy=False)
    instantiator = Instantiator.from_designspace(designspace)
    instance = instantiator.generate_instance(instance_descriptor)
    file_stem = f"{instance.info.familyName}-{instance.info.styleName}".replace(" ", "")
    instance.save(output_dir / f"{file_stem}.ufo", overwrite=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("designspace_path", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    # 1. Load Designspace and filter out instances that are marked as non-exportable.
    designspace = DesignSpaceDocument.fromfile(args.designspace_path)
    designspace.instances = [
        s
        for s in designspace.instances
        if s.lib.get("com.schriftgestaltung.export", True)
    ]

    # (Fork one process per instance)
    processes = []
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    for instance in designspace.instances:
        print(f"Queueing {instance.name}")
        processes.append(
            pool.apply_async(
                generate_and_write_autohinted_instance,
                args=(designspace, instance, args.output_dir),
            )
        )
    pool.close()
    pool.join()
    for process in processes:
        process.get()  # Catch exceptions.
