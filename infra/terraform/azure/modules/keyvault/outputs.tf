output "id" {
  description = "Key Vault resource ID."
  value       = azurerm_key_vault.this.id
}

output "vault_uri" {
  description = "Key Vault URI, e.g. https://kv-name.vault.azure.net/."
  value       = azurerm_key_vault.this.vault_uri
}
