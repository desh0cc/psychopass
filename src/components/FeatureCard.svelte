<script lang="ts">
  export let icon: string = "";
  export let label: string = "";
  export let desc: string = "";
  export let color: string = "#7fffd4";
  export let onClick: () => void;
</script>

<button class="container" type="button" on:click={onClick}>
    <div class="icon" style="background-color: {color};">
        <img src={icon} alt={label} />
    </div>
    <div class="info">
        <p class="label">{label}</p>
        <p class="description">{@html desc}</p>
    </div>
</button>

<style>
.container {
    padding: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 200px;
    height: 220px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #f1f1f1;
    cursor: pointer;
    user-select: none;
    transition: transform 0.2s, box-shadow 0.2s;
}

.container:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.5);
}

.icon {
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 8px;
    height: 60px;
    width: 60px;
    margin-bottom: 14px;
    transition: background-color 0.2s;
}

.icon img {
    width: 32px;
    height: 32px;
    filter: invert(100%);
    transition: transform 0.2s;
}

.container:hover .icon img {
    transform: scale(1.1);
}

.info {
    text-align: center;
    font-family: 'Nunito', monospace;
    font-weight: 600;
    color: white;
}

.label {
    font-size: 1.1rem;
    margin: 0;
}

.description {
    font-size: 0.9rem;
    margin: 2px 0 0 0;
    color: #ccc;
}
</style>
