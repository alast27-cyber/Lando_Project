import unittest

from Lando_Project.chatbot.engine import OfflineChatbot


class OfflineChatbotTests(unittest.TestCase):
    def test_greeting_intent(self):
        bot = OfflineChatbot(seed=1)
        response = bot.respond("hello")
        self.assertTrue("hello" in response.lower() or "hi" in response.lower() or "hey" in response.lower())

    def test_name_capture_and_summary(self):
        bot = OfflineChatbot(seed=1)
        bot.respond("my name is Alex")
        summary = bot.respond("/summary")
        self.assertIn("Alex", summary)

    def test_coding_intent(self):
        bot = OfflineChatbot(seed=1)
        response = bot.respond("I need to debug this python bug")
        self.assertTrue("debug" in response.lower() or "test" in response.lower() or "coding" in response.lower())


if __name__ == "__main__":
    unittest.main()
