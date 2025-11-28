<script lang="ts">
	// Main window attributes
	import TitleBar from "../components/TitleBar.svelte";
	import SideBar from "../components/SideBar.svelte";
	import { chosen_color } from "../libs/preferences";
	import { pageState } from "../libs/pageState";
	import { onMount } from "svelte";
	import { fade } from "svelte/transition";
	import { fly } from "svelte/transition";
	import { cubicOut } from "svelte/easing";

	// Overlay components
	import { overlayStack, popOverlay } from "../libs/overlayState";
	import FullProfile from "../components/FullProfile.svelte";
	import EmotionDialog from "../components/EmotionDialog.svelte";
	import Chat from "../components/Chat.svelte";
	import ConfirmDialog from "../components/ConfirmDialog.svelte";

	// Pages
	import Home from "../pages/Home.svelte";
	import Upload from "../pages/Upload.svelte";
	import Profiles from "../pages/Profiles.svelte";
	import Graph from "../pages/Memory.svelte";
	import Settings from "../pages/Settings.svelte";

	// Python calls
	import { pyInvoke } from "tauri-plugin-pytauri-api";
	import { progress, current_file, max_progress } from "../libs/progressState";
	import ErrorComp from "../components/ErrorComp.svelte";
	import { errorListener } from "../libs/errorhandler";
	import { initDeleteListener } from "../libs/deleteState";
	import { contextMenuStore } from "../libs/contextMenuState";

	onMount(async () => {
		await pyInvoke('create_cfg');
		await pyInvoke('create_database');
		await pyInvoke('load_resources');

		let unlisten = await initDeleteListener();
	})

	$: overlay = $overlayStack.length > 0 ? $overlayStack[$overlayStack.length - 1] : null;

	function closeOverlay() {
		popOverlay();
	}

	$: percentage = Math.round(Math.min(
		Math.max(($progress / $max_progress) * 100, 0),
		100
	));

	$: if (percentage === 100) {
		current_file.set("");
		progress.set(0);
		max_progress.set(1);

		percentage = 0;
	}

	
</script>

<main class="container">
	<TitleBar />

	{#if overlay}
	{#key overlay.data}
		<div 
		class="overlay-bg" 
		transition:fade={{ duration: 150 }}
		onclick={closeOverlay}
		role="button" 
		tabindex="0"
		onkeydown={(e) => { if (e.key === 'Escape') popOverlay(); }}
		>
			<!-- svelte-ignore a11y_click_events_have_key_events -->
			<div class="overlay-content" onclick={(e) => e.stopPropagation()} role="button" tabindex="0">
				{#if overlay.type === 'profile'}
					<FullProfile {...overlay.data}/>
				{:else if overlay.type === "emotion"}
					<EmotionDialog {...overlay.data}/>
				{:else if overlay.type === "chat"}
					<Chat {...overlay.data}/>
				{:else if overlay.type === "error"}
					<ErrorComp {...overlay.data}/>
				{:else if overlay.type === "sure"}
					<ConfirmDialog {...overlay.data}/>
				{/if}
			</div>
		</div>
	{/key}
	{/if}


	<div class="content">
		<div class="sidebar">
			<SideBar />
		</div>


		<div class="page" style="--thumb-color: {$chosen_color}"> 
			{#if $pageState === 1}
				<Home />
			{:else if $pageState === 2}
				<Upload />
			{:else if $pageState === 3}
				<Profiles />
			{:else if $pageState === 4}
				<Graph />
			{:else if $pageState === 5}
				<Settings />
			{/if}
		</div>

	{#if $current_file}
		<div
			class="upload-div"
			style="--color: {$chosen_color}"
			transition:fly={{ y: 100, duration: 400, easing: cubicOut }}
		>
			<div class="upload-content">
				<p class="filename">📁 {$current_file}</p>
			<div class="progress-container">
				<div class="progress-bar" style="width: {percentage}%"></div>
			</div>
				<p class="progress-text">{percentage}%</p>
			</div>
		</div>
	{/if}
	</div>
</main>

<style>
@font-face {
	font-family: "Nunito";
	src: url("/fonts/Nunito-Regular.ttf") format("truetype");
	font-weight: 400;
	font-style: normal;
}

@font-face {
	font-family: "Nunito";
	src: url("/fonts/Nunito-Bold.ttf") format("truetype");
	font-weight: 700;
	font-style: normal;
}

:root {
	font-family: 'Nunito', 'monospace';
}

.container {
	display: flex;
	flex-direction: column;
	height: 100vh;
	width: 100vw;
	overflow: hidden;
}

.overlay-bg {
	position: fixed;
	inset: 0;
	background: rgba(0,0,0,0.7);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 999;
	backdrop-filter: blur(2px);
}

.overlay-content {
	margin-top: 40px;
	animation: pop 0.2s ease;
}

@keyframes pop {
	from { transform: scale(0.95); opacity: 0; }
	to { transform: scale(1); opacity: 1; }
}

.content {
	display: flex;
	flex: 1;
	overflow: hidden;
}

.sidebar {
	margin-top: 40px;
	width: 120px;
	flex-shrink: 0;
	overflow: hidden;
}

.page {
	flex: 1;
	width: 100%;
	overflow-y: auto;
	overflow-x: hidden;
	margin-top: 40px;
	box-sizing: border-box;
	position: relative;
}

.page::-webkit-scrollbar {
	width: 12px;
}

.page::-webkit-scrollbar-track {
	background: rgba(25, 24, 24, 0.962);
}

.page::-webkit-scrollbar-thumb {
	background-color: var(--thumb-color);
	border-radius: 4px;
	border: 2px solid transparent;
	background-clip: content-box;
}

.upload-div {
	position: fixed;
	bottom: 24px;
	right: 24px;
	width: 320px;
	background: rgba(28, 28, 28, 0.9);
	color: #fff;
	border-radius: 16px;
	box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
	overflow: hidden;
	backdrop-filter: blur(10px);
	z-index: 1000;
	animation: fadeIn 0.3s ease forwards;
	}

.upload-content {
	padding: 16px 20px;
}

.filename {
	font-size: 0.95rem;
	font-weight: 500;
	margin-bottom: 8px;
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
}

.progress-container {
	width: 100%;
	height: 8px;
	background: rgba(255, 255, 255, 0.15);
	border-radius: 4px;
	overflow: hidden;
	margin-bottom: 6px;
}

.progress-bar {
	height: 100%;
	background-color: var(--color);
	transition: width 0.3s ease;
}

.progress-text {
	text-align: right;
	font-size: 0.85rem;
	color: rgba(255, 255, 255, 0.7);
}

@keyframes fadeIn {
	from { opacity: 0; transform: translateY(20px); }
	to { opacity: 1; transform: translateY(0); }
}
</style>
