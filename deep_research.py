import os, json, time, re
from tqdm import tqdm
import concurrent.futures
from google import genai
from google.genai import types
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class deepReseacher:
    def __init__(self):
        self.analysis_grounding_prompt = f""""You are given a company's details.
Your task is to search for recent news articles regarding the client that cover topics such as mergers, acquisitions, lawsuits, and product launches.
Also, identify industry-specific updates, including changes in tax laws and regulatory shifts, that may impact the client or their industry.
Focus on collecting a comprehensive set of articles related to the client's recent activities and industry changes.

The research and final detailed report should be such as if created by a top-tier CPA firm specializing in corporate intelligence, market analysis and financial expertise.
MY CONSULTANCY FIRM NAME:- KNAV CPA

(ALL SEARCH ARTICLES SHOULD NOT BE MORE THAN 12 MONTHS OLD)
TODAY'S DATE - {datetime.today().strftime("%-d %B %Y")}

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
ONLY AND ONLY AFTER FULL REPORT IS GENERATED, APPEND THE TOKEN <CHARLIEWAFFLES> TO THE TEXT STREAM. SO THIS TOKEN WOULD BE THE LAST TOKEN OF YOUR GENERATION.

([In real use, include a longer and more specific textual content reflecting actual recent news based on the client and industry context.])

COMPANY DETAILS:-
"""

        self.DS_SYSTEM_CONTEMPLATION_PROMPT = """You are an assistant that engages in extremely thorough, self-questioning financial analysis, mirroring how an expert Certified Public Accountant / Chartered Accountant would think. Your approach should reflect a continuous exploration and iterative reasoning process, ensuring no detail is overlooked, and every possible angle is explored before arriving at a recommendation for a financial / accounting / consulting service.

## Core Principles
1. EXPLORATION OVER CONCLUSION
- Never rush to conclusions
- Keep exploring until a solution emerges naturally from the evidence
- If uncertain, continue reasoning indefinitely
- Question every assumption and inference

2. DEPTH OF REASONING
- Engage in extensive contemplation (minimum 10,000 characters)
- Express thoughts in natural, conversational internal monologue
- Break down complex thoughts into simple, atomic steps
- Embrace uncertainty and revision of previous thoughts

3. THINKING PROCESS
- Use short, simple sentences that mirror natural thought patterns
- Express uncertainty and internal debate freely
- Show work-in-progress thinking
- Acknowledge and explore dead ends
- Frequently backtrack and revise

4. PERSISTENCE
- Value thorough exploration over quick resolution

## Output Format for contemplator
Your contemplator responses must follow this exact structure given below. Make sure to always include the final answer.
```
<contemplator>
[Your extensive internal monologue goes here]
- Begin with small, foundational observations
- Question each step thoroughly
- Show natural thought progression
- Express doubts and uncertainties
- Revise and backtrack if you need to
- Continue until natural resolution
</contemplator>
```

You will be given:-
- a company document, which will have some information about the company financials, future plans, product information, communications, etc.
- a financial / accounting / consulting service on offer, in the tags <service_offered>.
- a juridiction country, in which the company operates, and the services are offered.

Your contemplation should revolve around the thoughts whether the <service_offered> will have an impact (postive or negative) on the company or not.
Your contemplation, reasoning, thoughts should all be highly relevant and valid for the provided jurisdiction country of the company.

INSTRUCTIONS:-
- YOU MUST FIRST GENERATE YOUR ENTIRE CONTEMPLATION, BY FOLLOWING THE CORE PRINCIPLES MENTIONED ABOVE.
- ONLY AFTER CLOSING </contemplator>, PROCEED WITH IMPACT SCORE AND DETAILED ANALYSIS REPORT.
- YOU MUST NOT ASSUME ANYTHING ABOUT THE COMPANY, ONLY CONSIDER FACTS AND KNOWLEDGE PRESENT IN THE COMPANY DOCUMENT.
- ONLY AND ONLY AFTER CONTEMPLATION, IMPACT SCORE AND DETAILED REASONING IS GENERATED, APPEND THE TOKEN <CHARLIEWAFFLES> TO THE TEXT STREAM. SO THIS TOKEN WOULD BE THE LAST TOKEN OF YOUR GENERATION.

impact_score - A IMPACT SCORE (1 - 10), which entails how big a impact would the service have on the company (1 being no impact / high uncertainity / not required by the company, 10 being an absolute big impact and the company definitely needs this service)
Use the tags shown below to give the impact_score.
<impact_score> </impact_score>

detailed_reasoning_report - an extremely detailed and informative reasoning report, with grounding to source knowledge and citations from the company document, as to why that service will help / not help the company, base on your thougths and contemplation. Provide a good structure to this report. Report must be minimum 1000 words.
Use the tags shown below to give the detailed_reasoning_report.
<detailed_reasoning_report> </detailed_reasoning_report>

summary_report - a detailed, and highly informative, summary of the detailed_reasoning_report. The summary should be very informative, and avoid platitudes. A general structure would be to start with helpfulness in just 1 line, and then HOW exactly the service will be helpful / not helpful to the company, in 300 words.
Use the tags shown below to give the summary_report.
<summary_report> </summary_report>

"""

        self.client = genai.Client(
            api_key = os.getenv("GEMINI_API_KEY"),
        )

        self.generation_config = {
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

        self.generation_content_config = types.GenerateContentConfig(
            tools = tools,
            temperature = self.generation_config["temperature"],
            top_p = self.generation_config["top_p"],
            top_k = self.generation_config["top_k"],
            seed = self.generation_config["seed"],
            max_output_tokens = self.generation_config["max_output_tokens"],
            response_modalities = self.generation_config["response_modalities"],
        )

        self.chat = None

        self.first_reply = None

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
    
    def extract_content_from_tags(self, text, tag_name):
        # Build a regex pattern dynamically based on the tag_name
        pattern = rf"<{tag_name}>(.*?)</{tag_name}>"
        
        # Use re.findall to extract all matches
        matches = re.findall(pattern, text, re.DOTALL)
        
        return matches[0] if matches else None

    def extract_and_custom_process_tags(self, response_text):
        impact_score = self.extract_content_from_tags(response_text, "impact_score")
        impact_score = impact_score if impact_score else -1
        try:
            impact_score = int(impact_score)
        except:
            impact_score = -1

        detailed_reasoning_report = self.extract_content_from_tags(response_text, "detailed_reasoning_report")
        detailed_reasoning_report = detailed_reasoning_report if detailed_reasoning_report else ""

        summary_report = self.extract_content_from_tags(response_text, "summary_report")
        summary_report = summary_report if summary_report else ""

        return {
            "impact_score": impact_score,
            "summary_report": summary_report,
            "detailed_reasoning_report": detailed_reasoning_report
        }
    
    def process_COATT_single_thread(self, document, service_data, model_name = "gemini-2.0-flash"):
        total_cost = 0
        start_time = time.time()

        # Initialize results dictionary to capture partial results
        results = {
            "status_code": 999,
            "total_cost": 0,
            "time_taken": None,
            "response": None,
            "response_parsed": None,
            "error": None,
        }

        # Step 1: Get available API key
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key == None:
                raise Exception("All APIs are busy, try again in some time.")
            # results["get_API_key"] = True
        except Exception as e:
            results["error"] = f"Fetching API key failed: {str(e)}"
            results["status_code"] = 401
            return results

        # Step 2: Initialize client
        try:
            client = genai.Client(api_key = api_key)
            # results["client_initialize"] = True
        except Exception as e:
            results["error"] = f"Client initialization failed: {str(e)}"
            results["status_code"] = 402
            return results

        # Step 4: Initialize chat
        try:
            chat = client.chats.create(
                model = model_name,
                config = types.GenerateContentConfig(
                    temperature = self.generation_config["temperature"],
                    top_p = self.generation_config["top_p"],
                    top_k = self.generation_config["top_k"],
                    seed = self.generation_config["seed"],
                    max_output_tokens = self.generation_config["max_output_tokens"],
                    response_modalities = self.generation_config["response_modalities"],
                )
            )
            # results["chat_initialization"] = True
        except Exception as e:
            results["error"] = f"Chat initialization failed: {str(e)}"
            results["status_code"] = 404
            return results

        # Step 5: Get Gemini response
        try:
            responses = []
            analysis_recommendation_response = chat.send_message([
                document,
                self.DS_SYSTEM_CONTEMPLATION_PROMPT + service_data
            ])

            total_cost += self.calculate_cost(
                analysis_recommendation_response.usage_metadata.prompt_token_count,
                analysis_recommendation_response.usage_metadata.candidates_token_count,
                model_name
            )

            responses.append(analysis_recommendation_response.text)

            # Handle continuation if "<CHARLIEWAFFLES>" not found
            continue_loop_limit = 2
            while "<CHARLIEWAFFLES>" not in responses[-1] and continue_loop_limit > 0:
                analysis_recommendation_response = chat.send_message(["""Continue exactly from where you left off."""])
                total_cost += self.calculate_cost(
                    analysis_recommendation_response.usage_metadata.prompt_token_count,
                    analysis_recommendation_response.usage_metadata.candidates_token_count,
                    model_name
                )
                responses.append(analysis_recommendation_response.text)
                continue_loop_limit -= 1

            responses = " ".join(responses)
            results["response"] = responses
            results["total_cost"] = total_cost
        except Exception as e:
            results["error"] = f"Response generation failed: {str(e)}"
            results["status_code"] = 405
            
        del client

        # Finalize time taken
        end_time = time.time()
        results["time_taken"] = end_time - start_time

        # All steps executed gracefully
        results["status_code"] = 200 if results["error"] == None else results["status_code"]

        # Return results, even if some steps failed
        return results

    def get_services_offered_data(self, services_json_path = "./services.json"):
        with open(services_json_path, 'r') as file:
            services_data = json.load(file)

        def structure_service(service_datapoint):
            service_structurised = ""
            service_structurised += f"<section>\n{service_datapoint['section']}\n</section>\n\n"
            service_structurised += f"<name>\n{service_datapoint['name']}\n</name>\n\n"
            service_structurised += f"<service_country>\n{service_datapoint['country']}\n</service_country>\n\n"
            service_structurised += f"<summary>\n{service_datapoint['summary']}\n</summary>\n\n"
            service_structurised += f"<sample_situations_and_high_level_prerequisites>\n{service_datapoint['situations']}\n</sample_situations_and_high_level_prerequisites>\n"
            return service_structurised

        SERVICES_DESCRIPTION = []

        for idx in range(1, len(services_data) + 1):
            SERVICES_DESCRIPTION.append("<service_offered>\n" + structure_service(services_data[idx-1]) + "</service_offered>\n")

        return SERVICES_DESCRIPTION, services_data

    def process_COATT_parallel(self, document, all_services_data, model_name="gemini-2.0-flash"):
        def process_with_retry(service_data):
            """
            Inner helper function that wraps process_COATT_single_thread with retry logic.
            """
            attempts = 0
            final_response = None

            while attempts < 2:
                try:
                    response = self.process_COATT_single_thread(document, service_data, model_name)
                    
                    # If no error in response, mark success and return
                    if response["error"] != None:
                        return response
                except:
                    response = {
                        "status_code": 999,
                        "total_cost": 0,
                        "time_taken": None,
                        "response": None,
                        "response_parsed": None,
                        "error": None,
                    }

                # If an error occurred, increment attempts and store last response
                attempts += 1
                final_response = response
                time.sleep(10)  # Wait before retrying

            return final_response

        results = [None] * len(all_services_data)  # Pre-allocate list with correct size
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            # Submit tasks to the executor and keep track of futures with their indices
            future_to_index = {
                executor.submit(process_with_retry, service_data): idx
                for idx, service_data in enumerate(all_services_data)
            }

            # Use tqdm to display progress
            for future in tqdm(concurrent.futures.as_completed(future_to_index), total=len(future_to_index), desc="Processing"):
                idx = future_to_index[future]
                try:
                    result = future.result()
                    results[idx] = result  # Place result at correct index
                except:
                    results[idx] = {
                        "status_code": 999,
                        "total_cost": 0,
                        "time_taken": None,
                        "response": None,
                        "response_parsed": None,
                        "error": None,
                    }

        # Post-processing results
        failed_requests = 0
        for idx, result in enumerate(results):
            try:
                # Parse response if available
                if result.get("response"):
                    response_parsed = self.extract_and_custom_process_tags(result["response"])
                    results[idx]["response_parsed"] = response_parsed
                else:
                    failed_requests += 1
            except:
                failed_requests += 1

        return results

    def generate_grounding_report(self, company_details, model_name):
        total_cost = 0
        start_time = time.time()

        # Initialize results dictionary to capture partial results
        results = {
            "status_code": 999,
            "total_cost": 0,
            "time_taken": None,
            "response": None,
            "response_parsed": None,
            "error": None,
        }

        # Step 1: Get available API key
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key == None:
                raise Exception("All APIs are busy, try again in some time.")
            # results["get_API_key"] = True
        except Exception as e:
            results["error"] = f"Fetching API key failed: {str(e)}"
            results["status_code"] = 401
            return results

        # Step 2: Initialize client
        try:
            client = genai.Client(api_key = api_key)
            # results["client_initialize"] = True
        except Exception as e:
            results["error"] = f"Client initialization failed: {str(e)}"
            results["status_code"] = 402
            return results

        # Step 4: Initialize chat
        try:
            chat = client.chats.create(
                model = model_name,
                config = types.GenerateContentConfig(
                    temperature = self.generation_config["temperature"],
                    top_p = self.generation_config["top_p"],
                    top_k = self.generation_config["top_k"],
                    seed = self.generation_config["seed"],
                    max_output_tokens = self.generation_config["max_output_tokens"],
                    response_modalities = self.generation_config["response_modalities"],
                )
            )
            # results["chat_initialization"] = True
        except Exception as e:
            results["error"] = f"Chat initialization failed: {str(e)}"
            results["status_code"] = 404
            return results
        
        # Step 5: Get Gemini response
        try:
            responses = []
            report_response = chat.send_message([
                self.analysis_grounding_prompt + json.dumps(company_details, indent = 4)
            ])

            total_cost += self.calculate_cost(
                report_response.usage_metadata.prompt_token_count,
                report_response.usage_metadata.candidates_token_count,
                model_name
            )

            responses.append(report_response.text)

            # Handle continuation if "<CHARLIEWAFFLES>" not found
            continue_loop_limit = 2
            while "<CHARLIEWAFFLES>" not in responses[-1] and continue_loop_limit > 0:
                report_response = chat.send_message(["""Continue exactly from where you left off."""])
                total_cost += self.calculate_cost(
                    report_response.usage_metadata.prompt_token_count,
                    report_response.usage_metadata.candidates_token_count,
                    model_name
                )
                responses.append(report_response.text)
                continue_loop_limit -= 1

            responses = " ".join(responses)
            results["response"] = responses
            results["total_cost"] = total_cost
        except Exception as e:
            results["error"] = f"Response generation failed: {str(e)}"
            results["status_code"] = 405

        del client

        # Finalize time taken
        end_time = time.time()
        results["time_taken"] = end_time - start_time

        # All steps executed gracefully
        results["status_code"] = 200 if results["error"] == None else results["status_code"]

        # Return results, even if some steps failed
        return results

    def generate_standard_response(self, message, model_name):
        total_cost = 0
        start_time = time.time()

        # Initialize results dictionary to capture partial results
        results = {
            "status_code": 999,
            "total_cost": 0,
            "time_taken": None,
            "response": None,
            "response_parsed": None,
            "error": None,
        }

        # Get Gemini response
        try:
            responses = []
            report_response = self.chat.send_message([
                message
            ])

            total_cost += self.calculate_cost(
                report_response.usage_metadata.prompt_token_count,
                report_response.usage_metadata.candidates_token_count,
                model_name
            )

            responses.append(report_response.text)

            # Handle continuation if "<CHARLIEWAFFLES>" not found
            continue_loop_limit = 2
            while "<CHARLIEWAFFLES>" not in responses[-1] and continue_loop_limit > 0:
                report_response = self.chat.send_message(["""Continue exactly from where you left off."""])
                total_cost += self.calculate_cost(
                    report_response.usage_metadata.prompt_token_count,
                    report_response.usage_metadata.candidates_token_count,
                    model_name
                )
                responses.append(report_response.text)
                continue_loop_limit -= 1

            responses = " ".join(responses)
            results["response"] = responses
            results["total_cost"] = total_cost
        except Exception as e:
            results["error"] = f"Response generation failed: {str(e)}"
            results["status_code"] = 405

        # Finalize time taken
        end_time = time.time()
        results["time_taken"] = end_time - start_time

        # All steps executed gracefully
        results["status_code"] = 200 if results["error"] == None else results["status_code"]

        # Return results, even if some steps failed
        return results
    
    def process_template(self, company_details = None, message = None):
        total_cost = 0

        if company_details:
            self.first_query = None
            self.first_reply = None

            report_results = self.generate_grounding_report(company_details, "gemini-2.5-pro-preview-03-25")

            print("Generated analysis report!")

            total_cost += report_results["total_cost"]
            print("Running Cost:- $", total_cost)

            report_results_response = report_results["response"]
            services_data, services_data_json = self.get_services_offered_data("services_usa.json")
            recommendations = self.process_COATT_parallel(report_results_response, services_data, "gemini-2.0-flash")

            total_cost += sum([dp["total_cost"] for dp in recommendations])
            print("Running Cost:- $", total_cost)

            for i in range(len(recommendations)):
                recommendations[i]["service_section"], recommendations[i]["service_name"] = services_data_json[i]["section"], services_data_json[i]["name"]

            self.first_query = self.analysis_grounding_prompt + json.dumps(company_details, indent = 4)
            self.first_reply = report_results_response + "\n\nRecommended Services:\n"
            for recom in recommendations:
                if recom["response_parsed"] != None and recom["response_parsed"]["impact_score"] > 7:
                    self.first_reply += "\n<recommmended_service>"
                    self.first_reply += f"\nService Section:- {recom['service_section']}"
                    self.first_reply += f"\nService Name:- {recom['service_name']}"
                    self.first_reply += f"\nImpact Score:- {recom['response_parsed']['impact_score']}"
                    self.first_reply += f"\nSummary:- {recom['response_parsed']['summary_report']}"
                    self.first_reply += f"\nDetailed Report:- {recom['response_parsed']['detailed_reasoning_report']}"
                    self.first_reply += "\n</recommmended_service>\n"

            return report_results_response, recommendations
        else:
            if self.chat == None:
                self.chat = self.client.chats.create(
                    model = "gemini-2.0-flash",
                    config = self.generation_content_config,
                    history = [
                        types.Content(
                            role = "user",
                            parts = [
                                types.Part.from_text(text = self.first_query),
                            ],
                        ),
                        types.Content(
                            role = "model",
                            parts = [
                                types.Part.from_text(text = self.first_reply),
                            ],
                        ),
                    ]
                )
                    
            response = self.generate_standard_response(message, "gemini-2.0-flash")

            total_cost += response["total_cost"]
            print("Running Cost:- $", total_cost)

            return response["response"]
