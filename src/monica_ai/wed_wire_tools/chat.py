from browser_use import Flow, step, run_flow
from typing import List
import time


class WeddingWireChatFlow(Flow):
    def __init__(self, venue_name: str, message_text: str = None):
        super().__init__()
        self.venue_name = venue_name
        self.message_text = message_text
        self.chat_history = []

    @step()
    def go_to_inbox(self):
        self.page.goto("https://www.weddingwire.com/inbox")
        self.page.wait_for_selector(
            "input[placeholder='Search messages']", timeout=15000
        )

    @step()
    def search_venue(self):
        search_input = self.page.locator("input[placeholder='Search messages']")
        search_input.fill(self.venue_name)
        time.sleep(2)

        venue_entry = self.page.locator(
            f"//span[contains(text(), '{self.venue_name}')]"
        )
        venue_entry.click()
        self.page.wait_for_selector("div[class*='ThreadMessage']", timeout=10000)

    @step()
    def extract_chat(self):
        bubbles = self.page.locator("div[class*='ThreadMessage']")
        count = bubbles.count()
        for i in range(count):
            msg = bubbles.nth(i).inner_text()
            self.chat_history.append(msg.strip())

    @step(condition=lambda self: self.message_text is not None)
    def send_message(self):
        reply_box = self.page.locator("textarea[placeholder^='Reply to']")
        reply_box.fill(self.message_text)
        reply_box.press("Enter")
        time.sleep(1)

    def get_chat(self) -> List[str]:
        return self.chat_history
