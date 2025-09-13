import argparse
import logging
import subprocess
import os
import sys
import json
from multiprocessing import cpu_count
from pathlib import Path
from time import perf_counter

from lang import *

init_i18n(get_language_json("en-us"))
_ = t

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s (%(filename)s.%(funcName)s %(lineno)d)",
    datefmt=_("time")
)
logger = logging.getLogger("PyMake")

VERSION = "1.1.5"
AUTHOR = "RED.BLUE.LIGHT 红蓝灯"
DEFAULT_CONFIG_PATH = Path("config.json")

DEFAULT_CONFIG = {
    "nuitka_args": [
        "--standalone",
        "--remove-output",
        "--output-dir=dist",
        "--enable-plugin=upx",
        "--windows-disable-console",
        "--jobs=auto"
    ]
}


def load_config(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        logger.info(_("1"), file_path)
        return config_data

    except FileNotFoundError:
        logger.error(_("2"), file_path)
        sys.exit(1)

    except json.JSONDecodeError as e:
        logger.error(_("3"), file_path, e)
        sys.exit(1)

    except Exception as e:
        logger.exception(_("4"), e)
        sys.exit(1)


def save_config(config, file_path):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        logger.info(_("5"), file_path)

    except Exception as e:
        logger.error(_("6"), e)
        sys.exit(1)


def validate_and_process_args(config):
    args = config.get("nuitka_args", [])
    processed_args = []
    jobs_set = False

    for arg in args:

        if arg == "--jobs=$auto":
            run_cpu_count = cpu_count() << 1
            processed_args.append(f"--jobs={run_cpu_count}")
            jobs_set = True
            logger.info(_("7"), run_cpu_count)
        elif arg.startswith("--jobs="):
            jobs_set = True
            processed_args.append(arg)
        else:
            if arg == "--file-version=$get":
                version = input(_("8"))
                processed_args.append(f"--file-version={version}")
            else:
                processed_args.append(arg)

    if not jobs_set:
        run_cpu_count = cpu_count() << 1
        processed_args.append(f"--jobs={run_cpu_count}")
        logger.info(_("9"), run_cpu_count)

    return processed_args


def run_nuitka(config):
    try:
        nuitka_args = validate_and_process_args(config)
        cmd = [sys.executable, "-m", "nuitka"] + nuitka_args

        logger.info(_("10"))
        logger.debug(_("11"), " ".join(cmd))

        start_time = perf_counter()

        with subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1
        ) as proc:
            if proc.stdout:
                for line in proc.stdout:
                    print(f"[{_('nuitka-output')}] {line}", end="")

        return_code = proc.wait()
        duration = perf_counter() - start_time

        if return_code == 0:
            logger.info(_("12"), duration)
            return 0
        else:
            logger.error(_("13"), return_code, duration)
            return 1

    except FileNotFoundError:
        logger.error(_("14"))
        sys.exit(1)
    except Exception as e:
        logger.exception(_("15"), e)
        sys.exit(1)


def is_compiled():
    try:
        if __compiled__ is not None:
            return True
    except NameError:
        return False


def main():
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--set-language", metavar="language-code-value")
    pre_args = pre_parser.parse_args()

    if pre_args.set_language:
        init_i18n(get_language_json(pre_args.set_language))
    else:
        init_i18n(get_language_json(get_system_language()))

    global _
    _ = t

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s (%(filename)s.%(funcName)s %(lineno)d)",
        datefmt=_("time"),
        force=True
    )
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
        prog="PyMake",
        description=f"PyMake v{VERSION} by {AUTHOR}{'' if is_compiled() else ' (DEBUG)'}",
        usage=f"pymake.exe [{_('options')}]" if is_compiled() else f"pymake.py [{_('options')}]",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=_("16")
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"PyMake v{VERSION}",
        help=_("--version-help")
    )

    parser.add_argument(
        "--load-config",
        metavar=_("json-file-value"),
        help=_("--load-config-help")
    )

    parser.add_argument(
        "--save-config",
        metavar=_("json-file-value"),
        nargs="?",
        const=DEFAULT_CONFIG_PATH,
        help=_("--save-config-help")
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help=_("--verbose-help")
    )

    parser.add_argument(
        "--set-language",
        metavar=_("language-code-value"),
        help=_("--set-language-help")
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if args.save_config is not None:
        if args.save_config.endswith(".json"):
            save_config(DEFAULT_CONFIG, Path(args.save_config))
        else:
            save_config(DEFAULT_CONFIG, Path(DEFAULT_CONFIG_PATH))
    elif args.load_config:
        config = load_config(Path(args.load_config))
        run_nuitka(config)
    else:
        parser.print_help()
        logger.info("test TEST 测试")

    print(_("pause-exit"), end="")
    os.system("pause >nul")
    return 0


if __name__ == "__main__":
    main()