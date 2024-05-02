#!/usr/bin/env python3
import re
import shlex
import sys

import yaml

gitlab_ci = yaml.safe_load(sys.stdin)
for name, job in gitlab_ci.items():
    if "script" in job:
        if len(sys.argv) <= 1 or name == sys.argv[1]:
            # https://docs.gitlab.com/ee/ci/runners/hosted_runners/linux.html#container-images
            image = job.get("image") or gitlab_ci.get("image") or "ruby:3.1"
            if not re.search(r"^.*\..*[^/]", image):
                if not "/" in image:
                    image = f"library/{image}"
                image = f"docker.io/{image}"
            cmd = ["podman", "run", "-it", "-w", "/mnt", "-v", ".:/mnt", image]
            print("#", shlex.join(cmd))
            print("\n".join(job["script"]))
