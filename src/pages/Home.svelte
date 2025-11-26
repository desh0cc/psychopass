<script lang="ts">
    import { onMount } from "svelte";
    import { pyInvoke } from "tauri-plugin-pytauri-api";
    import { change_page } from "../libs/pageState";
    import { chosen_color } from "../libs/preferences";
    import { getCurrentWindow } from "@tauri-apps/api/window";
    import { colors } from "../libs/types";

    import FeatureCard from "../components/FeatureCard.svelte";

    let username: string = ""

    let displayed = "";
    let index = 0;

    function typeWriter() {
        if (index < username.length) {
            displayed += username[index];
            index += 1;
            setTimeout(typeWriter, 100);
        }
    }

    onMount(async () => {
        username = await pyInvoke<string>('get_username');
        typeWriter();

        const res = getCurrentWindow().listen("height", ({ event, payload }) => { });
        console.log(res);
    });
</script>

<main class="container" style="--accent-color: {$chosen_color}">
  <div class="background" style="--color: {$chosen_color + "26"}"></div>

  <div class="main">
    <div class="welcome">
        <img class="logo" src="psychopass trans.svg" alt="logo" />
        <p class="welcome-text hello">Hey <span class="typewriter">{displayed}</span> 👋</p>
        <p class="welcome-text subtitle">Welcome to <span style="color: {$chosen_color};" class="highlight">PSYCHOPASS</span> !</p>
    </div>
    <div class="features">
        <p style="text-align: center; font-size: 25px">Explore the features</p>
        <div class="features-row">
            <FeatureCard
                icon={'icons/upload.svg'}
                label={'Upload'}
                desc={'Import your messages in json format from different platforms'}
                color={"#4CAF50"} 
                onClick={() => change_page(2)}
            />
            <FeatureCard
                icon={'icons/database.svg'}
                label={'Database'}
                desc={'See how much people have you interacted with in your life <br><span style="opacity:0.7">(Hopefully a lot)</span>'}
                color={"#9C27B0"}
                onClick={() => change_page(3)}
            />
            <FeatureCard
                icon={'icons/network.svg'}
                label={'Memory'}
                desc={'Visualize and search messages over different years'}
                color={"#FF9800"}
                onClick={() => change_page(4)}
            />
            <FeatureCard
                icon={'icons/settings.svg'}
                label={'Settings'}
                desc={'Customize colors, preferences for a personal touch'}
                color={"#03A9F4"}
                onClick={() => change_page(5)}
            />
        </div>
    </div>
    <div class="howitworks">
        <p style="text-align: center; font-size: 25px">How it works?</p>
          <div class="steps-info">
            <div class="step">
                <div class="number">1</div>
                <div class="text">
                    <h3>Upload</h3>
                    <p>Import your messages or files into the system</p>
                </div>
            </div>

            <div class="step">
                <div class="number">2</div>
                <div class="text">
                    <h3>Analyze</h3>
                    <p>AI detects and categorizes emotions within the text</p>
                </div>
            </div>

            <div class="step">
                <div class="number">3</div>
                <div class="text">
                    <h3>Organize</h3>
                    <p>Manage chats, profiles, messages and store chats the way you like</p>
                </div>
            </div>
        </div>
        <div class="separator"></div>
        <div class="emotions">
            {#each Object.entries(colors).slice(0,9) as [name, color]}
                <div class="emotion">
                    <div class="color" style="background-color:{color};"></div>
                    <p>{name}</p>
                </div>
            {/each}
        </div>
    </div>
  </div>
</main>

<style>

.container {
    position: relative;
    width: 100%;
    min-height: 100vh;
    height: auto;
    overflow-y: auto;
    overflow-x: hidden;
    user-select: none;
    padding-bottom: 30px;
}



.main {
    margin-top: 30px;
    display: flex;
    flex-direction: column;
    font-family: 'Nunito', 'monospace';
    font-weight: 700;
    color: white;
    justify-self: center;
    animation: fadeIn 0.6s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.welcome {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 2rem 1rem;
    text-align: center;
}

.logo {
    width: 120px;
    height: auto;
    margin-bottom: 0;
}

img {
    color: #55a0ec;
}

.welcome-text {
    margin: 0;
    line-height: 1.2;
    font-family: 'Segoe UI', Roboto, sans-serif;
    color: #eee;
}

.hello {
    font-size: 1.2rem;
    font-weight: 500;
}

.subtitle {
    font-size: 1rem;
    color: #bbb;
}

.highlight {
    font-weight: 700;
}


.features-row {
    display: flex;
    flex-direction: row;
    gap: 10px;
}

.howitworks {
  margin-top: 40px;
  padding: 40px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.07);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #f1f1f1;
  font-family: 'Nunito', 'Segoe UI', sans-serif;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}


.steps-info {
  display: flex;
  flex-direction: row;
  gap: 25px;
  align-items: center;
}

img {
    color: #898d90;
}

.step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    width: 190px;
    height: 150px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 12px 18px;
    transition: background 0.3s ease;
}

.step:hover {
  background: rgba(255, 255, 255, 0.1);
}

.number {
  background-color: var(--accent-color);
  color: white;
  font-weight: bold;
  font-size: 18px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.text h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.text p {
  margin: 4px 0 0;
  font-size: 14px;
  opacity: 0.8;
}

.separator {
  height: 1px;
  width: 100%;
  margin: 30px auto;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.emotions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
}

.emotion {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  opacity: 0.9;
  transition: opacity 0.3s ease;
}

.emotion:hover {
  opacity: 1;
}

.emotion .color {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}



.background {
    position: absolute;
    inset: 0;
    background-color: #0e0e0e;
    background-image:
        linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: moveGrid 5s linear infinite;
    overflow: hidden;
    z-index: -1;
}

.background::after {
    content: "";
    position: absolute;
    inset: -100px;
    background: radial-gradient(circle at 50% 50%, var(--color), transparent 70%);
    filter: blur(80px);
    animation: pulseLight 8s ease-in-out infinite alternate;
}

@keyframes moveGrid {
    from { background-position: 0 0; }
    to { background-position: 60px 60px; }
}

@keyframes pulseLight {
    from { transform: translate(0,0); opacity: 0.6; }
    to { transform: translate(40px, -20px); opacity: 0.9; }
}






</style>
