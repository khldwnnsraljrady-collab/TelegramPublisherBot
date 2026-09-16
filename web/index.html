/* =====================================================
   TELEGRAM WEB APP INIT
===================================================== */

const tg = window.Telegram?.WebApp;

if (tg) {
    tg.ready();
    tg.expand();
}

const initData = tg?.initData || "";


/* =====================================================
   STATE
===================================================== */

let currentLanguage = "ar";
let channels = [];
let selectedFile = null;
let uploadedMedia = null;
let toastTimer = null;


/* =====================================================
   TRANSLATIONS
===================================================== */

const translations = {

    ar: {

        /* Header / Welcome */
        controlCenter: "✨ مركز التحكم",
        welcomeTitle: "أهلاً بك 👋",
        welcomeDescription:
            "أنشئ منشوراتك وانشرها لقنواتك بطريقة سريعة واحترافية.",

        /* Channels */
        yourChannels: "قنواتك",
        currentChannel: "القناة الحالية",
        connected: "متصل",
        noChannels: "لا توجد قنوات. أضف قناة أولًا.",

        /* Create Post */
        createPost: "إنشاء منشور",
        createPostSub: "ابدأ منشورًا جديدًا",

        /* Quick actions */
        quickActions: "إجراءات سريعة",
        myPosts: "منشوراتي",
        myPostsSub: "المحفوظة",
        scheduled: "المجدولة",
        scheduledSub: "قيد الانتظار",
        statistics: "الإحصائيات",
        statisticsSub: "أداء القناة",
        settings: "الإعدادات",
        settingsSub: "تخصيص النظام",

        /* Features */
        smartLinksDescription: "اكتشاف الروابط تلقائيًا",
        fastPublishingDescription: "نشر سريع وآمن",
        secureDescription: "كل مستخدم يدير قنواته فقط",
        crafted: "صُنع من أجل تليجرام",

        /* Modal — Create Post */
        create: "إنشاء",
        newPost: "✨ منشور جديد",
        publishTo: "نشر إلى",
        addMedia: "إضافة صورة أو ملف",
        mediaDescription: "صورة، فيديو، ملف، صوت أو GIF",
        postText: "نص المنشور",
        postTextPlaceholder: "اكتب محتوى المنشور هنا...",
        smartLinksHelp:
            "سيتم اكتشاف الروابط تلقائيًا وتحويلها إلى أزرار.",
        buttons: "🔘 الأزرار",
        addButtonText: "نص الزر",
        addButtonUrl: "الرابط",
        preview: "👀 المعاينة",
        previewPlaceholder: "اكتب النص لمشاهدة المعاينة...",
        cancel: "إلغاء",
        publish: "نشر المنشور",

        /* Modal — Add Channel */
        channel: "قناة",
        addNewChannel: "📢 إضافة قناة",
        channelStep1: "أضف البوت إلى قناتك كمسؤول.",
        channelStep2: "امنحه صلاحية نشر الرسائل.",
        channelStep3:
            "أدخل اسم مستخدم القناة مثل: @KhaldounSoft",
        channelUsername: "اسم مستخدم القناة",
        verifyChannel: "التحقق من القناة",

        /* Posts modal */
        posts: "المنشورات",
        noPosts: "لا توجد منشورات بعد.",

        /* Messages */
        uploading: "جاري رفع الملف...",
        publishing: "جاري النشر...",
        published: "تم نشر المنشور بنجاح 🚀",
        uploadFailed: "فشل رفع الملف",
        publishFailed: "فشل النشر",
        chooseChannel: "اختر قناة أولًا",
        emptyPost: "المنشور فارغ",
        unauthorized: "غير مصرح",
        loadChannelsFailed: "فشل تحميل القنوات",
        verifyChannelSuccess: "✅ تمت إضافة القناة بنجاح",
        openLink: "🔗 فتح الرابط",

        /* Add channel instructions */
        channelAddedBot:
            "أضف البوت كمسؤول في القناة، ثم أدخل @username هنا."
    },

    en: {

        /* Header / Welcome */
        controlCenter: "✨ CONTROL CENTER",
        welcomeTitle: "Welcome 👋",
        welcomeDescription:
            "Create and publish your posts to your channels quickly and professionally.",

        /* Channels */
        yourChannels: "Your Channels",
        currentChannel: "Current Channel",
        connected: "Connected",
        noChannels: "No channels. Add one first.",

        /* Create Post */
        createPost: "Create Post",
        createPostSub: "Start a new post",

        /* Quick actions */
        quickActions: "Quick Actions",
        myPosts: "My Posts",
        myPostsSub: "Saved",
        scheduled: "Scheduled",
        scheduledSub: "Waiting",
        statistics: "Statistics",
        statisticsSub: "Channel performance",
        settings: "Settings",
        settingsSub: "Customize",

        /* Features */
        smartLinksDescription: "Auto-detect links",
        fastPublishingDescription: "Fast & secure publishing",
        secureDescription: "Each user sees only their channels",
        crafted: "Crafted for Telegram",

        /* Modal — Create Post */
        create: "CREATE",
        newPost: "✨ New Post",
        publishTo: "Publish to",
        addMedia: "Add photo or file",
        mediaDescription: "Photo, video, file, audio or GIF",
        postText: "Post text",
        postTextPlaceholder: "Write your post here...",
        smartLinksHelp:
            "Links will be auto-detected and turned into buttons.",
        buttons: "🔘 Buttons",
        addButtonText: "Button text",
        addButtonUrl: "URL",
        preview: "👀 Preview",
        previewPlaceholder: "Write something to preview...",
        cancel: "Cancel",
        publish: "Publish post",

        /* Modal — Add Channel */
        channel: "CHANNEL",
        addNewChannel: "📢 Add Channel",
        channelStep1: "Add the bot to your channel as admin.",
        channelStep2: "Give it permission to post messages.",
        channelStep3: "Enter the channel username like: @KhaldounSoft",
        channelUsername: "Channel username",
        verifyChannel: "Verify channel",

        /* Posts modal */
        posts: "POSTS",
        noPosts: "No posts yet.",

        /* Messages */
        uploading: "Uploading file...",
        publishing: "Publishing...",
        published: "Post published successfully 🚀",
        uploadFailed: "File upload failed",
        publishFailed: "Publishing failed",
        chooseChannel: "Choose a channel first",
        emptyPost: "Post is empty",
        unauthorized: "Unauthorized",
        loadChannelsFailed: "Failed to load channels",
        verifyChannelSuccess: "✅ Channel added successfully",
        openLink: "🔗 Open link",

        /* Add channel instructions */
        channelAddedBot:
            "Add the bot as admin in the channel, then enter @username here."
    }
};


