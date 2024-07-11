# THIS TESTS: TWO AGENTS WITH TERMINATION

altmodel_llm_config = {
    "config_list":
    [
        {
            "api_type": "ollama",
            "model": "llama3",
            "client_host": "http://10.124.79.197:11434",
            # "seed": 42
        }
    ]
}

from autogen import ConversableAgent

jack = ConversableAgent(
    "Jack",
    llm_config=altmodel_llm_config,
    system_message="Your name is Jack and you are a comedian in a two-person comedy show.",
    is_termination_msg=lambda x: True if "FINISH" in x["content"] else False
)
emma = ConversableAgent(
    "Emma",
    llm_config=altmodel_llm_config,
    system_message="Your name is Emma and you are a comedian in two-person comedy show. Say the word FINISH ONLY AFTER you've heard 2 of Jack's jokes.",
    is_termination_msg=lambda x: True if "FINISH" in x["content"] else False
)

chat_result = jack.initiate_chat(emma, message="Emma, tell me a joke about goldfish and peanut butter.", max_turns=10)