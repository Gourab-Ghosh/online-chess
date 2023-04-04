from credentials import USERNAME, PASSWORD
from classes import LichessBrowser, ChessDotComBrowser

browser = ChessDotComBrowser()
# browser = LichessBrowser()
# browser.login(USERNAME, PASSWORD)
browser.start_game()
while True:
    try:
        browser.driver.find_element_by_css_selector(".create-game-component")
    except:
        break
browser.board.play_game()