/* =====================================================
   TRANSLATE HELPER
===================================================== */

function tr(key) {

    return (
        translations[currentLanguage]?.[key]
        ||
        translations.ar[key]
        ||
        key
    );
}


/* =====================================================
   DOM REFS
===================================================== */

const postModal =
    document.getElementById("postModal");

const postsModal =
    document.getElementById("postsModal");

const channelModal =
    document.getElementById("channelModal");

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

const characterCount =
    document.getElementById("characterCount");

const previewText =
    document.getElementById("previewText");

const previewMedia =
    document.getElementById("previewMedia");

const previewButtons =
    document.getElementById("previewButtons");

const buttonsContainer =
    document.getElementById("buttonsContainer");

const smartLinksCheckbox =
    document.getElementById("smartLinks");

const toast =
    document.getElementById("toast");

const toastMessage =
    document.getElementById("toastMessage");

const toastIcon =
    document.getElementById("toastIcon");

const channelMessage =
    document.getElementById("channelMessage");

const channelUsername =
    document.getElementById("channelUsername");

const postsList =
    document.getElementById("postsList");


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

    if (postText) {
        postText.placeholder =
            tr("postTextPlaceholder");
    }

    if (previewText) {
        updatePreview();
    }

    if (channelUsername) {
        channelUsername.placeholder =
            "@KhaldounSoft";
    }

}


