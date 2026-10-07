import argparse
import logging
import sys

from downloader import TeachableDownloader
from utils import read_urls_from_file

logger = logging.getLogger(__name__)


def check_required_args(args):
    return bool(args.email and args.password or args.man_login_url)


def get_log_level(verbose):
    if verbose == 0:
        return logging.WARNING
    elif verbose == 1:
        return logging.INFO
    else:
        return logging.DEBUG


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Teachable-Dl",
        description="Download courses",
    )
    parser.add_argument("--url", required=False, help="URL of the course")
    parser.add_argument("-e", "--email", required=False, help="Email of the account")
    parser.add_argument(
        "-p", "--password", required=False, help="Password of the account"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (repeat for more verbosity)",
    )
    parser.add_argument(
        "--complete-lecture",
        action="store_true",
        default=False,
        help="Complete the lecture after downloading",
    )
    parser.add_argument(
        "--login_url", required=False, help="(Optional) URL to teachable SSO login page"
    )
    parser.add_argument(
        "--man_login_url",
        required=False,
        help="Login manually and start downloading when this url is reached",
    )
    parser.add_argument(
        "-f", "--file", required=False, help="Path to a text file that contains URLs"
    )
    parser.add_argument(
        "--user-agent",
        required=False,
        help="User agent to use when downloading videos",
        default="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/116.0.0.0 Safari/537.36",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        required=False,
        help="Timeout for selenium driver",
        default=10,
    )
    args = parser.parse_args()
    verbose = False
    log_level = get_log_level(args.verbose)
    if log_level == logging.DEBUG:
        verbose = True

    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    if not check_required_args(args):
        logger.error(
            "Required arguments are missing. Choose email/password or manual login (man_login_url)."
        )
        sys.exit(1)

    downloader = TeachableDownloader(
        verbose_arg=verbose,
        complete_lecture_arg=args.complete_lecture,
        user_agent_arg=args.user_agent,
        timeout_arg=args.timeout,
    )

    if args.file:
        urls = read_urls_from_file(args.file)
        try:
            downloader.run_batch(
                urls,
                args.email,
                args.password,
                args.login_url,
                args.man_login_url,
            )
            downloader.cleanup()
            sys.exit(0)
        except KeyboardInterrupt:
            logger.error("Interrupted by user")
            downloader.cleanup()
            sys.exit(1)
        except Exception as e:
            logger.error("Error: " + str(e))
            downloader.cleanup()
            sys.exit(1)
    else:
        # Check if url argument is passed
        if not args.url:
            logger.error("URL is required")
            sys.exit(1)
        try:
            downloader.run(
                course_url=args.url,
                email=args.email,
                password=args.password,
                login_url=args.login_url,
                man_login_url=args.man_login_url,
            )
            downloader.cleanup()
            sys.exit(0)
        except KeyboardInterrupt:
            logger.error("Interrupted by user")
            downloader.cleanup()
            sys.exit(1)
        except Exception as e:
            logger.error("Error: " + str(e))
            downloader.cleanup()
            sys.exit(1)
