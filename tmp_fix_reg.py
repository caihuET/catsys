# -*- coding: utf-8 -*-
import os
path = r"E:\Project\Cat_Sys\frontend\register.html"
with open(path, "r", encoding="utf-8") as f: c = f.read()
# 1. Add validation script after <script>
val_script = """function validatePhone() {
    var phone = document.getElementById('phone').value;
    var btn = document.getElementById('codeBtn');
    var valid = /^1\\d{10}$/.test(phone);
    btn.disabled = !valid;
    btn.style.opacity = valid ? '1' : '0.4';
}
document.addEventListener('DOMContentLoaded', function() {
    validatePhone();
    document.getElementById('phone').addEventListener('input', validatePhone);
});
"""
c = c.replace("<script>", "<script>\n" + val_script)
# 2. Fix phone validation message
c = c.replace('alert("\\u8bf7\\u8f93\\u5165\\u6b63\\u786e\\u7684\\u624b\\u673a\\u53f7")', 'alert("\\u8bf7\\u8f93\\u5165\\u6b63\\u786e\\u768411\\u4f4d\\u624b\\u673a\\u53f7")')
with open(path, "w", encoding="utf-8") as f: f.write(c)
print("register.html updated")
