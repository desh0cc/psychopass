import { writable } from "svelte/store";

export const pageState = writable(1);

export function change_page(page: number) {
    pageState.set(page);
}