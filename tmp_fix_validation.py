# -*- coding: utf-8 -*-
import os
path = r"E:\Project\Cat_Sys\frontend\register.html"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 改进的手机号验证 - 带视觉反馈
new_validate = """function validatePhone() {
    var inp = document.getElementById('phone');
    var btn = document.getElementById('codeBtn');
    var v = inp.value.trim();
    var valid = /^1[3-9]\\d{9}$/.test(v);
    var el = document.getElementById('phoneStatus');
    if (!el) {
        el = document.createElement('span');
        el.id = 'phoneStatus';
        el.style.cssText = 'position:absolute;right:10px;top:50%;transform:translateY(-50%);font-size:16px;font-weight:bold;';
        inp.parentNode.style.position = 'relative';
        inp.parentNode.appendChild(el);
    }
    if (v.length === 0) {
        inp.style.borderColor = '#d9d9d9';
        el.textContent = '';
        btn.disabled = true;
    } else if (valid) {
        inp.style.borderColor = '#52c41a';
        el.textContent = '\\u2713';
        el.style.color = '#52c41a';
        btn.disabled = false;
    } else {
        inp.style.borderColor = '#ff4d4f';
        el.textContent = '\\u2717';
        el.style.color = '#ff4d4f';
        btn.disabled = true;
    }
    btn.style.opacity = btn.disabled ? '0.4' : '1';
    btn.style.cursor = btn.disabled ? 'not-allowed' : 'pointer';
}
document.addEventListener('DOMContentLoaded', function() {
    var inp = document.getElementById('phone');
    validatePhone();
    inp.addEventListener('input', validatePhone);
    inp.addEventListener('blur', function() {
        if (inp.value.trim().length > 0 && !/^1[3-9]\\d{9}$/.test(inp.value.trim())) {
            inp.style.borderColor = '#ff4d4f';
        }
    });
});"""

# Replace the old validation
old_start = "function validatePhone() {"
old_end = "});"
old_idx = c.index(old_start)
end_idx = c.index(old_end, old_idx) + len(old_end)
old_block = c[old_idx:end_idx]
c = c.replace(old_block, new_validate)

# Update getCode phone check
c = c.replace('if (!phone || phone.length < 11) { alert("\\u8bf7\\u8f93\\u5165\\u6b63\\u786e\\u7684\\u624b\\u673a\\u53f7"); return; }',
    'if (!phone || !/^1[3-9]\\d{9}$/.test(phone.trim())) { alert("\\u8bf7\\u8f93\\u5165\\u6b63\\u786e\\u7684\\u4e2d\\u56fd\\u5927\\u9646\\u624b\\u673a\\u53f7"); return; }')

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("register.html validation updated")
print("Done")
