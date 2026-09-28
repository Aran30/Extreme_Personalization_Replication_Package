# You may need to add your working directory to the Python path. To do so, uncomment the following lines of code
# import sys
# sys.path.append("/Path/to/directory/besser-agentic-framework") # Replace with your directory path

import json
import logging
import operator

from besser.agent.core.agent import Agent
from besser.agent.nlp.llm.llm_huggingface import LLMHuggingFace
from besser.agent.nlp.llm.llm_huggingface_api import LLMHuggingFaceAPI
from besser.agent.nlp.llm.llm_openai_api import LLMOpenAI
from besser.agent.nlp.llm.llm_replicate_api import LLMReplicate
from besser.agent.core.session import Session
from besser.agent.nlp.intent_classifier.intent_classifier_configuration import LLMIntentClassifierConfiguration, SimpleIntentClassifierConfiguration
from besser.agent.nlp.speech2text.openai_speech2text import OpenAISpeech2Text
from besser.agent.nlp.text2speech.openai_text2speech import OpenAIText2Speech

# Configure the logging module
logging.basicConfig(level=logging.INFO, format='{levelname} - {asctime}: {message}', style='{')

def build_agent_configuration_prompt(agent_configuration: dict) -> str:
    base_prompt = """
You are a personalized AI assistant.

You will be provided with an object called `agent_configuration` as a JSON string.
This object defines how you should present yourself and formulate your responses.

It controls stylistic and presentation aspects such as:
- Response language
- Level of formality
- Language complexity
- Sentence length
- And more

You must strictly follow the preferences defined in `agent_configuration` for all responses.

Here is the current agent configuration (JSON):

{agent_configuration_json}
"""
    return base_prompt.format(agent_configuration_json=json.dumps(agent_configuration, indent=2))


def build_user_profile_prompt(user_profile: dict) -> str:
    profile_prompt = """
You have access to the current user's profile encoded as JSON.
Leverage these traits whenever the agent configuration instructs you to adapt content.

Here is the active user profile (JSON):

{user_profile_json}
"""
    return profile_prompt.format(user_profile_json=json.dumps(user_profile, indent=2))


# Create the bot
agent = Agent('Agent_Diagram', user_profiles_path='user_profiles.json', persist_sessions=True)
# Load bot properties stored in a dedicated file
agent.load_properties('config.ini')

# Define the platform your chatbot will use

# Collect profile names from provided personalization mappings
profile_names = []
agent_configurations = {}
user_profiles = {}
context_prompts = {}
profile_prompts = {}
profile_names.append('ElderlyProfile')
agent_configurations['ElderlyProfile'] = json.loads(r'''{
  "adaptContentToUserProfile": false,
  "agentLanguage": "none",
  "agentPlatform": "streamlit",
  "agentStyle": "formal",
  "avatar": null,
  "inputModalities": [
    "text",
    "speech"
  ],
  "intentRecognitionTechnology": "llm-based",
  "interfaceStyle": {
    "alignment": "left",
    "color": "var(--apollon-primary-contrast)",
    "contrast": "medium",
    "font": "sans",
    "lineSpacing": 1.5,
    "size": 16
  },
  "languageComplexity": "simple",
  "llm": {
    "model": "gpt-5",
    "provider": "openai"
  },
  "outputModalities": [
    "text",
    "speech"
  ],
  "responseTiming": "instant",
  "sentenceLength": "original",
  "useAbbreviations": false,
  "userProfileName": null,
  "voiceStyle": {
    "gender": "male",
    "speed": 1
  }
}''')
user_profiles['ElderlyProfile'] = json.loads(r'''{
  "model": {
    "Personal_Information": {
      "age": 65
    },
    "class": "User",
    "id": "user_1"
  },
  "name": "UserProfile"
}''')
context_prompts['ElderlyProfile'] = build_agent_configuration_prompt(agent_configurations['ElderlyProfile'])
profile_names.append('ParaplegicProfile')
agent_configurations['ParaplegicProfile'] = json.loads(r'''{
  "adaptContentToUserProfile": true,
  "agentLanguage": "none",
  "agentPlatform": "streamlit",
  "agentStyle": "original",
  "avatar": null,
  "inputModalities": [
    "text"
  ],
  "intentRecognitionTechnology": "llm-based",
  "interfaceStyle": {
    "alignment": "left",
    "color": "var(--apollon-primary-contrast)",
    "contrast": "medium",
    "font": "sans",
    "lineSpacing": 1.5,
    "size": 16
  },
  "languageComplexity": "original",
  "llm": {
    "model": "gpt-5",
    "provider": "openai"
  },
  "outputModalities": [
    "text"
  ],
  "responseTiming": "instant",
  "sentenceLength": "original",
  "useAbbreviations": false,
  "userProfileName": "ParaplegicProfile",
  "voiceStyle": {
    "gender": "male",
    "speed": 1
  }
}''')
user_profiles['ParaplegicProfile'] = json.loads(r'''{
  "model": {
    "Accessibility": {
      "Disability": {
        "affects": "Mobility",
        "description": "Can\u0027t use lower body",
        "name": "Paraplegic"
      }
    },
    "class": "User",
    "id": "user_1"
  },
  "name": "UserProfile"
}''')
context_prompts['ParaplegicProfile'] = build_agent_configuration_prompt(agent_configurations['ParaplegicProfile'])
profile_prompts['ParaplegicProfile'] = build_user_profile_prompt(user_profiles['ParaplegicProfile'])




