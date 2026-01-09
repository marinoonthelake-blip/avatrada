import json
import time
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
import logging

class ExecutionFirewall:
    def __init__(self):
        self.logger = logging.getLogger("ExecutionFirewall")
        # In production, this public key would be loaded from a secure vault/env
        # For this phase, we generate a keypair on startup for demonstration
        self._private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self._private_key.public_key()

    def sign_order(self, order_payload: dict) -> bytes:
        """
        Simulates the Human Operator signing an order.
        In production, this happens on the client-side (The Cockpit).
        """
        canonical_payload = json.dumps(order_payload, sort_keys=True).encode('utf-8')
        signature = self._private_key.sign(
            canonical_payload,
            ec.ECDSA(hashes.SHA256())
        )
        return signature

    def verify_order(self, order_payload: dict, signature: bytes) -> bool:
        """
        Verifies that the order was signed by the Human Operator.
        """
        try:
            canonical_payload = json.dumps(order_payload, sort_keys=True).encode('utf-8')
            self.public_key.verify(
                signature,
                canonical_payload,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except InvalidSignature:
            self.logger.critical(f"FIREWALL BLOCK: Invalid signature for order {order_payload}")
            return False
        except Exception as e:
            self.logger.error(f"Firewall Error: {e}")
            return False

firewall = ExecutionFirewall()
