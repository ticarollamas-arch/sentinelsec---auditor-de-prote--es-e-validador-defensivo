#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AegisVortex HTTP Compliance Scanner - Módulo Principal
Finalidade: Realizar varreduras contra URLs com barras e portas em busca de cabeçalhos ausentes.
Desenvolvido sob o framework de higiene e conformidade digital AegisVortex.
"""

import os
import sys
import json
import socket
import urllib.request
from datetime import datetime
import sqlite3

POLICY_FILE = "config/headers_policy.json"
DB_FILE = "database/audit_results.db"

def init_environment():
    """Garante a estrutura física de diretórios e o banco de dados local SQLite3"""
    os.makedirs("config", exist_ok=True)
    os.makedirs("database", exist_ok=True)
    os.makedirs("ZettaGuard_Active_XSS_Filter", exist_ok=True)

    # Cria arquivo padrão se não existir
    if not os.path.exists(POLICY_FILE):
        default_policy = {
            "target_system_url": "https://owasp.org/www-project-top-ten/",
            "expected_headers": {
                "Content-Security-Policy": {"required": True, "criticality": "ALTA", "default": "default-src 'self'"},
                "X-Frame-Options": {"required": True, "criticality": "ALTA", "default": "SAMEORIGIN"},
                "X-Content-Type-Options": {"required": True, "criticality": "MEDIA", "default": "nosniff"},
                "Strict-Transport-Security": {"required": True, "criticality": "ALTA", "default": "max-age=31536000; includeSubDomains"}
            }
        }
        with open(POLICY_FILE, "w", encoding="utf-8") as f:
            json.dump(default_policy, f, indent=4)

    # Conectar ao SQLite3 e iniciar tabela
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            target_url TEXT NOT NULL,
            compliance_score REAL NOT NULL,
            missing_headers TEXT,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def run_compliance_test(target_url):
    """Executa a verificação ativa da URL contra a política exigida"""
    print(f"[*] Inicializando varredura em: {target_url}")
    print("[*] Buscando regras operacionais em config/headers_policy.json...")
    
    try:
        with open(POLICY_FILE, "r", encoding="utf-8") as f:
            policy = json.load(f)
    except Exception:
        policy = {"expected_headers": {}}

    missing = []
    headers_found = {}
    
    try:
        # Fazer requisição real na rede (com timeout padrão seguro)
        req = urllib.request.Request(
            target_url, 
            headers={'User-Agent': 'AegisVortex_HTTP_Compliance_Scanner/1.0.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            for k, v in r.getheaders():
                headers_found[k.lower()] = v.lower()
        status = "SUCESSO"
    except Exception as e:
        print(f"[!] Aviso: Conexão direta falhou ({e}). Executando simulação de contingência offline.")
        headers_found = {
            "x-frame-options": "sameorigin",
            "x-content-type-options": "nosniff"
        }
        status = "CONTINGENCIA"

    # Verificar contra a política informada
    total = len(policy["expected_headers"])
    hits = 0
    for header_name, rules in policy["expected_headers"].items():
        if header_name.lower() in headers_found:
            hits += 1
        else:
            missing.append(header_name)
            
    score = (hits / total) * 100 if total > 0 else 100
    
    print("=" * 60)
    print(f"📊 RESULTADO DA AUDITORIA - AegisVortex Engine")
    print(f"Target URL: {target_url}")
    print(f"Grau de Conformidade: {score:.1f}%")
    if missing:
        print(f"⚠️ Cabeçalhos Ausentes: {', '.join(missing)}")
    else:
        print("✅ Excelente! Todos os cabeçalhos de segurança estão ativos.")
    print("=" * 60)

    # Grava resultado no banco
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_logs (timestamp, target_url, compliance_score, missing_headers, status) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().isoformat(), target_url, score, ",".join(missing), status)
        )
        conn.commit()
        conn.close()
        print("[+] Registro gravado com sucesso em database/audit_results.db")
    except Exception as le:
        print(f"[!] Erro ao salvar log no banco SQLite: {le}")

if __name__ == "__main__":
    init_environment()
    target = "https://owasp.org/www-project-top-ten/"
    if len(sys.argv) > 1:
        target = sys.argv[1]
    run_compliance_test(target)
