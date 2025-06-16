document.addEventListener("DOMContentLoaded", function () {
    var sidebarToggle = document.getElementById('sidebarToggle');
    var sidebar = document.querySelector('.sidebar');
    var contentWrapper = document.getElementById('content-wrapper');

    sidebarToggle.addEventListener('click', function () {
        sidebar.classList.toggle('toggled');
        contentWrapper.classList.toggle('toggled');
    });
});
