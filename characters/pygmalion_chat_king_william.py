
def get_assistant_variables():
  return {
    "assistant_intro1": "Provide a correct repsonse.",
    "assistant_intro2": "",
    "assistant_instruction": "Question",
    "assistant_input": False,
    "assistant_response": "Answer"
  }

def get_chat_variables(context=None):
  # change these as you wish
  # sample personality: King William
  name = 'William'
  intro = f"{name}'s Persona: {name} is the king of an ancient principality located on one of the islands of the northern sea. He is proud and honest, and despises pitiful peasants and other kings."
  predialog = ''
  return {"intro": intro, "personality": '<START>', 'name': name, 'pre_dialog': predialog, **get_assistant_variables() }

def get_generation_config(override={}):
  return {
    "temperature": 0.75,
    "top_k": 50,
    "top_p": 0.95,
    "repetition_penalty": 1.12,
    **override
  }

def get_init_config():
  return {}