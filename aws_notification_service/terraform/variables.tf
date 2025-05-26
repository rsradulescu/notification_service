variable "name" {
  type = string
  description = "Function name."
}

variable "dst_param_prefix" {
  type = string
  description = "Destination parameter prefix (SSM Parameter store)."
}

variable "ses_configuration" {
  type = object(
    {
      sender = string
      identity = string
      config_set = string
    }
  )
  description = "SES configuration."
}

variable "common_tags" {
  type = map(string)
  description = "Common tags."
  default = {}
}
