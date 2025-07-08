resource "aws_iot_thing" "ev_charger" {
  name = "AndersenEVCharger"
}

resource "aws_iam_role" "lambda_execution_role" {
  name = "ev_charger_lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "iot_policy" {
  name        = "ev_charger_iot_policy"
  description = "Policy to allow Lambda to interact with IoT Thing Shadow"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "iot:UpdateThingShadow",
          "iot:GetThingShadow"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:iot:${var.region}:${data.aws_caller_identity.current.account_id}:thing/${aws_iot_thing.ev_charger.name}"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_iot_policy" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.iot_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "ev_charger_lambda" {
  function_name = "ev_charger_lambda"
  architectures = ["arm64"]
  runtime       = "python3.12"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "lambda_function.lambda_handler"

  filename         = "${path.module}/../lambda/build/lambda_function.zip"
  source_code_hash = filebase64sha256("${path.module}/../lambda/build/lambda_function.zip")

  environment {
    variables = {
      IOT_THING_NAME = aws_iot_thing.ev_charger.name
    }
  }
}
