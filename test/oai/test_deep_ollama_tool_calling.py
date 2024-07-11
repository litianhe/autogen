import autogen
from typing import Literal
from typing_extensions import Annotated

import autogen.runtime_logging

autogen.runtime_logging.start(logger_type="file")

# THIS TESTS: TOOL CALLING

# altmodel_llm_config = {
#     "config_list":
#     [
#         {
#             "api_type": "ollama",
#             "model": "llama3:8b-instruct-q6_K",
#             "client_host": "http://192.168.0.1:11434",
#             "seed": 43,
#             "cache_seed": None
#         }
#     ]
# }

altmodel_llm_config = {
    "config_list":
    [
        {
            "api_type": "ollama",
            "model": "llama3",
            "client_host": "http://10.124.79.197:11434",
            "cache_seed": None,
        }
    ]
}

# Create the agent and include examples of the function calling JSON in the prompt
# to help guide the model
chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="For currency exchange tasks, "
        "only use the functions you have been provided with.",
    llm_config=altmodel_llm_config,
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
)

CurrencySymbol = Literal["USD", "EUR"]

# Define our function that we expect to call
def exchange_rate(base_currency: CurrencySymbol, quote_currency: CurrencySymbol) -> float:
    if base_currency == quote_currency:
        return 1.0
    elif base_currency == "USD" and quote_currency == "EUR":
        return 1 / 1.1
    elif base_currency == "EUR" and quote_currency == "USD":
        return 1.1
    else:
        raise ValueError(f"Unknown currencies {base_currency}, {quote_currency}")

# Register the function with the agent
@user_proxy.register_for_execution()
@chatbot.register_for_llm(description="Currency exchange calculator.")
def currency_calculator(
    base_amount: Annotated[float, "Amount of currency in base_currency"],
    base_currency: Annotated[CurrencySymbol, "Base currency"] = "USD",
    quote_currency: Annotated[CurrencySymbol, "Quote currency"] = "EUR",
) -> str:
    quote_amount = exchange_rate(base_currency, quote_currency) * base_amount
    return f"{format(quote_amount, '.2f')} {quote_currency}"

# start the conversation
res = user_proxy.initiate_chat(
    chatbot,
    message="How much is 1 US Dollor in EUR? How much is 1 EUR in US Dollor?",# correct
    # message="How much is 11.45 EUR in USD?",  # correct
    # message="How much is 11.45 EUR in US Dollor?",  # wrong
    # message="How much is 1 EUR in US Dollor?",
    # message="How much is 11.45 EUR in CNY?",    # failed in function call
    summary_method="reflection_with_llm",
)

print(f"SUMMARY: {res.summary['content']}")