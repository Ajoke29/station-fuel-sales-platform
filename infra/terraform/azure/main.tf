locals {
  name_prefix = "${var.project}-${var.environment}"

  tags = merge(
    {
      project     = "station-fuel-sales-platform"
      environment = var.environment
      managed_by  = "terraform"
      owner       = "it-ops"
      cost_center = "it-shared"
    },
    var.tags,
  )
}

data "azurerm_client_config" "current" {}

# Short random suffix so globally-unique names (storage, Key Vault) don't clash
resource "random_string" "suffix" {
  length  = 5
  upper   = false
  special = false
}

resource "azurerm_resource_group" "this" {
  name     = "rg-${local.name_prefix}"
  location = var.location
  tags     = local.tags
}

module "monitoring" {
  source = "./modules/monitoring"

  name                = "log-${local.name_prefix}"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  retention_in_days   = var.log_retention_days
  tags                = local.tags
}

module "network" {
  source = "./modules/network"

  name_prefix         = local.name_prefix
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  address_space       = var.vnet_address_space
  subnets             = var.subnets
  tags                = local.tags
}

module "storage" {
  source = "./modules/storage"

  name                       = substr("st${var.project}${var.environment}${random_string.suffix.result}", 0, 24)
  resource_group_name        = azurerm_resource_group.this.name
  location                   = azurerm_resource_group.this.location
  allowed_ip_ranges          = var.allowed_ip_ranges
  allowed_subnet_ids         = [module.network.subnet_ids["data"]]
  log_analytics_workspace_id = module.monitoring.workspace_id
  tags                       = local.tags
}

module "keyvault" {
  source = "./modules/keyvault"

  name                       = substr("kv-${var.project}-${var.environment}-${random_string.suffix.result}", 0, 24)
  resource_group_name        = azurerm_resource_group.this.name
  location                   = azurerm_resource_group.this.location
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  admin_object_id            = data.azurerm_client_config.current.object_id
  allowed_ip_ranges          = var.allowed_ip_ranges
  allowed_subnet_ids         = [module.network.subnet_ids["data"]]
  log_analytics_workspace_id = module.monitoring.workspace_id
  tags                       = local.tags
}

module "aks" {
  source = "./modules/aks"
  count  = var.enable_aks ? 1 : 0

  name                       = "aks-${local.name_prefix}"
  resource_group_name        = azurerm_resource_group.this.name
  location                   = azurerm_resource_group.this.location
  node_vm_size               = var.aks_node_vm_size
  node_count                 = var.aks_node_count
  subnet_id                  = module.network.subnet_ids["app"]
  log_analytics_workspace_id = module.monitoring.workspace_id
  tags                       = local.tags
}
