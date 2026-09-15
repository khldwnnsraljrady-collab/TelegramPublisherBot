const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();


// =====================================================
// ELEMENTS
// =====================================================

const createPost = document.getElementById("createPost");
const postModal = document.getElementById("postModal");
const closeModal = document.getElementById("closeModal");

const postText = document.getElementById("postText");

const previewText = document.getElementById("previewText");
const previewButtons = document.getElementById("previewButtons");

const addButton = document.getElementById("addButton");
const buttonList = document.getElementById("buttonList");

const publishButton = document.getElementById("publishButton");


// =====================================================
// OPEN MODAL
// =====================================================

createPost.addEventListener("click", () => {

    postModal.classList.add("show");

    postText.focus();

});


// =====================================================
// CLOSE MODAL
// =====================================================

closeModal.addEventListener("click", () => {

    postModal.classList.remove("show");

});


// =====================================================
// UPDATE PREVIEW
// =====================================================

postText.addEventListener("input", updatePreview);


function updatePreview() {

    const text = postText.value.trim();

    previewText.textContent =
        text ||
        "اكتب النص لمشاهدة المعاينة...";


    updateButtons();

}


// =====================================================
// EXTRACT LINKS
// =====================================================

function extractLinks(text) {

    const results = [];

    const urlRegex =
        /https?:\/\/[^\s<>()]+/gi;

    const usernameRegex =
        /(^|\s)@([A-Za-z0-9_]{5,32})\b/g;


    const urls =
        text.match(urlRegex) || [];


    urls.forEach(url => {

        url = url.replace(
            /[.,!?;:)\]}]+$/,
            ""
        );

        if (!results.some(x => x.url === url)) {

            let label = "🌐 فتح الرابط";

            const lower =
                url.toLowerCase();


            if (
                lower.includes("t.me/") ||
                lower.includes("telegram.me/")
            ) {

                const parts =
                    url.split("/");

                const username =
                    parts[parts.length - 1]
                    .split("?")[0];

                label =
                    "📢 " + username;

            }

            else if (
                lower.includes("youtube.com") ||
                lower.includes("youtu.be")
            ) {

                label = "▶️ YouTube";

            }

            else if (
                lower.includes("github.com")
            ) {

                label = "💻 GitHub";

            }

            else if (
                lower.includes("instagram.com")
            ) {

                label = "📸 Instagram";

            }

            results.push({
                label,
                url
            });

        }

    });


    let match;

    while (
        (match =
            usernameRegex.exec(text)) !== null
    ) {

        const username =
            match[2];

        const url =
            `https://t.me/${username}`;

        if (
            !results.some(
                x =>
                    x.url.toLowerCase() ===
                    url.toLowerCase()
            )
        ) {

            results.push({
                label:
                    "👤 " + username,

                url
            });

        }

    }


    return results;

}


// =====================================================
// CUSTOM BUTTONS
// =====================================================

function getCustomButtons() {

    const rows =
        buttonList.querySelectorAll(
            ".custom-row"
        );

    const buttons = [];

    rows.forEach(row => {

        const inputs =
            row.querySelectorAll("input");

        const label =
            inputs[0].value.trim();

        const url =
            inputs[1].value.trim();

        if (label && url) {

            buttons.push({
                label,
                url
            });

        }

    });

    return buttons;

}


// =====================================================
// UPDATE BUTTON PREVIEW
// =====================================================

function updateButtons() {

    previewButtons.innerHTML = "";

    const text =
        postText.value;

    const automatic =
        extractLinks(text);

    const custom =
        getCustomButtons();

    const all =
        [...automatic, ...custom];


    all.forEach(button => {

        const element =
            document.createElement("div");

        element.className =
            "preview-button";

        element.textContent =
            button.label;

        previewButtons.appendChild(
            element
        );

    });

}


// =====================================================
// ADD CUSTOM BUTTON
// =====================================================

addButton.addEventListener(
    "click",
    () => {

        const row =
            document.createElement("div");

        row.className =
            "custom-row";


        const label =
            document.createElement("input");

        label.placeholder =
            "اسم الزر";


        const url =
            document.createElement("input");

        url.placeholder =
            "https://example.com";


        const remove =
            document.createElement("button");

        remove.className =
            "delete-button";

        remove.textContent =
            "×";


        remove.addEventListener(
            "click",
            () => {

                row.remove();

                updateButtons();

            }
        );


        label.addEventListener(
            "input",
            updateButtons
        );

        url.addEventListener(
            "input",
            updateButtons
        );


        row.appendChild(label);
        row.appendChild(url);
        row.appendChild(remove);

        buttonList.appendChild(row);

        label.focus();

    }
);


// =====================================================
// PUBLISH
// =====================================================

publishButton.addEventListener(
    "click",
    () => {

        const text =
            postText.value.trim();

        if (!text) {

            tg.showAlert(
                "⚠️ اكتب نص المنشور أولًا."
            );

            return;

        }


        const automatic =
            extractLinks(text);

        const custom =
            getCustomButtons();


        const payload = {

            type: "text",

            text,

            buttons: [
                ...automatic,
                ...custom
            ]

        };


        /*
         * Telegram WebApp sendData has
         * a limited payload size.
         */

        const data =
            JSON.stringify(payload);


        if (data.length > 4000) {

            tg.showAlert(
                "⚠️ المنشور كبير جدًا لإرساله من Mini App."
            );

            return;

        }


        tg.sendData(data);

        tg.close();

    }
);


// =====================================================
// TELEGRAM THEME
// =====================================================

function applyTelegramTheme() {

    const params =
        tg.themeParams || {};


    if (params.bg_color) {

        document.documentElement
            .style
            .setProperty(
                "--telegram-bg",
                params.bg_color
            );

    }

}


applyTelegramTheme();


// =====================================================
// BACK BUTTON
// =====================================================

tg.BackButton.onClick(
    () => {

        if (
            postModal.classList.contains(
                "show"
            )
        ) {

            postModal.classList.remove(
                "show"
            );

        } else {

            tg.close();

        }

    }
);
