import django.conf

import openai
from django.conf import settings
openai.api_key = settings.OPENAI_API_KEY

"""
Prompts example:
    [
        {"role": "system",
         "content": "You are AI tool with highly experienced Customer experience skills and  
         a helpful assistant. EXTRA DETAIL ABOUT company."},
        {"role": "assistant", "content": f"These are the ....."},
        {"role": "user", "content": f"Give me:\n...."}
    ]
"""


def create_request(prompts: list) -> object:

    main_prompt = [
            {"role": "system",
             "content": "You are AI tool with highly experienced Customer experience skills and  a helpful assistant. "
                        "EXTRA DETAIL ABOUT company."}
        ]

    main_prompt.extend(prompts)

    response = openai.ChatCompletion.create(
        model="gpt-4",
        max_tokens=1000,
        messages=main_prompt
    )

    return response
