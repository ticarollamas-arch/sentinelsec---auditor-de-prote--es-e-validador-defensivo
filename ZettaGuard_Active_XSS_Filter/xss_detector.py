#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZettaGuard Active XSS Filter Module
Analisa strings e payloads em busca de tags maliciosas contra o OWASP Top 10.
"""

import re

XSS_PATTERNS = [
    r"<script.*?>.*?</script.*?>",
    r"javascript\s*:",
    r"onerror\s*=",
    r"onload\s*=",
    r"onclick\s*="
]

def scan_payload(payload: str) -> bool:
    """Retorna True se detectar padrões típicos de injeção XSS"""
    for pattern in XSS_PATTERNS:
        if re.search(pattern, payload, re.IGNORECASE):
            return True
    return False

if __name__ == "__main__":
    test_str = "<script>alert('AegisVortex Sandbox Exploded')</script>"
    print(f"Analisando payload: '{test_str}'")
    is_malicious = scan_payload(test_str)
    print(f"Resultado: {'⚠️ MALICIOSO' if is_malicious else '✅ SEGURO'}")
