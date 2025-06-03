from enum import Enum
import boto3
import json
import logging
import os

iot_client = boto3.client(
    "iot-data",
    region_name=os.environ.get("AWS_REGION", "eu-west-1")
)

IOT_THING_NAME = os.environ.get("IOT_THING_NAME", "AndersonsEVCharger")


class ChargeMode(Enum):
    """Enum for charge modes."""
    GRID = "grid"
    SOLAR = "solar"


def set_charge_mode(charge_mode: ChargeMode):
    """Set the charge mode to grid or solar in the IoT shadow."""
    try:
        payload = {
            "state": {
                "desired": {
                    "chargeMode": charge_mode.value
                }
            }
        }
        iot_client.update_thing_shadow(
            thingName=IOT_THING_NAME,
            payload=json.dumps(payload)
        )
        logging.info(f"Charge mode set to {charge_mode.value} in IoT shadow.")
    except Exception as e:
        logging.error(f"Failed to set charge mode: {e}")


def get_charge_mode() -> ChargeMode:
    """Get the current charge mode from the IoT shadow."""
    try:
        response = iot_client.get_thing_shadow(thingName=IOT_THING_NAME)
        shadow_payload = json.loads(response["payload"].read())
        charge_mode = shadow_payload.get("state", {}).get("desired", {}).get("chargeMode")
        if charge_mode == ChargeMode.GRID.value:
            return ChargeMode.GRID
        elif charge_mode == ChargeMode.SOLAR.value:
            return ChargeMode.SOLAR
        else:
            logging.warning("Charge mode in shadow is invalid or not set.")
            return None
    except Exception as e:
        logging.error(f"Failed to get charge mode: {e}")
        return None


