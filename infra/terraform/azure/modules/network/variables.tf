variable "name_prefix" {
  description = "Prefix for resource names, e.g. fuelsales-dev."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group to create the network in."
  type        = string
}

variable "location" {
  description = "Azure region."
  type        = string
}

variable "address_space" {
  description = "VNet address space."
  type        = list(string)
}

variable "subnets" {
  description = "Subnets keyed by name. Must include \"app\" (gets the web NSG) and \"data\"."
  type = map(object({
    address_prefixes = list(string)
  }))

  validation {
    condition     = contains(keys(var.subnets), "app") && contains(keys(var.subnets), "data")
    error_message = "subnets must contain keys \"app\" and \"data\"."
  }
}

variable "tags" {
  description = "Tags to apply."
  type        = map(string)
  default     = {}
}
