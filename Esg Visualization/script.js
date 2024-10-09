// 获取下拉菜单元素
const identityDropdown = document.getElementById('identity');

// 监听下拉菜单选择的变化
identityDropdown.addEventListener('change', () => {
    // 获取当前选择的值
    const selectedValue = identityDropdown.value;
    // 更新页面内容
    updateReportContent(selectedValue);
});

// 更新报告内容的函数
function updateReportContent(selectedValue) {
    const summaryList = document.getElementById('summary-list');

    // 根据不同的选择更新 Summary & Suggestions 部分
    if (selectedValue === 'investor') {
        summaryList.innerHTML = `
            <li>投资建议</li>
            <li>市场分析</li>
            <li>风险管理</li>`;
    } else if (selectedValue === 'government-agency') {
        summaryList.innerHTML = `
            <li>重点关注</li>
            <li>政策影响</li>
            <li>环境与社会责任</li>`;
    } else if (selectedValue === 'business-owner') {
        summaryList.innerHTML = `
            <li>可持续性发展建议</li>
            <li>企业责任</li>
            <li>长期规划</li>`;
    }
}

// 初始化时根据默认选择更新内容
updateReportContent(identityDropdown.value);
