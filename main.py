import argparse
import logging
import multiprocessing
import platform
import subprocess
import sys
import time
from lang import *
from pathlib import Path

init_i18n(get_language_json(get_system_language()))

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s (%(filename)s.%(funcName)s %(lineno)d)",
    datefmt=t("time")
)
logger: logging.Logger = logging.getLogger("PyMake")

VERSION: str = "1.1.3"
AUTHOR: str = "RED.BLUE.LIGHT 红蓝灯"
DEFAULT_CONFIG_PATH: Path = Path("config.json")

DEFAULT_CONFIG: dict = {
    "nuitka_args": [
        "--standalone",
        "--remove-output",
        "--output-dir=dist",
        "--enable-plugin=upx",
        "--windows-disable-console",
        "--jobs=auto"
    ]
}


def load_config(file_path: Path) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            config_data: dict = json.load(f)

        logger.info(t("1"), file_path)
        return config_data

    except FileNotFoundError:
        logger.error(t("2"), file_path)
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(t("3"), file_path, e)
        sys.exit(1)
    except Exception as e:
        logger.exception(t("4"), e)
        sys.exit(1)


def save_config(config: dict, file_path: Path):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        logger.info("配置已保存到: %s", file_path)

    except Exception as e:
        logger.error("保存配置文件失败: %s", e)
        sys.exit(1)


def validate_and_process_args(config: dict) -> list[str]:
    args: list = config.get("nuitka_args", [])
    processed_args: list = []
    jobs_set: bool = False

    for arg in args:

        if arg == "--jobs=$auto":
            cpu_count = multiprocessing.cpu_count()
            run_cpu_count: int = cpu_count * 2
            processed_args.append(f"--jobs={run_cpu_count}")
            jobs_set = True
            logger.info("自动设置并行编译工作数: %d", run_cpu_count)
        elif arg.startswith("--jobs="):
            jobs_set = True
            processed_args.append(arg)
        else:
            if arg == "--file-version=$get":
                version: str = input("请输入版本号（格式：X.X.X.X）：")
                processed_args.append(f"--file-version={version}")
            else:
                processed_args.append(arg)

    if not jobs_set:
        run_cpu_count = multiprocessing.cpu_count()
        processed_args.append(f"--jobs={run_cpu_count}")
        logger.info(f"自动添加并行编译参数: --jobs={run_cpu_count}")

    return processed_args


def run_nuitka(config: dict) -> int | None:
    try:

        nuitka_args = validate_and_process_args(config)

        cmd = [sys.executable, "-m", "nuitka"] + nuitka_args

        logger.info("开始执行Nuitka编译...")
        logger.debug("完整命令: %s", " ".join(cmd))

        start_time: float = time.perf_counter()
        print(cmd)

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
                    print(f"[Nuitka输出] {line}", end="")

            return_code: int = proc.wait()

        duration = time.perf_counter() - start_time

        if return_code == 0:
            logger.info("编译成功完成! 耗时: %.3f秒", duration)
            return 0
        else:
            logger.error("编译失败! 退出码: %d, 耗时: %.2f秒", return_code, duration)
            sys.exit(1)

    except FileNotFoundError:
        logger.error("未找到Nuitka, 请先安装: pip install nuitka")
        sys.exit(1)
    except Exception as e:
        logger.exception("编译过程中发生意外错误: %s", e)
        sys.exit(1)


def is_compiled() -> bool:
    try:
        if __compiled__ is not None:
            return True
    except NameError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="PyMake",
        description=f"PyMake v{VERSION} by {AUTHOR}{'' if is_compiled() else ' (DEBUG)'}",
        usage="pymake.exe [选项]" if is_compiled() else "pymake.py [选项]",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="若要了解更多信息，请查看help.md"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"PyMake {VERSION}",
        help="显示工具版本"
    )

    parser.add_argument(
        "--load-config",
        metavar="JSON文件",
        help="从JSON文件加载配置\n示例: --load-config build.json\n本程序内置配置可前往程序所在目录的help.html查看"
    )

    parser.add_argument(
        "--save-config",
        metavar="JSON文件",
        nargs="?",
        const=DEFAULT_CONFIG_PATH,
        help="保存默认配置到JSON文件\n示例: --save-config 或 --save-config custom.json"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="启用详细输出模式"
    )

    parser.add_argument(
        "--language",
        metavar="语言代码",
        help="设置工具语言"
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

    print("按下任意键以退出程序", end=" ")
    os.system("pause>nul")
    return 0


if __name__ == "__main__":
    if not platform.system() == "Windows":
        sys.exit()
    sys.exit(main())
