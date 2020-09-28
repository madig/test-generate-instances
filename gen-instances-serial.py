#!/bin/env python3

import argparse
from pathlib import Path

import ufoLib2
from fontmake.instantiator import Instantiator
from fontTools.designspaceLib import DesignSpaceDocument


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

    # (Load all sources into memory completely rather than have the instantiator load
    # data on demand. This cleanly separates source loading from source preparation in
    # profilers. This may distort measurements if the sources have extra layers or any
    # data/ data or images.)
    designspace.loadSourceFonts(ufoLib2.Font.open, lazy=False)
    instantiator = Instantiator.from_designspace(designspace)
    
    for instance_descriptor in designspace.instances:
        instance = instantiator.generate_instance(instance_descriptor)
        file_stem = f"{instance.info.familyName}-{instance.info.styleName}".replace(" ", "")
        instance.save(args.output_dir / f"{file_stem}.ufo", overwrite=True)
