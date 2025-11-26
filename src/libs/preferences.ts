import { pyInvoke } from "tauri-plugin-pytauri-api";
import { writable } from "svelte/store";

export const chosen_color = writable<string>("");

pyInvoke<string>("get_config_value", {'key': 'color'}).then((value) => { 
    chosen_color.set(value); console.log(chosen_color) }).catch((err) => { 
        console.error("Failed to load color from config:", err); 
    }
);