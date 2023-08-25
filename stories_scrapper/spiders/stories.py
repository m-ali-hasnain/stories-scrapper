import re
import scrapy
from time import sleep
from scrapy import Selector
from selenium import webdriver
from scrapy.spiders import CrawlSpider
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from ..items import StoriesScrapperItem
import time

DEV = True

ALLOWED_CATEGORIES = ["clothing", "lingerie", "swimwear"]
INVALID_CATEGORIES = ["clothing", "mens", "womens"]
DISALLOWED_SUB_CATEGORIES = ["shoes", "gloves", "belts", "sunglasses", "accessories", "headwear", "care", "beauty",
                             "hats", "hair", "towel", "sandals", "ring", "teva", "bag", "bracelet", "scarves", "scarf",
                             "shoe",
                             "garment", "garment care", "ankle", "mat", "adidas", "boots", "jewelry", "earrings",
                             "sneakers", "care", "socks"]

FIT_KEYWORDS = ["Maternity", "Petite", "Plus Size", "Curvy", "Tall"]
NECK_LINE_KEYWORDS = ["Scoop", "Round Neck,", "U Neck", "U-Neck", "V Neck",
                      "V-neck", "V Shape", "V-Shape", "Deep", "Plunge", "Square",
                      "Straight", "Sweetheart", "Princess", "Dipped", "Surplice",
                      "Halter", "Asymetric", "One-Shoulder", "One Shoulder",
                      "Turtle", "Boat", "Off- Shoulder", "Collared", "Cowl", "Neckline"]

OCCASIONS_KEYWORDS = ["office", "work", "smart", "workwear", "wedding", "nuptials",
                      "night out", "evening", "spring", "summer", "day", "weekend",
                      "outdoor", "outdoors", "adventure", "black tie", "gown",
                      "formal", "cocktail", "date night", "vacation", "vacay", "fit",
                      "fitness", "athletics", "athleisure", "work out", "sweat",
                      "swim", "swimwear", "lounge", "loungewear"]

LENGTH_KEYWORDS = ["length", "mini", "short", "maxi", "crop", "cropped", "sleeves",
                   "tank", "top", "three quarter", "ankle", "long"]

STYLE_KEYWORDS = ["bohemian", "embellished", "sequin", "floral", "off shoulder",
                  "puff sleeve", "bodysuit", "shell", "crop", "corset", "tunic",
                  "bra", "camisole", "polo", "aviator", "shearling", "sherpa",
                  "biker", "bomber", "harrington", "denim", "jean", "leather",
                  "military", "quilted", "rain", "tuxedo", "windbreaker", "utility",
                  "duster", "faux fur", "overcoat", "parkas", "peacoat", "puffer",
                  "skater", "trench", "Fleece", "a line", "bodycon", "fitted",
                  "high waist", "high-low", "pencil", "pleat", "slip", "tulle",
                  "wrap", "cargo", "chino", "skort", "cigarette", "culottes",
                  "flare", "harem", "relaxed", "skinny", "slim", "straight leg",
                  "tapered", "wide leg", "palazzo", "stirrup", "bootcut", "boyfriend",
                  "loose", "mom", "jeggings", "backless", "bandage", "bandeau",
                  "bardot", "one-shoulder", "slinger", "shift", "t-shirt", "smock",
                  "sweater", "gown"]

AESTHETIC_KEYWORDS = ["E-girl", "VSCO girl", "Soft Girl", "Grunge", "CottageCore",
                      "Normcore", "Light Academia", "Dark Academia ", "Art Collective",
                      "Baddie", "WFH", "Black", "fishnet", "leather"]

FABRIC_KEYWORDS = ['velvet', 'silk', 'satin', 'cotton', 'lace', 'sheer', 'organza', 'chiffon',
                   'spandex', 'polyester', 'poly', 'linen', 'nylon', 'viscose', 'georgette',
                   'ponte', 'smock', 'smocked', 'shirred', 'rayon', 'bamboo', 'knit', 'crepe', 'leather', 'cotton',
                   'lyocell',
                   'elastane', 'acetate', 'cupro', 'polyamide', 'acrylic', 'wool', 'viscose', 'ramie']

