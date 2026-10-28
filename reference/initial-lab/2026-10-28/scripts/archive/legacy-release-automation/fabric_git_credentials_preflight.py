#!/usr/bin/env python3
"""Inspect Fabric Git credentials for the non-production release identity.

This command is read-only.

It:
- authenticates through the current Azure CLI session;
- discovers the DEV workspace;
- reads the existing Fabric Git connection;
- reads the caller-specific Git credential configuration;
- lists Fabric connections visible to the caller;
- identifies Azure DevOps Source Control connection candidates;
- optionally verifies that the configured connection is visible;
- reads Fabric Git status when credentials are configured;
- writes non-secret JSON evidence.

It does not change Git credentials and does not call updateFromGit.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential, CredentialUnavailableError


FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"
FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"
FABRIC_HOST = "api.fabric.microsoft.com"

DEV_WORKSPACE_NAME = "ws_reference_lab_dev"
EXPECTED_BRANCH = "dev"


class GitCredentialPreflightFailure(RuntimeError):
    """Raised when an expected Git configuration invariant is violated."""


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect Fabric Git-provider credentials visible to the "
            "non-production release identity."
        )
    )

    parser.add_argument(
        "--tenant-id",
        required=True,
        help="Microsoft Entra tenant ID.",
    )

    parser.add_argument(
        "--output",
        default="artifacts/fabric-git-credentials-preflight.json",
        help="Path for generated non-secret JSON evidence.",
    )

    return parser.parse_args()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GitCredentialPreflightFailure(message)


def validate_url(url: str) -> None:
    parsed = urlparse(url)

    require(
        parsed.scheme == "https"
        and parsed.hostname == FABRIC_HOST,
        (
            "Refusing to send a Fabric bearer token to "
            f"unexpected URL: {url}"
        ),
    )


def request_json(
    session: requests.Session,
    url: str,
    headers: dict[str, str],
) -> dict[str, Any]:
    validate_url(url)

    response = session.get(
        url,
        headers=headers,
        timeout=60,
    )

    if response.status_code != 200:
        try:
            body = response.json()
        except requests.JSONDecodeError:
            body = response.text.strip()

        raise GitCredentialPreflightFailure(
            f"GET {url} failed with HTTP "
            f"{response.status_code}: {body}"
        )

    try:
        payload = response.json()
    except requests.JSONDecodeError as error:
        raise GitCredentialPreflightFailure(
            f"GET {url} returned invalid JSON."
        ) from error

    require(
        isinstance(payload, dict),
        f"GET {url} returned unexpected JSON.",
    )

    return payload


def single(
    values: Any,
    predicate,
    description: str,
) -> dict[str, Any]:
    require(
        isinstance(values, list),
        f"{description} collection is not a list.",
    )

    matches = [
        value
        for value in values
        if isinstance(value, dict)
        and predicate(value)
    ]

    require(
        len(matches) == 1,
        (
            f"Expected exactly one {description}; "
            f"found {len(matches)}."
        ),
    )

    return matches[0]


def connection_type(
    connection: dict[str, Any],
) -> str | None:
    details = connection.get("connectionDetails")

    if not isinstance(details, dict):
        return None

    value = details.get("type")

    return value if isinstance(value, str) else None


def safe_connection_evidence(
    connection: dict[str, Any],
) -> dict[str, Any]:
    credential_details = connection.get(
        "credentialDetails"
    )

    credential_type = None

    if isinstance(credential_details, dict):
        credential_type = credential_details.get(
            "credentialType"
        )

    return {
        "id": connection.get("id"),
        "displayName": connection.get("displayName"),
        "connectivityType": connection.get(
            "connectivityType"
        ),
        "connectionType": connection_type(
            connection
        ),
        "credentialType": credential_type,
    }


def main() -> int:
    arguments = parse_arguments()

    try:
        credential = AzureCliCredential(
            tenant_id=arguments.tenant_id
        )

        access_token = credential.get_token(
            FABRIC_SCOPE
        )

        headers = {
            "Authorization": (
                f"Bearer {access_token.token}"
            ),
            "Accept": "application/json",
        }

        with requests.Session() as session:
            workspaces = request_json(
                session,
                f"{FABRIC_API_BASE}/workspaces",
                headers,
            )

            dev_workspace = single(
                workspaces.get("value"),
                lambda value: (
                    value.get("displayName")
                    == DEV_WORKSPACE_NAME
                ),
                (
                    "visible workspace named "
                    f"'{DEV_WORKSPACE_NAME}'"
                ),
            )

            workspace_id = dev_workspace.get("id")

            require(
                isinstance(workspace_id, str)
                and bool(workspace_id),
                "DEV workspace ID is missing.",
            )

            connection = request_json(
                session,
                (
                    f"{FABRIC_API_BASE}/workspaces/"
                    f"{workspace_id}/git/connection"
                ),
                headers,
            )

            provider = connection.get(
                "gitProviderDetails"
            )

            require(
                isinstance(provider, dict),
                "DEV Git provider details are missing.",
            )

            require(
                provider.get("gitProviderType")
                == "AzureDevOps",
                (
                    "DEV workspace is not connected "
                    "to Azure DevOps Git."
                ),
            )

            require(
                provider.get("branchName")
                == EXPECTED_BRANCH,
                (
                    "DEV workspace is connected to "
                    f"'{provider.get('branchName')}', "
                    f"expected '{EXPECTED_BRANCH}'."
                ),
            )

            git_credentials = request_json(
                session,
                (
                    f"{FABRIC_API_BASE}/workspaces/"
                    f"{workspace_id}/git/"
                    "myGitCredentials"
                ),
                headers,
            )

            connections_payload = request_json(
                session,
                f"{FABRIC_API_BASE}/connections",
                headers,
            )

            visible_connections = [
                safe_connection_evidence(value)
                for value in connections_payload.get(
                    "value",
                    [],
                )
                if isinstance(value, dict)
            ]

            source_control_connections = [
                value
                for value in connections_payload.get(
                    "value",
                    [],
                )
                if (
                    isinstance(value, dict)
                    and connection_type(value)
                    == "AzureDevOpsSourceControl"
                )
            ]

            source_control_evidence = [
                safe_connection_evidence(value)
                for value in source_control_connections
            ]

            configured_connection = None
            git_status = None

            if (
                git_credentials.get("source")
                == "ConfiguredConnection"
            ):
                configured_id = (
                    git_credentials.get("connectionId")
                )

                matches = [
                    value
                    for value
                    in source_control_connections
                    if value.get("id") == configured_id
                ]

                require(
                    len(matches) == 1,
                    (
                        "The configured Git connection "
                        "is not visible to the caller."
                    ),
                )

                configured_connection = (
                    safe_connection_evidence(
                        matches[0]
                    )
                )

                git_status = request_json(
                    session,
                    (
                        f"{FABRIC_API_BASE}/workspaces/"
                        f"{workspace_id}/git/status"
                    ),
                    headers,
                )

            evidence = {
                "generatedAtUtc": datetime.now(
                    timezone.utc
                ).isoformat(),
                "validation": {
                    "readOnly": True,
                    "workspaceFound": True,
                    "azureDevOpsConnectionFound": True,
                },
                "workspace": {
                    "id": workspace_id,
                    "name": DEV_WORKSPACE_NAME,
                },
                "gitConnection": connection,
                "myGitCredentials": git_credentials,
                "configuredConnection": (
                    configured_connection
                ),
                "azureDevOpsSourceControlConnections": (
                    source_control_evidence
                ),
                "visibleConnectionCount": len(
                    visible_connections
                ),
                "gitStatus": git_status,
            }

            output_path = Path(arguments.output)

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_path.write_text(
                json.dumps(
                    evidence,
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            print("Fabric Git credential preflight")
            print("===============================")
            print(
                "Workspace: "
                f"{DEV_WORKSPACE_NAME}"
            )
            print(
                "Git branch: "
                f"{provider.get('branchName')}"
            )
            print(
                "Credential source: "
                f"{git_credentials.get('source')}"
            )
            print(
                "Visible Azure DevOps Source "
                "Control connections: "
                f"{len(source_control_connections)}"
            )

            if configured_connection:
                print(
                    "Configured connection: "
                    f"{configured_connection['displayName']}"
                )
                print(
                    "Credential type: "
                    f"{configured_connection['credentialType']}"
                )
                print()
                print(
                    "GIT CREDENTIAL PREFLIGHT "
                    "READY FOR SYNCHRONIZATION"
                )
            else:
                print()
                print(
                    "GIT CREDENTIAL CONFIGURATION "
                    "REQUIRED"
                )

            print(
                f"Evidence written to: {output_path}"
            )

        return 0

    except (
        CredentialUnavailableError,
        ClientAuthenticationError,
    ) as error:
        print(
            "GIT CREDENTIAL PREFLIGHT FAILED: "
            f"authentication failed. {error}",
            file=sys.stderr,
        )

        return 1

    except GitCredentialPreflightFailure as error:
        print(
            f"GIT CREDENTIAL PREFLIGHT FAILED: {error}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())