from backend.agent.llm_client import (
    LLMClient,
)


def main() -> None:
    llm = LLMClient()

    response = llm.generate(
        "You are NexCord, an event operations "
        "assistant. Explain in one sentence what "
        "you do."
    )

    print("Gemini response:")
    print(response)


if __name__ == "__main__":
    main()