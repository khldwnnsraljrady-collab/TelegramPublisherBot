const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

const initData = tg.initData || "";

let currentLanguage = "ar";
let channels = [];
let selectedFile = null;
let uploadedMedia = null;


/* =====================================================
   TRANSLATIONS
===================================================== */

const translations = {

    ar: {

        currentChannel: "القناة الحالية",
        selectChannel: "اختر القناة",

        createPost: "إنشاء منشور",
        createPostSub: "نص، صورة، فيديو أو ملف",

        quickActions: "الإجراءات السريعة",

        myPosts: "منشوراتي",
        scheduled: "المجدولة",
        statistics: "الإحصائيات",
        settings: "الإعدادات",

        smartLinks: "روابط ذكية",
        smartLinksSub: "اكتشاف الروابط والأزرار تلقائيًا",

        fastPublishing: "نشر سريع",
        fastPublishingSub: "انشر المحتوى إلى قنواتك بسهولة",

        secure: "آمن",
        secureSub: "كل مستخدم يرى قنواته فقط",

        newPost: "منشور جديد",
        newPostSub: "أنشئ منشورك ثم عاينه قبل النشر",

        publishTo: "النشر في",
        postText: "نص المنشور",

        media: "الوسائط والملفات",

        chooseFile: "اختيار صورة أو فيديو أو ملف",

        customButtons: "أزرار مخصصة",

        preview: "معاينة",

        cancel: "إلغاء",
        publish: "نشر الآن",

        noChannels: "لا توجد قنوات. أضف قناة أولًا.",

        uploading: "جاري رفع الملف...",
        publishing: "جاري النشر...",

        published: "تم نشر المنشور بنجاح 🚀",

        uploadFailed: "فشل رفع الملف",
        publishFailed: "فشل النشر",

        chooseChannel: "اختر قناة أولًا",

        emptyPost: "المنشور فارغ",

        addButtonText: "نص الزر",
        addButtonUrl: "الرابط",

        channelAddedBot:
            "لإضافة قناة، أضف البوت كمسؤول ثم أرسل @username إلى البوت."
    },

    en: {

        currentChannel: "Current channel",
        selectChannel: "Select channel",

        createPost: "Create Post",
        createPostSub: "Text, photo, video or file",

        quickActions: "Quick actions",

        myPosts: "My posts",
        scheduled: "Scheduled",
        statistics: "Statistics",
        settings: "Settings",

        smartLinks: "Smart Links",
        smartLinksSub: "Automatically detect links and buttons",

        fastPublishing: "Fast Publishing",
        fastPublishingSub: "Publish content to your channels",

        secure: "Secure",
        secureSub: "Each user only sees their own channels",

        newPost: "New Post",
        newPostSub: "Create and preview your post",

        publishTo: "Publish to",
        postText: "Post text",

        media: "Media & Files",

        chooseFile: "Choose photo, video or file",

        customButtons: "Custom buttons",

        preview: "Preview",

        cancel: "Cancel",
        publish: "Publish now",

        noChannels: "No channels. Add a channel first.",

        uploading: "Uploading file...",
        publishing: "Publishing...",

        published: "Post published successfully 🚀",

        uploadFailed: "File upload failed",
        publishFailed: "Publishing failed",

        chooseChannel: "Choose a channel first",

        emptyPost: "Post is empty",

        addButtonText: "Button text",
        addButtonUrl: "URL",

        channelAddedBot:
            "To add a channel, add the bot as administrator then send @username to the bot."
    }
};


function tr(key) {

    return (
        translations[currentLanguage][key]
        ||
        translations.ar[key]
        ||
        key
    );
}


/* =====================================================
   DOM
===================================================== */

const modal =
    document.getElementById("postModal");

const postsModal =
    document.getElementById("postsModal");

const channelSelect =
    document.getElementById("channelSelect");

const postChannel =
    document.getElementById("postChannel");

const postText =
    document.getElementById("postText");

const mediaInput =
    document.getElementById("mediaInput");

const fileInfo =
    document.getElementById("fileInfo");

const previewText =
    document.getElementById("previewText");

const previewMedia =
    document.getElementById("previewMedia");

const previewButtons =
    document.getElementById("previewButtons");

const buttonsContainer =
    document.getElementById("buttonsContainer");

const toast =
    document.getElementById("toast");


/* =====================================================
   APPLY LANGUAGE
===================================================== */

