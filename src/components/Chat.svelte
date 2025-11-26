<script lang="ts">
    import { onMount, tick } from "svelte";
    import { pyInvoke } from "tauri-plugin-pytauri-api";
    import { type ChatType, type MessageType } from "../libs/types";
    import Message from "./Message.svelte";
    import { createVirtualizer } from '@tanstack/svelte-virtual';
    import { convertFileSrc } from "@tauri-apps/api/core";
    import { chosen_color } from "../libs/preferences";
    import { open } from "@tauri-apps/plugin-dialog";
    import { profilesRefresh } from "../libs/overlayState";

    let { chat_id, scroll_to }: { chat_id: string, scroll_to: number | null } = $props();

    let chat_info = $state<ChatType>();
    let messages = $state<MessageType[]>([]);
    let messageContainer = $state<HTMLDivElement>();

    let chat_name = $state<string>("Loading...");
    let chat_avatar = $state<string | null>(null);

    let currentDateLabel = $state("");
    let messageElements: (HTMLDivElement | null)[] = $state([]);
    
    let virtualizer = $derived(createVirtualizer<HTMLDivElement, HTMLDivElement>({
        count: messages.length,
        getScrollElement: () => messageContainer ?? null,
        estimateSize: () => 120,
        overscan: 5,
        gap: 8,
        measureElement: (el) => el?.getBoundingClientRect().height ?? 120,
    }));

    let virtualItems = $derived($virtualizer.getVirtualItems());
    let totalSize = $derived($virtualizer.getTotalSize());

    function shouldShowDateSeparator(index: number): boolean {
        if (index === 0) return true;
        
        const currentMsg = messages[index];
        const prevMsg = messages[index - 1];
        
        if (!currentMsg || !prevMsg) return false;
        
        const currentDate = new Date(currentMsg.timestamp).toDateString();
        const prevDate = new Date(prevMsg.timestamp).toDateString();
        
        return currentDate !== prevDate;
    }

    function formatDateSeparator(timestamp: string): string {
        const date = new Date(timestamp);
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        if (date.toDateString() === today.toDateString()) {
            return 'Today';
        } else if (date.toDateString() === yesterday.toDateString()) {
            return 'Yesterday';
        } else {
            return date.toLocaleDateString('en-US', {
                day: "2-digit",
                month: "short",
                year: "numeric",
            });
        }
    }

    
    function scroll_to_mssg() {
        if (!scroll_to) {
            $virtualizer.scrollToIndex(messages.length-1, {
                align: 'start',
                behavior: 'auto'
            });
        };
        
        const index = messages.findIndex(m => m.id === scroll_to);
        if (index !== -1) {
            $virtualizer.scrollToIndex(index, {
                align: 'start',
                behavior: 'auto'
            });
        }
    }

    onMount(async () => {
        chat_info = await pyInvoke<ChatType>("get_chat", {"chat_id": chat_id});
        messages = await pyInvoke<Array<MessageType>>("get_chat_messages", {"chat_id": chat_id});

        if (chat_info) {
            chat_name = chat_info.name;
            chat_avatar = chat_info.avatar ? convertFileSrc(chat_info.avatar) : null;
        }

        setTimeout(() => tick().then(scroll_to_mssg), 100);
    });

    $effect(() => {
        if (messageElements.length) {
            messageElements.forEach((el) => {
                if (el) $virtualizer.measureElement(el);
            });
        }
    });

    $effect(() => {
        if (virtualItems.length > 0 && messages[virtualItems[0].index]) {
            const date = new Date(messages[virtualItems[0].index].timestamp);
            currentDateLabel = date.toLocaleDateString('en-US', {
                day: "2-digit",
                month: "short",
                year: "numeric",
            });
        }
    });

    async function selectFile() {
        const filePath = await open({
            multiple: false,
            filters: [
                { name: 'Image files', extensions: ['png', 'jpg', 'jpeg', 'webp', 'gif'] }
            ],
            directory: false
        });

        if (filePath) {
            chat_avatar = convertFileSrc(filePath);
            await saveChat("avatar", filePath);
            return;
        } else {
            console.log('не вибрав файл');
            return;
        }
    }

    async function saveChat(option: string, value: string) {
        const res = await pyInvoke("update_chat", {
            id: chat_info?.id,
            [option]: value
        });
        profilesRefresh.set(true);
        console.log(res);
    }
</script>

