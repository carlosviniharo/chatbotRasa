# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

#from typing import Any, Text, Dict, List

# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
# class ActionEndConversation(Action):
#     def name(self) -> str:
#         return "action_end_conversation"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: dict) -> list:
#         # To end the conversation and clear forms
#         return [Restarted(), FollowupAction('action_listen')]

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import Restarted, FollowupAction


class ActionEndConversation(Action):
    def name(self) -> str:
        return "action_end_conversation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        # To end the conversation and clear forms
        dispatcher.utter_message(text="Bueno, si tienes alguna otra pregunta no dudes en escribirme de nuevo")
        return [Restarted()]


class ActionShowIdentity(Action):

    def name(self) -> str:
        return "action_show_identity"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:

        identity = tracker.get_slot("identity")
        if identity:
            dispatcher.utter_message(text=f"Your identity number is {identity}")
        else:
            dispatcher.utter_message(text="I could not get your identity number.")

        return []


class ActionShowOption(Action):

    def name(self) -> str:
        return "action_show_option"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        
        option = tracker.get_slot("option")
        
        if option == "creditos":
            dispatcher.utter_message(text="Un momento ya le ayudo con la informacion de creditos")
            return [FollowupAction("utter_loans")]
        elif option == "inversiones":
            dispatcher.utter_message(text="Un momento ya le ayudo con la informacion de inversiones")
        elif option == "cuentas":
            dispatcher.utter_message(text="Un momento ya le ayudo con la informacion de cuentas")
        else:
            dispatcher.utter_message(text=f"Perdon tu respuesta no esta en nuestras opciones")
            return [FollowupAction("choose_option")]
        
        return []