function applyLanguage() {

    document.documentElement.lang =
        currentLanguage;

    document.documentElement.dir =
        currentLanguage === "ar"
            ? "rtl"
            : "ltr";

    document
        .querySelectorAll("[data-i18n]")
        .forEach(element => {

            const key =
                element.dataset.i18n;

            const value =
                tr(key);

            if (value) {
                element.textContent = value;
            }

        });

    postText.placeholder =
        currentLanguage === "ar"
            ? "اكتب منشورك هنا..."
            : "Write your post here...";

}


/* =====================================================
   LOAD CHANNELS
===================================================== */

async function loadChannels() {

    try {

        const response =
            await fetch(
                "/api/channels",
                {
                    headers: {
                        "X-Telegram-Init-Data":
                            initData
                    }
                }
            );

        const data =
            await response.json();

        if (!data.ok) {

            showToast(
                "Unauthorized"
            );

            return;
        }

        channels =
            data.channels || [];

        renderChannels();

    } catch (error) {

        console.error(error);

        showToast(
            "Failed to load channels"
        );
    }
}


/* =====================================================
   RENDER CHANNELS
===================================================== */

function renderChannels() {

    channelSelect.innerHTML = "";

    postChannel.innerHTML = "";

    if (!channels.length) {

        const option =
            document.createElement("option");

        option.value = "";

        option.textContent =
            tr("noChannels");

        channelSelect.appendChild(
            option
        );

        postChannel.appendChild(
            option.cloneNode(true)
        );

        return;
    }


    channels.forEach(channel => {

        const label =
            channel.username
            ||
            channel.title
            ||
            channel.id;

        const option1 =
            document.createElement("option");

        option1.value =
            channel.id;

        option1.textContent =
            label;

        channelSelect.appendChild(
            option1
        );


        const option2 =
            option1.cloneNode(true);

        postChannel.appendChild(
            option2
        );

    });

}


/* =====================================================
   OPEN POST MODAL
===================================================== */

document
    .getElementById("createPostButton")
    .addEventListener(
        "click",
        () => {

            if (!channels.length) {

                showToast(
                    tr("noChannels")
                );

                tg.HapticFeedback
                    ?.notificationOccurred(
                        "warning"
                    );

                return;
            }

            modal.classList.add("show");

            updatePreview();

        }
    );


/* =====================================================
   CLOSE
===================================================== */

document
    .getElementById("closeModal")
    .addEventListener(
        "click",
        closePostModal
    );

document
    .getElementById("cancelButton")
    .addEventListener(
        "click",
        closePostModal
    );


function closePostModal() {

    modal.classList.remove(
        "show"
    );

}


/* =====================================================
   LANGUAGE
===================================================== */

document
    .getElementById("languageButton")
    .addEventListener(
        "click",
        () => {

            currentLanguage =
                currentLanguage === "ar"
                    ? "en"
                    : "ar";

            applyLanguage();

            tg.HapticFeedback
                ?.selectionChanged();

        }
    );


/* =====================================================
   ADD CHANNEL
===================================================== */

document
    .getElementById("addChannelButton")
    .addEventListener(
        "click",
        () => {

            tg.showAlert(
                tr("channelAddedBot")
            );

        }
    );


/* =====================================================
   TEXT PREVIEW
===================================================== */

postText.addEventListener(
    "input",
    updatePreview
);


/* =====================================================
   FILE PICKER
===================================================== */

document
    .getElementById("uploadButton")
    .addEventListener(
        "click",
        () => {

            mediaInput.click();

        }
    );


mediaInput.addEventListener(
    "change",
    async () => {

        selectedFile =
            mediaInput.files[0];

        if (!selectedFile) {
            return;
        }

        fileInfo.classList.remove(
            "hidden"
        );

        fileInfo.textContent =
            `${selectedFile.name} — ${formatBytes(selectedFile.size)}`;

        previewFile(
            selectedFile
        );

        await uploadFile();

    }
);


/* =====================================================
   PREVIEW FILE
===================================================== */

function previewFile(file) {

    previewMedia.innerHTML = "";

    previewMedia.classList.remove(
        "hidden"
    );

    if (
        file.type.startsWith(
            "image/"
        )
    ) {

        const img =
            document.createElement(
                "img"
            );

        img.src =
            URL.createObjectURL(
                file
            );

        previewMedia.appendChild(
            img
        );

    }

    else if (
        file.type.startsWith(
            "video/"
        )
    ) {

        const video =
            document.createElement(
                "video"
            );

        video.src =
            URL.createObjectURL(
                file
            );

        video.controls = true;

        previewMedia.appendChild(
            video
        );

    }

    else {

        previewMedia.textContent =
            `📎 ${file.name}`;

    }

}


/* =====================================================
   UPLOAD
===================================================== */

