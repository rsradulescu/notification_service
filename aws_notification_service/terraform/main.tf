module "notification_function" {
  source = "./lambda"

  name = "${var.name}-lambda"
  src_path = "${path.root}/aws_notification_service/app/src"

  policies = {
    main = data.aws_iam_policy_document.lambda.json
  }

  environment_variables = {
    "SES_SENDER" = var.ses_configuration.sender,
    "SES_CONFIGURATION_SET" = var.ses_configuration.config_set,
    "DST_PARAM_PREFIX" = var.dst_param_prefix
  }

}

module "notification_queue" {
  source = "./sqs"

  name = "${var.name}-sqs"

  principals = [
    {
      type        = "Service"
      identifier = "events.amazonaws.com"
    }
  ]
}

data "aws_iam_policy_document" "lambda" {
  statement {
    effect = "Allow"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
    ]
    resources = [
        module.notification_queue.arn
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "tag:GetResources",
    ]
    resources = [
        "*"
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParametersByPath",
    ]
    resources = [
      "arn:aws:ssm:${local.region}:${local.account}:parameter/${var.dst_param_prefix}/*"
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "ses:SendEmail",
    ]
    resources = [
      "arn:aws:ses:${local.region}:${local.account}:identity/${var.ses_configuration.identity}",
      "arn:aws:ses:${local.region}:${local.account}:configuration-set/${var.ses_configuration.config_set}",
    ]
  }
}

resource "aws_lambda_event_source_mapping" "this" {
  event_source_arn = module.notification_queue.arn
  function_name    = module.notification_function.arn
}

locals {
  region  = data.aws_region.current.id
  account = data.aws_caller_identity.current.account_id
}
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
