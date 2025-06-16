document.addEventListener("DOMContentLoaded", function() {
    var sidebarToggle = document.getElementById("sidebarToggle");
    var wrapper = document.getElementById("wrapper");
    var sidebar = document.querySelector(".sidebar");

    sidebarToggle.addEventListener("click", function() {
        sidebar.classList.toggle("toggled");
    });

    var userMenuToggle = document.getElementById("userMenuToggle");
    var userMenu = document.getElementById("userMenu");

    userMenuToggle.addEventListener("click", function() {
        userMenu.classList.toggle("show");
    });
});