CATEGORY_KEYWORDS = ['Bottom', 'Shift', 'Swim Brief', 'Quilted', 'Boyfriend',
                     'Padded', 'Track', 'Other', 'Oversized', 'Denim Skirt',
                     'Stick On Bra', 'Cardigan', 'Thong', 'Romper', 'Pea Coat',
                     'Skater', 'Swing', 'Lingerie & Sleepwear', 'Wrap', 'Cargo Pant',
                     'Cape', 'Trucker', 'Nursing', 'Bikini', 'Parka', 'Regular', 'Denim',
                     'Duster', 'Faux Fur', 'Hoodie', 'Bralet', 'Overcoat', 'Corset Top',
                     'T-Shirt', 'Mini', 'Maxi', 'Blazer', 'Super Skinny', 'Summer Dresses',
                     'Chino', 'Short', 'Set', 'Military', 'Overall', 'Vest', 'Bomber Jacket',
                     'Tea', 'Ski Suit', 'Work Dresses', 'High Waisted', 'Culotte', 'Overall Dress',
                     'Jean', 'Loungewear', 'Leather Jacket', 'Unpadded', 'Coats & Jackets', 'Underwired',
                     'Corset', 'Night gown', 'Poncho', 'Pant', 'Cigarette', 'Sweatpant', 'Rain Jacket',
                     'Loose', 'Swimwear & Beachwear', 'Shirt', 'Denim Jacket', 'Co-ord', 'Tight', 'Vacation Dress',
                     'Harrington', 'Bandage', 'Bootcut', 'Biker', 'Crop Top', 'Trench', 'Tracksuit', 'Suit Pant',
                     'Relaxed', 'Day Dresses', 'Tuxedo', 'Tapered', 'Wide Leg', 'Bohemian', 'Pleated', 'Wiggle',
                     'One Shoulder', 'Smock Dress', 'Flare', 'Peg Leg', 'Cover Up', 'Unitard', 'Sweater',
                     'Lounge', 'Top', 'Bodycon', 'Push Up', 'Slip', 'Knitwear', 'Leather', 'Pencil Dress',
                     'Off Shoulder', 'Jersey Short', 'Multiway', 'Balconette', 'Wax Jacket', 'Coat', 'Brief',
                     'Coach', 'Jumpsuits & Rompers', 'Bra', 'Long Sleeve', 'Fleece', 'Activewear', 'Jegging',
                     'Outerwear', 'Bandeau', 'Slim', 'Going Out Dresses', 'Bardot', 'Pajama', 'Sweatsuit',
                     'Blouse', 'Sweaters & Cardigans', 'Straight Leg', 'Windbreaker', 'Tank Top', 'Cold Shoulder',
                     'Halter', 'Dresses', 'T-Shirt', 'Trouser', 'Cami', 'Camis', 'Wedding Guest', 'Bodysuit', 'Triangle',
                     'Casual Dresses', 'Chino Short', 'Boiler Suit', 'Raincoat', 'Formal Dresses', 'Skinny',
                     'Jumper', 'Strapless', 'Cropped', 'Jacket', 'Bridesmaids Dress', 'Tunic', 'A Line',
                     'Denim Dress', 'Cocktail', 'Skirt', 'Jumpsuit', 'Shapewear', 'Occasion Dresses',
                     'Hoodies & Sweatshirts', 'Sweatshirt', 'Aviator', 'Sweater Dress', 'Sports Short',
                     'Shirt', 'Puffer', 'Cargo Short', 'Tulle', 'Swimsuit', 'Mom Jean', 'Legging',
                     'Plunge', 'Teddie', 'Denim Short', 'Intimate', 'Pencil Skirt', 'Backless', 'Tank']

