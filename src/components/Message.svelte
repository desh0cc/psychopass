<script lang="ts">
    import { type MessageType } from "../libs/types";
    import { convertFileSrc } from "@tauri-apps/api/core";
    import { colors } from "../libs/types";
    import { pushOverlay } from "../libs/overlayState";
    import linkifyHtml from 'linkify-html';
    import { openUrl } from "@tauri-apps/plugin-opener";
    import { open } from "@tauri-apps/plugin-fs";
    import { chosen_color } from "../libs/preferences";
    import { scale } from 'svelte/transition';
    import { contextMenuStore } from "../libs/contextMenuState";
    import { pyInvoke } from "tauri-plugin-pytauri-api";
    import { deleteStore } from "../libs/deleteState";

    const { message, jumpButton = false, emotionBg = false, 
        highlight = false, showFullDate = false} = $props<{
        message: MessageType;
        jumpButton?: boolean;
        emotionBg?: boolean;
        highlight?: boolean;
        showFullDate?: boolean;
    }>();

    const color = colors[message.emotion];
    const mssgBg = emotionBg ? color : "#ffffff0d";
    const emotionColor = emotionBg ? "#f1f1f1" : color;

    let contextMenu = $state($contextMenuStore);

    function openMessage() {
        if (jumpButton) {
            pushOverlay({
                type: 'chat',
                data: { chat_id: message.chat_id.toString(), scroll_to: message.id }
            });
        }
    }

    function handleClick(e: MouseEvent, file: boolean = false) {
        const target = e.target as HTMLAnchorElement;
        if (target.tagName === 'A' && target.href) {
            e.preventDefault();
            if (file) {open(target.href)}
            else {
                openUrl(target.href);
            }
        }
    }

    function handleContextMenu(e: MouseEvent) {
        e.preventDefault();
        e.stopPropagation();

        const target = e.currentTarget as HTMLElement;
        const chatContainer = target.closest('.chat-container') || target.offsetParent;
        
        if (chatContainer instanceof HTMLElement) {
            const rect = chatContainer.getBoundingClientRect();
            
            const relativeX = e.clientX - rect.left;
            const relativeY = e.clientY - rect.top;
            
            contextMenuStore.open(relativeX, relativeY, message.id);
        } else {
            contextMenuStore.open(e.clientX, e.clientY, message.id);
        }
    }

    function closeContextMenu(e?: MouseEvent) {
        if (e) {
            const target = e.target as HTMLElement;
            if (target.closest('.context-menu')) {
                return;
            }
        }
        contextMenuStore.close();
    }

    async function handleDeleteMessage(e: MouseEvent) {
        e.stopPropagation();
        const res = await pyInvoke("delete_message", {"message_id": message.id})
        console.log(res);
        contextMenuStore.close();
    }

    $effect(() => {
        contextMenu = $contextMenuStore;
    });

    const options = {
        rel: "noopener",
        target: {
            href: "url",
            url: "_blank"
        },
        className: "link",
        validate: true
    };

    let date = $derived(
        showFullDate
            ? new Date(message.timestamp).toLocaleDateString()
            : new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    );

    let isHidden = $derived(
        $deleteStore.some(d => d.obj_type === 'message' && d.obj_id === message.id)
    );



</script>


<button
    class="message"
    class:toside={jumpButton}
    data-emotion={message.emotion}
    onclick={openMessage}
    oncontextmenu={handleContextMenu}
    style="--accent: {$chosen_color}"
    class:hide={isHidden}
