import requests
import html
import random

def get_session_token():
    """Retrieve a session token from the Open Trivia Database API."""
    try:
        response = requests.get("https://opentdb.com/api_token.php?command=request")
        data = response.json()
        if data["response_code"] == 0:
            return data["token"]
        else:
            print("Failed to retrieve session token.")
            return None
    except requests.RequestException as e:
        print(f"Error fetching session token: {e}")
        return None

def fetch_trivia_questions(amount=10, category=None, difficulty=None, type="multiple", token=None):
    """Fetch trivia questions from the Open Trivia Database API."""
    base_url = "https://opentdb.com/api.php"
    params = {
        "amount": amount,
        "type": type
    }
    if category:
        params["category"] = category
    if difficulty:
        params["difficulty"] = difficulty
    if token:
        params["token"] = token

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error fetching questions: {e}")
        return None

def decode_html(text):
    """Decode HTML-encoded text."""
    return html.unescape(text)

def display_question(question_data, question_number):
    """Display a trivia question and its answer options, then get user's answer."""
    question = decode_html(question_data["question"])
    correct_answer = decode_html(question_data["correct_answer"])
    incorrect_answers = [decode_html(ans) for ans in question_data["incorrect_answers"]]
    
    # Combine and shuffle answers
    all_answers = incorrect_answers + [correct_answer]
    random.shuffle(all_answers)
    
    print(f"\nQuestion {question_number}: {question}")
    for i, answer in enumerate(all_answers, 1):
        print(f"{i}. {answer}")
    
    # Get user's answer
    while True:
        try:
            user_input = input("\nEnter the number of your answer (1-4): ")
            user_answer = int(user_input)
            if 1 <= user_answer <= 4:
                return all_answers[user_answer - 1], correct_answer
            else:
                print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 4.")

def main():
    print("Welcome to the Trivia Game!")
    
    # Get session token to avoid duplicate questions
    token = get_session_token()
    if not token:
        print("Cannot proceed without a session token. Exiting.")
        return
    
    # Ask user for preferences
    try:
        num_questions = int(input("How many questions would you like (1-50)? "))
        if not 1 <= num_questions <= 50:
            print("Number of questions must be between 1 and 50. Defaulting to 10.")
            num_questions = 10
    except ValueError:
        print("Invalid input. Defaulting to 10 questions.")
        num_questions = 10
    
    # Fetch questions
    data = fetch_trivia_questions(amount=num_questions, type="multiple", token=token)
    
    if not data or data["response_code"] != 0:
        print("Error fetching questions. Response code:", data.get("response_code", "Unknown"))
        if data:
            if data["response_code"] == 1:
                print("Not enough questions for your query.")
            elif data["response_code"] == 2:
                print("Invalid parameter in the request.")
            elif data["response_code"] == 3:
                print("Session token not found.")
            elif data["response_code"] == 4:
                print("Session token has returned all possible questions. Please reset the token.")
            elif data["response_code"] == 5:
                print("Rate limit exceeded. Please wait and try again.")
        return
    
    questions = data["results"]
    score = 0
    
    # Present questions to the user
    for i, question in enumerate(questions, 1):
        user_answer, correct_answer = display_question(question, i)
        if user_answer == correct_answer:
            print("Correct!")
            score += 1
        else:
            print(f"Incorrect. The correct answer was: {correct_answer}")
    
    print(f"\nGame Over! Your score: {score}/{num_questions} ({score/num_questions*100:.1f}%)")
    
    # Ask if the user wants to play again
    play_again = input("\nWould you like to play again? (yes/no): ").lower()
    if play_again == "yes":
        main()

if __name__ == "__main__":
    main()