platform = agent.use_websocket_platform(use_ui=True, authenticate_users=True)
# LLM instantiation based on config['llm']
reply_llm = LLMOpenAI(
    agent=agent,
    name='gpt-5',
    parameters={}
)

stt = OpenAISpeech2Text(agent=agent, model_name="whisper-1")
tts = OpenAIText2Speech(agent=agent, model_name="gpt-4o-mini-tts")




ic_config = LLMIntentClassifierConfiguration(
    llm_name='gpt-5',
    parameters={},
    use_intent_descriptions=True,
    use_training_sentences=True,
    use_entity_descriptions=False,
    use_entity_synonyms=False
)

agent.set_default_ic_config(ic_config)


##############################
# INTENTS
##############################
Muscles_intent = agent.new_intent('Muscles_intent', [
    'I want muscles',
    ],
    description='Question about how to become muscular and which exercises to perform.'
)
Nutrition_intent = agent.new_intent('Nutrition_intent', [
    'Which food to eat?',
    ],
    description='Question about nutrition in gym.'
)
Other = agent.new_intent('Other', [
    ],
    description='Any question that does not fit in "Muscles" or "Nutrition"'
)

##############################
# PERSONALIZED INTENTS
##############################
# Intents for profile ElderlyProfile
Muscles_intent_ElderlyProfile = agent.new_intent('Muscles_intent_ElderlyProfile', [
    'I want muscles',
    ],
    description='Question about how to become muscular and which exercises to perform.'
)
Nutrition_intent_ElderlyProfile = agent.new_intent('Nutrition_intent_ElderlyProfile', [
    'Which food to eat?',
    ],
    description='Question about nutrition in gym.'
)
Other_ElderlyProfile = agent.new_intent('Other_ElderlyProfile', [
    ],
    description='Any question that does not fit in "Muscles" or "Nutrition"'
)

# Intents for profile ParaplegicProfile
Muscles_intent_ParaplegicProfile = agent.new_intent('Muscles_intent_ParaplegicProfile', [
    'I want muscles',
    ],
    description='Question about how to become muscular and which exercises to perform.'
)
Nutrition_intent_ParaplegicProfile = agent.new_intent('Nutrition_intent_ParaplegicProfile', [
    'Which food to eat?',
    ],
    description='Question about nutrition in gym.'
)
Other_ParaplegicProfile = agent.new_intent('Other_ParaplegicProfile', [
    ],
    description='Any question that does not fit in "Muscles" or "Nutrition"'
)


##############################
# STATES
##############################

# Dummy entry state to fan out to profile-specific initial states
router_initial_state = agent.new_state('router_initial_state', initial=True)

