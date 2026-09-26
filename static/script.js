// =========================================================
// MY DAY ANALYZER
// PROFESSIONAL THEME SYSTEM
// =========================================================


// =========================================================
// AVAILABLE THEMES
// =========================================================

const themes = [

    {
        id: "light",
        name: "☀️ Original Light",
        description: "Clean & professional",
        preview: "preview-light"
    },

    {
        id: "dark",
        name: "🌙 Original Dark",
        description: "Simple dark mode",
        preview: "preview-dark"
    },

    {
        id: "forest",
        name: "🌿 Forest Calm",
        description: "Peaceful nature",
        preview: "preview-forest"
    },

    {
        id: "sakura",
        name: "🌸 Sakura",
        description: "Soft & elegant",
        preview: "preview-sakura"
    },

    {
        id: "cozy",
        name: "🧸 Cute Cozy",
        description: "Warm & cute",
        preview: "preview-cozy"
    },

    {
        id: "ocean",
        name: "🌊 Ocean Breeze",
        description: "Fresh & relaxing",
        preview: "preview-ocean"
    },

    {
        id: "galaxy",
        name: "🌌 Midnight Galaxy",
        description: "Dark & dreamy",
        preview: "preview-galaxy"
    },

    {
        id: "cloud",
        name: "☁️ Cloud Dream",
        description: "Soft & dreamy",
        preview: "preview-cloud"
    },

    {
        id: "matcha",
        name: "🍵 Matcha",
        description: "Calm & minimal",
        preview: "preview-matcha"
    },

    {
        id: "sunset",
        name: "🌅 Sunset",
        description: "Warm & energetic",
        preview: "preview-sunset"
    },

    {
        id: "noir",
        name: "🖤 Elegant Noir",
        description: "Luxury & elegant",
        preview: "preview-noir"
    },

    {
        id: "lavender",
        name: "💜 Lavender Dream",
        description: "Soft & peaceful",
        preview: "preview-lavender"
    }

];


// =========================================================
// CREATE THEME PANEL
// =========================================================

function createThemePanel() {

    // Don't create twice
    if (document.querySelector(".theme-panel")) {
        return;
    }


    const panel =
        document.createElement("div");

    panel.className =
        "theme-panel";


    panel.innerHTML = `

        <div class="theme-panel-header">

            <div>

                <h3>🎨 Choose Your Theme</h3>

                <p>
                    Make your productivity space yours.
                </p>

            </div>

            <button
                class="close-theme"
                onclick="closeThemePanel()"
            >
                ✕
            </button>

        </div>


        <div class="theme-grid">

            ${themes.map(theme => `

                <button
                    class="theme-option"
                    data-theme-option="${theme.id}"
                    onclick="selectTheme('${theme.id}')"
                >

                    <div
                        class="theme-preview ${theme.preview}"
                    ></div>

                    <div class="theme-name">
                        ${theme.name}
                    </div>

                    <div class="theme-description">
                        ${theme.description}
                    </div>

                </button>

            `).join("")}

        </div>

    `;


    document.body.appendChild(panel);

}


// =========================================================
// OPEN THEME PANEL
// =========================================================

function openThemePanel() {

    createThemePanel();


    const panel =
        document.querySelector(".theme-panel");


    panel.classList.add("show");


    updateActiveTheme();

}


// =========================================================
// CLOSE THEME PANEL
// =========================================================

function closeThemePanel() {

    const panel =
        document.querySelector(".theme-panel");


    if (panel) {

        panel.classList.remove("show");

    }

}


// =========================================================
// SELECT THEME
// =========================================================

function selectTheme(theme) {

    // Remove old theme
    document.body.removeAttribute(
        "data-theme"
    );


    // Remove dark class
    document.body.classList.remove(
        "dark"
    );


    // Original light
    if (theme === "light") {

        document.body.removeAttribute(
            "data-theme"
        );

    }


    // Original dark
    else if (theme === "dark") {

        document.body.classList.add(
            "dark"
        );

    }


    // All custom themes
    else {

        document.body.setAttribute(
            "data-theme",
            theme
        );

    }


    // Save theme
    localStorage.setItem(
        "appTheme",
        theme
    );


    updateActiveTheme();


    updateThemeButton();


    // Small delay before closing
    setTimeout(
        closeThemePanel,
        250
    );

}


// =========================================================
// APPLY SAVED THEME
// =========================================================

function applySavedTheme() {

    const savedTheme =
        localStorage.getItem(
            "appTheme"
        );


    // Default
    if (!savedTheme) {

        selectThemeWithoutAnimation(
            "light"
        );

        return;

    }


    selectThemeWithoutAnimation(
        savedTheme
    );

}


