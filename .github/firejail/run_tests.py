import subprocess
import sys
import shlex


def run(cmd, **kwargs):
    print("+ " + shlex.join(cmd), flush=True)
    try:
        subprocess.run(cmd, check=True, **kwargs)
    except Exception as e:
        sys.exit(e)


def firejail_cmd():
    return [
        "firejail",
        "--quiet",
        "--whitelist=./bld",
        "--whitelist=/tmp",
        "--netfilter=.github/firejail/netfilter.rules",
        "--tracelog",
        "--seccomp",
        "--seccomp.drop",
        "@network-io",
        "--seccomp.keep",
        "@file-system,@io-event,@ipc,@basic-io,@default-keep",
    ]


def main():
    match sys.argv[1]:
        case "configure":
            run(["mkdir", "bld"])
            run(
                firejail_cmd()
                + [
                    "--",
                    "bash",
                    "-lc",
                    "cmake -B bld "
                    "-DCMAKE_C_COMPILER='clang' "
                    "-DCMAKE_CXX_COMPILER='clang++' "
                    "-DAPPEND_CXXFLAGS='-O3 -g2' "
                    "-DAPPEND_CFLAGS='-O3 -g2' "
                    "-DCMAKE_BUILD_TYPE=Debug "
                    "-DBUILD_GUI=ON "
                    "-DBUILD_BENCH=ON "
                    "-DBUILD_FUZZ_BINARY=ON "
                    "-DWITH_ZMQ=ON "
                    "-DWITH_USDT=ON "
                    "-DWERROR=ON",
                ]
            )
        case "build":
            run(
                firejail_cmd()
                + ["--", "bash", "-lc", "cmake --build ./bld -j $(nproc)"]
            )
        case "unit":
            run(
                firejail_cmd()
                + [
                    "--",
                    "bash",
                    "-lc",
                    "ctest --build-run-dir ./ --output-on-failure --stop-on-failure "
                    "--test-dir ./bld -j $(nproc)",
                ]
            )
        case "fun":
            run(
                firejail_cmd()
                + [
                    "--",
                    "bash",
                    "-lc",
                    "./bld/test/functional/test_runner.py -j $(( $(nproc) * 2 )) "
                    "--combinedlogslen=99999999 --timeout-factor=10 --extended "
                    '--exclude "interface_bitcoin_cli,rpc_bind"',
                ]
            )
        case "fuzz":
            run(
                [
                    "git",
                    "clone",
                    "https://github.com/bitcoin-core/qa-assets",
                    "--depth=1",
                    "./bld/qa-assets",
                ]
            )
            run(
                firejail_cmd()
                + [
                    "--",
                    "bash",
                    "-lc",
                    "./bld/test/fuzz/test_runner.py -l DEBUG -j $(nproc) ./bld/qa-assets/fuzz_corpora/",
                ]
            )

        case _:
            print(f"Unknown command!")
            sys.exit(1)


if __name__ == "__main__":
    main()
