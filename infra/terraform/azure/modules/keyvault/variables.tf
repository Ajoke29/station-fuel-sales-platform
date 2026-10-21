variable "name" {
  description = "Globally unique Key Vault name (3-24 characters)."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group to create the Key Vault in."
  type        = string
}

variable "location" {
  description = "Azure region."
  type        = string
}

variable "tenant_id" {
  description = "Microsoft Entra tenant ID that owns the vault."
  type        = string
}

variable "admin_object_id" {
  description = "Object ID of the user or service principal that may manage secrets."
  type        = string
}

variable "soft_delete_retention_days" {
  description = "Days a deleted vault or secret can be recovered (7-90)."
  type        = number
  default     = 7
}

variable "allowed_ip_ranges" {
  description = "Public CIDR ranges allowed through the Key Vault firewall."
  type        = list(string)
  default     = []
}

variable "allowed_subnet_ids" {
  description = "Subnet IDs allowed through the Key Vault firewall."
  type        = list(string)
  default     = []
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace that receives Key Vault audit logs."
  type        = string
}

variable "tags" {
  description = "Tags to apply."
  type        = map(string)
  default     = {}
}
