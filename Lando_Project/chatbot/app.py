"""CLI entry point for the offline chatbot."""

from .engine import OfflineChatbot


def main() -> None:
    bot = OfflineChatbot()
    print("Offline Chatbot ready. Type '/help' for commands. Type 'quit' to exit.")
    print(f"Cognition mode: {bot.cognition_mode}")

    while True:
        try:
            user_input = input("you> ")
        except (EOFError, KeyboardInterrupt):
            print("\nbye>", bot.respond("bye"))
            break

        if user_input.strip().lower() in {"quit", "exit"}:
            print("bot>", bot.respond("bye"))
            break

        print("bot>", bot.respond(user_input))


if __name__ == "__main__":
    main()
