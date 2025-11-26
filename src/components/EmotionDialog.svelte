<script lang='ts'>
    import { onMount } from "svelte";
    import { pyInvoke } from "tauri-plugin-pytauri-api";
    import Message from "./Message.svelte";
    import { type MessageType } from "../libs/types";
    import { colors } from "../libs/types";
    import { VirtualList } from "flowbite-svelte";

    let {id, emotion}: {id: number, emotion: string} = $props();
    
    let messages: Array<MessageType> = $state([]);
    let loading = $state(true);

    
    onMount(async () => {
        try {
            messages = await pyInvoke<Array<MessageType>>('get_emotion_messages', { id, emotion });
        } catch (e) {
            console.error("[ERROR] couldn't get messages - ", e);
        } finally {
            loading = false;
        }
    });

</script>

<main class="container" style="--accent: {colors[emotion]}">
    <div class="emotion-header">
        {emotion}
    </div>

    {#if loading}
        <p>Message loading...</p>
    {:else}
        <div class="messages-column" style="height: 80vh; overflow-y: auto;">
            {#each messages as message}
                    <Message message={message} jumpButton={true} emotionBg={true} showFullDate={true}/>
            {/each}
        </div>
    {/if}
</main>

<style>
.container {
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 15px;
    max-height: 80vh;
    overflow: hidden;
}


.emotion-header {
    font-family: 'Nunito', 'monospace';
    font-weight: 900;
    font-size: 1.5rem;
    text-align: center;
    color: white;
    position: sticky;
    top: 0;
    background-color: #191818;
    padding: 0.5rem 1rem;
    border-radius: 6px;
}

.messages-column {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    border-radius: 8px;
    background-color: #191818;
    overflow-y: scroll;
    overflow-x: hidden;
}

.messages-column::-webkit-scrollbar {
    width: 12px;
}

.messages-column::-webkit-scrollbar-track {
    background: rgba(25, 24, 24, 0.962);
}

.messages-column::-webkit-scrollbar-thumb {
    background-color: var(--accent);
    border-radius: 4px;
    border: 2px solid transparent;
    background-clip: content-box;
}
</style>