<script lang="ts">
    import { pyInvoke } from "tauri-plugin-pytauri-api";
    import EmotionJar from "./EmotionJar.svelte";
    import { onMount } from "svelte";
    import { chosen_color } from "../libs/preferences";
    import { pushOverlay } from "../libs/overlayState";
    import type { Writable } from "svelte/store";
    import { type EmotionStats } from "../libs/types";
    import { convertFileSrc } from "@tauri-apps/api/core";


    export let id: number;
    export let name: string = "";
    export let avatar: string | null;
    export let isMerging: Writable<boolean>;

    let emotions: EmotionStats | null = null;
    let emotionEntries: [string, number][] = [];

    onMount(async () => {
        emotions = await pyInvoke<EmotionStats>("get_emotions", { user_id: id });

        if (emotions?.emotions) {
            emotionEntries = emotions.emotions
                .map(e => [e.name, e.percent] as [string, number])
                .sort((a, b) => b[1] - a[1]);
        }

    });

    $: topEmotions = emotionEntries.slice(0, 4);

    function openProfile() {
        if ($isMerging) return;

        pushOverlay({
            type: 'profile',
            data: { id, isMerging }
        })
    }
</script>

<button class="profile-sticker" style="--accent: {$chosen_color}" onclick={openProfile}>
    <div class="sticker-header">
        <h2>Hello, my psyche is</h2>
    </div>

    <div class="profile-inner">
        <div class="avatar">
            {#if avatar}
                <img src={convertFileSrc(avatar)} alt={name}>
            {:else if name}
                <div class="placeholder">{(name?.[0] ?? "?").toUpperCase()}</div>
            {:else}
                <div class="placeholder">?</div>
            {/if}
        </div>

        <div class="profile-text">
            <h3 class="name">{name}</h3>
            <div class="bubbles">
                <div class="bubble">
                    <img src="icons/messages.svg" alt="msgs" />
                    {emotions?.total_messages || 0}
                </div>
            </div>
        </div>
    </div>

    <div class="emotions-container">
        {#if topEmotions.length > 0}
            {#each topEmotions as [emotionName, percentage]}
                <EmotionJar emotion={emotionName} fill={percentage} id={id} isMerging={isMerging}/>
            {/each}
        {:else}
            <p class="empty-state">No emotions tracked yet</p>
        {/if}
    </div>
</button>

<style>
.profile-sticker {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 380px;
    height: 300px;
    border-radius: 15px;
    background: repeating-linear-gradient(
        45deg,
        #ffffff,
        #ffffff 12px,
        #fafafa 12px,
        #fafafa 24px
    );
    cursor: pointer;
    font-family: 'Nunito', sans-serif;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    border: 1.5px solid var(--accent);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25);
}

.profile-sticker:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.35);
}

.sticker-header {
    width: 110%;
    margin-top: -2px;
    text-align: center;
    background-color: var(--accent);
    color: white;
    font-weight: 800;
    letter-spacing: 0.5px;
    border-radius: 10px 10px 0 0;
    font-size: 15px;
}

.profile-inner {
    padding: 15px;
    padding-left: 50px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    width: 100%;
    gap: 14px;
}

.avatar {
    flex-shrink: 0;
    width: 58px;
    height: 58px;
    border-radius: 50%;
    overflow: hidden;
    background: #e2dddd;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: rgb(25, 24, 24);
    text-transform: uppercase;
    font-size: 20px;
    border: 2px solid var(--accent);
}

.avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.profile-text {
    display: flex;
    flex-direction: column;
    gap: 4px;
    text-align: start;
}

.name {
    margin: 0;
    font-size: 17px;
    font-weight: 700;
    color: #333;
}

.bubbles {
    display: flex;
    flex-direction: row;
}

.bubble {
    display: flex;
    flex-direction: row;
    gap: 3px;
    color: #222;
    background-color: rgba(0, 0, 0, 0.06);
    border: 1px solid rgba(0, 0, 0, 0.15);
    padding: 3px 6px;
    border-radius: 10px;
    align-items: center;
}

.bubble img {
    height: 15px;
    width: 15px;
    filter: invert(10%);
}

.emotions-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: center;
    padding-top: 6px;
}

.empty-state {
    margin: 0;
    font-size: 13px;
    color: #a0a0a0;
    font-style: italic;
}
</style>
