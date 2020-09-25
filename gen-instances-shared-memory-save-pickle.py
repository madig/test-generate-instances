#!/bin/env python3

import argparse
import multiprocessing
import pickle
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path

from fontmake.instantiator import Instantiator
from fontTools.designspaceLib import DesignSpaceDocument, InstanceDescriptor


def generate_and_write_autohinted_instance(
    shared_generator_memory_name: str,
    instance_descriptor: InstanceDescriptor,
    output_dir: Path,
):
    shm_b = SharedMemory(shared_generator_memory_name)
    instantiator = pickle.loads(shm_b.buf)
    shm_b.close()
    print(f"Generating {instance_descriptor.name}")
    instance = instantiator.generate_instance(instance_descriptor)
    file_stem = f"{instance.info.familyName}-{instance.info.styleName}".replace(" ", "")
    instance_pickled = pickle.dumps(instance)
    with open(output_dir / f"{file_stem}.ufo.pickle", "wb+") as f:
        f.write(instance_pickled)


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

    # 3. Pickle instantiator into shared memory once so all worker processes can
    #    re-instantiate it from there, otherwise we have to pickle it for for every
    #    single worker.
    generator_pickled = pickle.dumps(generator)
    shared_generator_memory = SharedMemory(create=True, size=len(generator_pickled))
    shared_generator_memory.buf[:] = generator_pickled
    del generator, generator_pickled

    # (Fork one process per instance)
    processes = []
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    for instance in designspace.instances:
        print(f"Queueing {instance.name}")
        processes.append(
            pool.apply_async(
                generate_and_write_autohinted_instance,
                args=(shared_generator_memory.name, instance, args.output_dir),
            )
        )
    pool.close()
    pool.join()
    try:
        for process in processes:
            process.get()  # Catch exceptions.
    finally:
        shared_generator_memory.close()
        shared_generator_memory.unlink()