/* =====================================================
   HAPTIC
===================================================== */

function haptic(type = "selection") {

    try {

        if (!tg?.HapticFeedback) return;

        if (type === "success") {
            tg.HapticFeedback.notificationOccurred("success");
        } else if (type === "warning") {
            tg.HapticFeedback.notificationOccurred("warning");
        } else if (type === "error") {
            tg.HapticFeedback.notificationOccurred("error");
        } else {
            tg.HapticFeedback.selectionChanged();
        }

    } catch (e) {
        /* silent */
    }

}


/* =====================================================
   TOAST
===================================================== */

function showToast(message, icon = "✓") {

    if (!toast) return;

    toastMessage.textContent = message;
    toastIcon.textContent = icon;

    toast.classList.add("show");

    clearTimeout(toastTimer);

    toastTimer = setTimeout(
        () => toast.classList.remove("show"),
        2500
    );

}


/* =====================================================
   FORMAT BYTES
===================================================== */

function formatBytes(bytes) {

    if (!bytes) return "0 B";

    const units = ["B", "KB", "MB", "GB"];

    const index = Math.min(
        Math.floor(Math.log(bytes) / Math.log(1024)),
        units.length - 1
    );

    return (
        (bytes / Math.pow(1024, index)).toFixed(1)
        + " "
        + units[index]
    );

}


/* =====================================================
   API HELPER
===================================================== */

async function apiFetch(url, options = {}) {

    const headers = {
        "X-Telegram-Init-Data": initData,
        ...(options.headers || {})
    };

    return fetch(url, {
        ...options,
        headers
    });

}


/* =====================================================
   LOAD CHANNELS
===================================================== */

async function loadChannels() {

    try {

        const response = await apiFetch("/api/channels");

        const data = await response.json();

        if (!data.ok) {

            showToast(
                data.error || tr("unauthorized"),
                "⚠"
            );

            return;
        }

        channels = data.channels || [];

        renderChannels();

    } catch (error) {

        console.error(error);

        showToast(tr("loadChannelsFailed"), "⚠");

    }

}


/* =====================================================
   RENDER CHANNELS
===================================================== */

function renderChannels() {

    if (channelSelect) {
        channelSelect.innerHTML = "";
    }

    if (postChannel) {
        postChannel.innerHTML = "";
    }

    if (!channels.length) {

        const option =
            document.createElement("option");

        option.value = "";
        option.textContent = tr("noChannels");

        channelSelect?.appendChild(
            option
        );

        postChannel?.appendChild(
            option.cloneNode(true)
        );

        return;
    }


    channels.forEach(channel => {

        const label =
            channel.username
            || channel.title
            || channel.id;

        /* Channel select (top of page) */

        const opt1 =
            document.createElement("option");

        opt1.value = channel.id;
        opt1.textContent = label;

        channelSelect?.appendChild(opt1);

        /* Post channel (modal) */

        const opt2 =
            document.createElement("option");

        opt2.value = channel.id;
        opt2.textContent = label;

        postChannel?.appendChild(opt2);

    });

}


/* =====================================================
   OPEN POST MODAL
===================================================== */

document
    .getElementById("createPostButton")
    ?.addEventListener("click", () => {

        if (!channels.length) {

            showToast(tr("noChannels"), "⚠");

            haptic("warning");

            return;

        }

        postModal.classList.add("show");

        updatePreview();

        haptic();

    });


/* =====================================================
   CLOSE POST MODAL
===================================================== */

function closePostModal() {

    postModal?.classList.remove("show");

}

document
    .getElementById("closeModal")
    ?.addEventListener("click", closePostModal);

document
    .getElementById("cancelButton")
    ?.addEventListener("click", closePostModal);

