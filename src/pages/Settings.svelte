<script lang="ts">
    import { chosen_color } from "../libs/preferences";
    import { pyInvoke } from "tauri-plugin-pytauri-api";
    import SettingsField from "../components/SettingsField.svelte";
    import ColorPicker from 'svelte-awesome-color-picker';

    async function handleColorChange(color: string | null) {
        if (color != null) {
            chosen_color.set(color);
            const result = await pyInvoke("change_config_value", {'key': 'color', 'value': color})
            console.log(result);
        }
    }
</script>

<main class="container">
  <div class="background">
    <img class="bg-cog cog1" src="icons/settings.svg" alt="cogwheel">
    <img class="bg-cog cog2" src="icons/settings.svg" alt="cogwheel">
  </div>

  <div class="settings">
    <p class="title">Settings</p>
    <div class="settings-cont">
        <SettingsField
            label={"App Version"}>
            <p style="font-weight: 700;" >0.1.0</p>
        </SettingsField>
        <SettingsField
            label={"Developed by"}>
            <p style="font-weight: 700;" >desh0cc</p>
        </SettingsField>
        <SettingsField 
            label="Accent">
            <div class="dark">
                <ColorPicker
                    label={""}
                    hex={$chosen_color}
                    isAlpha = {false}
                    isTextInput={false}
                    --picker-indicator-size={"15px"}
                    --input-size={"25px"}
                    onInput={(e) => handleColorChange(e.hex)}
                    position={"fixed"}
                    isDark={false}
                />
            </div>
        </SettingsField>
    </div>
  </div>
</main>

<style>
:root {
    image-rendering: auto;
}

.container {
    position: relative;
    background: #121212;
    width: 100%;
    height: 100%;
    overflow: hidden;
    user-select: none;
    color: #E5E5E5;
    display: flex;
    justify-content: center;
    align-items: center;
}

.title {
    font-weight: 700;
    font-size: 35px;
    margin-bottom: 30px;
}

.dark {
    --cp-bg-color: #1c1b1d;
    --cp-border-color: #3a383c;
    --cp-text-color: #f5f5f5;
    --cp-input-color: #2a272b;
    --cp-button-hover-color: #3e3b42;
}


.settings {
    position: absolute;
    top: 10%;
    left: 50%;
    transform: translateX(-50%);
    width: 400px;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.settings-cont {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    background-color: #222123;
    border-radius: 20px;
    padding: 30px;
    border: 3px solid white;
    vertical-align: middle;
    gap: 5px;
}


.bg-cog {
    position: absolute;
    opacity: 0.15;
    transform-origin: center;
}

img {
    filter: invert(100%);
}

.cog1 {
    width: 400px;
    height: 400px;
    bottom: -150px;
    left: -150px;
    animation: spin 20s linear infinite;
    filter: brightness(0.8);
    
}

.cog2 {
    width: 300px;
    height: 300px;
    top: -100px;
    right: -100px;
    animation: spin-reverse 25s linear infinite;
    filter: brightness(0.7);
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}

@keyframes spin-reverse {
    from { transform: rotate(360deg); }
    to   { transform: rotate(0deg); }
}
</style>
