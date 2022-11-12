from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import datetime
import math
import boto3
import os


class FacebookPoster:
    def __init__(self, login: str, password: str):

        # For facebook login id credentials
        self.login = login

        # For facebook login password credentials
        self.password = password

        # Facebook page url
        self.base_url = "https://www.facebook.com/"

        # Setup Selenium Options
        # Add binary location for Firefox which is mandatory
        # Headless mode on
        options = Options()
        options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        # options.add_argument("--headless")

        # Setup Firefox driver
        self.driver = Firefox(
            service=Service(GeckoDriverManager().install()),
            options=options,
        )

        # Setup Selenium action chain
        self.action = ActionChains(self.driver)

        # By default, is set to 5,
        # will be used by time patterns
        self.time_pattern = 5  # seconds

        # Run function to retrive or make cookie for Facebook session
        self._login_to_facebook()

    @staticmethod
    def get_txt(filename):
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()
        return content

    @staticmethod
    def get_img_from_aws(img_name: str, bucket_name: str):
        s3 = boto3.resource("s3")
        s3.meta.client.download_file(bucket_name, img_name, "copy.jpg")
        dir_path = os.path.dirname(os.path.realpath("copy.jpg"))
        return dir_path + r"\copy.jpg"

    @staticmethod
    def get_txt_from_aws(txt_name: str, bucket_name: str):
        s3 = boto3.resource("s3")
        s3.meta.client.download_file(bucket_name, txt_name, "content.txt")
        return "content.txt"

    def _login_to_facebook(self):
        # This function is to log into Facebook

        self.driver.get(self.base_url)
        self.driver.find_element(
            By.XPATH,
            "//button[text()='Zezwól na korzystanie z niezbędnych i opcjonalnych plików cookie']",
        ).click()

        # For pausing the script for sometime
        self._time_patterns(3)

        self.driver.find_element(By.ID, "email").send_keys(self.login)
        self.driver.find_element(By.ID, "pass").send_keys(self.password)

        # For pausing the script for sometime
        self._time_patterns(3)

        self.driver.find_element(By.XPATH, "//button[text()='Zaloguj się']").click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "facebook"))
        )

    def _time_patterns(self, tp=None):
        # This function is to pause the script for some time
        # Also takes argument as second,
        # If not given then it will
        # Take by default seconds to wait
        if tp is None:
            time.sleep(self.time_pattern)

        else:
            self.time_pattern = tp
            time.sleep(self.time_pattern)

    def prepare_and_send_post(self, txt_name: str, bucket_name: str, img_name: str):
        # This function is to post content on Facebook group

        # Load imgage from s3 AWS
        image = self.get_img_from_aws(img_name=img_name, bucket_name=bucket_name)

        # Load txt_file from s3 AWS
        content_filename = self.get_txt_from_aws(
            txt_name=txt_name, bucket_name=bucket_name
        )

        # JS scripts to load images to post
        JS_DROP_FILE = """
            var target = arguments[0],
                offsetX = arguments[1],
                offsetY = arguments[2],
                document = target.ownerDocument || document,
                window = document.defaultView || window;

            var input = document.createElement('INPUT');
            input.type = 'file';
            input.onchange = function () {
              var rect = target.getBoundingClientRect(),
                  x = rect.left + (offsetX || (rect.width >> 1)),
                  y = rect.top + (offsetY || (rect.height >> 1)),
                  dataTransfer = { files: this.files };

              ['dragenter', 'dragover', 'drop'].forEach(function (name) {
                var evt = document.createEvent('MouseEvent');
                evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
                evt.dataTransfer = dataTransfer;
                target.dispatchEvent(evt);
              });

              setTimeout(function () { document.body.removeChild(input); }, 25);
            };
            document.body.appendChild(input);
            return input;
        """

        # Load list of Facebook groups
        fb_groups = [
            "https://www.facebook.com/groups/pracawlodzkim/",
            "https://www.facebook.com/groups/1752579184959123/",
            "https://www.facebook.com/groups/960366354163646/",
        ]

        # Itarate through groups
        start_t = time.time()
        print(f"/// START PROCESS {datetime.datetime.now()}")
        for group in fb_groups:

            # Load content from file
            content = self.get_txt(content_filename)

            try:
                # Open Facebook group url
                self.driver.get(group + "buy_sell_discussion")
                print(f"/// Start processing group: {group + 'buy_sell_discussion'}")

                # For pausing the script for sometime
                self._time_patterns(8)

                # Locate postbox element and click it
                self.driver.find_element(
                    By.XPATH,
                    "//div[@class='xi81zsa x1lkfr7t xkjl1po x1mzt3pk xh8yej3 x13faqbe']",
                ).click()

                # For pausing the script for sometime
                self._time_patterns(3)

                # Activate postbox pop up to send value to it
                element = self.driver.switch_to.active_element

                # Spilit content by newline symbol to dict
                content = content.split("\n")

                # Iterate through content
                for con in content:

                    # Make first paragraph bold
                    # Check if 1-st itarate element is 1-st element from content dict
                    if con == content[0]:

                        # Send value and then by action chain make it bold
                        element.send_keys(con)

                        # First using CTRL + A to select whole text and
                        # Then using CTRL + B to bold it
                        # Then using SHIFT + ENTER to make newline
                        self.action.key_down(Keys.CONTROL).send_keys("a").key_down(
                            Keys.CONTROL
                        ).send_keys("b").key_down(Keys.DOWN).key_down(
                            Keys.SHIFT
                        ).key_down(
                            Keys.ENTER
                        ).perform()

                        # Reste action chain
                        self.action.reset_actions()

                        # Then deactivate bold format
                        self.action.key_down(Keys.CONTROL).send_keys("b").perform()

                        # For pausing the script for sometime
                        self._time_patterns(3)

                    # Check if itarate element has colon symbol
                    # If so bold the paragraph before colon
                    elif ":" in con:
                        con = con.split(":")
                        self.action.key_down(Keys.CONTROL).send_keys("b").perform()
                        self.action.reset_actions()
                        element.send_keys(con[0] + ":")
                        self.action.send_keys(Keys.SPACE).key_down(
                            Keys.CONTROL
                        ).send_keys("b").perform()
                        self.action.reset_actions()
                        element.send_keys(con[1])
                        self.action.key_down(Keys.SHIFT).key_down(Keys.ENTER).perform()
                        self.action.reset_actions()

                    # Check if itarate element has question mark
                    # If so bold the paragraph before colon
                    elif "?" in con:
                        con = con.split("?")
                        self.action.key_down(Keys.CONTROL).send_keys("b").perform()
                        self.action.reset_actions()
                        element.send_keys(con[0] + "?")
                        self.action.send_keys(Keys.SPACE).key_down(
                            Keys.CONTROL
                        ).send_keys("b").perform()
                        self.action.reset_actions()
                        element.send_keys(con[1])
                        self.action.key_down(Keys.SHIFT).key_down(Keys.ENTER).perform()
                        self.action.reset_actions()

                    # If none of the above just send text
                    else:
                        element.send_keys(con)
                        self.action.key_down(Keys.SHIFT).key_down(Keys.ENTER).perform()
                        self.action.reset_actions()

                # For pausing the script for sometime
                self._time_patterns(5)

                # Add images to post
                driver = element.parent
                file_input = driver.execute_script(JS_DROP_FILE, element, 0, 0)
                file_input.send_keys(image)
                # For pausing the script for sometime
                self._time_patterns()

                # click post btn
                self.driver.find_element(
                    By.XPATH, "//div[@aria-label='Opublikuj']"
                ).click()

                # For pausing the script for sometime
                self._time_patterns(10)
                print(f"/// End processing group: {group + 'buy_sell_discussion'}\n")

            except Exception as e:
                print(
                    f"/// Problem with processing group: {group + 'buy_sell_discussion'}\nError: {e}"
                )

        # delete tmp file
        os.remove("copy.jpg")
        os.remove("content.txt")

        duration_t = time.time() - start_t
        print(f"/// END PROCESS {datetime.datetime.now()}")
        print(f"/// Duration time: {math.ceil(duration_t / 60)}")
