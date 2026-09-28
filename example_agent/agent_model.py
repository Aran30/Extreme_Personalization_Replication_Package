###############
# AGENT MODEL #
###############
import datetime
from besser.BUML.metamodel.state_machine.state_machine import Body, Condition, Event, ConfigProperty, CustomCodeAction
from besser.BUML.metamodel.state_machine.agent import Agent, AgentSession, AgentReply, LLMReply, RAGReply, LLMOpenAI, LLMHuggingFace, LLMHuggingFaceAPI, LLMReplicate, RAGVectorStore, RAGTextSplitter
from besser.BUML.metamodel.structural import Metadata
import operator

agent = Agent('Agent_Diagram')

agent.add_property(ConfigProperty('websocket_platform', 'websocket.host', 'localhost'))
agent.add_property(ConfigProperty('websocket_platform', 'websocket.port', 8765))
agent.add_property(ConfigProperty('websocket_platform', 'streamlit.host', 'localhost'))
agent.add_property(ConfigProperty('websocket_platform', 'streamlit.port', 5000))
agent.add_property(ConfigProperty('nlp', 'nlp.language', 'en'))
agent.add_property(ConfigProperty('nlp', 'nlp.region', 'US'))
agent.add_property(ConfigProperty('nlp', 'nlp.timezone', 'Europe/Madrid'))
agent.add_property(ConfigProperty('nlp', 'nlp.pre_processing', True))
agent.add_property(ConfigProperty('nlp', 'nlp.intent_threshold', 0.4))
agent.add_property(ConfigProperty('nlp', 'nlp.openai.api_key', 'YOUR-API-KEY'))
agent.add_property(ConfigProperty('nlp', 'nlp.hf.api_key', 'YOUR-API-KEY'))
agent.add_property(ConfigProperty('nlp', 'nlp.replicate.api_key', 'YOUR-API-KEY'))

# INTENTS
Muscles_intent = agent.new_intent('Muscles_intent', [
    'I want muscles',
],
description="Question about how to become muscular and which exercises to perform.")
Nutrition_intent = agent.new_intent('Nutrition_intent', [
    'Which food to eat?',
],
description="Question about nutrition in gym.")
Other = agent.new_intent('Other', [
],
description="Any question that does not fit in \"Muscles\" or \"Nutrition\"")

# Create LLM instance for use in state bodies
llm = LLMOpenAI(agent=agent, name='gpt-4o-mini', parameters={})

# STATES
Initial = agent.new_state('Initial', initial=True)
Idle = agent.new_state('Idle')
TrainingPlan = agent.new_state('TrainingPlan')
Nutrition = agent.new_state('Nutrition')
OtherQuestions = agent.new_state('OtherQuestions')

# Initial state
Initial_body = Body('Initial_body')
Initial_body.add_action(AgentReply('Hello. I am your fitness advisor.'))

Initial.set_body(Initial_body)
Initial.go_to(Idle)

# Idle state
Idle_body = Body('Idle_body')
Idle_body.add_action(AgentReply('I can answer your questions about exercise, food, and rest.'))

Idle.set_body(Idle_body)
Idle.when_intent_matched(Muscles_intent).go_to(TrainingPlan)

Idle.when_intent_matched(Other).go_to(OtherQuestions)

Idle.when_intent_matched(Nutrition_intent).go_to(Nutrition)

# TrainingPlan state
TrainingPlan_body = Body('TrainingPlan_body')
TrainingPlan_body.add_action(AgentReply('Focus on heavy lifts that use many muscles, like squats, deadlifts, bench press, overhead press, and rows.'))
TrainingPlan_body.add_action(AgentReply('Train 3 to 5 times a week. Add weight slowly. Eat enough protein and calories to grow.'))
TrainingPlan_body.add_action(AgentReply('Sleep well and be consistent. Muscle grows with steady effort over time.'))

TrainingPlan.set_body(TrainingPlan_body)
TrainingPlan.go_to(Idle)

# Nutrition state
Nutrition_body = Body('Nutrition_body')
Nutrition_body.add_action(AgentReply('Food basics: Eat mostly whole foodslean proteins, vegetables, fruits, whole grains, and healthy fats. Aim for about 1.6 to 2.2 grams of protein per kilogram of your body weight each day.'))
Nutrition_body.add_action(AgentReply('Match your calories to your goal: eat a little more to gain muscle, eat less to lose fat, eat the same to maintain.'))
Nutrition_body.add_action(AgentReply('Carbs give you energy to train. Fats help your hormones work well.'))
Nutrition_body.add_action(AgentReply('Drink plenty of water. Limit highly processed foods and alcohol.'))
Nutrition_body.add_action(AgentReply('Be consistent. Results come from habits, not perfection.'))

Nutrition.set_body(Nutrition_body)
Nutrition.go_to(Idle)

# OtherQuestions state
OtherQuestions_body = Body('OtherQuestions_body')
OtherQuestions_body.add_action(LLMReply())
OtherQuestions.set_body(OtherQuestions_body)
OtherQuestions.go_to(Idle)

