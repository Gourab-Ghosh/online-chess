import time, chess, string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from rich.traceback import install
from timecat import Timecat

try:
    from credentials import USERNAME, PASSWORD
except:
    USERNAME = PASSWORD = None

install()

inf = float("inf")

# class Timecat:
    
#     def __init__(self) -> None:
#         self.board = chess.Board()
    
#     def apply_move(self, uci: str):
#         self.board.push_uci(uci)
    
#     def get_best_move(self) -> chess.Move:
#         import random
#         return random.choice(tuple(self.board.legal_moves)).uci()

class Driver:

    def __init__(self, driver = None) -> None:
        if driver is None:
            driver = webdriver.Firefox()
            driver.maximize_window()
        self.driver = driver

    def find_element(self, by: By, value: str, wait_time: int = 60):
        if wait_time == 0:
            return self.driver.find_element(by, value)
        return WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located((by, value)))

    def find_elements(self, by: By, value: str, wait_time: int = 60): # Incomplete
        if wait_time == 0:
            return self.driver.find_elements(by, value)
        return self.driver.find_elements(by, value)

    def wait(self, wait_time: int = 1) -> None:
        time.sleep(wait_time)
    
    def click(self, element, wait_time = 5):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        if wait_time == 0:
            try:
                element.click()
            except Exception as e:
                print(e)
                self.driver.execute_script("arguments[0].click();", element)
            return
        start_time = time.time()
        while time.time() - start_time < wait_time:
            try:
                element.click()
            except Exception as e:
                print(e)
            else:
                return
        self.driver.execute_script("arguments[0].click();", element)

class Piece(Driver):
    pass

class Square(Driver):
    pass

class Board(Driver):
    
    def __init__(self, driver=None, auto_decline_draw=True) -> None:
        super().__init__(driver)
        self.board = chess.Board()
        self.bot = Timecat()
        self.auto_decline_draw = auto_decline_draw

