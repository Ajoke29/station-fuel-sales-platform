output "vnet_id" {
  description = "ID of the virtual network."
  value       = azurerm_virtual_network.this.id
}

output "subnet_ids" {
  description = "Map of subnet key to subnet ID."
  value       = { for k, s in azurerm_subnet.this : k => s.id }
}

output "app_nsg_id" {
  description = "ID of the NSG attached to the app subnet."
  value       = azurerm_network_security_group.app.id
}
