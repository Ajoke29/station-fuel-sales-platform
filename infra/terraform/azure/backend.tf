# Remote state example (commented out so `terraform init -backend=false` and
# local experiments work with no Azure account).
#
# For a team, keep state in an Azure Storage container so everyone shares one
# copy with locking. Create the storage account once (by hand or a bootstrap
# script), then uncomment and run `terraform init -migrate-state`.
#
# terraform {
#   backend "azurerm" {
#     resource_group_name  = "rg-tfstate-shared"
#     storage_account_name = "sttfstatefuelsales"
#     container_name       = "tfstate"
#     key                  = "station-fuel-sales/dev.tfstate"
#     use_azuread_auth     = true
#   }
# }
