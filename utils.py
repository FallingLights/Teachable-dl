import logging
import os

logger = logging.getLogger(__name__)


def create_folder(course_title):
    root_path = os.path.abspath(os.getcwd())
    course_path = os.path.join(root_path, "courses", course_title)
    os.makedirs(course_path, exist_ok=True)
    return course_path


def clean_string(data):
    logger.debug("Cleaning string: " + data)
    # Remove all non-ASCII characters (including emojis)
    data = data.encode("ascii", "ignore").decode("ascii")
    # Replace specific characters with "-"
    return (
        data.replace("\n", "-")
        .replace(" ", "-")
        .replace(":", "-")
        .replace("/", "-")
        .replace("|", "-")
        .replace("*", "")
        .replace("?", "-")
        .replace("<", "-")
        .replace(">", "-")
        .replace('"', "-")
        .replace("\\", "-")
    )


def truncate_title_to_fit_filename(title, max_filename_length=250):
    # the file name length should not be too long
    # truncate the title to accommodate the max used file extension length and lecture index prefix
    max_title_length = max_filename_length - len(".mp4.part-Frag0000.part") - 3
    if len(title) > max_title_length:
        truncated_title = title[:max_title_length]
        logger.warning("Truncating title: " + truncated_title)
        return truncated_title
    return title


def read_urls_from_file(file_path):
    urls = []
    try:
        with open(file_path) as file:
            urls = file.read().splitlines()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    except OSError as e:
        logger.error(f"IOError reading file: {file_path}. Error: {e!s}")
    except Exception as e:
        logger.error(f"Unexpected error reading file: {file_path}. Error: {e!s}")

    if urls:
        logger.info(f"Successfully read {len(urls)} URLs from file: {file_path}")
    else:
        logger.warning(f"No URLs found in file: {file_path}")

    return urls