CATEGORY_TO_TYPE = {
    'Co-ords': ['Co-ord', 'Sweatsuit', 'Tracksuit', 'Set'],
    'Coats & Jackets': ['Coats & Jacket', 'Cape', 'Cardigan', 'Coat', 'Jacket', 'Poncho', 'Ski Suit', 'Vest', 'Blazer'],
    'Dresses': ['Dresses', 'Bridesmaids Dress', 'Casual Dress', 'Going Out Dress', 'Occasion Dress',
                'Summer Dress', 'Work Dress', 'Formal Dress', 'Day Dress', 'Wedding Guest', 'Vacation Dress'],
    'Hoodies & Sweatshirts': ['Hoodies & Sweatshirts', 'Fleece', 'Hoodie', 'Sweatshirt'],
    'Denim': ['Denim Jacket', 'Denim Dress', 'Denim Skirt', 'Denim Short', 'Jean', 'Jegging'],
    'Jumpsuits & Rompers': ['Jumpsuits & Rompers', 'Boiler Suit', 'Jumpsuit', 'Overall', 'Romper', 'Unitard'],
    'Lingerie & Sleepwear': ['Lingerie & Sleepwear', 'Intimate', 'Bra', 'Brief', 'Corset', 'Bralet', 'Night gown',
                             'Pajama', 'Shapewear', 'Slip', 'Teddie', 'Thong', 'Tight', 'Bodysuit', 'Camis', 'Cami'],
    'Loungewear': ['Loungewear', 'Lounge', 'Activewear', 'Outerwear', 'Hoodie', 'Legging', 'Overall', 'Pajama',
                   'Sweatpant', 'Sweatshirt', 'Tracksuit', 'T-Shirt'],
    'Bottoms': ['Bottom', 'Chino', 'Legging', 'Pant', 'Suit Pant', 'Sweatpant', 'Tracksuit', 'Short', 'Skirt',
                'Trouser'],
    'Sweaters & Cardigans': ['Sweaters & Cardigans', 'Sweatpant', 'Cardigan', 'Sweater', 'Knitwear'],
    'Swimwear & Beachwear': ['Swimwear & Beachwear', 'Bikini', 'Cover Up', 'Short', 'Skirt', 'Swim Brief', 'Swimsuit'],
    'Tops': ['Top', 'Blouse', 'Bodysuit', 'Bralet', 'Camis', 'Corset Top', 'Crop Top', 'Shirt', 'Sweater',
             'Tank Top', 'T-Shirt', 'Tunic'],
}
CATEGORY_TO_STYLE = {
  'Co-ords' : ['Co-ords'],
  'Coats & Jackets' : ['Coats & Jackets', 'Aviator', 'Biker', 'Bomber Jacket', 'Coach', 'Denim Jacket', 'Duster', 'Faux Fur', 'Harrington', 'Leather', 'Leather Jacket', 'Military', 'Other', 'Overcoat', 'Parkas', 'Pea Coat', 'Puffer', 'Quilted', 'Raincoats', 'Rain Jackets', 'Regular', 'Skater', 'Track', 'Trench', 'Trucker', 'Tuxedo', 'Wax Jacket', 'Windbreaker'],
  'Dresses' : ['Dresses', 'A Line', 'Backless', 'Bandage', 'Bandeau', 'Bardot', 'Bodycon', 'Bohemian', 'Cold Shoulder', 'Denim', 'Jumper', 'Leather', 'Long Sleeve', 'Off Shoulder', 'One Shoulder', 'Other', 'Overall Dress', 'Pencil Dress', 'Shift', 'Shirt', 'Skater', 'Slip', 'Smock Dresses', 'Sweater Dress', 'Swing', 'Tea', 'T-Shirt', 'Wiggle', 'Wrap', 'Cocktail', 'Maxi', 'Mini'],
  'Hoodies & Sweatshirts' : ['Hoodies & Sweatshirts'],
  'Denim' : ['Jeans', 'Bootcut', 'Boyfriend', 'Cropped', 'Flare', 'High Waisted', 'Loose', 'Mom Jeans', 'Other', 'Regular', 'Skinny', 'Slim', 'Straight Leg', 'Super Skinny', 'Tapered', 'Wide Leg'],
  'Jumpsuits & Rompers' : ['Jumpsuits & Rompers'],
  'Lingerie & Sleepwear' : ['Lingerie & Sleepwear', 'Balconette', 'Halter', 'Multiway', 'Nursing', 'Padded', 'Plunge', 'Push Up', 'Stick On Bra', 'Strapless', 'Triangle', 'T-Shirt', 'Underwired', 'Unpadded'],
  'Loungewear' : ['Loungewear'],
  'Bottoms' : ['Bottoms', 'Cargo Pants', 'Cigarette', 'Cropped', 'Culottes', 'Flare', 'High Waisted', 'Other', 'Oversized', 'Peg Leg', 'Regular', 'Relaxed', 'Skinny', 'Slim', 'Straight Leg', 'Super Skinny', 'Tapered', 'Wide Leg', 'Cargo Shorts', 'Chino Shorts', 'Denim', 'High Waisted', 'Jersey Shorts', 'Other', 'Oversized', 'Regular', 'Relaxed', 'Skinny', 'Slim', 'Sports Shorts', 'A Line', 'Bodycon', 'Denim', 'High Waisted', 'Other', 'Pencil Skirt', 'Pleated', 'Skater', 'Slip', 'Tulle', 'Wrap'],
  'Sweaters & Cardigans' : ['Sweaters & Cardigans'],
  'Swimwear & Beachwear' : ['Swimwear & Beachwear', 'Halter', 'High Waisted', 'Multiway', 'Padded', 'Plunge', 'Strapless', 'Triangle', 'Underwired'],
  'Tops' : ['Tops'],
}

