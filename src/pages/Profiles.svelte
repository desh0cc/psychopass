<script lang="ts">
    import { onMount } from "svelte";
    import { pyInvoke } from "tauri-plugin-pytauri-api";
    import UserProfile from "../components/UserProfile.svelte";
    import { chosen_color } from "../libs/preferences";
    import { profilesRefresh } from "../libs/overlayState";
    import { writable, type Writable } from "svelte/store";
    import { VirtualList } from "flowbite-svelte";
    import { windowSize } from "../libs/windowState";
    import ChatProfile from "../components/ChatProfile.svelte";
    import {type ChatType, type Profile } from "../libs/types";

    const currentMode: Writable<"profiles" | "chats"> = writable("profiles");
    let searchQuery = "";
    let selectedItems: number[] = [];

    let profiles: Profile[] = [];
    let chats: Array<ChatType> = [];
    let filteredItems: Array<Profile | ChatType> = [];

    const mergeMode = writable(false);
    const canMerge = writable(false);

    async function loadProfiles() {
        try {
            profiles = await pyInvoke<Profile[]>("get_profiles");
        } catch (err) {
            console.error("Failed to load profiles:", err);
        }
    }

    async function loadChats() {
        try {
            chats = await pyInvoke<ChatType[]>("get_chats");
            console.log(chats);
        } catch (err) {
            console.error("Failed to load chats:", err);
        }
    }

    onMount(async () => {
        await loadProfiles();
        await loadChats();
    });

    $: {
        if ($currentMode === "profiles") {
            filteredItems = profiles.filter(p =>
                p.global_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                p.platform_users?.some(u => u.username.toLowerCase().includes(searchQuery.toLowerCase()))
            );
        } else {
            filteredItems = chats.filter(c =>
                c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                c.participants?.some(p => p.global_name.toLowerCase().includes(searchQuery.toLowerCase()))
            );
        }
    }


    function toggleSelect(id: number) {
        if ($mergeMode === true) {
            if (selectedItems.includes(id)) {
                selectedItems = selectedItems.filter(x => x !== id);
            } else {
                selectedItems = [...selectedItems, id];
            }
        } else { return }
    }

    $: canMerge.set(selectedItems.length >= 2);

    function switchMode() {
        if ($currentMode === "profiles") {
            currentMode.set("chats");
            mergeMode.set(false);
        } else {
            currentMode.set("profiles");
        }
        selectedItems = [];
    }
    
    function switchMergeMode() {
        if ($currentMode === "profiles") {
            mergeMode.set(!$mergeMode);
            selectedItems = [];
        } else { return }
    }

    async function linkAndMerge() { 

        if (selectedItems.length >= 2) {
            await pyInvoke("merge_profiles", { primary_id: selectedItems[0], secondary_ids: selectedItems.slice(1), }); 
            profilesRefresh.set(true); 
            mergeMode.set(false); 
            selectedItems = []; 
        } else { return }
    }

    $: if ($profilesRefresh) {
        (async () => {
            await loadProfiles();
            await loadChats();
            profilesRefresh.set(false);
        })();
    }

    let containerHeight: number;
    let RowEl: number;

    $: if ($currentMode === "chats") {
        RowEl = Math.max(1, Math.floor(($windowSize.width - 48) / (450 + 24)));
    } else { RowEl = Math.max(1, Math.floor(($windowSize.width - 48) / (380 + 24)))}

    $: rowCount = Math.ceil(filteredItems.length / RowEl);
    $: if ($currentMode === "chats") {
        containerHeight = (rowCount * 200 + (rowCount - 1) * 24) + 200
    } else {(containerHeight = rowCount * 300 + (rowCount - 1) * 24) + 20}

    $: grouped = Array.from(
        { length: rowCount },
        (_, i) => filteredItems.slice(i * RowEl, i * RowEl + RowEl)
    );
</script>

