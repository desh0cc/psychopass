<script lang="ts">
    import { onMount } from "svelte";
    import { pyInvoke } from "tauri-plugin-pytauri-api";
    import EmotionJar from "./EmotionJar.svelte";
    import { profilesRefresh } from "../libs/overlayState";
    import { open } from "@tauri-apps/plugin-dialog";
    import { convertFileSrc } from "@tauri-apps/api/core";
    import { type Writable, writable } from "svelte/store";
    import { type PlatformUser, type Profile, type EmotionStats } from "../libs/types";
    import { platforms_icons } from "../libs/types";
    import { chosen_color } from "../libs/preferences";
    import { type ChatType } from "../libs/types";
    import { popOverlay } from "../libs/overlayState";
  
    export let id: number;
    export let isMerging: Writable<boolean>;

    let loading = true;
    let avatar: string;
    let name = "";
    let created_at = "";
    let total_messages = 0;
    let all_emotions: [string, number][] = [];
    let platforms = writable<PlatformUser[]>([]);
    let chats: Array<ChatType> = [];

    onMount(async () => {
        try {
            const data = await pyInvoke<Profile>("get_profile_id", { user_id: id });
            console.log(data);
            const emotions = await pyInvoke<EmotionStats>("get_emotions", { user_id: id });
            console.log(emotions);
            total_messages = emotions.total_messages;
            if (data.avatar) avatar = convertFileSrc(data.avatar);
            name = data.global_name;
            created_at = new Date(data.added_at).toLocaleDateString();
            platforms.set(data.platform_users ?? []);
            if (data.chats) {
                chats = data.chats;
            }

            if (emotions?.emotions) {
                all_emotions = emotions.emotions
                    .map(e => [e.name, e.percent] as [string, number])
                    .sort((a, b) => b[1] - a[1]);
            }
        } catch (err) {
            console.error("Error loading profile:", err);
        } finally {
            loading = false;
        }
    });

    async function selectFiles() {
        const filePath = await open({
            multiple: false,
            filters: [
                { name: 'Image files', extensions: ['png', 'jpg', 'jpeg', 'webp', 'gif'] }
            ],
            directory: false
        });

        if (filePath) {
            avatar = filePath;
            await save_avatar();
            return;
        } else {
            console.log('не вибрав файл(и)');
            return;
        }
    }

    async function save_name() {
        const res = await pyInvoke<string>("update_profile", {"id": id, "global_name": name});
        profilesRefresh.set(true);
    }

    async function save_avatar() {
        const res = await pyInvoke<string>("update_profile", {"id": id, "avatar": avatar});
        avatar = convertFileSrc(avatar);
        profilesRefresh.set(true);
    }


    async function unmerge_profile(second_id: number) {
        const res = await pyInvoke("unmerge_profiles", {"primary_id": id, "secondary_ids": [second_id]})
        profilesRefresh.set(true);
        platforms.update(plats => plats.filter(p => p.id !== second_id));
    }

    function close() {
        popOverlay();
    }
</script>

