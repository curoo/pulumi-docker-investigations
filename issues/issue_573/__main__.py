import base64
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
    resource_name="issue_573:repo",
    name="issue_573",
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
    "issue_573:image",
    build=docker.DockerBuildArgs(
        context=str(PROJECT_DIR),
        dockerfile=str(PROJECT_DIR / "Dockerfile"),
        platform="linux/amd64",
        # Despite https://github.com/pulumi/pulumi-docker/issues/576
        # an image has already been pushed, in this example, so enable cache_from
        cache_from=docker.CacheFromArgs(images=[pulumi.Output.concat(ecr_repo.repository_url, ":latest")])
    ),
    registry=registry,
    image_name=pulumi.Output.concat(ecr_repo.repository_url, ":latest"),
)
