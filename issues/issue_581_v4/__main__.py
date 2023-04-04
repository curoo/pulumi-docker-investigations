import base64
from datetime import datetime
from pathlib import Path

import pulumi
import pulumi_aws as aws
import pulumi_docker as docker

PROJECT_DIR = Path(__file__).resolve().parent


# https://github.com/pulumi/pulumi-docker/blob/master/examples/aws-container-registry/py/__main__.py
# Get registry info (creds and endpoint) so we can build/publish to it.
def _get_registry_info(rid):
    creds = aws.ecr.get_credentials(registry_id=rid)
    decoded = base64.b64decode(creds.authorization_token).decode()
    parts = decoded.split(":")
    if len(parts) != 2:
        raise Exception("Invalid credentials")
    return docker.RegistryArgs(
        server=creds.proxy_endpoint,
        username=parts[0],
        password=parts[1],
    )


ecr_repo = aws.ecr.Repository(
    resource_name="repo",
    name="issue_581_v4",
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
    build=docker.DockerBuildArgs(
        context=str(PROJECT_DIR),
        dockerfile=str(PROJECT_DIR / "Dockerfile"),
        platform="linux/amd64",
    ),
    registry=registry,
    image_name=pulumi.Output.concat(ecr_repo.repository_url, ":latest"),
)

# I expected image_name to be different to base_image_name, to contain a unique tag
pulumi.export("latest:base_image_name", image.base_image_name)
pulumi.export("latest:image_name", image.image_name)

workaround_tag = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")
workaround_image = docker.Image(
    "workaround_image",
    build=docker.DockerBuildArgs(
        context=str(PROJECT_DIR),
        dockerfile=str(PROJECT_DIR / "Dockerfile"),
        platform="linux/amd64",
    ),
    registry=registry,
    image_name=pulumi.Output.concat(ecr_repo.repository_url, ":", workaround_tag),
)

pulumi.export("specific_tag:base_image_name", workaround_image.base_image_name)
pulumi.export("specific_tag:image_name", workaround_image.image_name)
