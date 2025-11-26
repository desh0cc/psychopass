import { writable } from "svelte/store";


export const profilesRefresh = writable(false);
export const overlayStack = writable<Array<{ type: string; data?: any }>>([]);

export const pushOverlay = (overlay: { type: string; data?: any }) => {
    overlayStack.update(stack => [...stack, overlay]);
};

export const popOverlay = () => {
    overlayStack.update(stack => {
        const newStack = [...stack];
        newStack.pop();
        return newStack;
    });
};

export const clearOverlays = () => {
    overlayStack.set([]);
};