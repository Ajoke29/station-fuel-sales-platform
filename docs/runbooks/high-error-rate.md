# Runbook: High error rate (5xx)

**Alert:** `StationFuelSalesHighErrorRate` (critical): more than 5% of requests
returned a server error (HTTP 5xx) for 5 minutes.

## What it means (plain language)
People or systems asking the app for sales data are getting "something went wrong
on our side" answers. Pods might look healthy, but the answers are failing.

## Check (5 minutes)
1. Open the **Station Fuel Sales** Grafana dashboard. Look at "Requests per second by
   status" and "by route": which route is failing, and when did it start?
2. Did something just change?
   ```bash
   NS=fuel-sales-dev
   helm -n $NS history station-fuel-sales      # recent releases
   kubectl -n $NS rollout history deploy/station-fuel-sales
   ```
   Also check the latest pipeline run and the Argo CD app history.
3. Read the logs:
   ```bash
   kubectl -n $NS logs deploy/station-fuel-sales --since=15m | grep -i -E "error|traceback"
   ```
4. Query Prometheus directly:
   ```promql
   sum by (path, status) (rate(http_requests_total{namespace="fuel-sales-dev", status=~"5.."}[5m]))
   ```

## Common causes and fixes
| What you see | Likely cause | Fix |
|---|---|---|
| Errors started right after a deploy | Bad release | Roll back (below), then fix forward in a new commit |
| Only `/api/chaos/error` failing | Someone is testing alerts (`CHAOS_ENABLED=true` in dev) | Expected in dev; ensure it is `false` in prod |
| Errors plus high latency, CPU at limit | Overloaded | Scale out (`kubectl scale` or raise HPA max), then review limits |
| Errors on every route | Config or dependency problem | Check ConfigMap values and pod logs |

## Roll back quickly
```bash
git revert <bad-commit> && git push                 # GitOps way (Argo CD re-syncs)
helm -n $NS rollback station-fuel-sales <revision>  # direct Helm way
```

## Practise it (dev only)
```bash
# Send a mix of good and failing requests for about 7 minutes
end=$((SECONDS + 420))
while [ $SECONDS -lt $end ]; do
  curl -s -o /dev/null localhost:8080/api/sales
  curl -s -o /dev/null localhost:8080/api/chaos/error
  sleep 0.5
done
```
The alert should go to "pending" within a couple of minutes and "firing" after it
has stayed above 5% for 5 minutes. Check it in Prometheus under **Alerts**.
