from toolchain import Recipe, shprint, current_directory
from os.path import join, exists
import os
import sh


arch_mapper = {'i386': 'darwin-i386-cc',
               'x86_64': 'darwin64-x86_64-cc',
               'armv7': 'iphoneos-cross',
               'arm64': 'iphoneos-cross'}


class OpensslRecipe(Recipe):
    version = "1.0.2l"
    url = "http://www.openssl.org/source/openssl-{version}.tar.gz"
    depends = ["hostopenssl"]
    #libraries = ["libssl.a", "libcrypto.a"]
    include_dir = "include"
    include_per_arch = True

    def build_arch(self, arch):
        options_iphoneos = (
            "-isysroot {}".format(arch.sysroot),
            "-DOPENSSL_THREADS",
            "-D_REENTRANT",
            "-DDSO_DLFCN",
            "-DHAVE_DLFCN_H",
            "-fomit-frame-pointer",
            "-fno-common",
            "-O3"
        )

        build_env = arch.get_env()
        #build_env['INSTALL_PREFIX'] = "@executable_path/../Frameworks"
        #build_env['INSTALLTOP'] = "@executable_path/../Frameworks"
        build_env['LIBDIR'] = ''
        target = arch_mapper[arch.arch]
        shprint(sh.env, _env=build_env)
        sh.perl(join(self.build_dir, "Configure"),
                target,
                "-shared", #: Build shared lib
                #'--install_prefix=@executable_path/../Frameworks', #: Set install prefix
                '--prefix=@rpath', #: Apparently prefix isnt used
                _env=build_env)
        if target == 'iphoneos-cross':
            sh.sed("-ie", "s!^CFLAG=.*!CFLAG={} {}!".format(build_env['CFLAGS'],
                   " ".join(options_iphoneos)),
                   "Makefile")
            sh.sed("-ie", "s!static volatile sig_atomic_t intr_signal;!static volatile intr_signal;! ",
                   "crypto/ui/ui_openssl.c")
        else:
            sh.sed("-ie", "s!^CFLAG=!CFLAG={} !".format(build_env['CFLAGS']),
                   "Makefile")

        #: Patch for version
        sh.sed("-ie", "s!SHLIB_MINOR=0.0!"
                      "SHLIB_MINOR=0.2!", "Makefile")
        sh.sed("-ie", "s!SHLIB_VERSION_NUMBER=1.0.0!"
                      "SHLIB_VERSION_NUMBER={}!".format(self.version), "Makefile")

        shprint(sh.make, "clean")
        shprint(sh.make, "-j4", "build_libs","LIBDIR=.")#, _env=build_env)

        #: Copy to dist/lib/arch folder
        arch_lib_dir = join(self.ctx.dist_dir,'.',arch.arch)
        if not exists(arch_lib_dir):
            os.makedirs(arch_lib_dir)

        #: Why is version not the same?
        with current_directory(self.build_dir):
            for f in ['crypto','ssl']:
                #: Copy and rename
                v = self.version[:-1]
                sh.cp('-f','lib{}.{}.dylib'.format(f,v),
                      join(arch_lib_dir,'lib{}.{}.dylib'.format(f,v)))



recipe = OpensslRecipe()
