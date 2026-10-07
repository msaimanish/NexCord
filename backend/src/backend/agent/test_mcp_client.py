from backend.agent.mcp_client import NexCordMCPClient


def main():
    client = NexCordMCPClient()

    result = client.call(
        "simulate_plan",
        {
            "plan_id": 2,
        },
    )

    print("MCP simulate_plan result:")
    print(result)


if __name__ == "__main__":
    main()
