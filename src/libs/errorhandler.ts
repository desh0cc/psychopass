import { listen } from "@tauri-apps/api/event"
import { writable, type Writable } from "svelte/store";
import { pushOverlay } from "./overlayState";

export interface ErrorEvent {
    func: string
    error: string
}

export const errorState: Writable<ErrorEvent> = writable();

export const errorListener = listen<ErrorEvent>("error_event", (event) => {
    let error = event.payload
    errorState.set(error);
    pushOverlay({
        type: 'error',
        data: { error }
    })
});