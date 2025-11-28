<script lang="ts">
    import { open } from "@tauri-apps/plugin-dialog";
    import { pyInvoke } from "tauri-plugin-pytauri-api";
    import DashCard from "../components/DashCard.svelte";
    import { onMount } from "svelte";

    let stats: { messages: number; uploads: number; profiles: number; last_upload: string | null} =  {
        messages: 0,
        uploads: 0,
        profiles: 0,
        last_upload: "No record >_<"
    };

    let isLoading = false;

    async function selectFiles(platform: string) {
        const filePaths = await open({
            multiple: true,
            filters: [
                { name: 'JSON Files', extensions: ['json'] }
            ],
            directory: true
        });

        if (filePaths) {
            console.log('вибрані файли:', filePaths);
            isLoading = true;
            filePaths.forEach(async element => {
                await pyInvoke('analyze_messages', {'path': element, 'platform': platform})
            });
            await update_stats();
            isLoading = false;
            return;
        } else {
            console.log('не вибрав файл(и)');
            return;
        }
    }
    interface Stats {
        messages: number;
        uploads: number;
        profiles: number;
        last_upload: string | null;
    }

    let lastUpload = "No record >_<"

    async function update_stats() {
        stats = await pyInvoke<Stats>('get_statistics');
        if (stats.last_upload?.toString() != null) {
            lastUpload = stats.last_upload
        }
    }

    onMount(async () => {
        await update_stats()
    });
</script>

<main class="container">
    <div class="dashboard row">
        <DashCard
            icon={"icons/upload-alt.svg"}
            label={"TOTAL UPLOADS"}
            color={"#6C63FF"}
            num={stats.uploads}
        />

        <DashCard
            icon={"icons/messages.svg"}
            label={"MESSAGES PROCESSED"}
            color={"#00BFA6"}
            num={stats.messages}
        />

        <DashCard
            icon={"icons/calendar.svg"}
            label={"LAST UPLOAD"}
            color={"#F4B400"}
            num={lastUpload}
        />
    </div>

    <!-- Upload section -->
    <div class="upload-section">
        
        <div class="row">
            <button class="option" onclick={() => selectFiles("telegram")} disabled={isLoading}>
                {#if isLoading}
                    <div class="loader"></div>
                    <p class="label">Processing...</p>
                {:else}
                    <img src="telegram.svg" alt="telegram">
                    <p class="label">Telegram</p>
                {/if}
            </button>
            <button class="option" onclick={() => selectFiles("discord")} disabled={isLoading}>
                {#if isLoading}
                    <div class="loader"></div>
                    <p class="label">Processing...</p>
                {:else}
                    <img src="discord.svg" alt="discord">
                    <p class="label">Discord</p>
                {/if}
            </button>
            
            <div class="option-placeholder">
                <div class="placeholder-icon">
                    <img style="width: 50px; height: 50px; filter:invert(1); opacity:0.7;" src="plus.svg" alt="feature-request">
                </div>
                <p class="label">Need more sources?<br/>
                    <a target="_blank" href="https://github.com/desh0cc/psychopass/issues/new?template=feature_request.md">Feature Request</a>
                </p>
            </div>
        </div>
    </div>
</main>

<style>

.container {
    position: relative;
    background-color: #121212;
    min-width: 100%;
    height: 100%;
    overflow: auto;
    user-select: none;
    color: #E5E5E5;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    flex-direction: column;
    gap: 0px;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.dashboard {
    animation: fadeInUp 0.6s ease-out 0.2s backwards;
}

.row {
    display: flex;
    flex-direction: row;
    vertical-align: middle;
    justify-items: center;
    gap: 20px;
    width: 90%;
    max-width: 1200px;
    padding: 15px;
    z-index: 1;
    margin-top: 30px;
    justify-self: center;
    animation: fadeIn 0.6s ease;
}

.upload-section {
    text-align: center;
    width: 100%;
    z-index: 1;
    animation: fadeInUp 0.6s ease-out 0.4s backwards;
}


.option {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    color: #f1f1f1;
    height: 220px;
    width: 220px;
    cursor: pointer;
    padding: 10px;
    transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
    position: relative;
    overflow: hidden;
}

.option::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s;
}

.option:hover::before {
    left: 100%;
}

.option:hover:not(:disabled) {
    transform: translateY(-6px);
}

.option:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.option img {
    margin-top: 20px;
    height: 100px;
    width: 100px;
    filter: invert(100%);
    transition: transform 0.3s;
}

.option:hover:not(:disabled) img {
    transform: scale(1.1) rotate(5deg);
}

.option .label {
    font-family: 'Nunito', 'monospace';
    font-weight: 700;
    font-size: 20px;
    margin-top: 15px;
}

.loader {
    width: 60px;
    height: 60px;
    border: 4px solid rgba(255, 255, 255, 0.1);
    border-top: 4px solid #6C63FF;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-top: 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.option-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 2px dashed rgba(255, 255, 255, 0.15);
    color: rgba(241, 241, 241, 0.4);
    height: 220px;
    width: 220px;
}

.option-placeholder a {
    color: #4da6ff;
    text-decoration: underline;
}

.option-placeholder a:hover {
    color: #80c1ff;
}

.placeholder-icon {
    margin-top: 20px;
    opacity: 0.3;
}

.option-placeholder .label {
    font-family: 'Nunito', 'monospace';
    font-weight: 600;
    font-size: 16px;
    margin-top: 15px;
    text-align: center;
    line-height: 1.4;
}
</style>