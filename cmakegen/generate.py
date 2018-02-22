from pathlib import Path

from .options import *
from .files import cmake_lists, cpp_files, cpp_headers, clang_format

class Generator:
  def __init__(self): pass

class NormalGenerator(Generator):
  def __init__(self, force):
    super().__init__()
    self.force = force

  def mkdir(self, path):
    path.mkdir(exist_ok=self.force)

  def write_file(self, path, to_write):
    with path.open(mode="w") as file:
      file.write(to_write)

class DryRunGenerator(Generator):
  def __init__(self):
    super().__init__()

  def mkdir(self, path):
    print("> mkdir", path)

  def write_file(self, path, to_write):
    print("> writing to `", path, "`: ", sep="")
    print(to_write)
    print()

def cmake_file(project_name, kind, standard):
  cml = None
  if kind == KIND_EXE:
    cml = cmake_lists.executable
  elif kind == KIND_LIB:
    cml = cmake_lists.library
  elif kind == KIND_HEAD:
    cml = cmake_lists.header
  else:
    assert False

  return cml.substitute(
      projname=project_name,
      cxx_version=standard)

def build_project(generator, project_name, kind, standard, style):
  proj_dir = Path(Path.cwd(), project_name)
  generator.mkdir(proj_dir)
  
  source_dir = Path(proj_dir, "source")
  generator.mkdir(source_dir)

  include_dir = Path(proj_dir, "include")
  generator.mkdir(include_dir)

  proj_include_dir = Path(include_dir, project_name)
  generator.mkdir(proj_include_dir)

  cmake_path = Path(proj_dir, "CMakeLists.txt")
  generator.write_file(cmake_path, cmake_file(project_name, kind, standard))

  if style is not None:
    clangfmt_path = Path(proj_dir, ".clang-format")
    if style == STYLE_NICOLETTE:
      generator.write_file(clangfmt_path, clang_format.nicolette)
    else:
      assert False

  header_path = Path(proj_include_dir, project_name + ".h")

  if kind == KIND_EXE:
    generator.write_file(
        header_path,
        cpp_headers.standalone.substitute(projname=project_name))
    generator.write_file(
        Path(source_dir, "main.cpp"),
        cpp_files.executable.substitute(projname=project_name))
  elif kind == KIND_LIB:
    generator.write_file(
        header_path,
        cpp_headers.dependent.substitute(projname=project_name))
    generator.write_file(
        Path(source_dir, project_name + ".cpp"),
        cpp_files.library.substitute(projname=project_name))

  else: # header only library
    generator.write_file(
        header_path,
        cpp_headers.standalone.substitute(projname=project_name))