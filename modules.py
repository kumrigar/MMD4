import openai

def get_openai_response(prompt):
    openai.api_key = 'sk-proj-f8bL6T3zc8airViV5XzcT3BlbkFJWOKimruuQDk3UPOu3zfy'  # Replace with your OpenAI API key
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # Using a chat-based model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens = 500  # Adjust the token count as needed
    )
    return response.choices[0].message.content

#Randomly pick a prompt for email generation from the prompt dataframe and save it in a variable. 
def get_random_prompt(prompt_data):
    # Randomly select one row from the prompt_data DataFrame
    prompt_row = prompt_data.sample(n=1).iloc[0]
    # Extract the prompt text from the selected row
    random_prompt = prompt_row['Prompt']
    return random_prompt