<main class="container" style="--accent: {$chosen_color}">
    <div class="header">
        <div
            class="avatar"
            onclick={() => selectFile()}
            role="button"
            onkeydown={() => console.log("lel")}
            tabindex="0"
        >
            {#if chat_avatar}
                <img src={chat_avatar} alt={chat_name} />
            {:else if chat_name}
                <div class="placeholder">
                    {(chat_name?.[0] ?? "?").toUpperCase()}
                </div>
            {:else}
                <div class="placeholder">?</div>
            {/if}
            <div class="avatar-overlay">
                <img
                    style="filter: invert(100%); width:30px; height:30px;"
                    src="icons/edit.svg"
                    alt="edit"
                />
            </div>
        </div>
        <input
            type="text"
            bind:value={chat_name}
            style="width: {chat_name.length + 1}ch"
            class="name-input"
            onchange={() => saveChat("name", chat_name)}
            oninput={(e) =>
                ((e.target as HTMLInputElement).style.width =
                    ((e.target as HTMLInputElement).value.length + 1 || 1) +
                    "ch")}
        />
    </div>

    <div class="message-div" bind:this={messageContainer}>
        {#if messages.length >= 1}
            <div
                style="height: {totalSize}px; width: 100%; position: relative;"
            >
                {#each virtualItems as virtualRow, idx (virtualRow.key)}
                    <div
                        bind:this={messageElements[idx]}
                        data-index={virtualRow.index}
                        style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        transform: translateY({virtualRow.start}px);
                    "
                    >
                        {#if shouldShowDateSeparator(virtualRow.index)}
                            <div class="date-separator">
                                <span class="date-label">
                                    {formatDateSeparator(messages[virtualRow.index].timestamp)}
                                </span>
                            </div>
                        {/if}
                        <Message
                            message={messages[virtualRow.index]}
                            highlight={scroll_to ===
                                messages[virtualRow.index].id}
                        />
                    </div>
                {/each}
            </div>
        {/if}
    </div>
    <div class="footer" style="height: 15px; background-color: #151515; border-top: 1px solid rgba(255, 255, 255, 0.1);"></div>

</main>

<style>
    .container {
        display: flex;
        flex-direction: column;
        height: 80vh;
        width: 70vw;
        font-family: "Nunito", "monospace";
        color: white;
        border-radius: 25px;
        margin-top: -40px;
        overflow: hidden;
        background: rgba(20, 20, 25, 0.95);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .header {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        text-align: center;
        flex-shrink: 0;
        height: 90px;
        background: #151515;
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        font-weight: 700;
        font-size: 20px;
        gap: 15px;
        padding: 15px 20px;
    }

    .message-div {
        flex: 1;
        position: relative;
        width: 100%;
        background: rgba(17, 17, 18, 0.987);
        overflow-y: auto;
        overflow-x: hidden;
    }

    .message-div::-webkit-scrollbar {
        width: 12px;
    }

    .message-div::-webkit-scrollbar-track {
        background: rgba(25, 24, 24, 0.962);
    }

    .message-div::-webkit-scrollbar-thumb {
        background-color: var(--accent);
        border-radius: 4px;
        border: 2px solid transparent;
        background-clip: content-box;
    }

    .avatar {
        flex-shrink: 0;
        width: 65px;
        height: 65px;
        border-radius: 50%;
        overflow: hidden;
        background: rgba(50, 50, 55, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        text-transform: uppercase;
        font-size: 22px;
        position: relative;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .avatar:hover {
        transform: scale(1.05);
        border-color: rgba(255, 255, 255, 0.3);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
    }

    .avatar .avatar-overlay {
        opacity: 0;
    }

    .avatar:hover .avatar-overlay {
        opacity: 1;
    }

    .avatar:hover img {
        filter: brightness(0.4);
    }

    .avatar-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(4px);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
        color: white;
    }

    .avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: filter 0.3s ease;
    }

    .placeholder {
        font-size: 24px;
    }

    .name-input {
        font-size: 1.5rem;
        font-weight: 700;
        color: #fff;
        background: transparent;
        border: none;
        outline: none;
        padding: 8px 12px;
        margin: 0;
        font-family: "Nunito", sans-serif;
        border-radius: 10px;
        transition: all 0.3s ease;
    }

    .name-input:hover {
        background: rgba(255, 255, 255, 0.05);
    }

    .name-input:focus {
        background: rgba(255, 255, 255, 0.08);
        box-shadow: 0 0 0 2px rgba(var(--accent), 0.3);
    }

    .date-separator {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px 0 15px 0;
        position: relative;
    }


    .date-label {
        padding: 6px 16px;
        background: #151515;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        color: white;
        margin: 0 15px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        white-space: nowrap;
    }
</style>