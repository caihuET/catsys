# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.shared.database import get_db_sync, engine
from src.shared.models import Base, Module

Base.metadata.create_all(bind=engine)
MODULES = [
    ("cat_mgmt", "\u732b\u54aa\u7ba1\u7406", "basic", 1),
    ("customer_mgmt", "\u5ba2\u6237\u7ba1\u7406", "basic", 2),
    ("branch_mgmt", "\u5206\u5e97\u7ba1\u7406", "basic", 3),
    ("employee_mgmt", "\u5458\u5de5\u7ba1\u7406", "basic", 4),
    ("dashboard", "\u57fa\u7840\u4eea\u8868\u76d8", "basic", 5),
    ("account", "\u8d26\u53f7\u4e0e\u6743\u9650", "basic", 6),
    ("sales", "\u9500\u552e\u7ba1\u7406", "advanced", 7),
    ("health_pro", "\u5065\u5eb7\u7ba1\u7406Pro", "advanced", 8),
    ("contract", "\u5408\u540c\u4e0e\u8bc1\u4e66", "advanced", 9),
    ("finance", "\u8d22\u52a1\u62a5\u8868", "advanced", 10),
    ("bulk_ops", "\u6279\u91cf\u5bfc\u5165\u5bfc\u51fa", "advanced", 11),
    ("api_access", "API\u63a5\u53e3", "advanced", 12),
    ("auto_followup", "\u5ba2\u6237\u81ea\u52a8\u8ddf\u8fdb", "advanced", 13),
]
db = get_db_sync()
existing = {m.code for m in db.query(Module).all()}
added = 0
for code, name, mtype, sort in MODULES:
    if code not in existing:
        db.add(Module(code=code, name=name, module_type=mtype, sort_order=sort))
        added += 1
db.commit()
print(f"Tables ready, {added} new modules inserted")
db.close()
