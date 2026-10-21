# Runbook: Pod restarting / CrashLoopBackOff

**Alerts:** `StationFuelSalesPodRestarting` (warning), `StationFuelSalesPodCrashLooping` (critical)

## What it means (plain language)
Kubernetes starts the app, the app stops or fails its health check, and Kubernetes
starts it again. If this keeps happening, Kubernetes waits longer between tries.
That waiting state is called **CrashLoopBackOff**. With 2+ replicas, users may not
notice yet, but we are running with less safety margin.

## Check (5 minutes)
```bash
NS=fuel-sales-dev
kubectl -n $NS get pods                                   # which pods, how many restarts
kubectl -n $NS describe pod <pod>                         # read "Last State" and "Events"
kubectl -n $NS logs <pod> --previous                      # logs from the crashed run
kubectl -n $NS get events --sort-by=.lastTimestamp | tail -20
```

## Common causes and fixes
| What you see | Likely cause | Fix |
|---|---|---|
| `Last State: Terminated, Reason: OOMKilled` | Memory limit too low | Raise `resources.limits.memory` in the values file, commit, let CI/Argo CD roll out |
| `Liveness probe failed` in Events | App too slow to start, or hung | Check logs; if it is slow start, raise `livenessProbe.initialDelaySeconds` |
| `ValueError: SALES_SEED must be an integer` in logs | Bad value in the ConfigMap | Fix `config.*` in the values file |
| `ImagePullBackOff` / `ErrImagePull` | Wrong tag or no registry access | Check `image.tag` exists in the registry; check pull secret |
| `Read-only file system` in logs | Code writing outside `/tmp` | Write to `/tmp` (an emptyDir) or add a volume |

## Roll back quickly
```bash
# GitOps (Argo CD): revert the bad commit in Git; Argo CD syncs it back
git revert <commit> && git push
# Plain Helm:
helm -n $NS history station-fuel-sales
helm -n $NS rollback station-fuel-sales <previous-revision>
```

## After it is fixed
- Confirm `kubectl -n $NS get pods` shows all pods `Running` and `READY 1/1`.
- Write two or three lines in the ticket: cause, fix, and how to stop it happening again.