// =========================================================
// APPLY WITHOUT CLOSING PANEL
// =========================================================

function selectThemeWithoutAnimation(theme) {

    document.body.removeAttribute(
        "data-theme"
    );

    document.body.classList.remove(
        "dark"
    );


    if (theme === "dark") {

        document.body.classList.add(
            "dark"
        );

    }

    else if (theme !== "light") {

        document.body.setAttribute(
            "data-theme",
            theme
        );

    }


    updateThemeButton();

}


// =========================================================
// UPDATE ACTIVE THEME
// =========================================================

function updateActiveTheme() {

    const currentTheme =
        localStorage.getItem(
            "appTheme"
        ) || "light";


    document
        .querySelectorAll(
            ".theme-option"
        )
        .forEach(button => {

            const theme =
                button.getAttribute(
                    "data-theme-option"
                );


            if (theme === currentTheme) {

                button.classList.add(
                    "active"
                );

            } else {

                button.classList.remove(
                    "active"
                );

            }

        });

}


// =========================================================
// UPDATE THEME BUTTON
// =========================================================

function updateThemeButton() {

    const buttons =
        document.querySelectorAll(
            ".theme-button"
        );


    const currentTheme =
        localStorage.getItem(
            "appTheme"
        ) || "light";


    buttons.forEach(button => {

        if (
            currentTheme === "dark" ||
            currentTheme === "galaxy" ||
            currentTheme === "noir"
        ) {

            button.textContent =
                "☀️";

        } else {

            button.textContent =
                "🎨";

        }


        button.title =
            "Change Theme";

    });

}


// =========================================================
// CREATE THEME BUTTON
// =========================================================

function addThemeButton() {

    const navButtons =
        document.querySelector(
            ".nav-buttons"
        );


    if (!navButtons) {
        return;
    }


    // Don't create twice
    if (
        navButtons.querySelector(
            ".theme-selector-button"
        )
    ) {

        return;

    }


    const button =
        document.createElement("button");


    button.className =
        "theme-button theme-selector-button";


    button.type =
        "button";


    button.textContent =
        "🎨";


    button.title =
        "Change Theme";


    button.onclick =
        function(event) {

            event.stopPropagation();

            const panel =
                document.querySelector(
                    ".theme-panel"
                );


            if (
                panel &&
                panel.classList.contains(
                    "show"
                )
            ) {

                closeThemePanel();

            } else {

                openThemePanel();

            }

        };


    navButtons.appendChild(
        button
    );

}


// =========================================================
// MOBILE THEME BUTTON
// =========================================================

function setupMobileThemeButton() {

    const mobileButton =
        document.querySelector(
            ".mobile-nav button"
        );


    if (!mobileButton) {
        return;
    }


    mobileButton.innerHTML =
        `
            🎨
            <span>Theme</span>
        `;


    mobileButton.onclick =
        function(event) {

            event.stopPropagation();

            const panel =
                document.querySelector(
                    ".theme-panel"
                );


            if (
                panel &&
                panel.classList.contains(
                    "show"
                )
            ) {

                closeThemePanel();

            } else {

                openThemePanel();

            }

        };

}


// =========================================================
// CLOSE PANEL WHEN CLICKING OUTSIDE
// =========================================================

document.addEventListener(
    "click",
    function(event) {

        const panel =
            document.querySelector(
                ".theme-panel"
            );


        if (!panel) {
            return;
        }


        const themeButton =
            document.querySelector(
                ".theme-selector-button"
            );


        const mobileButton =
            document.querySelector(
                ".mobile-nav button"
            );


        if (
            !panel.contains(event.target) &&
            event.target !== themeButton &&
            event.target !== mobileButton
        ) {

            closeThemePanel();

        }

    }
);


// =========================================================
// END DATE VALIDATION
// =========================================================

function setupDateValidation() {

    const startDate =
        document.querySelector(
            'input[name="start_date"]'
        );


    const endDate =
        document.querySelector(
            'input[name="end_date"]'
        );


    if (
        startDate &&
        endDate
    ) {

        function updateEndDate() {

            if (startDate.value) {

                endDate.min =
                    startDate.value;

            }

        }


        startDate.addEventListener(
            "change",
            updateEndDate
        );


        updateEndDate();

    }

}


// =========================================================
// INITIALIZE APPLICATION
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        applySavedTheme();

        addThemeButton();

        setupMobileThemeButton();

        setupDateValidation();

    }
);