document
    .getElementById("modalOverlay")
    ?.addEventListener("click", closePostModal);


/* =====================================================
   LANGUAGE TOGGLE
===================================================== */

document
    .getElementById("languageButton")
    ?.addEventListener("click", () => {

        currentLanguage =
            currentLanguage === "ar"
                ? "en"
                : "ar";

        applyLanguage();

        renderChannels();

        haptic();

    });


/* =====================================================
   ADD CHANNEL MODAL
===================================================== */

function openChannelModal() {

    if (channelMessage) {
        channelMessage.textContent = "";
        channelMessage.className = "channel-message";
    }

    if (channelUsername) {
        channelUsername.value = "";
    }

    channelModal?.classList.add("show");

    haptic();

}

function closeChannelModal() {

    channelModal?.classList.remove("show");

}

document
    .getElementById("addChannelButton")
    ?.addEventListener("click", openChannelModal);

document
    .getElementById("closeChannelModal")
    ?.addEventListener("click", closeChannelModal);

document
    .getElementById("channelModalOverlay")
    ?.addEventListener("click", closeChannelModal);


/* =====================================================
   VERIFY CHANNEL
===================================================== */

document
    .getElementById("verifyChannelButton")
    ?.addEventListener("click", verifyChannel);

async function verifyChannel() {

    const username =
        channelUsername?.value.trim();

    if (!username) {

        channelMessage.textContent =
            "⚠ أدخل اسم المستخدم أولًا";

        channelMessage.className =
            "channel-message error";

        haptic("warning");

        return;
    }

    const button =
        document.getElementById("verifyChannelButton");

    button.disabled = true;

    const originalHTML = button.innerHTML;

    button.innerHTML = "⏳ ...";

    try {

        const response = await apiFetch(
            "/api/verify-channel",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ username })
            }
        );

        const data = await response.json();

        if (!data.ok) {

            channelMessage.textContent =
                data.error || "خطأ";

            channelMessage.className =
                "channel-message error";

            haptic("error");

            return;
        }

        channelMessage.textContent =
            tr("verifyChannelSuccess");

        channelMessage.className =
            "channel-message success";

        haptic("success");

        /* Reload channels */

        await loadChannels();

        setTimeout(closeChannelModal, 1200);

    } catch (error) {

        console.error(error);

        channelMessage.textContent =
            "فشل الاتصال بالسيرفر";

        channelMessage.className =
            "channel-message error";

        haptic("error");

    } finally {

        button.disabled = false;
        button.innerHTML = originalHTML;

    }

}


/* =====================================================
   TEXT PREVIEW
===================================================== */

postText?.addEventListener("input", () => {

    updateCharacterCount();

    updatePreview();

});


function updateCharacterCount() {

    if (!characterCount || !postText) return;

    characterCount.textContent =
        `${postText.value.length} / 4096`;

}


/* =====================================================
   FILE PICKER
===================================================== */

document
    .getElementById("uploadButton")
    ?.addEventListener("click", e => {

        /* Let the label trigger the input */

        if (e.target.id !== "mediaInput") {
            mediaInput?.click();
        }

    });


mediaInput?.addEventListener("change", async () => {

    selectedFile = mediaInput.files?.[0];

    if (!selectedFile) return;

    fileInfo.classList.remove("hidden");

    fileInfo.textContent =
        `${selectedFile.name} — ${formatBytes(selectedFile.size)}`;

    previewFile(selectedFile);

    await uploadFile();

});


/* =====================================================
   PREVIEW FILE
===================================================== */

function previewFile(file) {

    if (!previewMedia) return;

    previewMedia.innerHTML = "";
    previewMedia.classList.remove("hidden");

    if (file.type.startsWith("image/")) {

        const img = document.createElement("img");

        img.src = URL.createObjectURL(file);

        previewMedia.appendChild(img);

    } else if (file.type.startsWith("video/")) {

        const video = document.createElement("video");

        video.src = URL.createObjectURL(file);
        video.controls = true;

        previewMedia.appendChild(video);

    } else if (file.type.startsWith("audio/")) {

        const audio = document.createElement("audio");

        audio.src = URL.createObjectURL(file);
        audio.controls = true;

        previewMedia.appendChild(audio);

    } else {

        previewMedia.textContent =
            `📎 ${file.name}`;

    }

}