class ChessDotComBoard(Board):

    def __init__(self, driver) -> None:
        super().__init__(driver)

    def scan_board(self):
        self.chess_board = self.find_element(By.TAG_NAME, "chess-board")

    def get_piece_map(self):
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
                    return self.get_piece_map()
            except:
                return self.get_piece_map()
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
            promotion_piece_css_selector = ".promotion-piece.{}{}".format(
                "w" if self.board.turn else 'b',
                " pkbrqk"[promotion],
            )
            promotion_piece = self.find_element(By.CSS_SELECTOR, promotion_piece_css_selector)
            self.click(promotion_piece)
        self.wait_while_dragging_piece()

    def is_game_over(self):
        if self.is_puzzle_rush_over():
            return True
        for css_selector in [".game-over-modal-content", ".board-modal-modal"]:
            try:
                self.find_element(By.CSS_SELECTOR, css_selector, 0)
            except:
                pass
            else:
                return True
        is_game_over = False
        outcome = self.board.outcome()
        if outcome is not None:
            is_game_over = outcome.termination in [getattr(chess.Termination, attr) for attr in [
                "VARIANT_LOSS",
                "VARIANT_WIN",
                "VARIANT_DRAW",
                "CHECKMATE",
                "INSUFFICIENT_MATERIAL",
                "STALEMATE",
            ]]
        return is_game_over or self.board.is_repetition(3) or self.board.is_fifty_moves()

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
        self.board.push(move)
        self.bot.apply_move(move.uci())

    def move_list(self, wait_time = 60):
        if wait_time == 0:
            try:
                return self.find_element(By.ID, "move-list", 0)
            except:
                try:
                    return self.find_element(By.CLASS_NAME, "play-controller-moves-container", 0)
                except:
                    return
        start_time = time.time()
        while time.time() - start_time < wait_time:
            try:
                return self.find_element(By.ID, "move-list", 0)
            except:
                try:
                    return self.find_element(By.CLASS_NAME, "play-controller-moves-container", 0)
                except:
                    pass
        raise Exception("Move list not found after waiting for {} seconds".format(wait_time))

    def reset(self):
        self.board.reset()
        self.bot.reset()
    
    def set_fen(self, fen):
        self.board.set_fen(fen)
        self.bot.set_fen(fen)

    def set_pre_play_constants(self):
        self.reset()
        self.chess_board = self.find_element(By.TAG_NAME, "wc-chess-board")
        self.is_flipped = "flipped" in self.chess_board.get_attribute("class")
        print(f"Board flipped: {self.is_flipped}")

    def get_draw_buttons(self):
        return self.find_elements(By.CLASS_NAME, "draw-offer-button")

    def accept_draw(self):
        self.click(self.get_draw_buttons()[-1], 0)

    def decline_draw(self):
        self.click(self.get_draw_buttons()[0], 0)

    def get_ply(self) -> int:
        try:
            moves = self.move_list(0).find_elements(By.CLASS_NAME, "node")
        except:
            if self.auto_decline_draw:
                try:
                    self.decline_draw()
                except:
                    return
                return self.get_ply()
            return
        return len(moves)

    def wait_while_dragging_piece(self):
        while any("dragging" in i.get_attribute("class") for i in self.find_elements(By.CLASS_NAME, "piece")):
            pass

    def detect_move(self, wait_for_move = True, num_retries = 3):
        if num_retries == 0:
            return
        if wait_for_move:
            while True:
                self.wait_while_dragging_piece()
                if self.is_game_over():
                    return
                if self.board.piece_map() != self.get_piece_map():
                    break
        curr_piece_map = self.get_piece_map()
        for move in self.board.legal_moves:
            self.board.push(move)
            try:
                if self.board.piece_map() == curr_piece_map:
                    return move
            finally:
                self.board.pop()
        if self.is_game_over():
            return
        return self.detect_move(False, num_retries - 1)

    def parse_move(self, move):
        if isinstance(move, chess.Move):
            return move
        try:
            return self.board.parse_san(move)
        except:
            return chess.Move.from_uci(move)

    def get_fen_from_piece_map(self, turn = None, castling_squares = (), en_passant = None, halfmove_clock = None, fullmove_number = None):
        piece_map = self.get_piece_map()
        board = chess.Board()
        board.clear()
        for square, piece in piece_map.items():
            board.set_piece_at(square, piece)
        castling_rights = 0
        for square in castling_squares:
            castling_rights |= chess.BB_SQUARES[square]
        if fullmove_number is None:
            fullmove_number = self.get_ply()
        for attr, value in [
            ("turn", turn),
            ("castling_rights", castling_rights),
            ("ep_square", en_passant),
            ("halfmove_clock", halfmove_clock),
            ("fullmove_number", fullmove_number),
        ]:
            if value is not None:
                setattr(board, attr, value)
        return board.fen()

    def play_game(self, starting_fen = None, wait_for_move_list = True):
        if wait_for_move_list:
            self.move_list(inf)
        self.set_pre_play_constants()
        if starting_fen:
            self.set_fen(starting_fen)
        else:
            self.reset()
        print("Started Playing...")
        bot_color = not self.is_flipped
        if self.board.turn != bot_color:
            move = self.detect_move(False)
            if move is not None:
                self.push(move, False)
        while True:
            if self.is_game_over():
                print("Game is over!")
                break
            bot_turn = self.board.turn == bot_color
            move = self.parse_move(self.bot.get_best_move()) if bot_turn else self.detect_move()
            if move is None:
                print("Got None as move")
                break
            self.push(move, bot_turn)
    
    def play_puzzle_rush_once(self):
        turn = "white" in self.find_element(By.CSS_SELECTOR, ".section-heading-title.section-heading-normal").text.lower()
        self.play_game(self.get_fen_from_piece_map(turn = turn), False)

    def is_puzzle_rush_over(self):
        try:
            self.find_element(By.CSS_SELECTOR, ".modal-chessboard-container-next-component", 0)
        except:
            return False
        return True

    def play_puzzle_rush(self):
        while True:
            self.play_puzzle_rush_once()
            self.wait()
            self.wait_while_dragging_piece()
            if self.is_puzzle_rush_over():
                break

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
        self.click(login_page_link)
        username_input = self.find_element(*self.username_input_selector)
        username_input.send_keys(username)
        password_input = self.find_element(*self.password_input_selector)
        password_input.send_keys(password)
        login_button = self.find_element(*self.login_button_selector)
        self.click(login_button)
        self._logged_in = True

class ChessDotComBrowser(Browser):
    
    def __init__(self) -> None:
        super().__init__()
        self.goto('https://www.chess.com')
    
    def set_ids_and_css(self) -> None:
        self.board = ChessDotComBoard(self.driver)
        self.login_page_link_selector = (By.LINK_TEXT, "Log In")
        self.username_input_selector = (By.CSS_SELECTOR, ".cc-input-component.cc-input-group-space-prepend")
        self.password_input_selector = (By.CSS_SELECTOR, ".cc-input-component.cc-input-group-space-prepend.cc-input-group-space-append")
        self.login_button_selector = (By.ID, "login")
        self.play_button_selector = (By.CSS_SELECTOR, ".ui_v5-button-component.ui_v5-button-primary.ui_v5-button-large.ui_v5-button-full")

    def start_game(self, click_play_button = True):
        play_link1 = self.find_element(By.LINK_TEXT, "Play")
        self.click(play_link1)
        play_link2 = self.find_element(By.PARTIAL_LINK_TEXT, "Play Online")
        self.click(play_link2)
        if click_play_button:
            play_button = self.find_element(*self.play_button_selector)
            self.click(play_button)
            if not self._logged_in:
                play_as_guest_button = self.find_element(By.ID, "guest-button")
                authentication_levels = self.find_elements(By.CLASS_NAME, "authentication-intro-level")
                authentication_level = authentication_levels[-1]
                self.click(authentication_level)
                self.click(play_as_guest_button)
                play_button = self.find_element(*self.play_button_selector)
                self.click(play_button)

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

def main():
    global browser
    browser = ChessDotComBrowser()
    # browser = LichessBrowser()
    if USERNAME is not None and PASSWORD is not None:
        browser.login(USERNAME, PASSWORD)
    browser.start_game()
    browser.board.play_game()