import andersen_ev
import datetime as dt
import logging


class AndersenA2:
    def __init__(self, username: str, password: str, device_name: str):
        self._a2 = andersen_ev.AndersenA2()
        self._a2.authenticate(username, password)
        self._device = self._a2.device_by_name(device_name)
        self._deviceId = self._device["id"]

    def get_solar_override(self) -> bool:
        try:
            solar = self._a2.get_device_solar(self._deviceId)
            start_str = (
                solar.get("getDevice", {})
                .get("deviceInfo", {})
                .get("solarOverrideStart", None)
            )
            if not start_str:
                return False
            start = dt.datetime.fromisoformat(start_str).replace(tzinfo=None)
            return dt.datetime.utcnow() - start < dt.timedelta(hours=2)
        except Exception as e:
            logging.error(f"failed to fetch solar override: {e}")
            return False

    def get_max_grid_charge_percent(self):
        try:
            status = self._a2.get_device_status(self._deviceId)
            return int(status.get("deviceStatus", {}).get("solarMaxGridChargePercent"))
        except Exception as e:
            logging.error(f"failed to fetch max grid charge: {e}")
            return 0

    def set_charge_from_grid(self, charge_from_grid: bool):
        if charge_from_grid == self.get_charge_from_grid():
            logging.info(f"set_charge_from_grid {charge_from_grid} already set")
            return
        try:
            override = self.get_solar_override()
            logging.info(f"set_charge_from_grid {charge_from_grid} override={override}")
            self._a2.set_solar(
                deviceId=self._deviceId,
                override=override,
                chargeAlways=charge_from_grid,
                maxGridChargePercent=100 if charge_from_grid else 0,
            )
        except Exception as e:
            logging.error(f"failed to set charge mode: {e}")

    def get_charge_from_grid(self) -> bool:
        try:
            return self.get_max_grid_charge_percent() == 100
        except Exception as e:
            logging.error(f"failed to get charge mode: {e}")
            return False

if __name__ == "__main__":
    import dotenv, os, sys

    dotenv.load_dotenv()
    logging.basicConfig(level=logging.DEBUG)

    a2 = AndersenA2(
        os.getenv("ANDERSEN_USERNAME"),
        os.getenv("ANDERSEN_PASSWORD"),
        os.getenv("ANDERSEN_DEVICE_NAME"),
    )
    enable = "on" in sys.argv
    a2.set_charge_from_grid(enable)

