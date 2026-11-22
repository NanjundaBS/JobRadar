#!/usr/bin/env python3
"""
Seed the Company table from backend/data/companies.json.
Run this script after database initialization.

Usage:
  python scripts/seed_companies.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Ensure root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))


async def main():
    from backend.database import AsyncSessionLocal, init_db
    from backend.models import Company
    from sqlalchemy import select

    companies_file = root_dir / "backend" / "data" / "companies.json"
    if not companies_file.exists():
        print(f"Error: {companies_file} not found.")
        return

    with open(companies_file, "r", encoding="utf-8") as f:
        companies_data = json.load(f)

    print("Initializing DB tables if not present...")
    await init_db()

    async with AsyncSessionLocal() as db:
        added = 0
        skipped = 0
        for item in companies_data:
            name = item.get("name")
            if not name:
                continue
            existing = await db.execute(select(Company).where(Company.name == name))
            if existing.scalar_one_or_none():
                skipped += 1
                continue

            company = Company(
                name=name,
                type=item.get("type", "Unknown"),
                career_url=item.get("career_url"),
            )
            db.add(company)
            added += 1

        await db.commit()
        print(f"✅ Seeding complete: {added} companies added, {skipped} already existed.")


if __name__ == "__main__":
    asyncio.run(main())
