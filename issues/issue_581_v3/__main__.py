import base64
from pathlib import Path

import pulumi
import pulumi_aws as aws
import pulumi_docker as docker

PROJECT_DIR = Path(__file__).resolve().parent


# Get registry info (creds and endpoint) so we can build/publish to it.
def _get_registry_info(rid):
    creds = aws.ecr.get_credentials(registry_id=rid)
    decoded = base64.b64decode(creds.authorization_token).decode()
    parts = decoded.split(":")
    if len(parts) != 2:
        raise Exception("Invalid credentials")
    return docker.ImageRegistry(creds.proxy_endpoint, parts[0], parts[1])


ecr_repo = aws.ecr.Repository(
    resource_name="repo",
    name="issue_581_v3",
    force_delete=True,
    # Tags are not relevant to the issue
    # but mandatory for the AWS permissions (not shown here)
    tags={
        "pulumi:project": pulumi.get_project(),
        "pulumi:stack": pulumi.get_stack(),
    }
)

registry = ecr_repo.registry_id.apply(_get_registry_info)

image = docker.Image(
    "image",
    build=docker.DockerBuild(
        context=str(PROJECT_DIR),
        dockerfile=str(PROJECT_DIR / "Dockerfile"),
        # This is how I enabled buildkit in v3 for improved caching and build speed
        env={"DOCKER_BUILDKIT": "1"},
        extra_options=["--build-arg", "BUILDKIT_INLINE_CACHE=1"],
    ),
    registry=registry,
    image_name=pulumi.Output.concat(ecr_repo.repository_url, ":latest"),
)

pulumi.export("base_image_name", image.base_image_name)
pulumi.export("image_name", image.image_name)
