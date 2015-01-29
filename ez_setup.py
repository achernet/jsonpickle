#!/usr/bin/env python
"""Bootstrap setuptools installation

To use setuptools in your package's setup.py, include this
file in the same directory and add this to the top of your setup.py::

    from ez_setup import use_setuptools
    use_setuptools()

To require a specific version of setuptools, set a download
mirror, or use an alternate download directory, simply supply
the appropriate options to ``use_setuptools()``.

This file can also be run as a script to install or upgrade setuptools.
"""
import glob
import tarfile
import os
import shutil
import sys
import tempfile
import zipfile
import optparse
import subprocess
import platform
import textwrap
import contextlib

from distutils import log

try:
    # noinspection PyCompatibility
    from urllib.request import urlopen
except ImportError:
    # noinspection PyCompatibility
    from urllib2 import urlopen

try:
    from site import USER_SITE
except ImportError:
    USER_SITE = None

try:
    import simplejson as json
except ImportError:
    import json


def _python_cmd(*args):
    """
    Return True if the command succeeded.
    """
    args = (sys.executable,) + args
    return subprocess.call(args) == 0


def _install(archive_filename, install_args=()):
    with archive_context(archive_filename):
        # installing
        log.warn('Installing Setuptools')
        if not _python_cmd('setup.py', 'install', *install_args):
            log.warn('Something went wrong during the installation.')
            log.warn('See the error message above.')
            # exitcode will be 2
            return 2


@contextlib.contextmanager
def archive_context(filename):
    # extracting the archive
    tmpdir = tempfile.mkdtemp()
    log.warn('Extracting in %s', tmpdir)
    old_wd = os.getcwd()
    try:
        os.chdir(tmpdir)
        filename_base, file_ext = os.path.splitext(filename)
        if file_ext == '.zip':
            with contextlib.closing(zipfile.ZipFile(filename)) as archive:
                archive.extractall()
        else:
            with contextlib.closing(tarfile.open(filename)) as archive:
                archive.extractall()

        # going in the directory
        subdir = os.path.join(tmpdir, os.listdir(tmpdir)[0])
        os.chdir(subdir)
        log.warn('Now working in %s', subdir)
        yield

    finally:
        os.chdir(old_wd)
        shutil.rmtree(tmpdir)


def _do_download(package, version, to_dir, download_delay):
    glob_fmt = '{package}-{version}-py{major}.{minor}*.egg'
    file_glob = glob_fmt.format(package=package,
                                version=version,
                                major=sys.version_info[0],
                                minor=sys.version_info[1])
    path_glob = os.path.join(to_dir, file_glob)
    egg_paths = glob.glob(path_glob)
    if not egg_paths:
        archive = download_package(package, version, to_dir, download_delay)
        with archive_context(archive):
            # building an egg
            log.warn('Building a %s egg in %s', package, to_dir)
            _python_cmd('setup.py', '-q', 'bdist_egg', '--dist-dir', to_dir)
        # returning the result
        egg_paths = glob.glob(path_glob)
        log.warn('Pattern %s matches %d files', path_glob, len(egg_paths))
        if not egg_paths:
            raise IOError('Could not build the egg.')
    egg_stats = {}
    for path in egg_paths:
        try:
            egg_stats[path] = os.stat(path).st_mtime
        except Exception as e:
            log.fatal('Error reading path %s', path)
    egg = max(egg_stats.items(), key=lambda (k, v): v)[0]
    sys.path.insert(0, egg)

    # Remove previously-imported pkg_resources if present (see
    # https://bitbucket.org/pypa/setuptools/pull-request/7/ for details).
    for key, val in sys.modules.items():
        if key.startswith('pkg_resources'):
            del sys.modules[key]

    import setuptools

    setuptools.bootstrap_install_from = egg


def use_package(package='setuptools', version=None, to_dir=os.curdir, download_delay=15):
    to_dir = os.path.abspath(to_dir)
    if version is None:
        version = get_version_info(package)['latest_version']
    rep_modules = 'pkg_resources', 'setuptools'
    imported = set(sys.modules).intersection(rep_modules)
    try:
        import pkg_resources
    except ImportError:
        pkg_resources = None
    if pkg_resources is None:
        return _do_download(package, version, to_dir, download_delay)
    while True:
        try:
            pkg_resources.require("{0}>={1}".format(package, version))
            break
        except pkg_resources.DistributionNotFound as dnf:
            log.error('Error loading package %s: %s', package, dnf)
            dnf_package = dnf.args[0].key
            if package == dnf_package:
                _do_download(package, version, to_dir, download_delay)
            else:
                dnf_version = get_version_info(dnf_package)['latest_version']
                _do_download(dnf_package, dnf_version, to_dir, download_delay)
        except pkg_resources.VersionConflict as VC_err:
            if imported:
                msg = textwrap.dedent("""
                    The required version of setuptools (>={version}) is not available,
                    and can't be installed while this script is running. Please
                    install a more recent version first, using
                    'easy_install -U setuptools'.

                    (Currently using {VC_err.args[0]!r})
                    """).format(VC_err=VC_err, version=version)
                sys.stderr.write(msg)
                sys.exit(2)

            # otherwise, reload ok
            del pkg_resources, sys.modules['pkg_resources']
            return _do_download(package, version, to_dir, download_delay)