Initial = agent.new_state('Initial')
Idle = agent.new_state('Idle')
TrainingPlan = agent.new_state('TrainingPlan')
Nutrition = agent.new_state('Nutrition')
OtherQuestions = agent.new_state('OtherQuestions')

##############################
# PROFILE STATES
##############################
# States for profile ElderlyProfile
Initial_ElderlyProfile = agent.new_state('Initial_ElderlyProfile')
Idle_ElderlyProfile = agent.new_state('Idle_ElderlyProfile')
TrainingPlan_ElderlyProfile = agent.new_state('TrainingPlan_ElderlyProfile')
Nutrition_ElderlyProfile = agent.new_state('Nutrition_ElderlyProfile')
OtherQuestions_ElderlyProfile = agent.new_state('OtherQuestions_ElderlyProfile')
# States for profile ParaplegicProfile
Initial_ParaplegicProfile = agent.new_state('Initial_ParaplegicProfile')
Idle_ParaplegicProfile = agent.new_state('Idle_ParaplegicProfile')
TrainingPlan_ParaplegicProfile = agent.new_state('TrainingPlan_ParaplegicProfile')
Nutrition_ParaplegicProfile = agent.new_state('Nutrition_ParaplegicProfile')
OtherQuestions_ParaplegicProfile = agent.new_state('OtherQuestions_ParaplegicProfile')

##############################
# ROUTER TRANSITIONS TO PROFILE INITIAL STATES
##############################
router_initial_state.when_variable_matches_operation('user_profile', operator.eq, 'ElderlyProfile').go_to(Initial_ElderlyProfile)
router_initial_state.when_variable_matches_operation('user_profile', operator.eq, 'ParaplegicProfile').go_to(Initial_ParaplegicProfile)


# Initial
def Initial_body(session: Session):
    speech_messages = []
    reply_text = 'Hello. I am your fitness advisor.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    if speech_messages:
        platform.reply_speech(session, ' '.join(speech_messages))
Initial.set_body(Initial_body)
Initial.go_to(Idle)
# Idle
def Idle_body(session: Session):
    speech_messages = []
    reply_text = 'I can answer your questions about exercise, food, and rest.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    if speech_messages:
        platform.reply_speech(session, ' '.join(speech_messages))
Idle.set_body(Idle_body)
Idle.when_intent_matched(Muscles_intent).go_to(TrainingPlan)
Idle.when_intent_matched(Other).go_to(OtherQuestions)
Idle.when_intent_matched(Nutrition_intent).go_to(Nutrition)
Idle.when_variable_matches_operation('user_profile', operator.eq, 'ElderlyProfile').go_to(router_initial_state)
Idle.when_variable_matches_operation('user_profile', operator.eq, 'ParaplegicProfile').go_to(router_initial_state)
# TrainingPlan
def TrainingPlan_body(session: Session):
    speech_messages = []
    reply_text = 'Focus on heavy lifts that use many muscles, like squats, deadlifts, bench press, overhead press, and rows.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    reply_text = 'Train 3 to 5 times a week. Add weight slowly. Eat enough protein and calories to grow.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    reply_text = 'Sleep well and be consistent. Muscle grows with steady effort over time.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    if speech_messages:
        platform.reply_speech(session, ' '.join(speech_messages))
TrainingPlan.set_body(TrainingPlan_body)
TrainingPlan.go_to(Idle)
# Nutrition
def Nutrition_body(session: Session):
    speech_messages = []
    reply_text = 'Food basics: Eat mostly whole foodslean proteins, vegetables, fruits, whole grains, and healthy fats. Aim for about 1.6 to 2.2 grams of protein per kilogram of your body weight each day.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    reply_text = 'Match your calories to your goal: eat a little more to gain muscle, eat less to lose fat, eat the same to maintain.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    reply_text = 'Carbs give you energy to train. Fats help your hormones work well.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    reply_text = 'Drink plenty of water. Limit highly processed foods and alcohol.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    reply_text = 'Be consistent. Results come from habits, not perfection.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    if speech_messages:
        platform.reply_speech(session, ' '.join(speech_messages))
