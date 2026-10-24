"""Fresh bounded CPU rebuild and full 35-case public API CTest for v5."""
import argparse, hashlib, json, os, pathlib, shlex, subprocess, time


def sha(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def run(argv, env, log, timeout=300):
    with pathlib.Path(log).open('ab') as f:
        subprocess.run(argv, env=env, stdout=f, stderr=subprocess.STDOUT,
                       check=True, timeout=timeout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--source-root', required=True)
    parser.add_argument('--candidate-root', required=True)
    args = parser.parse_args()
    out = pathlib.Path(args.output)
    source_root = pathlib.Path(args.source_root)
    candidate_root = pathlib.Path(args.candidate_root)
    park = pathlib.Path('/mnt/oldpc/vesuvius_park')
    assert out.resolve().is_relative_to(park)
    assert source_root == park / 'selected-read-integrity-v3-source'
    assert candidate_root == park / 'selected-read-upstream-failclosed-v5-source'
    out.mkdir(parents=True, exist_ok=True)
    provenance_path = source_root / 'build-provenance.json'
    provenance = json.loads(provenance_path.read_text())
    assert all(sha(path) == expected
               for path, expected in provenance['source_snapshot_pins'].items())
    env = dict(os.environ)
    env['TMPDIR'] = str(out)
    commands = []
    started = time.monotonic()

    def checked(argv):
        commands.append(argv)
        run(argv, env, out / 'build-and-test.log')

    original = shlex.split(provenance['original_compile_command']['command'])
    flags = original[1:original.index('-o')]
    flags = [arg.replace('-flto=auto', '-flto=2')
             .replace('/work/flatboi_build/src_pr/volume-cartographer/utils/include',
                      str(source_root / 'source-snapshot/include'))
             .replace('/work/flatboi_build/', '/mnt/scrolls/vesuvius/flatboi_build/')
             for arg in flags]
    candidate_zarr = candidate_root / 'volume-cartographer/utils/src/zarr.cpp'
    assert candidate_zarr.is_file()
    object_file = out / 'zarr-candidate.o'
    checked(['/usr/bin/g++', '-I' + str(source_root / 'compile-include'),
             '-I' + str(source_root), *flags, '-c', str(candidate_zarr),
             '-o', str(object_file)])

    runtime_libs = pathlib.Path('/mnt/oldpc/vesuvius_park/production-renderer-library-restore-v5/science/lib')
    library = out / 'libutils.so'
    env['LD_LIBRARY_PATH'] = str(out) + ':' + str(runtime_libs)
    retained = provenance['retained_objects']
    checked(['/usr/bin/g++', '-shared', '-flto=2', '-Wl,--gc-sections',
             '-Wl,--as-needed', '-Wl,-soname,libutils.so', str(object_file),
             *retained, '-L' + str(runtime_libs), '-Wl,-rpath,' + str(runtime_libs),
             '-Wl,-l:libQt6Core.so.6', '-Wl,-l:libcurl.so.4', '-Wl,-l:libz.so.1',
             '-Wl,-l:libzstd.so.1', '-Wl,-l:liblz4.so.1',
             '-Wl,-l:libcrypto.so.3', '-o', str(library)])
    dependencies = subprocess.run(['ldd', str(library)], env=env, check=True,
                                  capture_output=True, text=True).stdout
    assert 'not found' not in dependencies
    (out / 'ldd.txt').write_text(dependencies)

    cmake_source = out / 'cmake-source'
    cmake_source.mkdir()
    fixture = candidate_root / 'volume-cartographer/utils/tests'
    include_root = source_root / 'source-snapshot/include'
    compile_include = source_root / 'compile-include'
    cmake_source.joinpath('CMakeLists.txt').write_text(f'''cmake_minimum_required(VERSION 3.20)
project(verified_ct_read_failclosed_v5 LANGUAGES CXX)
enable_testing()
set(CMAKE_CXX_STANDARD 23)
function(vc_register_test_target target)
endfunction()
function(vc_register_ctest test_name target)
endfunction()
add_library(utils SHARED IMPORTED)
set_target_properties(utils PROPERTIES IMPORTED_LOCATION "{library}"
  INTERFACE_COMPILE_DEFINITIONS UTILS_HAS_CURL=1
  INTERFACE_INCLUDE_DIRECTORIES "{compile_include};{include_root}")
add_subdirectory("{fixture}" "{out / 'build/tests'}")
''')
    checked(['cmake', '-S', str(cmake_source), '-B', str(out / 'build'),
             '-DCMAKE_BUILD_TYPE=Release'])
    checked(['cmake', '--build', str(out / 'build'), '--target',
             'test_verified_ct_read', '-j2'])
    checked(['ctest', '--test-dir', str(out / 'build'), '-R',
             'verified_ct_read', '--output-on-failure'])
    fixture_report_path = out / 'build/tests/verified-ct-read/integrated-fixture-report.json'
    fixture_report = json.loads(fixture_report_path.read_text())
    assert fixture_report['status'] == 'PASS_INTEGRATED_GUARDED_PUBLIC_ZARR_API'
    assert len(fixture_report['cases']) == 35, len(fixture_report['cases'])
    partial = {row['case'] for row in fixture_report['cases']
               if row['case'].startswith('partial_opt_in_mask_')}
    assert partial == {f'partial_opt_in_mask_{mask}' for mask in range(1, 7)}, partial
    report = {
        'status': 'V5_CPU_ONLY_PUBLIC_API_CTEST_PASS',
        'base_commit': '417e17689029434fa1572efe20a3e7a9bfc79be4',
        'candidate_patch_sha256': sha(candidate_root / 'selected-read-cpu-final-v5.patch'),
        'commands': commands,
        'wall_seconds': time.monotonic() - started,
        'library_sha256': sha(library),
        'fixture_report': fixture_report,
        'scope': 'Fresh v5 zarr.cpp rebuild against retained pinned project objects and all 35 guarded public API cases. CPU-only; no renderer integration or performance evidence. This result is newly generated and does not reuse v2/v3/v4 CTest results.'
    }
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'cases': len(fixture_report['cases']),
                      'partial_environment_masks': sorted(partial),
                      'library_sha256': report['library_sha256']}))


if __name__ == '__main__':
    main()
