import { listen } from "@tauri-apps/api/event";
import { writable, type Writable } from "svelte/store";
import { pushOverlay } from "./overlayState";

export interface DeleteEvent {
    obj_type: string;
    obj_id: number;
}

export const deleteStore: Writable<Array<DeleteEvent>> = writable([]);

export const initDeleteListener = async () => {
    const unlisten = await listen<DeleteEvent>("delete_event", (event) => {
        console.log(event);
        deleteStore.update($deleteStore => [...$deleteStore, event.payload]);
    });
    
    return unlisten;
};

export function isDeleted(objType: string, objId: number, deletedItems: DeleteEvent[]): boolean {
    return deletedItems.some(item => item.obj_type === objType && item.obj_id === objId);
}

export function clearDeleteStore() {
    deleteStore.set([]);
}

export function AreYouSure(func: () => void) {
    pushOverlay({
        type: "sure",
        data: {"onConfirm": func}
    })
}