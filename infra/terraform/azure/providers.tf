# Authentication comes from your Azure CLI login (`az login`) or from
# ARM_* environment variables in a pipeline. Nothing secret lives in this repo.
provider "azurerm" {
  features {
    key_vault {
      # Keep deleted vaults recoverable instead of purging them on destroy
      purge_soft_delete_on_destroy = false
    }
    resource_group {
      prevent_deletion_if_contains_resources = true
    }
  }

  # Optional: set var.subscription_id, or export ARM_SUBSCRIPTION_ID instead
  subscription_id = var.subscription_id
}
