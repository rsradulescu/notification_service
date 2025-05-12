data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

module "notification_service" {
  source = "./aws_notification_service/terraform"

  name = "notification_service"

  dst_param_prefix = "ssm/notification_service"
  ses_configuration = {
    config_set = "SERVICE-SES"
    identity = "gmail.com"
    sender = "no-reply@gmail.com"
  }
}
