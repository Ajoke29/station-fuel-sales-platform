#!/usr/bin/env python3
"""Pull the plain Prometheus rule groups out of a PrometheusRule manifest,
so `promtool check rules` and `promtool test rules` can validate them."""

import sys

import yaml

src, dst = sys.argv[1], sys.argv[2]
with open(src, encoding="utf-8") as fh:
    manifest = yaml.safe_load(fh)
with open(dst, "w", encoding="utf-8") as fh:
    yaml.safe_dump({"groups": manifest["spec"]["groups"]}, fh, sort_keys=False)
print(f"wrote {dst}")
