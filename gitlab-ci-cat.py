#!/usr/bin/env python3
import argparse
import os
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
parser.add_argument("-e", "--exec", action="store_true", help="execute first found job")
parser.add_argument(
    "-r", "--runtime", default="podman", help="container runtime to execute the job"
)
args = parser.parse_args()

gitlab_ci = yaml.safe_load(open(args.gitlab_ci_file))
job_nr = 0
for name, job in gitlab_ci.items():
    if "script" in job:
        if args.job is None or name == args.job:
            variables = gitlab_ci.get("variables", {}) | job.get("variables", {})
            exports = [shlex.join(["export", f"{k}={v}"]) for k, v in variables.items()]
            script = "\n".join(
                exports
                + job.get("before_script", gitlab_ci.get("before_script", []))
                + job["script"]
            )
            if job_nr > 0:
                print()
            print(f"# Job: {name}")
            # https://docs.gitlab.com/ee/ci/runners/hosted_runners/linux.html#container-images
            # TODO: use image.entrypoint
            get_name = lambda obj: isinstance(obj, dict) and obj.get("name") or obj
            get_image = lambda obj: get_name(obj.get("image"))
            image = get_image(job) or get_image(gitlab_ci) or "ruby:3.1"
            if not re.search(r"^.*\..*[^/]", image):
            if not re.search(r"^[^/]*\.[^/]*[^/]", image):
                if not "/" in image:
                    image = f"library/{image}"
                image = f"registry-1.docker.io/{image}"
            cmd = [args.runtime, "run", "-it", "-w", "/mnt", "-v", ".:/mnt", image]
            print("#", shlex.join(cmd))
            print(script)
            if args.exec:
                os.execvp(cmd[0], cmd + ["sh", "-c", script])
            job_nr += 1
