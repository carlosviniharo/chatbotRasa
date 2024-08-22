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
from rasa.core.channels.channel import OutputChannel
from whatsapp_connector import WhatsAppOutput


class ActionEndConversation(Action):
    def name(self) -> str:
        return "action_end_conversation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        # To end the conversation and clear forms
        dispatcher.utter_message(text="Bueno, si tienes alguna otra pregunta no dudes en escribirme de nuevo")
        return [Restarted()]



class ActionCheckDisclaimer(Action):

    def name(self) -> str:
        return "action_check_disclaimer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        
        option_value = tracker.get_slot("disclosure")  # Replace with your slot name

        print(option_value)

        if option_value != True:  # Replace with the value you want to check
            dispatcher.utter_message(text="Por favor primero debes aceptar los terminos y condiciones")
            return [UserUtteranceReverted()]
        return []


class ActionOptionsDisclaimerMessage(Action):
    def name(self) -> str:
        return "action_options_disclaimer_message"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        # Define the custom JSON message payload
        json_message = {
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "¿Aceptas los términos y condiciones?"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "yes_option",
                                "title": "Si"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "no_option",
                                "title": "No"
                        }
                        }
                    ]
                }
            }
        }
        dispatcher.utter_message(json_message=json_message)


class ActionOptionsServiceMessage(Action):
    def name(self) -> str:
        return "action_options_service_message"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        # Define the custom JSON message payload
        json_message = {
              "interactive": {
                  "type": "list",
                # "header": {
                #   "type": "text",
                #   "text": "Choose Shipping Option"
                # },
                  "body": {
                      "text": "Tenemos las siguientes opciones disponibles:"
                 },
                # "footer": {
                #   "text": "Lucky Shrub: Your gateway to succulents™"
                # },
                  "action": {
                      "button": "options",
                      "sections": [
                        {
                            "title": "Inversiones",
                            "rows": [
                                {
                                    "id": "Investments",
                                    "title": "Inversiones",
                                },
                            ]
                        },
                        {
                            "title": "Creditos",
                            "rows": [
                                {
                                    "id": "Loans information",
                                    "title": "Información de mis créditos",
                                },
                                {
                                    "id": "New Loan",
                                    "title": "Solicitar un crédito.",
                                },
                            ]
                        },
                        {
                        "title": "Cuentas",
                        "rows": [
                            {
                                "id": "New account",
                                "title": "Apertura de Cuentas",
                            },
                            ]
                        }
                    ]
                }
            }
        }
        dispatcher.utter_message(json_message=json_message)

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
    
    def validation_identity(self, slot_value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
        
        identity = tracker.get_slot("identity")

        if validate_ecuadorian_id(identity):
            return [SlotSet("identity", identity)]
        else:
            # Identity is invalid
            dispatcher.utter_message(response="utter_invalid_identity")
            return [SlotSet("identity", None)]

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