<div class="profile-full" style="--thumb-color: {$chosen_color}">
    <button class="close" onclick={close}>×</button>

    {#if loading}
        <div class="loading">
            <p>Loading profile...</p>
        </div>
    {:else}
        <div class="header">
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <div
                class="avatar"
                onclick={() => selectFiles()}
                role="button"
                onkeydown={() => console.log("lel")}
                tabindex="0"
            >
                {#if avatar}
                    <img src={avatar} alt={name} />
                {:else if name}
                    <div class="placeholder">
                        {(name?.[0] ?? "?").toUpperCase()}
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
            <div class="info">
                <div class="change-name">
                     <input
                        type="text"
                        bind:value={name}
                        style="width: {name.length + 1}ch"
                        class="name-input"
                        onchange={() => save_name()}
                        oninput={(e) =>
                            ((e.target as HTMLInputElement).style.width =
                                ((e.target as HTMLInputElement).value.length + 1 || 1) +
                                "ch")}
                    />
                </div>
                <p class="date">Added: {created_at}</p>
                <p class="total">Messages: {total_messages}</p>
            </div>
        </div>

        {#if $platforms.length > 0}
            <h3>Linked Platforms</h3>
            <div class="platforms">
                {#each $platforms as p}
                    <div class="bubble">
                        <img src="{platforms_icons[p.platform]}" alt={p.platform}> 
                        <p class="username">{p.username}</p>
                        {#if p.id != id}
                        <span>
                            <button onclick={() => unmerge_profile(p.id)}>
                                <p>x</p>
                            </button>
                        </span>
                        {/if}
                    </div> 
                {/each}
            </div>
        {/if}
        {#if chats.length > 0}
            <h3>Chats</h3>
            <div class="chats">
                {#each chats as chat}
                    <div class="bubble">
                        {#if chat.avatar}
                            <img style="height:32px; width:32px; border-radius:50%" src="{convertFileSrc(chat.avatar)}" alt={chat.name}>
                        {:else}
                            <div class="placeholder">
                                <span>{chat.name ? chat.name[0] : "?"}</span>
                            </div>
                        {/if}  
                        <span class="username">{chat.name}</span>
                    </div> 
                {/each}
            </div>
        {/if}

        {#if all_emotions.length > 0}
            <h3>Emotion Jars</h3>
            <div class="emotions">
                {#each all_emotions as [emotion, percent]}
                    <EmotionJar
                        emotion={emotion}
                        fill={percent}
                        id={id}
                        isMerging={isMerging}
                    />
                {/each}
            </div>
        {:else}
            <p class="no-data">No emotion data available.</p>
        {/if}
    {/if}
</div>

<style>
.profile-full {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: #151515;
    border-radius: 20px;
    max-width: 500px;
    max-height: 90vh;
    padding: 25px;
    overflow-y: auto;
    position: relative;
    color: #f0f0f0;
    box-shadow: 0 0 25px rgba(0, 0, 0, 0.5);
    transition: all 0.3s ease;
    user-select: none;
}

.profile-full::-webkit-scrollbar {
    width: 12px;
}

.profile-full::-webkit-scrollbar-track {
    background: rgba(25, 24, 24, 0.962);
}

.profile-full::-webkit-scrollbar-thumb {
    background-color: var(--thumb-color);
    border-radius: 4px;
    border: 2px solid transparent;
    background-clip: content-box;
}

.change-name {
    display: flex;
    flex-direction: row;
    justify-content: center;
}

.chats,
.platforms {
    width: 85%;
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 6px;
}

.platforms .bubble {
    display: inline-flex;
    flex: 0 0 auto;       
    align-items: center;
    height: 15px;
    gap: 3px;
    color: #ffffff;
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(243, 235, 235, 0.15);
    padding: 3px 6px;
    border-radius: 10px;
    height: auto;
}

.platforms .bubble p {
    margin: 0;
    line-height: 1;
}


.platforms .bubble img {
    width: 15px;
    height: 15px;
    filter: invert(1);
}

.platforms .bubble span button {
    width: 15px;
    height: 15px;
    color: #f0f0f0;
    font-size: 10px;
    font-weight: 700;
    text-align: center;
    background-color: #211f1f26;
    filter: blur(10);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    justify-content: center;
    align-items: center;
    justify-items: center;
    cursor: pointer;
}

.platforms .bubble span {
    display: none;
    visibility: hidden;
}

.platforms .bubble:hover span {
    display: flex;
    visibility: visible;
}

.chats .bubble {
    display: inline-flex;
    flex: 0 0 auto;       
    align-items: center;
    gap: 3px;
    color: #ffffff;
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(243, 235, 235, 0.15);
    padding: 3px 8px;
    border-radius: 10px;
    height: auto;
}

.chats .placeholder {
    height: 32px;
    width: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #151414, #1d1c1c);
    display: flex;
    justify-content: center;
    align-items: center;
    color: #cfcfcf;
    font-weight: 600;
    font-size: 14px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.35);
}

.close {
    position: absolute;
    top: 12px;
    right: 18px;
    border: none;
    background: transparent;
    font-size: 1.8rem;
    cursor: pointer;
    color: #888;
    transition: color 0.2s ease;
}
.close:hover {
    color: #fff;
}

.header {
    display: flex;
    align-items: center;
    gap: 20px;
    flex-direction: column;
}

.header .info input,
.header .info {
    text-align: center;
}

.avatar {
    flex-shrink: 0;
    width: 96px;
    height: 96px;
    border-radius: 50%;
    overflow: hidden;
    background: rgba(50, 50, 55, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: white;
    text-transform: uppercase;
    font-size: 35px;
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


.emotions {
    padding: 10px;
    max-width: 75%;
    max-height: 250px;
    justify-content: center;
    border-radius: 20px;
    background-color: #0b0b0b;
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 10px;
    overflow: auto;
}

.name-input {
    font-size: 1.8rem;
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
    justify-self: center;
}

.name-input:hover {
    background: rgba(255, 255, 255, 0.05);
}

.name-input:focus {
    background: rgba(255, 255, 255, 0.08);
    box-shadow: 0 0 0 2px rgba(var(--accent), 0.3);
}

.date, .total {
    color: #aaa;
    margin: 2px 0;
}

h3 {
    font-size: 1.2rem;
    color: #fff;
    margin-bottom: 10px;
}


.loading {
    text-align: center;
    padding: 40px;
    color: #aaa;
}


.no-data {
    color: #666;
    text-align: center;
    margin-top: 20px;
}
</style>
