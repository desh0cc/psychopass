<script lang="ts">
    import { colors } from "../libs/types";

    export let name: string;
    export let percent: number;
    export let x: number;
    export let y: number;
    export let r: number;

    const color = colors[name];
</script>

<main
    class="region-container emotion-region"
    style="
        background-color: {color};
        top: {y}px;
        left: {x}px;
        width: {r * 2}px;
        height: {r * 2}px;
        --emo_color: {color};
    "
>
    <p>{name}</p>
    <span>{percent.toFixed(2)}%</span>
</main>


<style>
.region-container {
    position: absolute;
    transform: translate(-50%, -50%);
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.3s ease;
    box-shadow: 0 0 20px rgba(0,0,0,0.3);
    user-select: none;
}

.region-container:hover {
    box-shadow: 0 0 25px var(--emo_color);
}
</style>
