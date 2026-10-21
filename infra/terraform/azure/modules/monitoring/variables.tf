variable "name" {
  description = "Log Analytics workspace name."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group to create the workspace in."
  type        = string
}

variable "location" {
  description = "Azure region."
  type        = string
}

variable "retention_in_days" {
  description = "Days to keep logs (30-730)."
  type        = number
  default     = 30
}

variable "daily_quota_gb" {
  description = "Daily ingestion cap in GB, a safety net against surprise bills. -1 means no cap."
  type        = number
  default     = 1
}

variable "tags" {
  description = "Tags to apply."
  type        = map(string)
  default     = {}
}
