#!/usr/bin/env python3
import argparse
import re
import shlex
import sys

import yaml

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "gitlab_ci_file",
    nargs="?",
    default=".gitlab-ci.yml",
    help="path to GitLab CI file",
)
parser.add_argument(
    "job", nargs="?", help="job to print; by default, all jobs are printed"
)
args = parser.parse_args()

gitlab_ci = yaml.safe_load(open(args.gitlab_ci_file))
for name, job in gitlab_ci.items():
    if "script" in job:
        if args.job is None or name == args.job:
            print(f"# Job: {name}")
            # https://docs.gitlab.com/ee/ci/runners/hosted_runners/linux.html#container-images
            image = job.get("image") or gitlab_ci.get("image") or "ruby:3.1"
            if not re.search(r"^.*\..*[^/]", image):
                if not "/" in image:
                    image = f"library/{image}"
                image = f"docker.io/{image}"
            cmd = ["podman", "run", "-it", "-w", "/mnt", "-v", ".:/mnt", image]
            print("#", shlex.join(cmd))
            print("\n".join(job["script"]))
