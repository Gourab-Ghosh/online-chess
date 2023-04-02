import time, chess, string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class Driver:

    def __init__(self, driver = None) -> None:
        if driver is None:
            driver = webdriver.Firefox()
            driver.maximize_window()
        self.driver = driver

    def find_element(self, by: By, value: str, wait_time: int = 60) -> None:
        if wait_time == 0:
            return self.driver.find_element(by, value)
        return WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located((by, value)))

    def wait(self, wait_time: int = 3) -> None:
        time.sleep(wait_time)

class Piece(Driver):
    pass

class Square(Driver):
    pass

class Board(Driver):
    pass

class ChessDotComBoard(Board):
    
    def get_piece_unordered_map(self):
        pieces = self.driver.find_elements(By.CLASS_NAME, "piece")
        piece_map = {}
        for piece in pieces:
            try:
                classes = piece.get_attribute("class").strip().split(" ")
                detail = position = None
                for cls in classes:
                    if len(cls) == 2 and cls[0] in "wb" and cls[1] in "pnbrqk":
                        detail = cls
                    if cls.startswith("square"):
                        position = cls
                if detail is None or position is None:
                    return self.get_piece_unordered_map()
            except:
                return self.get_piece_unordered_map()
            row, col = tuple(int(i) for i in position[-2:])
            piece_symbol = detail[1].upper() if detail[0] == "w" else detail[1].lower()
            piece = chess.Piece.from_symbol(piece_symbol)
            square = getattr(chess, f"{string.ascii_uppercase[row-1]}{col}")
            piece_map[square] = piece
        return piece_map

class Browser(Driver):

    def __init__(self) -> None:
        super().__init__()
        self.board = Board(self.driver)
        self._logged_in = False
        self.set_ids_and_css()
    
    def set_ids_and_css(self) -> None:
        raise NotImplemented

    def goto(self, url: str) -> None:
        self.driver.get(url)

    def login(self, username: str, password: str) -> None:
        if None in [self.login_page_link_selector, self.username_input_selector, self.password_input_selector, self.login_button_selector]:
            raise NotImplementedError
        login_page_link = self.find_element(*self.login_page_link_selector)
        login_page_link.click()
        username_input = self.find_element(*self.username_input_selector)
        username_input.send_keys(username)
        password_input = self.find_element(*self.password_input_selector)
        password_input.send_keys(password)
        login_button = self.find_element(*self.login_button_selector)
        login_button.click()
        self._logged_in = True

class ChessDotComBrowser(Browser):
    
    def __init__(self) -> None:
        super().__init__()
        self.goto('https://www.chess.com')
    
    def set_ids_and_css(self) -> None:
        self.login_page_link_selector = (By.LINK_TEXT, "Log In")
        self.username_input_selector = (By.ID, "username")
        self.password_input_selector = (By.ID, "password")
        self.login_button_selector = (By.ID, "login")
        self.play_button_selector = (By.CSS_SELECTOR, ".ui_v5-button-component.ui_v5-button-primary.ui_v5-button-large.ui_v5-button-full")

    def start_game(self, click_play_button = True):
        # "move-list"
        play_link1 = self.find_element(By.LINK_TEXT, "Play")
        play_link1.click()
        play_link2 = self.find_element(By.PARTIAL_LINK_TEXT, "Play Online")
        play_link2.click()
        if click_play_button:
            self.wait()
            play_button = self.find_element(*self.play_button_selector)
            play_button.click()
            if not self._logged_in:
                play_as_guest_button = self.find_element(By.ID, "guest-button")
                authentication_levels = self.driver.find_elements(By.CLASS_NAME, "authentication-intro-level")
                authentication_level = authentication_levels[-1]
                authentication_level.click()
                play_as_guest_button.click()
                play_button = self.find_element(*self.play_button_selector)
                play_button.click()

class LichessBrowser(Browser):
    
    def __init__(self) -> None:
        super().__init__()
        self.goto('https://lichess.org')
    
    def set_ids_and_css(self) -> None:
        self.login_page_link_selector = (By.LINK_TEXT, "SIGN IN")
        self.username_input_selector = (By.ID, "form3-username")
        self.password_input_selector = (By.ID, "form3-password")
        self.login_button_selector = (By.CSS_SELECTOR, ".submit.button")