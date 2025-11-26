<script lang="ts">
    export let icon: string = "";
    export let label: string = "";
    export let num: number | string = 0;
    export let color: string = "#6C63FF";
</script>

<div class="dash-card" style="border: 1px solid {color + '4d'}; background-color: {color + '26'};">
    <div class="icon-div" style="background-color: {color + '15'}; border: 1px solid {color + '33'};">
        <img src={icon} alt="icon" />
    </div>

    <p class="label">{label}</p>
    <p class="stats" style="color: {color};">{num}</p>
</div>

<style>
.dash-card {
    display: flex;
    flex-direction: column;
    align-items: start;
    justify-content: start;
    gap: 10px;
    text-align: start;
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 20px 25px;
    width: 33%;
    height: auto;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.25s ease;
    user-select: none;
}

.dash-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
}

.icon-div {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 70px;
    height: 70px;
    border-radius: 14px;
    transition: all 0.3s ease;
}

.icon-div img {
    width: 36px;
    height: 36px;
    opacity: 0.9;
    filter: invert(100%);
}

.label {
    font-family: "Nunito", sans-serif;
    font-size: 16px;
    font-weight: 600;
    opacity: 0.85;
    margin: 0;
}

.stats {
    font-family: "Poppins", sans-serif;
    font-size: 28px;
    font-weight: 700;
    margin: 0;
}
</style>
