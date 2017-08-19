import sh
from os.path import join, exists
import os
from glob import glob
from toolchain import CppPythonRecipe, shprint, current_directory

class AtomRecipe(CppPythonRecipe):
    site_packages_name = 'atom'
    version = '0.3.10'
    url = 'https://github.com/nucleic/atom/archive/master.zip'
    depends = ['python','host_setuptools']

    # def install_package(self, arch):
    #     """Automate the installation of a Python package into the target
    #     site-packages.
    #
    #     """
    #     env = self.get_recipe_env(arch)
    #     build_dir = self.get_build_dir(arch.arch)
    #     try:
    #         super(AtomRecipe, self).install_package()
    #     except:
    #         #: Dont ccare that this fails, we copy everything manually
    #         pass
    #     with current_directory(join(build_dir, 'build',
    #                                 'lib.{}-2.7'.format(env['_PYTHON_HOST_PLATFORM']))):
    #         dest = join(self.ctx.dist_dir, 'python', arch.arch, 'site-packages')
    #         if not exists(dest):
    #             os.makedirs(dest)
    #
    #         #: Find all the so files
    #         for f in sh.find('.','-name','*.so').strip().split("\n"):
    #             so_name = ".".join(f.split("/")[1:])
    #
    #             #: Copy
    #             shprint(sh.mv, f, join(dest,so_name))

            #: Clean up crap from install fail above



recipe = AtomRecipe()