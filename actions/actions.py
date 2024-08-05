# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


import re
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import Restarted, FollowupAction
from utils.helper import validate_ecuadorian_id


class ActionEndConversation(Action):
    def name(self) -> str:
        return "action_end_conversation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        # To end the conversation and clear forms
        dispatcher.utter_message(text="Bueno, si tienes alguna otra pregunta no dudes en escribirme de nuevo")
        return [Restarted()]



class ActionValidateID(Action):
    def name(self) -> str:
        return "action_validate_id"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
                # Extract the identity entity from the latest message
        identity = tracker.get_slot("identity")
        user_message = tracker.latest_message.get('text')

        print(user_message)
        
        # Define the validation pattern for the identity (e.g., 10-digit number)
        pattern = re.compile(r"^\d{10}$")
        dispatcher.utter_message(identity and validate_ecuadorian_id(identity))
        if (identity and validate_ecuadorian_id(identity)):
            # Identity is valid, save it to the slot
            dispatcher.utter_message(text=f"Tu número de identificación {identity} ha sido guardado correctamente.")
            return [SlotSet("identity", identity), FollowupAction("utter_disclaimer")]
        else:
            # Check if the user message contains a valid identity
            matches = pattern.findall(user_message)
            # Check the first match as the identity
            valid_identity = validate_ecuadorian_id(matches[0])

            if valid_identity:
                print(valid_identity)
                dispatcher.utter_message(text=f"Tu número de identificación {valid_identity} ha sido guardado correctamente.")
                return [SlotSet("identity", valid_identity), FollowupAction("utter_disclaimer")]
            else:
                # Identity is invalid
                dispatcher.utter_message(text="El número de identificación proporcionado no es válido.")
                return [SlotSet("identity", None), FollowupAction("utter_ask_identity")]

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
            return [FollowupAction("utter_services")]
        
        return []