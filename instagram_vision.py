"""
Before running the script:

1. Install selenium: 
    
    pip install selenium

2. Download chrome driver and note the path

3. Install google-cloud-vision: 
    
    pip install google-cloud-vision --ignore-installed

4. Create an environment variable: GOOGLE_APPLICATION_CREDENTIALS
    In MAC/Linux:
        run the following command in your terminal
            export GOOGLE_APPLICATION_CREDENTIALS PATH-OF-JSON-FILE 
            for example: 
            export GOOGLE_APPLICATION_CREDENTIALS=/Users/msbde164/Documents/ImageAssignment-2f16f129fb67.json 
    In Windows 10 and Windows 8
            In Search, search for and then select: System (Control Panel)
            Click the Advanced system settings link.
            Click Environment Variables. In the section System Variables, select new 
            provide: GOOGLE_APPLICATION_CREDENTIALS for variable_name and PATH-OF-JSON-FILE for variable_value.


"""




import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from google.cloud import vision
from google.cloud.vision import types
import io, urllib

## you dont have to change anything in this function ##
def google_tags(url):
    temp_image_name = "00000001.jpg"
    urllib.urlretrieve(url, temp_image_name)
    with io.open(temp_image_name, 'rb') as image_file:
        content = image_file.read()
    client = vision.ImageAnnotatorClient()
    image = types.Image(content=content)
    response_label = client.label_detection(image= image)
    response_web = client.web_detection(image=image)
    response_text = client.text_detection(image=image)
    labels = response_label.label_annotations
    notes = response_web.web_detection
    texts = response_text.text_annotations
    image_labels = []
    for label in labels:
        image_labels.append(label.description)
    image_labels = " ".join(image_labels)
    image_text = []
    for text in texts:
        image_text.append(text.description)
    image_text = " ".join(image_text)
    web_entities = []
    if notes.web_entities:
        for entity in notes.web_entities:
            if entity.score > 0.1:
                web_entities.append(entity.description)
    web_entities = " ".join(web_entities)
    return [image_labels, image_text, web_entities]


if __name__ == '__main__':
    # URL of the page
    PAGE_URL = "https://www.instagram.com/natgeo/"
    # path to the chrome driver
    CHROME_PATH = "/Users/lily2/Desktop/UGCA/assignment/Assignment4/chromedriver"
    # number of times to click the button - load more comments
    COMMENT_LOADS = 0
    # number of time to scroll
    # if POST_LOADS is considerably high it may take longer time to scrape and get the results.
    POST_LOADS = 1	  #change it
    LOAD_PAUSE_TIME = 2
    SCROLL_PAUSE_TIME = 4
    PAGE_LOAD_TIME = 2
    COMMENT_LOAD_TIME = 3
    # RETRIEVING THE URL
    driver = webdriver.Chrome(executable_path= CHROME_PATH)
    driver.get(PAGE_URL)

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    load_more_posts_elem = driver.find_elements_by_xpath("//*[contains(text(), 'Load more')]")
    if len(load_more_posts_elem) > 0:
        driver.find_element_by_xpath("//*[contains(text(), 'Load more')]").click()
    time.sleep(LOAD_PAUSE_TIME)
    post_loads = 1
    while True:

        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        # if new_height == last_height:
#             break
        last_height = new_height	

        # track the number of scrolls
        post_loads += 1
        if post_loads>POST_LOADS:
            break
    # obtain the links of all the posts using 'taken-by' attribute
    links = driver.find_elements_by_xpath("//a[contains(@href, 'taken-by')]")

    #creating an empty data frame for image metadata and comments
    insta_images = pd.DataFrame(columns=['image_id', 'image_url', 'post', 'no_likes', 'no_comments', 'image_labels', 'image_text', 'web_entities'])
    insta_comments = pd.DataFrame(columns= ['image_id','user_name','user_comment'])
    for link_id in range(0, len(links)):
        link = links[link_id]
        imglink = link.get_attribute("href")
        # opening the link in a new tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(imglink)
        time.sleep(PAGE_LOAD_TIME)

        #intializing the values
        image_src_temp = ""
        post_title = ""
        likes = ""
        comments = ""
        user_name = ""
        user_comment = ""

        # check if the post is video or image.
        # video posts have 'views', so we skip a post if it has views
        post = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div[2]/section[2]/div/span').text
        if post.split()[1] != 'views':
            # obtaining the image source
            # image = driver.find_element_by_xpath("//img[contains(@class, '_2di5p')]")
            # image_src_temp = image.get_attribute('src')
            
            image_url = driver.find_element_by_xpath("//meta[contains(@property, 'image')]")
            image_src_temp = image_url.get_attribute('content')

            # obtaining the tags from google-cloud-vision
            [image_labels, image_text, web_entities] = google_tags(image_src_temp)

            # retreiving number of likes and comments
            image = driver.find_element_by_xpath("//meta[contains(@name, 'description')]")
            content = image.get_attribute('content')
            contents = content.split()
            likes = contents[0]
            comments = contents[2]

            # loading more comments
            elements = driver.find_elements_by_partial_link_text('comments')
            i = 0
            while len(elements) > 0:
                driver.find_element_by_partial_link_text('comments').send_keys(Keys.SPACE)
                time.sleep(COMMENT_LOAD_TIME)
                i += 1 
                elements = driver.find_elements_by_partial_link_text('comments')
                if i > COMMENT_LOADS:
                    break
            comment_list = driver.find_elements_by_tag_name('li')

            # Assumption - first comment of the post made by the user-posting the picture.
            # Since we are only looking at the posts of brands it is not a very wild assumption.
            # there are chances it may go wrong please let me know if you come across such situations.

            post_comment_elem = comment_list[0].find_elements_by_tag_name('span')
            if len(post_comment_elem) > 0:
                post_title = comment_list[0].find_element_by_tag_name('span').text
            insta_images.loc[len(insta_images)] = [link_id, image_src_temp, post_title, likes, comments, image_labels, image_text, web_entities]
            for comment_number in range(2, len(comment_list)):
                user_name_elem = comment_list[comment_number].find_elements_by_tag_name('a')
                user_comment_elem = comment_list[comment_number].find_elements_by_tag_name('span')
                if (len(user_name_elem) > 0) & (len(user_comment_elem) > 0):
                    user_name = comment_list[comment_number].find_element_by_tag_name('a').text
                    user_comment = comment_list[comment_number].find_element_by_tag_name('span').text
                    # print user_comment
                    insta_comments.loc[len(insta_comments)] = [link_id, user_name, user_comment]    					   
                else:
                    break
            print("number of comments for image link: " + str(link_id) + "- "+ str(len(insta_comments)))
            if link_id == 700:
                insta_images.to_excel('insta_images_natgeo.xlsx', index = False)
                insta_comments.to_excel('insta_comments_natgeo.xlsx', index = False)
        driver.close()
        #switching back to the initial tab
        driver.switch_to.window(driver.window_handles[0])
    driver.close()
    # writing the excel files
    # you may have to change the file names
    insta_images.to_excel('insta_images_whitehouse.xlsx', index = False)
    insta_comments.to_excel('insta_comments_whitehouse.xlsx', index = False)         
