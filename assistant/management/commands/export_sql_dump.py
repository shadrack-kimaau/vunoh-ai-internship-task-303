from __future__ import annotations

import os
import sqlite3

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Export a SQLite SQL dump including schema + data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="sql_dump.sql",
            help="Output path relative to project root (default: sql_dump.sql).",
        )

    def handle(self, *args, **options):
        db = settings.DATABASES.get("default") or {}
        if db.get("ENGINE") != "django.db.backends.sqlite3":
            raise CommandError("export_sql_dump currently supports SQLite only.")

        db_path = db.get("NAME")
        if not db_path:
            raise CommandError("SQLite database path not configured.")

        output_rel = str(options["output"])
        base_dir = str(settings.BASE_DIR)
        output_path = os.path.join(base_dir, output_rel)

        con = sqlite3.connect(db_path)
        try:
            dump_lines = list(con.iterdump())
        finally:
            con.close()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("-- Vunoh AI Internship Practical Test SQL dump\n")
            f.write("-- Generated via `python manage.py export_sql_dump`\n\n")
            for line in dump_lines:
                f.write(line)
                if not line.endswith("\n"):
                    f.write("\n")

        self.stdout.write(self.style.SUCCESS(f"Wrote SQL dump to {output_path}"))