<main class="container" style="--br-color: {$chosen_color}">
    <h1 class="title">
        {#if $currentMode === "profiles"}
            Profiles
        {:else}
            Chats
        {/if}
    </h1>

    <div class="search-bar sticky">
        <input 
            type="text" 
            placeholder="Search by name or username..." 
            bind:value={searchQuery} 
        />

        <button class:clickable={$currentMode != "profiles"} class:active={$mergeMode} onclick={switchMergeMode}>
            <img src="icons/chain.svg" alt="linkANDmerge">
            <span class="tooltip-text">LINK & MERGE!</span>
        </button>
        <button onclick={switchMode}>
            {#if $currentMode === "profiles"}
                <img style="margin-top: 5px;" src="icons/chat.svg" alt="chats">
                <span class="tooltip-text">Switch to chats</span>
            {:else}
                <img src="icons/users.svg" alt="chats">
                <span class="tooltip-text">Switch to profiles</span>
            {/if}
        </button>
    </div>

    {#key filteredItems.length}
        <div class="items-div"> 
        {#if filteredItems.length > 0} 
            <VirtualList items={grouped} minItemHeight={300} height={containerHeight}> 
                {#snippet children(row, rowIndex)} 
                    <div class="profile-row"> 
                        {#each row as profile}
                            <div class="profile-wrapper 
                                {selectedItems.includes(profile.id)}" 
                                class:mergeMode={$mergeMode} 
                                class:selected={selectedItems.includes(profile.id)} 
                                onclick={() => toggleSelect(profile.id)} 
                                tabindex="0" 
                                role="button" 
                                onkeydown={()=>console.log("nun")}> 
                                {#if $currentMode === "profiles" && 'global_name' in profile}
                                    <UserProfile 
                                        id={profile.id} 
                                        name={profile.global_name} 
                                        avatar={profile.avatar} 
                                        isMerging={mergeMode} 
                                    />
                                {:else if $currentMode === "chats" && 'participants' in profile}
                                    <ChatProfile
                                        id={String(profile.id)}
                                        name={profile.name}
                                        avatar={profile.avatar}
                                        type={profile.type}
                                        participants={profile.participants}
                                    />
                                {/if}
                                {#if selectedItems.includes(profile.id)} 
                                    <div class="selected-overlay"> 
                                        <img src="icons/check.svg" alt="check"/> 
                                    </div> 
                                {/if}
                            </div> 
                        {/each} 
                    </div> 
                {/snippet} 
            </VirtualList> 
        {:else} 
            <p class="empty-state">
                Nothing's here brochacho :(
            </p>
        {/if}
        </div>
    {/key}

    {#if selectedItems.length >= 1}
        <div class="selected-div">
            <p class="selected-num">{selectedItems.length}</p>
            <button class:active={$canMerge} class="merge" onclick={linkAndMerge}>
                <img src="icons/check.svg" alt="merge">
            </button>
        </div>
    {/if}

</main>

<style>
.container {
    position: relative;
    background-color: #121212;
    min-width: 100%;
    min-height: 100%;
    user-select: none;
    color: #E5E5E5;
    display: flex;
    justify-content: start;
    align-items: center;
    flex-direction: column;
    gap: 20px;
    overflow-y: auto;
    overflow-x:hidden
}

main.container {
    height: 90vh;
}

.selected-div {
    position: fixed;
    bottom: 25px;
    right: 25px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    background-color: rgba(20, 20, 20, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #f1f1f1;

    padding: 12px 14px;
    border-radius: 18px;
    gap: 8px;

    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(6px);
    font-weight: 600;
    font-size: 24px;
    z-index: 9999;
}

.selected-div .selected-num {
    margin: 0;
    font-size: 26px;
    line-height: 1;
}

.selected-div button {
    border: none;
    height: 56px;
    width: 56px;
    border-radius: 50%;
    background-color: rgb(29, 28, 28);
    cursor: not-allowed;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.15s ease, opacity 0.15s ease;
}

.selected-div button.active {
    background-color: var(--br-color);
    cursor: pointer;
}

.selected-div button.active:hover {
    transform: scale(1.07);
    opacity: 0.9;
}

.selected-div button img {
    width: 28px;
    height: 28px;
    filter: invert(1);
}

.container::-webkit-scrollbar {
    width: 12px;
}

.container::-webkit-scrollbar-track {
    background: rgba(25, 24, 24, 0.962);
}

.container::-webkit-scrollbar-thumb {
    background-color: var(--thumb-color);
    border-radius: 4px;
    border: 2px solid transparent;
    background-clip: content-box;
}


.title {
    font-family: 'Nunito', monospace;
    font-size: 32px;
    color: #fff;
    margin-top: 50px;
    letter-spacing: 1px;
}

.search-bar {
    position: sticky;
    width: 100%;
    top: 0;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: center; /* центрирует input */
    gap: 20px;
    padding: 10px 20px;
    background: #121212;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

/* input */
.search-bar input {
    flex: 0 1 60%; /* занимает 60% ширины */
    height: 40px;
    padding: 12px 14px;
    border-radius: 14px;
    border: 2px solid transparent;
    background: #1a1a1a;
    color: #f1f1f1;
    font-size: 15px;
    font-family: 'Nunito', monospace;
    font-weight: 600;
    outline: none;
    transition: 0.25s;
}

.search-bar input:focus {
    border-color: var(--br-color);
}

/* кнопка */
.search-bar button {
    position: relative;
    height: 65px;
    width: 65px;
    background-color: #1a1a1a;
    border: 2px solid #555;
    border-radius: 15px;
    color: #fff;
    font-family: 'Nunito', monospace;
    font-weight: 700;
    cursor: pointer;
    transition: 0.2s;
}

.tooltip-text {
  visibility: hidden;
  opacity: 0;
  width: max-content;
  max-width: 200px;
  background-color: #222;
  color: #fff;
  text-align: center;
  border-radius: 8px;
  padding: 6px 10px;
  position: absolute;
  z-index: 1;
  bottom: -85%; /* над кнопкой */
  left: 50%;
  transform: translateX(-50%);
  transition: opacity 0.25s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  font-size: 13px;
  pointer-events: none; /* чтобы курсор не мешал */
}

/* Маленький треугольник */
.tooltip-text::after {
    transform: rotateX(180deg);
  content: "";
  position: absolute;
  bottom: 100%;
  left: 50%;
  margin-left: -6px;
  border-width: 6px;
  border-style: solid;
  border-color: #222 transparent transparent transparent;
}

/* Активация */
.search-bar button:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
}

.search-bar button img {
    justify-self: center;
    height: 30px;
    width: 30px;
    filter: invert(1) brightness(0.7);
    transition: all 100ms ease-in;
}

.search-bar button:hover img {
    transform: scale(1.1);
    filter: invert(1) brightness(1);
}

.search-bar button.clickable:hover {
    cursor: not-allowed;
}

.search-bar button.clickable:hover img {
    filter: invert(1) brightness(0.7);
}

.search-bar button.active {
    border: 2px solid white;
    background-color: var(--br-color);
}

.search-bar button.active img{
    filter: invert(1) brightness(1);
}


.items-div {
    display: flex;
    flex-wrap: wrap;
    gap: 24px;
    width: 85%;
    justify-content: center;
    align-items: start;
    padding-left: 30px;
    animation: fadeIn 0.6s ease;
}

.profile-row {
    width: 100%;
    justify-self: center;
    justify-content: flex-start;
	display: flex;
	gap: 24px;
	margin-bottom: 24px;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.empty-state {
    font-style: italic;
    color: #888;
    margin-top: 40px;
    font-size: 16px;
}

.profile-wrapper {
  position: relative;
  border-radius: 14px;
}

.profile-wrapper.mergeMode {
    outline: 2px solid var(--accent-color);
    outline-offset: 4px;
    outline-color: var(--accent-color); opacity: 0.6;
}

.profile-wrapper.mergeMode.true {
    outline: 2px solid var(--accent-color);
    outline-offset: 4px;
    outline-color: var(--accent-color); opacity: 1;
}

@keyframes mergeOutline {
  0%, 100% { outline-color: var(--accent-color); opacity: 0.6; }
  50% { outline-color: var(--accent-color); opacity: 1; }
}

.profile-wrapper.mergeMode:hover {
    outline-color: var(--accent-color); opacity: 1;
    cursor: pointer;
    animation: shake 0.4s infinite alternate;
}

.profile-wrapper.mergeMode::after {
    outline-color: var(--accent-color); opacity: 1;
}

.selected-overlay {
    position: absolute;
    inset: 0;
    background: var(--br-color);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 14px;
    animation: pop 150ms;
}

.selected-overlay img {
    width: 80px;
    height: 80px;
    justify-self: center;
    filter: invert(1);
}

@keyframes pop {
    0% { transform: scale(0); opacity: 0; }
    80% { transform: scale(1.05); opacity: 1; }
    100% { transform: scale(1); }
}

@keyframes shake {
    0%, 100% { transform: translate(0, 0); }
    25% { transform: translate(1px, -1px); }
    50% { transform: translate(-1px, 1px); }
    75% { transform: translate(1px, 1px); }
}
</style>