WEBSITE_NAME = "stories"
class StoriesSpider(CrawlSpider):
    name = 'stories'
    allowed_domains = ['www.stories.com']

    def __init__(self, *a, **kw):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        super().__init__(*a, **kw)

    def start_requests(self):
        base_url = 'https://www.stories.com/'
        yield scrapy.Request(url=base_url, callback=self.parse_categories)


    def parse_categories(self, response):
        category_labels = response.css(".primary li[data-category-id]>a::text").getall()
        category_labels = [item.strip() for item in category_labels if item not in " "]
        category_ids = response.css(".primary li::attr(data-category-id)").getall()
        if len(category_labels) == len(category_ids) and len(category_ids) > 0:
            for index in range(len(category_labels)):
                if (category_labels[index]).lower() in ALLOWED_CATEGORIES:
                    url = response.css(
                        f"div[data-category-id={category_ids[index]}] li:first-child>a::attr(href)").get()
                    yield scrapy.Request(url=url, callback=self.parse_category_page)

    def parse_category_page(self, response):
        self.driver.get(response.url)
        sleep(20)
        product_count = response.css('.total-items::text').get()
        product_count = int(((product_count.split())[0]).strip("("))
        product_urls = []
        SCROLL_PAUSE_TIME = 10
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight{-500});")
            sleep(SCROLL_PAUSE_TIME)
            new_height = self.driver.execute_script(f"return document.body.scrollHeight")
            if new_height == last_height:
                if self.check_exists_by_css_selector(".is-loadmore"):
                    # load_more_button =  self.driver.find_element_by_css_selector(".is-loadmore")
                    load_more_button = self.driver.find_element(By.CSS_SELECTOR, ".is-loadmore")
                    if load_more_button.is_displayed():
                        self.driver.execute_script(f"window.scrollTo(0, {(load_more_button.location['y']) - 500})")
                        load_more_button.click()
                    else:
                        break
            last_height = new_height
        custom_selector = Selector(text=self.driver.page_source)
        product_urls.extend(custom_selector.css('.producttile-wrapper>a::attr(href)').getall())

        for url in product_urls:
            yield scrapy.Request(url=url, callback=self.parse_product)

    def parse_product(self, response):
        self.driver.get(response.url)
        custom_selector = Selector(text=self.driver.page_source)
        url = response.url
        categories = []
        name = custom_selector.css(".product-name::text").get()
        scrapped_categories = re.findall(r"www.stories.com/en/(.*?)/product.*", url)
        scrapped_categories = ("".join(scrapped_categories)).split('/')
        scrapped_categories = [item for item in scrapped_categories if item.lower() not in INVALID_CATEGORIES]
        scrapped_categories = [" ".join((item.capitalize()).split('-')) for item in scrapped_categories]

        extracted_categories = extract_categories_from(url)
        if extracted_categories:
            categories = find_actual_parent(scrapped_categories, extracted_categories)
        else:
            extracted_categories = extract_categories_from(name)
            if extracted_categories:
                categories = find_actual_parent(scrapped_categories, extracted_categories)
            else:
                extracted_categories = extract_categories_from(scrapped_categories)
                if extracted_categories:
                    categories = find_actual_parent(scrapped_categories, extracted_categories)


        check = self.check_disallowed_category(categories, name, DISALLOWED_SUB_CATEGORIES)
        if not check:
            external_id = custom_selector.css('#product-number::text').get()
            price = (self.get_price(custom_selector)).strip()
            colors = custom_selector.css('.a-swatch>input::attr(value)').getall()
            sizes = []
            if self.check_exists_by_css_selector("#sizeList"):
                sizes.extend(custom_selector.css("#sizeList>ul>li::text").getall())
            else:
                sizes = custom_selector.css('.a-size-swatch>button::attr(data-value)').getall()
            if custom_selector.css('.a-size-swatch>span'):
                meta = {'out_of_stock': 'True'}

            details = custom_selector.css("div#product-description *::text").getall()
            images = self.get_images(custom_selector)
            fabric_details = custom_selector.css("span#articleCompositions span::text").get()
            if fabric_details:
                fabric_details = fabric_details.split(":")
            fabric = fabric_details[-1].strip()
            neck_line = self.find_from_target_string_single(details, NECK_LINE_KEYWORDS)
            length = self.find_from_target_string_multiple(details, name, categories, LENGTH_KEYWORDS)
            occasions = self.find_from_target_multiple_list(details, name, categories, OCCASIONS_KEYWORDS)
            style = self.find_from_target_multiple_list(details, name, categories, STYLE_KEYWORDS)
            fit = self.find_from_target_string_single(details, FIT_KEYWORDS)
            style = list(set(style))
            gender = 'women'
            # aesthetics = self.find_from_target_string_multiple(raw_details, name, categories, AESTHETIC_KEYWORDS)
            # Removing Length from details
            details = [det for det in details if not re.search("Length .*\)", det, re.IGNORECASE)]
            number_of_reviews = ""
            review_description = []
            top_best_seller = ""
            meta = {}

            item = StoriesScrapperItem()
            item["url"] = url  # string
            item["external_id"] = external_id  # string
            item["categories"] = categories  # list
            item["name"] = name  # string
            item["price"] = price.strip()  # sring
            item["colors"] = colors  # list
            item["sizes"] = sizes  # list
            item["details"] = details  # list
            item["images"] = images  # list
            item["fabric"] = fabric  # string
            item["occasions"] = occasions  # list
            item["length"] = length  # string
            item["neck_line"] = neck_line  # string
            item["fit"] = fit  # string
            item["style"] = style  # list
            item["gender"] = gender  # string
            item["number_of_reviews"] = number_of_reviews  # string
            item["review_description"] = review_description  # list
            item["top_best_seller"] = top_best_seller  # string
            item["meta"] = meta  # json
            item["website_name"] = WEBSITE_NAME
            # item["aesthetics"] = aesthetics #string
            if categories:
                yield item

    def check_exists_by_css_selector(self, selector):
        try:
            # self.driver.find_element_by_css_selector(selector)
            self.driver.find_element(By.CSS_SELECTOR, selector)

        except NoSuchElementException:
            return False
        return True

    def check_disallowed_category(self, categories, name, keywords):
        list = []
        list.extend(name.split())
        list.extend(categories)
        for item in list:
            if item.lower() in keywords:
                return True
        return False

    def get_categories(self, custom_selector):
        categoires = []
        raw_categoires = custom_selector.css('.pdp-breadcrumb li>a>span::text').getall()
        if len(raw_categoires) > 2:
            raw_categoires = ([' '.join(item.split()) for item in raw_categoires])[1:-1]
            categoires.extend(raw_categoires)
        else:
            raw_categoires = ([' '.join(item.split()) for item in raw_categoires])[1]
            categoires.append(raw_categoires)
        return categoires

    def get_price(self, custom_selector):
        price = custom_selector.css('.m-product-price>.is-regular::text').get()
        if price:
            return price
        return custom_selector.css('.m-product-price>.is-deprecated ::text').get()

    def get_images(self, custom_selector):
        if self.check_exists_by_css_selector('#imageContainer>.swiper-slide-visible>picture>source:first-child'):
            images = custom_selector.css(
                '#imageContainer>.swiper-slide-visible>picture>source:first-child::attr(srcset)').getall()
        else:
            images = custom_selector.css(
                '#imageContainer>.swiper-slide>picture>source:first-child::attr(srcset)').getall()
        images = [f"https:{item}" for item in images]
        return images

    def check_exists_by_css_selector(self, selector):
        try:
            self.driver.find_element(By.CSS_SELECTOR, selector)
            # self.driver.find_element_by_css_selector(selector)
        except NoSuchElementException:
            return False
        return True

    # This helper finds fabric from details and returns it
    def find_fabric_from_details(self, details):
        product_details = ' '.join(details)
        fabrics_founded = re.findall(r"""(
            velvet\b|silk\b|satin\b|cotton\b|lace\b|
            sheer\b|organza\b|chiffon\b|spandex\b|polyester\b|
            poly\b|linen\b|nylon\b|viscose\b|Georgette\b|Ponte\b|
            smock\b|smocked\b|shirred\b|Rayon\b|Bamboo\b|Knit\b|Crepe\b|
            Leather\b|polyamide\b|Acrylic\b|Elastane\bTencel\bCashmere\b)(\d+ ?%\s?)\)?""", product_details,
                                     flags=re.IGNORECASE | re.MULTILINE)
        return re.sub("\(|\)", "", ' '.join([''.join(tups) for tups in fabrics_founded]))

    def find_from_target_string_single(self, source_data, target_keywords):
        for each_element in source_data:
            for keyword in target_keywords:
                if keyword.lower() in each_element.lower():
                    return keyword
        return ""

    def find_from_target_multiple_list(self, details, name, categories, target_keywords):
        target_list = details[:]
        target_list.extend(name)
        target_list.extend(categories)
        final_list = []

        for each_element in target_list:
            for keyword in target_keywords:
                if keyword.lower() in each_element.lower():
                    final_list.append(keyword)

        return final_list

    def find_from_target_string_multiple(self, details, name, categories, target_keywords):
        target_list = details[:]
        target_list.extend(name)
        target_list.extend(categories)

        for element in target_list:
            for keyword in target_keywords:
                if keyword.lower() in element.lower():
                    return keyword
        return ""

        # This function scrolls product detail page to the bottom

    def scroll(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(5)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height


# This function maps category we have extracted from name or url to taxonomy,
# and then it returns the list of extracted keywords.
def map_to_parents(cats):
    # where cats -> categories
    # cat -> category
    finals = []
    for cat in cats:
        for key in CATEGORY_TO_TYPE:
            if re.search(cat, ' '.join(CATEGORY_TO_TYPE[key]), re.IGNORECASE):
                finals.append(key)

    if not finals:
        for cat in cats:
            for key in CATEGORY_TO_STYLE:
                if re.search(cat, ' '.join(CATEGORY_TO_STYLE[key]), re.IGNORECASE):
                    finals.append(key)
    return list(set(finals))


# This function find real parent category from the list of extracted categories we provided
# Arguments: -> here first arg is scrapped categories and second is one which is list of extracted keywords
# we basically loop over scrapped categories and check if any category from scrapped one lies in extracted ones
def find_actual_parent(scrapped_cats, categories):
    finals = []
    final_categories = map_to_parents(categories)
    if len(final_categories) > 1:
        for fc in final_categories:
            if re.search(fc, ' '.join(scrapped_cats), re.IGNORECASE):
                finals.append(fc)

        if finals:
            return finals
        else:
            return []
    else:
        if final_categories:
            return final_categories
        else:
            return []


# This function extracts category keywords from product attribute passed as an argument to it
def extract_categories_from(keyword):
    cats = []  # categories
    if type(keyword) == list:
        keyword = ' '.join(keyword)

    for cat in CATEGORY_KEYWORDS:
        if re.search(cat, keyword, re.IGNORECASE):
            cats.append(cat)

    return cats
