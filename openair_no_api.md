I once had a need to pull a lot of data out of OpenAir.  There was a requirement to audit some data specific to each employee of an organization.

Ordinarily this sort of task would come with API access to the system in question, and it would be fairly trivial to retrieve the required data and offload it to my workstation for the requisite processing.

Unfortunately, I did not have API access to the OpenAir instance in question. Furthermore, the instance was accessed through Okta, which adds an additional layer of abstraction to the issue.  Without the Okta layer in place, I might be able to goose it directly from a script. 

So how do we access hundreds of pages of data on a website that sits behind another website, and which provides no documented API access?

Let’s try Selenium.

The Okta issue is actually pretty easy to solve.  If we tell Selenium to navigate to the Okta login page, and feed the appropriate credentials to the relevant form elements, it’ll log us in to the Okta instance.

Please note that in the script below, we’re storing the credentials in a separate file called credentials.   We’re also using loguru for enhanced logging, instead of a simple print statement.


```python
import datetime
import os
import time
import re
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
import credentials
import loguru
from selenium.common.exceptions import WebDriverException
import json
from collections import defaultdict, Counter
import numpy as np
logger = loguru.logger
chromedriver_path = '<chromedriver path>'


def init_driver():
    try:
        options = webdriver.ChromeOptions()
        options.binary_location = chromedriver_path
        driver = webdriver.Chrome(options=options)
        return driver
    except WebDriverException as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        return None

driver = init_driver()
if driver is None:
    logger.error("Exiting script due to WebDriver initialization failure.")
    exit(1)

url = '<okta url>'
driver.get(url)
logger.info(f"Fetching Okta login url: {url}")
time.sleep(5)

username_field = driver.find_element(By.NAME, "username")
password_field = driver.find_element(By.NAME, "password")
username_field.send_keys(credentials.username)
password_field.send_keys(credentials.password)

time.sleep(3)

button_element = driver.find_element(By.ID, "okta-signin-submit")
button_element.click()
logger.info("Submitted Okta login")
```

This script takes credentials from a separate file, feeds them into the username and password fields, then clicks the submit button.

The recurring instances of time.sleep() are important, because it’s very easy for Selenium to get ahead of itself.  You need to deliberately slow it down sometimes.

The URL to OpenAir from within Okta should be consistent, so that can be hardcoded in, and retrieved with the web driver:
```python
driver.get("<OpenAir URL>")
logger.info("Fetching OA homepage")
time.sleep(3)

oa_url = driver.current_url.split(";")
uid = oa_url[2].replace("uid=", "")
```

The second half of this snippet is the way in which the UID for the current OpenAir login session is fetched.  Each time a person logs in to OpenAir, they’re assigned a different UID.  This UID is required to fetch any resources from within OpenAir. Fortunately, it’s part of the URL on the homepage, and can therefor be extracted.

Here’s an example.  Say I wanted to go to the *Resources* page of OpenAir.   The URL looks like this:

https://<OA URL>.app.openair.com/webapi/v2/list/resource@resource/data?uid=xxxxxxxxxx&app=rm&page=1

The UID must be known, in order to submit a valid GET request through the browser.    If we extract the UID from the URL of the homepage, we can make this work. Example:

```python
driver.get(f"<OA URL>.app.openair.com/webapi/v2/list/resource@resource/data?uid={uid}&app=rm&page=1")
logger.info(f"Fetching resources URL: https://<OA URL>.app.openair.com/webapi/v2/list/resource@resource/data?uid={uid}&app=rm&page=1")
time.sleep(3)
page_text = driver.page_source
```

And with that, we’ve successfully fetched the first page of results for the Resources section of OpenAir, without external API access.

So now what?

The format of the page returned by the (undocumented) API endpoint above appears to be JSON, but it’s actually JSON wrapped in HTML.  For that reason, we need to extract the JSON before we can parse it:

```python
try:
    json_match = re.search(r'({.*})', page_text, re.DOTALL)
    if json_match:
        json_content = json.loads(json_match.group(1))
        meta = json_content.get("meta")
        total_pages = meta["total_pages"]
        logger.info(f"Found a total resource page count of {total_pages}")
    else:
        logger.warning("No JSON content found")
except json.JSONDecodeError:
    logger.error("Failed to decode JSON")

page_count = 1
all_user_data = []

while True:
    driver.get(f"<OA URL>.app.openair.com/webapi/v2/list/resource@resource/data?uid={uid}&app=rm&page={page_count}")
    logger.info(f"Fetching resource page: <OA URL>.app.openair.com/webapi/v2/list/resource@resource/data?uid={uid}&app=rm&page={page_count}")
    driver.implicitly_wait(5)
    page_text = driver.page_source

    json_match = re.search(r'({.*})', page_text, re.DOTALL)
    if json_match:
        json_content = json.loads(json_match.group(1))
        logger.info(f"Found JSON for resource page {page_count}")

        initial_user_data = json_content.get("data", [])
        all_user_data.extend(initial_user_data)  # Collecting all user data

    page_count += 1
    if total_pages and page_count > total_pages:
        break
 ```

It’s first extracting the JSON from page #1, and looking for the value of the total_pages attribute. Using that value, it then paginates through all of the pages of results, and extracts the JSON from each page.

Here’s the full script:

