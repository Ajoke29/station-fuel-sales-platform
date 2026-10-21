# Azure infrastructure (Terraform)

This folder describes the Azure "home" for the platform as code. Nothing here has
been applied. CI only runs `terraform fmt -check` and `terraform validate`, which
are free and need no Azure account.

## What it would create

| Piece | Why | Secure defaults |
|---|---|---|
| Resource group `rg-fuelsales-dev` | One box to hold (and delete) everything | Tagged with project, env, owner, cost centre |
| Virtual network + 2 subnets (`app`, `data`) | Private network for the app and data services | Service endpoints for Storage and Key Vault |
| Network security group on `app` subnet | Firewall for the app subnet | Only TCP 80 and 443 allowed in from the internet; everything else denied by default |
| Storage account | Where stations could drop daily sales files | TLS 1.2 minimum, HTTPS only, no public blob access, no shared keys (Entra ID only), firewall default **Deny**, versioning and soft delete |
| Key Vault | Store secrets (DB passwords, API keys) outside the code | Azure RBAC, purge protection, soft delete, firewall default **Deny**, audit logs to Log Analytics |
| Log Analytics workspace | One place for logs and diagnostics | 30-day retention, 1 GB/day cap so a mistake can't run up a big bill |
| AKS cluster (optional) | Managed Kubernetes to run the app | **Off by default** (`enable_aks = false`). Free tier control plane, 1 small node, Azure CNI overlay, network policy, workload identity, Container Insights |

Code layout:

```
azure/
├── versions.tf        # Terraform + provider versions
├── providers.tf       # azurerm provider settings
├── backend.tf         # remote state example (commented out)
├── variables.tf       # every input, with a description
├── main.tf            # wires the modules together
├── outputs.tf         # useful values after apply
├── terraform.tfvars.example
└── modules/
    ├── network/       # VNet, subnets, NSG
    ├── storage/       # storage account + diagnostics
    ├── keyvault/      # Key Vault + RBAC + diagnostics
    ├── monitoring/    # Log Analytics workspace
    └── aks/           # optional AKS cluster
```

## Check it for free (no Azure account needed)

```bash
cd infra/terraform/azure
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
```

## If you want to really build it (cheaply), then tear it down

You need an Azure subscription (a free account works) and the Azure CLI.

```bash
az login
export ARM_SUBSCRIPTION_ID=$(az account show --query id -o tsv)

cd infra/terraform/azure
cp terraform.tfvars.example terraform.tfvars   # put your own public IP in allowed_ip_ranges
terraform init
terraform plan -out tfplan        # shows exactly what will be created; still free
terraform apply tfplan            # this is the step that creates (and may bill) resources
terraform output
```

**Delete everything when you are done:**

```bash
terraform destroy
```

Cost notes:

- With `enable_aks = false`, the network, NSG, Key Vault and an empty storage account
  cost cents per day. Log Analytics is billed per GB ingested (capped at 1 GB/day here).
- With `enable_aks = true`, the AKS control plane is free (Free tier) but the node VM
  (Standard_B2s) and its disk are billed by the hour. Build it, practise, destroy it
  the same day.
- Key Vault has purge protection, so after `destroy` the vault name stays reserved
  (soft-deleted) for 7 days. Terraform picks a random suffix each time, so a rebuild
  still works.
- Set a budget alert in Azure Cost Management before applying anything.

## Remote state for a team

`backend.tf` shows how state would live in an Azure Storage container (shared,
locked, encrypted) instead of on one laptop. Uncomment it once that storage exists.
