#!/usr/bin/env python3
"""Validate the Azure CLI identity used for Microsoft Fabric API access.

The script:
- authenticates through the current Azure CLI session;
- requests a Microsoft Fabric access token;
- inspects non-secret identity claims;
- validates the expected tenant and workload-identity client ID;
- writes non-secret JSON evidence.

The access token itself is never persisted.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential, CredentialUnavailableError


FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"


class IdentityPreflightFailure(RuntimeError):
    """Raised when an expected identity invariant is not satisfied."""


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the Azure CLI identity used to acquire "
            "a Microsoft Fabric access token."
        )
    )

    parser.add_argument(
        "--expected-tenant-id",
        required=True,
        help="Expected Microsoft Entra tenant ID.",
    )

    parser.add_argument(
        "--expected-client-id",
        required=True,
        help="Expected client ID of the workload identity.",
    )

    parser.add_argument(
        "--expected-identity-name",
        required=True,
        help="Human-readable identity name written to evidence.",
    )

    parser.add_argument(
        "--output",
        default="artifacts/fabric-identity-preflight.json",
        help="Path for non-secret JSON evidence.",
    )

    return parser.parse_args()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise IdentityPreflightFailure(message)


def normalize(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    value = value.strip()

    return value.lower() if value else None


def decode_jwt_payload(token: str) -> dict[str, Any]:
    parts = token.split(".")

    require(
        len(parts) >= 2,
        "The Fabric access token is not JWT-shaped.",
    )

    payload = parts[1]
    payload += "=" * (-len(payload) % 4)

    try:
        decoded = base64.urlsafe_b64decode(
            payload.encode("ascii")
        )

        claims = json.loads(
            decoded.decode("utf-8")
        )
    except (
        ValueError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as error:
        raise IdentityPreflightFailure(
            "The Fabric access-token payload could not be decoded."
        ) from error

    require(
        isinstance(claims, dict),
        "The Fabric token payload is not a JSON object.",
    )

    return claims


def determine_client_id(
    claims: dict[str, Any],
) -> str | None:
    return (
        normalize(claims.get("azp"))
        or normalize(claims.get("appid"))
    )


def main() -> int:
    arguments = parse_arguments()

    try:
        expected_tenant_id = normalize(
            arguments.expected_tenant_id
        )

        expected_client_id = normalize(
            arguments.expected_client_id
        )

        require(
            expected_tenant_id is not None,
            "Expected tenant ID is empty.",
        )

        require(
            expected_client_id is not None,
            "Expected client ID is empty.",
        )

        credential = AzureCliCredential(
            tenant_id=arguments.expected_tenant_id
        )

        access_token = credential.get_token(
            FABRIC_SCOPE
        )

        claims = decode_jwt_payload(
            access_token.token
        )

        actual_tenant_id = normalize(
            claims.get("tid")
        )

        actual_client_id = determine_client_id(
            claims
        )

        object_id = normalize(
            claims.get("oid")
        )

        require(
            actual_tenant_id == expected_tenant_id,
            (
                "Fabric token tenant mismatch: "
                f"actual '{actual_tenant_id}', "
                f"expected '{expected_tenant_id}'."
            ),
        )

        require(
            actual_client_id == expected_client_id,
            (
                "Fabric token client-ID mismatch: "
                f"actual '{actual_client_id}', "
                f"expected '{expected_client_id}'."
            ),
        )

        require(
            object_id is not None,
            "Fabric token contains no Entra object ID.",
        )

        evidence = {
            "generatedAtUtc": datetime.now(
                timezone.utc
            ).isoformat(),
            "validation": {
                "readOnly": True,
                "tokenPersisted": False,
                "tenantIdMatched": True,
                "clientIdMatched": True,
            },
            "authentication": {
                "credentialType": "AzureCliCredential",
                "requestedScope": FABRIC_SCOPE,
                "expectedIdentityName": (
                    arguments.expected_identity_name
                ),
                "tenantId": actual_tenant_id,
                "clientId": actual_client_id,
                "objectId": object_id,
                "identityTypeClaim": claims.get("idtyp"),
                "subject": claims.get("sub"),
                "audience": claims.get("aud"),
                "tokenExpiresOnUtc": datetime.fromtimestamp(
                    access_token.expires_on,
                    tz=timezone.utc,
                ).isoformat(),
            },
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

        print("Fabric workload identity preflight")
        print("==================================")
        print(
            "Expected identity: "
            f"{arguments.expected_identity_name}"
        )
        print(f"Tenant ID: {actual_tenant_id}")
        print(f"Client ID: {actual_client_id}")
        print(f"Object ID: {object_id}")
        print("Token persisted: no")
        print()
        print("IDENTITY PREFLIGHT SUCCEEDED")
        print(f"Evidence written to: {output_path}")

        return 0

    except (
        CredentialUnavailableError,
        ClientAuthenticationError,
    ) as error:
        print(
            "IDENTITY PREFLIGHT FAILED: "
            f"Azure CLI authentication failed. {error}",
            file=sys.stderr,
        )

        return 1

    except IdentityPreflightFailure as error:
        print(
            f"IDENTITY PREFLIGHT FAILED: {error}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
