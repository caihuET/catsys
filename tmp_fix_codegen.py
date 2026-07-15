# -*- coding: utf-8 -*-
import os
path = r"E:\Project\Cat_Sys\services\user-service\app\service\sms.py"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Insert local code generation before try
c = c.replace(
    'def send_sms(phone: str) -> dict:',
    'def send_sms(phone: str) -> dict:\n    import random\n    code = "".join(str(random.randint(0, 9)) for _ in range(6))\n    store_code(phone, code)'
)

# 2. Replace template_param to use local code instead of ##code##
c = c.replace('"##code##"', 'code')

# 3. Remove verify_code extraction
c = c.replace("            sms_code = body.model.verify_code\n            store_code(phone, sms_code)\n            ", "            ")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("sms.py updated")
print("Done")