Nutrition.set_body(Nutrition_body)
Nutrition.go_to(Idle)
# OtherQuestions
def OtherQuestions_body(session: Session):
    message = reply_llm.predict(message=session.event.message, session=session)
    session.reply(message)
    platform.reply_speech(session, message)
OtherQuestions.set_body(OtherQuestions_body)
OtherQuestions.go_to(Idle)



##############################
# PROFILE STATE BODIES & TRANSITIONS
##############################
# Initial (ElderlyProfile)
def Initial_body_ElderlyProfile(session: Session):
    reply_llm.add_user_context(
        session=session,
        context=context_prompts.get('ElderlyProfile'),
        context_name='agent_configuration_ElderlyProfile'
    )
    speech_messages = []
    reply_text = 'Hello. I am your fitness advisor.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    if speech_messages:
        platform.reply_speech(session, ' '.join(speech_messages))
Initial_ElderlyProfile.set_body(Initial_body_ElderlyProfile)
Initial_ElderlyProfile.go_to(Idle_ElderlyProfile)
# Idle (ElderlyProfile)
def Idle_body_ElderlyProfile(session: Session):
    speech_messages = []
    reply_text = 'I can answer your questions about exercise, food, and rest.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    if speech_messages:
        platform.reply_speech(session, ' '.join(speech_messages))
Idle_ElderlyProfile.set_body(Idle_body_ElderlyProfile)
Idle_ElderlyProfile.when_intent_matched(Muscles_intent_ElderlyProfile).go_to(TrainingPlan_ElderlyProfile)
Idle_ElderlyProfile.when_intent_matched(Other_ElderlyProfile).go_to(OtherQuestions_ElderlyProfile)
Idle_ElderlyProfile.when_intent_matched(Nutrition_intent_ElderlyProfile).go_to(Nutrition_ElderlyProfile)
Idle_ElderlyProfile.when_variable_matches_operation('user_profile', operator.eq, 'ParaplegicProfile').go_to(router_initial_state)
# TrainingPlan (ElderlyProfile)
def TrainingPlan_body_ElderlyProfile(session: Session):
    speech_messages = []
    reply_text = 'Focus on heavy lifts that use many muscles, like squats, deadlifts, bench press, overhead press, and rows.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    reply_text = 'Train 3 to 5 times a week. Add weight slowly. Eat enough protein and calories to grow.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    reply_text = 'Sleep well and be consistent. Muscle grows with steady effort over time.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    if speech_messages:
        platform.reply_speech(session, ' '.join(speech_messages))
TrainingPlan_ElderlyProfile.set_body(TrainingPlan_body_ElderlyProfile)
TrainingPlan_ElderlyProfile.go_to(Idle_ElderlyProfile)
# Nutrition (ElderlyProfile)
def Nutrition_body_ElderlyProfile(session: Session):
    speech_messages = []
    reply_text = 'Food basics: Eat mostly whole foodslean proteins, vegetables, fruits, whole grains, and healthy fats. Aim for about 1.6 to 2.2 grams of protein per kilogram of your body weight each day.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    reply_text = 'Match your calories to your goal: eat a little more to gain muscle, eat less to lose fat, eat the same to maintain.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    reply_text = 'Carbs give you energy to train. Fats help your hormones work well.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    reply_text = 'Drink plenty of water. Limit highly processed foods and alcohol.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    reply_text = 'Be consistent. Results come from habits, not perfection.'
    session.reply(reply_text)
    speech_messages.append(reply_text)
    if speech_messages:
        platform.reply_speech(session, ' '.join(speech_messages))
Nutrition_ElderlyProfile.set_body(Nutrition_body_ElderlyProfile)
Nutrition_ElderlyProfile.go_to(Idle_ElderlyProfile)
# OtherQuestions (ElderlyProfile)
def OtherQuestions_body_ElderlyProfile(session: Session):
    message = reply_llm.predict(message=session.event.message, session=session)
    session.reply(message)
    platform.reply_speech(session, message)
