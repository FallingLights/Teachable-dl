import base64
import os
import sys

import wget
from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc
import yt_dlp
import json
from urllib.parse import urljoin
import requests
import argparse


class TeachableDownloader:
    def __init__(self):
        self.chrome_options = uc.ChromeOptions()
        self.driver = uc.Chrome(options=self.chrome_options)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "Origin": "https://player.hotmart.com"
        }
        self.verbose = False

    def run(self, course_url, email, password):
        try:
            self.login(course_url, email, password)
        except Exception as e:
            print("Could not login: " + str(e))
            return

        try:
            self.pick_course_downloader(course_url)
        except Exception as e:
            print("Could not download course: " + course_url + " cause: " + str(e))

    def login(self, course_url, email, password):
        self.driver.get(course_url)
        self.driver.implicitly_wait(20)

        login_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.LINK_TEXT, "Login")))
        login_element.click()

        email_element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "email")))
        password_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        commit_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "commit")))

        email_element.click()
        email_element.clear()
        self.driver.execute_script("document.getElementById('email').value='" + email + "'")

        password_element.click()
        password_element.clear()
        self.driver.execute_script("document.getElementById('password').value='" + password + "'")

        commit_element.click()

        self.driver.implicitly_wait(30)
        self.driver.get(course_url)

    def get_course_title(self, course_url):
        if self.driver.current_url != course_url:
            self.driver.get(course_url)

        wrap = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".wrap")))
        heading = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".heading")))
        course_title = heading.text

        course_title = course_title.replace("\n", "-").replace(" ", "-").replace(":", "-")
        return course_title

    def pick_course_downloader(self, course_url):
        self.driver.get(course_url)
        self.driver.implicitly_wait(20)

        old = self.driver.find_elements(By.ID, "__next")
        if old:
            self.download_course_old(course_url)
        else:
            print("Not implemented yet!")

    def download_course_old(self, course_url):
        root_path = os.path.abspath(os.getcwd())
        course_title = self.get_course_title(course_url)
        course_path = os.path.join(root_path, "courses", course_title)
        os.makedirs(course_path, exist_ok=True)

        chapter_idx = 1
        video_list = []
        slim_sections = self.driver.find_elements(By.CSS_SELECTOR, ".slim-section")
        for slim_section in slim_sections:
            bars = slim_section.find_elements(By.CSS_SELECTOR, ".bar")
            chapter_title = slim_section.find_element(By.CSS_SELECTOR, ".heading").text
            chapter_title = chapter_title.replace("\n", "-").replace(" ", "-").replace(":", "-")
            chapter_title = str(chapter_idx) + "-" + chapter_title
            print(chapter_title)
            download_path = os.path.join(course_path, chapter_title)
            os.makedirs(download_path, exist_ok=True)
            chapter_idx += 1
            idx = 1
            for bar in bars:

                video = bar.find_element(By.CSS_SELECTOR, ".text")
                link = video.get_attribute("href")
                title = video.text
                # Remove new line characters from the title and replace spaces with -
                title = title.replace("\n", "-").replace(" ", "-").replace(":", "-")
                video_entity = {"link": link, "title": title, "idx": idx, "download_path": download_path}
                video_list.append(video_entity)
                idx += 1

        for video in video_list:
            self.driver.get(video["link"])
            self.driver.implicitly_wait(10)

            try:
                self.download_attachments(video["link"], video["title"], video["idx"], video["download_path"])
            except Exception as e:
                print("Could not download attachments: " + video["title"] + " cause: " + str(e))

            WebDriverWait(self.driver, timeout=10).until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.XPATH, "//iframe[starts-with(@data-testid, 'embed-player')]"))
            )

            script_text = self.driver.find_element(By.ID, "__NEXT_DATA__")
            json_text = json.loads(script_text.get_attribute("innerHTML"))
            link = json_text["props"]["pageProps"]["applicationData"]["mediaAssets"][0]["urlEncrypted"]

            try:
                self.download_subtitle(link, video["title"], video["idx"], video["download_path"])
            except Exception as e:
                print("Could not download subtitle: " + video["title"] + " cause: " + str(e))

            try:
                self.download_video(link, video["title"], video["idx"], video["download_path"])
            except Exception as e:
                print("Could not download video: " + video["title"] + " cause: " + str(e))

            print("Downloaded: " + video["title"])

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
            "concurrentfragments": 10,
            "outtmpl": os.path.join(output_path, str(video_index) + "-" + title + ".mp4"),
            "ffmpeg_location": "C:\\Users\\FallingLights\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-6.0-full_build\\bin\\ffmpeg.exe",
            "verbose": self.verbose,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        except Exception as e:
            print("Could not download video: " + title + " cause: " + str(e))

    # This function is needed because yt-dlp subtitile downloader is not working
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
            "ffmpeg_location": "C:\\Users\\FallingLights\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan"
                               ".FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-6.0-full_build\\bin\\ffmpeg.exe",
            "verbose": self.verbose,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                info_json = ydl.sanitize_info(info)
        except Exception as e:
            print("Could not download subtitle: " + title + " cause: " + str(e))

        subtitle_links = {}
        for lang, sub_info in info_json["requested_subtitles"].items():
            subtitle_links[lang] = {"url": sub_info["url"], "ext": sub_info["ext"]}

        # Print the subtitle links and language names
        for lang, sub in subtitle_links.items():
            base_url = sub["url"]
            try:
                req = requests.get(sub["url"], headers=self.headers)
            except Exception as e:
                print("Could not download subtitle: " + title + " cause: " + str(e))
            relative_path = req.text.split("\n")[5]
            full_url = urljoin(base_url, relative_path)
            subtitle_filename = str(video_index) + "-" + title + "." + lang + "." + sub["ext"]
            file_path = os.path.join(output_path, subtitle_filename)
            try:
                response = requests.get(full_url, headers=self.headers)
                with open(file_path, "wb") as f:
                    f.write(response.content)
            except Exception as e:
                print("Could not download subtitle: " + title + " cause: " + str(e))

    def download_attachments(self, link, title, video_index, output_path):
        video_title = str(video_index) + "-" + title

        # Grab the video attachments type file
        video_attachments = self.driver.find_elements(By.CLASS_NAME, "lecture-attachment-type-file")
        # Get all links from the video attachments

        if video_attachments:
            video_links = video_attachments[0].find_elements(By.TAG_NAME, "a")

            output_path = os.path.join(output_path, video_title)
            os.makedirs(output_path, exist_ok=True)

            # Get href attribute from the first link
            if video_links:
                for video_link in video_links:
                    link = video_link.get_attribute("href")
                    file_name = video_link.text
                    print(link, file_name)
                    # Download file and save the file in output_path directory
                    wget.download(link, out=output_path)
        else:
            print("No attachments found for video: " + title)

    def save_webpage(self, link, title, output_path):
        # Save the webpage as mhtml
        mhtml_filename = title + ".mhtml"
        mhtml_path = os.path.join(output_path, mhtml_filename)
        self.driver.execute_cdp_cmd(
            "Page.captureSnapshot", {"format": "mhtml", "quality": 100}
        )
        with open(mhtml_path, "wb") as f:
            f.write(base64.b64decode(self.driver.page_source))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download subtitles from URL')
    parser.add_argument("--url", help='URL of the course')
    parser.add_argument("--email", required=True, help='Email of the account')
    parser.add_argument("--password", required=True, help='Password of the account')
    # parser.add_argument('-o', '--output', help='Output directory for the downloaded subtitle', default='.')
    args = parser.parse_args()

    downloader = TeachableDownloader()
    try:
        downloader.run(args.url, args.email, args.password)
    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print("Error: " + str(e))
        sys.exit(1)
