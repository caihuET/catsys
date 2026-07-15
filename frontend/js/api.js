// Cat_Sys API Client
const API_BASE = "/cat/api";

function getToken() {
    return localStorage.getItem("cat_sys_token");
}

function setToken(token) {
    localStorage.setItem("cat_sys_token", token);
}

function getUser() {
    const u = localStorage.getItem("cat_sys_user");
    return u ? JSON.parse(u) : null;
}

function setUser(user) {
    localStorage.setItem("cat_sys_user", JSON.stringify(user));
}

function logout() {
    localStorage.removeItem("cat_sys_token");
    localStorage.removeItem("cat_sys_user");
    window.location.href = "/";
}

async function api(path, options = {}) {
    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) headers["Authorization"] = "Bearer " + token;
    const resp = await fetch(API_BASE + path, { ...options, headers });
    return resp.json();
}

function showMsg(msg, type = "success") {
    const div = document.getElementById("msg") || document.createElement("div");
    div.id = "msg";
    div.style.cssText = "position:fixed;top:20px;right:20px;padding:12px 20px;border-radius:6px;z-index:999;font-size:14px;";
    div.style.background = type === "success" ? "#f6ffed" : "#fff2f0";
    div.style.border = type === "success" ? "1px solid #b7eb8f" : "1px solid #ffccc7";
    div.style.color = type === "success" ? "#52c41a" : "#ff4d4f";
    div.textContent = msg;
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 3000);
}