>
    {#if message.reply}
        <div class="reply-block">
            <img src="icons/reply.svg" alt="reply-img">

            <div class="reply-content">
                <div class="reply-author">{message.reply.author_name}</div>

                {#if message.reply.text}
                    <div class="reply-text">{message.reply.text}</div>
                {/if}

                {#if message.reply.media}
                    <div class="reply-media">
                        <img src="image.svg" alt="media_default">
                    </div>
                {/if}
            </div>
        </div>
    {/if}


    <div class="content" class:highlight={highlight} style="background-color: {mssgBg}; --end-bg: {mssgBg}; --start-bg: {color}">

        <div class="header">
            <div class="avatar">
                {#if message.avatar}
                    <img src={convertFileSrc(message.avatar)} alt={message.author_name} />
                {:else}
                    <div class="placeholder">{(message.author_name?.[0] ?? "?").toUpperCase()}</div>
                {/if}
            </div>

            <div class="header-info">
                <span class="author">{message.author_name}</span>
                <span class="timestamp">{date}</span>
            </div>
        </div>

        {#if message.media}
            <div class="media">
                {#each message.media as media}
                    {#if media.type === "photo"}
                        <!-- svelte-ignore a11y_img_redundant_alt -->
                        <img src={convertFileSrc(media.path)} alt="photo"/>
                    {:else if media.type === "video" || media.type === "animation"}
                        <video controls src={convertFileSrc(media.path)}>
                            <track kind="captions">
                        </video>
                    {:else}
                        <a class="file" target="_blank" href={media.path} download onclick={(e) => handleClick(e, true)}>
                            Download {media.type}
                        </a>
                    {/if}
                {/each}
            </div>
        {/if}

        <div class="text-content" class:forward={message.forwarded_from !== null}>
            {#if message.forwarded_from}
                <p class="forward-name">
                    <span style="opacity: 0.3;">forwarded:</span>
                    {message.forwarded_from}
                </p>
            {/if}
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
            <p class="text" onclick={handleClick}>    
                {@html linkifyHtml(message.text, options)}
            </p>
        </div>

        {#if message.emotion}
            <span style="color: {emotionColor};" class="emotion">{message.emotion}</span>
        {/if}
    </div>
</button>

{#if !jumpButton && contextMenu.show && contextMenu.messageId === message.id}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div 
        class="context-menu" 
        style="left: {contextMenu.x}px; top: {contextMenu.y}px;"
        in:scale={{ duration: 150, start: 0.85, opacity: 0 }}
        out:scale={{ duration: 100, start: 0.95, opacity: 0 }}
        onclick={(e) => e.stopPropagation()}
        oncontextmenu={(e) => e.stopPropagation()}
    >
        <button class="context-item delete" onclick={handleDeleteMessage}>
            <img style="height: 20px; width:20px;" src="delete.svg" alt="delete-btn">
            Delete message
        </button>
    </div>
{/if}

<style>
.message {
    display: flex;
    align-items: flex-start;
    flex-direction: column;
    gap: 10px;
    border-radius: 12px;
    transition: background 0.2s ease;
    font-size: 1rem;
    border: none;
    font-family: 'Nunito', 'monospace';
    font-weight: 700;
    color: white;
    min-height: 100px;
    max-width: 99%;
    overflow: hidden;
    transition: all 100ms ease-in;
    background-color: transparent;
    user-select: text;
}

.message.hide {
    display: none;
}

.message.toside:hover {
    cursor: pointer;
    transform: translateX(8px);
}

.media :global(a),
.text :global(a) {
    color: #4da6ff;
    text-decoration: underline;
}

.media :global(a:hover),
.text :global(a:hover) {
    color: #80c1ff;
}

@keyframes highlight {
    0% { background-color: var(--start-bg); }
    50% { background-color: var(--start-bg + 26); }
    100% { background-color: var(--end-bg); }
}

.message .highlight {
    animation: highlight 10s ease;
}

.avatar {
    flex-shrink: 0;
    width: 50px;
    height: 50px;
    min-height: 50px;
    border-radius: 50%;
    overflow: hidden;
    background: #333;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: white;
    text-transform: uppercase;
}

.avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.content {
    display: flex;
    flex-direction: column;
    padding: 8px 12px;
    margin-right: 50px;
    width: 100%;
    border-radius: 12px;
}

.header {
    display: flex;
    align-items: center;
    gap: 10px;
}

.header-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex: 1;
    padding-right: 20px;
}

.author {
    color: #fff;
    font-weight: 600;
    text-overflow: ellipsis;
    max-lines: 1;
}

.timestamp {
    color: #f8f0f0;
    opacity: 0.6;
}

.text-content {
    text-align: start;
    min-width: 200px;
    max-width: 95%;
    margin-left: 60px;
    margin-top: -10px;
}

.text-content.forward {
    border-radius: 5px;      
    background-color: color-mix(in srgb, var(--accent) 30%, transparent);
    border-left: 4px solid var(--accent);
    padding-left: 10px;
    margin-right: 30px;
}

.text {
    margin-top: 4px;
    color: #eee;
    font-size: 0.95rem;
    word-wrap: break-word;
    white-space: pre-wrap;
    cursor: text;
}


.emotion {
    align-self: flex-end;
    opacity: 0.9;
    font-weight: 600;
    padding-right: 20px;
}


.reply-block {
    display: flex;
    margin-bottom: -6px;
    padding: 8px 10px;
    background: #1a1a1a;
    border-radius: 8px;
    border-left: 3px solid rgba(255,255,255,0.15);
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06);
    opacity: 0.9;
    text-align: start;
    z-index: 10;
    width: 100%;
    flex-direction: row;
    gap: 5px;
}

.reply-block img {
    width: 15px;
    height: 15px;
    transform: scaleX(-1);
    filter: invert(1);
}

.reply-content {
    display: flex;
    flex-direction: column;
}



.reply-author {
    font-size: 0.8rem;
    font-weight: 600;
    color: #ccc;
}

.reply-text {
    font-size: 0.9rem;
    color: #ddd;
    margin-top: 2px;
}

.reply-media img {
    max-width: 120px;
    border-radius: 6px;
    margin-top: 6px;
    opacity: 0.9;
}

.media {
    display: flex;
    justify-content: start;
}

.media img,
.media video {
    max-width: 260px;
    border-radius: 10px;
    margin-left: 60px;
    margin-bottom: 15px;
}

.media .file {
    margin-left: 60px;
    margin-bottom: 5px;
}

.context-menu {
    position: fixed;
    z-index: 9999;
    background: #1a1a1a;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    min-width: 180px;
}

.context-item {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 8px 12px;
    background: transparent;
    border: none;
    color: #eee;
    font-family: 'Nunito', 'monospace';
    font-size: 0.9rem;
    font-weight: 600;
    text-align: left;
    cursor: pointer;
    border-radius: 6px;
    transition: background 0.15s ease;
}

.context-item:hover {
    background: rgba(255, 255, 255, 0.08);
}

.context-item.delete:hover {
    background: rgba(255, 59, 48, 0.15);
    color: #ff3b30;
}

.context-item.delete img {
    filter:invert(1);
}

.context-item.delete:hover img {
    filter: invert(48%) sepia(79%) saturate(2476%) hue-rotate(336deg) brightness(95%) contrast(91%);
}
</style>