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

    def find_elements(self, by: By, value: str, wait_time: int = 60) -> None: # Incomplete
        if wait_time == 0:
            return self.driver.find_elements(by, value)
        return self.driver.find_elements(by, value)

    def wait(self, wait_time: int = 1) -> None:
        time.sleep(wait_time)

class Piece(Driver):
    pass

class Square(Driver):
    pass

class Board(Driver):
    
    def __init__(self, driver=None) -> None:
        super().__init__(driver)
        self.board = chess.Board()

class ChessDotComBoard(Board):

    def __init__(self, driver) -> None:
        super().__init__(driver)

    def scan_board(self):
        self.chess_board = self.find_element(By.TAG_NAME, "chess-board")

    def get_piece_unordered_map(self):
        pieces = self.find_elements(By.CLASS_NAME, "piece")
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

    def square_to_coordinate(self, square: int):
        row, col = divmod(square, 8)
        if self.is_flipped:
            col = 7-col
        else:
            row = 7-row
        rect = self.chess_board.rect
        x = rect["x"]
        y = rect["y"]
        width = rect["width"]
        height = rect["height"]
        single_cell_width, single_cell_height = width / 8, height / 8
        return (col + 0.5) * single_cell_width + x, (row + 0.5) * single_cell_height + y

    def move_piece(self, from_square: int, to_square: int, promotion: chess.PieceType = None):
        from_square_coord = self.square_to_coordinate(from_square)
        to_square_coord = self.square_to_coordinate(to_square)
        action = ActionChains(self.driver)
        offset = (j-i for i, j in zip(from_square_coord, to_square_coord))
        piece = self.find_element(By.CLASS_NAME, f"square-{from_square % 8 + 1}{from_square // 8 + 1}")
        action.drag_and_drop_by_offset(piece, *offset).perform()
        if promotion:
            promotion_piece_css_selector = f".promotion-piece.{'w' if self.board.turn else 'b'}{' pkbrqk'[promotion]}"
            promotion_piece = self.find_element(By.CSS_SELECTOR, promotion_piece_css_selector)
            promotion_piece.click()

    def is_game_over(self):
        return self.board.is_game_over()

    def push(self, move: chess.Move, drag: bool = True):
        if move == chess.Move.null():
            raise Exception
        self.board.san(move)
        if self.is_game_over():
            return
        if drag:
            if self.is_game_over():
                return
            self.move_piece(move.from_square, move.to_square, move.promotion)
        print(f"Move: {self.board.san(move)}")
        self.board.push(move)
        # self.bot.apply_move(move.uci())

    def set_pre_play_constants(self):
        self.move_list = self.find_element(By.ID, "move-list")
        self.chess_board = self.find_element(By.TAG_NAME, "chess-board")
        self.is_flipped = "flipped" in self.chess_board.get_attribute("class")
        print(f"Board flipped: {self.is_flipped}")
    
    def detect_move(self):
        # moves = self.move_list.find_elements(By.CLASS_NAME, "move")
        pass

    def play_game(self):
        self.set_pre_play_constants()
        print("Started Playing...")
        bot_color = not self.board_flipped
        # white_clock = self.find_element(By.CSS_SELECTOR, ".clock-white.player-clock")
        # black_clock = self.find_element(By.CSS_SELECTOR, ".clock-black.player-clock")
        # detect_move = lambda: self.detect_move(white_clock, black_clock)
        # while True:
        #     if self.is_game_over(True):
        #         break
        #     bot_turn = self.board.turn == bot_color
        #     bot_clock = white_clock if bot_color else black_clock
        #     opponent_clock = black_clock if bot_color else white_clock
        #     move = chess.Move.from_uci(self.bot.get_best_move(print_move = True, self_time_left = self.detect_time_left(bot_clock), opponent_time_left = self.detect_time_left(opponent_clock))) if bot_turn else detect_move()
        #     if move is None:
        #         break
        #     # move = chess.Move.from_uci(self.bot.get_best_move(debug=False)) if bot_turn else detect_move()
        #     self.push(move, bot_turn)

class LichessBoard(Board):
    pass

class Browser(Driver):

    def __init__(self) -> None:
        super().__init__()
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
        self.board = ChessDotComBoard(self.driver)
        self.login_page_link_selector = (By.LINK_TEXT, "Log In")
        self.username_input_selector = (By.ID, "username")
        self.password_input_selector = (By.ID, "password")
        self.login_button_selector = (By.ID, "login")
        self.play_button_selector = (By.CSS_SELECTOR, ".ui_v5-button-component.ui_v5-button-primary.ui_v5-button-large.ui_v5-button-full")

    def start_game(self, click_play_button = True):
        play_link1 = self.find_element(By.LINK_TEXT, "Play")
        play_link1.click()
        play_link2 = self.find_element(By.PARTIAL_LINK_TEXT, "Play Online")
        play_link2.click()
        if click_play_button:
            play_button = self.find_element(*self.play_button_selector)
            play_button.click()
            if not self._logged_in:
                play_as_guest_button = self.find_element(By.ID, "guest-button")
                authentication_levels = self.find_elements(By.CLASS_NAME, "authentication-intro-level")
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
        self.board = LichessBoard(self.driver)
        self.login_page_link_selector = (By.LINK_TEXT, "SIGN IN")
        self.username_input_selector = (By.ID, "form3-username")
        self.password_input_selector = (By.ID, "form3-password")
        self.login_button_selector = (By.CSS_SELECTOR, ".submit.button")