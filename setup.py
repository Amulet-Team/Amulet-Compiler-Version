import subprocess
import os

from setuptools import setup

version = "1.2.0"

try:
    import amulet_compiler_version
except ImportError:
    build_specialised = os.environ.get("BUILD_SPECIALISED", "1")
    if build_specialised == "1":
        # verify cmake is installed
        if subprocess.run(["cmake", "--version"]).returncode:
            raise RuntimeError(
                "Could not find cmake command. cmake is required to compile extension code."
            )

        # get the compiler id and version
        if subprocess.run(
                ["cmake", "-S", "get_compiler", "-B", "get_compiler/build"]
        ).returncode:
            raise RuntimeError("Could not find a C++ 20 compiler. Do you have a C++ 20 compiler installed?")

        # Get the compiler variables generated by the cmake file
        with open("get_compiler/build/compiler_id.txt") as f:
            compiler_id_str = f.read().strip()
        with open("get_compiler/build/compiler_version.txt") as f:
            compiler_version = f.read().strip()

        # convert the compiler id to an int so it can be used in a version number
        compiler_id_int = 0
        for c in compiler_id_str:
            compiler_id_int <<= 8
            compiler_id_int += ord(c)

        # combine the compiler id and compiler version into a version number
        version = f"{version}.{compiler_id_int}.{compiler_version}"
    elif build_specialised == "0":
        compiler_id_str = "UNKNOWN"
        compiler_version = "UNKNOWN"
    else:
        raise RuntimeError("BUILD_SPECIALISED must be '0' or '1'")

    # write the python file
    os.makedirs("src", exist_ok=True)
    with open("src/amulet_compiler_version.py", "w") as f:
        f.write(f'compiler_id = "{compiler_id_str}"\n')
        f.write(f'compiler_version = "{compiler_version}"\n')
        f.write(f'__version__ = "{version}"\n')
else:
    compiler_id_str = amulet_compiler_version.compiler_id
    compiler_version = amulet_compiler_version.compiler_version


# run setup with the generated or default version
setup(version=version)
