#!/bin/env python3

import argparse
import multiprocessing
from pathlib import Path

from fontmake.instantiator import Instantiator
from fontTools.designspaceLib import DesignSpaceDocument, InstanceDescriptor


def generate_and_write_autohinted_instance(
    instantiator: Instantiator,
    instance_descriptor: InstanceDescriptor,
    output_dir: Path,
):
    print(f"Generating {instance_descriptor.name}")
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

    # 2. Prepare masters.
    print("Instantiating instantiator")
    generator = Instantiator.from_designspace(designspace, round_geometry=True)

    # (Fork one process per instance)
    processes = []
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    for instance in designspace.instances:
        print(f"Queueing {instance.name}")
        processes.append(
            pool.apply_async(
                generate_and_write_autohinted_instance,
                args=(generator, instance, args.output_dir),
            )
        )
    pool.close()
    pool.join()
    for process in processes:
        process.get()  # Catch exceptions.
