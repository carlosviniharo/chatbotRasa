# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


import re
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, Restarted, FollowupAction, UserUtteranceReverted
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
        identity = tracker.get_slot("identity")
        print(identity)
       
        # Check the first match as the identity
        valid_identity = validate_ecuadorian_id(identity)

        if valid_identity:
            dispatcher.utter_message(text=f"Tu número de identificación {identity} ha sido guardado correctamente.")
            return [SlotSet("identity", identity), FollowupAction("utter_ask_disclaimer")]
        else:
            # Identity is invalid
            dispatcher.utter_message(text="El número de identificación proporcionado no es válido.")
            return [SlotSet("identity", None), FollowupAction("utter_ask_identity")]


class ActionCheckDisclaimer(Action):

    def name(self) -> str:
        return "action_check_disclaimer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        
        option_value = tracker.get_slot("disclosure")  # Replace with your slot name

        print(option_value)

        if option_value != True:  # Replace with the value you want to check
            dispatcher.utter_message(text="Por favor primero debes proporcionar tu cedula y aceptar los terminos y condiciones")
            return [UserUtteranceReverted()]

        return []

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
        print(names_splited)

        if len(names_splited) >= 2:
            return {"fullname": naked_name}
        else:
            dispatcher.utter_message(response="utter_invalid_fullname")
            return {"fullname": None}

    def validate_city(self, slot_value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
        print(slot_value)
        if re.match(r"^[a-zA-Z\s]{2,}$", slot_value):
            return {"city": slot_value}
        else:
            dispatcher.utter_message(response="utter_invalid_city")
            return {"city": None}

    def validate_cellphone(self, slot_value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
        cellphone = tracker.get_slot("cellphone")
        print(cellphone)
        print(slot_value)
        if validate_ecuadorian_phone(cellphone):
            return {"cellphone": cellphone}
        else:
            dispatcher.utter_message(response="utter_invalid_cellphone")
            return {"cellphone": None}
        
    def validate_email(self, slot_value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
        print(slot_value)
        if validate_email_string(slot_value):
            return {"email": slot_value}
        else:
            dispatcher.utter_message(response="utter_invalid_email")
            return {"email": None}

class ValidateClientNewLoanForm(ValidateClientDataForm):

    def name(self) -> str:
        return "validate_client_new_loan_form"
    
    def validate_salary(self, slot_value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
        # print(slot_value)
        basic_wage = 450
        if int(slot_value) >= basic_wage:
            return {"salary": slot_value}
        else:
            dispatcher.utter_message(response="utter_invalid_salary")
            return {"salary": None}

    def validate_amount_required(self, slot_value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
        print(slot_value)
        minimun_loan = 500
        if int(slot_value) >= minimun_loan:
            return {"amount_required": slot_value}
        else:
            dispatcher.utter_message(response="utter_invalid_amount_required")
            return {"amount_required": None}

    # def validate_salary(self, value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
    #     if tracker.get_slot("salary") is None:
    #         return {"salary": value}
    #     else:
    #         return {"salary": tracker.get_slot("salary")}

    # def validate_amount_required(self, value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
    #     if tracker.get_slot("amount_required") is None:
    #         return {"amount_required": value}
    #     else:
    #         return {"amount_required": tracker.get_slot("amount_required")}