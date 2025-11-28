import { writable } from 'svelte/store';

interface ContextMenuState {
    show: boolean;
    x: number;
    y: number;
    messageId: number | null;
}

function createContextMenuStore() {
    const { subscribe, set } = writable<ContextMenuState>({
        show: false,
        x: 0,
        y: 0,
        messageId: null
    });

    return {
        subscribe,

        open: (x: number, y: number, messageId: number) => {
            set({ show: true, x, y, messageId });
        },

        close: () => {
            set({ show: false, x: 0, y: 0, messageId: null });
        },

        toggle: (x: number, y: number, messageId: number) => {
            set({ show: true, x, y, messageId });
        }
    };
}

export const contextMenuStore = createContextMenuStore();

export function handleGlobalClick(e: MouseEvent): void {
    const target = e.target as HTMLElement;
    if (!target.closest('.context-menu')) {
        contextMenuStore.close();
    }
}