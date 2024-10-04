import os
import logging
import re
import requests
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

user_description = ''

def generate_compliment(description):
    """Generate a compliment based on the description using OpenAI."""
    PROMPT_MESSAGES = [
        {
            "role": "system",
            "content": (
                """
                You are an expert assistant who creates personalized one-liner compliments that seamlessly follow a response. Your compliments should feel like a natural continuation, focusing on the person's attire and overall presence. The compliment should be concise, thoughtful, and tailored based on their appearance, exuding warmth and sincerity.

               - Compliment their **attire**, highlighting any specific details or qualities that stand out.
               - Make sure the compliment flows as the final line of a response, sounding natural and like a graceful conclusion.
               - The tone should be warm, uplifting, and appreciative, leaving a memorable, positive impression.
               """
            )
        },
        {
            "role": "user",
            "content": f"Here is a description of the person: {description}. Compliment them accordingly."
        }
    ]

    params = {
        "model": "gpt-4o-mini",
        "messages": PROMPT_MESSAGES,
        "temperature": 0.7,
        "top_p": 1,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.6,
    }

    result = client.chat.completions.create(**params)
    compliment = result.choices[0].message.content
    return compliment


def process_compliment(image_url):

    """Analyze the image and generate a compliment based on its description."""
    
    params = {
        "model": "gpt-4o-mini",
        "messages": [{
            "role": "system",
            "content": (
                """
                Analyze the customer's facial expression and provide a detailed assessment based on their demeanor.
                Evaluate the following aspects based on the customer's appearance and provide output in the format below (strictly follow the format):

                - Attire: {Describe the customer’s clothing and style in detail}
                - Gender: {Male, Female, Other}
                """
            ),
        },

    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Analyze the person in this image"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{image_url}"
          }
        }
      ]
    }
  ],
        "temperature": 0.1,
        "top_p": 1,
        "frequency_penalty": 0.2,
        "presence_penalty": 0.1,
    }

    result = client.chat.completions.create(**params)
    description = result.choices[0].message.content
    parsed_description = parse_description(description)

    compliment = generate_compliment(parsed_description)
    
    logging.info(f"\nDescription:\n{parsed_description}")
    # print(f"\nCompliment:\n{compliment}")
    logging.info(f"\n{compliment}")
    with open('user_description.txt', 'w') as file:
        file.write(compliment)


def process_document(image_url):
    """Analyze the document image and extract information."""

    params = {
        "model": "gpt-4o-mini",
        "messages": [{
            "role": "system",
            "content": (
                """
                You are a highly accurate and precise document verification assistant. Your task is to extract **only the information** visible in the provided document image and present it in a well-formatted, structured manner.

                **Instructions**:
                - Extract **only** the information from the document exactly as it appears.
                - **Do not infer or guess** any information that is unclear or missing.
                - Maintain the **original sequence** and **format** of the data as closely as possible to how it appears in the document.
                - If the document contains **tables, lists, or sections**, replicate them in your output, ensuring to format them properly for clarity.
                - If any information is **unclear or illegible**, indicate this by marking it as `[unreadable]`.
                """
            ),
        },

    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Extract information from this document image"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{image_url}"
          }
        }
      ]
    }
  ],
        "temperature": 0.1,
        "top_p": 1,
        "frequency_penalty": 0.2,
        "presence_penalty": 0.1,
    }

    result = client.chat.completions.create(**params)
    description = result.choices[0].message.content
    print(f"\nExtracted document information:\n{description}")

def parse_description(description):
    """Parse the description into a dictionary format."""
    parsed_data = {}
    try:
        parsed_data["Attire"] = re.search(r"Attire:\s*([\w\s,]+)", description).group(1).strip() if re.search(r"Attire:\s*([\w\s,]+)", description) else "Unknown"
        parsed_data["Gender"] = re.search(r"Gender:\s*([\w]+)", description).group(1).strip() if re.search(r"Gender:\s*([\w]+)", description) else "Unknown"
    except AttributeError as e:
        logger.error(f"Error parsing description: {e}")

    return parsed_data


