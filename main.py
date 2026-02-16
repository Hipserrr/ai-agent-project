import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import argparse
from prompts import system_prompt
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file
from functions.call_function import call_function
#from functions.call_function import available_functions

def main():
    print("Hello from ai-agent!")
    available_functions = types.Tool(
        function_declarations=[schema_get_files_info, schema_get_file_content, schema_run_python_file, schema_write_file],
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
    for i in range(20):
        content_response = client.models.generate_content(model="gemini-2.5-flash", contents=messages, config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt))
        if content_response.usage_metadata == None:
            raise RuntimeError("Failed API request")
        for candidate in content_response.candidates:
            messages.append(candidate.content)

        function_results = []
        if args.verbose:
            print(f"User prompt: {args.user_prompt}\nPrompt tokens: {content_response.usage_metadata.prompt_token_count}\nResponse tokens:{content_response.usage_metadata.candidates_token_count}")
        if content_response.function_calls != None:
            for function_call in content_response.function_calls:
                function_call_result = call_function(function_call, verbose=False)
                if not isinstance(function_call_result.parts, list) or function_call_result == []:
                    raise ValueError("not a non empty list")
                if function_call_result.parts[0].function_response is None:
                    raise TypeError("function_response not a FunctionResponse object")
                if function_call_result.parts[0].function_response.response is None:
                    raise Exception("no response")
                function_results.append(function_call_result.parts[0])
                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
                # print(f"Calling function: {function_call.name}({function_call.args})")
            if i == 20:
                print("did not get a response in time")
                exit
        else:
            print(f"Response: {content_response.text}")
            break
        messages.append(types.Content(role="user", parts=function_results))

if __name__ == "__main__":
    main()
