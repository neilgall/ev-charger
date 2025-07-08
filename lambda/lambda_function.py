from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model import Response
import datetime
import json
import logging

from iot_data import set_charge_mode, get_charge_mode, ChargeMode


logging.basicConfig(level=logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech_text = "Welcome to the EV Charger skill. How can I assist you?"
        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "You can ask me to override the charging mode or check the current mode."
        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response


class SetChargingModeIntentHandler(AbstractRequestHandler):
    """Handler for setting the charging mode."""
    def can_handle(self, handler_input):
        return (
            is_intent_name("SetGridChargingIntent")(handler_input) or 
            is_intent_name("SetSolarChargingIntent")(handler_input)
        )

    def handle(self, handler_input):
        if is_intent_name("SetGridChargingIntent")(handler_input):
            set_charge_mode(ChargeMode.GRID)
            speech_text = "Power source is now grid."
        else:
            set_charge_mode(ChargeMode.SOLAR)
            speech_text = "Power source is now solar."

        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response


class CheckChargingModeIntentHandler(AbstractRequestHandler):
    """Handler for checking the current charging mode."""
    def can_handle(self, handler_input):
        return is_intent_name("CheckChargingModeIntent")(handler_input)

    def handle(self, handler_input):
        mode = get_charge_mode()
        speech_text = f"The current charging mode is {mode.value}."
        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response


class CancelAndStopIntentHandler(AbstractRequestHandler):
    """Handler for Cancel and Stop Intents."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.CancelIntent")(handler_input) or is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "Goodbye!"
        return handler_input.response_builder.speak(speech_text).set_should_end_session(True).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # Cleanup logic can go here
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "Sorry, I didn't understand that. Please try again."
        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response


def handle_scheduled_event(event):
    """Handler for Scheduled Events triggered by EventBridge."""
    current_hour = datetime.datetime.now().hour
    mode = ChargeMode.GRID if 0 <= current_hour < 5 else ChargeMode.SOLAR
    set_charge_mode(mode)
    
    # Logic to control the EV charger
    logging.info(f"Scheduled event triggered. Setting charging mode to {mode}.")
    
    return {
        "statusCode": 200,
        "body": f"Charging mode set to {mode.value} based on the current time."
    }


sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(SetChargingModeIntentHandler())
sb.add_request_handler(CheckChargingModeIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler())


def lambda_handler(event, context):
    """Main Lambda handler to route requests."""
    if "source" in event and event["source"] == "aws.events":
        # EventBridge scheduled event
        return handle_scheduled_event(event)

    if "request" in event:
        # Alexa Skill request
        return sb.lambda_handler()(event, context)

    return {
        "statusCode": 400,
        "body": "Unsupported event type"
    }


