from app.service import AfyaPlusService


def main() -> None:
    """
    Run the AfyaPlus assistant as an interactive
    command-line application.
    """
    service = AfyaPlusService()

    print("=" * 60)
    print("AfyaPlus Health Assistant")
    print("=" * 60)
    print(
        "Ask about AfyaPlus insurance, clinical routing, "
        "or medication calculations."
    )
    print("Type 'exit' to quit.")
    print("Type 'clear' to reset the conversation.")
    print()

    while True:
        try:
            user_message = input("You: ").strip()

            if not user_message:
                continue

            if user_message.lower() in {
                "exit",
                "quit",
            }:
                print("Goodbye.")
                break

            if user_message.lower() == "clear":
                service.clear_session()
                print("Conversation cleared.")
                continue

            response = service.process_message(
                user_message
            )

            print(f"\nAfyaPlus: {response}\n")

        except KeyboardInterrupt:
            print("\nGoodbye.")
            break

        except Exception as exc:
            print(
                "\nUnable to process your request: "
                f"{exc}\n"
            )


if __name__ == "__main__":
    main()