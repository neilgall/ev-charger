# EV Charger
This repo contains an AWS Lambda function to control an Andersen A2 EV Charger. It has two main functions:

1. Respond to AWS Event Bridge scheduled events. If the current time is between midnight and 5am, the EV charger is configured for 100% grid energy. At other times the EV charger is configured for 100% solar energy.

2. Respond to invocations from an Alexa skill supporting two intents:

* `CheckChargingModeIntent`, which will read out the current mode set on the charger
* `SetChargingModeIntent`, which requires a slot called `mode` containing the string `grid` or `solar`.
