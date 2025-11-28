<script lang="ts">
    import { onMount } from "svelte";
    import { type ErrorEvent } from "../libs/errorhandler";
    import { openUrl } from "@tauri-apps/plugin-opener";
    import { popOverlay } from "../libs/overlayState";

    export let error: ErrorEvent;

    function reportBug() {
        openUrl("https://github.com/desh0cc/psychopass/issues/new?template=bug_report.md")
    }

    let details: string;

    onMount(()=>{
        if (error.func === "analyze_messages") {
            details = "Make sure you're using the correct parser :)"
        }
    });
</script>

<main class="container">
    <h1 class="title">Something went wrong ( ｡ •` ⤙´• ｡)</h1>

    <div class="error-card">
        <div class="error-header">
            <div class="error-badge">ERROR</div>
            <span class="error-func">{error.func}</span>
        </div>

        <div class="error-content">
            <pre class="error-details">{error.error}</pre>
        </div>

        {#if details}
            <div class="details-section">
                <p class="details-text">💡 {details}</p>
            </div>
        {/if}
    </div>

    <div class="buttons-div">
        <button class="report-bug-btn" onclick={reportBug}>
            Report this issue
        </button>

        <button class="close-error-btn" onclick={popOverlay}>
            Close
        </button>
    </div>
</main>

<style>
.container {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: linear-gradient(135deg, #1a1a1a 0%, #151515 100%);
    border-radius: 24px;
    min-width: 320px;
    max-width: 600px;
    width: 90vw;
    padding: 40px 32px 32px;
    color: #f0f0f0;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05);
    font-family: 'Nunito', sans-serif;
    overflow: hidden;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.8);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.title {
    font-size: 26px;
    font-weight: 700;
    margin: 0 0 8px 0;
    color: #ffffff;
    text-align: center;
}


.error-card {
    background: #1f1f1f;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    width: 100%;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    margin-top: 20px;
}

.error-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    background: rgba(233, 122, 110, 0.08);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.error-badge {
    background: #e97a6e;
    color: #0a0a0a;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 6px;
    letter-spacing: 0.5px;
}

.error-func {
    color: #e97a6e;
    font-weight: 600;
    font-size: 16px;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.error-content {
    padding: 20px;
    max-height: 240px;
    overflow-y: auto;
    overflow-x: hidden;
}

.error-details {
    margin: 0;
    padding: 0;
    font-family: "Consolas", monospace;
    font-size: 13px;
    line-height: 1.6;
    color: #ffbdb3;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.error-content::-webkit-scrollbar {
    width: 6px;
}

.error-content::-webkit-scrollbar-track {
    background: transparent;
}

.error-content::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
}

.error-content::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.15);
}

.buttons-div {
    margin-top: 24px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
}

button {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
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

.details-section {
    display: flex;
    flex-direction: row;
    background-color: #1a1a1a;
    padding-left: 10px;
}
</style>