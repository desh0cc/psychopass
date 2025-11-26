import { writable, type Writable } from "svelte/store";
import { listen } from "@tauri-apps/api/event";

export const current_file: Writable<string> = writable("");
export const progress: Writable<number> = writable(0);
export const max_progress: Writable<number> = writable(1);

export interface ProgressBar {
    current_file: string; 
    progress: number;
    max_progress: number;
}

export const progressListener = listen<ProgressBar>("emotion_analyzing", (event) => {
    current_file.set(event.payload.current_file);
    progress.set(event.payload.progress);
    max_progress.set(event.payload.max_progress);
});