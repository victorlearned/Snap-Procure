#!/usr/bin/env python
import sys
from datetime import datetime
from snap_procure.crew import SnapProcure


def run():
    """
    Entry point for interactive chat mode.
    Every user message is routed to the chat task via kickoff.
    """
    bot = SnapProcure()
    crew = bot.crew()
    
    print("\n🤖 SnapProcure Chatbot: assisting general contractors! "
          "(type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            sys.exit(0)

        # Use kickoff with the user_request input
        try:
            reply = crew.kickoff(
                inputs={
                    "user_request": user_input
                }
            )
            print(f"Bot: {reply}\n")
        except Exception as e:
            print(f"⚠️  Error generating reply: {e}", file=sys.stderr)
            sys.exit(1)

# def run():
#     """
#     Run the procurement crew.
#     This is the main entry point for the CrewAI CLI.
#     """
#     # Default values if not provided
#     product = os.environ.get('PRODUCT', '2x4x8 lumber')
#     quantity = int(os.environ.get('QUANTITY', 1))
#     max_delivery_days = int(os.environ.get('MAX_DELIVERY_DAYS', '7'))  # Default to 7 days

#     inputs = {
#         'product': product,
#         'quantity': quantity,
#         'max_delivery_days': max_delivery_days,
#         'current_date': datetime.now().strftime('%Y-%m-%d')
#     }

#     print(f"\n🔍 Searching for: {quantity}x {product}")
#     print("This may take a minute...\n")

#     try:
#         # Run the procurement workflow
#         result = SnapProcure().crew().kickoff(inputs=inputs)
#         print("\n✅ Procurement analysis complete!")
#         print(f"📄 Check the 'data' directory for the full report and recommendations.")
#         return result
#     except Exception as e:
#         print(f"\n❌ An error occurred: {e}", file=sys.stderr)
#         sys.exit(1)

# For backward compatibility
def replay():
    """Replay the crew execution from a specific task."""
    try:
        if len(sys.argv) < 2:
            print("Please provide a task ID to replay")
            sys.exit(1)
        SnapProcure().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        SnapProcure().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    run()