async function uploadFile() {

    showToast(
        tr("uploading")
    );

    const formData =
        new FormData();

    formData.append(
        "file",
        selectedFile
    );

    try {

        const response =
            await fetch(
                "/api/upload",
                {
                    method: "POST",

                    headers: {
                        "X-Telegram-Init-Data":
                            initData
                    },

                    body: formData
                }
            );

        const data =
            await response.json();

        if (!data.ok) {

            uploadedMedia =
                null;

            showToast(
                data.error
                ||
                tr("uploadFailed")
            );

            return;
        }

        uploadedMedia =
            data;

        showToast(
            "✓"
        );

    } catch (error) {

        console.error(error);

        uploadedMedia =
            null;

        showToast(
            tr("uploadFailed")
        );
    }

}


/* =====================================================
   CUSTOM BUTTONS
===================================================== */

document
    .getElementById("addButton")
    .addEventListener(
        "click",
        addCustomButton
    );


function addCustomButton(
    text = "",
    url = ""
) {

    const row =
        document.createElement(
            "div"
        );

    row.className =
        "custom-button-row";


    const textInput =
        document.createElement(
            "input"
        );

    textInput.placeholder =
        tr("addButtonText");

    textInput.value =
        text;


    const urlInput =
        document.createElement(
            "input"
        );

    urlInput.placeholder =
        tr("addButtonUrl");

    urlInput.value =
        url;


    const remove =
        document.createElement(
            "button"
        );

    remove.className =
        "remove-button";

    remove.textContent =
        "×";


    textInput.addEventListener(
        "input",
        updatePreview
    );

    urlInput.addEventListener(
        "input",
        updatePreview
    );

    remove.addEventListener(
        "click",
        () => {

            row.remove();

            updatePreview();

        }
    );


    row.appendChild(
        textInput
    );

    row.appendChild(
        urlInput
    );

    row.appendChild(
        remove
    );

    buttonsContainer.appendChild(
        row
    );

    updatePreview();

}


/* =====================================================
   GET BUTTONS
===================================================== */

function getButtons() {

    const result = [];

    const rows =
        buttonsContainer.querySelectorAll(
            ".custom-button-row"
        );

    rows.forEach(row => {

        const inputs =
            row.querySelectorAll(
                "input"
            );

        const text =
            inputs[0].value.trim();

        const url =
            inputs[1].value.trim();

        if (
            text &&
            (
                url.startsWith("https://")
                ||
                url.startsWith("http://")
                ||
                url.startsWith("tg://")
            )
        ) {

            result.push({
                text,
                url
            });

        }

    });

    return result;
}


/* =====================================================
   AUTO DETECT LINKS
===================================================== */

function detectLinks(text) {

    const buttons = [];

    if (
        !document.getElementById(
            "smartLinks"
        ).checked
    ) {

        return buttons;
    }


    const urlRegex =
        /https?:\/\/[^\s<]+/gi;

    const urls =
        text.match(
            urlRegex
        )
        || [];


    const unique =
        [...new Set(urls)];


    unique
        .slice(0, 8)
        .forEach(url => {

            buttons.push({
                text:
                    currentLanguage === "ar"
                        ? "🔗 فتح الرابط"
                        : "🔗 Open link",

                url
            });

        });


    return buttons;
}


/* =====================================================
   PREVIEW
===================================================== */

function updatePreview() {

    const text =
        postText.value.trim();

    previewText.textContent =
        text
        ||
        (
            currentLanguage === "ar"
                ? "اكتب شيئًا للمعاينة..."
                : "Write something to preview..."
        );


    previewButtons.innerHTML = "";


    const custom =
        getButtons();

    const automatic =
        detectLinks(
            text
        );


    const allButtons = [
        ...custom,
        ...automatic
    ];


    const unique = [];

    const seen = new Set();


    allButtons.forEach(button => {

        if (
            seen.has(
                button.url
            )
        ) {
            return;
        }

        seen.add(
            button.url
        );

        unique.push(
            button
        );

    });


    unique.forEach(
        button => {

            const element =
                document.createElement(
                    "div"
                );

            element.className =
                "preview-button";

            element.textContent =
                button.text;

            previewButtons.appendChild(
                element
            );

        }
    );

}


/* =====================================================
   SMART LINKS
===================================================== */

document
    .getElementById("smartLinks")
    .addEventListener(
        "change",
        updatePreview
    );


/* =====================================================
   PUBLISH
===================================================== */

document
    .getElementById("publishButton")
    .addEventListener(
        "click",
        publish
    );


