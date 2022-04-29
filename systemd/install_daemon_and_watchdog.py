from pathlib import Path
import shutil
import git
import re


repo = git.Repo(Path.cwd().joinpath('.git').as_posix())
repo.git.add('--all')
repo.git.commit('-m', 'commit test', author='katayama@udel.edu')
origin = repo.remote(name="main")
origin.push()
