variable "subscription_id" {
  description = "Azure subscription ID to deploy into. Leave null to use ARM_SUBSCRIPTION_ID or the Azure CLI default."
  type        = string
  default     = null
}

variable "project" {
  description = "Short project name used in resource names."
  type        = string
  default     = "fuelsales"

  validation {
    condition     = can(regex("^[a-z0-9]{3,12}$", var.project))
    error_message = "project must be 3-12 lowercase letters or digits (it is used in storage account names)."
  }
}

variable "environment" {
  description = "Environment name, e.g. dev or prod."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "environment must be one of: dev, test, prod."
  }
}

variable "location" {
  description = "Azure region. Canada East (Quebec) or Canada Central (Toronto) keep data in Canada."
  type        = string
  default     = "canadaeast"
}

variable "vnet_address_space" {
  description = "Address space for the virtual network."
  type        = list(string)
  default     = ["10.40.0.0/16"]
}

variable "subnets" {
  description = "Subnets to create: one for the app/AKS nodes and one for private endpoints and data services."
  type = map(object({
    address_prefixes = list(string)
  }))
  default = {
    app = {
      address_prefixes = ["10.40.1.0/24"]
    }
    data = {
      address_prefixes = ["10.40.2.0/24"]
    }
  }
}

variable "allowed_ip_ranges" {
  description = "Public IP ranges (CIDR) allowed to reach the storage account and Key Vault, e.g. your office IP. Empty means Azure services only."
  type        = list(string)
  default     = []
}

variable "log_retention_days" {
  description = "How many days Log Analytics keeps logs (30 is the cheapest tier)."
  type        = number
  default     = 30
}

variable "enable_aks" {
  description = "Create a small AKS cluster. Off by default because AKS nodes cost money while they run."
  type        = bool
  default     = false
}

variable "aks_node_vm_size" {
  description = "VM size for the AKS system node pool (only used when enable_aks = true)."
  type        = string
  default     = "Standard_B2s"
}

variable "aks_node_count" {
  description = "Number of AKS nodes (only used when enable_aks = true)."
  type        = number
  default     = 1
}

variable "tags" {
  description = "Extra tags added to every resource."
  type        = map(string)
  default     = {}
}
