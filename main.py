from credentials import USERNAME, PASSWORD
from classes import LichessBrowser, ChessDotComBrowser

browser = ChessDotComBrowser()
# browser = LichessBrowser()
# browser.login(USERNAME, PASSWORD)
browser.start_game()