/* =====================================================
   UPLOAD FILE
===================================================== */

async function uploadFile() {

    showToast(tr("uploading"), "⏳");

    const formData = new FormData();

    formData.append("file", selectedFile);

    try {

        const response = await apiFetch(
            "/api/upload",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!data.ok) {

            uploadedMedia = null;

            showToast(
                data.error || tr("uploadFailed"),
                "⚠"
            );

            return;
        }

        uploadedMedia = data;

        showToast("✓", "✓");

    } catch (error) {

        console.error(error);

        uploadedMedia = null;

        showToast(tr("uploadFailed"), "⚠");

    }

}


/* =====================================================
   CUSTOM BUTTONS
===================================================== */

document
    .getElementById("addButton")
    ?.addEventListener("click", () => addCustomButton());


function addCustomButton(text = "", url = "") {

    const row =
        document.createElement("div");

    row.className = "custom-button-row";

    const textInput =
        document.createElement("input");

    textInput.placeholder = tr("addButtonText");
    textInput.value = text;

    const urlInput =
        document.createElement("input");

    urlInput.placeholder = tr("addButtonUrl");
    urlInput.value = url;

    const remove =
        document.createElement("button");

    remove.className = "remove-button";
    remove.type = "button";
    remove.textContent = "×";

    textInput.addEventListener("input", updatePreview);
    urlInput.addEventListener("input", updatePreview);

    remove.addEventListener("click", () => {

        row.remove();

        updatePreview();

    });

    row.appendChild(textInput);
    row.appendChild(urlInput);
    row.appendChild(remove);

    buttonsContainer.appendChild(row);

    updatePreview();

}


/* =====================================================
   GET CUSTOM BUTTONS
===================================================== */

function getButtons() {

    const result = [];

    const rows =
        buttonsContainer?.querySelectorAll(
            ".custom-button-row"
        ) || [];

    rows.forEach(row => {

        const inputs =
            row.querySelectorAll("input");

        if (inputs.length < 2) return;

        const text = inputs[0].value.trim();
        const url = inputs[1].value.trim();

        if (
            text
            && (
                url.startsWith("https://")
                || url.startsWith("http://")
                || url.startsWith("tg://")
            )
        ) {

            result.push({ text, url });

        }

    });

    return result;

}


/* =====================================================
   AUTO DETECT LINKS
===================================================== */

function detectLinks(text) {

    const buttons = [];

    if (!smartLinksCheckbox?.checked) {
        return buttons;
    }

    const urlRegex = /https?:\/\/[^\s<]+/gi;

    const urls = text.match(urlRegex) || [];

    const unique = [...new Set(urls)];

    unique.slice(0, 8).forEach(url => {

        buttons.push({
            text: tr("openLink"),
            url
        });

    });

    return buttons;

}


/* =====================================================
   UPDATE PREVIEW
===================================================== */

function updatePreview() {

    if (!previewText || !previewButtons) return;

    const text = postText?.value.trim() || "";

    previewText.textContent =
        text || tr("previewPlaceholder");

    previewButtons.innerHTML = "";

    const custom = getButtons();
    const automatic = detectLinks(text);

    const all = [...custom, ...automatic];

    const seen = new Set();
    const unique = [];

    all.forEach(button => {

        if (seen.has(button.url)) return;

        seen.add(button.url);
        unique.push(button);

    });

    unique.forEach(button => {

        const element =
            document.createElement("div");

        element.className = "preview-button";
        element.textContent = button.text;

        previewButtons.appendChild(element);

    });

}


