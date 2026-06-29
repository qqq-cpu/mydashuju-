# -*- coding: utf-8 -*-
"""Unified ClickHouse client: native (9000) or HTTP (8123, Aliyun public)."""
from config_loader import load_config


def _split_sql(sql: str):
    parts = []
    buf = []
    for line in sql.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        buf.append(line)
        if stripped.endswith(";"):
            parts.append("\n".join(buf))
            buf = []
    if buf:
        parts.append("\n".join(buf))
    return parts


class CKClient:
    def __init__(self, cfg):
        self.cfg = cfg
        self.mode = "native"
        port = int(cfg.get("port", 9000))
        if port == 8123:
            import clickhouse_connect
            self.mode = "http"
            self.client = clickhouse_connect.get_client(
                host=cfg["host"],
                port=8123,
                username=cfg["user"],
                password=cfg["password"],
                database=cfg["database"],
                connect_timeout=30,
            )
        else:
            from clickhouse_driver import Client
            self.client = Client(
                host=cfg["host"],
                port=port,
                user=cfg["user"],
                password=cfg["password"],
                database=cfg["database"],
                connect_timeout=30,
                send_receive_timeout=300,
            )

    def execute(self, sql, params=None):
        if self.mode == "http":
            if params:
                for k, v in params.items():
                    sql = sql.replace(f"%({k})s", repr(v) if isinstance(v, str) else str(v))
            self.client.command(sql)
        else:
            self.client.execute(sql, params or {})

    def execute_many(self, sql: str):
        for stmt in _split_sql(sql):
            self.execute(stmt)

    def query(self, sql):
        if self.mode == "http":
            return self.client.query(sql).result_rows
        return self.client.execute(sql)

    def insert_rows(self, table, rows, columns):
        if self.mode == "http":
            self.client.insert(table, rows, column_names=columns)
        else:
            cols = ", ".join(columns)
            self.client.execute(
                f"INSERT INTO {table} ({cols}) VALUES",
                rows,
            )


def get_ck_client():
    cfg = load_config()["clickhouse"]
    return CKClient(cfg)
