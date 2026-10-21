output "resource_group_name" {
  description = "Name of the resource group holding everything."
  value       = azurerm_resource_group.this.name
}

output "vnet_id" {
  description = "ID of the virtual network."
  value       = module.network.vnet_id
}

output "subnet_ids" {
  description = "Map of subnet name to subnet ID."
  value       = module.network.subnet_ids
}

output "storage_account_name" {
  description = "Name of the storage account (for station sales file drops)."
  value       = module.storage.name
}

output "key_vault_uri" {
  description = "URI of the Key Vault for app secrets."
  value       = module.keyvault.vault_uri
}

output "log_analytics_workspace_id" {
  description = "ID of the Log Analytics workspace that collects logs and diagnostics."
  value       = module.monitoring.workspace_id
}

output "aks_cluster_name" {
  description = "Name of the AKS cluster, or null when enable_aks is false."
  value       = var.enable_aks ? module.aks[0].name : null
}
