document.addEventListener("DOMContentLoaded", function() {
    const file = document.getElementById('file');
    const observer = new MutationObserver(function() {
        const fileLabel = file.nextSibling; // 获取文件输入框旁边的标签
        if (fileLabel && fileLabel.nodeType === Node.TEXT_NODE) {
            fileLabel.textContent = "No file chosen"; // 将文本更改为英文
        }
    });
    observer.observe(file.parentNode, { childList: true });
});