OtherQuestions_ElderlyProfile.set_body(OtherQuestions_body_ElderlyProfile)
OtherQuestions_ElderlyProfile.go_to(Idle_ElderlyProfile)

# Initial (ParaplegicProfile)
def Initial_body_ParaplegicProfile(session: Session):
    reply_llm.add_user_context(
        session=session,
        context=context_prompts.get('ParaplegicProfile'),
        context_name='agent_configuration_ParaplegicProfile'
    )
    reply_llm.add_user_context(
        session=session,
        context=profile_prompts.get('ParaplegicProfile'),
        context_name='user_profile_ParaplegicProfile'
    )
    reply_text = 'Hi, I am your buddy, the fitness agent.'
    session.reply(reply_text)
Initial_ParaplegicProfile.set_body(Initial_body_ParaplegicProfile)
Initial_ParaplegicProfile.go_to(Idle_ParaplegicProfile)
# Idle (ParaplegicProfile)
def Idle_body_ParaplegicProfile(session: Session):
    reply_text = 'I am here to answer any questions regarding exercises, nutrition and recovery.'
    session.reply(reply_text)
Idle_ParaplegicProfile.set_body(Idle_body_ParaplegicProfile)
Idle_ParaplegicProfile.when_intent_matched(Muscles_intent_ParaplegicProfile).go_to(TrainingPlan_ParaplegicProfile)
Idle_ParaplegicProfile.when_intent_matched(Other_ParaplegicProfile).go_to(OtherQuestions_ParaplegicProfile)
Idle_ParaplegicProfile.when_intent_matched(Nutrition_intent_ParaplegicProfile).go_to(Nutrition_ParaplegicProfile)
Idle_ParaplegicProfile.when_variable_matches_operation('user_profile', operator.eq, 'ElderlyProfile').go_to(router_initial_state)
# TrainingPlan (ParaplegicProfile)
def TrainingPlan_body_ParaplegicProfile(session: Session):
    reply_text = 'Focus on compound upper-body lifts and accessible movements like bench press, overhead press, rows, pull-ups or lat pulldowns, dips, and cable work to build overall muscle mass.'
    session.reply(reply_text)
    reply_text = 'Train 35 times per week, progressively increasing the weight while eating enough protein and calories to support growth.'
    session.reply(reply_text)
    reply_text = 'Get good sleep and stay consistentmuscle comes from steady effort over time.'
    session.reply(reply_text)
TrainingPlan_ParaplegicProfile.set_body(TrainingPlan_body_ParaplegicProfile)
TrainingPlan_ParaplegicProfile.go_to(Idle_ParaplegicProfile)
# Nutrition (ParaplegicProfile)
def Nutrition_body_ParaplegicProfile(session: Session):
    reply_text = 'Nutrition basics: Eat mostly whole foods (lean protein, vegetables, fruits, whole grains, healthy fats). Protein: ~1.62.2 g per kg of body weight daily.'
    session.reply(reply_text)
    reply_text = 'Match calories to your goal: slight surplus to gain muscle, deficit to lose fat, maintenance to stay the same.'
    session.reply(reply_text)
    reply_text = 'Carbs fuel training; fats support hormones.'
    session.reply(reply_text)
    reply_text = 'Drink plenty of water and limit ultra-processed foods and alcohol.'
    session.reply(reply_text)
    reply_text = 'Be consistentresults come from habits, not perfection.'
    session.reply(reply_text)
Nutrition_ParaplegicProfile.set_body(Nutrition_body_ParaplegicProfile)
Nutrition_ParaplegicProfile.go_to(Idle_ParaplegicProfile)
# OtherQuestions (ParaplegicProfile)
def OtherQuestions_body_ParaplegicProfile(session: Session):
    message = reply_llm.predict(message=session.event.message, session=session)
    session.reply(message)
OtherQuestions_ParaplegicProfile.set_body(OtherQuestions_body_ParaplegicProfile)
OtherQuestions_ParaplegicProfile.go_to(Idle_ParaplegicProfile)


# RUN APPLICATION

if __name__ == '__main__':
    agent.run()