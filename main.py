from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import traceback
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import time
import traceback
import re
from utilities import *
from db_functions import *
from logger_config import setup_logger

OEM_name = 'Royal Enfield'
data = []
file_name = 'RF_2_data.xlsx'
logger = setup_logger()



def accept_cookies_if_present(page, timeout=5000):
    try:
        cookie_btn = page.locator("button.cookie-btn.accept")

        # wait a little for it to appear
        cookie_btn.wait_for(state="visible", timeout=timeout)

        if cookie_btn.is_visible():
            cookie_btn.click()
            logger.info(" Cookie accept button clicked")
    except PlaywrightTimeoutError:
        logger.info(" Cookie accept button not visible, skipping")

def init_driver_playwrite():
    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(
        headless=False,
        args=["--start-maximized", "--disable-notifications", "--disable-popup-blocking" , "--disable-application-cache",
            "--disable-extensions"]
    )

    # create context and block popup-related network requests (prevent popup assets)
    context = browser.new_context(
        no_viewport=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
    context.set_geolocation({"latitude": 28.6139, "longitude": 77.2090})  # Delhi
    context.grant_permissions(["geolocation"])

    # Block common popup resource patterns early (prevent heavy JS/CSS that spawns popups)
    def route_handler(route):
        url = route.request.url.lower()
        # abort requests that look like popup/callback widgets
        if ("evg-generic-popup" in url) or ("requestcallback" in url) or ("popup" in url) or ("evg" in url):
            return route.abort()
        return route.continue_()

    try:
        context.route("**/*", lambda route: route_handler(route))
    except Exception:
        pass

    page = context.new_page()
    page.add_init_script("""
        (() => {
            const popups = ['#evg-generic-popup', '#requestcallbackPopup'];
            const removeIfPresent = () => {
                popups.forEach(sel => {
                    const el = document.querySelector(sel);
                    if (el) {
                        try { el.remove(); } catch(e) {}
                    }
                });
            };
            // remove immediately (in case already added before load)
            removeIfPresent();
            // observe DOM for any future popup additions
            const obs = new MutationObserver(removeIfPresent);
            obs.observe(document, { childList: true, subtree: true });
            // also hide via css as a fallback
            const style = document.createElement('style');
            style.innerHTML = popups.join(',') + '{ display:none !important; visibility:hidden !important; }';
            document.documentElement.appendChild(style);
        })();
    """)

    # page.goto("https://www.tvsmotor.com/", timeout=60000)
    # time.sleep(2)

    return page, browser




def safe_goto(page, link, retries=3, timeout=10000):
   
    attempt = 0
    while attempt < retries:
        try:
            # page.goto(link, timeout=timeout)
            page.goto(link,timeout=timeout,wait_until="domcontentloaded" )
            logger.info(f"Page loaded successfully: {link}")
            return True
        except TimeoutError:
            attempt += 1
            logger.info(f"Timeout while loading {link}. Retrying {attempt}/{retries}...")
    logger.info(f"Failed to load page after {retries} attempts: {link}")
    return False

def get_engine_and_price(page , state , model):
    try:
        displacement_div = page.locator(
            ".engine-feature-one .simple-text")
        displacement_div.wait_for(state="visible", timeout=2000)
        displacement = displacement_div.text_content().strip()
    except :
        displacement = ''
    try:
        on_road_price_div = page.locator(
            ".variant-price")
        on_road_price_div.wait_for(state="visible", timeout=2000)

        on_road_price_text = on_road_price_div.text_content().strip()
        on_road_price = int(re.sub(r"[^\d]", "", on_road_price_text))
    except :
        on_road_price = ''
    
    logger.info(f'{state} |{model}| {displacement} | {on_road_price}')

    row ={
           "Vehicle_type": 'm/c',
           "OEM_name" : OEM_name,
           "Model_Name": model,
           "Engine_Displacement" : displacement,
           "Variant":"",
           "State": state,
           "Ex_Showroom_Price": "",
           "On_Road_Price": on_road_price
       }
    data.append(row)
    save_to_excel([row] )
    # insert_one_row(row)
    # logger.info('-'*15)


def open_each_model(page , state):

    try:

        page.wait_for_selector(".models-container")
        page.wait_for_selector("a.model-see-details")

        cards = page.locator("a.model-see-details")
        total_cards = cards.count()

        logger.info(f"Total models found: {total_cards}")

        model_names = page.locator("h5.model-title").all_text_contents()
        logger.info(model_names)

        for i in range(total_cards):

            try:

                model_titles = page.locator("h5.model-title")
                see_details_buttons = page.locator("a.model-see-details")

                model_titles.nth(i).wait_for(state="visible", timeout=5000)

                model = model_titles.nth(i).text_content().strip()
                logger.info(model)

                logger.info(f"\nOpening model => {model} ---- {i + 1}/{total_cards}")

                see_details_btn = see_details_buttons.nth(i)
                see_details_btn.scroll_into_view_if_needed()
                time.sleep(2)
                see_details_btn.click(force=True)
            
                time.sleep(3)


                get_colors_by_navigation(page, state, model)
                # get_engine_and_price(page , state , model)

                back_btn = page.locator("div.backBtn")
                back_btn.wait_for(state="visible", timeout=2000)
                back_btn.click()
            
            except Exception as e:
                logger.error("Model Error", exc_info=True)

    except Exception as e:
        logger.error("ERROR----------", exc_info=True)

def get_colors_by_navigation(page, state, model):

    try:
        page.wait_for_selector(".slick-slide")

        seen = set()

        while True:
            try:
                # ✅ current active slide
                active_slide = page.locator(".slick-slide.slick-current")

                # color_name = active_slide.locator(".tank-image-color").text_content().strip()
                #changed 
                color_text = active_slide.locator(".tank-image-color").text_content()
                color_name = color_text.strip() if color_text and color_text.strip() else "Unnamed variant"
                
                if color_name in seen:
                    logger.info("Completed full cycle")
                    break

                seen.add(color_name)

                logger.info(f"\nCurrent color: {color_name}")

                # ✅ get price
                price_el = page.locator(".variant-price")
                price_el.wait_for(state="visible", timeout=3000)

                price_text = price_el.text_content().strip()
                price = int(re.sub(r"[^\d]", "", price_text))

                logger.info(f"{state} | {model} | {color_name} | {price}")

                # 👉 SAVE DATA
                row = {
                    "Vehicle_type": 'm/c',
                    "OEM_name": OEM_name,
                    "Model_Name": model,
                    "Variant": color_name,
                    "State": state,
                    "On_Road_Price": price
                }

                data.append(row)
                save_to_excel([row])

                # ✅ CLICK NEXT BUTTON (IMPORTANT)
                next_btn = page.locator(".slick-next")
                next_btn.click()

                # ✅ wait for change
                page.wait_for_timeout(1500)

            except Exception as e:
                logger.error("ERROR----------", exc_info=True)
                break

        logger.info(f"Total unique colors: {len(seen)}")

    except Exception as e:
        logger.error("ERROR----------", exc_info=True)

def bike(page):

    try:
    
        safe_goto(page, 'https://finance.royalenfield.com/enquire/select-city')
        accept_cookies_if_present(page)

        state_dropdown = page.locator("#city-selector").first
        state_dropdown.wait_for(state="visible")
        state_dropdown.click()

        page.wait_for_selector(".dropdown-menu.show a.dropdown-item")
        states = page.locator(".dropdown-menu.show a.dropdown-item")
        state_names = states.all_text_contents()

        logger.info(state_names)

        for state in state_names:
            try:

                logger.info(f"\nSelecting State: {state}")
                # input('stop')
                if state != state_names[0]:
                    state_dropdown.click()
                state_locator = page.locator(
                    f".dropdown-menu.show a.dropdown-item:text-is('{state}')"
                )
                state_locator.wait_for(state="attached")
                state_locator.click(force=True)
                logger.info('clicked')


                city_dropdown = page.locator("#city-selector").nth(1)
                city_dropdown.wait_for(state = 'visible')
                city_dropdown.click()

                page.wait_for_selector(".dropdown-menu.show a.dropdown-item")
                first_city = page.locator(
                    ".dropdown-menu.show a.dropdown-item").first
                first_city.wait_for(state="attached")
                city_name = first_city.text_content().strip()
                first_city.click(force=True)

                confirm_btn = page.locator('//*[@id="root"]/div[2]/div[2]/div/div')
                confirm_btn.click()

                logger.info(f"Confirmed: {state} | {city_name}")

                open_each_model(page , state)
                safe_goto(page, 'https://finance.royalenfield.com/enquire/select-city')

            except Exception as e:
                logger.error("ERROR----------", exc_info=True)
                safe_goto(page, 'https://finance.royalenfield.com/enquire/select-city')

    

    except Exception as e:
        logger.error("ERROR----------", exc_info=True)




def find_bikes(page):
    # Open home page
    safe_goto(page, 'https://www.royalenfield.com/in/en/home/')
    accept_cookies_if_present(page)


    # Click "Motorcycles"
    motorcycles_header = page.locator('//*[@id="accordion-adc43eb997-item-8da7d32b16-button"]')
    motorcycles_header.click()
    # page.wait_for_load_state("networkidle")
    logger.info("Motorcycles clicked")

    # Locate category headers
    category_headers = page.locator(".re-revamp-v4-category-header")
    category_count = category_headers.count()

    logger.info(f"Total categories found: {category_count}")

    for c_index in range(category_count):

        category_headers = page.locator(".re-revamp-v4-category-header")
        category = category_headers.nth(c_index)

        category_name = category.inner_text().strip()
        logger.info(f"Category: {category_name}")

        # Expand category
        category.click()
        page.wait_for_timeout(1000)

        bikes_locator = page.locator(
            f"(//div[contains(@class,'re-revamp-v4-category-content')])[{c_index + 1}]"
            f"//div[contains(@class,'re-revamp-v4-bike-thumbnail')]"
        )

        bike_count = bikes_locator.count()
        logger.info(f"   Bikes found: {bike_count}")

        for b_index in range(bike_count):

            #Reload page after each bike
            safe_goto(page , 'https://www.royalenfield.com/in/en/home/')


            # Re-click Motorcycles (important after reload)
            motorcycles_header = page.locator('//*[@id="accordion-adc43eb997-item-8da7d32b16-button"]')
            motorcycles_header.click()
            page.wait_for_timeout(1000)

            # Re-open same category
            category_headers = page.locator(".re-revamp-v4-category-header")
            category_headers.nth(c_index).click()
            page.wait_for_timeout(1000)

            bikes_locator = page.locator(
                f"(//div[contains(@class,'re-revamp-v4-category-content')])[{c_index + 1}]"
                f"//div[contains(@class,'re-revamp-v4-bike-thumbnail')]"
            )

            bike = bikes_locator.nth(b_index)
            bike_name = bike.get_attribute("aria-label")
            logger.info(f" Clicking bike: {bike_name}")
            bike.click()
            time.sleep(2)
            
        

    logger.info("\n All categories & bikes processed")


def main ():
    data = []
    # logger = setup_logger()
    try:
        
        # logger.info("start driver")
        page, browser = init_driver_playwrite() 
        try:
            bike(page)
        except Exception as e:
            logger.error("ERROR---------------", exc_info=True)
        # fetch_data_today(file_name)
        
    except Exception as e :
        logger.error("Main error", exc_info=True)
main()