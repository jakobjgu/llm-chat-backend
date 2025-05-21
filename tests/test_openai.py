from utils.openai_client import get_openai_response

if __name__ == "__main__":
    test_message = "What is the capital of Kenya?"
    response = get_openai_response(test_message)
    print("Assistant:", response)