```python
import datetime
import os
import time
import re
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
import credentials
import loguru
from selenium.common.exceptions import WebDriverException
import json
from collections import defaultdict, Counter
import numpy as np
logger = loguru.logger
chromedriver_path = '<path to ChromeDriver>'
json_filename = f"oa_skills_export_{datetime.datetime.today().date()}.json"
oa_url = "<okta subdomain url>"
okta_url = "<okta url>"
okta_oa_url = "<url from Okta to OpenAir"
def init_driver():
    try:
        options = webdriver.ChromeOptions()
        options.binary_location = chromedriver_path
        driver = webdriver.Chrome(options=options)
        return driver
    except WebDriverException as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        return None

driver = init_driver()
if driver is None:
    logger.error("Exiting script due to WebDriver initialization failure.")
    exit(1)

driver.get(okta_url)
time.sleep(5)

username_field = driver.find_element(By.NAME, "username")
password_field = driver.find_element(By.NAME, "password")
username_field.send_keys(credentials.username)
password_field.send_keys(credentials.password)

time.sleep(3)

button_element = driver.find_element(By.ID, "okta-signin-submit")
button_element.click()

time.sleep(3)

driver.get(f"{okta_oa_url}")
logger.info(f"Fetching OA homepage: {okta_oa_url}")
time.sleep(3)

oa_homepage_url = driver.current_url.split(";")
uid = oa_url[2].replace("uid=", "")

driver.get(f"https://{oa_url}.app.openair.com/webapi/v2/list/resource@resource/data?uid={uid}&app=rm&page=1")
logger.info(f"Fetching resources URL: https://{oa_url}.app.openair.com/webapi/v2/list/resource@resource/data?uid={uid}&app=rm&page=1")
time.sleep(3)
page_text = driver.page_source

try:
    json_match = re.search(r'({.*})', page_text, re.DOTALL)
    if json_match:
        json_content = json.loads(json_match.group(1))
        meta = json_content.get("meta")
        total_pages = meta["total_pages"]
        logger.info(f"Found a total resource page count of {total_pages}")
    else:
        logger.warning("No JSON content found")
except json.JSONDecodeError:
    logger.error("Failed to decode JSON")

page_count = 1
all_user_data = []

while True:
    driver.get(f"https://{oa_url}.app.openair.com/webapi/v2/list/resource@resource/data?uid={uid}&app=rm&page={page_count}")
    logger.info(f"Fetching resource page: https://{oa_url}.app.openair.com/webapi/v2/list/resource@resource/data?uid={uid}&app=rm&page={page_count}")
    driver.implicitly_wait(5)
    page_text = driver.page_source

    json_match = re.search(r'({.*})', page_text, re.DOTALL)
    if json_match:
        json_content = json.loads(json_match.group(1))
        logger.info(f"Found JSON for resource page {page_count}")

        initial_user_data = json_content.get("data", [])
        all_user_data.extend(initial_user_data)  # Collecting all user data

    page_count += 1
    if total_pages and page_count > total_pages:
        break

# Reinitialize the driver for fetching detailed user info

# Fetch detailed user info and update the user data
for user in all_user_data:
    username = user.get("username", {}).get("props", {}).get("value")
    user_url = user.get("username", {}).get("props", {}).get("url")

    if user_url:
        logger.info(f'Fetching details for user: {username} from URL: {user_url}')
        driver.get(user_url)
        driver.implicitly_wait(5)
        user_data_text = driver.page_source

        user_json_match = re.search(r'({.*})', user_data_text, re.DOTALL)
        if user_json_match:
            user_json_content = json.loads(user_json_match.group(1))
            user['detailed_info'] = user_json_content
            logger.info(f'Added detailed info for user: {username}')

driver.quit()

with open(json_filename, "w") as json_file:
    json.dump(all_user_data, json_file, indent=4)

print(f"Combined user data with line managers saved to {json_filename}")


# Define a path to the existing JSON file:
json_file_path = json_filename
# Read the JSON file
# Read the JSON file
with open(json_file_path, 'r') as file:
    user_json_data = json.load(file)

line_managers = []
users_without_manager = []
unique_skills = []

# Collecting line managers and users without managers
for user in user_json_data:
    username = user["username"]["props"]["value"]
    if "line_manager" in user and user["line_manager"]:
        line_manager = user["line_manager"]["props"]["value"]
    else:
        line_manager = None

    if line_manager:
        if line_manager not in line_managers:
            line_managers.append(line_manager)
    else:
        users_without_manager.append(username)

department_skills_count = defaultdict(lambda: defaultdict(set))

for user in user_json_data:
    department = user["department"]
    if "detailed_info" in user and user["detailed_info"] and "skills" in user["detailed_info"]:
        skills = user["detailed_info"]["skills"]
        if skills is not None:
            for skill_type, skill_list in skills["types"].items():
                for skill in skill_list:
                    department_skills_count[department][skill_type].add(skill["name"])

for user in user_json_data:
    try:
        skills = user["detailed_info"]["skills"]['types']['Skills']
        if skills is not None:
            for skill in skills:
                unique_skills.append(skill['name'])
    except:
        pass
values, counts = np.unique(unique_skills, return_counts=True)
skill_count_dict = dict(zip(values, counts))

skill_to_users = defaultdict(list)

for user in user_json_data:
    username = user["username"]["props"]["value"]
    if "detailed_info" in user and user["detailed_info"] and "skills" in user["detailed_info"]:
        skills = user["detailed_info"]["skills"]
        if skills is not None:
            for skill_type, skill_list in skills["types"].items():
                for skill in skill_list:
                    skill_to_users[skill["name"]].append(username)
```

So what’s the point? The point is that there are limitations, and then there are limitations.   Just because a system is nominally set up a certain way, with apparent guard rails and restrictions, does not mean you have to respect those limitations
