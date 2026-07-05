import os
from tempfile import TemporaryDirectory
from hashlib import sha256
from base64 import urlsafe_b64encode
import shutil

MajorVersion = 4
CompilerStrings = ["AppleClang", "MSVC", "GNU"]


CompilerVersionPy = """\
compiler_id = "{compiler_str}"
compiler_version = "{compiler_version}"
__version__ = "{library_version}"
"""

Metadata = """\
Metadata-Version: 2.4
Name: amulet-compiler-version
Version: {library_version}
Summary: A tiny library to allow dependencies to require the same compiler.
Author: James Clare
Project-URL: Homepage, https://www.amuletmc.com
Project-URL: Repository, https://github.com/Amulet-Team/Amulet-Compiler-Version
Project-URL: Issues, https://github.com/Amulet-Team/Amulet-Compiler-Version/issues
Classifier: Programming Language :: Python :: 3
Classifier: Operating System :: OS Independent
Requires-Python: >=3.9
Description-Content-Type: text/markdown
Provides-Extra: dev
Requires-Dist: setuptools>=42; extra == "dev"
Requires-Dist: wheel; extra == "dev"

# Amulet Compiler Version

A tiny library to allow dependencies to require the same compiler.
"""

Wheel = """\
Wheel-Version: 1.0
Generator: setuptools (83.0.0)
Root-Is-Purelib: true
Tag: py3-none-any

"""

TopLevel = """\
amulet_compiler_version
"""

def hash(data: str) -> str:
    return urlsafe_b64encode(sha256(data.encode("utf-8")).digest()).decode().rstrip("=")


def main() -> None:
    wheel_dir = os.path.join(os.path.dirname(__file__), "wheels")
    os.makedirs(wheel_dir, exist_ok=True)
    for compiler_str in CompilerStrings:
        native_newline = "\r\n" if compiler_str == "MSVC" else "\n"
        compiler_int = 0
        for c in compiler_str:
            compiler_int = (compiler_int << 8) + ord(c)
        for compiler_version in range(1, 100):
            library_version = f"{MajorVersion}.{compiler_int}.{compiler_version}"
            with TemporaryDirectory() as tmpdir:
                dist_info = f"amulet_compiler_version-{library_version}.dist-info"
                dist_info_dir = os.path.join(tmpdir, dist_info)
                os.makedirs(dist_info_dir, exist_ok=True)
                with open(os.path.join(dist_info_dir, "RECORD"), "w", encoding="utf-8", newline="\n") as record:
                    def write_file(path: str, contents: str, newline="\n") -> None:
                        parent_path = os.path.dirname(path)
                        if parent_path:
                            os.makedirs(parent_path, exist_ok=True)
                        with open(os.path.join(tmpdir, path), "w", encoding="utf-8", newline=newline) as f:
                            f.write(contents)
                        contents = contents.replace("\r", "").replace("\n", newline)
                        record.write(f"{path},sha256={hash(contents)},{len(contents)}\n")

                    write_file(
                        "amulet_compiler_version.py",
                        CompilerVersionPy.format(
                            compiler_str=compiler_str,
                            compiler_version=compiler_version,
                            library_version=library_version,
                        ),
                        native_newline
                    )

                    write_file(
                        f"{dist_info}/METADATA",
                        Metadata.format(library_version=library_version),
                        native_newline
                    )

                    write_file(
                        f"{dist_info}/WHEEL",
                        Wheel
                    )

                    write_file(
                        f"{dist_info}/top_level.txt",
                        TopLevel
                    )

                    record.write(f"{dist_info}/RECORD,,\n")

                whl_path = os.path.join(wheel_dir, f"amulet_compiler_version-{library_version}-py3-none-any.whl")
                shutil.make_archive(
                    whl_path,
                    "zip",
                    tmpdir
                )
                os.rename(f"{whl_path}.zip", whl_path)


if __name__ == '__main__':
    main()
