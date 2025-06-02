from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model import Response
from andersen import AndersenA2
import datetime
import logging
import os

logging.basicConfig(level=logging.INFO)


andersen = AndersenA2(
    username=os.environ["ANDERSEN_USERNAME"],
    password=os.environ["ANDERSEN_PASSWORD"],
    device_name=os.environ["ANDERSEN_DEVICE_NAME"]
)


def set_charge_from_grid(charge_from_grid: bool):
    """Set the charge mode to grid or solar."""
    andersen.set_charge_from_grid(charge_from_grid)


def get_charge_from_grid() -> bool:
    """Get the current charge mode."""
    return andersen.get_charge_from_grid()


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
        return is_intent_name("SetChargingModeIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        mode = slots["mode"].value.lower()  # Expecting "grid" or "solar"
        
        if mode in ["grid", "solar"]:
            set_charge_from_grid(mode == "grid")
            speech_text = f"Charging mode is now {mode}."
        else:
            speech_text = "I didn't understand the mode. Please say 'grid' or 'solar'."
        
        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response


class CheckChargingModeIntentHandler(AbstractRequestHandler):
    """Handler for checking the current charging mode."""
    def can_handle(self, handler_input):
        return is_intent_name("CheckChargingModeIntent")(handler_input)

    def handle(self, handler_input):
        mode = "grid" if get_charge_from_grid() else "solar"
        speech_text = f"The current charging mode is {mode}."
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
    mode = "grid" if 0 <= current_hour < 5 else "solar"
    set_charge_from_grid(mode == "grid")
    
    # Logic to control the EV charger
    logging.info(f"Scheduled event triggered. Setting charging mode to {mode}.")
    
    return {
        "statusCode": 200,
        "body": f"Charging mode set to {mode}"
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


