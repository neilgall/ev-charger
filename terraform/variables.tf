variable "region" {
    description = "The AWS region to deploy the lambda function"
    type = string
    default = "eu-west-1"
}

variable "alexa-skill-id" {
    description = "The ID of the Alexa Skill which invokes the lambda"
    type = string
    default = "amzn1.ask.skill.a6f6fcc8-510c-4c94-940b-78b4c53cc9bc"
}