output "id" {
  description = "AKS cluster resource ID."
  value       = azurerm_kubernetes_cluster.this.id
}

output "name" {
  description = "AKS cluster name."
  value       = azurerm_kubernetes_cluster.this.name
}

output "kubelet_identity_object_id" {
  description = "Object ID of the kubelet identity (grant it AcrPull on your registry)."
  value       = azurerm_kubernetes_cluster.this.kubelet_identity[0].object_id
}
