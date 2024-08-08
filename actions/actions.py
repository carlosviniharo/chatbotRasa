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
from rasa_sdk.forms import FormValidationAction
from utils.helper import (
    validate_ecuadorian_id, 
    validate_ecuadorian_phone,
    validate_email_string
)


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
        # identity = tracker.get_slot("identity")
        user_message = tracker.latest_message.get('text')
        
        # # Define the validation pattern for the identity (e.g., 10-digit number)
        # pattern = re.compile(r"^\d{10}$")
        
        # # Check if the user message contains a valid identity
        # matches = pattern.findall(user_message)

        # if not matches:
        #     dispatcher.utter_message(text="El número de identificación proporcionado no es válido.")
        #     return [SlotSet("identity", None), FollowupAction("utter_ask_identity")]
       
        # Check the first match as the identity
        print(tracker.get_slot("identity"))
        valid_identity = validate_ecuadorian_id(user_message)

        if valid_identity:
            dispatcher.utter_message(text=f"Tu número de identificación {user_message} ha sido guardado correctamente.")
            return [SlotSet("identity", user_message), FollowupAction("utter_disclaimer")]
        else:
            # Identity is invalid
            dispatcher.utter_message(text="El número de identificación proporcionado no es válido.")
            return [SlotSet("identity", None), FollowupAction("utter_ask_identity")]


class ActionShowOption(Action):

    def name(self) -> str:
        return "action_show_option"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        
        option = tracker.get_slot("option")
        
        if option == "creditos":
            return [FollowupAction("utter_loans")]
        elif option == "inversiones":
            dispatcher.utter_message(text="Un momento ya le ayudo con la informacion de inversiones")
        elif option == "cuentas":
            dispatcher.utter_message(text="Un momento ya le ayudo con la informacion de cuentas")
        else:
            dispatcher.utter_message(text=f"Perdon tu respuesta no esta en nuestras opciones")
            return [FollowupAction("utter_services")]
        
        return []
    
class ValidateClientDataForm(FormValidationAction):
    def name(self) -> str:
        return "validate_client_info_loan_form"

    def validate_fullname(self, slot_value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
        naked_name = tracker.latest_message.get('text')
        names_splited = re.findall(r"\b[A-Za-z]+\b", naked_name)
        # print(slot_value)
        # print(names_splited)
        # print(tracker.latest_message.get('text'))
        
        if len(names_splited) >= 2:
            return {"fullname": naked_name}
        else:
            dispatcher.utter_message(response="utter_invalid_fullname")
            return {"fullname": None}

    def validate_city(self, slot_value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
        if re.match(r"^[a-zA-Z\s]{2,}$", slot_value):
            return {"city": slot_value}
        else:
            dispatcher.utter_message(response="utter_invalid_city")
            return {"city": None}

    def validate_phone(self, slot_value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
        if validate_ecuadorian_phone(slot_value):
            return {"phone": slot_value}
        else:
            dispatcher.utter_message(response="utter_invalid_phone")
            return {"phone": None}
        
    def validate_email(self, slot_value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
        
        if validate_email_string(slot_value):
            return {"email": slot_value}
        else:
            dispatcher.utter_message(response="utter_invalid_email")
            return {"email": None}