import os
import time
import logging
import re
from io import StringIO, BytesIO
from PIL import Image
from random import randint, uniform
from collections import namedtuple
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import boto3
from dotenv import load_dotenv
from typing import Union
from .logger import create_logger

load_dotenv()

# Prepare namedtuple
Test_output = namedtuple("Test_output", ["selenium_element", "n_for_end_and_position"])

logger = create_logger(__name__, level=logging.INFO)


class FacebookPoster:
    """
    A class representing a bot for posting in groups on Facebook.
    """

    def __init__(self, login: str, password: str, groups: list):
        """
        Initializes the attributes of the class.
        :param login: str Facebook login id credentials
        :param password: str Facebook login password credentials
        :param groups: list Facebook groups list
        """

        # Facebook login id credentials
        self.login = login

        # Facebook login password credentials
        self.password = password

        # List with Facebook groups
        self.groups = groups

        # Facebook page url
        self.base_url = "https://www.facebook.com/"

        # Setup Selenium Options
        options = Options()

        options.add_argument("--disable-blink-features=AutomationControlled")

        # Add argument headless
        options.add_argument("--headless")

        # Setup Firefox driver
        self.driver = webdriver.Remote(
            command_executor="http://selenium-hub:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.FIREFOX,
            options=options,
        )
        # Setup Selenium action chain
        self.action = ActionChains(self.driver)

        # By default, is set to 5,
        # will be used by time patterns
        self.time_pattern = randint(3, 5)  # seconds

        # Bukcet name
        self.bucket_name = "heroku-fb-poster"

        # Dict with text format action
        self.text_formatting_action = {
            0: "b",  # bold text
            1: "i",  # italics text
            2: "h1",  # h1 format
            3: "h2",  # h2 format
            4: "quote",  # quote text
            5: "ul",  # unordered list
            6: "ol",  # ordered list
        }

        # Javascript code to add image
        self.js_code = """
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

    @staticmethod
    def get_txt(content: Union[bytes, str]) -> str:
        """
        Returns the content of a text file as a string.
        :param content: bytes or str, the content to be stored in a text file.
        :return: str, the content of the text file.
        """
        if isinstance(content, bytes):
            # Decode the bytes content using UTF-8 encoding
            content = content.decode("utf-8")
        elif not isinstance(content, str):
            # Raise an error if the content is not bytes or str
            raise TypeError("content must be bytes or str")

        # Create a file-like buffer to receive the content
        file = StringIO(content)

        # Return the content of the text file
        return file.read()

    @staticmethod
    def get_image(image: Union[str, bytes]) -> Image:
        """
        Return image object from the given image path or bytes content.
        :param image: str or bytes Image file path or bytes content
        :return: Image object
        """
        if isinstance(image, str):
            # Open image file using Image module from PIL library
            return Image.open(image)
        elif isinstance(image, bytes):
            # Open image using BytesIO and Image module from PIL library
            return Image.open(BytesIO(image))
        else:
            # Raise an error if the content is not str or bytes
            raise TypeError(f"image must be str or bytes - it's {type(image)}")

    @staticmethod
    def _scroll_feed(driver, iterations):
        i = 0
        while i < iterations:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);", 2000
            )

            # Scroll down for 6 to 15 sec
            time.sleep(uniform(6, 15))

            # Stop for 3 to 5 sec
            time.sleep(uniform(3, 5))
            i += 1

    @staticmethod
    def get_from_aws(file_name: str, bucket_name: str):
        """
        This method retrieves the content of a file stored on AWS S3 bucket.
        :param file_name: str - name of the file in the S3 bucket
        :param bucket_name: str - name of the S3 bucket
        :return: str - content of the file
        """
        # retrieve access and secret key from environment variables
        access_key = os.environ.get("ACCESS_KEY")
        secret_key = os.environ.get("SECRET_KEY")

        # create a boto3 session using the access and secret key
        session = boto3.Session(
            aws_access_key_id=access_key, aws_secret_access_key=secret_key
        )
        # create an S3 resource using the session
        s3 = session.resource("s3")

        # create an S3 object to access the specified file in the specified bucket
        obj = s3.Object(bucket_name, file_name)
        # retrieve the content of the file and decode it as utf-8
        content = obj.get()["Body"].read()

        # return the content of the file
        return content

    def create_selenium_object_for_testing(self, content, direction=None):
        """
        Creates a Selenium web element that can be used for testing the 'move_cursor' method.
        :param content: The content to be added to the web element
        :param direction: The initial position of the cursor. Can be 'start', 'end' or 'position'.
        :return: Selenium web element with the added content and cursor at the specified position
        """
        n_for_end_and_position = None

        # Check if the provided direction is valid
        if direction not in ["start", "end", "position"]:
            raise ValueError(
                "Invalid value for argument 'direction'. Expected 'start', 'end' or 'position'."
            )

        # Log into Facebook
        self._login_to_facebook(human_simulation=True)
        self._time_patterns()

        # Open 1-st group from list
        self.driver.get(self.groups[0] + "buy_sell_discussion")

        # For pausing the script for sometime
        self._time_patterns()

        # Locate postbox element and click it
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[@class='x6s0dn4 x78zum5 x1l90r2v x1pi30zi x1swvt13 xz9dl7a']",
                )
            )
        )
        element.click()

        # For pausing the script for sometime
        self._time_patterns()

        # Activate postbox pop up to send value to it
        postbox = self.driver.switch_to.active_element
        postbox.send_keys(content)

        # Get the number of characters in the content
        n = len(content)

        # Set the cursor position based on the provided direction
        if direction == "start":
            self.action.send_keys(Keys.LEFT * n).perform()
        elif direction == "position":
            self.action.send_keys(Keys.LEFT * n).perform()
            n_for_end_and_position = self.move_cursor(
                selenium_element=postbox, direction="start", content=content
            )
        else:
            self.action.send_keys(Keys.LEFT * n).perform()
            n_for_end_and_position = self.move_cursor(
                selenium_element=postbox, direction="start", content=content
            )
            self.action.send_keys(Keys.RIGHT * n).perform()

        return Test_output(postbox, n_for_end_and_position)

    def move_cursor(
        self,
        content: str,
        selenium_element,
        direction: str,
        position=None,
        to_move=None,
        n_for_end_and_position=None,
    ):
        """
        Move cursor to the specified position of the line.
        :param n_for_end_and_position:
        :param content: File path
        :param selenium_element: Location to web element we point with selenium
        :param direction: "start", "end" or "position"
        :param position: int or None (if direction is not "position")
        :param to_move: int or None (if direction is not "position" or position is not specified)
        :return: int
        """
        if direction not in ["start", "end", "position"]:
            raise ValueError(
                "Invalid value for argument 'direction'. Expected 'start', 'end' or 'position'."
            )

        if direction == "position" and (
            position is None or not isinstance(position, int)
        ):
            raise ValueError(
                "Invalid value for argument 'position'. Expected int or None."
            )

        if direction in ["end", "position"] and (
            n_for_end_and_position is None
            or not isinstance(n_for_end_and_position, int)
        ):
            raise ValueError(
                "Invalid value for argument 'n_for_end_and_position'. Expected int or None."
            )

        # Select three characters and set move key
        if direction == "start":
            self.action.key_down(Keys.SHIFT).send_keys(Keys.RIGHT * 3).perform()
            move_key = Keys.LEFT
        elif direction == "end":
            self.action.key_down(Keys.SHIFT).send_keys(Keys.LEFT * 3).perform()
            move_key = Keys.RIGHT
            n_to_move = len(content)
        else:
            self.action.send_keys(Keys.RIGHT * position)
            self.action.key_down(Keys.SHIFT).send_keys(Keys.LEFT * 3).perform()
            move_key = Keys.RIGHT
            n_to_move = to_move if to_move else position
        self.action.reset_actions()

        # For pausing the script for some time
        self._time_patterns()

        # Copy selected characters
        copied_text = self.driver.execute_script(
            "return window.getSelection().toString();"
        )

        # Unselect selected characters
        selenium_element.send_keys(move_key)

        # Calculate number of characters to move
        if direction == "position":
            # Subtract the position where the copied text is found in the content
            # from the desired cursor position, taking into account that 3 characters were copied
            n_to_move -= (
                content.find(copied_text, position - n_for_end_and_position - 3) + 3
            )

        elif direction == "end":
            # Subtract the position where the copied text is found in the content
            # from the desired cursor position, taking into account that 3 characters were copied
            n_to_move -= (
                content.find(copied_text, len(content) - n_for_end_and_position - 3) + 3
            )

        else:
            # Find the position where the copied text is found in the content
            n_to_move = content.find(copied_text)

        # For pausing the script for some time
        self._time_patterns()

        if direction != "position":
            # Move cursor to the specified position
            selenium_element.send_keys(move_key * n_to_move)
            self._time_patterns()

        return n_to_move

    def _login_to_facebook(self, human_simulation=True):
        """
        Log into Facebook.
        :param human_simulation: Simulate human-like behavior during the login process.
        :return: None
        """
        # Open Facebook at login page
        self.driver.get(self.base_url)

        # Close cookie popup
        cookie = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[@data-cookiebanner='accept_button']",
                )
            )
        )
        cookie.click()

        # For pausing the script for some time
        self._time_patterns()

        # Enter login and password
        login = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.ID, "email"))
        )
        login.send_keys(self.login)

        # For pausing the script for some time
        self._time_patterns()

        password = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.ID, "pass"))
        )
        password.send_keys(self.password)

        # For pausing the script for some time
        self._time_patterns()

        # Click login button
        login_button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[@class='_42ft _4jy0 _6lth _4jy6 _4jy1 selected _51sy']",
                )
            )
        )
        login_button.click()

        # Load FB start page
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, "facebook"))
        )

        logger.info("Logged in to Facebook successfully")

        # Scroll the feed by 3 units to simulate human-like behavior
        # if human_simulation:
        #     self._scroll_feed(self.driver, 3)

    def _time_patterns(self, tp=None):
        """
        Pause script for some time.
        :param tp: Time pattern in seconds
        :return:
        """

        # Check if time pattern is set as default
        if tp is None:
            time.sleep(self.time_pattern)

        # If not set time pattern as argument passed in function
        else:
            self.time_pattern = tp
            time.sleep(self.time_pattern)

    def bold_and_italic_formatting(
        self,
        content: str,
        content_without_tags: str,
        selenium_element,
        text_modify_butttons,
        n_for_end_and_position=None,
    ):
        """
        This function performs bolding and italicizing of text by determining the start and end index of the formatted
        text and assigning a method to it (0 for bold, 1 for italic).

        The function uses the "content" and "content_without_tags" variables to determine the starting and ending
        indices of the text to be formatted. The indices are then used to perform the formatting using the
        "selenium_element" and "text_modify_butttons

        :param content: a line of text with text formatting tags (e.g. <b>)
        :param content_without_tags: a line of text without text formatting tags
        :param selenium_element: a web element that we point to with selenium
        :param text_modify_butttons: a web element with text modifier buttons
        :param n_for_end_and_position: int or None (if direction is not "position" or position is not specified)
        :return: a tuple of two boolean values, which is necessary to switch off a Facebook glitch
        """
        # Split text into text content and text formatting tags
        splited_content = [x for x in re.split(r"<(.+?)>", content) if x != ""]

        # Initialize an empty list
        steps = list()

        # Initialize temporary variable temp_clean_text as content_without_tags
        temp_clean_text = content_without_tags

        # Initialize num as 0 - it will be simulated as the current text index
        num = 0

        # Iterate through splited_content to find the start and end indexes of text formatting tags
        tags = ["b", "i", "/i", "/b"]  # tags to look for
        for elem in splited_content:
            # If we encounter a bold or italic tag, create a list containing the start/end index and the text formatting
            # tag and add it to the steps list
            if elem in tags:
                steps.append([num, elem])

            # If the element is not a text formatting tag, check how many characters it has and add it to
            # the num variable.
            # Ignore empty strings that may be created by the regex split.
            elif elem in temp_clean_text and elem != " ":
                num_to_add = temp_clean_text.index(elem) + len(elem)
                num = num_to_add

        for tag in steps:  # remove "/" character from list
            tag[1] = tag[1].replace("/", "")

        # Every element in the steps list is a tuple with two elements, such as (1, b) or (5, b).
        # The second element of the tuple represents a text formatting method, which has an equivalent integer value.
        # This information is stored in the self.text_formatting_action dictionary.
        # The code below swaps the text formatting method with its equivalent integer value.on
        mapping = {val: num for num, val in self.text_formatting_action.items()}
        for action in steps:
            if action[1] in mapping:
                action[1] = mapping[action[1]]

        # Initialize an empty list to store the text formatting actions to be executed
        action_to_execute = list()

        # In this step, we join the start and end indexes of actions for a single text formatting tag. One of the
        # final elements in the action_to_execute list should look like this (1, 10, 0) (start_index, end_index,
        # method)
        while steps:
            # Set the first element in the steps list as the current action
            action = steps[0]

            # Set the start index as the first element of the action tuple (the first element is the start index)
            start = action[0]

            # Set the text formatter as the second element of the action tuple (the second element is the text
            # formatting tag)
            text_formatter = action[1]

            # Iterate through the remaining elements in the steps list to find the next action with the same text
            # formatting tag
            for equal_action in steps[1:]:
                if equal_action[1] == text_formatter:
                    # Set the end index as the first element of the equal_action tuple (the first element is the end
                    # index)
                    end = equal_action[0]

                    # Add the prepared list to the action_to_execute list
                    action_to_execute.append([start, end, text_formatter])

                    # Remove both lists from the steps list and return to the main loop
                    steps.remove(equal_action)
                    steps.remove(action)
                    break

        # # Initialize the is_formatting_on and last_action variables as None
        is_formatting_on = None
        last_action = None

        # Iterate through the actions in the action_to_execute list
        for action in action_to_execute:
            # If the formatting starts at the first character in the line
            if action[0] == 0:
                # Check if cursor will set proper in 1-st postition
                # If not, add necessary int to move
                n_to_move = self.move_cursor(
                    content=content_without_tags,
                    selenium_element=selenium_element,
                    direction="position",
                    position=action[1],
                    n_for_end_and_position=n_for_end_and_position,
                )

                # Back to start of the line
                self.action.send_keys(Keys.LEFT * action[1])

                # Press and hold SHIFT and move the cursor to the right by the number of characters specified in
                # action[1]'
                self.action.key_down(Keys.SHIFT).send_keys(
                    Keys.RIGHT * (action[1] + n_to_move)
                ).perform()

                # Click text formatting button (after this, we reset action chain)
                text_modify_butttons[action[2]].click()
                self.action.reset_actions()

                # For pausing the script for some time
                self._time_patterns()

                # Unselect the selected characters
                selenium_element.send_keys(Keys.RIGHT)

                # Move back to the start of the line (after this, we reset action chain)
                self.action.send_keys(Keys.LEFT * action[1]).perform()
                self.action.reset_actions()

                # For pausing the script for some time
                self._time_patterns()

                # Check if we back to correct  place - if not correct it
                self.move_cursor(
                    content=content_without_tags,
                    selenium_element=selenium_element,
                    direction="start",
                )

                # There is a glitch in the Facebook text box - if our last word has formatting, the formatting will
                # be moved to the next line. So we have to check for this condition and if it's True,
                # save this information to variables which are needed to switch this off
                if action[1] == len(content_without_tags):
                    is_formatting_on = True
                    last_action = action[2]

            else:
                # Check if cursor will set proper in 1-st postition
                # If not, add necessary int to move
                n_to_move_1 = self.move_cursor(
                    content=content_without_tags,
                    selenium_element=selenium_element,
                    direction="position",
                    position=action[0],
                    n_for_end_and_position=n_for_end_and_position,
                )

                # Back to start of the line
                self.action.send_keys(Keys.LEFT * action[0])

                # Move to 1-st position
                self.action.send_keys(Keys.RIGHT * (action[0] + n_to_move_1))

                # Check if cursor will move proper to 2-nd postition
                # If not, add necessary int to move
                n_to_move_2 = self.move_cursor(
                    content=content_without_tags,
                    selenium_element=selenium_element,
                    direction="position",
                    position=action[1] - action[0],
                    to_move=action[1],
                    n_for_end_and_position=n_for_end_and_position,
                )

                # For pausing the script for some time
                self._time_patterns()

                # Calculate steps to move
                k = (action[1] - action[0]) + (action[0] + n_to_move_1)

                # Back to start of the line
                self.action.send_keys(Keys.LEFT * k)

                # Press and hold SHIFT and move cursor by n places to right
                self.action.send_keys(Keys.RIGHT * (action[0] + n_to_move_1)).perform()
                self.action.reset_actions()

                # For pausing the script for some time
                self._time_patterns()

                # Press and hold SHIFT and move cursor by n places to right
                self.action.key_down(Keys.SHIFT).send_keys(
                    Keys.RIGHT * (action[1] - action[0] + n_to_move_2)
                ).perform()

                # Click text formatting button (after this, we reset action chain)
                text_modify_butttons[action[2]].click()
                self.action.reset_actions()

                # For pausing the script for some time
                self._time_patterns()

                # Unselect the selected characters
                selenium_element.send_keys(Keys.RIGHT)

                # Move back to the start of the line (after this, we reset action chain)
                self.action.send_keys(Keys.LEFT * (int(action[1]))).perform()
                self.action.reset_actions()

                # For pausing the script for some time
                self._time_patterns()

                # Check if we back to correct place - if not correct it
                self.move_cursor(
                    content=content_without_tags,
                    selenium_element=selenium_element,
                    direction="start",
                )

                # There is a glitch in the Facebook text box - if our last word has formatting, the formatting will
                # be moved to the next line. So we have to check for this condition and if it's True,
                # save this information to variables which are needed to switch this off
                if action[1] == len(content_without_tags):
                    is_formatting_on = True
                    last_action = action[2]

        return is_formatting_on, last_action

    def send_text(self, content: str, selenium_element):
        """
        Sends the given `content` string to the Facebook text box element specified by `selenium_element` and applies
        text formatting according to formatting tags in the `content` string.
        :param content: The string to be sent to the Facebook text box
        :param selenium_element: A Selenium web element object representing the Facebook text box element.
        """
        # Find the text formatting buttons in the Facebook text box
        text_modify_butttons = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//span[@class='x12mruv9 xfs2ol5 x1gslohp x12nagc']")
            )
        )
        # Initialize empty lists to store text formatting actions for text without bold and italic formatting,
        # and text with only bold and italic formatting
        list_of_action_to_do_with_text_without_bold_and_italic = list()
        list_of_action_to_do_with_text_only_with_bold_and_italic = list()

        # Find all text formatting tags in the `content` string
        tags = re.findall(r"<(.+?)>", content)

        # If there are any tags in the `content` string
        if tags:
            # Create a dictionary mapping the tag strings to their corresponding values in the
            # `self.text_formatting_action` dictionary
            tag_values = {
                val: num
                for num, val in self.text_formatting_action.items()
                if val in tags
            }

            # Initialize empty lists to store text formatting actions for text without bold and italic formatting,
            # and text with only bold and italic formatting
            list_of_action_to_do_with_text_without_bold_and_italic = [
                num for num in tag_values.values() if num not in (0, 1)
            ]
            list_of_action_to_do_with_text_only_with_bold_and_italic = [
                num for num in tag_values.values() if num in (0, 1)
            ]
        # If there are no text formatting actions to perform
        if (
            not list_of_action_to_do_with_text_without_bold_and_italic
            and not list_of_action_to_do_with_text_only_with_bold_and_italic
        ):
            # Send the `content` to the Facebook text box and create a new line
            selenium_element.send_keys(content)
            selenium_element.send_keys(Keys.ENTER)

        # If there are text formatting actions to perform
        else:
            # Store the content without text formatting tags in `content_without_tags`
            content_without_tags = re.sub("<[^<>]+>", "", content)

            # Init var n where we store lenght of content_without_tags
            n = len(content_without_tags)

            # Send the `content_without_tags` to the Facebook text box
            selenium_element.send_keys(content_without_tags)
            # Press and hold Shift then press left by n times (after this, we reset action chain)
            self.action.key_down(Keys.SHIFT).send_keys(Keys.LEFT * n).perform()
            self.action.reset_actions()

            # For pausing the script for some time
            self._time_patterns()
            # Iterate through actions in `list_of_actions_without_bold_and_italic` and click the corresponding button
            # to trigger the action
            for action in list_of_action_to_do_with_text_without_bold_and_italic:
                text_modify_butttons[action].click()

                # For pausing the script for some time
                self._time_patterns(2)
            # Set cursor at the start of text
            selenium_element.send_keys(Keys.LEFT)
            # Check if the cursor is at the start of the line and move it if necessary
            n_to_move = self.move_cursor(
                content=content_without_tags,
                selenium_element=selenium_element,
                direction="start",
            )
            # Add n_to_move to variable when we store lenght of content to correct proper lenght
            n += n_to_move

            # Apply bold and italic formatting and fix the Facebook glitch if necessary
            is_formatting, last_action = self.bold_and_italic_formatting(
                content=content,
                content_without_tags=content_without_tags,
                selenium_element=selenium_element,
                text_modify_butttons=text_modify_butttons,
                n_for_end_and_position=n_to_move,
            )
            # For pausing the script for some time
            self._time_patterns()

            # Move the cursor to the end of the line
            selenium_element.send_keys(Keys.RIGHT * n)
            # Check if the cursor is at the end of the line and move it if necessary
            self.move_cursor(
                content=content_without_tags,
                selenium_element=selenium_element,
                direction="end",
                n_for_end_and_position=n_to_move,
            )
            # For pausing the script for some time
            self._time_patterns()

            # If the last word was bold or italic, turn off the formatting before creating a new line
            if is_formatting:
                self.action.key_down(Keys.CONTROL).send_keys(
                    "b" if last_action == 0 else "i"
                ).perform()
                self.action.reset_actions()
            # If the text has a list formatting, press Enter twice to turn off the formatting
            if (
                5 in list_of_action_to_do_with_text_without_bold_and_italic
                or 6 in list_of_action_to_do_with_text_without_bold_and_italic
            ):
                selenium_element.send_keys(Keys.ENTER)
                selenium_element.send_keys(Keys.ENTER)

            # In any other case, press Enter once
            else:
                selenium_element.send_keys(Keys.ENTER)
        # For pausing the script for some time
        self._time_patterns()

    def prepare_and_send_post(self, txt_name: str, img_name: str):

        # Log into Facebook
        self._login_to_facebook()

        counter = 0
        number = randint(3, 5)

        for group in self.groups:
            # Open Facebook group url
            self.driver.get(group + "buy_sell_discussion")
            logger.info(f"/// Start processing group: {group + 'buy_sell_discussion'}")

            # Load imgage from s3 AWS
            image = self.get_from_aws(
                file_name=img_name,
                bucket_name=self.bucket_name,
            )

            # Load txt_file from s3 AWS
            content = self.get_from_aws(
                file_name=txt_name, bucket_name=self.bucket_name
            )

            # For pausing the script for sometime
            self._time_patterns()

            # Locate postbox element and click it
            element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//div[@class='x6s0dn4 x78zum5 x1l90r2v x1pi30zi x1swvt13 xz9dl7a']",
                    )
                )
            )
            element.click()

            # For pausing the script for sometime
            self._time_patterns()

            # Activate postbox pop up to send value to it
            postbox = self.driver.switch_to.active_element

            # Load content from file
            content = self.get_txt(content)

            #  Iterate through content file and add text
            for line in content.split("\n"):
                self.send_text(content=line, selenium_element=postbox)

            # Add images to post
            driver = element.parent
            file_input = driver.execute_script(self.js_code, postbox, 0, 0)
            # Save the image to a temporary file
            image = self.get_image(image)
            with open("temp.jpg", "wb") as f:
                image.save(f, format="JPEG")

            file_input.send_keys("temp.jpg")

            # For pausing the script for sometime
            self._time_patterns()

            # Click post button
            self.driver.find_element(By.XPATH, "//div[@aria-label='Opublikuj']").click()

            # For pausing the script for sometime
            self._time_patterns()

            if counter % number:
                self.driver.get(self.base_url)
                self._time_patterns()
                self._scroll_feed(self.driver, 5)

            counter += 1
            logger.info(f"/// End processing group: {group + 'buy_sell_discussion'}")

        self.driver.quit()
