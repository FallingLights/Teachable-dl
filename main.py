from time import sleep

from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc


driver = uc.Chrome()

driver.get("https://courses.iamtimcorey.com/p/web-api-from-start-to-finish")

driver.find_element(By.LINK_TEXT, "Login").click()

# Wait for the login form to appear
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "email"))
)

email = driver.find_element(By.ID, "email")
password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
commit = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "commit")))

email.click()
email.clear()

# Create an instance of ActionChains
actions = ActionChains(driver)

# Send the email address using actions chain
actions.send_keys("vrtacnik.tim")
actions.send_keys("@")
actions.send_keys("gmail.com")
actions.perform()

password.click()
password.clear()
password.send_keys("!SEK6P#wN#dEucpHg")

commit.click()


sleep(200)
