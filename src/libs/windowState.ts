import { writable } from "svelte/store";
import { getCurrentWindow, PhysicalSize } from "@tauri-apps/api/window";

export const windowSize = writable({ width: 0, height: 0 });

(async () => {
	const win = getCurrentWindow();

	const size = await win.innerSize();
    console.log(size);
	windowSize.set({ width: size.width, height: size.height });

	const unlisten = await win.listen<PhysicalSize>("tauri://resize", (event) => {
		const { payload } = event;
		windowSize.set({ width: payload.width, height: payload.height });
	});
})();
