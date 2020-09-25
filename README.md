# UFO font instance generation benchmarking

Producing fonts from source files is often done with Python libraries, which happen to be slow in more than one way. Interpolating instances from a collection of drawn instances is extra slow: you have to read them all in (potentially thousands of glyphs per source) and then sift through them to prepare them for interpolation. All of that is currently done serially in the relevant Python libraries. Only the final step, the instance generation, can be done in parallel.

This repository contains some test scripts for timing and profiling various methods of generating instances in parallel.

Install the rquirements first:

```
> # Create a Python venv and activate it first.
> pip install -r requirements.txt
```

Run the scripts like this:

```
> python gen-instances-simple-copy.py NotoSans-MM.designspace /tmp
```

The instancees will then be written to `/tmp`. Note: On Fedora 32, this is usually a RAM-backed filesystem.

With a profiler like [py-spy](https://github.com/benfred/py-spy), run them like this:

```
> py-spy record -F -s -n -r 60 -f speedscope -o out.speedscope python gen-instances-simple-copy.py NotoSans-MM.designspace /tmp
```

and load the generated `out.speedscope` file into https://www.speedscope.app/.