<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/FallingLights/Teachable-Dl">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Teachable-dl</h3>

  <p align="center">
    A downloader for downloading courses from the Teachable platforms.
    <br />
    <br />
    <a href="https://github.com/FallingLights/Teachable-Dl/issues">Report Bug</a>
    ·
    <a href="https://github.com/FallingLights/Teachable-Dl/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<!--[![Product Name Screen Shot][product-screenshot]](https://example.com) -->

Teachable-dl is a Python-based downloader for downloading courses from the Teachable platform. It provides a command-line interface for easily downloading course materials such as videos, slides, and other resources, allowing users to access course content offline at their own pace. With Teachable-dl, users can conveniently download and organize all course materials in a single location, enabling easy access and review of course content without the need for an active internet connection.

⭐ `Star` this repository if you find it valuable and worth maintaining.

👁 `Watch` this repository to get notified about new releases, issues, etc.
<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python.org]][Python-url]
* [![Selenium][Selenium.org]][Selenium-url]
* [![yt-dlp][yt-dlp.org]][yt-dlp-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get the program up and running follow these simple steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
(You can also run this script on a windows machine)
* yt-dlp
    ```sh
  python3 -m pip install -U yt-dlp
    ```
* ffmpeg
    ```sh
    sudo apt install ffmpeg
    ```
* wget
    ```sh
    sudo apt install wget
    ```
* Chrome
    ```sh
    sudo apt install chromium-browser
    ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/FallingLights/Teachable-Dl.git
   ```
2. Set up the environment
   ```sh
    python3 -m venv env
   ```
3. Activate the environment
   ```sh
    source env/bin/activate
   ```
4. Install the requirements
   ```sh
    pip install -r requirements.txt
   ```


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Run the program
```sh
source env/bin/activate
python3 main.py --url <course_url> --email <email> --password <password>
```



<!-- ROADMAP -->
## Roadmap

- [x] Add support for downloading course materials from new Teachable template
- [ ] Add support for downloading all courses from a Teachable site

See the [open issues](https://github.com/FallingLights/Teachable-Dl/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the GNU LGPLv3 License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Your Name - [@fallinglight_s](https://twitter.com/fallinglight_s)

Project Link: [https://github.com/FallingLights/Teachable-Dl](https://github.com/FallingLights/Teachable-Dl)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [merberich](https://github.com/merberich)
* [Green0Photon](https://github.com/Green0Photon)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/FallingLights/Teachable-Dl.svg?style=for-the-badge
[contributors-url]: https://github.com/FallingLights/Teachable-Dl/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/FallingLights/Teachable-Dl.svg?style=for-the-badge
[forks-url]: https://github.com/FallingLights/Teachable-Dl/network/members
[stars-shield]: https://img.shields.io/github/stars/FallingLights/Teachable-Dl.svg?style=for-the-badge
[stars-url]: https://github.com/FallingLights/Teachable-Dl/stargazers
[issues-shield]: https://img.shields.io/github/issues/FallingLights/Teachable-Dl.svg?style=for-the-badge
[issues-url]: https://github.com/FallingLights/Teachable-Dl/issues
[license-shield]: https://img.shields.io/github/license/FallingLights/Teachable-Dl.svg?style=for-the-badge
[license-url]: https://github.com/FallingLights/Teachable-Dl/blob/master/LICENSE.txt
[product-screenshot]: images/screenshot.png
[Python.org]: https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org
[Selenium.org]: https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white
[Selenium-url]: https://www.selenium.dev
[yt-dlp.org]: https://img.shields.io/badge/yt--dlp-000000?style=for-the-badge&logo=github&logoColor=white
[yt-dlp-url]: https://github.com/yt-dlp/yt-dlp
