import os, json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class deepReseacher:
    def __init__(self):
        self.prompt = """"You are given a company's details.
Your task is to search for recent news articles regarding the client that cover topics such as mergers, acquisitions, lawsuits, and product launches.
Also, identify industry-specific updates, including changes in tax laws and regulatory shifts, that may impact the client or their industry.
Focus on collecting a comprehensive set of articles related to the client's recent activities and industry changes.

The research and final detailed report should be such as if created by a top-tier consultancy firm specializing in corporate intelligence and market analysis.
MY CONSULTANCY FIRM NAME:- KNAV CPA

(ALL SEARCH ARTICLES SHOULD NOT BE MORE THAN 12 MONTHS OLD)

1. Filter results to ensure they are recent and credible.
2. Classify findings into categories: client-related news (e.g., mergers, acquisitions, lawsuits, product launches) and industry-specific updates (e.g., tax law changes, regulatory shifts).

FOLLOW the given structure for your report generation:-
# Summarization
    - Condense long articles, reports, or posts into detailed, informative summaries (e.g., 8-10 sentences).
    - Example: "Acme Corp announced a merger with XYZ Inc. last week, expected to boost market share by 15%."
# Key Point Extraction
    - Pull out critical facts or figures (e.g., "Revenue up 10%," "New CEO appointed").
    - For financial data, calculate trends (e.g., "Profit margins down 5% from last quarter").
# Sentiment Analysis
    - Gauge public or social media perception (e.g., "Positive sentiment around Acme's new product launch").
# News Insights
    - Acme Corp launched a new product—ask about its impact on revenue forecasts.
# Financial Insights
    - Profit margins declined—discuss cost-cutting strategies.


MAKE SURE ALL SECTIONS / SUBSECTIONS ARE DOCUMENTED IN A DETAILED AN INFORMATIVE MANNER.
YOU CAN ADD MORE SECTIONS / SUBSECTIONS TO THIS STRUCTURE, IF REPORT IS MISSING ESSENTIAL PARTS FOR A DETAILED AND COMPLETE REPORT.
MAKE SURE YOUR REPORT IS COMPLETE, HIGHLY DETAILED AND INFORMATIVE, AND ATLEAST 10000 WORDS.

([In real use, include a longer and more specific textual content reflecting actual recent news based on the client and industry context.])

COMPANY DETAILS:-
"""

        client = genai.Client(
            api_key = os.getenv("GEMINI_API_KEY"),
        )

        self.model_name = "gemini-2.0-flash"
        # self.model_name = "gemini-2.5-pro-preview-03-25"
        generation_config = {
            "temperature": 1.0,
            "top_p": 0.95,
            "top_k": 40,
            "seed": 50,
            "max_output_tokens": 1024 * 64,
            "response_modalities": ["TEXT"],
        }

        tools = [
            types.Tool(google_search = types.GoogleSearch())
        ]

        generation_content_config = types.GenerateContentConfig(
            tools = tools,
            temperature = generation_config["temperature"],
            top_p = generation_config["top_p"],
            top_k = generation_config["top_k"],
            seed = generation_config["seed"],
            max_output_tokens = generation_config["max_output_tokens"],
            response_modalities = generation_config["response_modalities"],
        )

        self.chat = client.chats.create(
            model = self.model_name,
            config = generation_content_config
        )

    def calculate_cost(self, input_tokens, output_tokens, model):
        # Define pricing
        pricing_pro = {
            "input": {"under_200k": 1.25 / 1_000_000, "over_200k": 2.50 / 1_000_000},
            "output": {"under_200k": 10.00 / 1_000_000, "over_200k": 15.00 / 1_000_000}
        }

        pricing_flash = {
            "input": {"under_200k": 0.1 / 1_000_000, "over_200k": 0.4 / 1_000_000},
            "output": {"under_200k": 0.1 / 1_000_000, "over_200k": 0.4 / 1_000_000}
        }

        pricing = pricing_flash if "flash" in model else pricing_pro

        def get_cost(input_tokens, output_tokens):
            if input_tokens <= 128_000:
                input_cost = input_tokens * pricing["input"]["under_200k"]
                output_cost = output_tokens * pricing["output"]["under_200k"]
            else:
                input_cost = input_tokens * pricing["input"]["over_200k"]
                output_cost = output_tokens * pricing["output"]["over_200k"]
            return input_cost + output_cost

        return get_cost(input_tokens, output_tokens)

    def process_template(self, template_json = None, message = None):
        try:
            if template_json:
                response = self.chat.send_message([self.prompt + json.dumps(template_json, indent = 4)])
            else:
                response = self.chat.send_message([message])

            print("Cost:- $", self.calculate_cost(response.usage_metadata.prompt_token_count, response.usage_metadata.candidates_token_count, self.model_name))
        except:
            response = None

        try:
            source_urls = [cit.uri for cit in response.candidates[0].citation_metadata.citations]
        except:
            source_urls = []

        response = response.text

        return response, source_urls
