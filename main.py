import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import argparse
from prompts import system_prompt
from functions.get_files_info import schema_get_files_info
#from functions.call_function import available_functions

available_functions = types.Tool(
    function_declarations=[schema_get_files_info],
)

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User Prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if api_key == None:
    raise RuntimeError("No API key found")

messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
client = genai.Client(api_key=api_key)
content_response = client.models.generate_content(model="gemini-2.5-flash", contents=messages, config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt))
if content_response.usage_metadata == None:
    raise RuntimeError("Failed API request")

if args.verbose:
    print(f"User prompt: {args.user_prompt}\nPrompt tokens: {content_response.usage_metadata.prompt_token_count}\nResponse tokens:{content_response.usage_metadata.candidates_token_count}")
if content_response.function_calls != None:
    for function_call in content_response.function_calls:
        print(f"Calling function: {function_call.name}({function_call.args})")
else:
    print(f"Response: {content_response.text}")

def main():
    #print("Hello from ai-agent!")


if __name__ == "__main__":
    main()
