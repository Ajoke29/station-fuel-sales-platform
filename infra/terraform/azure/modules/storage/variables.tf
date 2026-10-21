variable "name" {
  description = "Globally unique storage account name (3-24 lowercase letters/digits)."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.name))
    error_message = "Storage account names must be 3-24 lowercase letters or digits."
  }
}

variable "resource_group_name" {
  description = "Resource group to create the storage account in."
  type        = string
}

variable "location" {
  description = "Azure region."
  type        = string
}

variable "replication_type" {
  description = "Replication: LRS is cheapest; ZRS/GRS add resilience."
  type        = string
  default     = "LRS"
}

variable "allowed_ip_ranges" {
  description = "Public CIDR ranges allowed through the storage firewall."
  type        = list(string)
  default     = []
}

variable "allowed_subnet_ids" {
  description = "Subnet IDs allowed through the storage firewall (via service endpoints)."
  type        = list(string)
  default     = []
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace that receives blob diagnostics."
  type        = string
}

variable "tags" {
  description = "Tags to apply."
  type        = map(string)
  default     = {}
}
