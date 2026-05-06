// Shared side menu HTML — injected into every page
function injectSideMenu() {
  const html = `
  <div class="side-menu" id="sideMenu">
    <div class="side-menu-top">
      <div class="side-menu-profile">
        <div class="side-avatar" id="menuAvatar"><i class="fa-solid fa-user"></i></div>
        <div>
          <p class="side-name" id="menuName">Traveller</p>
          <p class="side-handle" id="menuHandle">@mytripmate</p>
        </div>
      </div>
      <button class="side-close" onclick="closeMenu()"><i class="fa-solid fa-xmark"></i></button>
    </div>
    <nav class="side-nav">
      <a href="home.html"><i class="fa-solid fa-house"></i> Home</a>
      <a href="explore.html"><i class="fa-solid fa-compass"></i> Explore Trips</a>
      <a href="create-group.html"><i class="fa-solid fa-plus-circle"></i> Post a Trip</a>
      <a href="messages.html"><i class="fa-solid fa-message"></i> Messages</a>
      <a href="profile.html"><i class="fa-solid fa-user"></i> My Profile</a>
      <hr class="side-divider"/>
      <a href="index.html"><i class="fa-solid fa-right-to-bracket"></i> Log Out</a>
      <div class="side-theme-toggle">
        <span><i class="fa-solid fa-moon"></i> Light Mode</span>
        <label class="toggle-switch">
          <input type="checkbox" id="themeToggle" onchange="toggleTheme()"/>
          <span class="toggle-slider"></span>
        </label>
      </div>
    </nav>
  </div>
  <div class="menu-overlay" id="menuOverlay" onclick="closeMenu()"></div>`;
  document.body.insertAdjacentHTML('afterbegin', html);
  // populate user info
  const user = JSON.parse(sessionStorage.getItem('mtm_user') || '{}');
  if (user.name) document.getElementById('menuName').textContent = user.name;
  if (user.username) document.getElementById('menuHandle').textContent = user.username;
  if (user.avatar) document.getElementById('menuAvatar').innerHTML = `<img src="${user.avatar}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;"/>`;
}
