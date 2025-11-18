import os
import time
import click
import pathlib
import platform
import requests
import dataclasses
import logging as l
import subprocess as sb

OS_TYPE = platform.system()
DEFAULT_VOLUME_LEVEL = 15
DEFAULT_WATCH_URL_PATH = "https://www.google.com"
DEFAULT_MAX_FAILED_ATTEMPTS_NUM = 1
DEFAULT_SLEEP_TIME_SEC = 60
DEFAULT_LOG_LEVEL = l.INFO

CLI_LOG_LEVEL_MAP = {
    "debug": l.DEBUG,
    "info": l.INFO,
    "warning": l.WARNING,
    "error": l.ERROR,
    "critical": l.CRITICAL,
}


@dataclasses.dataclass
class CliArgs:
    alarm_file_path: pathlib.Path
    volume_level: int
    watch_url_path: str
    max_failed_attempts_num: int
    sleep_time_sec: int
    loglevel: int


logger = l.getLogger(__name__)


def setup_logging(level: int = l.INFO) -> l.Logger:
    logger.setLevel(level)
    formatter = l.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )
    handler = l.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    handler.setLevel(level)
    return logger


def is_network_down(url: str) -> bool:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to establish connection with {url}. {e}.")
        return True
    return False


# NOTE: I hate windows ;(
def alarm_windows(alarm_file_path: pathlib.Path, volume_level: int):
    try:
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        # Set the system volume
        logger.info(f"Setting Windows volume to: {volume_level}%")
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)

        # Convert volume (0-100) to pycaw's scalar (0.0-1.0)
        volume.SetMasterVolumeLevelScalar(volume_level / 100.0, None)
    except ImportError:
        logger.error("The 'pycaw' library not found")
    except Exception as e:
        logger.error(f"Failed to set volume: {e}")
    try:
        logger.info(f"Alarm sound file: {alarm_file_path}")
        os.startfile(str(alarm_file_path))
    except Exception as e:
        logger.error(f"Failed to play sound on Windows: {e}")


def alarm_linux(alarm_file_path: pathlib.Path, volume_level: int):
    try:
        sb.run(
            ["amixer", "sset", "Master", f"{volume_level}%"],
            check=True,
            capture_output=True,
        )
        logger.info(f"Volume set to: {volume_level}%")
        logger.info(f"Alarm sound file: {alarm_file_path}")
        sb.run(["paplay", str(alarm_file_path)], check=True)
    except FileNotFoundError:
        logger.error(
            "Failed to run command. Is 'amixer' or 'paplay' installed and in your PATH?"
        )
    except sb.CalledProcessError as e:
        logger.error(f"Failed to launch a process. {e}")
    except Exception as e:
        logger.error(f"Failed to run alarm command. {e}")


def alarm(alarm_file_path: pathlib.Path, volume_level: int):
    if OS_TYPE == "Linux":
        alarm_linux(alarm_file_path, volume_level)
    elif OS_TYPE == "Windows":
        alarm_windows(alarm_file_path, volume_level)
    else:
        logger.error("Invaild platform. Exiting...")
        click.exit(1)


def main(args: CliArgs):
    setup_logging(args.loglevel)

    logger.info("Alarm notifier start")
    logger.info(f"OS Type: {OS_TYPE}")
    logger.info(f"Watching URL: {args.watch_url_path}")
    logger.info(f"Alarm file: {args.alarm_file_path}")

    failed_attempts_num = 0
    while True:
        if is_network_down(args.watch_url_path):
            failed_attempts_num += 1
            logger.warning(
                f"Network is down. Number of failed attempts {failed_attempts_num}"
            )
            if failed_attempts_num >= args.max_failed_attempts_num:
                logger.error(
                    "Failed to establish internet connection. Starting the alarm."
                )
                alarm(args.alarm_file_path, args.volume_level)
                continue
        else:
            if failed_attempts_num > 0:
                logger.info("Connection established.")
            failed_attempts_num = 0
        time.sleep(args.sleep_time_sec)


@click.command()
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),
    required=True,
    help="Path to the audio file.",
)
@click.option(
    "--volume",
    "-v",
    type=click.IntRange(0, 100),
    default=DEFAULT_VOLUME_LEVEL,
    help="Volume level.",
)
@click.option(
    "--url",
    "-u",
    default=DEFAULT_WATCH_URL_PATH,
    help="The url to test connection.",
)
@click.option(
    "--attempts",
    "-a",
    type=int,
    default=DEFAULT_MAX_FAILED_ATTEMPTS_NUM,
    help="Number of attempts to establish connection.",
)
@click.option(
    "--period",
    "-p",
    type=int,
    default=DEFAULT_SLEEP_TIME_SEC,
    help="Time period between connection attempts.",
)
@click.option(
    "--loglevel",
    "-l",
    type=click.Choice(CLI_LOG_LEVEL_MAP.keys(), case_sensitive=False),
    default="info",
    help="Set log level",
)
def cli(file, volume, url, attempts, period, loglevel):
    args = CliArgs(
        file,
        volume,
        url,
        attempts,
        period,
        CLI_LOG_LEVEL_MAP[loglevel.lower()],
    )
    main(args)


if __name__ == "__main__":
    cli()
