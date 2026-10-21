variable "name" {
  description = "AKS cluster name (also used as the DNS prefix)."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group to create the cluster in."
  type        = string
}

variable "location" {
  description = "Azure region."
  type        = string
}

variable "node_vm_size" {
  description = "VM size for the system node pool."
  type        = string
  default     = "Standard_B2s"
}

variable "node_count" {
  description = "Number of nodes in the system node pool."
  type        = number
  default     = 1
}

variable "subnet_id" {
  description = "Subnet ID for the AKS nodes."
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace for Container Insights."
  type        = string
}

variable "tags" {
  description = "Tags to apply."
  type        = map(string)
  default     = {}
}
