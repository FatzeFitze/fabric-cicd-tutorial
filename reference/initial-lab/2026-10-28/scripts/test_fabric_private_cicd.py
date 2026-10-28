#!/usr/bin/env python3
"""Validate Fabric private API access and direct Item Definition deployment.

The script is intentionally compatible with Python 3.8 and has no third-party
Python dependencies. AzureCLI@2 establishes the workload-identity session; the
script obtains a Fabric token from that Azure CLI session and uses curl for
HTTP calls so a workspace-specific hostname can be pinned to a Private
Endpoint IP without changing VM-wide DNS or /etc/hosts.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlencode, urlparse


FABRIC_RESOURCE = "https://api.fabric.microsoft.com"
PUBLIC_HOST = "api.fabric.microsoft.com"
PUBLIC_BASE_URL = "https://api.fabric.microsoft.com"
CANARY_NAME = "__cicd_private_api_canary"
PRIVATE_NETWORKS = (
    IPv4Network("10.0.0.0/8"),
    IPv4Network("172.16.0.0/12"),
    IPv4Network("192.168.0.0/16"),
)


class ProbeFailure(RuntimeError):
    """Raised when a required probe invariant is not satisfied."""


@dataclass
class FabricResponse:
    method: str
    url: str
    status_code: int
    remote_ip: str
    headers: Dict[str, str]
    body: str
    json_body: Optional[Any]


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in ("true", "1", "yes"):
        return True
    if normalized in ("false", "0", "no"):
        return False
    raise argparse.ArgumentTypeError(
        "Expected true/false, 1/0 or yes/no; received {!r}.".format(value)
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe private Fabric CI/CD API capabilities."
    )
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--expected-private-api-ip", default="")
    parser.add_argument("--perform-write-probe", type=parse_bool, default=False)
    parser.add_argument("--cleanup-canary", type=parse_bool, default=False)
    parser.add_argument(
        "--require-public-endpoint-blocked",
        type=parse_bool,
        default=True,
    )
    parser.add_argument("--expected-tenant-id", required=True)
    parser.add_argument("--expected-client-id", required=True)
    parser.add_argument(
        "--output",
        default="artifacts/fabric-private-cicd-probe.json",
    )
    return parser.parse_args()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProbeFailure(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_uuid(value: str, name: str) -> str:
    try:
        return str(uuid.UUID(value.strip()))
    except (AttributeError, ValueError) as error:
        raise ProbeFailure(
            "{} is not a valid UUID: {!r}.".format(name, value)
        ) from error


def normalize_text(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    return normalized or None


def decode_jwt_payload(token: str) -> Dict[str, Any]:
    parts = token.split(".")
    require(len(parts) >= 2, "The Fabric access token is not JWT-shaped.")
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    try:
        decoded = base64.urlsafe_b64decode(payload.encode("ascii"))
        claims = json.loads(decoded.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProbeFailure(
            "The Fabric access-token payload could not be decoded."
        ) from error
    require(isinstance(claims, dict), "Fabric token payload is not an object.")
    return claims


def command_path(name: str) -> str:
    path = shutil.which(name)
    require(path is not None, "Required executable is unavailable: {}".format(name))
    return str(path)


def obtain_fabric_token(az_path: str) -> str:
    command = [
        az_path,
        "account",
        "get-access-token",
        "--resource",
        FABRIC_RESOURCE,
        "--query",
        "accessToken",
        "--output",
        "tsv",
    ]
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    require(
        result.returncode == 0,
        "Azure CLI failed to obtain a Fabric token: {}".format(
            result.stderr.strip()
        ),
    )
    token = result.stdout.strip()
    require(bool(token), "Azure CLI returned an empty Fabric token.")
    return token


def is_rfc1918(value: str) -> bool:
    try:
        address = IPv4Address(value)
    except ValueError:
        return False
    return any(address in network for network in PRIVATE_NETWORKS)


def resolve_ipv4(hostname: str) -> List[str]:
    try:
        results = socket.getaddrinfo(
            hostname,
            443,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror:
        return []
    return sorted({result[4][0] for result in results})


def safe_json(content: str) -> Optional[Any]:
    if not content.strip():
        return None
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


class FabricClient:
    def __init__(
        self,
        token: str,
        private_host: str,
        expected_private_ip: str,
        curl_path: str,
    ) -> None:
        self._token = token
        self.private_host = private_host
        self.private_base_url = "https://{}".format(private_host)
        self.expected_private_ip = expected_private_ip
        self._curl_path = curl_path

    def request(
        self,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        use_private_route: bool = False,
    ) -> FabricResponse:
        parsed = urlparse(url)
        allowed_hosts = {PUBLIC_HOST, self.private_host}
        require(
            parsed.scheme == "https" and parsed.hostname in allowed_hosts,
            "Refusing to send a Fabric token to unexpected URL: {}".format(url),
        )
        if use_private_route:
            require(
                parsed.hostname == self.private_host,
                "Private-route request does not use the workspace hostname.",
            )

        header_file = tempfile.NamedTemporaryFile(delete=False)
        response_file = tempfile.NamedTemporaryFile(delete=False)
        header_file.close()
        response_file.close()
        request_path = None

        try:
            arguments = [
                self._curl_path,
                "--silent",
                "--show-error",
                "--connect-timeout",
                "20",
                "--max-time",
                "120",
                "--dump-header",
                header_file.name,
                "--output",
                response_file.name,
                "--write-out",
                "%{http_code}|%{remote_ip}",
                "--request",
                method,
                "--header",
                "Authorization: Bearer {}".format(self._token),
                "--header",
                "Accept: application/json",
            ]

            if use_private_route:
                arguments.extend(["--noproxy", self.private_host])
                if self.expected_private_ip:
                    arguments.extend(
                        [
                            "--resolve",
                            "{}:443:{}".format(
                                self.private_host,
                                self.expected_private_ip,
                            ),
                        ]
                    )

            if body is not None:
                request_file = tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    delete=False,
                )
                request_path = request_file.name
                json.dump(body, request_file, separators=(",", ":"))
                request_file.close()
                arguments.extend(
                    [
                        "--header",
                        "Content-Type: application/json",
                        "--data-binary",
                        "@{}".format(request_path),
                    ]
                )
            elif method in ("POST", "PATCH"):
                # Fabric's bodyless POST operations, such as getDefinition,
                # still pass through HTTP components that require an explicit
                # message length. An empty --data-binary value makes curl send
                # Content-Length: 0 instead of an unframed POST request.
                arguments.extend(
                    [
                        "--header",
                        "Content-Type: application/json",
                        "--data-binary",
                        "",
                    ]
                )

            arguments.append(url)
            result = subprocess.run(
                arguments,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            require(
                result.returncode == 0,
                "curl failed for {} {}: {}".format(
                    method,
                    parsed.path,
                    result.stderr.strip(),
                ),
            )

            metadata = result.stdout.strip().splitlines()[-1]
            match = re.fullmatch(r"(\d{3})\|(.+)", metadata)
            require(match is not None, "Unexpected curl metadata: {}".format(metadata))
            status_code = int(match.group(1))
            remote_ip = match.group(2).strip()

            response_body = Path(response_file.name).read_text(
                encoding="utf-8",
                errors="replace",
            )
            headers: Dict[str, str] = {}
            for line in Path(header_file.name).read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    headers[key.strip().lower()] = value.strip()

            if use_private_route:
                if self.expected_private_ip:
                    require(
                        remote_ip == self.expected_private_ip,
                        "Private request connected to {} instead of expected "
                        "Private Endpoint IP {}.".format(
                            remote_ip,
                            self.expected_private_ip,
                        ),
                    )
                else:
                    require(
                        is_rfc1918(remote_ip),
                        "Private request connected to non-private IP {}. Supply "
                        "--expected-private-api-ip if private DNS is not working."
                        .format(remote_ip),
                    )

            return FabricResponse(
                method=method,
                url=url,
                status_code=status_code,
                remote_ip=remote_ip,
                headers=headers,
                body=response_body,
                json_body=safe_json(response_body),
            )
        finally:
            for path in (header_file.name, response_file.name, request_path):
                if path and os.path.exists(path):
                    os.remove(path)

    def private_request(
        self,
        method: str,
        path_and_query: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> FabricResponse:
        require(path_and_query.startswith("/"), "Fabric path must start with '/'.")
        return self.request(
            method,
            "{}{}".format(self.private_base_url, path_and_query),
            body=body,
            use_private_route=True,
        )

    def private_path_from_url(self, value: str) -> str:
        parsed = urlparse(value)
        if not parsed.scheme and value.startswith("/"):
            return value
        require(
            parsed.scheme == "https"
            and parsed.hostname in {PUBLIC_HOST, self.private_host},
            "Fabric returned an unexpected continuation/LRO URL: {}".format(value),
        )
        return parsed.path + (("?" + parsed.query) if parsed.query else "")

    def complete_lro(
        self,
        initial: FabricResponse,
        get_result: bool = False,
    ) -> FabricResponse:
        if initial.status_code != 202:
            return initial

        location = initial.headers.get("location")
        require(bool(location), "Fabric returned 202 without a Location header.")
        operation_path = self.private_path_from_url(str(location))
        print("LRO returned host: {}".format(urlparse(str(location)).hostname))
        print("LRO private polling path: {}".format(operation_path))

        deadline = time.monotonic() + 600
        current = initial
        while time.monotonic() < deadline:
            retry_value = current.headers.get("retry-after", "5")
            try:
                delay = min(max(int(retry_value), 1), 30)
            except ValueError:
                delay = 5
            time.sleep(delay)

            current = self.private_request("GET", operation_path)
            assert_status(current, (200,), "LRO polling")
            payload = current.json_body if isinstance(current.json_body, dict) else {}
            state = str(payload.get("status", ""))
            print("LRO status: {}".format(state or "<missing>"))
            require(
                state not in ("Failed", "Cancelled"),
                "Fabric LRO ended with state {}: {}".format(state, current.body),
            )
            if state in ("Succeeded", "Completed"):
                if not get_result:
                    return current
                parsed = urlparse(operation_path)
                result_path = parsed.path.rstrip("/") + "/result"
                if parsed.query:
                    result_path += "?" + parsed.query
                result = self.private_request("GET", result_path)
                assert_status(result, (200, 201), "LRO result retrieval")
                return result

        raise ProbeFailure("Fabric LRO did not complete within 10 minutes.")


def assert_status(
    response: FabricResponse,
    allowed: Sequence[int],
    operation: str,
) -> None:
    require(
        response.status_code in allowed,
        "{} failed with HTTP {}: {}".format(
            operation,
            response.status_code,
            response.body,
        ),
    )


def notebook_definition(marker: str) -> Dict[str, Any]:
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Fabric private CI/CD canary\n",
                    'CANARY_VERSION = "{}"\n'.format(marker),
                    "print(CANARY_VERSION)\n",
                ],
            }
        ],
        "metadata": {"language_info": {"name": "python"}},
    }
    content = json.dumps(notebook, separators=(",", ":")).encode("utf-8")
    payload = base64.b64encode(content).decode("ascii")
    return {
        "definition": {
            "format": "ipynb",
            "parts": [
                {
                    "path": "notebook-content.ipynb",
                    "payload": payload,
                    "payloadType": "InlineBase64",
                }
            ],
        }
    }


def definition_content(response: FabricResponse) -> str:
    require(
        isinstance(response.json_body, dict),
        "Definition response is not a JSON object.",
    )
    try:
        parts = response.json_body["definition"]["parts"]
        part = next(
            item for item in parts if item.get("path") == "notebook-content.ipynb"
        )
        return base64.b64decode(part["payload"]).decode("utf-8")
    except (KeyError, StopIteration, TypeError, ValueError, UnicodeDecodeError) as error:
        raise ProbeFailure(
            "Retrieved definition does not contain a valid notebook-content.ipynb."
        ) from error


def list_notebooks(
    client: FabricClient,
    workspace_id: str,
) -> List[Dict[str, Any]]:
    path = "/v1/workspaces/{}/items?{}".format(
        workspace_id,
        urlencode({"type": "Notebook"}),
    )
    items: List[Dict[str, Any]] = []
    while path:
        response = client.private_request("GET", path)
        assert_status(response, (200,), "Private List Items")
        require(
            isinstance(response.json_body, dict),
            "List Items response is not a JSON object.",
        )
        page_items = response.json_body.get("value", [])
        require(isinstance(page_items, list), "List Items value is not an array.")
        items.extend(item for item in page_items if isinstance(item, dict))
        continuation = response.json_body.get("continuationUri")
        path = client.private_path_from_url(continuation) if continuation else ""
    return items


def write_evidence(path: str, evidence: Dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def run_probe(arguments: argparse.Namespace, evidence: Dict[str, Any]) -> None:
    workspace_id = normalize_uuid(arguments.workspace_id, "Workspace ID")
    expected_tenant_id = normalize_uuid(
        arguments.expected_tenant_id,
        "Expected tenant ID",
    )
    expected_client_id = normalize_uuid(
        arguments.expected_client_id,
        "Expected client ID",
    )

    expected_private_ip = arguments.expected_private_api_ip.strip()
    if expected_private_ip:
        try:
            parsed_ip = IPv4Address(expected_private_ip)
        except ValueError as error:
            raise ProbeFailure(
                "Expected Private Endpoint IP is invalid: {!r}.".format(
                    expected_private_ip
                )
            ) from error
        require(
            any(parsed_ip in network for network in PRIVATE_NETWORKS),
            "Expected Private Endpoint IP is not RFC1918: {}".format(parsed_ip),
        )

    workspace_key = workspace_id.replace("-", "")
    private_host = "{}.z{}.w.api.fabric.microsoft.com".format(
        workspace_key,
        workspace_key[:2],
    )
    az_path = command_path("az")
    curl_path = command_path("curl")
    token = obtain_fabric_token(az_path)

    claims = decode_jwt_payload(token)
    actual_tenant_id = normalize_text(claims.get("tid"))
    actual_client_id = normalize_text(claims.get("azp")) or normalize_text(
        claims.get("appid")
    )
    require(
        actual_tenant_id == expected_tenant_id,
        "Fabric token tenant mismatch: actual {!r}, expected {!r}.".format(
            actual_tenant_id,
            expected_tenant_id,
        ),
    )
    require(
        actual_client_id == expected_client_id,
        "Fabric token client-ID mismatch: actual {!r}, expected {!r}.".format(
            actual_client_id,
            expected_client_id,
        ),
    )

    dns_addresses = resolve_ipv4(private_host)
    print("Agent: {}".format(os.environ.get("AGENT_NAME", "<unknown>")))
    print("Python: {}".format(sys.version.split()[0]))
    print("Workspace: {}".format(workspace_id))
    print("Private API host: {}".format(private_host))
    print("Configured DNS addresses: {}".format(
        ", ".join(dns_addresses) if dns_addresses else "<not resolved>"
    ))
    if expected_private_ip:
        print("Private route override: {} -> {}".format(
            private_host,
            expected_private_ip,
        ))
    else:
        require(
            any(is_rfc1918(address) for address in dns_addresses),
            "Workspace hostname does not resolve privately and no explicit "
            "Private Endpoint IP was supplied.",
        )

    evidence.update(
        {
            "workspaceId": workspace_id,
            "privateApiHost": private_host,
            "expectedPrivateApiIp": expected_private_ip or None,
            "configuredDnsAddresses": dns_addresses,
            "agentName": os.environ.get("AGENT_NAME"),
            "pythonVersion": sys.version.split()[0],
            "identity": {
                "tenantId": actual_tenant_id,
                "clientId": actual_client_id,
                "objectId": normalize_text(claims.get("oid")),
                "tokenPersisted": False,
            },
            "writeProbeRequested": arguments.perform_write_probe,
        }
    )

    client = FabricClient(
        token=token,
        private_host=private_host,
        expected_private_ip=expected_private_ip,
        curl_path=curl_path,
    )

    print("\nGate 1: private List Items request")
    list_response = client.private_request(
        "GET",
        "/v1/workspaces/{}/items".format(workspace_id),
    )
    assert_status(list_response, (200,), "Private List Items")
    print("Private HTTP status: {}".format(list_response.status_code))
    print("Private connected IP: {}".format(list_response.remote_ip))
    evidence["privateListItems"] = {
        "statusCode": list_response.status_code,
        "remoteIp": list_response.remote_ip,
        "passed": True,
    }

    print("\nGate 2: generic public Items endpoint negative control")
    public_response = client.request(
        "GET",
        "{}/v1/workspaces/{}/items".format(PUBLIC_BASE_URL, workspace_id),
    )
    public_error_code = None
    if isinstance(public_response.json_body, dict):
        public_error_code = public_response.json_body.get("errorCode")
    public_blocked = (
        public_response.status_code == 403
        and public_error_code == "RequestDeniedByInboundPolicy"
    )
    print("Public control HTTP status: {}".format(public_response.status_code))
    print("Public control error code: {}".format(public_error_code))
    print("Public control connected IP: {}".format(public_response.remote_ip))
    evidence["publicNegativeControl"] = {
        "statusCode": public_response.status_code,
        "remoteIp": public_response.remote_ip,
        "errorCode": public_error_code,
        "blockedByInboundPolicy": public_blocked,
    }
    if arguments.require_public_endpoint_blocked:
        require(
            public_blocked,
            "Public endpoint was not blocked with RequestDeniedByInboundPolicy.",
        )

    print("\nGate 3: communication policy observation")
    policy_response = client.request(
        "GET",
        "{}/v1/workspaces/{}/networking/communicationPolicy".format(
            PUBLIC_BASE_URL,
            workspace_id,
        ),
    )
    default_action = None
    if isinstance(policy_response.json_body, dict):
        try:
            default_action = policy_response.json_body[
                "inbound"
            ]["publicAccessRules"]["defaultAction"]
        except (KeyError, TypeError):
            default_action = None
    print("Communication policy HTTP status: {}".format(
        policy_response.status_code
    ))
    if default_action:
        print("Communication policy default action: {}".format(default_action))
    evidence["communicationPolicy"] = {
        "statusCode": policy_response.status_code,
        "defaultAction": default_action,
        "informational": True,
    }

    if not arguments.perform_write_probe:
        evidence["writeProbe"] = {"performed": False}
        print("\nREAD-ONLY PRIVATE FABRIC PROBE SUCCEEDED")
        return

    print("\nGate 4: locate or create the dedicated canary Notebook")
    notebooks = list_notebooks(client, workspace_id)
    canary = next(
        (
            item
            for item in notebooks
            if item.get("displayName") == CANARY_NAME
            and item.get("type") == "Notebook"
        ),
        None,
    )
    build_id = os.environ.get("BUILD_BUILDID") or str(int(time.time()))
    marker_v1 = "private-cicd-{}-v1".format(build_id)
    marker_v2 = "private-cicd-{}-v2".format(build_id)

    if canary is None:
        create_body = {
            "displayName": CANARY_NAME,
            "type": "Notebook",
            "description": (
                "Persistent canary for private Fabric CI/CD API validation."
            ),
        }
        create_body.update(notebook_definition(marker_v1))
        create_response = client.private_request(
            "POST",
            "/v1/workspaces/{}/items".format(workspace_id),
            body=create_body,
        )
        assert_status(
            create_response,
            (201, 202),
            "Create canary Notebook",
        )
        create_result = client.complete_lro(create_response, get_result=True)
        require(
            isinstance(create_result.json_body, dict)
            and bool(create_result.json_body.get("id")),
            "Create completed without returning a canary item ID.",
        )
        canary = create_result.json_body
        print("Created canary: {}".format(canary["id"]))
    else:
        print("Using existing canary: {}".format(canary["id"]))
        initialize_response = client.private_request(
            "POST",
            "/v1/workspaces/{}/items/{}/updateDefinition".format(
                workspace_id,
                canary["id"],
            ),
            body=notebook_definition(marker_v1),
        )
        assert_status(
            initialize_response,
            (200, 202),
            "Initialize canary definition",
        )
        client.complete_lro(initialize_response)

    canary_id = str(canary["id"])

    print("\nGate 5: retrieve and validate the initial definition")
    initial_response = client.private_request(
        "POST",
        "/v1/workspaces/{}/items/{}/getDefinition?format=ipynb".format(
            workspace_id,
            canary_id,
        ),
    )
    assert_status(initial_response, (200, 202), "Get initial definition")
    initial_definition = client.complete_lro(initial_response, get_result=True)
    require(
        marker_v1 in definition_content(initial_definition),
        "Initial definition round-trip did not contain the expected marker.",
    )
    print("Initial marker validated: {}".format(marker_v1))

    print("\nGate 6: update the canary definition")
    update_response = client.private_request(
        "POST",
        "/v1/workspaces/{}/items/{}/updateDefinition".format(
            workspace_id,
            canary_id,
        ),
        body=notebook_definition(marker_v2),
    )
    assert_status(update_response, (200, 202), "Update canary definition")
    client.complete_lro(update_response)

    print("\nGate 7: retrieve and validate the updated definition")
    updated_response = client.private_request(
        "POST",
        "/v1/workspaces/{}/items/{}/getDefinition?format=ipynb".format(
            workspace_id,
            canary_id,
        ),
    )
    assert_status(updated_response, (200, 202), "Get updated definition")
    updated_definition = client.complete_lro(updated_response, get_result=True)
    require(
        marker_v2 in definition_content(updated_definition),
        "Updated definition round-trip did not contain the expected marker.",
    )
    print("Updated marker validated: {}".format(marker_v2))

    deleted = False
    if arguments.cleanup_canary:
        print("\nGate 8: soft-delete the canary")
        delete_response = client.private_request(
            "DELETE",
            "/v1/workspaces/{}/items/{}".format(workspace_id, canary_id),
        )
        assert_status(delete_response, (200, 202), "Delete canary")
        client.complete_lro(delete_response)
        deleted = True
        print("Canary soft-deleted.")
    else:
        print("\nCanary retained for reuse: {} ({})".format(
            CANARY_NAME,
            canary_id,
        ))

    evidence["writeProbe"] = {
        "performed": True,
        "canaryName": CANARY_NAME,
        "canaryId": canary_id,
        "initialMarkerValidated": True,
        "updatedMarkerValidated": True,
        "softDeleted": deleted,
    }
    print("\nPRIVATE FABRIC CI/CD WRITE PROBE SUCCEEDED")


def main() -> int:
    arguments = parse_arguments()
    evidence: Dict[str, Any] = {
        "generatedAtUtc": utc_now(),
        "result": "started",
    }
    try:
        run_probe(arguments, evidence)
        evidence["result"] = "succeeded"
        evidence["completedAtUtc"] = utc_now()
        write_evidence(arguments.output, evidence)
        print("Evidence written to: {}".format(arguments.output))
        return 0
    except ProbeFailure as error:
        evidence["result"] = "failed"
        evidence["completedAtUtc"] = utc_now()
        evidence["error"] = str(error)
        write_evidence(arguments.output, evidence)
        print(
            "FABRIC PRIVATE CI/CD PROBE FAILED: {}".format(error),
            file=sys.stderr,
        )
        print("Evidence written to: {}".format(arguments.output))
        return 1
    except Exception as error:  # Defensive conversion to pipeline failure evidence.
        evidence["result"] = "failed"
        evidence["completedAtUtc"] = utc_now()
        evidence["error"] = "Unexpected failure: {}".format(error)
        write_evidence(arguments.output, evidence)
        print(
            "FABRIC PRIVATE CI/CD PROBE FAILED: unexpected failure: {}".format(
                error
            ),
            file=sys.stderr,
        )
        print("Evidence written to: {}".format(arguments.output))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