/* =====================================================
   SMART LINKS TOGGLE
===================================================== */

smartLinksCheckbox?.addEventListener(
    "change",
    updatePreview
);


/* =====================================================
   PUBLISH
===================================================== */

document
    .getElementById("publishButton")
    ?.addEventListener("click", publish);


async function publish() {

    const channelId = postChannel?.value;
    const text = postText?.value.trim() || "";

    if (!channelId) {

        showToast(tr("chooseChannel"), "⚠");
        haptic("warning");

        return;
    }

    if (!text && !uploadedMedia) {

        showToast(tr("emptyPost"), "⚠");
        haptic("warning");

        return;
    }

    const buttons = [
        ...getButtons(),
        ...detectLinks(text)
    ];

    const seen = new Set();
    const uniqueButtons = [];

    buttons.forEach(button => {

        if (seen.has(button.url)) return;

        seen.add(button.url);
        uniqueButtons.push(button);

    });

    const payload = {

        channel_id: channelId,
        text,
        media_type: uploadedMedia?.media_type || null,
        media_path: uploadedMedia?.path || null,
        buttons: uniqueButtons

    };

    const publishButton =
        document.getElementById("publishButton");

    const originalHTML = publishButton.innerHTML;

    publishButton.disabled = true;
    publishButton.innerHTML = `⏳ ${tr("publishing")}`;

    try {

        const response = await apiFetch(
            "/api/publish",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            }
        );

        const data = await response.json();

        if (!data.ok) {

            showToast(
                data.error || tr("publishFailed"),
                "⚠"
            );

            haptic("error");

            return;
        }

        haptic("success");

        showToast(tr("published"), "🚀");

        resetPost();
        closePostModal();

    } catch (error) {

        console.error(error);

        showToast(tr("publishFailed"), "⚠");
        haptic("error");

    } finally {

        publishButton.disabled = false;
        publishButton.innerHTML = originalHTML;

    }

}


/* =====================================================
   RESET POST FORM
===================================================== */

function resetPost() {

    if (postText) postText.value = "";
    if (mediaInput) mediaInput.value = "";

    selectedFile = null;
    uploadedMedia = null;

    fileInfo?.classList.add("hidden");
    fileInfo && (fileInfo.textContent = "");

    previewMedia.innerHTML = "";
    previewMedia?.classList.add("hidden");

    buttonsContainer.innerHTML = "";

    updateCharacterCount();
    updatePreview();

}


/* =====================================================
   POSTS MODAL
===================================================== */

document
    .getElementById("postsButton")
    ?.addEventListener("click", loadPosts);

document
    .getElementById("closePostsModal")
    ?.addEventListener("click", () => {

        postsModal?.classList.remove("show");

    });

document
    .getElementById("postsModalOverlay")
    ?.addEventListener("click", () => {

        postsModal?.classList.remove("show");

    });


async function loadPosts() {

    try {

        const response = await apiFetch("/api/posts");

        const data = await response.json();

        if (!data.ok) {
            showToast(tr("unauthorized"), "⚠");
            return;
        }

        postsList.innerHTML = "";

        if (!data.posts.length) {

            postsList.innerHTML =
                `<div class="post-item">${tr("noPosts")}</div>`;

        } else {

            data.posts.forEach(post => {

                const item =
                    document.createElement("div");

                item.className = "post-item";

                const title =
                    document.createElement("strong");

                title.textContent =
                    `#${post.id} · ${post.media_type || "text"}`;

                const content =
                    document.createElement("p");

                content.textContent =
                    post.text || "📎 Media post";

                item.appendChild(title);
                item.appendChild(content);

                postsList.appendChild(item);

            });

        }

        postsModal?.classList.add("show");

        haptic();

    } catch (error) {

        console.error(error);

        showToast("Failed to load posts", "⚠");

    }

}


/* =====================================================
   INIT
===================================================== */

applyLanguage();

updateCharacterCount();

updatePreview();

loadChannels();
