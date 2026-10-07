import json
import logging
import os
import re
import string
import time
from urllib.parse import urljoin, urlparse, urlunparse

import requests
import selenium.webdriver.support.expected_conditions as EC
import wget
import yt_dlp
from selenium.common import TimeoutException
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumbase import Driver

from utils import clean_string, create_folder, truncate_title_to_fit_filename

logger = logging.getLogger(__name__)


class TeachableDownloader:
    def __init__(
        self,
        verbose_arg=False,
        complete_lecture_arg=False,
        user_agent_arg="",
        origin_arg="",
        referer_arg="",
        timeout_arg=10,
    ):
        self.driver = Driver(uc=True, headed=True)
        self.headers = {
            "User-Agent": user_agent_arg,
            "Origin": origin_arg or "https://player.hotmart.com",
            "Referer": referer_arg or "https://player.hotmart.com",
        }
        self.verbose = verbose_arg
        self._complete_lecture = complete_lecture_arg
        self.global_timeout = timeout_arg

    def check_elem_exists(self, by, selector, timeout):
        try:
            WebDriverWait(self.driver, timeout=self.global_timeout).until(
                EC.presence_of_element_located((by, selector))
            )
        except Exception:
            return False
        return True

    def bypass_cloudflare_if_present(self):
        if self.check_elem_exists(
            By.ID, "challenge-stage", timeout=self.global_timeout
        ):
            self.bypass_cloudflare()
        else:
            logger.info("No need to bypass cloudflare")

    def bypass_cloudflare(self):
        if self.driver.capabilities["browserVersion"].split(".")[0] < "115":
            return
        logger.info("Bypassing cloudflare")
        time.sleep(1)

        try:
            self.driver.find_element(
                By.ID, "challenge-stage"
            ).click()  # make sure the challenge is focused
            self.driver.execute_script(
                '''window.open("''' + self.driver.current_url + """","_blank");"""
            )  # open page in new tab
            input(
                "\033[93mWarning: Bypassing Cloudflare\nplease click on the captcha checkbox if not done already "
                "and press enter to continue (do not close any of the tabs)\033[0m"
            )
            self.driver.switch_to.window(
                window_name=self.driver.window_handles[0]
            )  # switch to first tab
            self.driver.close()  # close first tab
            self.driver.switch_to.window(
                window_name=self.driver.window_handles[0]
            )  # switch back to new tab
        except Exception as e:
            logger.error("Could not bypass cloudflare: " + str(e))
            return

    def manual_login(self, man_login_url):
        while self.driver.current_url != man_login_url:
            time.sleep(3)
            logger.info("Waiting for user to navigate to url: " + man_login_url)
            logger.info("Current url: " + self.driver.current_url)
        return True

    def construct_sign_in_url(self, course_url):
        parsed_url = urlparse(course_url)
        # Replace the path with '/sign_in'
        sign_in_path = "/sign_in"
        fallback_url = urlunparse(
            (parsed_url.scheme, parsed_url.netloc, sign_in_path, "", "", "")
        )
        return fallback_url

    def find_login(self, course_url):
        logger.info("Trying to find login")
        self.driver.implicitly_wait(self.global_timeout)
        self.driver.get(course_url)

        try:
            login_element = WebDriverWait(self.driver, self.global_timeout).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Login"))
            )
        except TimeoutException:
            logger.warning("Login button not found, navigating to fallback URL")
            fallback_url = self.construct_sign_in_url(course_url)
            self.driver.get(fallback_url)
        else:
            login_element.click()

    def login(self, email, password):
        logger.info("Logging in")

        self.bypass_cloudflare_if_present()

        WebDriverWait(self.driver, timeout=15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        email_element = WebDriverWait(self.driver, self.global_timeout).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        password_element = WebDriverWait(self.driver, self.global_timeout).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        commit_element = WebDriverWait(self.driver, self.global_timeout).until(
            EC.presence_of_element_located((By.NAME, "commit"))
        )

        logger.debug("Filling in login form")
        email_element.click()
        email_element.clear()
        self.driver.execute_script(
            "document.getElementById('email').value='" + email + "'"
        )

        password_element.click()
        password_element.clear()
        self.driver.execute_script(
            "document.getElementById('password').value='" + password + "'"
        )

        commit_element.click()

        # Check for login error due to incorrect credentials
        logger.debug("Checking for login error")
        try:
            error_elements = WebDriverWait(self.driver, self.global_timeout).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div.toast, span.text-with-icon")
                )
            )
            for element in error_elements:
                if "Your email or password is incorrect" in element.text:
                    logger.error("Login failed: Incorrect email or password.")
                    return False
        except TimeoutException:
            # No error elements found, assuming login was successful
            pass

        # Check for new device challenge
        # input with name otp_code
        if self.check_elem_exists(By.NAME, "otp_code", timeout=self.global_timeout):
            # wait for user to enter code
            input(
                "\033[93mWarning: New device challenge\nplease enter the code sent to your email and press enter to "
                "continue\033[0m"
            )
        logger.info("Logged in, switching to course page")
        time.sleep(3)

    def run(self, course_url, email, password, login_url, man_login_url):
        logger.info("Starting login")

        if not man_login_url:
            # Check if login_url is not set
            if not login_url:
                try:
                    self.find_login(course_url)
                except Exception as e:
                    logger.error(
                        "Could not find login: " + str(e), exc_info=self.verbose
                    )
            else:
                self.driver.get(login_url)

            try:
                self.login(email, password)
            except Exception as e:
                logger.error("Could not login: " + str(e), exc_info=self.verbose)
                return
        else:
            self.driver.get(course_url)
            self.manual_login(man_login_url)

        logger.info("Starting download of course: " + course_url)

        try:
            self.pick_course_downloader(course_url)
        except Exception as e:
            logger.error(
                "Could not download course: " + course_url + " cause: " + str(e)
            )

    def run_batch(self, url_list, email, password, login_url, man_login_url):
        """
        This method handles batch downloading of courses. It navigates to the given URLs, logs in if necessary,
        and initiates the download process for each course.

        :param url_list: List[str]
            An array of URLs pointing to the courses that need to be downloaded.
        :param email: str
            The email address used to log in to the platform.
        :param password: str
            The password associated with the provided email address.
        :param login_url: str
            The URL of the login page. If not provided, manual login is assumed.
        :param man_login_url: str
            The URL of the page to navigate to after manual login. This parameter is optional.
            If provided, the script will wait until the user has manually navigated to this URL
            before starting the download process.
        :return: None
        """
        logger.info("Starting login")

        if not man_login_url:
            # Check if login_url is not set
            if login_url:
                self.driver.get(login_url)
            else:
                logger.error("Login url is not set")
                return

            try:
                self.login(email, password)
            except Exception as e:
                logger.error("Could not login: " + str(e), exc_info=self.verbose)
                return
        else:
            self.driver.get(url_list[0])
            self.manual_login(man_login_url)

        logger.info("Running batch download of courses ")
        for url in url_list:
            try:
                self.pick_course_downloader(url)
            except Exception as e:
                logger.error("Could not download course: " + url + " cause: " + str(e))

    def pick_course_downloader(self, course_url):
        # Check if we are already on the course page
        if self.driver.current_url != course_url:
            logger.info("Switching to course page")
            self.driver.get(course_url)
            self.bypass_cloudflare_if_present()

        WebDriverWait(self.driver, timeout=self.global_timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # https://support.teachable.com/hc/en-us/articles/360058715732-Course-Design-Templates
        logger.info("Picking course downloader")
        if self.driver.find_elements(By.ID, "__next"):
            logger.info("Choosing __next format")
            self.download_course_simple(course_url)
        elif self.driver.find_elements(By.CLASS_NAME, "course-mainbar"):
            logger.info("Choosing course-mainbar format")
            self.download_course_classic(course_url)
        elif self.driver.find_elements(By.CSS_SELECTOR, ".block__curriculum"):
            logger.info("Choosing .block__curriculum format")
            self.download_course_colossal(course_url)
        else:
            logger.error(
                "Downloader does not support this course template. Please open an issue on github."
            )
            return

    def download_course_colossal(self, course_url):
        logger.info("Detected block course format")
        course_title = self.get_course_title(
            course_url, By.CSS_SELECTOR, ".course__title"
        )
        course_path = create_folder(course_title)

        self.save_course_html(course_path)

        # Unhide all elements
        logger.info("Unhiding all elements")
        self.driver.execute_script(
            '[...document.querySelectorAll(".hidden")].map(e=>e.classList.remove("hidden"))'
        )

        chapter_idx = 1
        video_list = []
        wait = WebDriverWait(self.driver, timeout=self.global_timeout)
        sections = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".block__curriculum__section")
            )
        )
        for section in sections:
            chapter_title = section.find_element(
                By.CSS_SELECTOR, ".block__curriculum__section__title"
            ).text
            chapter_title = clean_string(chapter_title)
            chapter_title = f"{chapter_idx:02d}-{chapter_title}"
            logger.info("Found chapter: " + chapter_title)

            download_path = os.path.join(course_path, chapter_title)
            os.makedirs(download_path, exist_ok=True)

            chapter_idx += 1
            idx = 1

            section_items = section.find_elements(
                By.CSS_SELECTOR, ".block__curriculum__section__list__item__link"
            )
            for item in section_items:
                lecture_link = item.get_attribute("href")
                lecture_title = item.find_element(
                    By.CSS_SELECTOR,
                    ".block__curriculum__section__list__item__lecture-name",
                ).text
                lecture_title = clean_string(lecture_title)
                lecture_title = "".join(
                    char for char in lecture_title if char in string.printable
                )
                logger.info("Found lecture: " + lecture_title)

                truncated_lecture_title = truncate_title_to_fit_filename(lecture_title)
                video_entity = {
                    "link": lecture_link,
                    "title": truncated_lecture_title,
                    "download_path": download_path,
                    "idx": idx,
                }
                video_list.append(video_entity)
                idx += 1

        self.download_videos_from_links(video_list)

    def download_course_classic(self, course_url):
        logger.info("Detected _mainbar course format")
        course_title = self.get_course_title(
            course_url,
            By.CSS_SELECTOR,
            "body > section > div.course-sidebar > div > h2",
        )
        course_path = create_folder(course_title)

        self.save_course_html(course_path)
        self.get_course_image(course_path, By.CLASS_NAME, "course-image")

        chapter_idx = 1
        video_list = []
        sections = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".course-section"))
        )
        for section in sections:
            chapter_title = section.find_element(By.CSS_SELECTOR, ".section-title").text
            chapter_title = clean_string(chapter_title)
            chapter_title = f"{chapter_idx:02d}-{chapter_title}"
            logger.info("Found chapter: " + chapter_title)

            download_path = os.path.join(course_path, chapter_title)
            os.makedirs(download_path, exist_ok=True)

            chapter_idx += 1
            idx = 1

            section_items = section.find_elements(By.CSS_SELECTOR, ".section-item")
            for item in section_items:
                lecture_link = item.find_element(By.CLASS_NAME, "item").get_attribute(
                    "href"
                )
                lecture_title = item.find_element(By.CLASS_NAME, "lecture-name").text
                lecture_title = clean_string(lecture_title)
                logger.info("Found lecture: " + lecture_title)

                truncated_lecture_title = truncate_title_to_fit_filename(lecture_title)

                video_entity = {
                    "link": lecture_link,
                    "title": truncated_lecture_title,
                    "download_path": download_path,
                    "idx": idx,
                }
                video_list.append(video_entity)
                idx += 1

        self.download_videos_from_links(video_list)

    def download_course_simple(self, course_url):
        self.driver.implicitly_wait(2)
        logger.info("Detected next course format")
        course_title = self.get_course_title_simple(course_url)
        course_path = create_folder(course_title)

        self.save_course_html(course_path)
        self.get_course_image(
            course_path, By.XPATH, '//*[@id="__next"]/div/div/div[2]/div/div[1]/img'
        )

        chapter_idx = 0
        video_list = []
        slim_sections = self.driver.find_elements(By.CSS_SELECTOR, ".slim-section")
        for section in slim_sections:
            chapter_idx += 1
            bars = section.find_elements(By.CSS_SELECTOR, ".bar")
            chapter_title = section.find_element(By.CSS_SELECTOR, ".heading").text
            chapter_title = clean_string(chapter_title)
            chapter_title = f"{chapter_idx:02d}-{chapter_title}"
            logger.info("Found chapter: " + chapter_title)

            try:
                WebDriverWait(section, self.global_timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".drip-tag"))
                )
                logger.warning('Chapter "%s" not available, skipping', chapter_title)
                continue
            except TimeoutException:
                logger.info("Chapter is available")
                # Element wasn't found so the chapter is available

            download_path = os.path.join(course_path, chapter_title)
            os.makedirs(download_path, exist_ok=True)

            idx = 1
            for bar in bars:
                video = bar.find_element(By.CSS_SELECTOR, ".text")
                link = video.get_attribute("href")
                # Remove new line characters from the title and replace spaces with -
                title = clean_string(video.text)
                logger.info("Found lecture: " + title)
                truncated_title = truncate_title_to_fit_filename(title)
                video_entity = {
                    "link": link,
                    "title": truncated_title,
                    "download_path": download_path,
                    "idx": idx,
                }
                video_list.append(video_entity)
                idx += 1

        self.download_videos_from_links(video_list)

    def get_course_title(self, course_url, by, selector):
        if self.driver.current_url != course_url:
            self.driver.get(course_url)
        try:
            logger.info("Getting course title")
            course_title = (
                WebDriverWait(self.driver, self.global_timeout)
                .until(EC.presence_of_element_located((by, selector)))
                .text
            )
        except Exception:
            logger.warning("Could not get course title, using tab title instead")
            course_title = self.driver.title
        return clean_string(course_title)

    def get_course_title_simple(self, course_url):
        if self.driver.current_url != course_url:
            self.driver.get(course_url)
        WebDriverWait(self.driver, self.global_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".wrap"))
        )
        heading = WebDriverWait(self.driver, self.global_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".heading"))
        )
        course_title = heading.text
        return clean_string(course_title)

    def save_course_image(self, course_path, image_src):
        try:
            response = requests.get(image_src, timeout=30)
        except Exception as e:
            logger.warning("Could not download course image: " + str(e))
            return False

        if not response.ok:
            logger.warning("Failed to download image.")
            return False

        # save the image to disk
        image_path = os.path.join(course_path, "course-image.jpg")
        with open(image_path, "wb") as f:
            f.write(response.content)
        logger.info("Image downloaded successfully.")
        return True

    def get_course_image(self, course_path, by, selector):
        image_element = self.driver.find_elements(by, selector)

        if not image_element:
            logger.warning("No course image element found")
            return

        try:
            logger.info("Found course image")
            image_src = image_element[0].get_attribute("src")
            # Try the high-definition version first, falling back to the
            # original link if that fails for any reason.
            image_src_hd = re.sub(r"/resize=.+?/", "/", image_src)
            if self.save_course_image(course_path, image_src_hd):
                return
            self.save_course_image(course_path, image_src)
        except Exception as e:
            logger.warning("Could not find course image: " + str(e))

    def save_course_html(self, course_path):
        try:
            logger.debug("Saving course html")
            output_file = os.path.join(course_path, "course.html")
            with open(output_file, "w+", encoding="utf-8") as f:
                f.write(self.driver.page_source)
        except Exception as e:
            logger.error("Could not save course html: " + str(e), exc_info=self.verbose)

    def download_videos_from_links(self, video_list):
        for video in video_list:
            link = video["link"]
            title = video["title"]
            download_path = video["download_path"]
            idx = video["idx"]

            if self.driver.current_url != link:
                logger.info("Navigating to lecture: " + title)
                self.driver.get(link)
                self.driver.implicitly_wait(self.global_timeout)
            logger.info("Downloading lecture: " + title)

            try:
                logger.info("Saving html")
                self.save_webpage_as_html(title, idx, download_path)
            except Exception as e:
                logger.error(
                    "Could not save html: " + title + " cause: " + str(e),
                    exc_info=self.verbose,
                )

            try:
                logger.info("Downloading attachments")
                self.download_attachments(link, title, idx, download_path)
            except Exception as e:
                logger.warning(
                    "Could not download attachments: " + title + " cause: " + str(e)
                )

            try:
                logger.debug("Trying to download video as an attachment")
                if self.download_video_file(title, idx, download_path):
                    continue
            except Exception as e:
                logger.debug(
                    "Could not download video as an attachment: "
                    + title
                    + " cause: "
                    + str(e)
                )

            video_iframes = self.driver.find_elements(
                By.XPATH, "//iframe[starts-with(@data-testid, 'embed-player')]"
            )

            for i, iframe in enumerate(video_iframes):
                try:
                    logger.info("Switching to video frame")
                    self.driver.switch_to.frame(iframe)

                    script_text = self.driver.find_element(By.ID, "__NEXT_DATA__")
                    json_text = json.loads(script_text.get_attribute("innerHTML"))
                    url_encrypted = json_text["props"]["pageProps"]["applicationData"][
                        "mediaAssets"
                    ][0]["urlEncrypted"]

                    # Append -n to the video title if there are multiple iframes
                    video_title = title + (
                        "-" + str(i + 1) if len(video_iframes) > 1 else ""
                    )

                    try:
                        logger.info("Downloading subtitle")
                        self.download_subtitle(
                            url_encrypted, video_title, idx, download_path
                        )
                    except Exception as e:
                        logger.warning(
                            "Could not download subtitle: "
                            + video_title
                            + " cause: "
                            + str(e)
                        )

                    try:
                        logger.info("Downloading video")
                        self.download_video(
                            url_encrypted, video_title, idx, download_path
                        )
                    except Exception as e:
                        logger.warning(
                            "Could not download video: "
                            + video_title
                            + " cause: "
                            + str(e)
                        )

                    self.driver.switch_to.default_content()  # Switch back to main content before the next iteration

                except Exception:
                    logger.warning("Could not find video: " + title)
                    continue

            logger.info("Downloaded video: " + title)

            if self._complete_lecture:
                try:
                    logger.info("Completing lecture")
                    self.complete_lecture()
                except Exception as e:
                    logger.warning(
                        "Could not complete lecture: "
                        + video["title"]
                        + " cause: "
                        + str(e)
                    )

    def save_webpage_as_html(self, title, video_index, output_path):
        output_file = os.path.join(output_path, f"{video_index:02d}-{title}.html")
        with open(output_file, "w+", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        logger.info("Saved webpage as html: " + output_file)

    def download_attachments(self, link, title, video_index, output_path):
        video_title = f"{video_index:02d}-{title}"

        # Grab the video attachments type file
        video_attachments = self.driver.find_elements(
            By.CLASS_NAME, "lecture-attachment-type-file"
        )
        if video_attachments:
            # Get all links from the video attachments
            video_links = video_attachments[0].find_elements(By.TAG_NAME, "a")
            output_path = os.path.join(output_path, video_title)
            os.makedirs(output_path, exist_ok=True)

            # Get href attribute from the first link
            if video_links:
                for video_link in video_links:
                    link = video_link.get_attribute("href")
                    filename = video_link.text
                    logger.info(
                        "Downloading attachment: " + filename + " for video: " + title
                    )
                    # Download file and save the file in output_path directory
                    wget.download(link, out=output_path)
        else:
            logger.warning("No attachments found for video: " + title)

    def download_video_file(self, title, video_index, output_path, timeout=60):
        video_title = f"{video_index:02d}-{title}"

        # Grab the video attachments type video
        video_attachment = self.driver.find_element(
            By.CLASS_NAME, "lecture-attachment-type-video"
        )
        if not video_attachment:
            logger.debug(f"No video attachment found for lecture: {title}")
            return False

        video_link = video_attachment.find_element(By.TAG_NAME, "a")
        if not video_link:
            logger.debug(f"No video link found for lecture: {title}")
            return False

        # Set the download directory for this file
        self.driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {
                "behavior": "allow",
                "downloadPath": output_path,
            },
        )
        # Get list of files before download
        files_before_download = set(os.listdir(output_path))

        # Click the link to trigger download
        video_link.click()

        # Wait for download to complete
        start_time = time.time()
        while True:
            files_after_download = set(os.listdir(output_path))

            # Find new files
            new_files = files_after_download - files_before_download

            if len(new_files) > 0 and all(
                os.path.splitext(f)[1] != ".crdownload" for f in new_files
            ):
                break

            if timeout > 0 and (time.time() - start_time) > timeout:
                logger.warning(f"Download timeout for lecture: {title}")
                return False

            time.sleep(1)

        latest_file = os.path.join(output_path, next(iter(new_files)))

        # Determine the file extension
        _, extension = os.path.splitext(latest_file)

        # Create the new filename
        new_filename = f"{video_title}{extension}"
        new_filepath = os.path.join(output_path, new_filename)

        # Rename the file
        os.rename(latest_file, new_filepath)
        logger.info(f"Downloaded video file {new_filename}")
        return True

    # This function is needed because yt-dlp subtitle downloader is not working
    def download_subtitle(self, link, title, video_index, output_path):
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4",
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                },
                {
                    "key": "FFmpegMetadata",
                },
            ],
            "http_headers": self.headers,
            "allsubtitles": True,
            "subtitleslangs": ["all"],
            "concurrentfragments": 10,
            "writesubtitles": True,
            "outtmpl": os.path.join(output_path, title),
            "verbose": self.verbose,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                info_json = ydl.sanitize_info(info)
        except Exception as e:
            logger.warning(
                "Could not download subtitle: " + title + " cause: " + str(e)
            )
            return

        subtitle_links = {}
        for lang, sub_info in info_json["requested_subtitles"].items():
            subtitle_links[lang] = {
                "url": sub_info["url"],
                "ext": sub_info["ext"],
            }

        # Print the subtitle links and language names
        for lang, sub in subtitle_links.items():
            subtitle_filename = "{:02d}-{}.{}.{}".format(
                video_index, title, lang, sub["ext"]
            )
            file_path = os.path.join(output_path, subtitle_filename)
            if os.path.isfile(file_path):
                logger.info("Skipping existing subtitle: " + subtitle_filename)
            else:
                base_url = sub["url"]
                try:
                    req = requests.get(sub["url"], headers=self.headers, timeout=30)
                except Exception as e:
                    logger.warning(
                        "Could not download subtitle: " + title + " cause: " + str(e)
                    )
                    continue

                relative_path = req.text.split("\n")[5]
                full_url = urljoin(base_url, relative_path)
                try:
                    response = requests.get(full_url, headers=self.headers, timeout=30)
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                except Exception as e:
                    logger.warning(
                        "Could not download subtitle: " + title + " cause: " + str(e)
                    )
                    continue

                logger.info("Downloaded subtitle: " + subtitle_filename)

    def download_video(self, link, title, video_index, output_path):
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4",
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                },
                {
                    "key": "FFmpegMetadata",
                },
            ],
            "http_headers": self.headers,
            "concurrentfragments": 15,
            "outtmpl": os.path.join(output_path, f"{video_index:02d}-{title}.mp4"),
            "verbose": self.verbose,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        except Exception as e:
            logger.error("Could not download video: " + title + " cause: " + str(e))

    def complete_lecture(self):
        self.driver.switch_to.default_content()
        complete_button = self.driver.find_element(By.ID, "lecture_complete_button")
        if complete_button:
            logger.info("Found complete button")
            complete_button.click()
            logger.info("Completed lecture")
            time.sleep(3)

    def cleanup(self):
        logger.info("Cleaning up")
        self.driver.quit()
        # Delete cookies.txt
        if os.path.exists("cookies.txt"):
            os.remove("cookies.txt")
