<script lang="ts">
    import { popOverlay } from "../libs/overlayState";

    let { onConfirm }: { onConfirm: () => void; } = $props();

    const title = "Are you sure?";
    const message = "This action cannot be undone";
    
    function handleConfirm() {
        onConfirm();
        popOverlay();
        popOverlay();
    }

    function handleCancel() {
        popOverlay();
    }
</script>


<!-- svelte-ignore a11y_interactive_supports_focus -->
<div 
    class="dialog"
    role="alertdialog"
    onclick={(e) => e.stopPropagation()}
    onkeydown={(e) => e.stopPropagation()}
>
    <h2 class="title">{title}</h2>

    <div class="confirm-card">
        <p class="message">{message}</p>
    </div>

    <div class="buttons-div">
        <button class="cancel" onclick={handleCancel}>
            Cancel
        </button>

        <button class="confirm" onclick={handleConfirm}>
            Delete
        </button>
    </div>
</div>

<style>

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.85);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.dialog {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #151515;
    border-radius: 24px;
    min-width: 320px;
    max-width: 520px;
    width: 90vw;
    padding: 40px 32px 32px;
    color: #f0f0f0;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.5),
        0 0 0 1px rgba(255, 255, 255, 0.05);
    font-family: 'Nunito', sans-serif;
    overflow: hidden;

    animation: fadeIn 0.25s ease;
}

.title {
    font-size: 26px;
    font-weight: 700;
    margin: 0 0 12px 0;
    color: #ffffff;
    text-align: center;
}

.confirm-card {
    text-align: center;
    font-weight: 700;
    font-size: 20px;
}

.message {
    margin: 0;
    color: rgba(255, 255, 255, 0.75);
    line-height: 1.6;
    font-family: 'Nunito', sans-serif;
}

.buttons-div {
    margin-top: 24px;
    display: flex;
    flex-direction: row;
    gap: 10px;
    width: 100%;
}

button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 14px 24px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    color: rgba(255, 255, 255, 0.7);
    font-size: 15px;
    font-weight: 600;
    font-family: 'Nunito', sans-serif;
    cursor: pointer;
    transition: all 0.2s ease;
}

button:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.9);
}

.confirm {
    border-color: #e97a6e59;
    background: rgba(255, 59, 48, 0.15);
    color: #ef6e68;
}

.confirm:hover {
    background: rgba(233, 122, 110, 0.25);
    border-color: rgba(233, 122, 110, 0.6);
    color: #ffd2cc;
}
</style>
