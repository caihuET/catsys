// Shared sidebar state
function buildSidebar(pages, activeIdx) {
    const sidebar = document.getElementById("sidebar");
    if (!sidebar) return;
    let html = '<div class="logo"><span>猫</span>咖管理系统</div>';
    for (let i = 0; i < pages.length; i++) {
        const cls = i === activeIdx ? 'nav-item active' : 'nav-item';
        html += '<a href="' + pages[i][1] + '" class="' + cls + '">' + pages[i][0] + '</a>';
    }
    html += '<a href="#" onclick="doLogout()" class="nav-item" style="margin-top:20px;border-top:1px solid rgba(255,255,255,0.1);padding-top:12px;">退出登录</a>';
    sidebar.innerHTML = html;
}
function doLogout() {
    localStorage.removeItem("cat_sys_token");
    localStorage.removeItem("cat_sys_user");
    window.location.href = "/";
}
function initPage() {
    const user = getUser();
    if (!user) { window.location.href = "/"; return null; }
    const info = document.getElementById("userInfo");
    if (info) info.textContent = (user.phone || "") + " | " + new Date().toLocaleDateString();
    return user;
}
function s(v) { return v != null && v != undefined && v != "" ? v : "-"; }
function badge(status, map) {
    if (!map) map = {active:"green",available:"green",healthy:"green",interested:"blue",pending:"blue",contracted:"orange",sold:"gray",disabled:"gray",retired:"orange",lost:"red"};
    const cls = map[status] || "gray";
    return '<span class="wf-badge ' + cls + '">' + status + '</span>';
}