def _clean_check(cmd, target):
    """
    Run the command to download target. If the command fails, clean up before
    re-raising the error.
    """
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        if os.access(target, os.F_OK):
            os.unlink(target)
        raise


def download_file_powershell(url, target):
    """
    Download the file at url to target using Powershell (which will validate
    trust). Raise an exception if the command cannot complete.
    """
    target = os.path.abspath(target)
    ps_cmd = (
        "[System.Net.WebRequest]::DefaultWebProxy.Credentials = "
        "[System.Net.CredentialCache]::DefaultCredentials; "
        "(new-object System.Net.WebClient).DownloadFile(%(url)r, %(target)r)"
        % vars()
    )
    cmd = [
        'powershell',
        '-Command',
        ps_cmd,
    ]
    _clean_check(cmd, target)


def has_powershell():
    if platform.system() != 'Windows':
        return False
    cmd = ['powershell', '-Command', 'echo test']
    with open(os.path.devnull, 'wb') as devnull:
        try:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)
        except Exception:
            return False
    return True


download_file_powershell.viable = has_powershell


def download_file_curl(url, target):
    cmd = ['curl', url, '--silent', '--output', target]
    _clean_check(cmd, target)


def has_curl():
    cmd = ['curl', '--version']
    with open(os.path.devnull, 'wb') as devnull:
        try:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)
        except Exception:
            return False
    return True


download_file_curl.viable = has_curl


def download_file_wget(url, target):
    cmd = ['wget', url, '--quiet', '--output-document', target]
    _clean_check(cmd, target)


def has_wget():
    cmd = ['wget', '--version']
    with open(os.path.devnull, 'wb') as devnull:
        try:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)
        except Exception:
            return False
    return True


download_file_wget.viable = has_wget


def download_file_insecure(url, target):
    """
    Use Python to download the file, even though it cannot authenticate the
    connection.
    """
    src = urlopen(url)
    try:
        # Read all the data in one block.
        data = src.read()
    finally:
        src.close()

    # Write all the data in one block to avoid creating a partial file.
    with open(target, "wb") as dst:
        dst.write(data)


download_file_insecure.viable = lambda: True


def get_best_downloader():
    downloaders = (
        download_file_powershell,
        download_file_curl,
        download_file_wget,
        download_file_insecure,
    )
    viable_downloaders = (dl for dl in downloaders if dl.viable())
    return next(viable_downloaders, None)


def get_version_info(package='setuptools', version=None):
    """
    Get the latest version of setuptools.
    """
    default_version_url = 'https://pypi.python.org/pypi/{0}/json'.format(package)
    with contextlib.closing(urlopen(default_version_url)) as vsrc:
        data_str = vsrc.read()
    data = json.loads(data_str)
    if version is None or version not in data['info']:
        latest_version = data['info']['version']
    else:
        latest_version = version
    release_info = {'latest_version': latest_version}
    for release in data['releases'][latest_version]:
        if release['packagetype'] == 'sdist':
            release_info['filename'] = release['filename']
            release_info['url'] = release['url']
            break
    return release_info


def download_package(package='setuptools', version=None, to_dir=os.curdir, delay=15,
                     downloader_factory=get_best_downloader):
    """
    Download setuptools from a specified location and return its filename

    `version` should be a valid setuptools version number that is available
    as an egg for download under the `download_base` URL (which should end
    with a '/'). `to_dir` is the directory where the egg will be downloaded.
    `delay` is the number of seconds to pause before an actual download
    attempt.

    ``downloader_factory`` should be a function taking no arguments and
    returning a function for downloading a URL to a target.
    """
    # making sure we use the absolute path
    to_dir = os.path.abspath(to_dir)
    version = get_version_info(package, version)
    saveto = os.path.join(to_dir, version['filename'])
    if not os.path.exists(saveto):  # Avoid repeated downloads
        log.warn("Downloading %s", version['url'])
        downloader = downloader_factory()
        downloader(version['url'], saveto)
    return os.path.realpath(saveto)


def _build_install_args(options):
    """
    Build the arguments to 'python setup.py install' on the setuptools package
    """
    return ['--user'] if options.user_install else []


def _parse_args():
    """
    Parse the command line for options
    """
    parser = optparse.OptionParser()
    parser.add_option('--package', default='setuptools', metavar='PKG',
                      help='A package (other than setuptools) to install with this tool')
    parser.add_option(
        '--user', dest='user_install', action='store_true', default=False,
        help='install in user site package (requires Python 2.6 or later)')
    # parser.add_option(
    #     '--download-base', dest='download_base', metavar="URL",
    #     default=DEFAULT_URL,
    #     help='alternative URL from where to download the setuptools package')
    parser.add_option(
        '--insecure', dest='downloader_factory', action='store_const',
        const=lambda: download_file_insecure, default=get_best_downloader,
        help='Use internal, non-validating downloader'
    )
    parser.add_option(
        '--version', help="Specify which version to download",
        default=None,
    )
    options, args = parser.parse_args()
    # positional arguments are ignored
    return options


def main():
    """Install or upgrade setuptools and EasyInstall"""
    options = _parse_args()
    archive = download_package(package=options.package, version=options.version,
                               downloader_factory=options.downloader_factory)
    return _install(archive, _build_install_args(options))


if __name__ == '__main__':
    sys.exit(main())
