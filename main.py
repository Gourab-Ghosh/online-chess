# Remarkable Games:
# https://www.chess.com/game/live/74452837201
# https://www.chess.com/game/live/74634665629
# https://www.chess.com/game/live/74743923841
# https://www.chess.com/game/live/74823225147

from credentials import USERNAME, PASSWORD
from classes import LichessBrowser, ChessDotComBrowser

browser = ChessDotComBrowser()
# browser = LichessBrowser()
browser.login(USERNAME, PASSWORD)
browser.start_game()
browser.board.play_game()