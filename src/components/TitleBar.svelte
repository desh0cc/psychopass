<script lang="ts">
    import { getCurrentWindow } from '@tauri-apps/api/window';
    import { writable, type Writable } from 'svelte/store';
    import { pyInvoke } from "tauri-plugin-pytauri-api";

    const appWindow = getCurrentWindow();

    let maximize: HTMLElement;
    const maximized: Writable<Boolean> = writable(false);
    let emojiArray: Array<string> = ['💫','🌀','👁️','💖','👌','🫀','🦋']
    let emoji: HTMLParagraphElement;

    
    function handleMax() {
        maximized.set(!maximized);
        appWindow.toggleMaximize()
    }

    async function handleEmoji() {
        let idx = await pyInvoke<number>("get_random_emoji", {length: emojiArray.length});
        if (emojiArray[idx] === emoji.innerText) {
            idx = idx + 1
        }

        emoji.innerText = emojiArray[idx];

        if (emoji.innerText === "undefined") {
            handleEmoji()
        }
    }

    (async () => {
        const win = getCurrentWindow();
        maximized.set(await win.isMaximized());
        
        await win.listen("tauri://resize", async () => {
            maximized.set(await win.isMaximized());
        });

    })();

    $: maximize && (maximize.innerHTML = $maximized ? '&#xE923;' : '&#xE922;');
</script>



<div data-tauri-drag-region class="titlebar">
    <div class="left-section">
        <button class="not-clickable">0</button>
        <button class="not-clickable">1</button>
        <button class="not-clickable">2</button>
    </div>

    <div data-tauri-drag-region class="logo">
        <p class="logo-txt">Psych</p>
        <p bind:this={emoji} onmouseenter={handleEmoji} class="logo-emoji">${handleEmoji()}</p>
        <p class="logo-txt">Pass</p>
    </div>

    <div class="controls">
        <button onclick={() => appWindow.minimize()}>
            &#xE921;
        </button>
        <button bind:this={maximize} onclick={handleMax}>
            &#xE922;
        </button>
        <button id="close" onclick={() => appWindow.close()}>
            &#xE8BB;
        </button>
    </div>
</div>

<style>
.titlebar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 40px;
    backdrop-filter: blur(6px);
    background-color: rgb(36, 34, 34);
    user-select: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
}


.logo {
    display: flex;
    align-items: center;
    font-family: 'Cascadia Code';
    font-size: 17px;
    gap: 3px;
    color: rgb(238, 240, 243);
}

.logo-emoji {
    opacity: 0.85;
    font-size: 17px;
    transition: 
        opacity 150ms ease-in,
        font-size 150ms ease-in,
        transform 150ms ease-in;
}

.logo-emoji:hover {
    opacity: 1;
}

.left-section,
.controls {
    display: flex;
    align-items: center;
    gap: 0px;
}

.not-clickable{
    color: transparent;
}

.not-clickable:hover {
    background: transparent;
}

button { 
    font-family: 'Segoe MDL2 Assets'; 
    display: inline-flex; 
    background-color: transparent; 
    border: none; 
    color: white; 
    justify-content: center; 
    align-items: center; 
    width: 45px; 
    height: 40px; 
    font-size: 10px; 
    user-select: none; 
    -webkit-user-select: none; 
}


button:hover {
    background: #ffffff3e;
}

button#close:hover {
    background: rgba(255, 34, 34, 0.75);
}
</style>