async function publish() {

    const channelId =
        postChannel.value;

    const text =
        postText.value.trim();


    if (!channelId) {

        showToast(
            tr("chooseChannel")
        );

        return;
    }


    if (
        !text &&
        !uploadedMedia
    ) {

        showToast(
            tr("emptyPost")
        );

        return;
    }


    const buttons = [
        ...getButtons(),
        ...detectLinks(text)
    ];


    const uniqueButtons = [];

    const seen =
        new Set();


    buttons.forEach(
        button => {

            if (
                seen.has(
                    button.url
                )
            ) {
                return;
            }

            seen.add(
                button.url
            );

            uniqueButtons.push(
                button
            );

        }
    );


    const payload = {

        channel_id:
            channelId,

        text,

        media_type:
            uploadedMedia
                ? uploadedMedia.media_type
                : null,

        media_path:
            uploadedMedia
                ? uploadedMedia.path
                : null,

        buttons:
            uniqueButtons

    };


    const publishButton =
        document.getElementById(
            "publishButton"
        );


    publishButton.disabled =
        true;

    publishButton.innerHTML =
        `⏳ ${tr("publishing")}`;


    try {

        const response =
            await fetch(
                "/api/publish",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "X-Telegram-Init-Data":
                            initData
                    },

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        const data =
            await response.json();


        if (!data.ok) {

            showToast(
                data.error
                ||
                tr("publishFailed")
            );

            return;
        }


        tg.HapticFeedback
            ?.notificationOccurred(
                "success"
            );


        showToast(
            tr("published")
        );


        resetPost();

        closePostModal();


    } catch (error) {

        console.error(error);

        showToast(
            tr("publishFailed")
        );

    } finally {

        publishButton.disabled =
            false;

        publishButton.innerHTML =
            `🚀 <span>${tr("publish")}</span>`;

    }

}


/* =====================================================
   RESET
===================================================== */

function resetPost() {

    postText.value = "";

    mediaInput.value = "";

    selectedFile =
        null;

    uploadedMedia =
        null;

    fileInfo.classList.add(
        "hidden"
    );

    previewMedia.innerHTML = "";

    previewMedia.classList.add(
        "hidden"
    );

    buttonsContainer.innerHTML =
        "";

    updatePreview();

}


/* =====================================================
   POSTS
===================================================== */

document
    .getElementById("postsButton")
    .addEventListener(
        "click",
        loadPosts
    );


document
    .getElementById("closePostsModal")
    .addEventListener(
        "click",
        () => {

            postsModal.classList.remove(
                "show"
            );

        }
    );


async function loadPosts() {

    try {

        const response =
            await fetch(
                "/api/posts",
                {
                    headers: {
                        "X-Telegram-Init-Data":
                            initData
                    }
                }
            );


        const data =
            await response.json();


        if (!data.ok) {
            return;
        }


        const list =
            document.getElementById(
                "postsList"
            );


        list.innerHTML = "";


        if (!data.posts.length) {

            list.innerHTML =
                `<div class="post-item">
                    ${tr("noPosts")}
                 </div>`;

        }


        data.posts.forEach(
            post => {

                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "post-item";


                const title =
                    document.createElement(
                        "strong"
                    );

                title.textContent =
                    `#${post.id} · ${post.media_type || "text"}`;


                const content =
                    document.createElement(
                        "p"
                    );

                content.textContent =
                    post.text
                    ||
                    "📎 Media post";


                item.appendChild(
                    title
                );

                item.appendChild(
                    content
                );

                list.appendChild(
                    item
                );

            }
        );


        postsModal.classList.add(
            "show"
        );


    } catch (error) {

        console.error(error);

    }

}


/* =====================================================
   TOAST
===================================================== */

let toastTimer = null;


function showToast(message) {

    toast.textContent =
        message;

    toast.classList.add(
        "show"
    );


    clearTimeout(
        toastTimer
    );


    toastTimer =
        setTimeout(
            () => {

                toast.classList.remove(
                    "show"
                );

            },
            2500
        );

}


/* =====================================================
   FORMAT SIZE
===================================================== */

function formatBytes(bytes) {

    if (!bytes) {
        return "0 B";
    }

    const units = [
        "B",
        "KB",
        "MB",
        "GB"
    ];

    const index =
        Math.floor(
            Math.log(bytes) /
            Math.log(1024)
        );

    return (
        (bytes /
            Math.pow(
                1024,
                index
            )
        ).toFixed(1)
        +
        " "
        +
        units[index]
    );

}


/* =====================================================
   INIT
===================================================== */

applyLanguage();

loadChannels();

updatePreview();
