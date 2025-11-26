<script lang="ts">
    import { pushOverlay } from "../libs/overlayState";
    import { type Writable } from "svelte/store";
    import { colors } from "../libs/types";

    export let id: number;
    export let emotion: string = "happiness";
    export let fill: number = 50;
    export let color: string = "#000000";
    export let isMerging: Writable<boolean>;


    $: color = colors[emotion] || "#4fc3f7";
    $: fillClamped = Math.min(Math.max(fill, 0), 100);
    $: liquidHeight = Math.max(3, fillClamped)

    function openOverlay () {
        if ($isMerging) return;

        pushOverlay({
            type:"emotion", 
            data:{'id':id,"emotion":emotion}
        });
    }
</script>

<button class="emotion-jar" style="color: {color};" onclick={openOverlay}>
    <div class="jar-container">
        <div 
            class="liquid"
            style="height: {liquidHeight}%; background-color: {color};"
        ></div>
        <div class="shine"></div>
    </div>
    <div class="label-container">
        <span class="emotion-name">{emotion}</span>
        <span class="emotion-fill">{fillClamped}%</span>
    </div>
</button>

<style>
.emotion-jar {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 8px;
    border: none;
    background: transparent;
    user-select: none;
    cursor: pointer;
    transition: all 100ms ease-in;
    font-family: 'Nunito', 'monospace';
    font-weight: 700;
}

.emotion-jar:hover {
    transform: translateY(-4px);
}


.jar-container {
    position: relative;
    width: 40px;
    height: 65px;
    background: 
    linear-gradient(
        90deg,
        rgba(10, 10, 10, 0.9) 0%,
        rgba(28, 27, 27, 0.871) 50%,
        rgba(10, 10, 10, 0.9) 100%
    );
    border: 1.5px solid rgba(255, 255, 255, 0.08);
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
    overflow: hidden;
    box-shadow:
        inset 0 2px 6px rgba(255, 255, 255, 0.08),
        0 3px 8px rgba(0, 0, 0, 0.4);
}



.liquid {
    position: absolute;
    bottom: 0;
    width: 100%;
    transition: height 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    opacity: 0.95;
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
}

/* Имитация блика */
.shine {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    background: linear-gradient(
        130deg,
        rgba(255, 255, 255, 0.15) 10%,
        rgba(255, 255, 255, 0.03) 30%,
        transparent 70%
    );
    mix-blend-mode: overlay;
}

/* Подписи */
.label-container {
    margin-top: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.emotion-name {
    font-size: 12px;
    font-weight: 700;
    text-transform: capitalize;
}

.emotion-fill {
    font-size: 0.7rem;
    margin-top: 2px;
}
</style>
